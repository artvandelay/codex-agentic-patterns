# Agentic Design Patterns - Learning Materials

> **Educational materials based on the Codex CLI implementation**

This learning material demonstrates how real-world agentic design patterns are implemented in the Codex codebase, with simplified Python examples for educational purposes.

## 📚 Overview

These materials map the 21 agentic design patterns from the textbook to actual implementations in Codex, providing both theoretical understanding and practical code examples.

## 🎯 What You'll Learn

- How production agentic systems are architected
- Key patterns for building reliable AI agents
- Safety mechanisms and error handling strategies
- Tool integration and orchestration patterns
- Multi-turn conversation management

## 📂 Structure

```
learning-material/
├── README.md (this file)
├── 01-prompt-chaining/
├── 02-routing/
├── 03-parallelization/
├── 05-tool-use/
├── 08-memory-management/
├── 10-mcp-integration/
├── 12-exception-handling/
├── 13-human-in-the-loop/
├── 18-guardrails-safety/
└── complete-agent-example/
```

## 🚀 Getting Started

### Prerequisites

```bash
pip install openai asyncio aiohttp
```

### Environment Setup

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 📖 Pattern Coverage

| Pattern | Codex Quality | Python Example | Use Case |
|---------|---------------|----------------|----------|
| **1. Prompt Chaining** | ⭐⭐⭐⭐⭐ | ✅ | Multi-turn conversations |
| **2. Routing** | ⭐⭐⭐⭐⭐ | ✅ | Tool dispatch and classification |
| **3. Parallelization** | ⭐⭐⭐⭐⭐ | ✅ | Concurrent tool execution |
| **5. Tool Use** | ⭐⭐⭐⭐⭐ | ✅ | External system integration |
| **8. Memory Management** | ⭐⭐⭐⭐⭐ | ✅ | Conversation persistence |
| **10. MCP Integration** | ⭐⭐⭐⭐⭐ | ✅ | Protocol-based tool connection |
| **12. Exception Handling** | ⭐⭐⭐⭐⭐ | ✅ | Retry logic and recovery |
| **13. Human-in-the-Loop** | ⭐⭐⭐⭐⭐ | ✅ | Approval workflows |
| **18. Guardrails/Safety** | ⭐⭐⭐⭐⭐ | ✅ | Sandboxing and validation |

## 🎓 Learning Path

### Beginner Track
1. Start with **Pattern 1: Prompt Chaining** - understand basic conversation flow
2. Move to **Pattern 5: Tool Use** - learn how agents interact with external systems
3. Study **Pattern 8: Memory Management** - see how state is maintained

### Intermediate Track
4. Explore **Pattern 2: Routing** - understand intelligent decision-making
5. Learn **Pattern 12: Exception Handling** - build resilient systems
6. Study **Pattern 13: Human-in-the-Loop** - implement safety controls

### Advanced Track
7. Master **Pattern 3: Parallelization** - optimize performance
8. Understand **Pattern 18: Guardrails/Safety** - production-ready security
9. Integrate **Pattern 10: MCP** - build extensible agent systems

## 📝 Code Examples

Each pattern folder contains:

- **`README.md`**: Pattern explanation and Codex implementation analysis
- **`pattern_simple.py`**: Basic implementation of the pattern
- **`pattern_advanced.py`**: Production-like implementation with error handling
- **`codex_example.md`**: How Codex implements this pattern (with code references)

## 🔗 References

- **Codex Repository**: Real-world implementation at `codex-rs/`
- **Agentic Design Patterns Textbook**: Complete theoretical foundation
- **Model Context Protocol**: https://modelcontextprotocol.io/

## 💡 Key Insights from Codex

### 1. **Safety First**
Codex implements multiple layers of security:
- Sandboxing (Seatbelt on macOS, Landlock on Linux)
- Command validation and approval
- Network isolation by default

### 2. **User Control**
Three approval modes balance autonomy and safety:
- **Suggest**: All actions require approval
- **Auto Edit**: File changes approved, commands need approval
- **Full Auto**: Runs autonomously in sandbox

### 3. **Resilience**
Production-grade error handling:
- Automatic retries with exponential backoff
- Graceful degradation
- User notification of issues

### 4. **Modularity**
Clean separation of concerns:
- Core logic (business rules)
- TUI (user interface)
- Exec (non-interactive execution)
- MCP integration (extensibility)

## 🛠️ Running Examples

Each pattern folder has runnable examples:

```bash
# Navigate to a pattern
cd learning-material/01-prompt-chaining/

# Run basic example
python pattern_simple.py

# Run advanced example
python pattern_advanced.py
```

## 📚 Further Reading

- **Codex Documentation**: `/docs/` folder in repository
- **Core Implementation**: `codex-rs/core/src/` for Rust source
- **Protocol Design**: `codex-rs/docs/protocol_v1.md`
- **MCP Interface**: `codex-rs/docs/codex_mcp_interface.md`

## 🤝 Contributing

These materials are educational references. To contribute to Codex itself, see the main repository's CONTRIBUTING.md.

## 📄 License

Educational materials for learning purposes. See main Codex repository for license details.

---

**Ready to learn?** Start with [Pattern 1: Prompt Chaining](./01-prompt-chaining/)! 🚀

