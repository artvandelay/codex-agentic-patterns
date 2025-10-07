#!/usr/bin/env python3
"""
Advanced Pattern 5: Rollout System (Session Replay & Debugging)

This demonstrates Codex's sophisticated session persistence system using JSONL
(JSON Lines) format. It's NOT just logging - it's a complete replay system.

Key Features:
1. Append-only JSONL files (never modify past events)
2. Self-contained events (each line is complete)
3. Session resumption (load file → rebuild exact state)
4. Git-friendly (line-by-line diffs work)
5. Tool-inspectable (jq, grep, awk work)
6. Multiple event types (messages, tool calls, metadata)

Why JSONL over Database?
- Simple: No schema migrations
- Diffable: Git tracks changes
- Inspectable: Use standard Unix tools
- Portable: Just a text file
- Efficient: Append-only writes

Extracted from: codex-rs/core/src/rollout/recorder.rs (lines 1-268)

This is how production systems enable debugging and session replay.
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import uuid


# ============================================================================
# Event Types (Rollout Items)
# ============================================================================

class EventType(Enum):
    """Types of events that can be recorded."""
    SESSION_META = "session_meta"
    USER_MESSAGE = "user_message"
    ASSISTANT_MESSAGE = "assistant_message"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ERROR = "error"
    SYSTEM_EVENT = "system_event"


@dataclass
class SessionMeta:
    """Session metadata (first event in rollout)."""
    session_id: str
    timestamp: str
    cwd: str
    user_instructions: Optional[str] = None
    model: str = "gpt-4"
    version: str = "1.0.0"


@dataclass
class UserMessage:
    """User input message."""
    content: str
    timestamp: str


@dataclass
class AssistantMessage:
    """Assistant response message."""
    content: str
    timestamp: str
    reasoning: Optional[str] = None


@dataclass
class ToolCall:
    """Tool/function call from assistant."""
    call_id: str
    tool_name: str
    arguments: Dict[str, Any]
    timestamp: str


@dataclass
class ToolResult:
    """Result from tool execution."""
    call_id: str
    tool_name: str
    result: Any
    error: Optional[str] = None
    exit_code: Optional[int] = None
    duration: Optional[float] = None
    timestamp: str


@dataclass
class SystemEvent:
    """System-level event (errors, warnings, etc.)."""
    event_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str


# Union type for all possible events
RolloutEvent = Union[
    SessionMeta,
    UserMessage,
    AssistantMessage,
    ToolCall,
    ToolResult,
    SystemEvent,
]


# ============================================================================
# Rollout Line Format
# ============================================================================

@dataclass
class RolloutLine:
    """
    Single line in rollout file.
    
    Each line is a complete, self-contained event.
    Format: {"type": "...", "item": {...}, "seq": N}
    """
    type: EventType
    item: Dict[str, Any]
    seq: int  # Sequence number for ordering
    
    def to_json(self) -> str:
        """Serialize to JSON (one line)."""
        return json.dumps({
            "type": self.type.value,
            "item": self.item,
            "seq": self.seq,
        }, separators=(',', ':'))  # Compact format
    
    @staticmethod
    def from_json(line: str) -> 'RolloutLine':
        """Deserialize from JSON line."""
        data = json.loads(line)
        return RolloutLine(
            type=EventType(data["type"]),
            item=data["item"],
            seq=data["seq"],
        )


# ============================================================================
# Rollout Recorder (Append-Only Writer)
# ============================================================================

class RolloutRecorder:
    """
    Records session events to append-only JSONL file.
    
    From: codex-rs/core/src/rollout/recorder.rs
    
    Key Design Decisions:
    1. Append-only: Never modify existing lines
    2. Flush immediately: Don't buffer in memory
    3. Self-contained: Each line has full context
    4. Resumable: Can load and continue later
    """
    
    def __init__(self, session_id: str, sessions_dir: Path):
        self.session_id = session_id
        self.sessions_dir = sessions_dir
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate rollout filename with timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
        self.rollout_path = sessions_dir / f"rollout-{timestamp}-{session_id}.jsonl"
        
        self.sequence = 0
        self._file = None
        self._opened = False
    
    async def open(self):
        """Open file for writing."""
        if not self._opened:
            self._file = open(self.rollout_path, 'a', encoding='utf-8')
            self._opened = True
    
    async def close(self):
        """Close file and flush."""
        if self._file:
            self._file.flush()
            self._file.close()
            self._opened = False
    
    async def record_session_meta(self, meta: SessionMeta):
        """Record session metadata (first event)."""
        await self._write_event(EventType.SESSION_META, asdict(meta))
    
    async def record_user_message(self, message: UserMessage):
        """Record user input."""
        await self._write_event(EventType.USER_MESSAGE, asdict(message))
    
    async def record_assistant_message(self, message: AssistantMessage):
        """Record assistant response."""
        await self._write_event(EventType.ASSISTANT_MESSAGE, asdict(message))
    
    async def record_tool_call(self, call: ToolCall):
        """Record tool/function call."""
        await self._write_event(EventType.TOOL_CALL, asdict(call))
    
    async def record_tool_result(self, result: ToolResult):
        """Record tool execution result."""
        await self._write_event(EventType.TOOL_RESULT, asdict(result))
    
    async def record_system_event(self, event: SystemEvent):
        """Record system event (error, warning, etc.)."""
        await self._write_event(EventType.SYSTEM_EVENT, asdict(event))
    
    async def _write_event(self, event_type: EventType, item: Dict[str, Any]):
        """Write single event to file."""
        if not self._opened:
            await self.open()
        
        self.sequence += 1
        line = RolloutLine(
            type=event_type,
            item=item,
            seq=self.sequence,
        )
        
        # Write as single line + newline
        self._file.write(line.to_json() + '\n')
        
        # Flush immediately for crash safety
        self._file.flush()
        os.fsync(self._file.fileno())


# ============================================================================
# Session Replayer (Load & Rebuild State)
# ============================================================================

@dataclass
class ReplayedSession:
    """Rebuilt session state from rollout file."""
    session_id: str
    meta: SessionMeta
    events: List[RolloutLine]
    conversation: List[Dict[str, Any]]  # Reconstructed conversation
    tool_calls: Dict[str, ToolCall]  # call_id -> ToolCall
    tool_results: Dict[str, ToolResult]  # call_id -> ToolResult


class RolloutReplayer:
    """
    Load and replay session from rollout file.
    
    From: codex-rs/core/src/rollout/recorder.rs:199-268
    
    Use Cases:
    1. Resume interrupted session
    2. Debug agent behavior
    3. Replay for testing
    4. Analyze conversation flow
    """
    
    @staticmethod
    async def load_session(rollout_path: Path) -> ReplayedSession:
        """Load complete session from rollout file."""
        if not rollout_path.exists():
            raise FileNotFoundError(f"Rollout file not found: {rollout_path}")
        
        print(f"📂 Loading session from: {rollout_path.name}")
        
        events: List[RolloutLine] = []
        session_meta: Optional[SessionMeta] = None
        conversation: List[Dict[str, Any]] = []
        tool_calls: Dict[str, ToolCall] = {}
        tool_results: Dict[str, ToolResult] = {}
        
        # Read file line by line
        with open(rollout_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    rollout_line = RolloutLine.from_json(line)
                    events.append(rollout_line)
                    
                    # Extract session meta (first event)
                    if rollout_line.type == EventType.SESSION_META and session_meta is None:
                        session_meta = SessionMeta(**rollout_line.item)
                    
                    # Reconstruct conversation
                    elif rollout_line.type == EventType.USER_MESSAGE:
                        msg = UserMessage(**rollout_line.item)
                        conversation.append({
                            "role": "user",
                            "content": msg.content,
                            "timestamp": msg.timestamp,
                        })
                    
                    elif rollout_line.type == EventType.ASSISTANT_MESSAGE:
                        msg = AssistantMessage(**rollout_line.item)
                        conversation.append({
                            "role": "assistant",
                            "content": msg.content,
                            "timestamp": msg.timestamp,
                            "reasoning": msg.reasoning,
                        })
                    
                    # Track tool calls
                    elif rollout_line.type == EventType.TOOL_CALL:
                        call = ToolCall(**rollout_line.item)
                        tool_calls[call.call_id] = call
                    
                    elif rollout_line.type == EventType.TOOL_RESULT:
                        result = ToolResult(**rollout_line.item)
                        tool_results[result.call_id] = result
                
                except json.JSONDecodeError as e:
                    print(f"⚠️  Warning: Failed to parse line {line_num}: {e}")
                    continue
                except Exception as e:
                    print(f"⚠️  Warning: Error processing line {line_num}: {e}")
                    continue
        
        if session_meta is None:
            raise ValueError("No session metadata found in rollout file")
        
        print(f"✅ Loaded {len(events)} events")
        print(f"   Conversation turns: {len(conversation)}")
        print(f"   Tool calls: {len(tool_calls)}")
        print(f"   Tool results: {len(tool_results)}")
        
        return ReplayedSession(
            session_id=session_meta.session_id,
            meta=session_meta,
            events=events,
            conversation=conversation,
            tool_calls=tool_calls,
            tool_results=tool_results,
        )
    
    @staticmethod
    def print_conversation(session: ReplayedSession):
        """Pretty-print conversation from replayed session."""
        print("\n" + "=" * 80)
        print(f"SESSION: {session.session_id}")
        print(f"Model: {session.meta.model}")
        print(f"CWD: {session.meta.cwd}")
        print("=" * 80)
        
        for i, turn in enumerate(session.conversation, 1):
            role = turn["role"].upper()
            content = turn["content"]
            timestamp = turn.get("timestamp", "")
            
            print(f"\n[{i}] {role} ({timestamp})")
            print("-" * 80)
            print(content[:500] + ("..." if len(content) > 500 else ""))
            
            if turn.get("reasoning"):
                print(f"\n💭 Reasoning: {turn['reasoning'][:200]}")
        
        # Show tool calls
        if session.tool_calls:
            print("\n" + "=" * 80)
            print("TOOL CALLS")
            print("=" * 80)
            for call_id, call in session.tool_calls.items():
                print(f"\n🔧 {call.tool_name} [{call_id[:8]}]")
                print(f"   Args: {call.arguments}")
                
                if call_id in session.tool_results:
                    result = session.tool_results[call_id]
                    status = "✅" if result.error is None else "❌"
                    print(f"   {status} Result: {str(result.result)[:100]}")
                    if result.error:
                        print(f"      Error: {result.error}")


# ============================================================================
# Session Manager (High-Level API)
# ============================================================================

class SessionManager:
    """
    High-level API for session recording and replay.
    
    Usage:
        # Start new session
        session = await SessionManager.create_session(...)
        await session.user_says("Hello!")
        await session.assistant_says("Hi there!")
        await session.close()
        
        # Resume session
        session = await SessionManager.resume_session(rollout_path)
        await session.user_says("Continue...")
    """
    
    def __init__(self, recorder: RolloutRecorder, meta: SessionMeta):
        self.recorder = recorder
        self.meta = meta
    
    @staticmethod
    async def create_session(
        sessions_dir: Path,
        cwd: str,
        user_instructions: Optional[str] = None,
        model: str = "gpt-4",
    ) -> 'SessionManager':
        """Create new session with recording."""
        session_id = str(uuid.uuid4())
        
        meta = SessionMeta(
            session_id=session_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            cwd=cwd,
            user_instructions=user_instructions,
            model=model,
        )
        
        recorder = RolloutRecorder(session_id, sessions_dir)
        await recorder.open()
        await recorder.record_session_meta(meta)
        
        print(f"📝 Created session: {session_id}")
        print(f"   Rollout: {recorder.rollout_path.name}")
        
        return SessionManager(recorder, meta)
    
    @staticmethod
    async def resume_session(rollout_path: Path) -> 'SessionManager':
        """Resume existing session from rollout file."""
        replayed = await RolloutReplayer.load_session(rollout_path)
        
        # Create recorder that appends to existing file
        recorder = RolloutRecorder(replayed.session_id, rollout_path.parent)
        recorder.rollout_path = rollout_path
        recorder.sequence = len(replayed.events)
        await recorder.open()
        
        print(f"🔄 Resumed session: {replayed.session_id}")
        
        return SessionManager(recorder, replayed.meta)
    
    async def user_says(self, content: str):
        """Record user message."""
        msg = UserMessage(
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await self.recorder.record_user_message(msg)
    
    async def assistant_says(self, content: str, reasoning: Optional[str] = None):
        """Record assistant message."""
        msg = AssistantMessage(
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
            reasoning=reasoning,
        )
        await self.recorder.record_assistant_message(msg)
    
    async def tool_called(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Record tool call, return call_id."""
        call_id = str(uuid.uuid4())
        call = ToolCall(
            call_id=call_id,
            tool_name=tool_name,
            arguments=arguments,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await self.recorder.record_tool_call(call)
        return call_id
    
    async def tool_returned(
        self,
        call_id: str,
        tool_name: str,
        result: Any,
        error: Optional[str] = None,
        exit_code: Optional[int] = None,
        duration: Optional[float] = None,
    ):
        """Record tool result."""
        res = ToolResult(
            call_id=call_id,
            tool_name=tool_name,
            result=result,
            error=error,
            exit_code=exit_code,
            duration=duration,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await self.recorder.record_tool_result(res)
    
    async def system_event(self, event_type: str, message: str, details: Optional[Dict] = None):
        """Record system event."""
        event = SystemEvent(
            event_type=event_type,
            message=message,
            details=details,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await self.recorder.record_system_event(event)
    
    async def close(self):
        """Close session and flush to disk."""
        await self.recorder.close()
        print(f"💾 Session saved: {self.recorder.rollout_path}")


# ============================================================================
# Demo
# ============================================================================

async def demo_recording():
    """Demo: Record a session."""
    print("=" * 80)
    print("DEMO 1: Recording a Session")
    print("=" * 80)
    
    sessions_dir = Path("./demo_sessions")
    
    # Create session
    session = await SessionManager.create_session(
        sessions_dir=sessions_dir,
        cwd="/workspace/project",
        user_instructions="Build a calculator",
        model="gpt-4",
    )
    
    # Simulate conversation
    await session.user_says("Create a Python calculator")
    
    await session.assistant_says(
        "I'll create a calculator with basic operations.",
        reasoning="User wants a simple calculator, I'll implement add/subtract/multiply/divide"
    )
    
    # Simulate tool call
    call_id = await session.tool_called("write_file", {
        "path": "calculator.py",
        "content": "def add(a, b): return a + b\n..."
    })
    
    await asyncio.sleep(0.1)  # Simulate execution time
    
    await session.tool_returned(
        call_id=call_id,
        tool_name="write_file",
        result="File written successfully",
        exit_code=0,
        duration=0.05,
    )
    
    await session.assistant_says("I've created calculator.py with basic operations!")
    
    await session.user_says("Add unit tests")
    
    await session.system_event("info", "User requested additional work")
    
    await session.assistant_says("I'll add pytest tests...")
    
    # Close session
    await session.close()
    
    return session.recorder.rollout_path


async def demo_replay(rollout_path: Path):
    """Demo: Replay a session."""
    print("\n\n" + "=" * 80)
    print("DEMO 2: Replaying a Session")
    print("=" * 80)
    
    # Load and replay
    replayed = await RolloutReplayer.load_session(rollout_path)
    
    # Print conversation
    RolloutReplayer.print_conversation(replayed)


async def demo_resume(rollout_path: Path):
    """Demo: Resume a session."""
    print("\n\n" + "=" * 80)
    print("DEMO 3: Resuming a Session")
    print("=" * 80)
    
    # Resume session
    session = await SessionManager.resume_session(rollout_path)
    
    # Continue conversation
    await session.user_says("Actually, add a GUI too")
    await session.assistant_says("I'll create a Tkinter GUI...")
    
    await session.close()
    
    print("\n✅ Session continued and saved!")


async def main():
    """Run all demos."""
    # Demo 1: Record
    rollout_path = await demo_recording()
    
    # Demo 2: Replay
    await demo_replay(rollout_path)
    
    # Demo 3: Resume
    await demo_resume(rollout_path)
    
    print("\n\n💡 Key Takeaways:")
    print("=" * 80)
    print("1. ✅ JSONL format: Simple, diffable, inspectable")
    print("2. ✅ Append-only: Never modify past events")
    print("3. ✅ Self-contained: Each line is complete")
    print("4. ✅ Resumable: Load exact state and continue")
    print("5. ✅ Tool-friendly: Use jq, grep, awk on rollout files")
    print("\nThis is how production systems enable debugging!")
    
    print(f"\n📂 Rollout file: {rollout_path}")
    print(f"\n🔍 Try these commands:")
    print(f"  jq -C '.' {rollout_path}")
    print(f"  grep 'tool_call' {rollout_path}")
    print(f"  wc -l {rollout_path}")


if __name__ == "__main__":
    asyncio.run(main())
