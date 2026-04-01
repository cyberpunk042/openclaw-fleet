# Labor Attribution — Provenance for Every Artifact

> **3 files. 901 lines. Every fleet artifact carries a labor stamp: who, what model, what cost, what tier.**
>
> Nothing produced by the fleet is anonymous. Every task completion,
> every heartbeat, every artifact gets a labor stamp recording: which
> agent, which backend, which model, what effort level, what skills
> were used, what confidence tier (expert/standard/trainee/community),
> how long it took, how many tokens, what it cost. Trainee/community
> tier work automatically triggers adversarial challenge review.

### PO Requirements (Verbatim)

> "the agents are going to explain the source of their labor, the model,
> the effort, the skills used"

> "the LocalAI work will also need to be flagged as trainee's work like
> any other variant in what was used to generates the artifacts. making
> sure that when the agents leave their marks we know what produced it."

---

## 1. Why It Exists

The March catastrophe couldn't be diagnosed because nobody knew
what was consuming tokens. Which agent? Which model? How many tokens
per heartbeat? Were void sessions free or paid?

Labor stamps solve this:
- Every artifact is traceable to what produced it
- Trainee/community tier automatically triggers extra review
- Cost per agent, per model, per tier is measurable
- Heartbeat cost trends detect when idle polling gets expensive
- Fallback routing is recorded (audit trail of backend switching)

---

## 2. How It Works

### 2.1 The Stamp

```
┌──────────────────────────────────────────────────────┐
│                    LABOR STAMP                        │
│                                                       │
│  WHO:  agent_name, agent_role (worker/driver/heartbeat)│
│                                                       │
│  WHAT: backend (claude-code/localai/openrouter/direct) │
│        model (opus-4-6/sonnet-4-6/hermes-3b/qwen3-8b) │
│        model_version, effort (low/medium/high/max)    │
│                                                       │
│  HOW:  skills_used, tools_called                      │
│        session_type (fresh/compact/continue)           │
│                                                       │
│  CONFIDENCE: tier (expert/standard/trainee/community)  │
│              reason (auto-derived from backend+model)  │
│                                                       │
│  COST: duration_seconds, estimated_tokens,             │
│        estimated_cost_usd                              │
│                                                       │
│  EFFORT: lines_added, lines_removed, cache_read_tokens │
│          (from session telemetry W8)                   │
│                                                       │
│  ITERATION: iteration count, challenge_rounds,         │
│             challenge_types, challenge_skipped (W2)    │
│                                                       │
│  CONTEXT: budget_mode, fallback_from, fallback_reason  │
│           timestamp                                    │
└──────────────────────────────────────────────────────┘
```

### 2.2 Confidence Tier Derivation

```
derive_confidence_tier(backend, model):

  claude-code + opus     → "expert"     (highest quality)
  claude-code + sonnet   → "standard"   (good quality)
  claude-code + haiku    → "standard"   (acceptable)
  localai + any          → "trainee"    (needs validation)
  openrouter-free + any  → "community"  (needs validation)
  unknown                → "community"  (conservative default)
```

**Trainee/community tier → `requires_challenge` = True.**
Fleet-ops MUST NOT approve without adversarial challenge.

### 2.3 Stamp Assembly

```
Agent works on task → fleet_task_complete(summary)
  ↓
assemble_stamp(dispatch_record, duration, tokens, tools, session_type)
  ↓
1. Derive confidence tier from backend + model
  ↓
2. Estimate cost:
   - claude-code + opus: tokens × $0.000045
   - claude-code + sonnet: tokens × $0.000009
   - localai / openrouter-free: $0
  ↓
3. Build LaborStamp with all fields
  ↓
Stamp appears in:
  ├── Task custom fields (labor_*)
  ├── Completion comment (table format)
  ├── PR body (attribution section)
  ├── Board memory (tagged with tier)
  └── Event bus (fleet.task.completed event)
```

### 2.4 Heartbeat Stamps

Even idle heartbeats get stamps:

```python
create_heartbeat_stamp(
    agent_name="software-engineer",
    backend="claude-code",
    model="sonnet",
    duration_seconds=5,
    estimated_tokens=500,
    estimated_cost_usd=0.0045,
    budget_mode="standard",
    void=True,  # heartbeat produced no work
)
```

HeartbeatCostTracker monitors trends:
- Average heartbeat cost per agent
- Cost anomaly detection (heartbeat costing > 2× average)
- Total heartbeat cost as % of fleet cost
- Alert if heartbeats > 30% of total cost

