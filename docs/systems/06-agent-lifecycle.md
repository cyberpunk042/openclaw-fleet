# Agent Lifecycle & Roles — States, Authority, and Cost Control

> **2 files. 423 lines. Manages agent states (ACTIVE→IDLE→SLEEPING→OFFLINE) and PR authority per role.**
>
> Agent lifecycle tracks what each agent is doing. After 1 HEARTBEAT_OK
> the brain takes over evaluation — cron still fires, brain intercepts,
> silent OK if nothing for this agent ($0). States (IDLE, SLEEPING,
> OFFLINE) are visibility labels — all respond to wake triggers identically.
> Agent roles define PR authority — who can reject, who can close,
> who can set security holds. Fleet-ops is the final authority.

---

## 0. Silent Heartbeat Architecture — Cron Never Stops (2026-04-01)

### PO Requirement (Verbatim)

> "the agent need to be able to do silent heartbeat when they deem
> after a while that there is nothing new from the heartbeat, (2-3..)
> then it relay the work to the brain to actually do a compare and an
> automated work of the heartbeat in order to determine if it require
> a real heartbeat."

> "Like any good employee on call who know he can relax a bit reduce
> cost and let the automated systems take the relay while there is
> nothing particular to work on anyway."

### The Key Insight: We Never Stop

The gateway cron (`~/.openclaw/cron/jobs.json`) fires heartbeats at
a fixed interval per agent. **This never stops.** The agent is always
"on call." What changes is what HAPPENS when the cron fires:

```
Gateway cron fires for agent (every 10 min or configured interval)
  │
  ├── Brain intercepts BEFORE Claude call
  │   ├── Read agent lifecycle state
  │   ├── If ACTIVE/IDLE: proceed → real Claude heartbeat
  │   └── If IDLE/SLEEPING: brain evaluates deterministically (FREE)
  │       │
  │       ├── Check: mentions? tasks? contributions? directives?
  │       │   role triggers? board activity?
  │       │
  │       ├── Wake trigger found → fire REAL heartbeat
  │       │   (strategic config: model, effort, session strategy)
  │       │
  │       └── Nothing found → SILENT HEARTBEAT OK
  │           Log: "silent heartbeat OK for {agent}"
  │           Cost: $0
  │
  └── The agent never stopped. The cron never stopped.
      The brain is the FILTER between cron and Claude call.
```

### Current Gap

The brain interception layer does NOT exist yet. Currently:
- Gateway cron fires → Claude call happens immediately
- No lifecycle check between cron and Claude call
- SLEEPING agents still get expensive Claude calls

**What's needed:**
- Brain Step 8 (driver management) or a pre-heartbeat hook
  intercepts the cron firing and checks lifecycle state
- If sleeping: `_evaluate_sleeping_agent()` (fleet-elevation/23)
  runs deterministically, returns WakeDecision
- If WakeDecision.should_wake: brain fires real heartbeat with
  `decide_claude_call()` strategic config
- If not: brain responds "silent heartbeat OK" — no Claude call

**The cron interval itself may also adapt:**
- ACTIVE: 10 min (or per agent config)
- IDLE: could stay 10 min (brain filters cheap)
- IDLE/SLEEPING: could increase to 30min/60min
  (fewer cron fires = fewer brain evaluations, but brain eval is
  free so this is optimization, not requirement)

**Cron jobs.json structure (per agent):**
```json
{
  "id": "...",
  "agentId": "mc-{uuid}",
  "name": "{role}-heartbeat",
  "enabled": true,
  "schedule": {"kind": "every", "everyMs": 600000}
}
```

**Per-agent cron control exists partially:**
- `disable_gateway_cron_jobs()` — all-or-nothing (fleet pause)
- `enable_gateway_cron_jobs()` — all-or-nothing (fleet resume)
- No per-agent enable/disable yet
- No per-agent interval change yet
- Per-agent functions needed for interval adaptation (optional optimization)

