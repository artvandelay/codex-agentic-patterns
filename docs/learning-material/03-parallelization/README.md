# Pattern 3: Parallelization

> **"Executing independent operations concurrently for better performance"**

## 📖 Pattern Overview

Parallelization enables agents to execute multiple independent operations simultaneously rather than sequentially. This significantly improves performance for tasks that don't have dependencies.

## 🎯 Key Concepts

1. **Concurrent Execution**: Run independent tasks simultaneously
2. **Dependency Management**: Identify which tasks can run in parallel
3. **Result Aggregation**: Collect and combine parallel results
4. **Error Isolation**: Handle failures in parallel tasks independently

## 🔍 How Codex Implements This

### Location in Codebase
- **Primary**: `codex-rs/core/src/tools/parallel.rs` (lines 47-67)
- **Support**: `codex-rs/core/src/codex.rs` (parallel tool calls)

### Implementation Details

Codex's `ToolCallRuntime` intelligently decides whether to execute tools in parallel or serially:

```rust
// From codex-rs/core/src/tools/parallel.rs
pub(crate) async fn handle_tool_call(
    &mut self,
    call: ToolCall,
    output_index: usize,
    output: &mut [ProcessedResponseItem],
) -> Result<(), CodexErr> {
    let supports_parallel = self.router.tool_supports_parallel(&call.tool_name);
    
    if supports_parallel {
        // Launch task in background
        self.spawn_parallel(call, output_index);
    } else {
        // Wait for pending parallel tasks to complete first
        self.resolve_pending(output).await?;
        
        // Execute serially
        let response = self.dispatch_serial(call).await?;
        output[output_index].response = Some(response);
    }
    
    Ok(())
}
```

### Key Features

1. **Per-Tool Configuration**: Each tool declares if it supports parallelization
2. **Async/Await**: Uses Tokio for efficient concurrent execution
3. **Automatic Ordering**: Serial tools wait for parallel tasks to complete
4. **Error Propagation**: Parallel task failures propagate correctly

## 💡 Real-World Example from Codex

When the LLM wants to read 3 files:

```rust
// Sequential (slow):
read("file1.py")  // 10ms
read("file2.py")  // 10ms  
read("file3.py")  // 10ms
// Total: 30ms

// Parallel (fast):
spawn(read("file1.py"))  // }
spawn(read("file2.py"))  // } All run concurrently
spawn(read("file3.py"))  // }
await_all()
// Total: ~10ms
```

## 📊 Architecture Diagram

```
┌──────────────────────────────────────────────┐
│         LLM Returns 3 Tool Calls             │
│   1. read_file("a.py")                       │
│   2. read_file("b.py")                       │
│   3. shell("ls")  ← Must run serially        │
└───────────────────┬──────────────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │   Tool Router        │
         │  Check each tool     │
         └──────────┬───────────┘
                    │
    ┌───────────────┴─────────────────┐
    │                                 │
    ▼                                 ▼
┌─────────────┐               ┌──────────────┐
│ Tools 1 & 2 │               │   Tool 3     │
│ (parallel)  │               │  (serial)    │
└──────┬──────┘               └──────┬───────┘
       │                             │
  Spawn async                    Must wait
       │                             │
       ▼                             ▼
┌──────────────────────────┐   ┌─────────────┐
│  ┌──────┐    ┌──────┐   │   │             │
│  │Task 1│    │Task 2│   │   │   Task 3    │
│  │ a.py │    │ b.py │   │   │    "ls"     │
│  └───┬──┘    └───┬──┘   │   │             │
│      │           │       │   │             │
│      └───────┬───┘       │   │             │
│              │           │   │             │
│       Wait for both      │   │  Execute    │
└──────────────┬───────────┘   └──────┬──────┘
               │                      │
               └──────────┬───────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Collect Results │
                 │  Feed to LLM     │
                 └──────────────────┘
```

## 🐍 Python Examples

See the example files:
- **`pattern_simple.py`**: Basic parallel execution with asyncio
- **`pattern_advanced.py`**: Tool-aware parallelization
- **`benchmarks.py`**: Performance comparison

## 🔑 Key Takeaways

1. ✅ **Performance**: 3x-10x speedup for I/O-bound operations
2. ✅ **Scalability**: Handles many concurrent operations efficiently
3. ✅ **Smart Execution**: Only parallelizes when safe
4. ✅ **Error Handling**: Isolated failures don't block other tasks
5. ⚠️ **Complexity**: More complex than sequential execution

## 🚀 When to Use

- ✅ Multiple independent file reads
- ✅ Batch API calls to external services
- ✅ Parallel data processing tasks
- ✅ Multiple search queries
- ❌ Tasks with dependencies (must be sequential)
- ❌ Shared mutable state (needs synchronization)

## ⚠️ Common Pitfalls

### 1. Race Conditions
```python
❌ BAD: Parallel writes to same file
✅ GOOD: Parallel reads, or parallel writes to different files
```

### 2. Resource Exhaustion
```python
❌ BAD: Spawn 1000 tasks simultaneously
✅ GOOD: Use semaphore to limit concurrency
```

### 3. Deadlocks
```python
❌ BAD: Task A waits for B, B waits for A
✅ GOOD: Clear dependency ordering
```

## 📚 Further Reading

- **Codex Source**: `codex-rs/core/src/tools/parallel.rs`
- **Async Rust**: https://rust-lang.github.io/async-book/
- **Tokio Guide**: https://tokio.rs/tokio/tutorial
- **Python asyncio**: https://docs.python.org/3/library/asyncio.html

## 🔗 Related Patterns

- **Pattern 1: Prompt Chaining** - Parallel can be one step in chain
- **Pattern 2: Routing** - Router decides what runs parallel
- **Pattern 5: Tool Use** - Tools declare parallel capability

---

**Next**: [Pattern 8: Memory Management →](../08-memory-management/README.mdREADME.md)

