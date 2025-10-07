# Pattern 5: Tool Use

> **"Extending agent capabilities through external system integration"**

## 📖 Pattern Overview

Tool Use enables agents to interact with external systems, APIs, databases, and services. Instead of relying solely on pretrained knowledge, agents can retrieve real-time data, execute commands, and manipulate external resources.

## 🎯 Key Concepts

1. **Tool Definition**: Specify what the tool does and its parameters
2. **Tool Invocation**: LLM decides when and how to use tools
3. **Sandboxing**: Execute tools safely with appropriate restrictions
4. **Result Integration**: Feed tool output back to the LLM

## 🔍 How Codex Implements This

### Location in Codebase
- **Primary**: `codex-rs/core/src/exec.rs`
- **Tool Registry**: `codex-rs/core/src/tools/registry.rs`
- **MCP Tools**: `codex-rs/core/src/mcp_tool_call.rs`
- **Safety**: `codex-rs/core/src/safety.rs`

### Implementation Details

Codex has a **comprehensive tool system** with multiple execution modes:

```rust
// From codex-rs/core/src/exec.rs
pub async fn process_exec_tool_call(
    params: ExecParams,
    sandbox_type: SandboxType,
    sandbox_policy: &SandboxPolicy,
    sandbox_cwd: &Path,
    codex_linux_sandbox_exe: &Option<PathBuf>,
    stdout_stream: Option<StdoutStream>,
) -> Result<ExecToolCallOutput> {
    match sandbox_type {
        SandboxType::None => {
            // Direct execution (dangerous!)
            exec(params, sandbox_policy, stdout_stream).await
        }
        SandboxType::MacosSeatbelt => {
            // Execute under Apple Seatbelt sandbox
            let child = spawn_command_under_seatbelt(...).await?;
            consume_truncated_output(child, timeout, stdout_stream).await
        }
        SandboxType::LinuxSeccomp => {
            // Execute under Landlock + seccomp
            let child = spawn_command_under_landlock(...).await?;
            consume_truncated_output(child, timeout, stdout_stream).await
        }
    }
}
```

### Available Tools in Codex

1. **File Operations**
   - Read files
   - Write/patch files
   - List directories

2. **Shell Commands**
   - Execute in sandbox
   - Network-disabled by default
   - Output truncation for token limits

3. **Git Operations**
   - Status, diff, commit
   - Branch management

4. **MCP Tools**
   - Dynamic tool discovery
   - External server integration

5. **Web Search** (when enabled)
   - Real-time information retrieval

## 💡 Safety Mechanisms

Codex implements **multi-layer security** for tool execution:

### 1. Sandboxing
- **macOS**: Apple Seatbelt (`sandbox-exec`)
- **Linux**: Landlock + seccomp
- **Network**: Disabled by default
- **File Access**: Limited to workspace

### 2. Approval Workflow
```rust
// From codex-rs/core/src/safety.rs
pub fn assess_command_safety(
    command: &[String],
    approval_policy: AskForApproval,
    sandbox_policy: &SandboxPolicy,
    approved: &HashSet<Vec<String>>,
) -> SafetyCheck {
    if command_might_be_dangerous(command) {
        return SafetyCheck::AskUser;  // Request approval
    }
    
    if is_known_safe_command(command) {
        return SafetyCheck::AutoApprove { ... };
    }
    
    // Apply policy
    assess_safety_for_untrusted_command(...)
}
```

### 3. Command Whitelisting
- Known-safe commands: `ls`, `cat`, `grep`, etc.
- Dangerous commands: `rm -rf`, `dd`, `curl` (network)
- User approval required for dangerous operations

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────┐
│          LLM Decision Engine                │
│  "I need to read file X to answer this"    │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   Tool Router        │
        │  (Pattern #2)        │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Safety Assessment   │
        │  • Is it safe?       │
        │  • Needs approval?   │
        │  • Sandbox required? │
        └──────────┬───────────┘
                   │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
    ┌──────────┐      ┌──────────┐
    │ Approve  │      │  Reject  │
    └─────┬────┘      └──────────┘
          │
          ▼
    ┌──────────────────────┐
    │  Execute in Sandbox  │
    │  • Network: OFF      │
    │  • File access: CWD  │
    │  • Timeout: 30s      │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Collect Output      │
    │  • stdout/stderr     │
    │  • exit code         │
    │  • Truncate if long  │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Return to LLM       │
    │  "File contains..."  │
    └──────────────────────┘
```

## 🐍 Python Examples

See the example files:
- **`pattern_simple.py`**: Basic tool use with function calling
- **`pattern_advanced.py`**: Tool registry with sandboxing
- **`tool_safety.py`**: Safety checks and validation

## 🔑 Key Takeaways

1. ✅ **Real-time Data**: Access current information beyond training data
2. ✅ **Action Capability**: Agents can modify external state
3. ✅ **Extensibility**: Add new tools without retraining
4. ✅ **Safety Critical**: Must sandbox and validate all executions
5. ✅ **User Control**: Approval workflows for dangerous operations

## 🚀 When to Use

- ✅ Need real-time or dynamic data
- ✅ Agent must interact with external systems
- ✅ Task requires actions beyond text generation
- ✅ Integration with existing APIs/services
- ❌ All information available in training data
- ❌ Read-only Q&A tasks

## ⚠️ Safety Considerations

### Do's
- ✅ Always sandbox tool execution
- ✅ Validate all tool inputs
- ✅ Implement approval workflows for dangerous operations
- ✅ Truncate/limit tool output
- ✅ Set execution timeouts
- ✅ Log all tool invocations

### Don'ts
- ❌ Never trust tool input blindly
- ❌ Don't give unrestricted file system access
- ❌ Avoid network access unless explicitly needed
- ❌ Don't execute without output limits
- ❌ Never skip safety checks for convenience

## 📚 Further Reading

- **Codex Exec**: `codex-rs/core/src/exec.rs`
- **Tool Registry**: `codex-rs/core/src/tools/registry.rs`
- **Safety Module**: `codex-rs/core/src/safety.rs`
- **Textbook**: Chapter 5 - Tool Use
- **OpenAI Function Calling**: https://platform.openai.com/docs/guides/function-calling

## 🔗 Related Patterns

- **Pattern 2: Routing** - Routes to appropriate tools
- **Pattern 10: MCP** - Protocol for tool integration
- **Pattern 13: Human-in-the-Loop** - Approvals for tools
- **Pattern 18: Guardrails** - Safety for tool execution

---

**Next**: [Pattern 8: Memory Management →](../08-memory-management/)

