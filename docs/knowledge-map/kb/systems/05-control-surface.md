# System 05: Control Surface — PO Command & Control

**Type:** Fleet System
**ID:** S05
**Files:** fleet_mode.py (99 lines), directives.py (90 lines)
**Total:** 189 lines
**Tests:** 35+

## What This System Does

Gives the PO real-time, fine-grained control over fleet behavior through three independent axes plus directives. All settings stored in OCMC board's `fleet_config` JSON field. Brain reads every cycle (~30s). No code changes needed — PO adjusts via OCMC interface.

PO requirement: "I have to be in charge and yet be able to let them work and then again be able to chose the mode of work"

## The Three Independent Axes

Any combination is valid. Axes are INDEPENDENT — changing one doesn't affect the others.

### Work Mode — Where work comes from

| Mode | Dispatch? | Plane Pull? | What It Means |
|------|-----------|-------------|---------------|
| `full-autonomous` | Yes | Yes | All agents active, PM pulls from Plane |
| `project-management-work` | Yes | No | PM drives work, no Plane pulling |
| `local-work-only` | Yes | No | OCMC tasks only (NOT "LocalAI" — means OCMC-local) |
| `finish-current-work` | No | No | No new dispatch, finish what's in progress |
| `work-paused` | No | No | Nothing runs (heartbeats continue for awareness) |

### Cycle Phase — What agents do

| Phase | Active Agents | Focus |
|-------|--------------|-------|
| `execution` | All | Normal work — all stages |
| `planning` | PM + Architect | Sprint planning, task breakdown |
| `analysis` | Architect + PM | Codebase analysis |
| `investigation` | Any assigned | Research, exploration |
| `review` | Fleet-ops only | Approval processing |
| `crisis-management` | Fleet-ops + DevSecOps | Incident response, security triage |

### Backend Mode — Which AI processes requests

| Mode | Backends Enabled |
|------|-----------------|
| `claude` | Claude Code only |
| `localai` | LocalAI only |
| `hybrid` | Both (router decides per task) |

Plus `budget_mode` (added this session): turbo/aggressive/standard/economic — controls fleet tempo (orchestrator cycle speed, heartbeat frequency).

## Directives — PO Commands to Agents

PO posts to board memory with tags:
```
content: "PM: start working on AICP Stage 1"
tags: ["directive", "to:project-manager", "from:human"]
```

- `directive` — identifies as directive (required)
- `to:{agent-name}` — target agent (optional, default = all)
- `from:human` — source (always human for PO)
- `urgent` — high priority flag
- `processed` — added after handling (prevents re-processing)

Orchestrator reads every cycle → routes to target agent's heartbeat context (DIRECTIVES section — highest priority in HEARTBEAT.md protocol).

## How State Flows

```
PO changes setting on OCMC board (fleet_config JSON)
  ↓ Brain reads GET /api/v1/boards/{id} every 30s
  ↓ fleet_mode.py:read_fleet_control(board_data) → FleetControlState
  ↓ Brain compares with previous state
  ↓ Changed? → emit fleet.system.mode_changed event → IRC notification
  ↓ Applied within same cycle:
    ├── work_mode → should_dispatch() gate
    ├── cycle_phase → get_active_agents_for_phase() filter
    ├── backend_mode → route_task() backend selection
    └── budget_mode → tempo_multiplier to cycle interval + CRONs
```

Latency: PO changes setting → brain picks up within 30s → agents see in next heartbeat (CRON interval, 30-90 min).

## Relationships

- READ BY: orchestrator.py every cycle (read_fleet_control)
- STORED IN: OCMC board fleet_config JSON field
- GATES: orchestrator dispatch (should_dispatch, should_pull_from_plane, get_active_agents_for_phase)
- CONSUMED BY: backend_router.py (backend_mode → which backends enabled)
- CONSUMED BY: budget_modes.py (budget_mode → tempo_multiplier)
- CONSUMED BY: preembed.py (fleet state injected into fleet-context.md Layer 6)
- EMITS: fleet.system.mode_changed event on any axis change
- CONNECTS TO: S07 orchestrator (reads state, applies gates)
- CONNECTS TO: S12 budget (budget_mode axis)
- CONNECTS TO: S14 router (backend_mode axis)
- CONNECTS TO: S18 notifications (mode changes → IRC)
- CONNECTS TO: fleet-context.md Layer 6 (agents see current fleet state)
- CONNECTS TO: HEARTBEAT.md Layer 8 (directives are HIGHEST priority)
- NOT YET IMPLEMENTED: frontend UI (FleetControlBar dropdowns), directive "processed" tagging reliability

## For LightRAG Entity Extraction

Key entities: FleetControlState (dataclass), work_mode (5 values), cycle_phase (6 values), backend_mode (3 values), budget_mode (4 values), Directive (tagged board memory).

Key relationships: PO SETS fleet_config. Orchestrator READS every cycle. Work_mode GATES dispatch. Cycle_phase FILTERS active agents. Backend_mode ROUTES to backends. Budget_mode CONTROLS tempo. Directives ROUTE to target agents. Mode changes EMIT events.
