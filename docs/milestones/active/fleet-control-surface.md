# Fleet Control Surface — User Command & Control

**Date:** 2026-03-30
**Status:** Design discussion — requirements capture
**Scope:** How the user controls the fleet, sees events, and sets operational modes

---

## User Vision (Verbatim)

> "I should be able to say go to the fleet / the project manager and tell
> him he can start working on the first priority. I should be able to Pause
> and even Stop and I should be able to see the stream of events and their
> impacts"

> "The idea is that I will say on the ocmc (Local Work Only | Project
> Management Work | Work Paused | Finish Current Work | ...) you need to
> give me the control and the view."

> "I can even chose a cycle and force being in planning or analysis or
> investigation or crisis management....."

> "I have to be in charge and yet be able to let them work and then again
> be able to chose the mode of work"

> "this doesn't change the job of the ops agent and the project manager
> and orchestrator but everything has to be adaptive. like the LocalAI
> Vs Claude Vs Hybrid modes"

---

## What This Means

The user needs a **command center** — not just a task board. A place where they:

1. **Set the fleet's operational mode** (what kind of work agents do)
2. **See the event stream** in real-time (what's happening, who's doing what)
3. **Control pace** (pause, resume, stop, finish current)
4. **Direct focus** (force a cycle: planning, analysis, investigation, crisis)
5. **Choose backend mode** (LocalAI only, Claude only, hybrid)
6. **Give directives** (tell PM to start priority X, tell fleet-ops to review Y)

And this control must be **adaptive** — it changes the orchestrator behavior,
agent heartbeat responses, dispatch rules, and effort profiles. But it
doesn't replace the PM or fleet-ops — they still do their jobs, just within
the mode the user set.

---

## Current State — What OCMC Already Offers

### Board Memory
- Agents read board memory every heartbeat
- `/pause` and `/resume` commands in board memory
- Board memory is the user's voice to the fleet

### Effort Profiles (fleet/core/effort_profiles.py)
Already built — 4 profiles:
- **full**: max 2 dispatch/cycle, opus + sonnet
- **conservative**: max 1 dispatch/cycle, sonnet only (current default)
- **minimal**: max 1 dispatch every 3 cycles, sonnet only
- **paused**: zero dispatch, agents respond HEARTBEAT_OK only

### Fleet Pause/Resume (fleet/cli/pause.py)
Already built:
- `fleet pause` — writes /pause to board memory, agents stop
- `fleet resume` — writes /resume, agents restart
- But: no granularity (all-or-nothing)

### Board Config Gates
MC supports:
- `require_review_before_done` — enforces review chain
- `comment_required_for_review` — forces reasoning
- `block_status_changes_with_pending_approval` — prevents skipping

---

## What's Missing — The Control Surface

### 1. Operational Modes (beyond pause/resume)

Current: `full | conservative | minimal | paused`

Proposed — richer mode system:

| Mode | Dispatch | Focus | Who Works |
|------|----------|-------|-----------|
| **Full Autonomous** | Max rate, all agents | All projects, all priorities | Everyone |
| **Project Management Work** | PM + fleet-ops only | Backlog, planning, sprint | PM, fleet-ops |
| **Local Work Only** | Conservative, no cloud | Only LocalAI-routable tasks | Agents on LocalAI |
| **Work Paused** | Zero dispatch | Nothing new | Agents idle (HEARTBEAT_OK) |
| **Finish Current Work** | No new dispatch | Agents complete in-progress only | Those with active tasks |
| **Planning Mode** | PM only | Sprint planning, backlog grooming | PM agent |
| **Analysis Mode** | Architect + PM | Architecture review, complexity assessment | Architect, PM |
| **Investigation Mode** | Any assigned | Spikes and research tasks only | Assigned agents |
| **Crisis Management** | fleet-ops + devsecops | Security, hotfix, incident response | Ops team |
| **Review Only** | fleet-ops | Process pending reviews, clear queue | fleet-ops |
| **Hybrid (LocalAI+Claude)** | Normal rate | Route by complexity | Everyone, mixed backends |
| **Claude Only** | Normal rate | All tasks use Claude | Everyone |
| **LocalAI Only** | Conservative | Only tasks LocalAI can handle | Everyone, local only |

Each mode affects:
- **Orchestrator dispatch**: which agents get tasks, how many per cycle
- **Agent heartbeat behavior**: what they do when they wake up
- **Backend routing**: LocalAI vs Claude vs both
- **Task filtering**: what types of tasks are eligible for dispatch

### 2. Event Stream (Real-Time Dashboard)

The user needs to SEE what's happening:

```
[20:15:32] 📋 orchestrator: dispatched "Assess AICP codebase" → architect
[20:15:33] 📡 chain: task_dispatch → INTERNAL ✓, CHANNEL ✓, PLANE ✓
[20:16:01] ✅ architect: accepted task, plan shared
[20:18:45] 💾 architect: committed 3 files (aicp/core/assessment.md)
[20:19:02] 🔀 architect: task complete, PR #47 created
[20:19:03] 📡 chain: task_complete → INTERNAL ✓, PUBLIC ✓, CHANNEL ✓, PLANE ✓, NOTIFY ✓
[20:19:05] 👀 fleet-ops: review task queued
[20:25:12] ✅ fleet-ops: approved (confidence: 92%)
[20:25:13] 📡 chain: task_approved → INTERNAL ✓, CHANNEL ✓, PLANE ✓
[20:25:14] 🏁 task done: "Assess AICP codebase"
```

This is already in the event store (.fleet-events.jsonl) — needs a viewer:
- **CLI**: `fleet watch` — tail events in terminal with colors
- **IRC**: events already post to #fleet
- **OCMC board memory**: decisions and completions recorded
- **Web dashboard**: if we build one (future)

### 3. Directives (User → Fleet Communication)

The user needs to give orders:
- "PM, start working on AICP Stage 1"
- "fleet-ops, review all pending approvals now"
- "All agents, stop and report status"
- "Architect, investigate the chain runner coverage gaps"

These should be:
- Written to board memory with special tags (`directive`, `urgent`)
- Picked up by the orchestrator or specific agent on next heartbeat
- Create tasks if needed (PM breaks down directives into tasks)

### 4. Mode Switching

How the user switches modes:

**Option A: Board Memory Commands**
```
/mode full-autonomous
/mode planning
/mode crisis-management
/mode local-only
/mode finish-current
```

**Option B: Fleet CLI**
```
fleet mode full
fleet mode planning
fleet mode crisis
fleet mode local-only
fleet mode finish
```

**Option C: OCMC Board Config**
Custom field on the board itself — `fleet_mode: planning`

**Option D: Config File**
`config/fleet.yaml` → `orchestrator.mode: planning`

All four should work. The source of truth is the board memory / config.
The CLI writes to it. The orchestrator reads it.

### 5. Cycle Forcing

> "I can even chose a cycle and force being in planning or analysis"

The user can force the fleet into a specific work cycle:
- **Sprint Planning**: PM creates tasks, estimates, assigns
- **Sprint Execution**: agents work on assigned tasks
- **Sprint Review**: fleet-ops reviews all completed work
- **Sprint Retrospective**: PM generates report, lessons learned
- **Investigation**: only spike/research tasks dispatched
- **Crisis**: only security/hotfix tasks, max priority

This overrides the orchestrator's normal cycle detection.

---

## Design: How Modes Affect the System

### Orchestrator Changes

The orchestrator reads the current mode before each cycle:

```python
async def run_orchestrator_cycle(mc, irc, board_id, config, ...):
    mode = await read_fleet_mode(mc, board_id)  # From board memory or config

    if mode == "paused":
        return  # Skip everything

    if mode == "finish-current":
        # Don't dispatch new tasks, but still process approvals/parents
        skip_dispatch = True

    if mode == "planning":
        # Only dispatch to PM, only planning-type tasks
        dispatch_filter = lambda t: t.custom_fields.task_type in ("epic", "story")
        dispatch_agents = ["project-manager"]

    if mode == "crisis":
        # Only security/hotfix, fleet-ops + devsecops
        dispatch_filter = lambda t: "security" in t.tags or "hotfix" in t.tags
        dispatch_agents = ["fleet-ops", "devsecops-expert"]

    if mode == "local-only":
        # Only tasks that can be routed to LocalAI
        backend_override = "localai"
```

### Agent Heartbeat Changes

Agents check the fleet mode in their heartbeat context:

```
HEARTBEAT — architect
Fleet Mode: PLANNING
  → You are in planning mode. Only architectural assessment
    and complexity evaluation tasks are active.
  → Do NOT start implementation work.
  → Focus: review task descriptions, assess complexity,
    recommend story point estimates.
```

### Backend Mode Changes

The mode can override the inference router:
- **LocalAI Only**: all agent sessions use LocalAI backend
- **Claude Only**: all sessions use Claude (current default)
- **Hybrid**: router decides per operation (Stage 2+ target)

### Event Stream Integration

Every mode change is an event:
```json
{
  "type": "fleet.system.mode_changed",
  "data": {
    "old_mode": "conservative",
    "new_mode": "planning",
    "set_by": "human",
    "reason": "Sprint 1 kickoff"
  }
}
```

Agents see this in their event feed and adjust behavior.

---

## Milestones

### M-CS01: Fleet Mode System

**Files:**
- `fleet/core/fleet_mode.py` (NEW) — mode definitions, read/write
- Update `fleet/cli/orchestrator.py` — read mode before each cycle
- Update `fleet/core/heartbeat_context.py` — include mode in bundle

Modes: full-autonomous, project-management, local-only, paused,
finish-current, planning, analysis, investigation, crisis, review-only

### M-CS02: Mode CLI Commands

