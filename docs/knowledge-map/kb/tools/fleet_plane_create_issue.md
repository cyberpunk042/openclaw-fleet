# fleet_plane_create_issue

**Type:** MCP Tool (Plane integration)
**System:** S08 (MCP Tools), S17 (Plane Integration)
**Module:** fleet/mcp/tools.py:1729-1861
**Stage gating:** None — PM creates issues at any time
**Requires:** Plane configured (PLANE_URL + PLANE_API_KEY)

## Purpose

Create an issue on Plane — the PO's project management surface. Used by PM to create work items from OCMC sprint planning, keeping both surfaces in sync. Creates the issue, resolves labels by name to IDs, optionally adds to a module (epic), notifies IRC, and emits a cross-platform tracking event.

When an agent creates subtasks via fleet_task_create in OCMC, PM should also create corresponding Plane issues here to maintain bidirectional sync.

## Parameters

- `project` (string, required) — Project identifier: AICP, OF, DSPD, NNRT
- `title` (string, required) — Issue title
- `description` (string) — Plain text, converted to HTML paragraphs (`<p>` per double-newline)
- `priority` (string) — urgent, high, medium, low, none (default: medium)
- `assignee` (string) — Agent email for assignment (e.g., "architect@fleet.local")
- `labels` (string) — Comma-separated label NAMES (e.g., "infra,security") — resolved to IDs via Plane API
- `module` (string) — Module NAME to add issue to (e.g., "Stage 1: Make LocalAI Functional") — resolved to ID
- `parent_issue` (string) — Parent issue title for sub-issue linking

## Chain Operations

```
fleet_plane_create_issue(project, title, ...)
├── CHECK: Plane configured? If not → {plane_available: false}
├── RESOLVE PROJECT: plane.list_projects(ws) → find by identifier
├── BUILD HTML: description paragraphs → <p> wrapped HTML
├── RESOLVE LABELS: if labels provided:
│   ├── GET /api/v1/workspaces/{ws}/projects/{id}/labels/
│   ├── Map label names → label IDs
│   └── Pass resolved IDs to create_issue
├── CREATE ISSUE: plane.create_issue(ws, project_id, title, desc_html, priority, label_ids)
│   └── Returns: issue.id, issue.title, issue.sequence_id, issue.priority
├── ADD TO MODULE: if module specified:
│   ├── GET /api/v1/workspaces/{ws}/projects/{id}/modules/
│   ├── Find module by name
│   └── POST module-issues/ to link issue
├── IRC: "[{agent}] 📋 Plane issue: {title} ({project}/{sequence_id})"
└── EVENT: fleet.plane.issue_created
    ├── subject: issue.id
    ├── tags: [project:{project}, plane]
    ├── surfaces: [internal, channel, plane]
    └── Includes: title, issue_id, project, module
```

## Who Uses It

| Role | When | Why |
|------|------|-----|
| PM | Sprint planning | Create work items on Plane from OCMC sprint plan |
| PM | Epic breakdown | Create sub-issues linked to modules (epics) |
| PM | Backlog grooming | Add new items to Plane backlog with priority + labels |
| Writer | Documentation tasks | Create Plane issues for documentation gaps |

## Relationships

- DEPENDS ON: Plane configured (plane_client.py with PLANE_URL + PLANE_API_KEY)
- READS: plane.list_projects (resolve project identifier → ID)
- READS: Plane labels API (resolve label names → IDs)
- READS: Plane modules API (resolve module name → ID, add issue)
- CREATES: Plane issue with HTML description, priority, labels
- LINKS: issue to module (epic) if specified
- NOTIFIES: IRC #fleet with issue reference
- EMITS: fleet.plane.issue_created event (cross-platform tracking)
- BIDIRECTIONAL WITH: fleet_task_create (OCMC side) — PM creates on both surfaces to maintain sync
- SYNCED BY: plane_sync.py (PlaneSyncer.ingest_from_plane discovers unlinked Plane issues → creates OCMC tasks)
- CONSUMED BY: fleet_plane_sync (bidirectional sync includes created issues)
- CONNECTS TO: fleet-plane skill (PM's Plane management workflow)
- CONNECTS TO: fleet-sprint skill (sprint lifecycle creates issues per sprint plan)
- CONNECTS TO: methodology labels (plane_methodology.py adds stage:/readiness: labels at sync time)
