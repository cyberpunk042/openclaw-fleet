# Multi-Backend Router — Cheapest Capable Backend Wins

> **5 files. 1611 lines. Routes tasks to the cheapest backend that can handle them.**
>
> The router decides which backend processes each task: Claude (paid,
> expert), LocalAI (free, trainee), OpenRouter free (free, community),
> or direct (no LLM, deterministic). Budget mode constrains the options.
> Health dashboard tracks backend availability. Circuit breakers trigger
> fallback on failure. Model swap manages LocalAI's single-active-backend
> limitation. Codex review triggers adversarial review by tier.

### PO Requirement (Verbatim)

> "Just like we want to use methodologies and skills — Not an always in,
> more like a use case strategy logic decision."

---

## 1. Why It Exists

Without routing, every task goes to Claude regardless of complexity.
A simple heartbeat check consuming opus tokens is waste. A structured
JSON response from a 3B model is free. The router matches task
complexity to backend capability, budget mode to allowed models,
and health state to availability — then picks the cheapest option
that works.

---

## 2. How It Works

### 2.1 Routing Decision Flow

```
Task arrives with budget_mode
  ↓
Assess complexity: simple / medium / complex / critical
  ↓
backend_mode (from FleetControlState) determines enabled backends:
  7 possible combos of Claude / LocalAI / OpenRouter
  ↓
Route by complexity + enabled backends:
  Cheapest capable enabled backend wins
  Security/architecture agents never go to free/trainee
  ↓
Health check (W5 wiring):
  Backend DOWN? → execute_fallback()
  No fallback?  → queue task
  ↓
Circuit breaker check (storm integration):
  Breaker OPEN? → execute_fallback()
  Primary + fallback OPEN? → queue task
  ↓
Return RoutingDecision:
  backend, model, effort, reason, confidence_tier,
  fallback_from, fallback_reason, estimated_cost
```

### 2.2 The 4 Backends

```
┌────────────────────────────────────────────────────────┐
│                    BACKEND STACK                        │
│                                                         │
│  claude-code ─── Cloud/paid, expert/standard tier       │
│  │  ├── opus    (complex reasoning, $$$)                │
│  │  ├── sonnet  (standard work, $$)                     │
│  │  └── haiku   (simple tasks, $)                       │
│  │                                                      │
│  localai ─────── Local/free, trainee tier                │
│  │  ├── hermes-3b  (heartbeats, simple, GPU)            │
│  │  ├── hermes     (complex, multi-step, GPU)           │
│  │  └── codellama  (code generation, GPU)               │
│  │  NOTE: single-active-backend (only 1 GPU model)      │
│  │                                                      │
│  openrouter-free  Cloud/free, community tier             │
│  │  └── 29 free models via load balancer                │
│  │                                                      │
│  direct ───────── No LLM, deterministic                  │
│     └── MCP tool calls, template responses               │
└────────────────────────────────────────────────────────┘

Routing principle: CHEAPEST CAPABLE BACKEND WINS.
Fallback: LocalAI → OpenRouter → Claude sonnet → Claude opus → queue.
```

### 2.3 Security/Architecture Override

Security and architecture agents NEVER go to free/trainee backends:
```python
force_claude = agent_name in _SECURITY_AGENTS or agent_name in _ARCHITECTURE_AGENTS
```

Security/architecture agents always use Claude regardless of backend_mode.

### 2.4 Fallback Chain

Each routing function returns a RoutingDecision with `fallback_backend`
and `fallback_model`. When the primary fails:

```
execute_fallback(decision, failure_reason)
  ↓
1. Check if fallback_backend is defined
  ↓
2. Check if fallback backend is available in BACKEND_REGISTRY
  ↓
3. Derive confidence tier for fallback backend
  ↓
4. Return new RoutingDecision with:
   backend=fallback_backend
   reason="fallback from {primary}: {failure_reason} → {fallback}"
   (provenance recorded for labor stamp)
  ↓
5. If no fallback → return None (task queued)
```

### 2.5 Health-Aware Routing (W5 Wiring)

```python
_apply_health_check(decision, health_dashboard):
  state = dashboard.get(decision.backend)
  if state is None: return decision  # no data = proceed
  if state.status == BackendStatus.DOWN:
    fallback = execute_fallback(decision, "health: backend DOWN")
    if fallback: return fallback
    return RoutingDecision(backend="queue", ...)
  return decision
```

### 2.6 Backend Health Dashboard

```
BackendHealthDashboard:
  ├── LocalAIHealth
  │   ├── loaded_model, gpu_memory_used/total_mb
  │   ├── swap_in_progress
  │   └── status (UP/DOWN/DEGRADED/SWAPPING)
  │
  ├── ClaudeHealth
  │   ├── quota_used_pct (5-hour), weekly_quota_used_pct (7-day)
  │   ├── context_window_size (200K/1M)
  │   ├── rate_limited, model_available
  │   └── quota_warning (≥80%), quota_critical (≥95%)
  │
  └── OpenRouterHealth
      ├── free_models_available, free_tier_active
      └── status
```

