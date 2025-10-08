"""
Pattern 19: Inter-Agent Communication (A2A)
==========================================

A production-inspired implementation of agent-to-agent communication,
based on Codex's MCP architecture.

Prerequisites:
    pip install aiohttp

Key Concepts Demonstrated:
- Service discovery between agents
- Structured message passing
- Protocol abstraction
- Error handling in distributed communication
- Agent delegation and coordination

Based on: codex-rs/mcp-client/src/mcp_client.rs
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import aiohttp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of inter-agent messages."""
    DISCOVER = "discover"
    CAPABILITY_RESPONSE = "capability_response"
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


@dataclass
class AgentCapability:
    """Represents an agent's capability/tool."""
    name: str
    description: str
    parameters: Dict[str, Any]
    agent_id: str


@dataclass
class AgentMessage:
    """Standard message format for A2A communication."""
    id: str
    type: MessageType
    sender_id: str
    recipient_id: str
    payload: Dict[str, Any]
    timestamp: str
    correlation_id: Optional[str] = None

    def to_json(self) -> str:
        """Serialize message to JSON."""
        data = asdict(self)
        data["type"] = self.type.value
        return json.dumps(data, separators=(",", ":"))

    @classmethod
    def from_json(cls, json_str: str) -> "AgentMessage":
        """Deserialize message from JSON."""
        data = json.loads(json_str)
        data["type"] = MessageType(data["type"])
        return cls(**data)


class CommunicationError(Exception):
    """Base exception for agent communication errors."""
    pass


class AgentTimeoutError(CommunicationError):
    """Agent did not respond within timeout."""
    pass


class AgentUnavailableError(CommunicationError):
    """Agent is not available for communication."""
    pass


class AgentRegistry:
    """
    Central registry for agent discovery.
    In production, this might be a distributed service mesh.
    """

    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.capabilities: Dict[str, List[AgentCapability]] = {}

    def register_agent(
        self, agent_id: str, endpoint: str, capabilities: List[AgentCapability]
    ):
        """Register an agent and its capabilities."""
        self.agents[agent_id] = {
            "endpoint": endpoint,
            "last_seen": datetime.now().isoformat(),
            "status": "active",
        }
        self.capabilities[agent_id] = capabilities
        logger.info(f"Registered agent {agent_id} with {len(capabilities)} capabilities")

    def unregister_agent(self, agent_id: str):
        """Remove agent from registry."""
        self.agents.pop(agent_id, None)
        self.capabilities.pop(agent_id, None)
        logger.info(f"Unregistered agent {agent_id}")

    def discover_agents(self) -> List[str]:
        """Get list of active agent IDs."""
        return list(self.agents.keys())

    def get_agent_capabilities(self, agent_id: str) -> List[AgentCapability]:
        """Get capabilities for specific agent."""
        return self.capabilities.get(agent_id, [])

    def find_agents_with_capability(self, capability_name: str) -> List[str]:
        """Find agents that have a specific capability."""
        matching_agents = []
        for agent_id, caps in self.capabilities.items():
            if any(cap.name == capability_name for cap in caps):
                matching_agents.append(agent_id)
        return matching_agents

    def get_agent_endpoint(self, agent_id: str) -> Optional[str]:
        """Get agent's communication endpoint."""
        agent_info = self.agents.get(agent_id)
        return agent_info["endpoint"] if agent_info else None