**Cross-ref:** fleet-elevation/23 (lifecycle spec), brain-modules-standard.md,
agent-autonomy.yaml, System 22 §4.7 (session management)

---

## 1. Why It Exists

### Lifecycle: Cost Control

Without lifecycle management, every agent heartbeats at the same
frequency regardless of whether they have work. 10 agents × 30-second
heartbeats × Claude calls = expensive. With lifecycle + silent heartbeats:

```
ACTIVE agent: working on task, full sessions          → $$$
IDLE agent: nothing to do, real heartbeat every 30 min → $$
IDLE agent (1 HEARTBEAT_OK): brain intercepts, silent OK ($0) → $0
SLEEPING agent: 3+ HEARTBEAT_OK, brain evaluates ($0) → $0
```

**10 agents, 7 sleeping = ~70% cost reduction on idle agents.**

The savings come from the brain FILTERING the cron — not from stopping
it. The cron fires, the brain decides "nothing for this agent," no
Claude call happens, $0 cost. The agent is still on call — if a mention
or task arrives, the brain detects it and fires a real heartbeat.

### Roles: Authority Structure

Without role definitions, any agent could reject any PR. With roles:
- Only architect, QA, devsecops, and fleet-ops can reject PRs
- Only fleet-ops and devsecops can close PRs (abandon work)
- Only devsecops can set security_hold (block approval processing)
- Fleet-ops is the final authority (is_final_authority = True)

### PO Requirement (Verbatim)

> "the agent need to be able to do silent heartbeat when they deem
> after a while that there is nothing new from the heartbeat, (2-3..)
> then it relay the work to the brain to actually do a compare and an
> automated work of the heartbeat in order to determine if it require
> a real heartbeat."

---

## 2. How It Works

### 2.1 Lifecycle States

```
┌──────────┐
│  ACTIVE  │ Has work. Full Claude sessions.
│          │ Heartbeat: 0 (agent drives own work)
│          │ Cost: normal
└────┬─────┘
     │ 1 HEARTBEAT_OK (or no task for 10 min)
     ▼
┌──────────┐
│   IDLE   │ No work. Still real heartbeats.
│          │ Heartbeat: every 30 minutes
│          │ Cost: reduced
└────┬─────┘
     │ 2 consecutive HEARTBEAT_OK (or idle for 30 min)
     ▼
┌──────────┐
│  IDLE       │ 1 HEARTBEAT_OK → brain takes over. Silent OK.
│          │ Heartbeat: every 60 minutes
│          │ Cost: minimal
└────┬─────┘
     │ 3 consecutive HEARTBEAT_OK
     ▼
┌──────────┐
│ SLEEPING │ Brain evaluates deterministically (FREE).
│          │ Heartbeat: every 2 hours (rare check)
│          │ Cost: $0
└────┬─────┘
     │ 4 hours sleeping
     ▼
┌──────────┐
│ OFFLINE  │ Extended absence. Slow wake.
│          │ Heartbeat: every 2 hours
│          │ Cost: $0
└──────────┘

WAKE triggers (any sleeping/idle/offline agent):
  ├── Task assigned to agent     → wake immediately
  ├── @mention in board memory   → wake immediately
  ├── Contribution task created  → wake immediately
  └── PO directive targeting     → wake immediately
```

### 2.2 Transition Logic

Two transition mechanisms, content-aware has priority:

**Content-aware (from HEARTBEAT_OK count):**
```python
consecutive_heartbeat_ok >= 3  →  SLEEPING
consecutive_heartbeat_ok >= 1  →  brain_evaluates = True
```

