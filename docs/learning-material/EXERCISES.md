# 🎯 Practical Exercises

> **Hands-on practice to solidify your understanding**

## 📋 Exercise Format

Each exercise includes:
- **Difficulty**: ⭐ (Beginner) to ⭐⭐⭐⭐ (Expert)
- **Patterns**: Which patterns you'll practice
- **Learning Goals**: What you'll master
- **Tasks**: Step-by-step instructions
- **Solution Hints**: Guidance if you get stuck

---

## 🟢 Beginner Exercises

### Exercise 1: Extend a Chain ⭐

**Pattern**: Prompt Chaining (1)  
**File**: `01-prompt-chaining/pattern_simple.py`

**Learning Goals:**
- Understand sequential processing
- Modify existing chains
- Add new steps

**Tasks:**
1. Open `pattern_simple.py`
2. Add a 4th step that validates the recommendations from step 3
3. The validation should check if recommendations are actionable
4. Print validation results

**Hints:**
```python
# Step 4: Validate recommendations
step4_prompt = f"""
Review these recommendations and validate if they are:
1. Specific and actionable
2. Feasible to implement
3. Likely to solve the problem

Recommendations:
{step3_output}

Provide a brief validation summary.
"""
```

**Success Criteria:**
- [ ] Chain runs without errors
- [ ] 4th step uses output from step 3
- [ ] Validation makes sense

---

### Exercise 2: Build a Simple Tool ⭐

**Pattern**: Tool Use (5)  
**File**: `05-tool-use/pattern_simple.py`

**Learning Goals:**
- Create custom tools
- Define tool specifications
- Test tool invocation

**Tasks:**
1. Create a new tool called `count_words`
2. It should count words in a text string
3. Add tool specification for OpenAI API
4. Test it with a query like "Count words in: hello world"

**Hints:**
```python
def count_words(text: str) -> str:
    """Count words in text."""
    words = text.split()
    return f"Word count: {len(words)}"

# Add to TOOL_SPECS:
{
    "type": "function",
    "function": {
        "name": "count_words",
        "description": "Count words in a text string",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to count words in"
                }
            },
            "required": ["text"]
        }
    }
}
```

**Success Criteria:**
- [ ] Tool defined correctly
- [ ] LLM calls your tool
- [ ] Word count is accurate

---

### Exercise 3: Add Error Handling ⭐

**Pattern**: Exception Handling (12)

**Learning Goals:**
- Handle failures gracefully
- Implement retry logic
- Log errors properly

**Tasks:**
1. Create a function that sometimes fails randomly
2. Wrap it with retry logic (3 attempts)
3. Add exponential backoff (1s, 2s, 4s)
4. Log each attempt

**Hints:**
```python
import random
import time

def flaky_function():
    """Fails 50% of the time."""
    if random.random() < 0.5:
        raise ValueError("Random failure!")
    return "Success!"

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
            time.sleep(wait_time)
```

**Success Criteria:**
- [ ] Function retries on failure
- [ ] Backoff timing is correct
- [ ] Final failure is propagated

---

## 🟡 Intermediate Exercises

### Exercise 4: Build a Router ⭐⭐

**Pattern**: Routing (2)

**Learning Goals:**
- Intent classification
- Dynamic dispatch
- Handler registry

**Tasks:**
1. Create 3 specialized handlers (search, analyze, generate)
2. Build a classifier that routes to correct handler
3. Test with 10 different queries
4. Measure routing accuracy

**Hints:**
```python
def classify_intent_with_llm(query: str) -> str:
    """Use LLM to classify intent."""
    # Your code here
    pass

HANDLERS = {
    "search": search_handler,
    "analyze": analyze_handler,
    "generate": generate_handler,
}

def route_query(query: str):
    intent = classify_intent_with_llm(query)
    handler = HANDLERS.get(intent, default_handler)
    return handler(query)
```

**Success Criteria:**
- [ ] Classification is >80% accurate
- [ ] All handlers work correctly
- [ ] Fallback handler exists

---

### Exercise 5: Implement Memory ⭐⭐

**Pattern**: Memory Management (8)

**Learning Goals:**
- State persistence
- History management
- Session resumption

**Tasks:**
1. Create a `ConversationMemory` class
2. Store last 5 turns
3. Save to JSON file
4. Load and resume conversation

**Hints:**
```python
class ConversationMemory:
    def __init__(self, max_turns=5):
        self.turns = []
        self.max_turns = max_turns
    
    def add_turn(self, prompt, response):
        self.turns.append({"prompt": prompt, "response": response})
        if len(self.turns) > self.max_turns:
            self.turns.pop(0)  # Remove oldest
    
    def get_context(self):
        # Build context string from turns
        pass
    
    def save(self, filepath):
        # Save to JSON
        pass
    
    def load(self, filepath):
        # Load from JSON
        pass
```

**Success Criteria:**
- [ ] Turns are stored correctly
- [ ] History limits work
- [ ] Save/load preserves state

---

### Exercise 6: Add Approval System ⭐⭐

**Pattern**: Human-in-the-Loop (13)

**Learning Goals:**
- Approval workflows
- Safety checks
- User interaction

**Tasks:**
1. Create a `SafetyChecker` class
2. Define dangerous operations (file delete, network access)
3. Request approval before dangerous ops
4. Allow session-level approvals

**Hints:**
```python
class SafetyChecker:
    DANGEROUS_OPS = ["delete", "network", "execute"]
    
    def __init__(self):
        self.approved_for_session = set()
    
    def needs_approval(self, operation):
        if operation in self.approved_for_session:
            return False
        return any(danger in operation for danger in self.DANGEROUS_OPS)
    
    def request_approval(self, operation):
        print(f"⚠️  Approve '{operation}'? (y/n/session): ")
        response = input().strip().lower()
        
        if response == "session":
            self.approved_for_session.add(operation)
            return True
        return response == "y"
```

