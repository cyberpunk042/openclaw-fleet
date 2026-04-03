# Orchestrator — The Autonomous Brain

> **8 files. 2595 lines. The central coordinator that runs every 30 seconds.**
>
> The orchestrator is the fleet's brain. It reads fleet state, detects what
> needs attention, refreshes agent context, runs security scans, runs the
> immune system, creates review approvals, wakes driver agents, dispatches
> tasks, processes PO directives, evaluates parent tasks, and checks fleet
> health. Guarded by storm monitor, budget monitor, fleet mode, and effort
> profiles. The brain never creates Claude Code sessions directly — it
> writes context files and the gateway handles agent execution.

---

## 1. Why It Exists

Without the orchestrator, the fleet has no coordination:
- No one assigns agents to tasks
- No one wakes PM when tasks are unassigned
- No one wakes fleet-ops when approvals are pending
- No one detects stuck tasks or offline agents
- No one enforces budget limits or storm protections
- No one runs the immune system

The orchestrator is the ONLY component that sees the full fleet state
and makes coordination decisions. Everything else is either an agent
(sees only its own context) or a tool (handles one operation).

---

## 2. How It Works

### 2.1 The 30-Second Cycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR CYCLE (every 30s)                      │
│                                                                      │
│  PRE-CHECKS (gates — any can abort the cycle):                       │
│  ┌─────────────┐ ┌─────────────┐ ┌────────────┐ ┌──────────────┐   │
│  │ Storm       │ │ Gateway     │ │ Effort     │ │ Fleet Mode   │   │
│  │ Monitor     │ │ Duplication │ │ Profile    │ │              │   │
│  │             │ │ Check       │ │            │ │              │   │
│  │ CRITICAL    │ │ Duplicate   │ │ Profile    │ │ work-paused  │   │
│  │ → STOP      │ │ → STORM     │ │ disallows  │ │ → skip       │   │
│  │ STORM → 0   │ │   indicator │ │ dispatch   │ │ dispatch     │   │
│  │ WARNING → 1 │ │             │ │ → skip     │ │              │   │
│  └─────────────┘ └─────────────┘ └────────────┘ └──────────────┘   │
│                                                                      │
│  STEPS (executed in order):                                          │
│                                                                      │
│  Step 0 │ _refresh_agent_contexts()                                  │
│         │ Write context/ files for ALL agents (pre-embed full data)   │
│         │ Role-specific via role_providers. FULL data, not compressed.│
│         ↓                                                            │
│  Step 1 │ _security_scan()                                           │
│         │ Behavioral security scan on new/changed tasks.             │
│         │ Critical findings → security_hold on task + ntfy PO.       │
│         ↓                                                            │
│  Step 2 │ _run_doctor()                                              │
│         │ Immune system: detect diseases, decide responses.          │
│         │ Produce DoctorReport → skip/block flagged agents/tasks.    │
│         │ Inject teaching lessons via gateway.                        │
│         ↓                                                            │
│  Step 3 │ _ensure_review_approvals()                                 │
│         │ Create approval objects for tasks in review status.        │
│         │ Fleet-ops can then approve/reject.                         │
│         ↓                                                            │
│  Step 4 │ _wake_drivers()                                            │
│         │ PM wakes if unassigned inbox tasks (120s cooldown).        │
│         │ Fleet-ops wakes if tasks in review (120s cooldown).        │
│         │ Waking = inject_content() via gateway WebSocket RPC.       │
│         ↓                                                            │
│  Step 5 │ _dispatch_ready_tasks()                                    │
│         │ Dispatch unblocked inbox tasks to assigned agents.         │
│         │ Respects: doctor report, fleet mode, cycle phase, max/cycle│
│         ↓                                                            │
│  Step 6 │ _process_directives()                                      │
│         │ Parse PO directives from board memory.                     │
│         │ Route to target agent's heartbeat context.                 │
│         ↓                                                            │
│  Step 7 │ _evaluate_parents()                                        │
│         │ When ALL children of a parent task are done → parent moves │
│         │ to review status.                                          │
│         ↓                                                            │
│  Step 8 │ _health_check()                                            │
│         │ Detect stuck tasks, offline agents, stale dependencies.    │
│         │ Auto-resolve via self_healing (create tasks or escalate).  │
│                                                                      │
│  NOTE: Heartbeats managed by GATEWAY, not orchestrator.              │
│  Orchestrator NEVER creates Claude Code sessions directly.           │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Pre-Checks in Detail

