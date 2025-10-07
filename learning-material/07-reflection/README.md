# Pattern 07: Reflection / Review Mode

> "Branch to an isolated thread to critique or review without polluting the main conversation"

Codex spawns review threads: isolated in-memory histories seeded with environment context; UI deltas are suppressed; final review emits a summary.

Codex references:
- `codex-rs/core/src/codex.rs` (spawn_review_thread, is_review_mode)

## Example (Python)

```python
class Conversation:
    def __init__(self):
        self.main: list[str] = []
        self.review: list[str] = []
        self.in_review = False
    
    def add(self, msg: str):
        (self.review if self.in_review else self.main).append(msg)
    
    def start_review(self):
        self.in_review = True
        self.review = ["[env] cwd=/project"]
    
    def end_review(self) -> str:
        self.in_review = False
        return "\n".join(self.review)
```
