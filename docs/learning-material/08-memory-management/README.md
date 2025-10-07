# Pattern 08: Memory Management

> "Maintain a clean, append-only conversation history with turn-aware compaction"

Codex stores `ResponseItem`s and compacts at logical boundaries while preserving the last assistant/user messages for context.

Codex references:
- `codex-rs/core/src/conversation_history.rs`
- `codex-rs/core/src/codex/compact.rs`

## Example (Python)

```python
class Memory:
    def __init__(self, max_len=50):
        self.items: list[dict] = []
        self.max_len = max_len
    
    def add(self, role: str, content: str):
        self.items.append({"role": role, "content": content})
        if len(self.items) > self.max_len:
            self.items = self.items[-self.max_len:]
    
    def compact(self):
        # Keep last user + last assistant; drop older filler
        keep = []
        last_user = next((i for i in reversed(self.items) if i["role"]=="user"), None)
        last_asst = next((i for i in reversed(self.items) if i["role"]=="assistant"), None)
        if last_user: keep.append(last_user)
        if last_asst: keep.append(last_asst)
        self.items = sorted(set(map(tuple, map(dict.items, keep))))
```
