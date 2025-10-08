# Pattern 19: Inter-Agent Communication (A2A)

> **"Enabling agents to discover, coordinate, and communicate with each other through structured protocols"**

## 📖 Overview

Inter-Agent Communication (A2A) enables multiple agents to work together by establishing communication protocols, message passing, and coordination mechanisms. Unlike simple tool use, A2A involves agents discovering each other's capabilities and delegating complex tasks through structured interactions.

## 🎯 How Codex Implements A2A

Codex implements sophisticated agent-to-agent communication primarily through the **Model Context Protocol (MCP)**, enabling dynamic discovery and interaction with external agents and services.

### Key Implementation: MCP Client Architecture

**File**: [`codex-rs/mcp-client/src/mcp_client.rs`](https://github.com/openai/codex/blob/main/codex-rs/mcp-client/src/mcp_client.rs)

```rust
pub struct McpClient {
    stdio_client: Option<StdioClient>,
    http_client: Option<HttpClient>,
}

impl McpClient {
    // Agent discovery - list available tools from other agents
    pub async fn list_tools(&self) -> Result<Vec<Tool>, McpError> {
        match &self.stdio_client {
            Some(client) => client.list_tools().await,
            None => match &self.http_client {
                Some(client) => client.list_tools().await,
                None => Err(McpError::NoClientConfigured),
            }
        }
    }

    // Agent communication - call tools on other agents
    pub async fn call_tool(
        &self,
        name: &str,
        arguments: Value,
    ) -> Result<CallToolResult, McpError> {
        // Route message to appropriate agent
        match &self.stdio_client {
            Some(client) => client.call_tool(name, arguments).await,
            None => match &self.http_client {
                Some(client) => client.call_tool(name, arguments).await,
                None => Err(McpError::NoClientConfigured),
            }
        }
    }
}
```

### Agent Coordination in Tool Router

**File**: [`codex-rs/core/src/tools/router.rs`](https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/router.rs)

```rust
pub fn route_response_item(
    item: &ResponseItem,
    mcp_client: &Option<Arc<McpClient>>,
) -> Result<ToolHandler, ToolRouterError> {
    match item {
        ResponseItem::FunctionCall(func_call) => {
            // Route to MCP agent if available
            if let Some(client) = mcp_client {
                return Ok(ToolHandler::Mcp {
                    client: client.clone(),
                    call: func_call.clone(),
                });
            }
            
            // Fallback to local tools
            Ok(ToolHandler::Function(func_call.clone()))
        }
        _ => Err(ToolRouterError::UnsupportedItem),
    }
}
```

### Message Protocol Handling

**File**: [`codex-rs/mcp-types/src/lib.rs`](https://github.com/openai/codex/blob/main/codex-rs/mcp-types/src/lib.rs)

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct CallToolRequest {
    pub name: String,
    pub arguments: Option<Value>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CallToolResult {
    pub content: Vec<TextContent>,
    pub is_error: Option<bool>,
}

// Agent message envelope
#[derive(Debug, Serialize, Deserialize)]
pub struct McpMessage {
    pub jsonrpc: String,
    pub id: Option<Value>,
    pub method: Option<String>,
    pub params: Option<Value>,
    pub result: Option<Value>,
}
```

## 🔑 Key A2A Patterns in Codex

### 1. **Service Discovery**
```rust
// Agents discover each other's capabilities
let tools = mcp_client.list_tools().await?;
for tool in tools {
    println!("Available: {} - {}", tool.name, tool.description);
}
```

### 2. **Delegation & Coordination**
```rust
// Primary agent delegates to specialized agent
let search_result = mcp_client.call_tool(
    "web_search",
    json!({"query": "latest AI research"})
).await?;

// Process results from other agent
let analysis = analyze_search_results(search_result.content)?;
```

### 3. **Error Handling in Communication**
```rust
// Robust error handling for agent communication
match mcp_client.call_tool(name, args).await {
    Ok(result) => process_agent_response(result),
    Err(McpError::AgentTimeout) => retry_with_backoff(),
    Err(McpError::AgentUnavailable) => fallback_to_local_tool(),
    Err(e) => return Err(e.into()),
}
```

### 4. **Protocol Abstraction**
```rust
// Support multiple communication protocols
pub enum AgentTransport {
    Stdio(StdioClient),
    Http(HttpClient),
    WebSocket(WsClient),
}

impl AgentTransport {
    pub async fn send_message(&self, msg: McpMessage) -> Result<McpMessage> {
        match self {
            Self::Stdio(client) => client.send(msg).await,
            Self::Http(client) => client.post(msg).await,
            Self::WebSocket(client) => client.send(msg).await,
        }
    }
}
```

## 🎯 Key Takeaways

### ✅ **Production Insights**

1. **Protocol Standardization**: Codex uses MCP as a standard protocol for agent communication, ensuring interoperability.

2. **Transport Flexibility**: Support for multiple transport mechanisms (stdio, HTTP, WebSocket) allows agents to communicate across different environments.

3. **Graceful Degradation**: When agent communication fails, Codex falls back to local tools or alternative agents.

4. **Discovery Before Use**: Agents dynamically discover each other's capabilities rather than hardcoding dependencies.

### 🏗️ **Architecture Benefits**

- **Scalability**: New agents can be added without modifying existing code
- **Fault Tolerance**: Communication failures don't crash the system
- **Modularity**: Each agent can specialize in specific domains
- **Flexibility**: Support for various communication patterns (request/response, streaming, etc.)

## 🔗 Related Patterns

- **Pattern 2: Routing** - Routes messages between agents
- **Pattern 10: MCP Integration** - Underlying protocol for A2A
- **Pattern 12: Exception Handling** - Handles communication failures
- **Pattern 5: Tool Use** - Basic building block for agent capabilities

## 📚 Further Reading

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Codex MCP Implementation](https://github.com/openai/codex/tree/main/codex-rs/mcp-client)
- [Agent Communication Patterns](https://en.wikipedia.org/wiki/Agent_communication_language)

---

**Next**: [Pattern 20: Evaluation and Monitoring →](../20-evaluation-monitoring/README.md)
