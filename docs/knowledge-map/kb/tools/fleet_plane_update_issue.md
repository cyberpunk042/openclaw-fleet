# fleet_plane_update_issue

**Type:** MCP Tool (Plane integration)
**System:** S08 (MCP Tools), S17 (Plane Integration)
**Module:** fleet/mcp/tools.py:1942-2002
**Stage gating:** None
**Requires:** Plane configured

## Purpose

Update a Plane issue — change state, priority, or assignment. Used by PM to keep Plane in sync when OCMC tasks change, or by the sync worker for automated bidirectional propagation. Resolves state NAMES to UUIDs via the Plane states API (Plane uses UUIDs internally, not string names).

## Parameters

- `project` (string, required) — Project identifier (AICP, OF, DSPD, NNRT)
- `issue_id` (string, required) — Plane issue UUID
- `state` (string) — New state NAME (e.g., "In Progress", "Done"). Resolved to UUID. Empty = no change.
- `priority` (string) — New priority (urgent/high/medium/low/none). Empty = no change.
- `assignee` (string) — Agent email. Empty = no change.
- `labels` (string) — Comma-separated label names to SET. Empty = no change.

## Chain Operations

```
fleet_plane_update_issue(project, issue_id, state, priority, ...)
├── CHECK: Plane configured?
├── RESOLVE PROJECT: plane.list_projects(ws) → find by identifier
├── BUILD PATCH: only changed fields
│   ├── state → plane.list_states(ws, project_id) → match name (case-insensitive) → UUID
│   └── priority → direct string value
├── UPDATE: plane.update_issue(ws, project_id, issue_id, state_id, priority)
└── RETURN: {project, issue_id, updated: ["state=Done", "priority=high"]}
```

No IRC notification. No event emission. Lightweight — caller handles notifications.

## Who Uses It

| Role | When | Why |
|------|------|-----|
| PM | OCMC task status changes | Keep Plane in sync |
| Sync worker | Automated sync | plane_sync.py pushes: OCMC done → Plane "Done" |
| Fleet-ops | After approval | Plane issue → "Done" |

## State Resolution

Plane CE uses UUID state IDs. Tool resolves by calling `plane.list_states()` and matching `state.name.lower()`. Common states: Backlog, Unstarted, In Progress, In Review, Done, Cancelled.

## Relationships

- READS: plane.list_states (name → UUID resolution)
- UPDATES: Plane issue via API
- CALLED BY: plane_sync.py (push completions), PM workflow, fleet_task_complete event chain (PLANE surface)
- CONNECTS TO: fleet_plane_comment (comments accompany state updates)
- CONNECTS TO: plane_methodology.py (stage:/readiness: labels managed separately by sync, not this tool)
- BIDIRECTIONAL: plane_sync.py reads Plane changes AND pushes OCMC changes. This tool is the push mechanism.
