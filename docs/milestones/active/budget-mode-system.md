# Budget Mode System for OCMC Orders

## Severity: STRATEGIC
## Status: DESIGN
## Created: 2026-03-31

A budget mode system injected into OCMC orders that controls the **tempo**
(speed and frequency) of fleet operations. Budget mode is a tempo setting
only — it does NOT control models, backends, challenge depth, or routing.

Separate systems handle those concerns:
- **backend_mode** (7 combos of Claude/LocalAI/OpenRouter) controls backends
- **Storm system** controls dispatch limits and alerts
- **Model selection** controls which models are used

---

## Part 1: PO Requirements (Verbatim)

> "I am wondering if there is a new budgetMode (e.g. aggressive... whatever
> A, B... economic..) to inject into ocmc order to fine-tune the spending
> as speed / frequency of tasks / s and whatnot. The use of free open
> claude models..."

> "I know some endpoint are route through a loadbalancer of free models
> with autorouting to the one available to the level you want if its not
> too busy."

> "we need to evolve and make things observable and clean and scalable."

---

## Part 2: Current State vs. What's Needed

### What Exists Today

| Component | What It Does | Limitation |
|-----------|-------------|------------|
| `budget_modes.py` | Fleet tempo setting (speed/frequency) | Mode definitions TBD |
| `budget_monitor.py` | Reads Claude quota %, fast-climb detection | Reactive — detects problems, doesn't prevent them |
| Orchestrator | Checks `budget_monitor.check_quota()` before dispatch | Binary: safe or pause. No gradations. |

### What's Missing

1. **Per-order budget mode** — each OCMC order should carry a tempo strategy
2. **Graduated tempo** — not just "go" or "stop" but levels of intensity
3. **Budget mode in OCMC order schema** — first-class field, not afterthought

---

## Part 3: Budget Mode Design

### The Modes

Budget mode controls **tempo only** — speed and frequency of fleet operations.

| Mode | Speed | Max Dispatch/Cycle | Heartbeat Interval | Use When |
|------|-------|-------------------|-------------------|----------|
| **turbo** | Maximum | 5 | 15m | Sprint deadline, critical bugs, time-sensitive |
| **standard** | Normal | 2 | 30m | Normal operation, balanced cost/speed |
| **economic** | Moderate | 1 | 60m | Budget-conscious, steady work |

### Mode Inheritance

```
PO sets global mode → fleet.yaml / fleet effort <mode>
   ↓
OCMC order can override → order.budget_mode = "economic"
   ↓
Task inherits order mode unless overridden → task.custom_fields.budget_mode
   ↓
Brain respects the most restrictive mode in the chain
```

### Mode Schema (OCMC Order)

```yaml
# In OCMC order / MC task creation:
budget_mode: "standard"        # Required — controls fleet tempo
```

---

## Part 4: Fleet Control Settings

Fleet control uses independent settings:
- **work_mode** — dispatch gating (pause/resume/finish-current)
- **backend_mode** — which backends enabled (7 combos)
- **budget_mode** — fleet tempo (speed/frequency)

---

## Part 5: OCMC Order Schema Update

```python
@dataclass
class OrderBudgetConfig:
    """Budget configuration for an OCMC order."""

    mode: str = "standard"               # turbo/standard/economic
    max_iterations: int = 3              # Max retry attempts before human escalation
```

This config is:
- Set by PO when creating orders (or defaults from fleet.yaml)
- Readable by the brain at dispatch time

---

## Part 6: Milestones

### M-BM01: BudgetMode Data Model
- Define `BudgetMode` enum with turbo/standard/economic
- Define `OrderBudgetConfig` dataclass
- Add budget_mode field to OCMC order schema
- Add to task custom fields
- Tests for mode constraints
- **Status:** ⏳ PENDING

### M-BM02: Budget Mode in Fleet CLI
- `fleet budget` — show current mode
- `fleet budget set <mode>` — set global mode
- `fleet budget order <order-id> <mode>` — set per-order mode
- **Status:** ⏳ PENDING

### M-BM03: Budget Mode in OCMC UI
- Display current budget mode in MC header bar (control surface)
- Mode selector dropdown with descriptions
- Per-order budget mode override
- **Status:** ⏳ PENDING

### M-BM04: Budget Analytics
- Track tempo per mode over time
- Feed into PO decision-making about when to use which mode
- Cross-ref: labor stamps provide the data
- **Status:** ⏳ PENDING

---

## Part 7: Cross-References

| Related Milestone | Relationship |
|-------------------|-------------|
| Labor Attribution | Labor stamps provide per-task data |
| Storm Prevention | Storm system controls dispatch and alerts independently |
| Fleet Control | work_mode controls dispatch gating; budget_mode controls tempo |
| Fleet Elevation Doc 23 | Agent lifecycle sleep/wake managed by brain |

---

## Part 8: Why This Matters

Budget mode gives the PO a simple lever to control fleet tempo:
- **turbo** for sprints and urgent work
- **standard** for normal operation
- **economic** for steady, cost-conscious work

The PO sets the strategy. The brain executes it at the specified tempo.

> "reduce the efforts and strategy like that strategic and driven by the
> user and circumstances" — this is exactly what budget modes deliver.