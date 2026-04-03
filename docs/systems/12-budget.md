# Budget System — Fleet Tempo & Quota Monitoring

> Budget mode controls fleet TEMPO (how fast/frequent/hard agents work).
> Real quota monitoring via Claude OAuth API prevents overruns.
> Backend selection is a SEPARATE setting (backend_mode in FleetControlState).

### PO Requirement (Verbatim)

> "I am wondering if there is a new budgetMode (e.g. aggressive...
> whatever A, B... economic..) to inject into ocmc order to fine-tune
> the spending as speed / frequency of tasks / s and whatnot"

---

## 1. What Budget Mode IS

Budget mode is a **tempo setting** — it controls the pace of the fleet:
- Orchestrator cycle speed
- Heartbeat frequency
- Consequence: operations per minute

It is an **offset** applied to base config values in fleet.yaml.
PO examples: "aggressive" (faster tempo), "economic" (slower pace).

Budget mode does **NOT** control:
- Which models are allowed (that's model_selection.py)
- Which backends are enabled (that's backend_mode in fleet_mode.py)
- Challenge depth (that's the challenge system)
- Dollar amounts (there are no cost envelopes)

---

## 2. What Exists Today

### 2.1 Real Quota Monitoring (budget_monitor.py)

```
BudgetMonitor._fetch_quota()
  ↓
GET https://api.anthropic.com/api/oauth/usage
Authorization: Bearer <oauth_token from ~/.claude/.credentials.json>
  ↓
Response:
  five_hour.utilization: 23.5%     (session window)
  seven_day.utilization: 41.2%     (weekly all models)
  seven_day_sonnet.utilization: 35.0% (weekly sonnet)
  five_hour.resets_at: "2026-03-31T20:00:00Z"
  ↓
Cache for 5 minutes (rate limit protection)
  ↓
check_quota() → (safe_to_dispatch: bool, reason: str)
  Hard limits:
    weekly_all ≥ 90%   → PAUSE
    session ≥ 95%       → PAUSE (wait for reset)
    weekly_sonnet ≥ 90% → PAUSE
  Fast climb:
    +5% in 10 min       → PAUSE
```

### 2.2 Budget Mode (budget_modes.py)

Fleet tempo setting. Mode definitions are **TBD — waiting for PO input**.

```python
@dataclass
class BudgetMode:
    name: str
    description: str
    tempo_multiplier: float  # Applied to orchestrator/heartbeat intervals
```

Current config: `budget_mode: turbo` (fleet.yaml)

### 2.3 Per-Order Overrides (budget_ui.py)

PO can override budget mode for specific orders:

```python
mgr = BudgetOverrideManager()
mgr.set_override("ORDER-42", "turbo", reason="PO: critical delivery")
effective = mgr.effective_mode("ORDER-42", base_mode="standard")
# Returns "turbo"
```

### 2.4 Budget Analytics (budget_analytics.py)

Tracks cost per task type, story points, agent, backend.

---

## 3. File Map

```
fleet/core/
├── budget_monitor.py   Real quota via OAuth, fast climb detection
├── budget_modes.py     Tempo setting (TBD mode definitions)
├── budget_analytics.py Per-task cost tracking and metrics
└── budget_ui.py        Per-order overrides, UI payload
```

---

## 4. Separate Concerns

| Setting | File | What It Controls |
|---------|------|-----------------|
| budget_mode | budget_modes.py | Fleet tempo (speed/frequency) |
| backend_mode | fleet_mode.py | Which backends enabled (7 combos) |
| work_mode | fleet_mode.py | Which agents active, dispatch gating |
| model selection | model_selection.py | opus vs sonnet by task complexity |

These are independent settings. They do NOT override each other.

---

## 5. Cost Optimization Potential

| Mechanism | Savings | Status |
|-----------|---------|--------|
| Silent heartbeats | ~70% idle agents | NOT BUILT |
| Prompt caching | ~90% cached input | NOT ENABLED |
| LocalAI routing | ~100% simple tasks | NOT CONNECTED |
| Batch API | ~50% async work | NOT USED |
| Real quota monitoring | prevents overrun | IMPLEMENTED ✓ |
