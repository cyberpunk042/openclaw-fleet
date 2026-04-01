# Budget System — Graduated Cost Control

> **4 files. 1151 lines. Controls fleet spending through 6 budget modes with real quota monitoring.**
>
> The budget system reads REAL Claude quota via OAuth API, defines 6
> graduated budget modes (blitz $50 → blackout $0), constrains which
> models and backends agents can use, auto-transitions modes on quota
> pressure, tracks cost per mode/task/agent, and provides real-time
> cost tickers for the UI. The storm system forces budget modes during
> incidents. The router respects budget constraints for every dispatch.

### PO Requirement (Verbatim)

> "I am wondering if there is a new budgetMode (e.g. aggressive...
> whatever A, B... economic..) to inject into ocmc order to fine-tune
> the spending as speed / frequency of tasks / s and whatnot"

---

## 1. Why It Exists

Claude Code burns tokens at 10-100x the rate of chat. Without budget
control, a fleet of 10 agents can exhaust a weekly quota in hours.
The March catastrophe proved this — 15 bugs combined burned through
the entire budget.

The budget system provides:
1. **Awareness** — real quota reading from Claude OAuth API
2. **Constraints** — budget modes limit which models/backends are allowed
3. **Automation** — auto-transition to tighter modes on pressure
4. **Visibility** — cost tracking per mode, per agent, per task
5. **Override** — PO can override budget mode per order

---

## 2. How It Works

### 2.1 The 6 Budget Modes

```
┌─────────────────────────────────────────────────────────────┐
│                    BUDGET MODES                              │
│                                                              │
│  blitz    ──── $50/day │ opus + sonnet + haiku │ max effort  │
│                        │ Full power, all backends            │
│                                                              │
│  standard ──── $20/day │ opus + sonnet │ high effort          │
│                        │ Normal operation                     │
│                                                              │
│  economic ──── $10/day │ sonnet only │ medium effort           │
│                        │ No opus, automated challenges only   │
│                                                              │
│  frugal   ────  $5/day │ no Claude models │ medium effort     │
│                        │ LocalAI + OpenRouter free only       │
│                                                              │
│  survival ────  $1/day │ no Claude models │ low effort        │
│                        │ LocalAI only, no challenges          │
│                                                              │
│  blackout ────  $0/day │ no models │ low effort               │
│                        │ Fleet frozen, direct only            │
└─────────────────────────────────────────────────────────────┘
```

MODE_ORDER: blitz → standard → economic → frugal → survival → blackout

### 2.2 Real Quota Monitoring

```
BudgetMonitor._fetch_quota()
  ↓
GET https://api.anthropic.com/api/oauth/usage
Authorization: Bearer <oauth_token from ~/.claude/.credentials.json>
anthropic-beta: oauth-2025-04-20
  ↓
Response:
  five_hour.utilization: 23.5%     (session window)
  seven_day.utilization: 41.2%     (weekly all models)
  seven_day_sonnet.utilization: 35.0% (weekly sonnet)
  five_hour.resets_at: "2026-03-31T20:00:00Z"
  seven_day.resets_at: "2026-04-02T00:00:00Z"
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

### 2.3 Model Constraining

```python
constrain_model_by_budget(model="opus", effort="high",
                          reason="complex task", budget_mode="economic")
# Returns: ("sonnet", "medium", "complex task [constrained by economic: opus→sonnet]")
```

Economic mode blocks opus → falls back to sonnet.
Frugal/survival block ALL Claude models → caller routes to LocalAI.

### 2.4 Auto-Transitions

```python
evaluate_auto_transition(current_mode, quota_used_pct)

quota_used_pct:
  70%  → next tighter mode (standard → economic)
  80%  → skip to economic
  90%  → skip to frugal
  95%  → skip to survival
```

### 2.5 Cost Tracking (CostTicker)

```
CostTicker(budget_mode="standard"):
  cost_today_usd: 12.50
  cost_this_hour_usd: 3.20
  tasks_today: 8
  envelope_usd: 20.0 (from COST_ENVELOPES)
  cost_used_pct: 62.5%
  remaining_usd: 7.50
  over_budget: False

add_cost(cost_usd) → updates daily + hourly + task count
reset_daily() → zero daily counters
reset_hourly() → zero hourly counter
```

### 2.6 Per-Order Overrides

PO can override budget mode for specific orders:

```python
mgr = BudgetOverrideManager()
mgr.set_override("ORDER-42", "blitz", reason="PO: critical delivery")

