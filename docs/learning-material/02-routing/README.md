# Pattern 2: Routing

> **"Dynamically directing workflow based on intent, context, or conditions"**

## 📖 Pattern Overview

Routing introduces conditional logic into an agent's workflow, enabling dynamic decision-making about which action, tool, or sub-process to execute based on input classification, state analysis, or other criteria.

## 🎯 Key Concepts

1. **Intent Classification**: Determine what the user wants to do
2. **Dynamic Dispatch**: Route to appropriate handler
3. **Conditional Logic**: Decision trees based on multiple factors
4. **Handler Registry**: Map intentions to implementations

## 🔍 How Codex Implements This

### Location in Codebase
- **Primary**: `codex-rs/core/src/tools/router.rs` (lines 59-102)
- **Support**: `codex-rs/core/src/tools/registry.rs`
- **MCP Routing**: `codex-rs/mcp-server/src/message_processor.rs`

### Implementation Details

Codex implements a **sophisticated tool router** that classifies and dispatches different types of tool calls:

```rust
// From codex-rs/core/src/tools/router.rs
match item {
    ResponseItem::FunctionCall { name, arguments, call_id, .. } => {
        // Check if this is an MCP tool (format: "server__tool")
        if let Some((server, tool)) = session.parse_mcp_tool_name(&name) {
            Ok(Some(ToolCall {
                tool_name: name,
                call_id,
                payload: ToolPayload::Mcp {
                    server,
                    tool,
                    raw_arguments: arguments,
                },
            }))
        } else {
            // Route to unified_exec or standard function
            let payload = if name == "unified_exec" {
                ToolPayload::UnifiedExec { arguments }
            } else {
                ToolPayload::Function { arguments }
            };
            Ok(Some(ToolCall {
                tool_name: name,
                call_id,
                payload,
            }))
        }
    }
    ResponseItem::CustomToolCall { .. } => // Route to custom handler
    ResponseItem::LocalShellCall { .. } => // Route to shell executor
    // ... more cases
}
```

### Routing Strategies in Codex

1. **Name-Based Routing**: Tool name determines handler
2. **Type-Based Routing**: Payload type determines execution path
3. **Pattern Matching**: Complex conditions via Rust enums
4. **Registry Lookup**: Dynamic handler registration

## 💡 Real-World Example from Codex

When the LLM wants to execute a command, the router:

1. **Receives** tool call from model
2. **Classifies** the tool type (function, MCP, shell, custom)
3. **Routes** to appropriate handler:
   - `unified_exec` → Sandbox executor
   - `server__tool` → MCP client
   - Standard function → Function handler
4. **Executes** via the specialized handler
5. **Returns** results back to model

## 📊 Architecture Diagram

```
                    ┌─────────────────┐
                    │   LLM Output    │
                    │  (Tool Calls)   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Tool Router   │
                    │  (Classifier)   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   Function  │ │ Unified Exec│ │  MCP Tool   │
    │   Handler   │ │   Handler   │ │   Handler   │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
           └───────────────┴───────────────┘
                           │
                           ▼
                    ┌─────────────────┐
                    │   Execute &     │
                    │  Return Result  │
                    └─────────────────┘
```

## 🐍 Python Examples

See the example files:
- **`pattern_simple.py`**: Basic intent classification and routing
- **`pattern_advanced.py`**: Tool registry with dynamic dispatch
- **`codex_inspired.py`**: Multi-tier routing system like Codex

## 🔑 Key Takeaways

1. ✅ **Flexibility**: Handle diverse requests without monolithic logic
2. ✅ **Extensibility**: Add new routes without modifying core logic
3. ✅ **Clarity**: Explicit routing makes behavior predictable
4. ✅ **Performance**: Direct dispatch instead of sequential checks
5. ✅ **Maintainability**: Each handler focuses on one responsibility

## 🚀 When to Use

- ✅ Multiple possible actions based on user intent
- ✅ Different tools/agents for different task types
- ✅ Complex conditional logic governing execution paths
- ✅ Need to add new capabilities without code changes
- ❌ Single, deterministic workflow (no branching needed)

## 📚 Further Reading

- **Codex Source**: `codex-rs/core/src/tools/router.rs`
- **Tool Registry**: `codex-rs/core/src/tools/registry.rs`
- **Textbook**: Chapter 2 - Routing
- **LangGraph Routing**: https://langchain-ai.github.io/langgraph/

## 🔗 Related Patterns

- **Pattern 1: Prompt Chaining** - Routing decides which chain
- **Pattern 5: Tool Use** - Routes to appropriate tools
- **Pattern 7: Multi-Agent** - Routes between agents

---

**Next**: [Pattern 3: Parallelization →](../03-parallelization/README.md)

