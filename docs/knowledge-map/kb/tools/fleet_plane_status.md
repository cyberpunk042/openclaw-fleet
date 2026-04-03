# fleet_plane_status

**Type:** MCP Tool (Plane integration, read-only)
**System:** S08 (MCP Tools), S17 (Plane Integration)
**Module:** fleet/mcp/tools.py:1564-1622
**Stage gating:** None
**Requires:** Plane configured (PLANE_URL + PLANE_API_KEY). Returns `{plane_available: false}` if not.

## Purpose

Get Plane project overview: projects with their identifiers, active sprint name, and cycle counts. Used by PM during heartbeats to understand project state without making multiple Plane API calls. Can filter by project identifier or return all projects.

## Parameters

- `project` (string) — Project identifier to filter (AICP, OF, DSPD, NNRT). Empty = all projects.

## Chain Operations

```
fleet_plane_status(project)
├── CHECK: Plane configured? If not → {plane_available: false}
├── LOAD: plane.list_projects(workspace) → all projects
├── FILTER: if project specified, filter by identifier (uppercase match)
├── FOR EACH PROJECT:
│   ├── Get identifier, name
│   ├── plane.list_cycles(ws, project_id) → find "current" status
│   │   └── active_sprint = current cycle name (or None)
│   │   └── total_cycles = len(cycles)
│   └── Collect into proj_data list
└── RETURN: {plane_available: true, workspace, projects: [{identifier, name, active_sprint, total_cycles}]}
```

No events. No state changes. Read-only Plane data.

## Who Uses It

| Role | When | Why |
|------|------|-----|
| PM | Heartbeat | Quick project overview — which sprints are active across projects |
| Fleet-ops | Health monitoring | Verify Plane is responsive, projects exist |
| Any agent | Context gathering | Understand which projects are in the workspace |

## Relationships

- READS FROM: plane_client.py (list_projects, list_cycles)
- NO EVENTS: pure read
- COMPLEMENTS: fleet_plane_sprint (this = overview across projects; sprint = deep dive into one project's current sprint)
- CONNECTS TO: PM heartbeat protocol (check project state → decide on sprint actions)
- CONNECTS TO: fleet-plane skill (Plane management workflow)
- DATA NOTE: The code calls plane.list_cycles for "modules" (line 1605) — this appears to be a copy-paste from cycles. Modules (epics) are handled by fleet_plane_list_modules instead.
