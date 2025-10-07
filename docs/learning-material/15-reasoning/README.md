# Pattern 17: Reasoning Techniques

> "Surface summaries vs raw reasoning traces based on user settings"

Codex accumulates reasoning deltas but conditionally forwards raw content; summaries are streamed as deltas with optional section breaks.

Codex references:
- `codex-rs/core/src/chat_completions.rs` (AggregatedChatStream deltas for reasoning)
- `codex-rs/core/src/codex.rs` (AgentReasoningDelta vs AgentReasoningRawContentDelta)

## Example (Python)

```python
class ReasoningSwitch:
    def __init__(self, show_raw=False):
        self.show_raw = show_raw
    def emit(self, summary_delta: str=None, raw_delta: str=None):
        if raw_delta and self.show_raw:
            print(f"RAW: {raw_delta}")
        if summary_delta:
            print(f"SUMMARY: {summary_delta}")
```
