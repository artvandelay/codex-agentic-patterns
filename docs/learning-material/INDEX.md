# Learning Materials - Complete Index

> **Your guide to understanding agentic design patterns through the Codex implementation**

## 📚 Quick Navigation

| Resource | Description | Level |
|----------|-------------|-------|
| **[README](./README.md)** | Overview and getting started | Beginner |
| **[Pattern Summary](./CODEX_PATTERNS_SUMMARY.md)** | Comprehensive pattern analysis | All Levels |
| **[Complete Agent](./complete-agent-example/README.md)** | Production-ready implementation | Advanced |

---

## 🎯 Learning Paths

### Beginner → Intermediate Learning Path

**Fundamentals**
```
[Pattern 1: Prompt Chaining](./01-prompt-chaining/README.md)
         → Run pattern_simple.py
         → Read Codex examples in README
         → Experiment with pattern_advanced.py

[Pattern 5: Tool Use](./05-tool-use/README.md)
         → Understand function calling
         → Explore safety mechanisms
         → Build your own tool

[Pattern 8: Memory Management](./08-memory-management/README.md)
         → Study conversation history
         → Implement state persistence
         → Practice session management
```

**Intermediate Patterns**
```
[Pattern 2: Routing](./02-routing/README.md)
         → Classification and dispatch
         → Build a tool router
         → Dynamic handler registration

[Pattern 12: Exception Handling](./12-exception-handling/README.md)
         → Retry logic with backoff
         → Error recovery strategies
         → Graceful degradation

[Pattern 13: Human-in-the-Loop](./13-human-in-the-loop/README.md)
         → Approval workflows
         → Policy systems
         → User control patterns
```

**Integration**
```
[Complete Agent Example](./complete-agent-example/README.md)
         → Study complete_agent.py
         → Run example scenarios
         → Modify and extend
         → Build your own variant
```

### Path 2: Deep Dive 

**For Experienced Developers**
```
Codex Source Code Tour
       → codex-rs/core/src/codex.rs
       → Understand turn-based architecture
       → Trace a complete workflow

Safety & Sandboxing
       → codex-rs/core/src/safety.rs
       → codex-rs/core/src/exec.rs
       → Study platform-specific isolation

Tool System Architecture
       → codex-rs/core/src/tools/
       → Router, registry, handlers
       → Parallel execution

MCP Integration
       → codex-rs/mcp-client/
       → codex-rs/mcp-server/
       → Protocol implementation

Build Your Own
         → Design architecture
         → Implement core patterns
         → Add your own features
```

---

## 📖 Pattern-by-Pattern Guide

### Core Patterns (Essential)

#### 1. Prompt Chaining ⭐⭐⭐⭐⭐
- **Folder**: `01-prompt-chaining/`
- **Difficulty**: ⭐ Beginner
- **Time**: 2-3 hours
- **Files**:
  - `README.md` - Pattern explanation
  - `pattern_simple.py` - Basic chain
  - `pattern_advanced.py` - Production-ready

**What You'll Learn:**
- Sequential task decomposition
- State transfer between steps
- History management
- Turn-based execution

**Codex Reference**: `codex-rs/core/src/codex.rs:1620-1703`

---

#### 2. Routing ⭐⭐⭐⭐⭐
- **Folder**: `02-routing/`
- **Difficulty**: ⭐⭐ Intermediate
- **Time**: 3-4 hours
- **Files**:
  - `README.md` - Pattern explanation
  - `pattern_simple.py` - Basic routing
  - `pattern_advanced.py` - Registry system

**What You'll Learn:**
- Intent classification
- Dynamic dispatch
- Handler registry
- Conditional workflows

**Codex Reference**: `codex-rs/core/src/tools/router.rs:59-102`

---

#### 5. Tool Use ⭐⭐⭐⭐⭐
- **Folder**: `05-tool-use/`
- **Difficulty**: ⭐⭐ Intermediate
- **Time**: 4-5 hours
- **Files**:
  - `README.md` - Pattern explanation
  - `pattern_simple.py` - Basic tools
  - `pattern_advanced.py` - Sandboxing
  - `tool_safety.py` - Safety checks

**What You'll Learn:**
- Function calling API
- Tool specification
- Safety validation
- Sandboxed execution

**Codex Reference**: `codex-rs/core/src/exec.rs:82-115`

---

#### 8. Memory Management ⭐⭐⭐⭐⭐
- **Folder**: `08-memory-management/`
- **Difficulty**: ⭐⭐ Intermediate
- **Time**: 3-4 hours

**What You'll Learn:**
- Conversation state
- History persistence
- Context window management
- Session resumption

**Codex Reference**: `codex-rs/core/src/conversation_history.rs`

---