**Files:**
- `fleet/cli/mode.py` (NEW) — `fleet mode <name>` command
- Update `fleet/__main__.py` — register mode command

Commands: `fleet mode list`, `fleet mode set <name>`, `fleet mode get`

### M-CS03: Event Stream Viewer

**Files:**
- `fleet/cli/watch.py` (NEW) — `fleet watch` command
- Real-time tail of event store with color formatting
- Filter by agent, type, priority
- Uses `fleet/core/event_display.py` for rendering

### M-CS04: Directives System

**Files:**
- `fleet/core/directives.py` (NEW) — directive model and routing
- Board memory integration for `/directive` commands
- Orchestrator picks up directives and routes to agents

### M-CS05: Orchestrator Mode Enforcement

**Files:**
- Update `fleet/cli/orchestrator.py` — mode-aware dispatch
- Dispatch filters per mode
- Agent allowlists per mode
- Backend override per mode

### M-CS06: Agent Mode Awareness

**Files:**
- Update `fleet/core/heartbeat_context.py` — mode in bundle
- Update agent HEARTBEAT.md templates — mode-specific instructions
- Agents adjust behavior based on fleet mode

### M-CS07: Backend Mode (LocalAI/Claude/Hybrid)

**Files:**
- Update `config/fleet.yaml` — backend_mode setting
- Integration with AICP inference router (when built)
- Gateway configuration for backend selection

### M-CS08: Board Memory Mode Commands

**Files:**
- Update orchestrator to read `/mode` commands from board memory
- `/mode planning` in board memory → mode changes
- `/directive PM: start AICP Stage 1` → PM gets directive

### M-CS09: OCMC Dashboard Integration

**Files:**
- Board custom field: `fleet_mode` on the board itself
- Visible in MC UI
- Editable by human → orchestrator reads and applies

### M-CS10: Cycle Forcing

**Files:**
- `fleet/core/cycle_mode.py` (NEW) — sprint phase enforcement
- Phases: planning, execution, review, retrospective, investigation, crisis
- Overrides normal orchestrator behavior

---

## Priority Order

1. **M-CS01** — Mode system (foundation for everything)
2. **M-CS02** — CLI commands (user can set modes)
3. **M-CS05** — Orchestrator enforcement (modes actually work)
4. **M-CS03** — Event stream viewer (user sees what's happening)
5. **M-CS06** — Agent awareness (agents adapt to mode)
6. **M-CS04** — Directives (user gives orders)
7. **M-CS08** — Board memory commands (natural language control)
8. **M-CS09** — OCMC dashboard (visual control)
9. **M-CS07** — Backend mode (LocalAI/Claude/Hybrid)
10. **M-CS10** — Cycle forcing (sprint phases)

---

## How It All Connects

```
User sets mode (CLI / board memory / OCMC dashboard)
    ↓
Fleet mode stored (board memory + config)
    ↓
Orchestrator reads mode before each cycle
    ├── Filters which tasks to dispatch
    ├── Filters which agents are active
    ├── Sets backend preference
    └── Adjusts dispatch rate
    ↓
Agent heartbeat includes mode
    ├── Agent adjusts behavior
    ├── Agent knows what's expected
    └── Agent responds appropriately
    ↓
Event stream shows impact
    ├── Mode change event
    ├── Dispatch events (filtered by mode)
    ├── Agent responses
    └── User sees the flow in real-time
```

The user is ALWAYS in control. The mode system is the throttle and steering.
The orchestrator is the engine. The agents are the wheels.
Fleet-ops and PM still do their jobs — but within the mode the user set.

---

## Interaction Examples

### "Start working on AICP Stage 1"

```
User: fleet mode set full-autonomous
User: fleet directive "PM, break down AICP Stage 1 into tasks and start dispatching"

→ Directive written to board memory
→ PM's next heartbeat includes the directive
→ PM reads AICP Stage 1 epic details from Plane
→ PM creates tasks via fleet_task_create
→ Orchestrator dispatches tasks to agents
→ Event stream shows the flow
```

### "Pause everything, let me think"

```
User: fleet mode set paused

→ Mode change event emitted
→ Orchestrator stops dispatching
→ Agents on next heartbeat see "Fleet Mode: PAUSED"
→ Agents respond HEARTBEAT_OK, do nothing
→ Event stream: "[mode] Fleet paused by human"
```

### "We have a security issue"

```
User: fleet mode set crisis

→ Only fleet-ops and devsecops-expert active
→ Only security-tagged tasks dispatched
→ Other agents idle
→ Event stream: "[crisis] Security mode activated"
→ devsecops runs security audit
→ fleet-ops reviews findings
```

### "Just finish what you're doing"

```
User: fleet mode set finish-current

→ No new tasks dispatched
→ Agents with in-progress tasks continue
→ Agents with no tasks idle
→ Once all in-progress tasks complete → fleet effectively paused
→ Event stream shows each task completing
```