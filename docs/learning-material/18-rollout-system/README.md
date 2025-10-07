# Pattern 24: Rollout System (Session Replay & Debugging)

> **"JSONL append-only session logs for debugging and replay"**

## 📖 Pattern Overview

The Rollout System is Codex's sophisticated session persistence mechanism using JSONL (JSON Lines) format. It's not just logging - it's a complete replay system that enables debugging, session resumption, and exact state reconstruction.

## 🎯 Key Concepts

1. **JSONL Format** - One JSON object per line, append-only
2. **Self-Contained Events** - Each line has complete context
3. **Session Resumption** - Load file and rebuild exact state
4. **Git-Friendly** - Line-by-line diffs work perfectly
5. **Tool-Inspectable** - Use jq, grep, awk on rollout files
6. **Multiple Event Types** - Messages, tool calls, metadata, errors

## 🔍 How Codex Implements This

### Location in Codebase
- **Primary**: `codex-rs/core/src/rollout/recorder.rs` (lines 1-268)
- **Support**: `codex-rs/core/src/rollout/list.rs` (session discovery)

### Why JSONL over Database?

| JSONL | Database |
|-------|----------|
| ✅ Simple (no schema) | ❌ Complex setup |
| ✅ Git-friendly diffs | ❌ Binary format |
| ✅ Tool-inspectable | ❌ Needs special tools |
| ✅ Append-only writes | ❌ Complex transactions |
| ✅ Self-contained | ❌ Schema dependencies |

### Implementation Details

```rust
// From codex-rs/core/src/rollout/recorder.rs:38-50
#[derive(Clone)]
pub struct RolloutRecorder {
    tx: Sender<RolloutCmd>,
    pub(crate) rollout_path: PathBuf,
}

// Each line in the file
#[derive(Debug, Clone, Default)]
pub(crate) struct ConversationHistory {
    /// The oldest items are at the beginning of the vector.
    items: Vec<ResponseItem>,
}

// File format: ~/.codex/sessions/rollout-2025-05-07T17-24-21-uuid.jsonl
```

### File Format Example

```jsonl
{"type":"session_meta","item":{"session_id":"abc123","timestamp":"2025-10-07T12:00:00Z","cwd":"/workspace","model":"gpt-4"},"seq":1}
{"type":"user_message","item":{"content":"Create a calculator","timestamp":"2025-10-07T12:00:01Z"},"seq":2}
{"type":"tool_call","item":{"call_id":"tool_1","tool_name":"write_file","arguments":{"path":"calc.py","content":"def add(a,b): return a+b"},"timestamp":"2025-10-07T12:00:02Z"},"seq":3}
{"type":"tool_result","item":{"call_id":"tool_1","tool_name":"write_file","result":"File written","exit_code":0,"duration":0.05,"timestamp":"2025-10-07T12:00:02Z"},"seq":4}
{"type":"assistant_message","item":{"content":"I've created a calculator with an add function!","timestamp":"2025-10-07T12:00:03Z"},"seq":5}
```

## 💡 Real-World Example from Codex

```bash
# Session file created
~/.codex/sessions/rollout-2025-10-07T12-34-56-abc123.jsonl

# Inspect with standard tools
$ jq -C '.' rollout-2025-10-07T12-34-56-abc123.jsonl
$ grep 'tool_call' rollout-2025-10-07T12-34-56-abc123.jsonl
$ wc -l rollout-2025-10-07T12-34-56-abc123.jsonl

# Resume session
$ codex resume rollout-2025-10-07T12-34-56-abc123.jsonl
# Loads exact state and continues conversation
```

## 📊 Architecture Diagram

```
Agent Turn
    ↓
┌─────────────────────────────┐
│     Session Events          │
│                             │
│ • User message              │
│ • Assistant message         │
│ • Tool call                 │
│ • Tool result               │
│ • System event              │
│ • Error                     │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│    RolloutRecorder          │
│                             │
│ 1. Add sequence number      │
│ 2. Serialize to JSON        │
│ 3. Append line to file      │
│ 4. Flush immediately        │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│      JSONL File             │
│                             │
│ Line 1: {"type":"meta"...}  │
│ Line 2: {"type":"user"...}  │
│ Line 3: {"type":"tool"...}  │
│ Line 4: {"type":"result"..} │
│ Line N: {"type":"asst"...}  │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│    Session Replay           │
│                             │
│ 1. Read file line by line   │
│ 2. Parse each JSON event    │
│ 3. Reconstruct state        │
│ 4. Resume conversation      │
└─────────────────────────────┘
```

## 🐍 Python Implementation

See the example file:
- **`pattern_advanced.py`**: Complete 500-line implementation

Key classes:
- `RolloutRecorder`: Append-only writer
- `RolloutReplayer`: State reconstruction
- `SessionManager`: High-level API
- `RolloutLine`: Single event format

Key features:
- Multiple event types (messages, tools, errors)
- Session resumption from disk
- Git-friendly line format
- Tool inspection support

## 🔑 Key Takeaways

1. ✅ **Append-Only**: Never modify existing lines
2. ✅ **Self-Contained**: Each line has complete context
3. ✅ **Resumable**: Exact state reconstruction
4. ✅ **Tool-Friendly**: Standard Unix tools work
5. ✅ **Git-Compatible**: Line-by-line diffs
6. ✅ **Performance**: Simple file I/O, no database overhead

## 🚀 When to Use

- ✅ Production agent systems
- ✅ Debugging complex conversations
- ✅ Session resumption requirements
- ✅ Audit trails and compliance
- ✅ Development and testing
- ❌ Simple scripts or demos
- ❌ Systems without persistence needs

## ⚠️ Common Pitfalls

### 1. Modifying Past Events
```python
❌ BAD: Update existing lines in file
✅ GOOD: Always append new events
```

### 2. Missing Context
```python
❌ BAD: {"type": "error", "message": "Failed"}
✅ GOOD: {"type": "error", "call_id": "abc", "tool": "write_file", "message": "Permission denied", "timestamp": "..."}
```

### 3. Non-Standard Format
```python
❌ BAD: Custom binary format
✅ GOOD: Standard JSONL with proper escaping
```

## 📚 Further Reading

- **Codex Source**: `codex-rs/core/src/rollout/recorder.rs`
- **JSONL Specification**: JSON Lines format standard
- **jq Manual**: JSON query tool for inspection
- **Git Internals**: How line-based diffs work
- **Append-Only Logs**: Database design patterns

## 🔗 Related Patterns

- **Pattern 8: Memory Management** - Conversation state
- **Pattern 12: Exception Handling** - Error logging
- **Pattern 23: Turn Diff Tracking** - Change tracking
- **Observability Patterns** - System monitoring

---

**Next**: [Complete Agent Example →](../complete-agent-example/README.mdREADME.md)