#### 12. Exception Handling ⭐⭐⭐⭐⭐
- **Folder**: `12-exception-handling/`
- **Difficulty**: ⭐⭐⭐ Advanced
- **Time**: 3-4 hours

**What You'll Learn:**
- Retry logic
- Exponential backoff
- Circuit breakers
- Error recovery

**Codex Reference**: `codex-rs/core/src/codex.rs:1979-2012`

---

#### 13. Human-in-the-Loop ⭐⭐⭐⭐⭐
- **Folder**: `13-human-in-the-loop/`
- **Difficulty**: ⭐⭐⭐ Advanced
- **Time**: 4-5 hours

**What You'll Learn:**
- Approval workflows
- Policy systems
- Dangerous operation detection
- Session-level approvals

**Codex Reference**: `codex-rs/core/src/safety.rs:92-136`

---

#### 18. Guardrails/Safety ⭐⭐⭐⭐⭐
- **Folder**: Analysis in CODEX_PATTERNS_SUMMARY.md
- **Difficulty**: ⭐⭐⭐⭐ Expert
- **Time**: 6-8 hours

**What You'll Learn:**
- Multi-layer security
- Platform sandboxing
- Command whitelisting
- Defense-in-depth

**Codex Reference**: `codex-rs/core/src/safety.rs`, `codex-rs/execpolicy/`

---

### Advanced Patterns

#### 3. Parallelization ⭐⭐⭐⭐⭐
- **Folder**: `03-parallelization/`
- **Difficulty**: ⭐⭐⭐⭐ Expert
- **Codex Reference**: `codex-rs/core/src/tools/parallel.rs`

#### 10. MCP Integration ⭐⭐⭐⭐⭐
- **Folder**: `10-mcp-integration/`
- **Difficulty**: ⭐⭐⭐⭐ Expert
- **Codex Reference**: `codex-rs/mcp-client/`, `codex-rs/mcp-server/`

---

## 🚀 Complete Agent Example

**Folder**: `complete-agent-example/`

The crown jewel of these learning materials. A production-ready agent implementation combining all major patterns:

**Files**:
- `README.md` - Architecture overview
- `complete_agent.py` - Full implementation (500+ lines)
- `example_usage.py` - Demo scenarios

**Patterns Integrated**:
1. ✅ Prompt Chaining - Multi-turn loop
2. ✅ Routing - Tool dispatch
3. ✅ Tool Use - External integration
4. ✅ Memory Management - State persistence
5. ✅ Exception Handling - Retry logic
6. ✅ Human-in-the-Loop - Approvals
7. ✅ Guardrails - Safety checks

**Time to Study**: 8-10 hours
**Difficulty**: ⭐⭐⭐⭐ Expert

---

## 💻 Code Examples Summary

### Quick Reference

```python
# Pattern 1: Prompt Chaining
from learning-material.01-prompt-chaining.pattern_simple import simple_chain_example
simple_chain_example()

# Pattern 2: Routing
from learning-material.02-routing.pattern_simple import demo_routing
demo_routing()

# Pattern 5: Tool Use
from learning-material.05-tool-use.pattern_simple import demo_tool_use
demo_tool_use()

# Complete Agent
from learning-material.complete-agent-example.complete_agent import CodexInspiredAgent
agent = CodexInspiredAgent()
result = agent.run("Your task here")
```

---

## 📊 Pattern Implementation Status

### ✅ Fully Implemented (8 patterns)
- Pattern 1: Prompt Chaining (simple + advanced)
- Pattern 2: Routing (simple)
- Pattern 3: Parallelization (simple)
- Pattern 5: Tool Use (simple)
- Pattern 16: Sandbox Escalation (advanced)
- Pattern 17: Turn Diff Tracking (advanced)
- Pattern 18: Rollout System (advanced)
- Complete Agent Example (all patterns integrated)

### ⚠️ Analysis Only (14 patterns)
- Pattern 4: Reflection
- Pattern 6: Planning
- Pattern 7: Multi-Agent
- Pattern 8: Memory Management
- Pattern 9: Learning/Adaptation
- Pattern 10: MCP Integration
- Pattern 11: Goal Setting
- Pattern 12: Exception Handling
- Pattern 13: Human-in-the-Loop
- Pattern 14: Knowledge Retrieval (RAG)
- Pattern 15: Reasoning Techniques
- Pattern 19: Evaluation/Monitoring
- Pattern 20: Prioritization
- Pattern 21: Exploration/Discovery

---

## 🎓 Suggested Study Sequence

### Foundations
```
Monday:    Read main README + Pattern Summary
Tuesday:   Pattern 1 (Prompt Chaining) - Simple
Wednesday: Pattern 1 - Advanced
Thursday:  Pattern 5 (Tool Use) - Simple
Friday:    Pattern 5 - Advanced
Weekend:   Build your own simple chain with tools
```

