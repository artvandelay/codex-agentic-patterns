# Backstory: How This Book Came to Be

## The Backstory

While reading through the [Agentic Design Patterns textbook](https://docs.google.com/document/d/1rsaK53T3Lg5KoGwvf8ukOUvbELRtH-V0LnOIFDxBryE/preview), I got curious about real-world implementations. The patterns were fascinating in theory, but I wanted to see them in action.

I'd heard about [OpenAI's Codex CLI](https://github.com/openai/codex) - a production AI coding assistant that had been making waves. Perfect, I thought. Let me dive into their codebase to see these patterns in practice.

**Plot twist**: The entire codebase was in Rust. 🦀

Not being fluent in Rust, I did what any pragmatic developer would do - I enlisted an AI assistant (Cursor) to help me analyze the codebase and extract the agentic patterns. What started as a simple exploration turned into something much bigger.

## The Process

Using Cursor, I systematically went through Codex's ~100,000 lines of Rust code, identifying real implementations of:

- **Prompt Chaining** in their conversation management
- **Tool Use** in their MCP integration  
- **Exception Handling** in their retry mechanisms
- **Human-in-the-Loop** in their approval workflows
- **Sandbox Escalation** in their security systems
- And 12+ more patterns...

Each pattern I found was then abstracted into clean Python implementations, complete with explanations of how Codex actually uses them in production.

## What Makes This Different

This isn't just another AI tutorial. It's a **grounded textbook** that bridges the gap between:

- 📚 **Theory** (the original Agentic Design Patterns book)
- 🏭 **Production Reality** (OpenAI's battle-tested Codex implementation)  
- 🐍 **Practical Code** (Python examples you can run and modify)

Every pattern here is backed by real code from a system handling millions of interactions. No toy examples, no academic hypotheticals - just production patterns you can actually use.

## The Tools Behind This

- **Source Material**: [Agentic Design Patterns textbook](https://docs.google.com/document/d/1rsaK53T3Lg5KoGwvf8ukOUvbELRtH-V0LnOIFDxBryE/preview)
- **Code Analysis**: [OpenAI Codex CLI](https://github.com/openai/codex) (100k+ lines of Rust)
- **AI Assistant**: Cursor (for Rust→Python pattern extraction)
- **Human Supervision**: Heavy oversight to ensure accuracy and usefulness

## Why Open Source?

The original textbook and Codex are both open resources. This felt like a natural extension - taking those ideas and making them more accessible to Python developers who want to build production-grade AI agents.

Plus, the best way to learn is by doing. All code is MIT licensed, so fork it, break it, improve it, and share what you learn.

---

*Ready to dive in? Start with [Chapter 1: Prompt Chaining](./learning-material/01-prompt-chaining/README.md) or jump to any pattern that interests you.*

*Discussed on [Hacker News](https://news.ycombinator.com/item?id=45509853)*
