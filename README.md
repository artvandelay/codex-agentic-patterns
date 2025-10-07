# 🤖 Codex Agentic Patterns

> **Learn to build production-ready AI agents through real-world patterns extracted from OpenAI's Codex CLI**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com/)
[![Documentation](https://img.shields.io/badge/docs-live-brightgreen.svg)](https://artvandelay.github.io/codex-agentic-patterns/)

---

## 🌐 **[📖 Read the Interactive Documentation →](https://artvandelay.github.io/codex-agentic-patterns/)**

**Beautiful, searchable, mobile-friendly documentation with:**
- ✨ **Interactive navigation** through all 21 patterns
- 🔍 **Full-text search** across all content  
- 📱 **Mobile responsive** design
- 🌓 **Dark/light mode** toggle
- 📊 **Progress tracking** through learning paths

---

## 🎯 What Is This?

The **Codex Agentic Patterns** is a comprehensive learning resource that teaches you to build intelligent AI agents by studying **real production code** from OpenAI's Codex CLI. Instead of toy examples, you'll learn from battle-tested patterns used in production systems.

### 📚 What You'll Master

✅ **21 Agentic Design Patterns** - Complete coverage  
✅ **8 Fully Implemented Patterns** - With runnable Python code  
✅ **Production-Grade Examples** - Not academic demos  
✅ **Safety & Error Handling** - Real-world robustness  
✅ **Multi-Turn Conversations** - Complex agent workflows  
✅ **Tool Integration** - External system connections  
✅ **Human-in-the-Loop** - Approval and oversight patterns  

---

## 🚀 Quick Start

### 🌐 **Option 1: Browse Online (Recommended)**
**[Visit the Interactive Documentation →](https://artvandelay.github.io/codex-agentic-patterns/)**

No setup required! Browse all patterns, search content, and explore at your own pace.

### 💻 **Option 2: Run Code Locally**

```bash
# Clone the repository
git clone https://github.com/artvandelay/codex-agentic-patterns.git
cd codex-agentic-patterns

# Navigate to learning materials  
cd docs/learning-material

# Set up environment
export OPENAI_API_KEY="your-key-here"
pip install openai

# Run your first example
cd 01-prompt-chaining
python pattern_simple.py
```

**🎉 Start learning production agentic patterns!**

---

## 📖 Learning Paths

### 🟢 Beginner (1-2 weeks)
Start here if you're new to AI agents:
- [**Quick Start Guide**](./doc./docs/learning-material/QUICKSTART.md) ⚡
- [**Pattern 1: Prompt Chaining**](./docs/learning-material/01-prompt-chaining/) 
- [**Pattern 5: Tool Use**](./docs/learning-material/05-tool-use/)

### 🟡 Intermediate (2-3 weeks)  
For developers with some AI experience:
- [**Complete Navigation**](./docs/learning-material/INDEX.md) 📚
- [**Pattern 2: Routing**](./docs/learning-material/02-routing/)
- [**Memory & State Management**](./docs/learning-material/08-memory-management/)

### 🔴 Advanced (3-4 weeks)
For experienced developers wanting production patterns:
- [**Codex Patterns Analysis**](./docs/learning-material/CODEX_PATTERNS_SUMMARY.md) 📊
- [**Advanced Sandbox Escalation**](./docs/learning-material/16-sandbox-escalation/) ⭐
- [**Complete Agent Example**](./docs/learning-material/complete-agent-example/)

---

## 🏗️ What's Inside?

### 📁 Repository Structure

```
codex-agentic-patterns/
├── docs/learning-material/      🎓 Your learning journey starts here
│   ├── 01-prompt-chaining/      ✅ Sequential workflows  
│   ├── 02-routing/              ✅ Dynamic dispatch
│   ├── 03-parallelization/      ✅ Concurrent execution
│   ├── 05-tool-use/             ✅ External integration
│   ├── 16-sandbox-escalation/   ⭐ Advanced: Multi-stage execution
│   ├── 17-turn-diff-tracking/   ⭐ Advanced: Git-style diffs  
│   ├── 18-rollout-system/       ⭐ Advanced: Session replay
│   └── complete-agent-example/  🏆 Full production agent
└── docs/                        📚 Documentation site
```

### 🔗 Related Repositories

This learning resource analyzes patterns from:
- **[OpenAI Codex CLI](https://github.com/openai/codex)** - The original Rust implementation we study

### 📊 By The Numbers

- **~9,000 lines** of learning materials
- **8 patterns** fully implemented in Python
- **14 patterns** analyzed from Codex source
- **11 hands-on exercises** 
- **500+ lines** complete agent example
- **Production-grade** error handling & safety

---

## 🎓 How This Was Created

This learning resource was created using **AI-assisted education** with [Cursor](https://cursor.sh/) and grounded in real production code:

### 📝 Our Process

1. **Source Analysis**: Deep dive into [OpenAI's Codex CLI](https://github.com/openai/codex) Rust codebase
2. **Pattern Extraction**: Identified agentic patterns using the [Agentic Design Patterns textbook](https://docs.google.com/document/d/1rsaK53T3Lg5KoGwvf8ukOUvbELRtH-V0LnOIFDxBryE/preview?pli=1&tab=t.0#heading=h.pxcur8v2qagu)
3. **Python Implementation**: Abstracted patterns into learnable Python examples
4. **Production Focus**: Emphasized real-world complexity, not toy examples
5. **Iterative Refinement**: Polished through multiple review cycles

### 🙏 Attribution

This work builds upon:

- **[Agentic Design Patterns Complete](https://docs.google.com/document/d/1rsaK53T3Lg5KoGwvf8ukOUvbELRtH-V0LnOIFDxBryE/preview?pli=1&tab=t.0#heading=h.pxcur8v2qagu)** - The foundational textbook defining 21 agentic patterns
- **[OpenAI Codex CLI](https://github.com/openai/codex)** - Production Rust implementation providing real-world examples
- **[Cursor](https://cursor.sh/)** - AI-powered development environment used for analysis and content generation

*This is an educational resource created to make agentic AI patterns accessible to developers worldwide.*

---

## 🌟 Why This Matters

### ❌ Traditional AI Tutorials
- Toy examples that don't scale
- Academic focus, not production-ready
- Missing error handling & edge cases
- No real-world complexity

### ✅ Agentic Patterns Codebook
- **Production patterns** from real systems
- **Complete error handling** & retry logic
- **Safety mechanisms** & approval workflows  
- **Multi-turn conversations** & state management
- **Tool integration** with external systems

---

## 🛠️ Prerequisites

- **Python 3.8+** with pip
- **OpenAI API key** ([get one here](https://platform.openai.com/api-keys))
- **Basic understanding** of Python and APIs
- **Curiosity** about building intelligent agents!

---

## 📚 Learning Resources

### 🌐 **Interactive Documentation** (Start Here!)
- **[Main Documentation Site](https://artvandelay.github.io/codex-agentic-patterns/)** - Beautiful, searchable interface
- **[Getting Started Guide](https://artvandelay.github.io/codex-agentic-pattern./docs/learning-material/00-READ-ME-FIRST/)** - Your entry point  
- **[Quick Setup](https://artvandelay.github.io/codex-agentic-pattern./docs/learning-material/QUICKSTART/)** - Get running in 10 minutes
- **[Complete Index](https://artvandelay.github.io/codex-agentic-pattern./docs/learning-material/INDEX/)** - Navigate all content

### 🎯 Practice & Exercises  
- **[11 Hands-on Exercises](https://artvandelay.github.io/codex-agentic-pattern./docs/learning-material/EXERCISES/)** - From beginner to expert
- **[Pattern Implementations](https://artvandelay.github.io/codex-agentic-pattern./docs/learning-material/01-prompt-chaining/)** - Runnable Python code
- **[Complete Agent Example](https://artvandelay.github.io/codex-agentic-pattern./docs/learning-material/complete-agent-example/)** - 500+ line production example

### 🔍 Deep Analysis
- **[Codex Patterns Analysis](https://artvandelay.github.io/codex-agentic-pattern./docs/learning-material/CODEX_PATTERNS_SUMMARY/)** - How production systems work  
- **[Advanced Patterns](https://artvandelay.github.io/codex-agentic-pattern./docs/learning-material/16-sandbox-escalation/)** - Production complexity
- **[Original Codex Source](https://github.com/openai/codex)** - Rust implementation

---

## 🤝 Contributing

Found something unclear? Want to improve the materials?

1. **Open an issue** - Report bugs or suggest improvements
2. **Start a discussion** - Ask questions or share ideas  
3. **Submit a PR** - Fix typos, add examples, improve explanations

**Guidelines**: These are educational materials, so clarity and accuracy are paramount!

---

## 📄 License

This educational resource is licensed under the [MIT License](./LICENSE).

The original Codex CLI and textbook retain their respective licenses.

---

## 🌟 Star & Share

If this helped you learn agentic AI patterns, please:

⭐ **Star this repository**  
🐦 **Share on Twitter**  
💼 **Share on LinkedIn**  
📝 **Write a blog post**  

Help others discover production-grade agentic patterns!

---

## 🔗 Links

- **[Learning Materials](./docs/learning-material/)** - Start your journey
- **[Agentic Design Patterns Textbook](https://docs.google.com/document/d/1rsaK53T3Lg5KoGwvf8ukOUvbELRtH-V0LnOIFDxBryE/preview?pli=1&tab=t.0#heading=h.pxcur8v2qagu)** - Original theory
- **[OpenAI Codex CLI](https://github.com/openai/codex)** - Production implementation
- **[OpenAI Platform](https://platform.openai.com/)** - Get your API key
- **[Cursor](https://cursor.sh/)** - AI development environment

---

**🚀 Ready to build the future of AI? [Start learning →](./docs/learning-material/00-READ-ME-FIRST.md)**

---

*Built with ❤️ using AI-assisted education • Created October 2025 • Version 1.0*