### 2.5 Analytics

```
LaborAnalytics:
  record(stamp) → rolling window (max 500 stamps)
  record_approval(agent, task, approved)

  agent_metrics(agent) → total_tasks, total_cost, avg_cost,
                          avg_duration, approval_rate, primary_model
  model_metrics(model) → total_tasks, total_cost, avg_challenge_rounds
  tier_metrics(tier) → total_tasks, total_cost, approval_rate,
                        challenge_pass_rate
  cost_by_backend() → {"claude-code": $X, "localai": $0, ...}
  cost_by_budget_mode() → {"standard": $X, "economic": $Y, ...}
```

---

## 3. File Map

```
fleet/core/
├── labor_stamp.py      LaborStamp, DispatchRecord, assembly, tier derivation (240 lines)
├── labor_analytics.py  Per-agent/model/tier metrics, cost breakdowns        (414 lines)
└── heartbeat_stamp.py  Heartbeat stamps, cost tracking, anomaly detection   (247 lines)
```

Total: **901 lines** across 3 modules.

---

## 4. Per-File Documentation

### 4.1 `labor_stamp.py` — The Stamp (240 lines)

#### Functions

| Function | Lines | What It Does |
|----------|-------|-------------|
| `derive_confidence_tier(backend, model)` | 14-41 | Auto-derive tier from backend+model. Returns (tier, reason). |
| `assemble_stamp(dispatch, duration, tokens, tools, session_type, iteration, agent_role)` | 187-240 | Combine dispatch record + session metrics → full LaborStamp. Estimate cost from backend+model. |
| `mark_challenge_skipped(stamp, reason)` | 230-240 | Mark stamp as challenge skipped (W2 wiring). Sets challenge_skipped=True + reason. |

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `LaborStamp` | 47-100 | Full provenance: 25+ fields covering WHO, WHAT, HOW, CONFIDENCE, COST, EFFORT, ITERATION, CONTEXT. Properties: requires_challenge (True for trainee/community/hybrid). |
| `DispatchRecord` | 155-181 | Records dispatch intent: task_id, agent, backend, model, effort, selection_reason, budget_mode, skills, dispatched_at. |

### 4.2 `labor_analytics.py` — Metrics Engine (414 lines)

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `AgentCostMetrics` | 30-78 | Per-agent: total_tasks/cost/duration/tokens, approved/rejected, models_used, backends_used. Properties: avg_cost_per_task, approval_rate, primary_model. |
| `ModelCostMetrics` | 84-117 | Per-model: total_tasks/cost/tokens, approved/rejected, avg_challenge_rounds. |
| `TierCostMetrics` | 123-164 | Per-tier: total_tasks/cost, approved/rejected, challenge_required/passed. Properties: challenge_pass_rate, approval_rate. |
| `LaborAnalytics` | 170-414 | Engine: record(stamp), record_approval(), agent_metrics(), model_metrics(), tier_metrics(), cost_by_backend(), cost_by_budget_mode(), summary(), format_report(). Rolling window of 500 stamps. |

### 4.3 `heartbeat_stamp.py` — Heartbeat Cost (247 lines)

#### Functions

| Function | Lines | What It Does |
|----------|-------|-------------|
| `create_heartbeat_stamp(agent, backend, model, duration, tokens, cost, budget_mode, void)` | 28-68 | Create minimal LaborStamp for a heartbeat (agent_role="heartbeat"). |

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `HeartbeatCostEntry` | 74-80 | Single data point: agent, cost, duration, tokens, void bool, timestamp. |
| `HeartbeatCostTracker` | 85-247 | Track heartbeat costs: record(), per_agent_avg_cost(), cost_anomaly_detection() (>2× average), total_heartbeat_cost_pct(), summary(), format_report(). Alert threshold: heartbeats > 30% of total cost. |

---

## 5. Dependency Graph

```
labor_stamp.py       ← standalone (dataclasses, datetime, typing)
    ↑
labor_analytics.py   ← imports LaborStamp from labor_stamp
    ↑
heartbeat_stamp.py   ← imports LaborStamp from labor_stamp
```

---

## 6. Consumers (7 non-test)

