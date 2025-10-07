# Pattern 1: Prompt Chaining

> **"Breaking complex tasks into sequential, manageable steps"**

## 📖 Pattern Overview

Prompt chaining is a foundational pattern where complex tasks are decomposed into a sequence of smaller sub-tasks. The output of each step becomes the input to the next, creating a logical workflow.

## 🎯 Key Concepts

1. **Sequential Processing**: Tasks executed one after another
2. **State Transfer**: Output of step N becomes input to step N+1
3. **Modularity**: Each step has a focused responsibility
4. **Composability**: Steps can be reordered or replaced

## 🔍 How Codex Implements This

### Location in Codebase
- **Primary**: `codex-rs/core/src/codex.rs` (lines 1620-1703)
- **Support**: `codex-rs/core/src/conversation_history.rs`

### Implementation Details

Codex implements a sophisticated **turn-based conversation loop**:

```rust
loop {
    // 1. Get pending input from UI
    let pending_input = sess.get_pending_input().await;
    
    // 2. Construct turn input with full history
    let turn_input: Vec<ResponseItem> = if is_review_mode {
        review_thread_history.clone()
    } else {
        sess.turn_input_with_history(pending_input).await
    };
    
    // 3. Run turn and get results
    match run_turn(Arc::clone(&sess), ...) {
        Ok(TurnOutput::Continue(items)) => {
            // Record results as history
            sess.record_conversation_items(&items).await;
            
            // Items become input for next turn
            review_thread_history.extend(items);
        }
        Ok(TurnOutput::Complete(_)) => break,
        Err(e) => handle_error(e),
    }
}
```

### Key Features

1. **History Management**: Each turn maintains context from previous turns
2. **State Accumulation**: Conversation state grows with each turn
3. **Forking Support**: Can resume from earlier points in the chain
4. **Review Mode**: Isolated chains for specific workflows

## 💡 Why This Matters

### Without Prompt Chaining
```
User: "Analyze this codebase, find bugs, and fix them"
❌ Single massive prompt → cognitive overload → unreliable results
```

### With Prompt Chaining
```
Step 1: "Read and understand the codebase structure"
Step 2: "Analyze code for potential bugs" (uses output from step 1)
Step 3: "Generate fixes for identified bugs" (uses output from step 2)
Step 4: "Apply patches and verify" (uses output from step 3)
✅ Focused steps → reliable execution → better results
```

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                   User Input                         │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Turn 1: Process initial request                    │
│  • Read context                                      │
│  • Generate plan                                     │
│  Output: [Plan with 3 steps]                        │
└────────────────────┬────────────────────────────────┘
                     │ (Output becomes input)
                     ▼
┌─────────────────────────────────────────────────────┐
│  Turn 2: Execute step 1 of plan                     │
│  Input: [Previous plan + history]                   │
│  • Execute tools                                     │
│  • Collect results                                   │
│  Output: [Step 1 results]                           │
└────────────────────┬────────────────────────────────┘
                     │ (Output becomes input)
                     ▼
┌─────────────────────────────────────────────────────┐
│  Turn 3: Execute step 2 of plan                     │
│  Input: [All previous context]                      │
│  • Use results from step 1                          │
│  • Execute next tools                               │
│  Output: [Step 2 results]                           │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
                    ...
```

## 🐍 Python Examples

See the example files:
- **`pattern_simple.py`**: Basic sequential chain
- **`pattern_advanced.py`**: Production-ready with error handling
- **`codex_inspired.py`**: Mimics Codex's turn-based architecture

## 🔑 Key Takeaways

1. ✅ **Reliability**: Smaller steps = fewer errors
2. ✅ **Debuggability**: Easy to identify which step failed
3. ✅ **Flexibility**: Can modify individual steps without rewriting everything
4. ✅ **Context Building**: Each step enriches understanding
5. ✅ **Tool Integration**: Natural place to insert external tool calls

## 🚀 When to Use

- ✅ Multi-step workflows (research → analyze → summarize → report)
- ✅ Complex reasoning tasks requiring intermediate steps
- ✅ Tasks involving external tool calls between reasoning steps
- ✅ Scenarios where partial results are useful
- ❌ Simple, single-step queries (overhead not justified)

## 📚 Further Reading

- **Codex Source**: `codex-rs/core/src/codex.rs:1620-1703`
- **Conversation History**: `codex-rs/core/src/conversation_history.rs`
- **Textbook**: Chapter 1 - Prompt Chaining
- **LangChain LCEL**: https://python.langchain.com/docs/expression_language/

## 🔗 Related Patterns

- **Pattern 2: Routing** - Decides which chain to execute
- **Pattern 8: Memory Management** - Stores chain state
- **Pattern 12: Exception Handling** - Handles chain failures

---

**Next**: [Pattern 2: Routing →](../02-routing/)