**Storm Monitor** (orchestrator.py:114-152):
```
storm_severity = _storm_monitor.evaluate()

CRITICAL → return immediately (fleet frozen, no dispatch)
STORM    → max_dispatch = 0 (monitoring only)
WARNING  → max_dispatch = min(current, 1) (limited)
WATCH    → monitoring note
WARNING+ → diagnostic snapshot captured to disk
```

Gateway duplication check runs every cycle — the root cause of the
March catastrophe. If duplicate gateway detected → storm indicator.

**Effort Profile** (orchestrator.py:97-107):
```
profile = get_profile(profile_name)
if not profile.allow_dispatch:
    return state  # skip entire cycle

config["max_dispatch_per_cycle"] = min(current, profile.max_dispatch_per_cycle)
```

**Fleet Mode** (orchestrator.py:198-199):
```
if not fleet_should_dispatch(fleet_state):
    state.notes.append("dispatch paused")
```

### 2.3 Step 0: Context Refresh (The Most Important Step)

**Source:** orchestrator.py:257-366, preembed.py, context_writer.py, role_providers.py

Every cycle, the orchestrator writes fresh context files for ALL agents:

```
For each agent (excluding Gateway):
  ↓
1. Find agent's assigned tasks (inbox + in_progress)
  ↓
2. Find messages mentioning this agent (@mentions in board memory)
  ↓
3. Find PO directives
  ↓
4. Get role-specific data via provider:
   ├── fleet_ops_provider → pending_approvals, review_queue, offline_agents
   ├── project_manager_provider → unassigned_tasks, blocked, sprint progress
   ├── architect_provider → design_tasks, high_complexity
   ├── devsecops_provider → security_tasks, prs_needing_review
   └── worker_provider → my_tasks_count, in_review
  ↓
5. Build heartbeat pre-embed (FULL data):
   build_heartbeat_preembed(agent, role, tasks, messages, directives,
                            role_data, fleet_mode, fleet_phase, fleet_backend,
                            agents_online, agents_total)
  ↓
6. Write to agents/{name}/context/fleet-context.md
  ↓
7. For in-progress tasks: also write task-context.md with stage instructions
```

**Key principle:** Pre-embedded data is FULL. Not compressed. Not summarized.
The 300-char compression disease was what made agents non-functional.

### 2.4 Step 4: Wake Drivers

**Source:** orchestrator.py:761-830

Two wake triggers with 120-second cooldowns:

```
Unassigned inbox tasks exist?
  AND PM has session key?
  AND last PM wake > 120s ago?
  → inject_content(pm.session_key, wake_message_with_task_details)
  → IRC: "[orchestrator] Woke PM — N unassigned tasks"

Tasks in review status exist?
  AND fleet-ops has session key?
  AND last ops wake > 120s ago?
  → inject_content(ops.session_key, wake_message_with_review_count)
  → IRC: "[orchestrator] Woke fleet-ops — N pending reviews"
```

Waking = `inject_content()` via gateway WebSocket RPC (`chat.send`).
The message contains FULL task details (not just count).

### 2.5 What the Orchestrator Does NOT Do

- Does NOT create Claude Code sessions (gateway does)
- Does NOT manage heartbeat scheduling (gateway cron does)
- Does NOT read agent output (gateway handles)
- Does NOT modify agent files other than context/ (IaC principle)
- Does NOT make AI decisions (all logic is deterministic Python)

---

## 3. File Map

```
fleet/cli/
└── orchestrator.py       Main cycle, 9 steps (target: 13), pre-checks (1378 lines)

fleet/core/
├── driver.py             Driver agent model, product roadmaps       (155 lines)
├── smart_chains.py       Pre-computed dispatch/completion context    (171 lines)
├── context_assembly.py   Task + heartbeat context aggregation       (331 lines)
├── context_writer.py     Write context/ files to agent directories  (86 lines)
├── preembed.py           Format pre-embedded data (FULL, not compressed) (170 lines)
├── role_providers.py     Per-role data for heartbeat context        (181 lines)
└── change_detector.py    Track what changed between cycles          (123 lines)
```

