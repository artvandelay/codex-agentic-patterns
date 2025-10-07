# Pattern 22: Sandbox Escalation with Automatic Retry

> **"Multi-stage command execution with intelligent fallback strategies"**

## 📖 Pattern Overview

Sandbox Escalation is a sophisticated execution pattern that goes far beyond simple "run command and handle errors." It implements a complete decision tree for safe command execution with automatic retry mechanisms.

## 🎯 Key Concepts

1. **Safety Assessment** - Classify commands before execution
2. **Sandbox Selection** - Choose appropriate isolation level
3. **Automatic Escalation** - Retry without sandbox on failure
4. **Approval Workflows** - Smart user consent management
5. **Session Caching** - Remember user decisions
6. **Telemetry Tracking** - Log all decisions and outcomes

## 🔍 How Codex Implements This

### Location in Codebase
- **Primary**: `codex-rs/core/src/executor/runner.rs` (lines 76-218)
- **Support**: `codex-rs/core/src/executor/sandbox.rs` (lines 87-160)

### Implementation Flow

```rust
// From codex-rs/core/src/executor/runner.rs:77-157
pub(crate) async fn run(&self, request: ExecutionRequest) -> Result<ExecToolCallOutput> {
    // Step 1: Assess command safety
    let sandbox_decision = select_sandbox(
        &request,
        approval_policy,
        self.approval_cache.snapshot(),
        &config,
    ).await?;
    
    // Step 2: Execute in chosen sandbox
    let first_attempt = self.spawn(
        request.params.clone(),
        sandbox_decision.initial_sandbox,
        &config,
    ).await;
    
    // Step 3: Handle sandbox failures with escalation
    match first_attempt {
        Ok(output) => Ok(output),
        Err(CodexErr::Sandbox(error)) => {
            if sandbox_decision.escalate_on_failure {
                self.retry_without_sandbox(&request, error).await
            } else {
                Err(ExecError::rejection(message))
            }
        }
    }
}
```

### Key Features

1. **Three-Tier Safety Classification**:
   - Auto-approve (safe commands)
   - Ask user (potentially dangerous)
   - Reject (definitely dangerous)

2. **Sandbox Types**:
   - None (no isolation)
   - Restricted shell (limited environment)
   - Full container (Docker/etc.)

3. **Escalation Logic**:
   - Run in sandbox first
   - If sandbox denies → ask user
   - If approved → retry without sandbox
   - Cache approval for session

4. **Approval Scoping**:
   - Once (this command only)
   - Session (remember for this session)
   - Never (always deny)

## 💡 Real-World Example from Codex

```
User: "Install numpy with pip"

1. Safety Assessment: "pip install" → potentially dangerous (network access)
2. Sandbox Decision: Run in restricted sandbox first
3. Execute: sandbox blocks network access → fails
4. Escalation: Ask user "Command failed; retry without sandbox?"
5. User Choice: "Approve for session"
6. Retry: Run without sandbox → succeeds
7. Cache: Remember approval for future pip commands
8. Telemetry: Log decision chain for debugging
```

## 📊 Architecture Diagram

```
Command Request
    ↓
┌─────────────────┐
│ Safety Assessment│
│ - Check dangerous│
│ - Check approved │
│ - Apply policy   │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌────────┐  ┌─────────┐
│Auto    │  │Ask User │
│Approve │  │         │
└───┬────┘  └────┬────┘
    │            │
    │       ┌────┴────┐
    │       │         │
    │       ▼         ▼
    │   ┌─────────┐ ┌────────┐
    │   │Approved │ │Denied  │
    │   └────┬────┘ └────────┘
    │        │
    └────────┼────────────────┐
             │                │
             ▼                ▼
        ┌──────────────┐ ┌─────────────┐
        │Execute in    │ │Execute      │
        │Sandbox       │ │Unsandboxed  │
        └──────┬───────┘ └─────────────┘
               │
          ┌────┴────┐
          │         │
          ▼         ▼
     ┌─────────┐ ┌──────────────┐
     │Success  │ │Sandbox Error │
     └─────────┘ └──────┬───────┘
                        │
                   ┌────┴────┐
                   │Ask User │
                   │Escalate?│
                   └────┬────┘
                        │
                   ┌────┴────┐
                   │         │
                   ▼         ▼
              ┌─────────┐ ┌────────┐
              │Retry    │ │Fail    │
              │No       │ │        │
              │Sandbox  │ │        │
              └─────────┘ └────────┘
```

## 🐍 Python Implementation

See the example file:
- **`pattern_advanced.py`**: Complete 400-line implementation with all features

Key classes:
- `CommandExecutor`: Main orchestrator
- `SandboxDecision`: Execution strategy
- `SafetyCheck`: Risk assessment
- `ApprovalCache`: Session-scoped consent

## 🔑 Key Takeaways

1. ✅ **Multi-Stage Execution**: Don't just try once and fail
2. ✅ **Safety First**: Assess risk before execution
3. ✅ **Smart Escalation**: Automatic retry with user approval
4. ✅ **Session Memory**: Cache user decisions
5. ✅ **Comprehensive Logging**: Track all decision points
6. ⚠️ **Complex State**: Much more than simple try/catch

## 🚀 When to Use

- ✅ Production agent systems
- ✅ Commands that might need special permissions
- ✅ Systems with security requirements
- ✅ Multi-user environments
- ❌ Simple scripts or demos
- ❌ Fully trusted environments

## ⚠️ Common Pitfalls

### 1. Over-Engineering Simple Cases
```python
❌ BAD: Use for "echo hello"
✅ GOOD: Use for "curl external-api.com"
```

### 2. Ignoring User Experience
```python
❌ BAD: Ask for approval on every command
✅ GOOD: Smart caching with session scope
```

### 3. Poor Error Messages
```python
❌ BAD: "Command failed"
✅ GOOD: "Network access blocked by sandbox; retry without isolation?"
```

## 📚 Further Reading

- **Codex Source**: `codex-rs/core/src/executor/runner.rs`
- **Sandbox Implementation**: `codex-rs/core/src/executor/sandbox.rs`
- **Safety Assessment**: `codex-rs/core/src/safety.rs`
- **Seatbelt (macOS)**: Apple's sandboxing system
- **Seccomp (Linux)**: Linux's system call filtering

## 🔗 Related Patterns

- **Pattern 5: Tool Use** - Basic function calling
- **Pattern 12: Exception Handling** - Error recovery strategies
- **Pattern 13: Human-in-the-Loop** - Approval workflows
- **Pattern 18: Guardrails/Safety** - Security constraints

---

**Next**: [Pattern 17: Turn Diff Tracking →](../17-turn-diff-tracking/README.mdREADME.md)
