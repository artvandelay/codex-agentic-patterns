#!/usr/bin/env python3
"""
Pattern 1: Prompt Chaining - Simple Example

This demonstrates the basic concept of prompt chaining where the output
of one LLM call becomes the input to the next.

Inspired by: codex-rs/core/src/codex.rs (turn-based conversation loop)
"""

import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def call_llm(prompt: str, model: str = "gpt-4") -> str:
    """Simple LLM call wrapper."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content


def simple_chain_example():
    """
    Demonstrates a basic 3-step chain:
    1. Extract key info from text
    2. Analyze the extracted info
    3. Generate recommendations
    """
    print("=" * 60)
    print("SIMPLE PROMPT CHAIN EXAMPLE")
    print("=" * 60)

    # Sample input
    input_text = """
    Our Q4 sales report shows revenue increased by 15% compared to Q3,
    reaching $2.5M. However, customer acquisition cost (CAC) rose by 20%,
    and customer satisfaction scores dropped from 4.2 to 3.8 out of 5.
    The marketing team spent $500K on campaigns, up from $300K in Q3.
    """

    print("\n📄 Input Text:")
    print(input_text)

    # Step 1: Extract structured data
    print("\n" + "─" * 60)
    print("🔗 STEP 1: Extract Key Metrics")
    print("─" * 60)

    step1_prompt = f"""
    Extract the key business metrics from this text in a structured format:
    
    {input_text}
    
    Format as:
    - Metric: Value
    """

    step1_output = call_llm(step1_prompt)
    print(f"\n✅ Step 1 Output:\n{step1_output}")

    # Step 2: Analyze using previous output
    print("\n" + "─" * 60)
    print("🔗 STEP 2: Analyze Trends")
    print("─" * 60)

    step2_prompt = f"""
    Based on these extracted metrics, identify concerning trends:
    
    {step1_output}
    
    Focus on metrics moving in opposite directions or problematic patterns.
    """

    step2_output = call_llm(step2_prompt)
    print(f"\n✅ Step 2 Output:\n{step2_output}")

    # Step 3: Generate recommendations using all previous context
    print("\n" + "─" * 60)
    print("🔗 STEP 3: Generate Recommendations")
    print("─" * 60)

    step3_prompt = f"""
    Given this analysis of business trends:
    
    {step2_output}
    
    Provide 3 specific, actionable recommendations to address the concerns.
    """

    step3_output = call_llm(step3_prompt)
    print(f"\n✅ Step 3 Output:\n{step3_output}")

    print("\n" + "=" * 60)
    print("✨ CHAIN COMPLETE")
    print("=" * 60)

    return {
        "step1": step1_output,
        "step2": step2_output,
        "step3": step3_output,
    }


def coding_task_chain_example():
    """
    Example: Multi-step code review and improvement
    Similar to how Codex handles code-related tasks
    """
    print("\n\n" + "=" * 60)
    print("CODING TASK CHAIN EXAMPLE")
    print("=" * 60)

    code_snippet = """
def calculate_total(items):
    total = 0
    for i in items:
        total = total + i['price'] * i['quantity']
    return total
"""

    print(f"\n📝 Code to Review:\n{code_snippet}")

    # Step 1: Understand the code
    print("\n" + "─" * 60)
    print("🔗 STEP 1: Code Understanding")
    print("─" * 60)

    understand_prompt = f"""
    Analyze this code and explain what it does:
    
    {code_snippet}
    
    Be concise and factual.
    """

    understanding = call_llm(understand_prompt)
    print(f"\n✅ Understanding:\n{understanding}")

    # Step 2: Identify issues
    print("\n" + "─" * 60)
    print("🔗 STEP 2: Identify Issues")
    print("─" * 60)

    issues_prompt = f"""
    Based on this code and understanding:
    
    Code:
    {code_snippet}
    
    Understanding:
    {understanding}
    
    Identify potential issues, edge cases, or improvements needed.
    """

    issues = call_llm(issues_prompt)
    print(f"\n✅ Issues Found:\n{issues}")

    # Step 3: Generate improved version
    print("\n" + "─" * 60)
    print("🔗 STEP 3: Generate Improved Code")
    print("─" * 60)

    improve_prompt = f"""
    Given these identified issues:
    
    {issues}
    
    Rewrite the original code to address them. Provide only the improved code.
    
    Original code:
    {code_snippet}
    """

    improved_code = call_llm(improve_prompt)
    print(f"\n✅ Improved Code:\n{improved_code}")

    print("\n" + "=" * 60)
    print("✨ CODE IMPROVEMENT CHAIN COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    try:
        # Run both examples
        simple_chain_example()
        coding_task_chain_example()

        print("\n\n💡 Key Lessons:")
        print("1. Each step focuses on ONE specific task")
        print("2. Output of step N becomes input to step N+1")
        print("3. Context accumulates through the chain")
        print("4. Errors are easier to debug (know which step failed)")
        print("5. Steps can be modified independently")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure OPENAI_API_KEY is set:")
        print("   export OPENAI_API_KEY='your-key-here'")