Total: **2595 lines** across 8 modules.

---

## 4. Per-File Documentation

### 4.1 `orchestrator.py` — The Main Loop (1378 lines)

The largest module in the fleet. Contains the 30-second cycle,
all 9 steps (target: 13 per brain spec fleet-elevation/04), pre-checks,
and persistent state. New steps: event queue, gates, contributions,
propagation, session management (see brain-modules-standard.md).

#### Persistent State (module-level)

| Variable | Type | Purpose |
|----------|------|---------|
| `_fleet_lifecycle` | FleetLifecycle | Agent state tracking across cycles |
| `_notification_router` | NotificationRouter | Dedup notifications (300s cooldown) |
| `_change_detector` | ChangeDetector | Track changes between cycles |
| `_budget_monitor` | BudgetMonitor | Track quota usage |
| `_storm_monitor` | StormMonitor | Detect storms |
| `_doctor_health_profiles` | dict[str, AgentHealth] | Per-agent health (persistent) |
| `_doctor_tool_calls` | dict[str, list[str]] | Recent tool calls per agent |
| `_previous_fleet_state` | FleetControlState | Detect mode changes |
| `_last_pm_wake` | datetime | PM wake cooldown |
| `_last_ops_wake` | datetime | Fleet-ops wake cooldown |

#### Main Function

| Function | Lines | What It Does |
|----------|-------|-------------|
| `run_orchestrator_cycle(mc, irc, board_id, config, dry_run)` | 77-251 | Execute one 30-second cycle. Pre-checks → 9 steps → return OrchestratorState. |

#### Step Functions

| Function | Step | Lines | What It Does |
|----------|------|-------|-------------|
| `_refresh_agent_contexts()` | 0 | 257-366 | Write context/ files for ALL agents. Role-specific via providers. |
| `_security_scan()` | 1 | 543-601 | Scan changed tasks for suspicious patterns. Security holds + ntfy. |
| `_run_doctor()` | 2 | 379-530 | Run immune system. Produce DoctorReport. Inject lessons. Handle prune. |
| `_ensure_review_approvals()` | 3 | (inline) | Create approval objects for review tasks. |
| `_wake_drivers()` | 4 | 761-830 | Wake PM (unassigned) + fleet-ops (reviews). 120s cooldown. |
| `_dispatch_ready_tasks()` | 5 | (inline) | Dispatch unblocked inbox tasks. Respects doctor/mode/phase/max. |
| `_process_directives()` | 6 | (inline) | Parse PO directives → route to agent context. |
| `_evaluate_parents()` | 7 | (inline) | All children done → parent to review. |
| `_health_check()` | 8 | 606-668 | Fleet health assessment + self-healing actions. |

### 4.2 `driver.py` — Autonomous Drivers (155 lines)

Defines which agents own products and create their own work.

| Class | Lines | Purpose |
|-------|-------|---------|
| `ProductRoadmap` | 26-34 | Product: name, project, owner_agent, milestones, prerequisites |
| `DriverDirective` | 69-77 | What driver should do: priority (1-4), action, task_id, product |

| Constant | Value |
|----------|-------|
| `PRODUCTS` | dspd (PM owns), nnrt (accountability-generator owns) |
| `DRIVER_AGENTS` | project-manager, fleet-ops, accountability-generator, devsecops-expert |

| Function | Lines | What It Does |
|----------|-------|-------------|
| `determine_driver_directive(agent, tasks)` | 80-143 | Priority: 1=human-assigned, 2=any assigned, 3=own product roadmap, 4=fleet improvement |
| `is_driver(agent)` | 154-156 | True if agent is in DRIVER_AGENTS set |

### 4.3 `smart_chains.py` — Pre-Computed Context (171 lines)

Pre-computes context so agents don't waste MCP calls.

| Class | Lines | Purpose |
|-------|-------|---------|
| `DispatchContext` | 31-100 | Pre-computed task context: task details, worktree, model, acceptance criteria, recent decisions, related work, sprint progress. `format_message()` renders as dispatch message. |