**Time-based (fallback when count isn't tracked):**
```python
idle < 10 min          →  IDLE
idle < 30 min          →  IDLE
idle < 4 hours         →  SLEEPING
idle >= 4 hours        →  OFFLINE
```

Work assignment resets everything:
```python
has_active_task  →  ACTIVE, consecutive_heartbeat_ok = 0
```

### 2.3 PR Authority Matrix

```
                    can_    can_request_  can_    can_block_  is_final_  rejection_
                    reject  changes       close   approval    authority  creates_fix
architect           ✓       ✓             ✗       ✗           ✗          ✓
software-engineer   ✗       ✓             ✗       ✗           ✗          ✗
qa-engineer         ✓       ✓             ✗       ✗           ✗          ✓
devops              ✗       ✓             ✗       ✗           ✗          ✗
devsecops-expert    ✓       ✓             ✓       ✓           ✗          ✓
technical-writer    ✗       ✓             ✗       ✗           ✗          ✗
ux-designer         ✗       ✓             ✗       ✗           ✗          ✗
project-manager     ✗       ✓             ✗       ✗           ✗          ✗
fleet-ops           ✓       ✓             ✓       ✗           ✓          ✓
accountability      ✗       ✓             ✗       ✗           ✗          ✗
```

Key rules:
- **fleet-ops** is final authority — their approval/rejection is definitive
- **devsecops-expert** is the ONLY agent that can set security_hold
- **fleet-ops** and **devsecops** are the ONLY agents that can close PRs
- Rejection by architect/QA/devsecops auto-creates fix task for original author

### 2.4 Review Domains Per Agent

Each agent is qualified to review specific domains:

| Agent | Review Domains |
|-------|---------------|
| architect | architecture, design, coupling, abstraction, pattern |
| software-engineer | code, implementation, python, refactor |
| qa-engineer | test, quality, coverage, regression, validation |
| devops | docker, ci, deploy, infrastructure, pipeline |
| devsecops-expert | security, cve, vulnerability, secret, credential, compliance |
| technical-writer | documentation, readme, api_doc, changelog |
| ux-designer | ui, ux, accessibility, layout, user_flow |
| project-manager | planning, sprint, requirements, priority |
| fleet-ops | quality, governance, compliance, standard |
| accountability | accountability, evidence, traceability |

---

## 3. File Map

```
fleet/core/
├── agent_lifecycle.py  States, transitions, heartbeat scheduling  (217 lines)
└── agent_roles.py      PR authority, review domains per role      (206 lines)
```

Total: **423 lines** across 2 modules.

---

## 4. Per-File Documentation

### 4.1 `agent_lifecycle.py` — State Machine (217 lines)

#### Enums & Constants

| Name | Type | Value |
|------|------|-------|
| `AgentStatus` | Enum | ACTIVE, IDLE, SLEEPING, OFFLINE |
| `IDLE_AFTER` | int | 600 (10 min) |
| `SLEEPING_AFTER` | int | 1800 (30 min) |
| `OFFLINE_AFTER` | int | 14400 (4 hours) |
| `IDLE_AFTER_HEARTBEAT_OK` | int | 1 |
| `SLEEPING_AFTER_HEARTBEAT_OK` | int | 3 |
| `HEARTBEAT_INTERVALS` | dict | ACTIVE=0, IDLE=600, SLEEPING=1800, OFFLINE=3600 |

#### AgentState Class (lines 64-157)

| Method | Lines | What It Does |
|--------|-------|-------------|
| `update_activity(now, has_active_task, task_id)` | 78-113 | Update state based on current activity. Active task → ACTIVE + reset counter. No task → content-aware or time-based transition. |
| `record_heartbeat_ok()` | 115-121 | Increment consecutive_heartbeat_ok counter. Drives content-aware sleep. |
| `record_heartbeat_work()` | 123-128 | Reset counter to 0. Agent is active. |
| `needs_heartbeat(now)` | 130-142 | Check if enough time has passed since last heartbeat per status interval. ACTIVE agents never need heartbeat (they drive own work). |
| `mark_heartbeat_sent(now)` | 144-146 | Record heartbeat timestamp. |
| `wake(now)` | 148-152 | Explicitly wake agent → IDLE, reset counter. |
| `should_wake_for_task()` | — | True if IDLE, SLEEPING, or OFFLINE. |

Fields: name, status, last_active_at, last_heartbeat_at, last_task_completed_at, current_task_id, consecutive_heartbeat_ok, last_heartbeat_data_hash.

#### FleetLifecycle Class (lines 159-218)

| Method | Lines | What It Does |
|--------|-------|-------------|
| `get_or_create(name)` | 172-176 | Get or create AgentState for agent. |
| `update_all(now, active_agents)` | 178-191 | Update all tracked agents based on current board state. active_agents = {agent_name: task_id}. |
| `agents_needing_heartbeat(now)` | 193-198 | Return agents that need heartbeat check based on status and interval. |
| `get_status_summary()` | 200-211 | Agent names grouped by status: {"active": [...], "idle": [...], ...}. |
| `is_fleet_idle()` | 213-218 | True if no agent is ACTIVE. |

### 4.2 `agent_roles.py` — PR Authority & Domains (206 lines)

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `PRAuthority` | 25-35 | Dataclass: can_reject, can_request_changes, can_close_pr, can_block_approval, rejection_creates_fix_task, is_final_authority |
| `AgentRole` | 38-46 | Dataclass: name, primary_role, main_secondary_role, backup_secondary_role, pr_authority, review_domains |

#### Constants

| Name | Type | Size |
|------|------|------|
| `AGENT_ROLES` | dict[str, AgentRole] | 10 agents fully defined |

#### Functions

| Function | Lines | What It Does |
|----------|-------|-------------|
| `get_agent_role(name)` | 175-177 | Get full role definition. |
| `can_agent_reject(name)` | 180-183 | Check rejection authority. |
| `can_agent_close_pr(name)` | 186-189 | Check PR close authority. |
| `can_agent_block_approval(name)` | 192-195 | Check security_hold authority. |
| `should_create_fix_task(name)` | 198-201 | Check if rejection auto-creates fix task. |
| `get_review_domains(name)` | 204-206 | Get qualified review domains. |

---

## 5. Dependency Graph

```
agent_lifecycle.py   ← standalone (dataclasses, datetime, enum)

agent_roles.py       ← standalone (dataclasses)
```

No imports between them. Both consumed by orchestrator and MCP tools.

---

## 6. Consumers

| Layer | Module | What It Imports | How It Uses It |
|-------|--------|----------------|---------------|
| **Orchestrator** | `orchestrator.py` | `AgentStatus, FleetLifecycle` | Update lifecycle states every cycle. Check who needs heartbeat. Track active vs sleeping. |
| **MCP Tools** | `tools.py` | `AGENT_ROLES, can_agent_reject, should_create_fix_task, get_agent_role` | fleet_approve checks rejection authority. Auto-creates fix task on rejection. |

---

## 7. Design Decisions

### Why content-aware over pure time-based?

Time-based misses the signal: an agent might have work every 30 minutes
but report HEARTBEAT_OK in between. Content-aware (counting consecutive
HEARTBEAT_OK responses) detects when the agent ITSELF says "nothing for
me" — which is more accurate than timer-based idle detection.

### Why brain_evaluates after 1 HEARTBEAT_OK?

After 1 proper heartbeat with nothing to do, the brain takes over. It signals: "agent is idle,
but let's give one more check." If the brain can evaluate deterministically
the brain intercepts the cron and avoids the Claude call entirely.
Going directly from IDLE to SLEEPING would miss the gradual transition.

### Why is fleet-ops the only final authority?

One agent must have the last word on approvals. If multiple agents could
independently approve, there's no quality gate. Fleet-ops as final
authority means every piece of work gets one definitive review.

### Why can only devsecops set security_hold?

Security holds block the entire approval chain. This is a powerful
action that should only be used for genuine security concerns. Giving
it to every agent would lead to abuse or false positives. DevSecOps
is the security expert — they alone make the call.

### Why does rejection auto-create fix tasks?

When architect or QA rejects, the original author needs to know what
to fix. A fix task (auto-created, linked to original) is clearer than
a comment. It enters the PM's inbox, gets prioritized, and has its
own stage progression. The rejection reason becomes the fix task's
verbatim requirement.

---

## 8. Cost Model

```
Agent Status    Heartbeat Interval    Claude Calls/Hour    Cost
ACTIVE          0 (own work)          1-4 (per task)       $$$
IDLE            30 min                2                    $$
IDLE          60 min                1                    $
SLEEPING        2 hours               0.5                  ¢
OFFLINE         2 hours               0.5                  ¢

Fleet of 10 agents:
  3 ACTIVE + 2 IDLE + 2 IDLE + 3 SLEEPING
  = 12 + 4 + 2 + 1.5 = 19.5 calls/hour

  vs. without lifecycle (all at 2/hour):
  = 20 calls/hour

  vs. naive 30-second cycle for all:
  = 1200 calls/hour (!!!!)

Lifecycle reduces calls by 99% compared to naive polling.
```

---

## 9. Data Shapes

### AgentState

```python
AgentState(
    name="software-engineer",
    status=AgentStatus.IDLE,
    last_active_at=datetime(2026, 3, 31, 14, 0),
    last_heartbeat_at=datetime(2026, 3, 31, 15, 0),
    current_task_id=None,
    consecutive_heartbeat_ok=2,
    last_heartbeat_data_hash="abc123",
)
```

### Fleet Status Summary

```python
{
    "active": ["software-engineer", "architect"],
    "idle": ["project-manager"],
    "idle": ["qa-engineer"],
    "sleeping": ["devops", "technical-writer", "ux-designer",
                 "accountability-generator"],
    "offline": [],
}
```

### AgentRole

```python
AgentRole(
    name="devsecops-expert",
    primary_role="security",
    main_secondary_role="security_reviewer",
    backup_secondary_role="compliance",
    pr_authority=PRAuthority(
        can_reject=True,
        can_request_changes=True,
        can_close_pr=True,
        can_block_approval=True,
        rejection_creates_fix_task=True,
    ),
    review_domains=["security", "cve", "vulnerability", "secret",
                    "credential", "compliance"],
)
```

---

## 10. What's Needed

### Brain-Evaluated Heartbeats (Not Implemented)

The lifecycle data structures exist (IDLE state, consecutive_heartbeat_ok,
last_heartbeat_data_hash) but the brain evaluation logic is NOT in the
orchestrator. Currently, even IDLE agents get real Claude heartbeats.

What needs building:
1. Orchestrator checks: is agent IDLE or SLEEPING?
2. Instead of gateway heartbeat, brain evaluates deterministically:
   - Has the pre-embed data hash changed since last heartbeat?
   - Are there new tasks assigned to this agent?
   - Are there @mentions for this agent?
   - Are there directives targeting this agent?
3. If any trigger → wake the agent (real heartbeat)
4. If no trigger → skip (zero cost)

This is fleet-elevation/23 and the most impactful cost optimization.

### Wake Triggers Per Role (Not Implemented)

What would make each agent care:
- fleet-ops: new tasks in review, pending approvals
- PM: unassigned tasks in inbox, blocked tasks
- architect: tasks needing design input
- QA: tasks needing test predefinition
- DevSecOps: PRs needing security review

These are role-specific wake triggers that the brain should evaluate
during IDLE/SLEEPING. Currently hardcoded only for PM and fleet-ops
in the orchestrator's `_wake_drivers()`.

### Test Coverage

| File | Tests | Coverage |
|------|-------|---------|
| `test_agent_lifecycle.py` | 20+ | States, transitions, heartbeat scheduling, fleet management |
| `test_agent_roles.py` | 15+ | Authority checks, review domains, role definitions |
| **Total** | **35+** | Core logic covered. Missing: brain evaluation, wake triggers |