class InterAgentCommunicator:
    """
    Handles communication between agents.
    Inspired by: codex-rs/mcp-client/src/mcp_client.rs
    """

    def __init__(self, agent_id: str, registry: AgentRegistry):
        self.agent_id = agent_id
        self.registry = registry
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.session = None

    async def start(self):
        """Initialize communication session."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        logger.info(f"Started communicator for agent {self.agent_id}")

    async def stop(self):
        """Clean up communication session."""
        if self.session:
            await self.session.close()
        logger.info(f"Stopped communicator for agent {self.agent_id}")

    async def discover_capabilities(self, target_agent_id: str) -> List[AgentCapability]:
        """
        Discover capabilities of another agent.
        Equivalent to MCP's tools/list.
        """
        try:
            # First check registry cache
            cached_caps = self.registry.get_agent_capabilities(target_agent_id)
            if cached_caps:
                return cached_caps

            # If not cached, send discovery message
            message = AgentMessage(
                id=str(uuid.uuid4()),
                type=MessageType.DISCOVER,
                sender_id=self.agent_id,
                recipient_id=target_agent_id,
                payload={},
                timestamp=datetime.now().isoformat(),
            )

            response = await self._send_message(target_agent_id, message)
            if response.type == MessageType.CAPABILITY_RESPONSE:
                capabilities = [
                    AgentCapability(**cap) for cap in response.payload["capabilities"]
                ]
                # Update registry cache
                endpoint = self.registry.get_agent_endpoint(target_agent_id)
                if endpoint:
                    self.registry.register_agent(target_agent_id, endpoint, capabilities)
                return capabilities
            else:
                raise CommunicationError(f"Unexpected response type: {response.type}")

        except Exception as e:
            logger.error(f"Failed to discover capabilities for {target_agent_id}: {e}")
            raise CommunicationError(f"Discovery failed: {e}")

    async def delegate_task(
        self,
        target_agent_id: str,
        capability_name: str,
        parameters: Dict[str, Any],
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """
        Delegate a task to another agent.
        Equivalent to MCP's tools/call.
        """
        try:
            message = AgentMessage(
                id=str(uuid.uuid4()),
                type=MessageType.TASK_REQUEST,
                sender_id=self.agent_id,
                recipient_id=target_agent_id,
                payload={
                    "capability": capability_name,
                    "parameters": parameters,
                },
                timestamp=datetime.now().isoformat(),
            )

            response = await self._send_message(target_agent_id, message, timeout)

            if response.type == MessageType.TASK_RESPONSE:
                return response.payload
            elif response.type == MessageType.ERROR:
                raise CommunicationError(
                    f"Agent {target_agent_id} returned error: {response.payload.get('error', 'Unknown error')}"
                )
            else:
                raise CommunicationError(f"Unexpected response type: {response.type}")

        except asyncio.TimeoutError:
            raise AgentTimeoutError(
                f"Agent {target_agent_id} did not respond within {timeout}s"
            )
        except Exception as e:
            logger.error(f"Task delegation failed: {e}")
            raise

    async def _send_message(
        self,
        target_agent_id: str,
        message: AgentMessage,
        timeout: float = 30.0,
    ) -> AgentMessage:
        """Send message to target agent and wait for response."""
        endpoint = self.registry.get_agent_endpoint(target_agent_id)
        if not endpoint:
            raise AgentUnavailableError(f"Agent {target_agent_id} not found in registry")

        # Create future for response
        response_future = asyncio.Future()
        self.pending_requests[message.id] = response_future

        try:
            # Send HTTP POST request
            async with self.session.post(
                f"{endpoint}/message",
                data=message.to_json(),
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    response_data = await response.text()
                    return AgentMessage.from_json(response_data)
                else:
                    raise CommunicationError(
                        f"HTTP {response.status}: {await response.text()}"
                    )

        except aiohttp.ClientError as e:
            raise CommunicationError(f"Network error: {e}")
        finally:
            # Clean up pending request
            self.pending_requests.pop(message.id, None)


class BaseAgent:
    """
    Base class for agents that can communicate with each other.
    Inspired by Codex's agent architecture.
    """

    def __init__(self, agent_id: str, registry: AgentRegistry):
        self.agent_id = agent_id
        self.registry = registry
        self.communicator = InterAgentCommunicator(agent_id, registry)
        self.capabilities: List[AgentCapability] = []
        self.running = False

    def add_capability(self, name: str, description: str, parameters: Dict[str, Any]):
        """Add a capability to this agent."""
        capability = AgentCapability(
            name=name,
            description=description,
            parameters=parameters,
            agent_id=self.agent_id,
        )
        self.capabilities.append(capability)

    async def start(self, endpoint: str):
        """Start the agent and register with registry."""
        await self.communicator.start()
        self.registry.register_agent(self.agent_id, endpoint, self.capabilities)
        self.running = True
        logger.info(f"Agent {self.agent_id} started at {endpoint}")

    async def stop(self):
        """Stop the agent and unregister."""
        self.running = False
        self.registry.unregister_agent(self.agent_id)
        await self.communicator.stop()
        logger.info(f"Agent {self.agent_id} stopped")

    async def handle_message(self, message: AgentMessage) -> AgentMessage:
        """Handle incoming message from another agent."""
        try:
            if message.type == MessageType.DISCOVER:
                return await self._handle_discovery(message)
            elif message.type == MessageType.TASK_REQUEST:
                return await self._handle_task_request(message)
            else:
                return self._create_error_response(
                    message, f"Unsupported message type: {message.type}"
                )
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return self._create_error_response(message, str(e))

    async def _handle_discovery(self, message: AgentMessage) -> AgentMessage:
        """Handle capability discovery request."""
        return AgentMessage(
            id=str(uuid.uuid4()),
            type=MessageType.CAPABILITY_RESPONSE,
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            payload={
                "capabilities": [asdict(cap) for cap in self.capabilities]
            },
            timestamp=datetime.now().isoformat(),
            correlation_id=message.id,
        )

    async def _handle_task_request(self, message: AgentMessage) -> AgentMessage:
        """Handle task execution request."""
        capability_name = message.payload.get("capability")
        parameters = message.payload.get("parameters", {})

        # Find matching capability
        capability = next(
            (cap for cap in self.capabilities if cap.name == capability_name),
            None,
        )

        if not capability:
            return self._create_error_response(
                message, f"Capability '{capability_name}' not found"
            )

        try:
            # Execute the capability
            result = await self.execute_capability(capability_name, parameters)
            return AgentMessage(
                id=str(uuid.uuid4()),
                type=MessageType.TASK_RESPONSE,
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                payload={"result": result},
                timestamp=datetime.now().isoformat(),
                correlation_id=message.id,
            )
        except Exception as e:
            return self._create_error_response(message, f"Execution failed: {e}")

    def _create_error_response(self, original_message: AgentMessage, error: str) -> AgentMessage:
        """Create error response message."""
        return AgentMessage(
            id=str(uuid.uuid4()),
            type=MessageType.ERROR,
            sender_id=self.agent_id,
            recipient_id=original_message.sender_id,
            payload={"error": error},
            timestamp=datetime.now().isoformat(),
            correlation_id=original_message.id,
        )

    async def execute_capability(self, capability_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute a capability. Override in subclasses.
        """
        raise NotImplementedError("Subclasses must implement execute_capability")