effective_mode = mgr.effective_mode("ORDER-42", base_mode="economic")
# Returns "blitz" — PO override wins
```

---

## 3. File Map

```
fleet/core/
├── budget_monitor.py   Real quota via OAuth, fast climb detection  (201 lines)
├── budget_modes.py     6 modes, constraints, auto-transitions      (416 lines)
├── budget_analytics.py Per-mode metrics, mode comparison, cost/SP   (336 lines)
└── budget_ui.py        CostTicker, per-order overrides, UI payload  (198 lines)
```

Total: **1151 lines** across 4 modules.

---

## 4. Per-File Documentation

### 4.1 `budget_monitor.py` — Real Quota (201 lines)

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `QuotaReading` | 37-45 | session_pct, weekly_all_pct, weekly_sonnet_pct, reset times |
| `BudgetAlert` | 49-55 | severity, title, message, action (pause/warn/inform) |
| `BudgetMonitor` | 58-201 | OAuth quota fetching, caching, hard limits, fast climb detection, alert generation |

#### Key Methods on BudgetMonitor

| Method | Lines | What It Does |
|--------|-------|-------------|
| `_get_oauth_token()` | 69-79 | Read from ~/.claude/.credentials.json → claudeAiOauth.accessToken |
| `_fetch_quota()` | 81-120 | GET OAuth API (cached 5min). Parse five_hour, seven_day, seven_day_sonnet. Keep 50-entry history. |
| `check_quota()` | 122-153 | Hard limits: weekly≥90%→PAUSE, session≥95%→PAUSE, sonnet≥90%→PAUSE. Fast climb: +5% in 10min→PAUSE. Returns (safe, reason). |
| `get_alerts()` | 155-180 | Fire alerts at 50/70/80/90% thresholds (each fires once). |
| `format_status()` | 182-194 | One-line status: "Budget: session=23% weekly=41% sonnet=35% resets=..." |

### 4.2 `budget_modes.py` — 6 Modes (416 lines)

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `BudgetMode` | 23-41 | name, description, allowed_models, max_effort, max_dispatch, heartbeat_interval_min |

#### Constants

| Name | Type | Value |
|------|------|-------|
| `BUDGET_MODES` | dict[str, BudgetMode] | 6 modes: blitz, standard, economic, frugal, survival, blackout |
| `MODE_ORDER` | list[str] | blitz → standard → economic → frugal → survival → blackout |

#### Key Functions

| Function | Lines | What It Does |
|----------|-------|-------------|
| `get_mode(name)` | 115-116 | Get BudgetMode by name. |
| `is_model_allowed(model, budget_mode)` | 170-175 | Check if model in mode's allowed_models. |
| `constrain_model_by_budget(model, effort, reason, budget_mode)` | 178-210 | Downgrade model if not in allowed list. Cap effort to mode's max. Returns (model, effort, reason). |
| `evaluate_auto_transition(current, quota_pct)` | — | Return next tighter mode at thresholds. |

### 4.3 `budget_analytics.py` — Cost Analytics (336 lines)

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `BudgetEvent` | 28-55 | task_id, budget_mode, task_type, story_points, cost_usd, duration, backend, model, approved, challenge_passed |
| `BudgetModeMetrics` | 61-114 | Per-mode: total_tasks, total_cost, approval_rate, challenge_pass_rate, backends_used, models_used |
| `ModeComparison` | 120-159 | Compare two modes: avg_cost, approval_rate, both |
| `BudgetAnalytics` | 165-336 | Engine: record(), mode_metrics(), all_mode_metrics(), compare_modes(), cost_by_task_type(), cost_per_story_point(), summary(), format_report() |

### 4.4 `budget_ui.py` — Cost Ticker & Overrides (198 lines)

#### Constants

| Name | Value |
|------|-------|
| `COST_ENVELOPES` | blitz=$50, standard=$20, economic=$10, frugal=$5, survival=$1, blackout=$0 |

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `CostTicker` | 41-99 | Real-time: cost_today, cost_this_hour, tasks_today. Properties: envelope_usd, cost_used_pct, remaining_usd, over_budget. Methods: add_cost(), reset_daily(), reset_hourly(). |
| `BudgetOverride` | — | Per-order: order_id, mode, reason, created_at |
| `BudgetOverrideManager` | — | set_override(), remove_override(), effective_mode(). PO overrides per order. |

---

## 5. Dependency Graph

```
budget_monitor.py   ← standalone (urllib, json, no fleet imports)

budget_modes.py     ← standalone (dataclasses only)
    ↑
budget_analytics.py ← standalone (collections, dataclasses)

