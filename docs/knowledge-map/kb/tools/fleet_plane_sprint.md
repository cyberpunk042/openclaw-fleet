# fleet_plane_sprint

**Type:** MCP Tool (Plane integration, read-only)
**System:** S08 (MCP Tools), S17 (Plane Integration)
**Module:** fleet/mcp/tools.py:1624-1675
**Stage gating:** None
**Requires:** Plane configured

## Purpose

Get current sprint details for a specific project: sprint name, status, dates, issue counts, and priority breakdown. Deep dive into one project's active sprint — complements fleet_plane_status which gives a multi-project overview.

Falls back to the most recent cycle if no "current" status cycle exists.

## Parameters

- `project` (string, default "AICP") — Project identifier

## Chain Operations

```
fleet_plane_sprint(project)
├── CHECK: Plane configured?
├── RESOLVE PROJECT: plane.list_projects(ws) → find by identifier (uppercase)
│   └── Not found → {error: "Project {project} not found in Plane"}
├── GET CYCLES: plane.list_cycles(ws, project_id)
│   ├── Find cycle with status="current"
│   └── Fallback: most recent cycle (cycles[0]) if no current
├── BUILD SPRINT DATA: name, status, start_date, end_date
├── GET ISSUES: plane.list_issues(ws, project_id) → total count
├── PRIORITY BREAKDOWN: group issues by priority → {urgent: N, high: N, medium: N, low: N}
└── RETURN: {plane_available, project, sprint: {name, status, dates},
            total_issues, by_priority: {urgent, high, medium, low}}
```

## Who Uses It

| Role | When | Why |
|------|------|-----|
| PM | Every heartbeat | Sprint progress awareness — issues remaining, priority distribution |
| PM | Sprint planning | Check current sprint state before planning next |
| Fleet-ops | Sprint boundary | Sprint status for reports |

## Relationships

- READS FROM: plane_client.py (list_projects, list_cycles, list_issues)
- NO EVENTS: pure read
- COMPLEMENTS: fleet_plane_status (overview) → this (sprint detail)
- FEEDS: PM heartbeat (sprint awareness injected into fleet-context.md)
- CONNECTS TO: fleet-sprint skill (sprint lifecycle management)
- CONNECTS TO: velocity.py (sprint velocity tracking — SP completed, cycle time)
- CONNECTS TO: pm_provider in role_providers.py (sprint progress for PM pre-embed)
- DATA NOTE: Issues are fetched without sprint/cycle filter — returns ALL project issues, not just sprint-specific. The by_priority breakdown is project-wide. This may need refinement to filter by current cycle.