### 4.4 `context_assembly.py` — Context Aggregation (331 lines)

Single source of truth for assembling context bundles.

| Function | Lines | What It Does |
|----------|-------|-------------|
| `clear_context_cache(cycle_id)` | 28-32 | Clear per-cycle cache. Called at start of each cycle. |
| `assemble_task_context(task, mc, board_id, plane, event_store)` | 35-223 | Aggregates: task core + custom fields + methodology (stage, instructions, readiness, required stages, next stage) + artifact (from Plane HTML via transpose) + comments (last 20) + activity (last 15 events) + related tasks (children, parent, dependencies) + Plane data. Per-cycle cached. |
| `assemble_heartbeat_context(agent, role, tasks, agents, mc, board_id, event_store, role_providers, fleet_state)` | 226-331 | Role-specific via providers + fleet state + messages + events. |

### 4.5 `context_writer.py` — File Writer (86 lines)

Writes to `agents/{name}/context/`:

| Function | Lines | What It Does |
|----------|-------|-------------|
| `write_heartbeat_context(agent_name, content)` | 24-37 | Write fleet-context.md. Gateway reads on next heartbeat. |
| `write_task_context(agent_name, content)` | 40-53 | Write task-context.md. Gateway reads at dispatch. |
| `clear_task_context(agent_name)` | 56-67 | Remove task-context.md (task complete or agent pruned). |

### 4.6 `preembed.py` — Data Formatting (170 lines)

Formats pre-embedded data as structured markdown agents read naturally.

| Function | Lines | What It Does |
|----------|-------|-------------|
| `format_events(events, limit)` | 19-35 | Format events with type, agent, summary, time. |
| `format_task_full(task)` | 38-63 | FULL task detail: id, status, priority, agent, type, stage, readiness, SP, verbatim, description, blocked_by, PR, Plane. NOT truncated (except description at 500 chars). |
| `build_task_preembed(task, completeness)` | 66-91 | Task context + stage instructions from stage_context.py. |
| `build_heartbeat_preembed(agent, role, tasks, messages, directives, events, role_data, fleet_mode, fleet_phase, fleet_backend, agents_online, agents_total)` | 94-170 | Full heartbeat: directives → messages → assigned tasks → role data → events. Each section with headers. |

### 4.7 `role_providers.py` — Per-Role Data (181 lines)

5 provider functions returning role-specific heartbeat data:

| Provider | Agent | Returns |
|----------|-------|---------|
| `fleet_ops_provider` | fleet-ops | pending_approvals (count + details), review_queue, offline_agents |
| `project_manager_provider` | project-manager | unassigned_tasks (count + details), blocked_tasks, progress (done/total) |
| `architect_provider` | architect | design_tasks (epics/stories in analysis/investigation/reasoning), high_complexity |
| `devsecops_provider` | devsecops | security_tasks (tagged security), prs_needing_security_review |
| `worker_provider` | all others | my_tasks_count, in_review tasks |

Registry: `ROLE_PROVIDERS` dict maps agent name → provider function.
`get_role_provider(role)` falls back to `worker_provider`.

### 4.8 `change_detector.py` — Cycle Diff (123 lines)

Tracks what changed between orchestrator cycles.

| Class | Lines | Purpose |
|-------|-------|---------|
| `Change` | 21-30 | Single change: type, task_id, agent, old/new value, timestamp |
| `ChangeSet` | 34-56 | All changes: new_tasks_in_review, new_tasks_done, new_tasks_in_inbox, tasks_unblocked, agents_went_offline. Properties: needs_review_wake, needs_dispatch |
| `ChangeDetector` | 59-123 | Diffs task states between cycles. `detect(tasks, now)` → ChangeSet |

---

## 5. Dependency Graph

```
orchestrator.py  ← imports from ALL other modules in this system
    ↑               + agent_lifecycle, change_detector, notification_router
    │               + budget_monitor, doctor, directives, fleet_mode, teaching
    │               + storm_monitor, gateway_guard, behavioral_security
    │               + self_healing, health
    │
    ├── context_assembly.py ← methodology, stage_context, transpose, artifact_tracker,
    │                          event_router, plane
    │
    ├── preembed.py ← stage_context (get_stage_instructions)
    │
    ├── context_writer.py ← standalone (writes files)
    │
    ├── role_providers.py ← models.Task, models.TaskStatus
    │
    ├── smart_chains.py ← models.Task
    │
    ├── change_detector.py ← models.Task, models.TaskStatus
    │
    └── driver.py ← models.Task, models.TaskStatus
```

