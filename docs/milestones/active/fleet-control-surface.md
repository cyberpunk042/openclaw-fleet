# Fleet Control Surface — User Command & Control

**Date:** 2026-03-30
**Status:** Design — grounded in MC vendor analysis
**Scope:** How the user controls the fleet through the OCMC UI

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

The fleet control surface lives in the **header bar** — the sticky navbar
at the top of every OCMC page. Always visible. Always accessible. The user
doesn't navigate to a separate page or open a panel. The controls are RIGHT
THERE in the header, on every page, at all times.

Three **independent** control axes as compact dropdowns in the header:

1. **Work Mode** — where new work comes from
2. **Cycle Phase** — what kind of work agents do
3. **Backend Mode** — which AI backend processes requests

These axes are independent. Any combination is valid. Setting one does not
affect the others.
6. **Directives** — the user types a command to an agent or the fleet

---

## Three Control Axes

### Axis 1 — Work Mode (where does new work come from?)

| Value | What It Means |
|-------|---------------|
| **Full Autonomous** | Everything open. PM pulls from Plane, orchestrator dispatches freely, all agents work. |
| **Project Management Work** | PM is active on Plane. Pulls priorities, creates tasks, drives sprints. |
| **Local Work Only** | Agents work on OCMC tasks only. PM does NOT pull new work from Plane. Plane sync still runs — always. |
| **Finish Current Work** | No new dispatch. Agents with in-progress tasks finish them. Then idle. |
| **Work Paused** | No new dispatch. Agents idle. Nothing moves. |

**Key clarification:** "Local Work Only" means local to the OCMC board —
work that's already on the board. It does NOT mean LocalAI. It does NOT
disable Plane sync. Plane sync is infrastructure; it always runs.

### Axis 2 — Cycle Phase (what kind of work?)

| Value | What It Means |
|-------|---------------|
| **Execution** | Normal work. Agents implement, build, test. Default. |
| **Planning** | Sprint planning, backlog grooming, task breakdown. PM drives. |
| **Analysis** | Architecture review, complexity assessment. Architect + PM active. |
| **Investigation** | Spikes, research, exploration tasks only. |
| **Review** | Clear the review queue. fleet-ops processes pending approvals. |
| **Crisis Management** | Security incidents, hotfixes. fleet-ops + devsecops only. |

### Axis 3 — Backend Mode (which AI?)

| Value | What It Means |
|-------|---------------|
| **Claude** | All inference through Claude. Current default. |
| **LocalAI** | All inference through LocalAI. Zero Claude tokens. |
| **Hybrid** | Router decides per operation by complexity. Stage 2+ target. |

---

## How Each Axis Affects the System

### Work Mode Effects

| Mode | Dispatch | PM Plane Pull | Plane Sync | Who Works |
|------|----------|--------------|------------|-----------|
| Full Autonomous | Max rate | Yes | Always | Everyone |
| Project Management Work | PM + fleet-ops | Yes | Always | PM, fleet-ops |
| Local Work Only | Conservative | No | Always | Everyone (OCMC tasks only) |
| Finish Current Work | Zero new | No | Always | Those with active tasks |
| Work Paused | Zero | No | Always | Nobody |

### Cycle Phase Effects

| Phase | Task Filter | Active Agents | Focus |
|-------|------------|---------------|-------|
| Execution | All types | Everyone | Normal work |
| Planning | epic, story only | PM, architect | Sprint planning |
| Analysis | assessment, spike | Architect, PM | Architecture review |
| Investigation | spike, research | Assigned agents | Research only |
| Review | review-tagged | fleet-ops | Clear approval queue |
| Crisis Management | security, hotfix | fleet-ops, devsecops | Incident response |

### Backend Mode Effects

| Mode | Inference Route | Model Selection |
|------|----------------|-----------------|
| Claude | All through Claude API | opus/sonnet by complexity |
| LocalAI | All through LocalAI | hermes-3b/hermes-7b by task |
| Hybrid | Router decides per op | Mixed based on complexity |

---

## The UI — Injected Into the MC Header Bar

### Where: `DashboardShell.tsx` — The Sticky Header

The header bar (`DashboardShell.tsx`) is a sticky `<header>` at the top of
every page. It currently has three sections:

```
+------------------------------------------------------------------------+
| [OC] OPENCLAW     | [Org Switcher ▾]              | User Name  [Avatar]|
|  Mission Control  |                                | Operator           |
+------------------------------------------------------------------------+
```