### 2.7 Model Swap (LocalAI)

LocalAI constraint: only 1 GPU model loaded at a time (8GB VRAM).

```
Router decides: task needs hermes (7B), currently loaded: hermes-3b (3B)
  ↓
SwapDecision: needed=True, current=hermes-3b, requested=hermes
  ↓
Skip-swap check: do queued tasks need current model?
  If majority of queue needs hermes-3b → skip swap, route differently
  ↓
If swap needed:
  SwapRecord: from_model=hermes-3b, to_model=hermes
  → initiate swap via LocalAI API
  → wait for model load (~10-80s depending on size)
  → verify health
  → record completion
  ↓
Metrics: swap_frequency(), model_load_count(), avg_duration()
```

### 2.8 Codex Review (Tier-Driven)

```
should_trigger_review(confidence_tier)
  ↓
REVIEW_TIERS = {"trainee", "trainee-validated", "community", "hybrid"}
  ↓
Tier in REVIEW_TIERS? → trigger review
  ↓
review_command(adversarial=True/False)
  → "/codex:adversarial-review" or "/codex:review"
```

W7 wiring: imports `VALID_TIERS` from tier_progression.py. `trainee-validated` added to REVIEW_TIERS.

---

## 3. File Map

```
fleet/core/
├── backend_router.py      Routing decision, 5 budget routes, fallback  (569 lines)
├── backend_health.py      Per-backend health states, dashboard          (324 lines)
├── model_swap.py          LocalAI swap management, skip-swap logic     (343 lines)
├── codex_review.py        Tier-driven adversarial review trigger       (313 lines)
└── router_unification.py  FUTURE: AICP ↔ Fleet bridge schema           (62 lines)
```

Total: **1611 lines** across 5 modules.

---

## 4. Per-File Documentation

### 4.1 `backend_router.py` — Routing Engine (569 lines)

#### Key Functions

| Function | Lines | What It Does |
|----------|-------|-------------|
| `route_task(task, agent, backend_mode, localai_available, localai_model, storm_monitor, health_dashboard)` | 201-272 | Main routing: assess complexity → filter by enabled backends (backend_mode) → cheapest capable wins → health check (W5) → circuit breaker check. Returns RoutingDecision. |
| `backends_for_mode(backend_mode)` | — | Map backend_mode to list of enabled backend names (7 combos). |
| `_assess_complexity(task)` | — | Map story points/type to simple/medium/complex/critical. |
| `_apply_health_check(decision, dashboard)` | — | W5: check backend DOWN → fallback or queue. |
| `_apply_circuit_breakers(decision, storm_monitor)` | 273-330 | Check breaker OPEN → fallback. Both OPEN → queue. |
| `execute_fallback(decision, reason)` | 479-511 | Execute fallback: check registry → derive tier → return new decision. |

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `BackendDefinition` | 40-55 | Backend: name, type (local/cloud/free/none), cost, capabilities, health_check_url, available, models. |
| `RoutingDecision` | 140-170 | Result: backend, model, effort, reason, confidence_tier, estimated_cost, fallback_backend/model/reason. |

#### Constants

| Name | Purpose |
|------|---------|
| `BACKEND_REGISTRY` | 4 backends with capabilities, cost, models |
| `_SECURITY_AGENTS` | Agents that always use Claude |
| `_ARCHITECTURE_AGENTS` | Agents that always use Claude |
| `_REQUIRED_CAPABILITIES` | Capability requirements per complexity level |

### 4.2 `backend_health.py` — Health States (324 lines)

| Class | Lines | Purpose |
|-------|-------|---------|
| `BackendStatus` | Enum | UP, DOWN, DEGRADED, UNKNOWN, SWAPPING |
| `BackendHealthState` | 37-74 | Base: name, status, last_check, latency_ms, stale detection (5min). |
| `LocalAIHealth` | 80-110 | + loaded_model, gpu_memory_used/total_mb, swap_in_progress. |
| `ClaudeHealth` | 116-145 | + quota_used_pct, weekly_quota_used_pct, context_window_size, rate_limited. Properties: quota_warning (≥80%), quota_critical (≥95%), weekly versions. |
| `OpenRouterHealth` | 152-170 | + free_models_available, free_tier_active. |
| `BackendHealthDashboard` | 175-311 | Aggregates all. Methods: update(), get(), availability_score(), routing_options(), format_report(). |

### 4.3 `model_swap.py` — LocalAI Swap (343 lines)

| Class | Lines | Purpose |
|-------|-------|---------|
| `SwapRecord` | 31-64 | from/to model, timing, success/skipped/error. |
| `SwapDecision` | 70-100 | needed, current/requested model, should_skip, skip_reason. |
| `QueuedTask` | — | Task in queue with needed model, for skip-swap evaluation. |
| `ModelSwapManager` | — | evaluate_swap(), record_successful/skipped/failed_swap(), swap_frequency(), model_load_count(). |

