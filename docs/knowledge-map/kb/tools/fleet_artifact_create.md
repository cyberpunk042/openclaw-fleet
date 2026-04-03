# fleet_artifact_create

**Type:** MCP Tool (initialize artifact on Plane)
**System:** S08 (MCP Tools), S10 (Transpose Layer)
**Module:** fleet/mcp/tools.py:2286-2346
**Stage gating:** None — agents create artifacts at any post-conversation stage

## Purpose

Initialize a new structured artifact on the task's linked Plane issue. Creates the object with just a title, renders it to rich HTML via transpose.to_html(), writes to Plane's description_html, and checks initial completeness (which will be low — just title filled). The agent then uses fleet_artifact_update to fill fields progressively.

This is the START of the progressive artifact workflow:
1. fleet_artifact_create (initialize with title — completeness ~10%)
2. fleet_artifact_update × N (fill fields across cycles — completeness rises)
3. fleet_artifact_read (inspect current state)
4. Completeness reaches 100% → artifact_tracker suggests readiness increase → PO reviews

## Parameters

- `artifact_type` (string, required) — One of 7 implemented types: analysis_document, investigation_document, plan, bug, progress_update, completion_claim, pull_request. (5 more designed but no renderers: security_assessment, qa_test_definition, ux_spec, documentation_outline, compliance_report)
- `title` (string, required) — Artifact title
- `task_id` (string) — Task ID. Uses current task if empty.

## Chain Operations

```
fleet_artifact_create(artifact_type, title, task_id)
├── RESOLVE: task_id
├── INITIALIZE OBJECT: obj = {"title": title}
│   └── Minimal — only title set. Other fields added via fleet_artifact_update.
├── RENDER HTML: transpose.to_html(artifact_type, obj)
│   ├── Type-specific renderer creates rich HTML layout
│   ├── Hidden JSON blob: <span class="fleet-data" style="display:none">{json}</span>
│   └── Artifact markers: fleet-artifact-start/end with data-type attribute
├── LOAD TASK: mc.get_task(board_id, task_id)
├── WRITE TO PLANE: if task has plane_issue_id + workspace + project_id:
│   └── plane.update_issue(ws, project_id, issue_id, description_html=new_html)
├── POST COMMENT: "Artifact created ({artifact_type}): {title}"
├── CHECK COMPLETENESS: artifact_tracker.check_artifact_completeness(type, obj)
│   └── With only title: required_pct ~10-15%, is_complete=False,
│       missing_required=[scope, findings, ...], suggested_readiness=10
└── RETURN: {ok, artifact_type, object, completeness}
```

## The 7 Implemented Artifact Types

Each type has a specific transpose renderer that produces role-appropriate HTML:

| Type | Renderer Output | Typical Creator | Stage |
|------|----------------|-----------------|-------|
| analysis_document | h2 title, scope paragraph, findings as blockquotes, implications list | Architect, Engineer | analysis |
| investigation_document | h2 title, scope, findings by topic, options as comparison table (name/pros/cons), recommendations | Architect | investigation |
| plan | h2 title, blockquote for verbatim, ordered steps, criteria mapping table, risks | Architect, Engineer | reasoning |
| progress_update | status summary | Any agent | work |
| bug | title, numbered steps to reproduce, expected/actual behavior, environment, impact | QA, Engineer | analysis |
| completion_claim | PR URL, summary, acceptance_criteria_check table, files_changed | Workers | work |
| pull_request | title, description, changes, testing, task reference | Workers | work |

## The 5 Missing Artifact Types (designed, no renderer)

| Type | Would Be Created By | Blocks |
|------|-------------------|--------|
| security_assessment | DevSecOps | Security contribution flow |
| qa_test_definition | QA | Test predefinition contribution flow |
| ux_spec | UX | UX contribution flow |
| documentation_outline | Writer | Documentation contribution flow |
| compliance_report | Accountability | Compliance reporting |

These 5 missing renderers block the contribution system for specialist artifact types. Until built, agents contribute via fleet_contribute (plain text comments) instead of structured artifacts on Plane.

## Who Uses It

| Role | Artifact Type | Stage |
|------|-------------|-------|
| Architect | analysis_document | analysis |
| Architect | investigation_document | investigation |
| Architect | plan | reasoning |
| Engineer | plan | reasoning |
| QA | bug | analysis |
| Workers | completion_claim, pull_request | work (via fleet_task_complete internally) |

## Relationships

- DEPENDS ON: Plane configured + task linked to Plane issue
- USES: transpose.py (to_html — renders object to rich HTML with hidden JSON blob)
- USES: artifact_tracker.py (check_artifact_completeness — initial check)
- WRITES TO: Plane issue description_html
- POSTS: MC task comment ("Artifact created")
- STARTS: progressive workflow (create → update × N → read → completeness → readiness)
- FOLLOWED BY: fleet_artifact_update (fill fields), fleet_artifact_read (inspect)
- CONNECTS TO: standards.py (required/optional fields per type)
- CONNECTS TO: methodology — completeness → suggested_readiness → PO reviews → readiness gate
- CONNECTS TO: preembed.py (artifact state in agent's task context)
- CONNECTS TO: fleet-ops review (completeness checked at Step 4)
- MISSING RENDERERS BLOCK: 5 contribution artifact types for specialist roles