The **center section** uses `flex-1` (takes all remaining space) but only
contains the OrgSwitcher at 220px. The rest of the space is empty.

The fleet controls go IN that center section, right after the OrgSwitcher.

### Header With Fleet Controls

```
+--------------------------------------------------------------------------------------------+
| [OC] OPENCLAW  | [Org ▾] [Local Work Only ▾] [Planning ▾] [Claude ▾] [8/10] | User [Avatar]|
|  Mission Control|                                                             | Operator     |
+--------------------------------------------------------------------------------------------+
```

Three compact `Select` dropdowns + an agent count badge. Always visible.
On every page. No navigation needed. The user glances at the header and
sees the fleet state. Clicks a dropdown and changes it instantly.

### Responsive Behavior

- **Desktop (md+):** All three dropdowns visible alongside OrgSwitcher
- **Tablet (sm-md):** Dropdowns collapse to icons with tooltips, or a
  single "Fleet" popover that expands to show all three
- **Mobile:** Hidden (same as OrgSwitcher — `hidden md:flex`)

### Component Structure

New component: `FleetControlBar.tsx`

Injected into `DashboardShell.tsx` center section, after OrgSwitcher:

```tsx
{/* CENTER SECTION */}
<SignedIn>
  <div className="hidden md:flex flex-1 items-center gap-3">
    <div className="max-w-[220px]">
      <OrgSwitcher />
    </div>
    {/* Fleet controls — injected here */}
    <FleetControlBar boardId={activeBoardId} />
  </div>
</SignedIn>
```

`FleetControlBar` renders:
- Work Mode `Select` (compact, ~160px)
- Cycle Phase `Select` (compact, ~130px)
- Backend Mode `Select` (compact, ~110px)
- Agent status badge (e.g., "8/10" with green/amber dot)

### UI Components Used

All from existing MC component library — no new dependencies:

| Control | Component | Source |
|---------|-----------|--------|
| Work Mode dropdown | `Select` (Radix) | `components/ui/select.tsx` |
| Cycle Phase dropdown | `Select` (Radix) | `components/ui/select.tsx` |
| Backend Mode dropdown | `Select` (Radix) | `components/ui/select.tsx` |
| Agent count badge | Custom span | Tailwind + StatusDot atom |

### Dropdown Styling

Compact header-friendly styling (smaller than board edit dropdowns):

```tsx
<Select value={workMode} onValueChange={handleWorkModeChange}>
  <SelectTrigger className="h-8 w-[160px] rounded-md border-slate-200 bg-white
    px-2 text-xs font-medium text-slate-700 shadow-none">
    <SelectValue />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="full-autonomous">Full Autonomous</SelectItem>
    <SelectItem value="project-management-work">PM Work</SelectItem>
    <SelectItem value="local-work-only">Local Work Only</SelectItem>
    <SelectItem value="finish-current-work">Finish Current</SelectItem>
    <SelectItem value="work-paused">Work Paused</SelectItem>
  </SelectContent>
</Select>
```

Height `h-8` (32px) to fit the header. Text `text-xs` for compactness.
Matching `border-slate-200` style of OrgSwitcher.

### Real-Time State

The `FleetControlBar` component:
- Fetches current fleet_config from the board snapshot on mount
- On dropdown change → PATCHes the board's `fleet_config` field
- Subscribes to board memory SSE stream for external state changes
  (e.g., if orchestrator or another tool changes the mode)
- Updates local state when SSE delivers a mode change event

### State Flow

```
User clicks "Planning" in Cycle Phase dropdown
  → Component calls: PATCH /api/v1/boards/{boardId}
    { "fleet_config": { ...current, "cycle_phase": "planning" } }
  → Board updated in MC database
  → SSE stream emits board update event
  → FleetControlBar confirms new state
  → Orchestrator reads fleet_config on next 30s cycle
  → Orchestrator adjusts dispatch behavior
  → Agent heartbeats include new phase context
```

---

## Storage — Where Fleet Control State Lives

**State** is stored in a `fleet_config` JSON field on the Board model.
The header dropdowns read and write this field via the standard PATCH API.

**Events** (mode changes, directives) are posted to board memory so
agents see them in their context and the activity feed shows them.

Clean separation: board config = current state, board memory = communication.

---

## Backend Changes (MC Vendor Patches)

### Patch 0004: Fleet Config on Board Model