class SearchAgent(BaseAgent):
    """Specialized agent for search operations."""

    def __init__(self, agent_id: str, registry: AgentRegistry):
        super().__init__(agent_id, registry)
        self.add_capability(
            "web_search",
            "Search the web for information",
            {"query": {"type": "string", "description": "Search query"}},
        )
        self.add_capability(
            "document_search",
            "Search through documents",
            {
                "query": {"type": "string", "description": "Search query"},
                "collection": {"type": "string", "description": "Document collection"},
            },
        )

    async def execute_capability(self, capability_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute search capabilities."""
        if capability_name == "web_search":
            query = parameters.get("query", "")
            # Simulate web search
            await asyncio.sleep(0.5)  # Simulate network delay
            return {
                "results": [
                    {"title": f"Result for '{query}' #1", "url": "http://example.com/1"},
                    {"title": f"Result for '{query}' #2", "url": "http://example.com/2"},
                ],
                "count": 2,
            }
        elif capability_name == "document_search":
            query = parameters.get("query", "")
            collection = parameters.get("collection", "default")
            await asyncio.sleep(0.3)
            return {
                "documents": [
                    {"title": f"Doc about '{query}'", "score": 0.95, "collection": collection}
                ],
                "count": 1,
            }
        else:
            raise ValueError(f"Unknown capability: {capability_name}")


class AnalysisAgent(BaseAgent):
    """Specialized agent for analysis operations."""

    def __init__(self, agent_id: str, registry: AgentRegistry):
        super().__init__(agent_id, registry)
        self.add_capability(
            "analyze_text",
            "Analyze text content",
            {"text": {"type": "string", "description": "Text to analyze"}},
        )
        self.add_capability(
            "summarize",
            "Summarize content",
            {
                "content": {"type": "string", "description": "Content to summarize"},
                "max_length": {"type": "integer", "description": "Maximum summary length"},
            },
        )

    async def execute_capability(self, capability_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute analysis capabilities."""
        if capability_name == "analyze_text":
            text = parameters.get("text", "")
            await asyncio.sleep(0.4)  # Simulate processing time
            return {
                "sentiment": "positive",
                "word_count": len(text.split()),
                "key_topics": ["AI", "agents", "communication"],
            }
        elif capability_name == "summarize":
            content = parameters.get("content", "")
            max_length = parameters.get("max_length", 100)
            await asyncio.sleep(0.6)
            summary = content[:max_length] + "..." if len(content) > max_length else content
            return {"summary": summary, "original_length": len(content)}
        else:
            raise ValueError(f"Unknown capability: {capability_name}")


class CoordinatorAgent(BaseAgent):
    """
    Coordinator agent that delegates tasks to specialized agents.
    Demonstrates the A2A pattern in action.
    """

    def __init__(self, agent_id: str, registry: AgentRegistry):
        super().__init__(agent_id, registry)
        self.add_capability(
            "research_and_analyze",
            "Research a topic and provide analysis",
            {"topic": {"type": "string", "description": "Topic to research"}},
        )

    async def execute_capability(self, capability_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute coordination capabilities."""
        if capability_name == "research_and_analyze":
            topic = parameters.get("topic", "")
            return await self._research_and_analyze(topic)
        else:
            raise ValueError(f"Unknown capability: {capability_name}")

    async def _research_and_analyze(self, topic: str) -> Dict[str, Any]:
        """
        Coordinate between search and analysis agents.
        Demonstrates multi-agent workflow.
        """
        try:
            # Step 1: Find agents with required capabilities
            search_agents = self.registry.find_agents_with_capability("web_search")
            analysis_agents = self.registry.find_agents_with_capability("analyze_text")

            if not search_agents:
                raise CommunicationError("No search agents available")
            if not analysis_agents:
                raise CommunicationError("No analysis agents available")

            # Step 2: Delegate search task
            logger.info(f"Delegating search for '{topic}' to {search_agents[0]}")
            search_result = await self.communicator.delegate_task(
                search_agents[0], "web_search", {"query": topic}, timeout=10.0
            )

            # Step 3: Extract text from search results
            search_text = " ".join([result["title"] for result in search_result["result"]["results"]])

            # Step 4: Delegate analysis task
            logger.info(f"Delegating analysis to {analysis_agents[0]}")
            analysis_result = await self.communicator.delegate_task(
                analysis_agents[0], "analyze_text", {"text": search_text}, timeout=10.0
            )

            # Step 5: Combine results
            return {
                "topic": topic,
                "search_results": search_result["result"],
                "analysis": analysis_result["result"],
                "workflow": ["search", "analyze", "combine"],
                "agents_used": {
                    "search": search_agents[0],
                    "analysis": analysis_agents[0],
                },
            }

        except Exception as e:
            logger.error(f"Coordination failed: {e}")
            raise


async def demo_inter_agent_communication():
    """
    Demonstrate inter-agent communication patterns.
    """
    print("🤖 Inter-Agent Communication (A2A) Demo")
    print("=" * 50)

    # Create shared registry
    registry = AgentRegistry()

    # Create specialized agents
    search_agent = SearchAgent("search-01", registry)
    analysis_agent = AnalysisAgent("analysis-01", registry)
    coordinator = CoordinatorAgent("coordinator-01", registry)

    try:
        # Start all agents
        await search_agent.start("http://localhost:8001")
        await analysis_agent.start("http://localhost:8002")
        await coordinator.start("http://localhost:8003")

        print(f"\n📡 Active agents: {registry.discover_agents()}")

        # Demo 1: Service Discovery
        print(f"\n🔍 Discovering capabilities of {search_agent.agent_id}...")
        capabilities = await coordinator.communicator.discover_capabilities("search-01")
        for cap in capabilities:
            print(f"  - {cap.name}: {cap.description}")

        # Demo 2: Direct Task Delegation
        print(f"\n📋 Delegating search task...")
        result = await coordinator.communicator.delegate_task(
            "search-01", "web_search", {"query": "artificial intelligence"}
        )
        print(f"  Search results: {len(result['result']['results'])} items found")

        # Demo 3: Multi-Agent Workflow
        print(f"\n🔄 Executing multi-agent workflow...")
        workflow_result = await coordinator.execute_capability(
            "research_and_analyze", {"topic": "machine learning"}
        )
        print(f"  Workflow completed using agents: {workflow_result['agents_used']}")
        print(f"  Analysis sentiment: {workflow_result['analysis']['sentiment']}")

        # Demo 4: Error Handling
        print(f"\n⚠️  Testing error handling...")
        try:
            await coordinator.communicator.delegate_task(
                "nonexistent-agent", "some_task", {}, timeout=5.0
            )
        except AgentUnavailableError as e:
            print(f"  ✅ Properly handled: {e}")

        print(f"\n✅ Inter-agent communication demo completed successfully!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise
    finally:
        # Clean up
        await coordinator.stop()
        await analysis_agent.stop()
        await search_agent.stop()


async def main():
    """Run the inter-agent communication demo."""
    try:
        await demo_inter_agent_communication()
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
