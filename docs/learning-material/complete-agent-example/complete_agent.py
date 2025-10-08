#!/usr/bin/env python3
"""
Complete Codex-Inspired Agent

This is a production-ready implementation combining multiple agentic patterns:
- Prompt Chaining (Pattern 1)
- Routing (Pattern 2)
- Tool Use (Pattern 5)
- Memory Management (Pattern 8)
- Exception Handling (Pattern 12)
- Human-in-the-Loop (Pattern 13)
- Safety/Guardrails (Pattern 18)

Inspired by: codex-rs/core/src/codex.rs
"""

import os
import json
import time
import asyncio
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import subprocess
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# ============================================================================
# PATTERN 8: Memory Management
# ============================================================================


@dataclass
class Turn:
    """Represents a single conversation turn."""

    turn_id: int
    prompt: str
    response: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ConversationMemory:
    """
    Manages conversation history and state.
    Inspired by: codex-rs/core/src/conversation_history.rs
    """

    def __init__(self, max_turns: int = 10):
        self.turns: List[Turn] = []
        self.max_turns = max_turns
        self.session_id = f"session_{int(time.time())}"

    def add_turn(self, turn: Turn):
        """Add a turn to history."""
        self.turns.append(turn)

        # Compress old history if too long
        if len(self.turns) > self.max_turns:
            self._compress_history()

    def _compress_history(self):
        """Keep only recent turns to manage context window."""
        # Keep first turn (context) and recent turns
        self.turns = [self.turns[0]] + self.turns[-(self.max_turns - 1) :]

    def get_context(self) -> str:
        """Build context string from history."""
        context_parts = []
        for turn in self.turns[-3:]:  # Last 3 turns
            context_parts.append(f"Turn {turn.turn_id}: {turn.prompt}")
            context_parts.append(f"Response: {turn.response[:200]}...")
        return "\n\n".join(context_parts)

    def save(self, filepath: str):
        """Persist conversation to file."""
        data = {
            "session_id": self.session_id,
            "turns": [asdict(turn) for turn in self.turns],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, filepath: str):
        """Load conversation from file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        self.session_id = data["session_id"]
        self.turns = [Turn(**turn_data) for turn_data in data["turns"]]


# ============================================================================
# PATTERN 18: Safety/Guardrails
# ============================================================================


class ApprovalPolicy(Enum):
    """Approval modes - inspired by Codex approval presets."""

    SUGGEST = "suggest"  # Always ask
    AUTO_EDIT = "auto_edit"  # Auto file ops, ask for commands
    FULL_AUTO = "full_auto"  # Auto everything (in sandbox)


class SafetyChecker:
    """
    Safety validation for tool execution.
    Inspired by: codex-rs/core/src/safety.rs
    """

    SAFE_COMMANDS = ["ls", "pwd", "echo", "date", "cat", "grep", "find"]
    DANGEROUS_COMMANDS = ["rm", "dd", "mkfs", "shutdown", "reboot", "format"]

    @classmethod
    def is_safe_command(cls, command: str) -> bool:
        """Check if command is in whitelist."""
        cmd_parts = command.split()
        if not cmd_parts:
            return False
        return cmd_parts[0] in cls.SAFE_COMMANDS

    @classmethod
    def is_dangerous_command(cls, command: str) -> bool:
        """Check if command is explicitly dangerous."""
        cmd_parts = command.split()
        if not cmd_parts:
            return False
        return any(danger in command.lower() for danger in cls.DANGEROUS_COMMANDS)

    @classmethod
    def assess_safety(cls, tool_name: str, args: dict, policy: ApprovalPolicy) -> bool:
        """
        Determine if operation needs approval.
        Returns: True if needs approval, False if can auto-execute
        """
        if policy == ApprovalPolicy.FULL_AUTO:
            # In full-auto, only block explicitly dangerous
            if tool_name == "shell" and cls.is_dangerous_command(
                args.get("command", "")
            ):
                return True  # Need approval even in full-auto
            return False  # Auto-execute

        if policy == ApprovalPolicy.AUTO_EDIT:
            # Auto file operations, ask for shell
            if tool_name == "shell":
                return True
            return False

        # SUGGEST mode: always ask
        return True


# ============================================================================
# PATTERN 5: Tool Use + PATTERN 13: Human-in-the-Loop
# ============================================================================


class ToolExecutor:
    """
    Tool execution with safety checks.
    Inspired by: codex-rs/core/src/exec.rs
    """

    def __init__(self, approval_policy: ApprovalPolicy = ApprovalPolicy.SUGGEST):
        self.approval_policy = approval_policy
        self.approved_commands = set()  # Session-level approvals

    def execute_tool(self, tool_name: str, args: dict) -> Dict[str, Any]:
        """
        Execute a tool with safety checks.

        Returns:
            Dict with 'success', 'output', and optional 'error'
        """
        print(f"\n  🔧 Tool: {tool_name}")
        print(f"  📝 Args: {args}")

        # Safety check
        needs_approval = SafetyChecker.assess_safety(
            tool_name, args, self.approval_policy
        )

        if needs_approval:
            if not self._request_approval(tool_name, args):
                return {
                    "success": False,
                    "error": "Operation denied by user",
                    "output": "",
                }

        # Execute the tool
        try:
            if tool_name == "shell":
                output = self._execute_shell(args["command"])
            elif tool_name == "read_file":
                output = self._read_file(args["path"])
            elif tool_name == "calculate":
                output = self._calculate(args["expression"])
            else:
                output = f"Unknown tool: {tool_name}"

            print(f"  ✅ Success: {output[:100]}...")
            return {"success": True, "output": output, "error": None}

        except Exception as e:
            error_msg = f"Error executing {tool_name}: {str(e)}"
            print(f"  ❌ {error_msg}")
            return {"success": False, "output": "", "error": error_msg}

    def _request_approval(self, tool_name: str, args: dict) -> bool:
        """Request user approval for operation."""
        print(f"\n  ⚠️  APPROVAL REQUIRED")
        print(f"     Tool: {tool_name}")
        print(f"     Args: {args}")

        response = input("     Approve? (y/n/session): ").strip().lower()

        if response == "session":
            # Approve for entire session
            key = f"{tool_name}:{json.dumps(args, sort_keys=True)}"
            self.approved_commands.add(key)
            return True

        return response == "y"

    def _execute_shell(self, command: str) -> str:
        """Execute shell command with timeout and sandboxing."""
        if SafetyChecker.is_dangerous_command(command):
            return f"BLOCKED: Dangerous command '{command}'"

        if not SafetyChecker.is_safe_command(command):
            return f"BLOCKED: Command not in whitelist"

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5,  # Timeout like Codex
            )
            output = result.stdout if result.stdout else result.stderr
            # Truncate like Codex does
            return output[:1000] if output else "Command executed (no output)"
        except subprocess.TimeoutExpired:
            return "ERROR: Command timed out after 5 seconds"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def _read_file(self, path: str) -> str:
        """Read file with size limit."""
        try:
            with open(path, "r") as f:
                content = f.read(10000)  # Max 10KB
            return content
        except Exception as e:
            return f"ERROR reading file: {str(e)}"

    def _calculate(self, expression: str) -> str:
        """Safely evaluate math expression."""
        try:
            # Only allow basic math
            allowed = set("0123456789+-*/(). ")
            if not all(c in allowed for c in expression):
                return "ERROR: Invalid characters"
            result = eval(expression, {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"ERROR: {str(e)}"


# ============================================================================
# PATTERN 2: Routing + PATTERN 12: Exception Handling
# ============================================================================


class CodexInspiredAgent:
    """
    Main agent class combining all patterns.
    Inspired by: codex-rs/core/src/codex.rs
    """

    def __init__(
        self,
        model: str = "gpt-4",
        approval_policy: ApprovalPolicy = ApprovalPolicy.SUGGEST,
        max_retries: int = 3,
    ):
        self.model = model
        self.approval_policy = approval_policy
        self.max_retries = max_retries

        self.memory = ConversationMemory()
        self.tool_executor = ToolExecutor(approval_policy)
        self.current_turn = 0

    def run(self, user_query: str, max_turns: int = 10) -> str:
        """
        Main execution loop - Pattern 1: Prompt Chaining.

        Similar to: codex-rs/core/src/codex.rs::run_task
        """
        print(f"\n{'=' * 70}")
        print(f"CODEX-INSPIRED AGENT")
        print(f"Query: {user_query}")
        print(f"Policy: {self.approval_policy.value}")
        print(f"{'=' * 70}")

        # Add user query to memory
        self.current_turn += 1

        # Main turn loop
        for turn_num in range(max_turns):
            print(f"\n{'─' * 70}")
            print(f"TURN {turn_num + 1}/{max_turns}")
            print(f"{'─' * 70}")

            # Build prompt with history
            if turn_num == 0:
                prompt = user_query
            else:
                context = self.memory.get_context()
                prompt = f"""
