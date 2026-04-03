# fleet_plane_sync

**Type:** MCP Tool (Plane integration, bidirectional sync)
**System:** S08 (MCP Tools), S17 (Plane Integration)
**Module:** fleet/mcp/tools.py:1677-1727
**Stage gating:** None
**Requires:** Plane configured

## Purpose

Trigger bidirectional Plane ↔ OCMC sync. Three directions: "in" (Plane→OCMC — discovers new Plane issues, creates OCMC tasks), "out" (OCMC→Plane — pushes completed tasks back to Plane as "Done"), or "both" (full bidirectional). Uses PlaneSyncer from plane_sync.py which handles the actual sync logic.

This is typically called by PM during sprint management or by the sync daemon automatically. The tool wraps PlaneSyncer and returns counts of what was created/updated/skipped/errored.

## Parameters

- `direction` (string, default "both") — "in" (Plane→OCMC), "out" (OCMC→Plane), or "both"

## Chain Operations

```
fleet_plane_sync(direction)
├── CHECK: Plane configured?
├── RESOLVE: plane.list_projects(ws) → get all project IDs
├── CREATE SYNCER: PlaneSyncer(mc, plane, board_id, workspace_slug, project_ids)
├── IF direction in ("in", "both"):
│   ├── syncer.ingest_from_plane()
│   │   ├── For each project: list Plane issues
│   │   ├── For each issue NOT already linked to OCMC task:
│   │   │   ├── Create OCMC task with custom_fields:
│   │   │   │   plane_issue_id, plane_project_id, plane_workspace
│   │   │   ├── Copy: title, description, priority
│   │   │   └── Set: source tags ["source:plane", "project:{name}"]
│   │   └── Return: IngestResult(created=[], skipped_count, errors)
│   └── result["ingest"] = {created: N, skipped: N, errors: [...]}
├── IF direction in ("out", "both"):
│   ├── syncer.push_completions_to_plane()
│   │   ├── Find OCMC tasks with status="done" AND plane_issue_id set
│   │   ├── For each: update Plane issue state → "Done"
│   │   ├── Post completion comment on Plane issue
│   │   └── Return: PushResult(updated=[], skipped=[], errors)
│   └── result["push"] = {updated: N, skipped: N, errors: [...]}
└── RETURN: {direction, ingest: {...}, push: {...}}
```

## The Two-Level Task Model

This sync operates in the context of the fleet's two-level task model:

```
Plane (PO surface)          OCMC (Agent surface)
  Issue: "Add auth"    →    PM Task: "Add auth" (linked via plane_issue_id)
                             ├── Architect: design_input (contribution)
                             ├── QA: qa_test_definition (contribution)
                             ├── DevSecOps: security_req (contribution)
                             ├── Engineer: implementation (work task)
                             ├── Fleet-ops: review (approval)
                             └── Writer: documentation (follow-up)
```

PM selects Plane issues → this tool creates OCMC PM tasks → PM creates 10-20+ ops tasks.
Ops tasks complete → PM task completes → this tool pushes "Done" back to Plane.

## Who Uses It

| Role | Direction | When |
|------|-----------|------|
| PM | "in" or "both" | Sprint start — discover new Plane issues |
| PM | "out" or "both" | Sprint end — push completions to Plane |
| Sync daemon | "both" | Automated periodic sync (60s loop) |

## Relationships

- USES: plane_sync.py (PlaneSyncer — the actual sync engine)
- READS: plane_client.py (list_projects, list_issues)
- READS: mc_client.py (list_tasks — find done tasks with Plane links)
- CREATES: OCMC tasks (ingest direction — new tasks from Plane)
- UPDATES: Plane issues (push direction — status to "Done")
- CONNECTS TO: plane_methodology.py (methodology labels synced: stage:/readiness:)
- CONNECTS TO: config_sync.py (Plane changes → update DSPD config YAML)
- CONNECTS TO: fleet-plane skill (PM's Plane management workflow)
- CONNECTS TO: fleet_plane_create_issue (manual issue creation vs this automatic discovery)
- AUTOMATED BY: sync daemon (fleet_sync_daemon.py — runs every 60s)
- NOT YET IMPLEMENTED: ops comment → Plane comment sync, full artifact HTML push, writer auto-update