The orchestrator is the hub — it imports from nearly every system.
The supporting modules are mostly standalone with minimal imports.

---

## 6. Consumers

The orchestrator is NOT consumed — it IS the consumer. It runs as a
daemon and calls into every other system:

| What It Calls | System | How |
|--------------|--------|-----|
| FleetLifecycle | Agent Lifecycle | Update states, check who needs heartbeat |
| StormMonitor | Storm Prevention | Evaluate severity, gate dispatch |
| BudgetMonitor | Budget | Track quota, inform effort decisions |
| FleetControlState | Control Surface | Read mode/phase/backend from board |
| FleetControlState | Control Surface | Work mode gates dispatch |
| ChangeDetector | (self) | Identify what changed since last cycle |
| DoctorReport | Immune System | Detect diseases, skip/block agents |
| scan_task | Behavioral Security | Scan new tasks for threats |
| adapt_lesson | Teaching | Create lessons for sick agents |
| inject_content | Gateway | Wake drivers, inject lessons |
| parse_directives | Directives | Route PO commands |
| plan_healing_actions | Self-Healing | Auto-resolve health issues |
| build_heartbeat_preembed | Context | Build agent context data |
| write_heartbeat_context | Context Writer | Write context/ files |
| role_providers | Context | Get per-role data |

---

## 7. Design Decisions

### Why 30-second cycle, not event-driven?

Event-driven would be more responsive but fragile. If the event
bus has a bug, the orchestrator stops working. The 30-second poll
is resilient — even if events are lost, the orchestrator will
detect the state change on next cycle. For a fleet of 10 agents,
30 seconds is fast enough. Most agent actions take minutes.

### Why does the orchestrator never create Claude sessions?

Separation of concerns. The orchestrator is deterministic Python —
it makes coordination decisions. The gateway manages AI sessions —
it handles Claude Code execution, heartbeats, context injection.
If the orchestrator created sessions directly, it would need to
handle session lifecycle, authentication, and error recovery — all
of which the gateway already handles.

### Why write files instead of API calls for context?

Files are the gateway's native interface. The gateway reads
`agents/{name}/context/*.md` when building the system prompt.
Writing files is atomic (write + rename), survives restarts,
and doesn't depend on the gateway being online at write time.
API calls would require the gateway to be up during context refresh.

### Why persistent health profiles across cycles?

Disease patterns are cumulative. An agent corrected once is a
mistake. Corrected 3 times is sick. If health profiles reset each
cycle, the immune system would never detect cumulative patterns.
Module-level state persists across cycles (but not across daemon restarts).

### Why 120-second cooldown on driver waking?

Without cooldown, the orchestrator would wake PM every 30 seconds
if unassigned tasks exist. This floods the PM with wake messages.
120 seconds gives the PM two full cycles to process the wake before
being woken again.

### Why does Step 0 run for ALL agents, not just active ones?

Even sleeping agents need fresh context. When they wake (task
assigned, @mention), their context/ files should already be current.
Writing context for 10 agents is cheap (no API calls, just file writes).
Stale context when an agent wakes is expensive (wrong decisions).

---

## 8. OrchestratorState — Cycle Tracking

```python
@dataclass
class OrchestratorState:
    approvals_processed: int = 0
    tasks_transitioned: int = 0
    tasks_dispatched: int = 0
    parents_evaluated: int = 0
    drivers_woken: int = 0
    errors: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def total_actions(self) -> int:
        return (approvals_processed + tasks_transitioned +
                tasks_dispatched + parents_evaluated + drivers_woken)
```

Each cycle produces a state object logging what happened.
Errors are logged but don't abort the cycle — each step has
its own try/except to prevent cascading failures.

---

## 9. Data Shapes

### Heartbeat Pre-Embed (what agents see)

