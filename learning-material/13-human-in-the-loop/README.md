# Pattern 13: Human-in-the-Loop (HITL)

> "Pause for approval on risky actions; remember session approvals"

Codex emits approval requests, waits via oneshot channels, and records session-wide approvals. Decisions are also tagged in telemetry.

Codex references:
- `codex-rs/core/src/codex.rs` (request_command_approval, notify_approval)
- `codex-rs/core/src/executor/sandbox.rs` (approval decision → sandbox)

## Example (Python)

```python
from enum import Enum

class Decision(Enum):
    APPROVED = 1
    APPROVED_FOR_SESSION = 2
    DENIED = 3

class Approver:
    def __init__(self):
        self.session_cache = set()
    def needs_approval(self, cmd: str) -> bool:
        return cmd.startswith("rm ") and cmd not in self.session_cache
    def request(self, cmd: str) -> Decision:
        return Decision.DENIED
    def record(self, cmd: str, decision: Decision):
        if decision == Decision.APPROVED_FOR_SESSION:
            self.session_cache.add(cmd)
```
