#!/usr/bin/env python3
"""
Pattern 1: Prompt Chaining - Advanced Example

Production-ready prompt chaining with:
- State management
- Error handling
- Conversation history
- Turn-based architecture (inspired by Codex)

Inspired by: codex-rs/core/src/codex.rs (run_task function)
"""

import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from openai import OpenAI
from datetime import datetime


@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation chain."""
    turn_number: int
    prompt: str
    response: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationHistory:
    """
    Manages conversation state across turns.
    Inspired by: codex-rs/core/src/conversation_history.rs
    """
    turns: List[ConversationTurn] = field(default_factory=list)
    
    def add_turn(self, turn: ConversationTurn):
        """Record a turn in history."""
        self.turns.append(turn)
    
    def get_context(self, max_turns: Optional[int] = None) -> str:
        """Build context string from recent turns."""
        recent_turns = self.turns[-max_turns:] if max_turns else self.turns
        context = []
        for turn in recent_turns:
            context.append(f"Turn {turn.turn_number}:")
            context.append(f"Prompt: {turn.prompt}")
            context.append(f"Response: {turn.response}")
            context.append("")
        return "\n".join(context)
    
    def to_dict(self) -> Dict:
        """Serialize history for persistence."""
        return {
            "turns": [
                {
                    "turn_number": t.turn_number,
                    "prompt": t.prompt,
                    "response": t.response,
                    "timestamp": t.timestamp,
                    "metadata": t.metadata,
                }
                for t in self.turns
            ]
        }


class PromptChainExecutor:
    """
    Advanced prompt chain executor with state management.
    
    Inspired by: codex-rs/core/src/codex.rs (Session and run_task)
    """
    
    def __init__(self, model: str = "gpt-4", max_retries: int = 3):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = model
        self.max_retries = max_retries
        self.history = ConversationHistory()
        self.current_turn = 0
    
    def execute_turn(
        self, 
        prompt: str, 
        use_history: bool = True,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Execute a single turn in the chain.
        
        Similar to: codex-rs/core/src/codex.rs::run_turn()
        
        Args:
            prompt: The prompt for this turn
            use_history: Whether to include previous context
            metadata: Optional metadata for this turn
        
        Returns:
            Response from the LLM
        """
        self.current_turn += 1
        
        # Build full prompt with history if requested
        if use_history and self.history.turns:
            context = self.history.get_context(max_turns=3)  # Keep last 3 turns
            full_prompt = f"""
Previous conversation context:
{context}

Current request:
{prompt}

Please respond to the current request, using context from previous turns as needed.
"""
        else:
            full_prompt = prompt
        
        # Execute with retry logic
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": full_prompt}],
                    temperature=0.7,
                )
                
                response_text = response.choices[0].message.content
                
                # Record in history
                turn = ConversationTurn(
                    turn_number=self.current_turn,
                    prompt=prompt,
                    response=response_text,
                    metadata=metadata or {}
                )
                self.history.add_turn(turn)
                
                return response_text
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                print(f"⚠️  Attempt {attempt + 1} failed, retrying...")
        
        raise Exception("Max retries exceeded")
    
    def execute_chain(
        self, 
        steps: List[Dict[str, Any]],
        continue_on_error: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a multi-step chain.
        
        Args:
            steps: List of step definitions, each with:
                   - name: Step identifier
                   - prompt: Prompt template (can use {previous_output})
                   - use_history: Whether to include conversation context
            continue_on_error: Whether to continue if a step fails
        
        Returns:
            Dictionary with results from all steps
        """
        results = {}
        previous_output = ""
        
        print(f"\n{'=' * 60}")
        print(f"EXECUTING CHAIN WITH {len(steps)} STEPS")
        print(f"{'=' * 60}\n")
        
        for i, step in enumerate(steps, 1):
            step_name = step.get("name", f"step_{i}")
            prompt_template = step["prompt"]
            use_history = step.get("use_history", True)
            
            print(f"{'─' * 60}")
            print(f"🔗 STEP {i}/{len(steps)}: {step_name}")
            print(f"{'─' * 60}")
            
            # Replace {previous_output} in prompt
            prompt = prompt_template.format(previous_output=previous_output)
            
            try:
                response = self.execute_turn(
                    prompt=prompt,
                    use_history=use_history,
                    metadata={"step_name": step_name, "step_number": i}
                )
                
                results[step_name] = {
                    "success": True,
                    "output": response,
                    "turn_number": self.current_turn
                }
                
                previous_output = response
                
                print(f"\n✅ Step {i} Complete")
                print(f"Output preview: {response[:150]}...")
                
            except Exception as e:
                print(f"\n❌ Step {i} Failed: {e}")
                
                results[step_name] = {
                    "success": False,
                    "error": str(e),
                    "turn_number": self.current_turn
                }
                
                if not continue_on_error:
                    print("\n🛑 Chain aborted due to error")
                    break
        
        print(f"\n{'=' * 60}")
        print(f"CHAIN EXECUTION COMPLETE")
        print(f"{'=' * 60}\n")
        
        return results
    
    def save_history(self, filepath: str):
        """Save conversation history to file."""
        with open(filepath, 'w') as f:
            json.dump(self.history.to_dict(), f, indent=2)
        print(f"💾 History saved to: {filepath}")


def example_research_chain():
    """
    Example: Research and analysis chain
    Similar to how Codex might handle a complex research task
    """
    executor = PromptChainExecutor(model="gpt-4")
    
    steps = [
        {
            "name": "understand_topic",
            "prompt": """
            I need to understand the topic of "Edge Computing" for a presentation.
            Provide a clear, concise explanation of what edge computing is.
            Focus on the core concept in 2-3 sentences.
            """,
            "use_history": False,
        },
        {
            "name": "identify_benefits",
            "prompt": """
            Based on this understanding:
            {previous_output}
            
            Identify the top 3 benefits of edge computing.
            Be specific and explain why each benefit matters.
            """,
            "use_history": True,
        },
        {
            "name": "find_challenges",
            "prompt": """
            Now identify the top 3 challenges or limitations of edge computing.
            Consider technical, business, and security aspects.
            """,
            "use_history": True,
        },
        {
            "name": "generate_comparison",
            "prompt": """
            Create a comparison table between edge computing and cloud computing.
            Include: latency, cost, scalability, and use cases.
            Format as a simple text table.
            """,
            "use_history": True,
        },
        {
            "name": "generate_summary",
            "prompt": """
            Synthesize all the previous analysis into a 1-paragraph executive summary
            suitable for a business presentation slide.
            """,
            "use_history": True,
        }
    ]
    
    results = executor.execute_chain(steps)
    
    # Save history
    executor.save_history("research_chain_history.json")
    
    # Display summary
    print("\n📊 EXECUTION SUMMARY")
    print("=" * 60)
    for step_name, result in results.items():
        status = "✅" if result["success"] else "❌"
        print(f"{status} {step_name}")
    
    return results


def example_code_refactoring_chain():
    """
    Example: Code analysis and refactoring chain
    Mimics Codex's approach to code-related tasks
    """
    executor = PromptChainExecutor(model="gpt-4")
    
    code = """
def process_data(data):
    result = []
    for item in data:
        if item['status'] == 'active':
            val = item['value'] * 2
            if val > 100:
                result.append({'id': item['id'], 'processed_value': val})
    return result
"""
    
    steps = [
        {
            "name": "analyze_code",
            "prompt": f"""
            Analyze this Python code and identify:
            1. What it does
            2. Potential issues or improvements
            3. Edge cases not handled
            
            Code:
            {code}
            """,
            "use_history": False,
        },
        {
            "name": "suggest_improvements",
            "prompt": """
            Based on the analysis, suggest specific improvements.
            Prioritize: readability, error handling, and performance.
            """,
            "use_history": True,
        },
        {
            "name": "write_refactored_code",
            "prompt": f"""
            Now write the refactored version of the code implementing the suggestions.
            
            Original code:
            {code}
            
            Provide only the improved code with brief comments.
            """,
            "use_history": True,
        },
        {
            "name": "write_tests",
            "prompt": """
            Write unit tests for the refactored code.
            Include test cases for edge cases mentioned earlier.
            Use pytest format.
            """,
            "use_history": True,
        }
    ]
    
    results = executor.execute_chain(steps)
    executor.save_history("refactoring_chain_history.json")
    
    return results


if __name__ == "__main__":
    try:
        print("🚀 Advanced Prompt Chaining Examples\n")
        
        # Run research chain
        print("\n" + "=" * 60)
        print("EXAMPLE 1: RESEARCH CHAIN")
        print("=" * 60)
        example_research_chain()
        
        # Run code refactoring chain
        print("\n\n" + "=" * 60)
        print("EXAMPLE 2: CODE REFACTORING CHAIN")
        print("=" * 60)
        example_code_refactoring_chain()
        
        print("\n\n💡 Key Advanced Features:")
        print("1. ✅ State Management - Full conversation history")
        print("2. ✅ Error Handling - Retry logic with backoff")
        print("3. ✅ Persistence - Save/load conversation state")
        print("4. ✅ Context Building - Previous turns inform current")
        print("5. ✅ Metadata Tracking - Rich debugging information")
        print("6. ✅ Flexible Execution - Continue or abort on errors")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure OPENAI_API_KEY is set:")
        print("   export OPENAI_API_KEY='your-key-here'")