```markdown
# HEARTBEAT CONTEXT

Agent: architect
Role: architect
Fleet: 7/10 online | Mode: full-autonomous | Phase: execution | Backend: claude

## PO DIRECTIVES
- Focus on AICP Stage 1 LocalAI integration (from human)

## MESSAGES
- From project-manager: Design review needed for task abc123

## ASSIGNED TASKS (2)

### Add Fleet Controls to Header
- ID: abc123
- Status: in_progress
- Stage: analysis
- Readiness: 30%
- Verbatim Requirement: "Add fleet controls to the OCMC header bar..."

### Review Backend Router
- ID: def456
- Status: inbox
- Stage: reasoning
- Readiness: 80%

## ROLE DATA
### design_tasks (3)
  - {'id': 'ghi789', 'title': 'Implement budget mode...', 'stage': 'reasoning'}

## EVENTS SINCE LAST HEARTBEAT
  2026-03-31T15:42:00 [completed] software-engineer: Task xyz completed
```

### DispatchContext

```python
DispatchContext(
    task_id="abc123",
    task_title="Add fleet controls to header bar",
    task_description="The PO wants fleet controls...",
    task_priority="high",
    task_type="story",
    project="fleet",
    worktree="/home/jfortin/openclaw-fleet",
    branch="fleet/architect/abc123",
    story_points=5,
    model="sonnet",
    effort="high",
    acceptance_criteria="Controls visible in header. Mode switching works.",
    recent_decisions=["Use Radix Select for dropdowns"],
    sprint_progress="5/15 done (33%)",
)
```

### ChangeSet

```python
ChangeSet(
    changes=[
        Change(change_type="task_status_changed", task_id="abc123",
               old_value="in_progress", new_value="review"),
    ],
    new_tasks_in_review=["abc123"],
    new_tasks_done=[],
    new_tasks_in_inbox=[],
    tasks_unblocked=[],
    agents_went_offline=[],
)
```

---

## 10. What's Needed

### Brain-Evaluated Heartbeats (Largest Gap)

Currently, even IDLE/SLEEPING (brain-evaluated) agents get real heartbeats (Claude calls)
when their interval fires. The brain should evaluate deterministically:

```
Agent is IDLE/SLEEPING (brain-evaluated):
  1. Has pre-embed data hash changed? → wake
  2. New task assigned? → wake
  3. @mention in board memory? → wake
  4. PO directive? → wake
  5. None of the above → skip (zero cost)
```

Data structures exist in `agent_lifecycle.py` (consecutive_heartbeat_ok,
last_heartbeat_data_hash). Logic not in orchestrator.

### Contribution Subtask Creation (Critical for Synergy)

When a task enters REASONING with readiness approaching 80, the brain
should create parallel contribution subtasks:

```
Task enters REASONING:
  → Create subtask: "design_review" assigned to architect
  → Create subtask: "qa_test_definition" assigned to qa-engineer
  → Create subtask: "security_requirement" assigned to devsecops (if applicable)
  → Create subtask: "ux_spec" assigned to ux-designer (if UI)
```

This is not in the orchestrator code. The `fleet_contribute` MCP tool
doesn't exist either.

### Full Role-Specific Pre-Embed (AR-01)

Current pre-embed is functional but not per AR-01 spec:
- PM doesn't get Plane sprint data in pre-embed
- Workers don't get artifact completeness in pre-embed
- Contributors' input not included in worker task context

### Strategic Claude Call Configuration (Fleet-Elevation/23)

The orchestrator doesn't configure Claude calls per situation:
- Model selection (opus vs sonnet) per task complexity
- Effort level per urgency
- Session strategy (fresh vs compact vs continue)
- Max turns per situation

### Test Coverage

| File | Tests | Coverage |
|------|-------|---------|
| `test_orchestrator.py` | 20+ | Cycle steps, pre-checks, dispatch gates |
| `test_context_assembly.py` | 15+ | Task + heartbeat context building |
| `test_preembed.py` | 10+ | Data formatting |
| `test_role_providers.py` | 10+ | Per-role data |
| `test_change_detector.py` | 10+ | Change detection |
| `test_driver.py` | 10+ | Driver directives, products |
| **Total** | **75+** | Core logic covered. Missing: brain evaluation, contribution flow |