**Files modified:**
- `backend/app/models/boards.py` — add `fleet_config: JSON` column
- `backend/app/schemas/boards.py` — add `fleet_config` to BoardRead/BoardUpdate
- `backend/app/api/boards.py` — pass through on PATCH
- Alembic migration — add column

The `fleet_config` field is a JSON column with this schema:

```json
{
  "work_mode": "full-autonomous",
  "cycle_phase": "execution",
  "backend_mode": "claude",
  "updated_at": "2026-03-30T20:15:32Z",
  "updated_by": "human"
}
```

Default value: `{"work_mode": "full-autonomous", "cycle_phase": "execution", "backend_mode": "claude"}`

The PATCH endpoint already handles partial updates. The UI sends:
```
PATCH /api/v1/boards/{boardId}
{ "fleet_config": { "work_mode": "planning", ... } }
```

### Patch 0005: Fleet Events SSE Endpoint (optional, future)

A dedicated SSE endpoint for fleet events (beyond task/memory/agent streams).
Not required for v1 — the existing streams cover what's needed.

---

## Frontend Changes (MC Vendor)

### New Files

| File | Purpose |
|------|---------|
| `src/components/fleet-control/FleetControlBar.tsx` | 3 dropdowns + agent badge, lives in header |

### Modified Files

| File | Change |
|------|--------|
| `src/components/templates/DashboardShell.tsx` | Import and render `FleetControlBar` in center section of header |

### Header Injection

In `DashboardShell.tsx`, the center section currently has only the OrgSwitcher.
`FleetControlBar` is added right after it:

```tsx
<SignedIn>
  <div className="hidden md:flex flex-1 items-center gap-3">
    <div className="max-w-[220px]">
      <OrgSwitcher />
    </div>
    <FleetControlBar boardId={activeBoardId} />
  </div>
</SignedIn>
```

---

## Orchestrator Integration

### How the Orchestrator Reads Fleet Control State

The orchestrator already runs every 30s. Before each cycle, it reads
the fleet control state from the board config:

```python
async def read_fleet_control(mc, board_id: str) -> FleetControlState:
    """Read fleet control state from board config."""
    board = await mc.get_board(board_id)
    config = board.fleet_config or {}
    return FleetControlState(
        work_mode=config.get("work_mode", "full-autonomous"),
        cycle_phase=config.get("cycle_phase", "execution"),
        backend_mode=config.get("backend_mode", "claude"),
    )
```

### How Each Axis Affects the Orchestrator Cycle

```python
async def run_orchestrator_cycle(mc, irc, board_id, config, ...):
    state = await read_fleet_control(mc, board_id)

    # ── Work Mode ────────────────────────────────────
    if state.work_mode == "work-paused":
        return  # Skip everything

    if state.work_mode == "finish-current":
        skip_dispatch = True  # Don't dispatch new tasks

    if state.work_mode == "local-work-only":
        pm_plane_pull = False  # PM doesn't pull from Plane

    if state.work_mode == "project-management-work":
        dispatch_agents = ["project-manager", "fleet-ops"]

    # ── Cycle Phase ──────────────────────────────────
    if state.cycle_phase == "planning":
        dispatch_filter = lambda t: t.task_type in ("epic", "story")
        active_agents = ["project-manager", "architect"]

    if state.cycle_phase == "crisis-management":
        dispatch_filter = lambda t: "security" in t.tags or "hotfix" in t.tags
        active_agents = ["fleet-ops", "devsecops-expert"]

    if state.cycle_phase == "review":
        active_agents = ["fleet-ops"]
        # Only process approvals, no new dispatch

    # ── Backend Mode ─────────────────────────────────
    if state.backend_mode == "localai":
        backend_override = "localai"
    elif state.backend_mode == "hybrid":
        backend_override = "hybrid"
    # else: claude (default, no override needed)
```

### Agent Heartbeat Context

Agents see the current fleet control state in their heartbeat bundle:

```
HEARTBEAT — architect
Fleet Control:
  Work Mode: Local Work Only
  Cycle Phase: Analysis
  Backend: Claude
  → Focus on architecture assessment. Do not start implementation.
  → Work from OCMC tasks only. PM is not pulling new Plane work.
```

---

## Directives

The directive input lets the user send a message to a specific agent or
the entire fleet:

- User selects target: `PM`, `fleet-ops`, `all`, or any agent name
- User types message: "Start working on AICP Stage 1"
- UI posts to board memory with tags: `["directive", "to:{agent}", "from:human"]`
- Orchestrator reads directives on next cycle
- If directed to PM → creates a task for PM with the directive content
- If directed to all → writes to board memory, all agents see it

Directive posting uses the existing board memory API:

```
POST /api/v1/boards/{boardId}/memory
{
  "content": "PM: Start working on AICP Stage 1",
  "tags": ["directive", "to:project-manager", "from:human", "urgent"],
  "source": "human"
}
```

No new backend endpoint needed. The orchestrator already reads board memory.

---

## Event Stream

The event stream section shows real-time fleet activity. Sources:

1. **Task stream** — dispatches, completions, status changes
2. **Memory stream** — directives, alerts, mode changes
3. **Agent stream** — online/offline, heartbeats

Rendering follows the existing Activity page pattern:
- SSE connection via `Response.body.getReader()`
- Exponential backoff with jitter for reconnection
- `usePageActive()` to pause when tab not visible
- Staggered connections (120ms spacing)
- Deduplication via seen-IDs ref
- Auto-scroll with manual override

Event format in the stream:

```
[20:15:32] dispatched "Assess AICP" → architect
[20:16:01] architect accepted task, plan shared
[20:18:45] architect committed 3 files
[20:19:02] architect task complete, PR #47
[20:19:05] fleet-ops review queued
[20:25:12] fleet-ops approved (92%)
[20:25:14] done: "Assess AICP codebase"
[20:30:00] MODE CHANGED: Work Mode → Planning (by human)
[20:30:01] DIRECTIVE: PM — start AICP Stage 1
```

Color-coded by type: dispatches (blue), completions (green), approvals
(emerald), mode changes (amber), directives (purple), errors (red).

---

## Current State — What Already Exists

### Already Built

| Component | Status | Location |
|-----------|--------|----------|
| Budget mode (tempo) | Built | `fleet/core/budget_modes.py` |
| Fleet pause/resume | Built | `fleet/cli/pause.py` |
| Board memory read/write | Built | `fleet/infra/mc_client.py` |
| Agent heartbeat context | Built | `fleet/core/heartbeat_context.py` |
| Event store | Built | `fleet/core/events.py` |
| Event router | Built | `fleet/core/event_router.py` |
| Chain runner | Built | `fleet/core/chain_runner.py` |
| SSE streams in MC | Built | MC vendor (tasks, memory, agents, approvals) |
| Board config gates | Built | MC board model (approval toggles) |
| Orchestrator daemon | Built | `fleet/cli/orchestrator.py` |

### Not Built Yet

| Component | What's Needed |
|-----------|---------------|
| Fleet control bar in header | FleetControlBar component in DashboardShell header |
| Fleet config on board | Backend patch (JSON field + migration) |
| Fleet mode reader | Python function in orchestrator |
| Mode-aware dispatch | Orchestrator reads state, filters dispatch |
| Mode-aware heartbeats | Include fleet state in heartbeat bundle |
| Directive routing | Orchestrator reads directives from board memory |
| Event stream viewer | Frontend component consuming SSE |

---

## Milestones

### M-CS01: Backend — Fleet Config on Board Model

**Patch 0004** to MC vendor:
- Add `fleet_config` JSON column to Board model
- Add to BoardRead/BoardUpdate schemas
- Alembic migration
- Default: `{"work_mode": "full-autonomous", "cycle_phase": "execution", "backend_mode": "claude"}`
- PATCH endpoint passes through

**Files:**
- `vendor/openclaw-mission-control/backend/app/models/boards.py`
- `vendor/openclaw-mission-control/backend/app/schemas/boards.py`
- `vendor/openclaw-mission-control/backend/alembic/versions/xxxx_add_fleet_config.py`
- `patches/0004-fleet-config-board-model.patch`

### M-CS02: Frontend — FleetControlBar in Header

Create `FleetControlBar` component and inject into `DashboardShell` header:
- 3 compact Radix `Select` dropdowns (Work Mode, Cycle Phase, Backend)
- Agent count badge with status dot
- Fetches board fleet_config on mount
- PATCHes board on dropdown change
- Responsive: `hidden md:flex`, compact `h-8 text-xs` styling

**Files:**
- `vendor/openclaw-mission-control/frontend/src/components/fleet-control/FleetControlBar.tsx` (NEW)
- `vendor/openclaw-mission-control/frontend/src/components/templates/DashboardShell.tsx` (MODIFY)

