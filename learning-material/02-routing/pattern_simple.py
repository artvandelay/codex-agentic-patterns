#!/usr/bin/env python3
"""
Pattern 2: Routing - Simple Example

Demonstrates basic intent classification and routing to different handlers.

Inspired by: codex-rs/core/src/tools/router.rs
"""

import os
import re
from typing import Callable, Dict
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def classify_intent(user_query: str) -> str:
    """
    Use LLM to classify user intent.
    
    Similar to how Codex router classifies tool calls.
    """
    classification_prompt = f"""
    Classify the user's intent into ONE of these categories:
    - search: User wants to search for information
    - calculate: User wants to perform a calculation
    - generate: User wants to generate content (code, text, etc.)
    - analyze: User wants to analyze or understand something
    - other: Doesn't fit above categories
    
    User query: "{user_query}"
    
    Respond with ONLY the category name, nothing else.
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": classification_prompt}],
        temperature=0,
    )
    
    return response.choices[0].message.content.strip().lower()


# Define handlers for each intent type
def handle_search(query: str) -> str:
    """Handler for search intent."""
    print(f"  📡 SEARCH Handler activated")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"Search for and summarize information about: {query}"
        }],
    )
    return response.choices[0].message.content


def handle_calculate(query: str) -> str:
    """Handler for calculation intent."""
    print(f"  🔢 CALCULATE Handler activated")
    
    # Extract numbers and operations
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"Perform this calculation and show your work: {query}"
        }],
    )
    return response.choices[0].message.content


def handle_generate(query: str) -> str:
    """Handler for generation intent."""
    print(f"  ✍️  GENERATE Handler activated")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user", 
            "content": f"Generate the following: {query}"
        }],
    )
    return response.choices[0].message.content


def handle_analyze(query: str) -> str:
    """Handler for analysis intent."""
    print(f"  🔍 ANALYZE Handler activated")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"Analyze and explain: {query}"
        }],
    )
    return response.choices[0].message.content


def handle_other(query: str) -> str:
    """Default handler for uncategorized intents."""
    print(f"  ❓ OTHER Handler activated (default)")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": query}],
    )
    return response.choices[0].message.content


# Router - maps intents to handlers
INTENT_HANDLERS: Dict[str, Callable[[str], str]] = {
    "search": handle_search,
    "calculate": handle_calculate,
    "generate": handle_generate,
    "analyze": handle_analyze,
    "other": handle_other,
}


def route_and_execute(user_query: str) -> str:
    """
    Main routing function.
    
    1. Classify the intent
    2. Route to appropriate handler
    3. Execute and return result
    """
    print(f"\n{'=' * 60}")
    print(f"ROUTING: {user_query}")
    print(f"{'=' * 60}")
    
    # Step 1: Classify
    print(f"\n🔀 Classifying intent...")
    intent = classify_intent(user_query)
    print(f"  ✅ Intent: {intent.upper()}")
    
    # Step 2: Route to handler
    print(f"\n🎯 Routing to handler...")
    handler = INTENT_HANDLERS.get(intent, handle_other)
    
    # Step 3: Execute
    print(f"\n⚡ Executing handler...")
    result = handler(user_query)
    
    print(f"\n✅ Result: {result[:200]}...")
    
    return result


def demo_routing():
    """Demonstrate routing with various query types."""
    
    test_queries = [
        "What is the capital of France?",  # search
        "Calculate 15% of $2,500",  # calculate
        "Write a Python function to reverse a string",  # generate
        "Explain how photosynthesis works",  # analyze
        "Hello, how are you?",  # other
    ]
    
    print("🚀 Simple Routing Pattern Demo")
    print("=" * 60)
    
    results = {}
    for query in test_queries:
        result = route_and_execute(query)
        results[query] = result
        print("\n" + "-" * 60 + "\n")
    
    return results


def keyword_based_routing_example():
    """
    Alternative: Simple keyword-based routing (no LLM classification).
    Faster but less flexible.
    """
    print("\n\n" + "=" * 60)
    print("BONUS: KEYWORD-BASED ROUTING")
    print("=" * 60)
    
    def classify_by_keywords(query: str) -> str:
        """Simple keyword-based classification."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["search", "find", "what is", "who is"]):
            return "search"
        elif any(word in query_lower for word in ["calculate", "compute", "sum", "multiply"]):
            return "calculate"
        elif any(word in query_lower for word in ["generate", "create", "write", "make"]):
            return "generate"
        elif any(word in query_lower for word in ["analyze", "explain", "why", "how"]):
            return "analyze"
        else:
            return "other"
    
    queries = [
        "What is machine learning?",
        "Calculate the area of a circle with radius 5",
        "Write a haiku about coding",
    ]
    
    for query in queries:
        intent = classify_by_keywords(query)
        handler = INTENT_HANDLERS[intent]
        print(f"\nQuery: {query}")
        print(f"Intent: {intent} → Handler: {handler.__name__}")


if __name__ == "__main__":
    try:
        # Run main demo
        demo_routing()
        
        # Show keyword-based alternative
        keyword_based_routing_example()
        
        print("\n\n💡 Key Lessons:")
        print("1. Classification determines execution path")
        print("2. Handlers specialize in specific intent types")
        print("3. Router maps intents to handlers dynamically")
        print("4. Adding new intents is as simple as adding a handler")
        print("5. Fallback handler ensures robustness")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure OPENAI_API_KEY is set:")
        print("   export OPENAI_API_KEY='your-key-here'")