### Intermediate
```
Monday:    Pattern 2 (Routing) - Simple
Tuesday:   Pattern 2 - Advanced
Wednesday: Pattern 8 (Memory) - Simple
Thursday:  Pattern 12 (Exception Handling)
Friday:    Pattern 13 (Human-in-the-Loop)
Weekend:   Integrate patterns 1, 2, 5, 8
```

### Advanced
```
Monday:    Pattern 3 (Parallelization)
Tuesday:   Pattern 18 (Guardrails/Safety)
Wednesday: Complete Agent - Read code
Thursday:  Complete Agent - Run examples
Friday:    Complete Agent - Modify/extend
Weekend:   Build your complete agent
```

### Mastery
```
Monday:    Codex source code - codex.rs
Tuesday:   Codex source code - tools/
Wednesday: Codex source code - safety.rs
Thursday:  Design your own agent
Friday:    Implement your design
Weekend:   Polish and test
```

---

## 🛠️ Setup & Prerequisites

### Required Software
```bash
# Python 3.8+
python --version

# OpenAI Python SDK
pip install openai aiohttp

# Optional: for testing
pip install pytest pytest-asyncio
```

### Environment Setup
```bash
# Clone repository (if needed)
cd /path/to/codex

# Navigate to learning materials
cd learning-material

# Set OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Run an example
cd 01-prompt-chaining
python pattern_simple.py
```

### Verify Setup
```bash
# Test import
python -c "import openai; print('OpenAI SDK OK')"

# Test API key
python -c "import os; print('API Key:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
```

---

## 📝 Practice Exercises

### Exercise 1: Extend Prompt Chaining
**Goal**: Add a 4th step to the simple chain

**Tasks**:
1. Read `01-prompt-chaining/pattern_simple.py`
2. Add validation step after recommendations
3. Test with different inputs

**Time**: 30 minutes
**Difficulty**: ⭐ Beginner

---

### Exercise 2: Build Custom Tool
**Goal**: Create a new tool for the agent

**Tasks**:
1. Read `05-tool-use/pattern_simple.py`
2. Add a "search_web" tool (mock implementation)
3. Update tool specs
4. Test tool invocation

**Time**: 1 hour
**Difficulty**: ⭐⭐ Intermediate

---

### Exercise 3: Implement Approval Policy
**Goal**: Add a new approval policy

**Tasks**:
1. Read `complete-agent-example/complete_agent.py`
2. Add "AUTO_READ" policy (auto-approve reads, ask for writes)
3. Update SafetyChecker logic
4. Test with different scenarios

**Time**: 2 hours
**Difficulty**: ⭐⭐⭐ Advanced

---

### Exercise 4: Build Mini-Agent
**Goal**: Create a specialized agent from scratch

**Tasks**:
1. Choose a domain (e.g., data analysis, code review)
2. Implement patterns 1, 2, 5, 8
3. Add 3-5 domain-specific tools
4. Test end-to-end workflow

**Time**: 8-10 hours
**Difficulty**: ⭐⭐⭐⭐ Expert

---

## 🔗 External Resources

### Documentation
- **Codex Docs**: `/docs/` in main repository
- **OpenAI Function Calling**: https://platform.openai.com/docs/guides/function-calling
- **MCP Specification**: https://modelcontextprotocol.io/
- **LangGraph**: https://langchain-ai.github.io/langgraph/

### Papers & Articles
- "ReAct: Synergizing Reasoning and Acting in Language Models"
- "Toolformer: Language Models Can Teach Themselves to Use Tools"
- "Tree of Thoughts: Deliberate Problem Solving with Large Language Models"

### Related Projects
- **LangChain**: Framework for LLM applications
- **AutoGPT**: Autonomous GPT-4 agent
- **BabyAGI**: Task-driven autonomous agent

---

## 🤝 Contributing

Found an issue? Want to improve these materials?

1. Check existing issues
2. Open a discussion
3. Submit a PR with improvements

These are educational materials, so clarity and correctness are paramount!

---

## 📄 License

These learning materials are provided for educational purposes. See main Codex repository for license details.

---

## ✨ What's Next?

After completing these materials, you should be able to:

1. ✅ Design multi-turn agentic workflows
2. ✅ Implement safe tool execution
3. ✅ Build approval workflows
4. ✅ Handle errors gracefully
5. ✅ Manage conversation state
6. ✅ Route between specialized handlers
7. ✅ Create production-ready agents

**Ready to start?** Begin with the [main README](./README.md)! 🚀

---

**Happy Learning!** 🎓

Questions? Comments? Open an issue or start a discussion!

