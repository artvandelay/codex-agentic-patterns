# Pattern 06: Planning

> "Keep a short, verifiable plan and update it as you execute"

Codex surfaces a lightweight plan tool (`update_plan`) and renders progress. Plans are concise, ordered steps; the agent updates status as work proceeds.

Codex references:
- `codex-rs/core/prompt.md` (Planning guidance)
- `codex-rs/core/src/codex.rs` (plan/tool events)

## Example (Python)

```python
from dataclasses import dataclass, field
from enum import Enum

class StepStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"

@dataclass
class Plan:
    steps: list[tuple[str, StepStatus]] = field(default_factory=list)
    
    def add(self, text: str):
        self.steps.append((text, StepStatus.PENDING))
    
    def start(self, idx: int):
        text, _ = self.steps[idx]
        self.steps[idx] = (text, StepStatus.IN_PROGRESS)
    
    def done(self, idx: int):
        text, _ = self.steps[idx]
        self.steps[idx] = (text, StepStatus.DONE)

# Demo
plan = Plan()
plan.add("Read requirements")
plan.add("Create design")
plan.start(0)
plan.done(0)
plan.start(1)
print(plan)
```