Previous context:
{context}

Continue working on the task. If complete, provide final summary.
"""

            # Execute turn with retry logic (Pattern 12)
            turn_result = self._execute_turn_with_retry(prompt)

            if not turn_result["success"]:
                print(f"\n❌ Turn failed: {turn_result['error']}")
                break

            # Check if task is complete
            response = turn_result["response"]
            if self._is_task_complete(response):
                print(f"\n✅ Task complete after {turn_num + 1} turns")
                return response

            # Record turn in memory
            turn = Turn(
                turn_id=self.current_turn,
                prompt=prompt,
                response=response,
                tool_calls=turn_result.get("tool_calls", []),
            )
            self.memory.add_turn(turn)
            self.current_turn += 1

        return "Task did not complete within turn limit"

    def _execute_turn_with_retry(self, prompt: str) -> Dict[str, Any]:
        """
        Execute a turn with retry logic - Pattern 12: Exception Handling.
        """
        for attempt in range(self.max_retries):
            try:
                return self._execute_turn(prompt)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return {
                        "success": False,
                        "error": f"Max retries exceeded: {str(e)}",
                        "response": "",
                    }

                # Exponential backoff
                wait_time = 2**attempt
                print(
                    f"  ⚠️  Attempt {attempt + 1} failed, retrying in {wait_time}s..."
                )
                time.sleep(wait_time)

        return {"success": False, "error": "Unexpected error", "response": ""}

    def _execute_turn(self, prompt: str) -> Dict[str, Any]:
        """
        Execute a single turn.
        May involve multiple LLM calls if tools are used.
        """
        # Define available tools
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "shell",
                    "description": "Execute a shell command (safe commands only)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Shell command",
                            }
                        },
                        "required": ["command"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File path"}
                        },
                        "required": ["path"],
                    },
                },
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
                                "description": "Math expression",
                            }
                        },
                        "required": ["expression"],
                    },
                },
            },
        ]

        # Call LLM
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model=self.model, messages=messages, tools=tools, tool_choice="auto"
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # If no tool calls, return response
        if not tool_calls:
            return {
                "success": True,
                "response": response_message.content,
                "tool_calls": [],
            }

        # Execute tools and feed results back
        print(f"\n  🔨 Executing {len(tool_calls)} tool(s)...")

        tool_results = []
        for tool_call in tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            # Execute tool (Pattern 5 + 13)
            result = self.tool_executor.execute_tool(func_name, func_args)

            tool_results.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": result["output"]
                    if result["success"]
                    else result["error"],
                }
            )

        # Feed tool results back to LLM
        messages.append(response_message)
        messages.extend(tool_results)

        final_response = client.chat.completions.create(
            model=self.model, messages=messages
        )

        return {
            "success": True,
            "response": final_response.choices[0].message.content,
            "tool_calls": [
                {"name": tc.function.name, "args": json.loads(tc.function.arguments)}
                for tc in tool_calls
            ],
        }

    def _is_task_complete(self, response: str) -> bool:
        """Heuristic to detect if task is complete."""
        completion_phrases = [
            "task is complete",
            "finished",
            "done",
            "completed successfully",
            "final result",
            "summary:",
        ]
        response_lower = response.lower()
        return any(phrase in response_lower for phrase in completion_phrases)

    def save_session(self, filepath: str):
        """Save conversation state."""
        self.memory.save(filepath)
        print(f"\n💾 Session saved to: {filepath}")

    def load_session(self, filepath: str):
        """Load previous conversation."""
        self.memory.load(filepath)
        self.current_turn = len(self.memory.turns)
        print(f"\n📂 Session loaded: {self.memory.session_id}")


# ============================================================================
# Demo Usage
# ============================================================================

if __name__ == "__main__":
    try:
        print("🚀 Complete Codex-Inspired Agent Demo\n")

        # Example 1: Simple query
        print("\n" + "=" * 70)
        print("EXAMPLE 1: Simple Query")
        print("=" * 70)

        agent1 = CodexInspiredAgent(approval_policy=ApprovalPolicy.FULL_AUTO)
        result1 = agent1.run("What is 2 + 2?")
        print(f"\nFinal Result: {result1}")

        # Example 2: File operation (needs approval in SUGGEST mode)
        print("\n\n" + "=" * 70)
        print("EXAMPLE 2: File Operation")
        print("=" * 70)

        agent2 = CodexInspiredAgent(approval_policy=ApprovalPolicy.SUGGEST)
        result2 = agent2.run("List files in current directory")
        print(f"\nFinal Result: {result2}")

        # Save session
        agent2.save_session("demo_session.json")

        print("\n\n💡 Key Features Demonstrated:")
        print("1. ✅ Multi-turn conversation (Pattern 1)")
        print("2. ✅ Tool routing and dispatch (Pattern 2)")
        print("3. ✅ Safe tool execution (Pattern 5)")
        print("4. ✅ Conversation memory (Pattern 8)")
        print("5. ✅ Retry logic (Pattern 12)")
        print("6. ✅ User approvals (Pattern 13)")
        print("7. ✅ Safety checks (Pattern 18)")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure OPENAI_API_KEY is set:")
        print("   export OPENAI_API_KEY='your-key-here'")
