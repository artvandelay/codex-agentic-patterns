# 🚀 Quick Start Guide

> **Get up and running in 10 minutes**

## 📋 Prerequisites

Before you begin, ensure you have:

```bash
# Python 3.8 or higher
python --version  # Should show 3.8+

# pip (Python package manager)
pip --version
```

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies

```bash
# Install OpenAI Python SDK
pip install openai

# Optional: For async examples
pip install aiohttp
```

### Step 2: Set API Key

```bash
# Export your OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"

# Verify it's set
echo $OPENAI_API_KEY
```

> **💡 Tip**: Add this to your `~/.bashrc` or `~/.zshrc` to make it permanent

### Step 3: Test Your Setup

```bash
# Navigate to learning materials
cd /path/to/codex/learning-material

# Run a simple example
cd 01-prompt-chaining
python pattern_simple.py
```

If you see output without errors, you're all set! 🎉

---

## 🎯 Your First 30 Minutes

### Minute 0-10: Understand Prompt Chaining

```bash
cd 01-prompt-chaining
cat README.md         # Read the pattern explanation
python pattern_simple.py   # Run basic example
```

**What you'll see:**
- A multi-step workflow
- Each step builds on previous output
- Results fed back into next step

### Minute 10-20: Try Tool Use

```bash
cd ../05-tool-use
cat README.md         # Read about tools
python pattern_simple.py   # Run tool examples
```

**What you'll see:**
- LLM calling external functions
- Different tool types (time, weather, calculator)
- Safety checks in action

### Minute 20-30: Explore the Complete Agent

```bash
cd ../complete-agent-example
cat README.md         # Architecture overview
python complete_agent.py   # Run complete agent
```

**What you'll see:**
- Multi-pattern integration
- Approval workflows
- Error handling
- Full agent lifecycle

---

## 🎓 Learning Paths

Choose your path based on your experience level:

### 🟢 Beginner Path

[Pattern 1: Prompt Chaining](./01-prompt-chaining/README.md)
```bash
cd 01-prompt-chaining
python pattern_simple.py    # Basic
python pattern_advanced.py  # Advanced
```

[Pattern 5: Tool Use](./05-tool-use/README.md)
```bash
cd 05-tool-use
python pattern_simple.py
```

Build your own simple agent
```python
# Combine patterns 1 and 5
# Create a research assistant
# Add 2-3 custom tools
```

### 🟡 Intermediate Path

[Pattern 2: Routing](./02-routing/README.md)
```bash
cd 02-routing
python pattern_simple.py
```

[Pattern 8: Memory Management](./08-memory-management/README.md)

[Pattern 12: Exception Handling](./12-exception-handling/README.md)

### 🔴 Advanced Path

[Pattern 3: Parallelization](./03-parallelization/README.md)

[Pattern 18: Guardrails/Safety](./18-guardrails-safety/README.md)

[Complete Agent Example](./complete-agent-example/README.md)

---

## 💻 Quick Examples

### Example 1: Simple Chain (5 lines)

```python
from openai import OpenAI

client = OpenAI()

# Step 1: Analyze
response1 = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Analyze: Python is great"}]
)
analysis = response1.choices[0].message.content

# Step 2: Expand (uses Step 1 output)
response2 = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": f"Expand on: {analysis}"}]
)
print(response2.choices[0].message.content)
```

### Example 2: Tool Use (10 lines)

```python
from openai import OpenAI
import json

client = OpenAI()

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }
}]

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools
)

# LLM will call the tool
print(response.choices[0].message.tool_calls)
```

### Example 3: Simple Agent (20 lines)

```python
from complete_agent_example.complete_agent import CodexInspiredAgent, ApprovalPolicy

# Create agent
agent = CodexInspiredAgent(
    model="gpt-4",
    approval_policy=ApprovalPolicy.FULL_AUTO
)

# Run task
result = agent.run("Calculate 15% of 2500")

print(f"Result: {result}")

# Save session
agent.save_session("my_session.json")
```

---

## 🐛 Troubleshooting

### Problem: "No module named 'openai'"

**Solution:**
```bash
pip install openai
```

### Problem: "API key not found"

**Solution:**
```bash
export OPENAI_API_KEY="your-key-here"
# Or create .env file with: OPENAI_API_KEY=your-key-here
```

### Problem: "Rate limit exceeded"

**Solution:**
- Wait a few seconds between calls
- Use time.sleep(1) between requests
- Check your API usage at platform.openai.com

### Problem: Import errors

**Solution:**
```bash
# Make sure you're in the right directory
cd /path/to/codex/learning-material

# Check Python path
python -c "import sys; print(sys.path)"

# Run with explicit path
python -m 01-prompt-chaining.pattern_simple
```

---

## 📚 Next Steps

### After Quick Start

1. ✅ **Read the Patterns Summary**
   - File: `CODEX_PATTERNS_SUMMARY.md`
   - 
   - Understand all 21 patterns

2. ✅ **Study Codex Source Code**
   - Directory: `codex-rs/core/src/`
   - Start with: `codex.rs`, `tools/router.rs`
   - See real production implementation

3. ✅ **Complete the Exercises**
   - File: `INDEX.md` (Exercise section)
   - Build custom tools
   - Extend the agent

4. ✅ **Build Your Own Agent**
   - Choose a domain (code review, data analysis, etc.)
   - Implement core patterns
   - Add domain-specific tools

---

## 🎯 Practice Projects

### Project 1: Research Assistant (Beginner)
  
**Patterns**: 1, 5, 8

Build an agent that:
- Searches for information
- Summarizes findings
- Saves research notes

### Project 2: Code Reviewer (Intermediate)
  
**Patterns**: 1, 2, 5, 8, 12

Build an agent that:
- Reads code files
- Identifies issues
- Suggests improvements
- Generates test cases

### Project 3: Data Analyst (Advanced)
  
**Patterns**: 1, 2, 3, 5, 8, 12, 13

Build an agent that:
- Reads CSV/JSON data
- Performs statistical analysis
- Generates visualizations
- Creates reports
- Asks for approval before changes

---

## 🆘 Getting Help

### Documentation
- **Main README**: `./README.md`
- **Index**: `./INDEX.md`
- **Pattern Summary**: `./CODEX_PATTERNS_SUMMARY.md`

### Resources
- **OpenAI Docs**: https://platform.openai.com/docs
- **Codex Repo**: https://github.com/openai/codex
- **MCP Docs**: https://modelcontextprotocol.io/

### Community
- Open an issue on GitHub
- Check existing discussions
- Review example code

---

## ✅ Checklist

Before moving on, make sure you can:

- [ ] Run Python examples without errors
- [ ] See LLM responses in terminal
- [ ] Understand basic prompt chaining
- [ ] Execute a tool call
- [ ] Read and modify example code
- [ ] Save/load agent state

If you checked all boxes, you're ready to dive deeper! 🎉

---

## 🚀 What's Next?

1. **Choose Your Path** (Beginner/Intermediate/Advanced)
2. **Study Patterns Sequentially** (1 → 5 → 8 → 2 → ...)
3. **Run All Examples** in each pattern folder
4. **Modify Examples** to understand behavior
5. **Build Your Own** mini-agent
6. **Read Codex Source** for production patterns

---

**Ready?** Start with [Pattern 1: Prompt Chaining →](./01-prompt-chaining/README.md)

Happy Learning! 🎓

---


- Basic Understanding: 1 week
- Intermediate Skills: 2-3 weeks  
- Advanced Mastery: 4-6 weeks
- Production-Ready: 2-3 months

*The journey of a thousand miles begins with a single step.* 🥋