| Layer | Module | What It Imports | How It Uses It |
|-------|--------|----------------|---------------|
| **MCP Tools** | `tools.py` | `DispatchRecord, assemble_stamp` | fleet_task_complete assembles stamp from dispatch + session data |
| **Backend Router** | `backend_router.py` | `derive_confidence_tier` | Derive tier for routing decision |
| **Templates** | `comment.py` | `LaborStamp` | Render stamp in task completion comment (table format) |
| **Templates** | `pr.py` | `LaborStamp` | Include stamp in PR body (attribution section) |
| **Dispatch CLI** | `dispatch.py` | `DispatchRecord` | Create dispatch record at task dispatch time |
| **Heartbeat Stamp** | `heartbeat_stamp.py` | `LaborStamp` | Create heartbeat-specific stamps |
| **Labor Analytics** | `labor_analytics.py` | `LaborStamp` | Aggregate stamps for metrics |

---

## 7. Design Decisions

### Why auto-derive confidence tier, not manual?

Humans forget to set confidence. Auto-derivation from backend+model
is deterministic: opus = expert, localai = trainee. No human input
needed. No mistakes. Every stamp gets a tier.

### Why track heartbeat cost separately?

Heartbeats are the #1 cost driver in an idle fleet. The March drain
was mostly heartbeat sessions. Separate tracking lets the PO see:
"heartbeats cost $15/day while actual work cost $3/day" — which
immediately suggests reducing heartbeat frequency or using LocalAI.

### Why trainee/community triggers challenge automatically?

Lower-quality backends (LocalAI, OpenRouter free) produce work that
needs validation. Instead of trusting fleet-ops to remember "this
was LocalAI, review extra carefully," the stamp's `requires_challenge`
property makes it automatic — the challenge engine checks the stamp
before allowing approval.

### Why rolling window of 500 stamps?

Unbounded lists grow forever. 500 stamps covers ~1-2 weeks of work
at normal fleet pace. Older data is less relevant for current cost
analysis. If historical data is needed, event store has the full log.

### Why estimate cost in assemble_stamp, not from session telemetry?

Stamp assembly happens at fleet_task_complete time. Session telemetry
data may not be available yet. The estimate (tokens × per-token rate)
gives a reasonable number immediately. When W8 session telemetry is
wired, real cost replaces the estimate.

---

## 8. Data Shapes

### LaborStamp (full)

```python
LaborStamp(
    agent_name="software-engineer",
    agent_role="worker",
    backend="claude-code",
    model="sonnet-4-6",
    model_version="sonnet-4-6",
    effort="high",
    skills_used=["implementation"],
    tools_called=["fleet_read_context", "fleet_task_accept",
                  "fleet_commit", "fleet_task_complete"],
    session_type="fresh",
    confidence_tier="standard",
    confidence_reason="claude-code/sonnet → standard quality",
    duration_seconds=180,
    estimated_tokens=15000,
    estimated_cost_usd=0.135,
    lines_added=256,
    lines_removed=31,
    cache_read_tokens=2000,
    iteration=1,
    challenge_rounds_survived=0,
    challenge_types_faced=[],
    challenge_skipped=False,
    budget_mode="standard",
    fallback_from=None,
    timestamp="2026-03-31T15:42:00",
)
```

### Completion Comment (rendered from stamp)

```markdown
| Field | Value |
|-------|-------|
| Agent | software-engineer |
| Backend | claude-code |
| Model | sonnet-4-6 |
| Confidence | standard |
| Effort | high |
| Duration | 3m 0s |
| Tokens | ~15,000 |
| Cost | $0.14 |
| Lines | +256 / -31 |
```

---

## 9. What's Needed

- **Session telemetry feeding real values** — W8 adapter built,
  `to_labor_fields()` returns real duration/cost/lines, but not
  wired to stamp assembly in fleet_task_complete
- **Stamp in task custom fields** — LaborStamp fields exist on
  TaskCustomFields but not populated during fleet_task_complete
- **Heartbeat stamp integration** — create_heartbeat_stamp() exists
  but orchestrator doesn't call it after heartbeats
- **Analytics dashboard** — cost per agent, per model, per tier
  visualization (not built)

### Test Coverage

| File | Tests | Coverage |
|------|-------|---------|
| `test_labor_stamp.py` | 17 | Stamp creation, tier derivation, assembly |
| `test_labor_analytics.py` | 27 | Metrics, approvals, cost breakdowns |
| `test_heartbeat_stamp.py` | 15+ | Heartbeat stamps, cost tracking |
| **Total** | **59+** | Core logic covered |
