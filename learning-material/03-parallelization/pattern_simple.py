#!/usr/bin/env python3
"""
Pattern 3: Parallelization - Simple Example

Demonstrates concurrent execution of independent tasks using asyncio.

Inspired by: codex-rs/core/src/tools/parallel.rs
"""

import asyncio
import time
from typing import List, Dict, Any


# Simulated slow operations
async def read_file(filename: str) -> str:
    """Simulate reading a file (slow I/O operation)."""
    print(f"  📖 Reading {filename}...")
    await asyncio.sleep(0.5)  # Simulate I/O delay
    return f"Contents of {filename}"


async def fetch_api(url: str) -> str:
    """Simulate API call (slow network operation)."""
    print(f"  🌐 Fetching {url}...")
    await asyncio.sleep(0.7)  # Simulate network delay
    return f"Data from {url}"


async def process_data(data: str) -> str:
    """Simulate CPU-intensive processing."""
    print(f"  ⚙️  Processing data...")
    await asyncio.sleep(0.3)  # Simulate processing
    return f"Processed: {data}"


# ============================================================================
# Sequential vs Parallel Comparison
# ============================================================================

async def sequential_execution():
    """Execute tasks one after another (slow)."""
    print("\n" + "=" * 60)
    print("SEQUENTIAL EXECUTION")
    print("=" * 60)
    
    start_time = time.time()
    
    # Execute one at a time
    result1 = await read_file("file1.txt")
    result2 = await read_file("file2.txt")
    result3 = await read_file("file3.txt")
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ Completed in {elapsed:.2f}s")
    print(f"   Results: {len([result1, result2, result3])} files read")
    
    return elapsed


async def parallel_execution():
    """Execute tasks concurrently (fast)."""
    print("\n" + "=" * 60)
    print("PARALLEL EXECUTION")
    print("=" * 60)
    
    start_time = time.time()
    
    # Launch all tasks concurrently
    tasks = [
        read_file("file1.txt"),
        read_file("file2.txt"),
        read_file("file3.txt"),
    ]
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ Completed in {elapsed:.2f}s")
    print(f"   Results: {len(results)} files read")
    
    return elapsed


# ============================================================================
# Parallel with Error Handling
# ============================================================================

async def flaky_operation(task_id: int, should_fail: bool = False) -> str:
    """Simulates an operation that might fail."""
    print(f"  🎲 Task {task_id} starting...")
    await asyncio.sleep(0.3)
    
    if should_fail:
        raise ValueError(f"Task {task_id} failed!")
    
    return f"Task {task_id} completed"


async def parallel_with_error_handling():
    """Demonstrate error handling in parallel execution."""
    print("\n" + "=" * 60)
    print("PARALLEL EXECUTION WITH ERROR HANDLING")
    print("=" * 60)
    
    tasks = [
        flaky_operation(1, should_fail=False),
        flaky_operation(2, should_fail=True),   # This will fail
        flaky_operation(3, should_fail=False),
    ]
    
    # gather with return_exceptions=True continues despite failures
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print("\n📊 Results:")
    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print(f"  ❌ Task {i}: Error - {result}")
        else:
            print(f"  ✅ Task {i}: {result}")


# ============================================================================
# Smart Parallelization (Codex-style)
# ============================================================================

class ToolExecutor:
    """
    Executor that intelligently decides what can run in parallel.
    Inspired by: codex-rs/core/src/tools/parallel.rs
    """
    
    # Define which tools support parallel execution
    PARALLEL_TOOLS = {"read_file", "fetch_api"}
    SERIAL_TOOLS = {"write_file", "execute_command"}
    
    def __init__(self):
        self.pending_parallel_tasks = []
    
    async def execute_tools(self, tool_calls: List[Dict[str, Any]]) -> List[str]:
        """
        Execute a list of tool calls, parallelizing when possible.
        
        Similar to: ToolCallRuntime::handle_tool_call in Codex
        """
        print("\n" + "=" * 60)
        print("SMART PARALLEL EXECUTION (Codex-style)")
        print("=" * 60)
        
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            args = tool_call["args"]
            
            if tool_name in self.PARALLEL_TOOLS:
                # Can run in parallel - spawn task
                print(f"\n🚀 Spawning parallel: {tool_name}({args})")
                task = self._execute_tool(tool_name, args)
                self.pending_parallel_tasks.append(task)
                
            elif tool_name in self.SERIAL_TOOLS:
                # Must run serially - wait for pending tasks first
                print(f"\n⏸️  Serial tool detected: {tool_name}")
                print(f"   Waiting for {len(self.pending_parallel_tasks)} pending tasks...")
                
                # Resolve all pending parallel tasks
                if self.pending_parallel_tasks:
                    parallel_results = await asyncio.gather(*self.pending_parallel_tasks)
                    results.extend(parallel_results)
                    self.pending_parallel_tasks = []
                
                # Now execute the serial tool
                print(f"   Executing serial: {tool_name}({args})")
                result = await self._execute_tool(tool_name, args)
                results.append(result)
        
        # Resolve any remaining parallel tasks
        if self.pending_parallel_tasks:
            print(f"\n⏳ Resolving {len(self.pending_parallel_tasks)} remaining parallel tasks...")
            parallel_results = await asyncio.gather(*self.pending_parallel_tasks)
            results.extend(parallel_results)
        
        return results
    
    async def _execute_tool(self, tool_name: str, args: str) -> str:
        """Execute a single tool."""
        if tool_name == "read_file":
            return await read_file(args)
        elif tool_name == "fetch_api":
            return await fetch_api(args)
        elif tool_name == "write_file":
            await asyncio.sleep(0.5)  # Simulate write
            return f"Wrote to {args}"
        elif tool_name == "execute_command":
            await asyncio.sleep(0.4)  # Simulate command
            return f"Executed {args}"
        else:
            return f"Unknown tool: {tool_name}"


async def demo_smart_parallelization():
    """Demonstrate intelligent parallelization like Codex."""
    executor = ToolExecutor()
    
    tool_calls = [
        {"name": "read_file", "args": "config.json"},      # Parallel
        {"name": "read_file", "args": "data.csv"},         # Parallel
        {"name": "fetch_api", "args": "https://api.com"},  # Parallel
        {"name": "execute_command", "args": "ls -la"},     # Serial - triggers wait
        {"name": "read_file", "args": "output.txt"},       # Parallel again
    ]
    
    start_time = time.time()
    results = await executor.execute_tools(tool_calls)
    elapsed = time.time() - start_time
    
    print(f"\n✅ All tools executed in {elapsed:.2f}s")
    print(f"   Total results: {len(results)}")


# ============================================================================
# Main Demo
# ============================================================================

async def main():
    """Run all demonstrations."""
    print("🚀 Parallelization Pattern Demo\n")
    
    # Demo 1: Compare sequential vs parallel
    seq_time = await sequential_execution()
    par_time = await parallel_execution()
    
    speedup = seq_time / par_time
    print(f"\n⚡ Speedup: {speedup:.2f}x faster with parallelization!")
    
    # Demo 2: Error handling
    await parallel_with_error_handling()
    
    # Demo 3: Smart parallelization (Codex-style)
    await demo_smart_parallelization()
    
    print("\n\n💡 Key Lessons:")
    print("1. ✅ Parallel execution is much faster for independent tasks")
    print("2. ✅ Use asyncio.gather() to run tasks concurrently")
    print("3. ✅ Handle errors gracefully with return_exceptions=True")
    print("4. ✅ Serial tools must wait for parallel tasks to complete")
    print("5. ✅ Not all operations can safely run in parallel")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")

