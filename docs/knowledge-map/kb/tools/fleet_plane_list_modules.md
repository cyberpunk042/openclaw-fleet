# fleet_plane_list_modules

**Type:** MCP Tool (Plane integration, read-only)
**System:** S08 (MCP Tools), S17 (Plane Integration)
**Module:** fleet/mcp/tools.py:2004-2044
**Stage gating:** None
**Requires:** Plane configured

## Purpose

List modules (epics) in a Plane project with their name, description, status, total issues, and completed issues. Modules in Plane CE represent epic-level work groupings — the high-level view of project organization.

## Parameters

- `project` (string, default "AICP") — Project identifier

## Chain Operations

```
fleet_plane_list_modules(project)
├── CHECK: Plane configured?
├── RESOLVE PROJECT: plane.list_projects(ws) → find by identifier
├── GET MODULES: GET /api/v1/workspaces/{ws}/projects/{id}/modules/
│   └── Direct API call (not via plane_client method — uses raw _client.get)
├── FOR EACH MODULE:
│   ├── id
│   ├── name
│   ├── description[:100] (truncated)
│   ├── status
│   ├── total_issues
│   └── completed_issues
└── RETURN: {project, modules: [{id, name, description, status, total_issues, completed_issues}]}
```

## Who Uses It

| Role | When | Why |
|------|------|-----|
| PM | Sprint planning | See epic-level breakdown, decide which module to focus sprint on |
| Architect | Architecture review | View modules for complexity assessment across epics |
| Fleet-ops | Status reporting | Module progress for stakeholder reports |

## Relationships

- READS FROM: Plane API (modules endpoint — direct HTTP, not plane_client method)
- NO EVENTS: pure read
- CONNECTS TO: fleet_plane_create_issue (issues can be added to modules via module parameter)
- CONNECTS TO: PM heartbeat (module awareness for sprint planning)
- CONNECTS TO: fleet-plane skill (module management as part of Plane workflow)
- NOTE: This uses raw `plane._client.get()` instead of a typed plane_client method. The plane_client.py doesn't have a `list_modules()` method — this is direct API access.