**Success Criteria:**
- [ ] Dangerous ops require approval
- [ ] Session approvals work
- [ ] User can deny operations

---

## 🔴 Advanced Exercises

### Exercise 7: Implement Parallelization ⭐⭐⭐

**Pattern**: Parallelization (3)

**Learning Goals:**
- Async/await
- Concurrent execution
- Result aggregation

**Tasks:**
1. Create a tool executor with parallel support
2. Some tools run parallel, others serial
3. Serial tools wait for parallel tasks
4. Benchmark speed improvement

**Hints:**
```python
import asyncio

class ParallelExecutor:
    PARALLEL_TOOLS = {"read", "fetch"}
    SERIAL_TOOLS = {"write", "execute"}
    
    def __init__(self):
        self.pending = []
    
    async def execute_tool(self, tool_name, args):
        if tool_name in self.PARALLEL_TOOLS:
            task = self._do_tool(tool_name, args)
            self.pending.append(task)
        else:
            # Wait for pending
            if self.pending:
                await asyncio.gather(*self.pending)
                self.pending = []
            # Execute serial
            await self._do_tool(tool_name, args)
```

**Success Criteria:**
- [ ] Parallel tools run concurrently
- [ ] Serial tools execute in order
- [ ] Speedup is measurable

---

### Exercise 8: Build Complete Mini-Agent ⭐⭐⭐⭐

**Patterns**: 1, 2, 5, 8, 12, 13

**Learning Goals:**
- System integration
- Production patterns
- End-to-end workflows

**Tasks:**
1. Choose a domain (code review, data analysis, etc.)
2. Implement patterns 1, 2, 5, 8
3. Add 5+ custom tools
4. Include error handling and approvals
5. Write documentation

**Requirements:**
- Multi-turn conversations
- Tool routing
- State persistence
- Error recovery
- Safety checks
- Clear documentation

**Success Criteria:**
- [ ] Agent completes complex tasks
- [ ] All patterns integrated
- [ ] Error handling works
- [ ] Documentation is clear
- [ ] Demo video/screenshots

---

## 🎓 Challenge Projects

### Challenge 1: Code Review Agent ⭐⭐⭐⭐

**Description**: Build an agent that reviews code for:
- Style issues
- Potential bugs
- Performance problems
- Security vulnerabilities
- Test coverage

**Tools Needed:**
- `read_file` - Read source code
- `run_linter` - Execute static analysis
- `run_tests` - Run test suite
- `generate_report` - Create review document

---

### Challenge 2: Research Assistant ⭐⭐⭐

**Description**: Build an agent that:
- Searches multiple sources
- Summarizes findings
- Generates citations
- Creates reports

**Tools Needed:**
- `web_search` - Search the web
- `read_url` - Fetch webpage content
- `save_notes` - Persist research
- `generate_report` - Create final document

---

### Challenge 3: Data Analyst ⭐⭐⭐⭐

**Description**: Build an agent that:
- Loads CSV/JSON data
- Performs statistical analysis
- Generates visualizations
- Creates reports
- Handles missing data

**Tools Needed:**
- `load_data` - Read data files
- `analyze_stats` - Calculate statistics
- `create_chart` - Generate visualizations
- `export_report` - Save results

---

## 📊 Exercise Tracker

Track your progress:

| Exercise | Started | Completed | Notes |
|----------|---------|-----------|-------|
| Ex 1: Extend Chain | ⬜ | ⬜ | |
| Ex 2: Build Tool | ⬜ | ⬜ | |
| Ex 3: Error Handling | ⬜ | ⬜ | |
| Ex 4: Build Router | ⬜ | ⬜ | |
| Ex 5: Implement Memory | ⬜ | ⬜ | |
| Ex 6: Approval System | ⬜ | ⬜ | |
| Ex 7: Parallelization | ⬜ | ⬜ | |
| Ex 8: Mini-Agent | ⬜ | ⬜ | |
| Challenge 1 | ⬜ | ⬜ | |
| Challenge 2 | ⬜ | ⬜ | |
| Challenge 3 | ⬜ | ⬜ | |

---

## 💡 Tips for Success

1. **Start Small**: Begin with beginner exercises
2. **Read First**: Understand the pattern before coding
3. **Run Examples**: Study existing code
4. **Experiment**: Modify examples to learn
5. **Debug**: Use print statements liberally
6. **Test**: Verify each component works
7. **Document**: Write clear comments
8. **Ask**: Seek help when stuck

---

## 🆘 Getting Unstuck

### If you're stuck on an exercise:

1. **Re-read** the pattern README
2. **Study** the example code
3. **Break down** the problem
4. **Google** specific errors
5. **Check** the hints section
6. **Ask** in discussions

### Common Issues:

**"My code doesn't run"**
- Check syntax errors
- Verify imports
- Test each function independently

**"The LLM doesn't call my tool"**
- Check tool specification format
- Verify description is clear
- Ensure parameters are correct

**"Results are inconsistent"**
- Set temperature=0 for deterministic output
- Use more specific prompts
- Add examples to prompts

---

## 🎯 Next Steps

After completing exercises:

1. **Review** your solutions
2. **Compare** with example code
3. **Optimize** for performance
4. **Share** your work
5. **Move** to next difficulty level

---

**Ready to practice?** Start with [Exercise 1 →](#exercise-1-extend-a-chain-)

Good luck! 🚀