### 4.4 `codex_review.py` — Review Trigger (313 lines)

| Function | What It Does |
|----------|-------------|
| `should_trigger_review(tier, budget_mode, task_type, force)` | Returns (should_review, reason). Tier in REVIEW_TIERS + budget allows it. |
| `review_backend(budget_mode)` | Returns "codex-plugin" (paid modes) or "localai" (free modes). |
| `review_command(budget_mode)` | Returns "/codex:adversarial-review", "/codex:review", or "" (free). |

| Class | Purpose |
|-------|---------|
| `CodexReviewRequest` | task_id, tier, budget_mode, review_type. `to_agent_instruction()` builds text instruction. |
| `CodexReviewResult` | passed, issues, findings. `to_pr_comment()` formats as APPROVED/CHANGES REQUESTED. |
| `CodexReviewTracker` | approval_rate, avg_issues, by_backend metrics. |

### 4.5 `router_unification.py` — FUTURE (62 lines)

Schema only: `UnifiedRoutingRequest(source: "aicp"|"fleet")`, `UnifiedRoutingResult`. Bridge between AICP router and fleet router — not implemented.

---

## 5. Dependency Graph

```
backend_router.py ← budget_modes (BUDGET_MODES, get_mode)
                    labor_stamp (derive_confidence_tier)
                    models (Task)
                    backend_health (BackendHealthDashboard, BackendStatus) [TYPE_CHECKING + W5]
                    storm_monitor (StormMonitor) [TYPE_CHECKING]

backend_health.py ← standalone (dataclasses, time)

model_swap.py     ← standalone (dataclasses, time)

codex_review.py   ← tier_progression (VALID_TIERS) [W7 wiring]

router_unification.py ← standalone (dataclasses)
```

---

## 6. Consumers

| Layer | Module | What It Imports | How It Uses It |
|-------|--------|----------------|---------------|
| **Orchestrator** | — (inline) | Uses route_task() for dispatch decisions |
| **Backend Router** (self) | `backend_health` | W5: health-aware routing |
| **Backend Router** (self) | `storm_monitor` | Circuit breaker check |
| **Model Promotion** | W6 | `routing_model()` returns promoted model for localai_model param |
| **Session Telemetry** | W8 | `to_claude_health()` feeds ClaudeHealth with real quota |

---

## 7. Design Decisions

### Why cheapest-capable, not highest-quality?

Fleet cost is the primary constraint. Most tasks don't need opus.
A simple heartbeat check on a 3B model is as effective as opus
and costs nothing. The router optimizes cost within quality bounds.

### Why security/architecture agents always Claude?

Security analysis and architecture design cannot be compromised.
A trainee-tier LocalAI model might miss a vulnerability or produce
a flawed design. The cost of a missed security issue far exceeds
the cost of a Claude call.

### Why skip-swap logic for LocalAI?

Model swaps take 10-80 seconds. If the next 3 tasks in queue need
the current model, swapping for one task then swapping back is waste.
Skip-swap logic checks the queue before deciding to swap.

### Why health check before circuit breaker?

Health check detects infrastructure issues (backend DOWN).
Circuit breakers detect behavioral issues (repeated failures).
Checking health first prevents triggering circuit breaker
fallback for an infrastructure problem.

---

## 8. Data Shapes

### RoutingDecision

```python
RoutingDecision(
    backend="localai",
    model="hermes-3b",
    effort="low",
    reason="trivial task → localai/hermes-3b (cheapest capable)",
    confidence_tier="trainee",
    estimated_cost=0.0,
    fallback_backend="openrouter-free",
    fallback_model="openrouter/free",
)
```

### ClaudeHealth (with session telemetry W8)

```python
ClaudeHealth(
    name="claude-code",
    status=BackendStatus.UP,
    quota_used_pct=23.5,        # 5-hour
    weekly_quota_used_pct=41.2,  # 7-day
    context_window_size=1000000, # 1M
    latency_ms=2300.0,
    rate_limited=False,
    model_available="Opus",
    # quota_warning = False (23.5 < 80)
    # weekly_quota_warning = False (41.2 < 80)
)
```

---

## 9. What's Needed

- **Connect to real dispatch** — orchestrator uses route_task() for dispatch decisions (partially implemented)
- **LocalAI routing live test** — route real task to LocalAI, verify response
- **OpenRouter free tier** — client not built, 29 free models not configured
- **AICP bridge** — router_unification.py schema only, bridge not built
- **Session telemetry feeding health** — W8 adapter built, not wired to runtime

### Test Coverage

| File | Tests | Coverage |
|------|-------|---------|
| `test_backend_router.py` | 45 | 5 budget routes, complexity, fallback, circuit breakers |
| `test_backend_health.py` | 28 | Health states, dashboard, quotas |
| `test_model_swap.py` | 26 | Swap decisions, skip logic, metrics |
| `test_codex_review.py` | 37 | Trigger logic, review commands, tracking |
| `test_future_milestones.py` | 5 | Router unification schema |
| **Total** | **141** | Core logic fully covered |
