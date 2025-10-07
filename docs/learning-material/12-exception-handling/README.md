# Pattern 12: Exception Handling & Recovery

> "Detect transient vs fatal errors; retry with backoff; inform the user"

Codex retries stream turns with provider-specific budgets and backoff, notifying the UI while waiting.

Codex references:
- `codex-rs/core/src/codex.rs` (try_run_turn retries, notify_stream_error)

## Example (Python)

```python
import time

def backoff(attempt):
    return min(2 ** attempt, 30)

def run_with_retry(fn, max_retries=3):
    for i in range(max_retries):
        try:
            return fn()
        except Exception as e:
            if i == max_retries - 1:
                raise
            delay = backoff(i+1)
            print(f"stream error: {e}; retrying {i+1}/{max_retries} in {delay}s…")
            time.sleep(delay)
```
