#!/usr/bin/env python3
"""
Pattern 5: Tool Use - Simple Example

Demonstrates basic tool/function calling with OpenAI's function calling API.

Inspired by: codex-rs/core/src/exec.rs and tool system
"""

import os
import json
import subprocess
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# Define available tools
def get_current_time() -> str:
    """Get the current time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_weather(location: str) -> str:
    """
    Get weather information for a location.
    (Mock implementation - real version would call weather API)
    """
    # Mock data
    weather_data = {
        "New York": "Sunny, 72°F",
        "London": "Cloudy, 15°C",
        "Tokyo": "Rainy, 20°C",
        "default": "Weather data not available"
    }
    return weather_data.get(location, weather_data["default"])


def run_shell_command(command: str) -> str:
    """
    Execute a shell command (DANGEROUS - use with caution!).
    In production, this should be sandboxed like Codex does.
    """
    # Whitelist of safe commands (inspired by Codex safety checks)
    safe_commands = ["ls", "pwd", "echo", "date", "whoami"]
    
    cmd_parts = command.split()
    if not cmd_parts or cmd_parts[0] not in safe_commands:
        return f"ERROR: Command '{command}' not allowed. Only safe commands permitted."
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5  # Timeout like Codex
        )
        return result.stdout if result.stdout else result.stderr
    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out"
    except Exception as e:
        return f"ERROR: {str(e)}"


def calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.
    """
    try:
        # Only allow basic math operations
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "ERROR: Invalid characters in expression"
        
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"ERROR: {str(e)}"


# Map function names to implementations
AVAILABLE_TOOLS = {
    "get_current_time": get_current_time,
    "get_weather": get_weather,
    "run_shell_command": run_shell_command,
    "calculate": calculate,
}


# Define tool specifications for OpenAI
TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name (e.g., 'New York', 'London')"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": "Execute a safe shell command (ls, pwd, echo, date, whoami only)",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression (e.g., '2 + 2', '10 * 5')"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]


def execute_tool(tool_name: str, tool_args: dict) -> str:
    """
    Execute a tool and return its result.
    Similar to: codex-rs/core/src/tools/mod.rs
    """
    print(f"  🔧 Executing tool: {tool_name}")
    print(f"  📝 Arguments: {tool_args}")
    
    tool_function = AVAILABLE_TOOLS.get(tool_name)
    if not tool_function:
        return f"ERROR: Unknown tool '{tool_name}'"
    
    try:
        # Call the tool with arguments
        if tool_args:
            result = tool_function(**tool_args)
        else:
            result = tool_function()
        
        print(f"  ✅ Result: {result}")
        return result
    except Exception as e:
        error_msg = f"ERROR executing {tool_name}: {str(e)}"
        print(f"  ❌ {error_msg}")
        return error_msg


def agent_with_tools(user_query: str, max_iterations: int = 5) -> str:
    """
    Run an agent loop with tool use.
    
    Similar to Codex's turn-based execution:
    1. LLM generates response (possibly with tool calls)
    2. Execute tools
    3. Feed results back to LLM
    4. Repeat until LLM gives final answer
    """
    print(f"\n{'=' * 60}")
    print(f"USER QUERY: {user_query}")
    print(f"{'=' * 60}\n")
    
    messages = [{"role": "user", "content": user_query}]
    
    for iteration in range(max_iterations):
        print(f"\n{'─' * 60}")
        print(f"ITERATION {iteration + 1}")
        print(f"{'─' * 60}")
        
        # Call LLM with tools
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=TOOL_SPECS,
            tool_choice="auto",
        )
        
        response_message = response.choices[0].message
        messages.append(response_message)
        
        # Check if LLM wants to use tools
        tool_calls = response_message.tool_calls
        
        if not tool_calls:
            # LLM provided final answer
            final_answer = response_message.content
            print(f"\n✅ FINAL ANSWER:")
            print(final_answer)
            return final_answer
        
        # Execute all tool calls
        print(f"\n🔨 LLM requested {len(tool_calls)} tool(s):")
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Execute the tool
            tool_result = execute_tool(function_name, function_args)
            
            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": tool_result,
            })
        
        print(f"\n📤 Feeding {len(tool_calls)} result(s) back to LLM...")
    
    return "ERROR: Max iterations reached without final answer"


def demo_tool_use():
    """Demonstrate tool use with various queries."""
    
    test_queries = [
        "What time is it right now?",
        "What's the weather like in Tokyo?",
        "Calculate 15% of 2500",
        "What files are in the current directory?",
        "What time is it in New York and what's the weather there?",
    ]
    
    print("🚀 Tool Use Pattern Demo")
    print("=" * 60)
    
    for query in test_queries:
        result = agent_with_tools(query)
        print("\n" + "═" * 60 + "\n")
    
    print("\n💡 Key Observations:")
    print("1. LLM decides WHEN to use tools")
    print("2. LLM decides WHICH tools to use")
    print("3. Tools extend capabilities beyond training data")
    print("4. Tool results feed back into conversation")
    print("5. Multiple tools can be used in sequence")


if __name__ == "__main__":
    try:
        demo_tool_use()
        
        print("\n\n💡 Key Lessons:")
        print("1. ✅ Tools give agents real-world capabilities")
        print("2. ✅ LLM orchestrates tool use intelligently")
        print("3. ✅ Safety checks are CRITICAL (whitelist, timeout, sandbox)")
        print("4. ✅ Tool results integrate seamlessly into conversation")
        print("5. ⚠️  In production, use proper sandboxing like Codex does")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure OPENAI_API_KEY is set:")
        print("   export OPENAI_API_KEY='your-key-here'")

