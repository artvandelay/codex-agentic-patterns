#!/usr/bin/env python3
"""
Complete Agent Example Usage Demo

This file demonstrates how to use the Codex-inspired agent implementation
combining multiple agentic design patterns.

Prerequisites:
    pip install openai aiohttp

Usage:
    python example_usage.py

This example shows:
- Pattern 1: Prompt Chaining (multi-turn conversations)
- Pattern 2: Routing (tool dispatch)
- Pattern 5: Tool Use (external integration)
- Pattern 8: Memory Management (conversation persistence)
- Pattern 12: Exception Handling (retry logic)
- Pattern 13: Human-in-the-Loop (approval workflows)
"""

import asyncio
import os
from complete_agent import CodexInspiredAgent


async def demo_basic_chat():
    """Demonstrate basic conversation with the agent."""
    print("🤖 Basic Chat Demo")
    print("=" * 50)

    agent = CodexInspiredAgent()

    # Simple conversation
    response = await agent.run("Hello! Can you help me understand Python decorators?")
    print(f"Agent: {response}")

    # Follow-up question (demonstrates memory)
    response = await agent.run("Can you show me a practical example?")
    print(f"Agent: {response}")

    print("✅ Basic chat demo completed!\n")


async def demo_tool_usage():
    """Demonstrate tool usage capabilities."""
    print("🔧 Tool Usage Demo")
    print("=" * 50)

    agent = CodexInspiredAgent()

    # Ask about current time (triggers time tool)
    response = await agent.run("What time is it right now?")
    print(f"Agent: {response}")

    # Ask about weather (triggers weather tool)
    response = await agent.run("What's the weather like in New York?")
    print(f"Agent: {response}")

    print("✅ Tool usage demo completed!\n")


async def demo_error_handling():
    """Demonstrate error handling and recovery."""
    print("🛡️ Error Handling Demo")
    print("=" * 50)

    agent = CodexInspiredAgent()

    # Try something that might fail (invalid tool call)
    try:
        response = await agent.run("Please run a command that doesn't exist")
        print(f"Agent: {response}")
    except Exception as e:
        print(f"Error handled gracefully: {e}")

    print("✅ Error handling demo completed!\n")


async def demo_multi_turn_workflow():
    """Demonstrate a complex multi-turn workflow."""
    print("🔄 Multi-Turn Workflow Demo")
    print("=" * 50)

    agent = CodexInspiredAgent()

    # Complex task requiring multiple steps
    response = await agent.run("""
    I need to analyze a Python project. Here's what I want to do:

    1. First, list all Python files in the current directory
    2. Then read one of them and analyze its structure
    3. Finally, suggest improvements to the code

    Can you help me with this step by step?
    """)

    print(f"Agent: {response}")
    print("✅ Multi-turn workflow demo completed!\n")


async def demo_approval_workflow():
    """Demonstrate human-in-the-loop approval workflow."""
    print("👤 Human-in-the-Loop Demo")
    print("=" * 50)

    agent = CodexInspiredAgent(enable_approvals=True)

    # This would normally require approval for certain operations
    response = await agent.run("Please create a summary of the current directory structure")

    print(f"Agent: {response}")
    print("✅ Approval workflow demo completed!\n")


async def main():
    """Run all demos."""
    print("🚀 Codex-Inspired Agent - Complete Demo")
    print("=" * 60)

    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        print("   Or create a .env file with OPENAI_API_KEY=your-key-here")
        print("   Some demos may not work without a valid API key.\n")

    try:
        # Run demos (comment out any you don't want to run)
        await demo_basic_chat()
        await demo_tool_usage()
        await demo_error_handling()
        await demo_multi_turn_workflow()
        await demo_approval_workflow()

        print("🎉 All demos completed successfully!")

    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("Make sure your OPENAI_API_KEY is set correctly")


if __name__ == "__main__":
    asyncio.run(main())