budget_ui.py        ← standalone (time, dataclasses)
```

All 4 modules independent. No circular dependencies.

---

## 6. Consumers (8 non-test)

| Layer | Module | What It Imports | How It Uses It |
|-------|--------|----------------|---------------|
| **Orchestrator** | `orchestrator.py` | `BudgetMonitor` | check_quota() before dispatch. Format status for logging. |
| **Backend Router** | `backend_router.py` | `BUDGET_MODES, get_mode` | Route by budget mode — constrain backends/models. |
| **Model Selection** | `model_selection.py` | `constrain_model_by_budget` | Downgrade model selection per budget constraints. |
| **Challenge Deferred** | `challenge_deferred.py` | `MODE_ORDER` | W1 wiring: challenge depth by mode using shared ordering. |
| **Storm Integration** | `storm_integration.py` | `MODE_ORDER` | W3 wiring: storm forces budget mode, validates against ordering. |
| **Budget CLI** | `budget.py` | All budget_modes functions | CLI commands for budget management. |
| **Dispatch CLI** | `dispatch.py` | `get_active_mode_name` | Include budget mode in dispatch context. |
| **Sync CLI** | `sync.py` | `BudgetMonitor` | Budget check during sync cycle. |

---

## 7. Design Decisions

### Why 6 modes, not 3 or 10?

6 modes map to clear operational states:
- **blitz**: deadline crunch, spend freely
- **standard**: normal operation
- **economic**: budget tightening, reduce quality slightly
- **frugal**: free backends only
- **survival**: absolute minimum
- **blackout**: emergency stop

3 modes would lack the gradual degradation. 10 modes would add
confusion without value. 6 gives clear steps from "full power"
to "zero cost."

### Why real OAuth API, not estimates?

Estimates are wrong. The March catastrophe showed that estimated
cost can be 10-20x off due to prompt cache bugs. Real quota from
the OAuth API shows actual usage as Claude sees it — the only
number that matters for weekly limits.

### Why cache quota for 5 minutes?

The OAuth API is rate-limited. Calling every 30-second cycle would
hit limits. 5-minute caching balances freshness with rate-limit
protection. Fast climb detection works because the comparison is
between cached readings (same interval).

### Why auto-transitions at 70/80/90/95%?

70% = early warning (standard → economic). 80% = tightening. 90% = 
serious (→ frugal). 95% = critical (→ survival). These thresholds
give the fleet time to react progressively rather than hitting a
hard wall at 100%.

### Why per-order overrides?

The PO might need one critical task at blitz while the fleet is
in economic mode. Per-order overrides let the PO say "this specific
order gets full power" without changing the fleet-wide mode.

---

## 8. Budget → Everything Flow

```
OAuth API → BudgetMonitor.check_quota()
  ↓
Orchestrator pre-check: safe_to_dispatch?
  ├── No → skip dispatch, log reason
  └── Yes → continue
  ↓
Budget mode constrains:
  ├── Backend Router: which backends allowed?
  ├── Model Selection: which models allowed?
  ├── Challenge Engine: which challenge depth?
  └── Effort Profile: max effort level?
  ↓
Each tool call → CostTicker.add_cost()
  ↓
Cost tracked per mode → BudgetAnalytics
  ↓
Storm forces budget mode if severity WARNING+
  ↓
Auto-transition if quota crosses threshold
```

---

## 9. Data Shapes

### QuotaReading

```python
QuotaReading(
    timestamp=datetime(2026, 3, 31, 15, 42),
    session_pct=23.5,
    weekly_all_pct=41.2,
    weekly_sonnet_pct=35.0,
    session_resets_at="2026-03-31T20:00:00Z",
    weekly_resets_at="2026-04-02T00:00:00Z",
)
```

### BudgetMode

```python
BudgetMode(
    name="economic",
    description="Budget-conscious — sonnet only",
    allowed_models=["sonnet"],
    max_effort="medium",
    max_dispatch=2,
    heartbeat_interval_min=60,
)
```

### CostTicker

```python
CostTicker(
    budget_mode="standard",
    cost_today_usd=12.50,
    cost_this_hour_usd=3.20,
    tasks_today=8,
    # envelope_usd = 20.0
    # cost_used_pct = 62.5%
    # remaining_usd = 7.50
    # over_budget = False
)
```

---

## 10. What's Needed

### Integration Gaps

- **Session telemetry feeding real cost** — W8 adapter built,
  `to_cost_delta()` provides real cost, but not wired to
  CostTicker.add_cost() in runtime
- **Budget mode in FleetControlBar** — TSX patch exists (M-BM05)
  but not deployed to OCMC UI
- **Prompt caching** — 90% savings available, not enabled
- **Batch API** — 50% savings for async work, not used

### Cost Optimization Potential

| Mechanism | Savings | Status |
|-----------|---------|--------|
| Silent heartbeats | ~70% idle agents | NOT BUILT |
| Prompt caching | ~90% cached input | NOT ENABLED |
| LocalAI routing | ~100% simple tasks | NOT CONNECTED |
| Batch API | ~50% async work | NOT USED |
| Real quota monitoring | prevents overrun | IMPLEMENTED ✓ |
| Auto-transitions | graduated degradation | IMPLEMENTED ✓ |

### Test Coverage

| File | Tests | Coverage |
|------|-------|---------|
| `test_budget_modes.py` | 47 | All 6 modes, constraints, transitions |
| `test_budget_ui.py` | 24 | CostTicker, overrides, payload |
| `test_budget_analytics.py` | 22 | Events, metrics, comparisons |
| `test_budget_monitor.py` | 10+ | Quota checking, alerts |
| **Total** | **103** | Core logic fully covered |