### M-CS06: Fleet — Fleet Control State Reader

Python module for reading fleet control state:
- `FleetControlState` dataclass (work_mode, cycle_phase, backend_mode)
- `read_fleet_control(mc, board_id)` function
- Parses board fleet_config JSON

**Files:**
- `fleet/core/fleet_mode.py` (NEW)

### M-CS07: Fleet — Mode-Aware Orchestrator

Orchestrator reads fleet control state before each cycle:
- Work mode → controls dispatch and PM Plane pull
- Cycle phase → filters task types and active agents
- Backend mode → overrides inference backend
- Every mode change emits a CloudEvent

**Files:**
- `fleet/cli/orchestrator.py` (MODIFY)

### M-CS08: Fleet — Mode-Aware Heartbeats

Include fleet control state in agent heartbeat context:
- Agents see current mode, phase, backend
- Mode-specific instructions per agent role
- Agents adjust behavior accordingly

**Files:**
- `fleet/core/heartbeat_context.py` (MODIFY)

### M-CS09: Fleet — Directive Processing

Orchestrator reads directives from board memory:
- Scans for `directive` tagged entries since last cycle
- Routes to target agent (creates task or posts to memory)
- Marks directive as processed

**Files:**
- `fleet/core/directives.py` (NEW)
- `fleet/cli/orchestrator.py` (MODIFY)

### M-CS10: Fleet — Mode Change Events

Every mode change emits a CloudEvent:
- `fleet.system.mode_changed` with old/new values
- Chain runner publishes to all surfaces
- IRC notification
- Board memory log entry

**Files:**
- `fleet/core/events.py` (MODIFY)
- `fleet/core/chain_runner.py` (MODIFY)

---

## Priority Order

1. **M-CS01** — Backend patch (foundation — header dropdowns need the field)
2. **M-CS02** — FleetControlBar in header (user can see and set modes)
3. **M-CS06** — State reader (orchestrator can consume modes)
4. **M-CS07** — Mode-aware orchestrator (modes actually work)
5. **M-CS08** — Mode-aware heartbeats (agents adapt to mode)
6. **M-CS09** — Directive processing (orders get routed)
7. **M-CS10** — Mode change events (full event chain)

---

## How It All Connects

```
User opens any OCMC page → header shows fleet controls
    ↓
User selects Work Mode: "Local Work Only" from dropdown
    ↓
UI PATCHes board: fleet_config.work_mode = "local-work-only"
    ↓
Mode change event emitted → event stream shows it
    ↓
Orchestrator next cycle (30s) reads fleet_config
    ├── PM: do NOT pull new work from Plane
    ├── Dispatch: only OCMC board tasks
    ├── Plane sync: still running (always)
    └── Agents: informed via heartbeat context
    ↓
User sees the impact in the event stream:
    "Mode changed: Local Work Only"
    "PM: acknowledging local-only mode"
    "architect: continuing task #38 (already in progress)"
    ↓
User types directive: "PM: prioritize the CI/CD tasks"
    ↓
UI posts to board memory: tags=["directive", "to:project-manager"]
    ↓
Orchestrator reads directive → creates task for PM
    ↓
PM heartbeat → sees directive → evaluates and acts
    ↓
Event stream shows the flow in real-time
```

The user is ALWAYS in control. The UI is the steering wheel.
The orchestrator is the engine. The agents are the wheels.
PM and fleet-ops still do their jobs — within the mode the user set.
Plane sync always runs. Backend mode is independent of work mode.

---

## Beyond the Control Surface — Three Systems UI

The control surface (fleet mode dropdowns in the header) is the first
UI injection into the OCMC vendor frontend. After the three systems
are built (immune system, teaching system, methodology system), the
OCMC UI is extended further to surface their activities and reporting:

- **Immune system activity** — doctor actions visible, agent health
  indicators, intervention history
- **Teaching system activity** — active lessons, comprehension status,
  lesson effectiveness
- **Methodology system** — task stages, protocol compliance, readiness
  percentage editable by PO
- **Reporting dashboard** — fleet health overview, disease trends,
  methodology compliance rates
- **Event stream** — immune/teaching/methodology events alongside
  existing task/agent events, color-coded by system

These are the G milestones in the milestone plan
(`milestone-plan-three-systems.md`). They extend the same approach —
inject new components into the MC vendor Next.js app using the existing
Radix UI + Tailwind component library and SSE streams.