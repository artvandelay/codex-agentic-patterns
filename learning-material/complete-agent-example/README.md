# Complete Agent Example

> **"Putting it all together: A production-inspired agentic system"**

## 📖 Overview

This example demonstrates how to combine multiple agentic patterns into a cohesive, production-ready system inspired by Codex's architecture.

## 🎯 Patterns Integrated

This complete example integrates:

1. **✅ Prompt Chaining** - Multi-turn conversation
2. **✅ Routing** - Dynamic tool dispatch
3. **✅ Parallelization** - Concurrent tool execution
4. **✅ Tool Use** - External system integration
5. **✅ Memory Management** - Conversation persistence
6. **✅ Exception Handling** - Retry logic and recovery
7. **✅ Human-in-the-Loop** - Approval workflows
8. **✅ Guardrails** - Safety checks and sandboxing

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Codex-Inspired Agent                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            Conversation Manager                        │  │
│  │  • Turn-based execution loop                          │  │
│  │  • History management                                 │  │
│  │  • State persistence                                  │  │
│  └──────────────────┬────────────────────────────────────┘  │
│                     │                                         │
│  ┌─────────────────┴──────────────────────────────────────┐ │
│  │            Tool Router & Safety Layer                   │ │
│  │  • Intent classification                               │ │
│  │  • Safety assessment                                   │ │
│  │  • Approval requests                                   │ │
│  └──────────────────┬────────────────────────────────────┘  │
│                     │                                         │
│         ┌───────────┼───────────┐                            │
│         │           │           │                            │
│  ┌──────▼────┐ ┌───▼────┐ ┌───▼────────┐                   │
│  │  File Ops │ │  Shell │ │ Calculator │  ...               │
│  │   Tools   │ │  Tools │ │   Tools    │                    │
│  └───────────┘ └────────┘ └────────────┘                    │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            Error Handler & Retry Logic                 │  │
│  │  • Exponential backoff                                │  │
│  │  • Circuit breaker                                    │  │
│  │  • Graceful degradation                               │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 📂 Files

- **`agent_core.py`**: Core agent implementation
- **`tool_system.py`**: Tool registry and execution
- **`safety_layer.py`**: Safety checks and approvals
- **`conversation_manager.py`**: State and history management
- **`error_handling.py`**: Retry logic and recovery
- **`example_usage.py`**: Demo scenarios

## 🚀 Quick Start

```bash
# Install dependencies
pip install openai aiohttp

# Set API key
export OPENAI_API_KEY="your-key-here"

# Run the complete example
python example_usage.py
```

## 💡 Key Features

### 1. Multi-Turn Conversations
Like Codex, maintains context across turns:
```python
agent = CodexInspiredAgent()
agent.run("Analyze the codebase")
# Turn 1: Reads files
# Turn 2: Analyzes code
# Turn 3: Generates report
```

### 2. Safe Tool Execution
Multiple layers of safety:
```python
# Whitelist checking
# Sandboxing simulation
# User approval for dangerous ops
# Output truncation
# Timeout enforcement
```

### 3. Intelligent Routing
Automatically routes to appropriate tools:
```python
# "What time is it?" → time tool
# "Calculate 2+2" → calculator tool
# "Read main.py" → file tool
```

### 4. Error Recovery
Handles failures gracefully:
```python
# Automatic retry with backoff
# Fallback to alternative approaches
# User notification of issues
```

### 5. Conversation Persistence
Saves and resumes sessions:
```python
agent.save_session("session_123.json")
# Later...
agent.load_session("session_123.json")
```

## 📊 Example Scenarios

### Scenario 1: Code Analysis Task
```python
query = "Analyze main.py, find bugs, and suggest fixes"

# Turn 1: Read file
# Turn 2: Analyze for bugs (uses analysis tool)
# Turn 3: Generate fixes (uses code generation)
# Turn 4: Present recommendations
```

### Scenario 2: Data Processing
```python
query = "Process sales.csv and create a summary report"

# Turn 1: Read CSV (file tool)
# Turn 2: Calculate statistics (calculator tool)
# Turn 3: Generate visualizations (visualization tool)
# Turn 4: Write report (file tool)
```

### Scenario 3: System Administration
```python
query = "Check disk usage and clean up old logs"

# Turn 1: Check disk (shell tool)
# Approval requested: "Execute 'du -sh'?"
# Turn 2: Identify old files (shell tool)
# Approval requested: "Delete 500MB of logs?"
# Turn 3: Clean up (shell tool)
# Turn 4: Verify space freed
```

## 🔐 Safety Features

### Command Whitelisting
```python
SAFE_COMMANDS = ["ls", "cat", "grep", "find"]
DANGEROUS_COMMANDS = ["rm", "dd", "mkfs", "shutdown"]
```

### Approval Workflow
```python
if is_dangerous_operation(tool_call):
    approval = request_user_approval(tool_call)
    if not approval:
        return "Operation denied by user"
```

### Sandboxing
```python
# Network disabled
# File access limited to workspace
# Process timeout: 30s
# Output truncated: 10KB max
```

## 📈 Performance Considerations

### Parallel Tool Execution
```python
# Some tools run in parallel
results = await asyncio.gather(
    execute_tool("read_file", {"path": "a.py"}),
    execute_tool("read_file", {"path": "b.py"}),
    execute_tool("read_file", {"path": "c.py"}),
)
```

### Context Window Management
```python
# Automatically compress old history
if len(history) > MAX_TURNS:
    history = compress_history(history)
```

### Caching
```python
# Cache file reads
# Cache tool results
# Cache LLM responses (deterministic queries)
```

## 🧪 Testing

```bash
# Run unit tests
python -m pytest test_agent.py

# Run integration tests
python -m pytest test_integration.py

# Run safety tests
python -m pytest test_safety.py
```

## 📚 Learning Objectives

After studying this example, you should understand:

1. ✅ How to architect a multi-pattern agent system
2. ✅ State management across async operations
3. ✅ Safety-first design principles
4. ✅ Error handling and recovery strategies
5. ✅ Tool orchestration and routing
6. ✅ User interaction patterns
7. ✅ Performance optimization techniques

## 🔗 Codex Comparison

| Feature | This Example | Codex |
|---------|-------------|-------|
| Language | Python | Rust |
| Sandboxing | Simulated | Real (Seatbelt/Landlock) |
| MCP Support | No | Yes |
| TUI | No | Yes (Ratatui) |
| State Persistence | JSON | Binary rollout files |
| Error Handling | Basic retry | Advanced with backoff |
| Tool Parallelization | Yes | Yes |
| Approval System | Yes | Yes |

## 🚀 Extension Ideas

1. **Add MCP Support**: Integrate with external MCP servers
2. **Implement Streaming**: Stream tool output in real-time
3. **Add Telemetry**: OpenTelemetry integration
4. **Build TUI**: Terminal UI like Codex
5. **Enhance Sandboxing**: Use Docker or similar
6. **Add Planning**: Explicit planning tool like Codex
7. **Multi-Agent**: Coordination between multiple agents

## 📄 License

Educational example for learning purposes.

---

**Start with**: [`example_usage.py`](./example_usage.py) to see it in action!

