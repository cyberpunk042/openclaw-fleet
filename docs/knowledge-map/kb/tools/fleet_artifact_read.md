# fleet_artifact_read

**Type:** MCP Tool (read-only, Plane data extraction)
**System:** S08 (MCP Tools), S10 (Transpose Layer)
**Module:** fleet/mcp/tools.py:2144-2192
**Stage gating:** None — read artifact at any stage

## Purpose

Read the current artifact object from a task's linked Plane issue. Extracts the structured object from the hidden JSON data blob embedded in Plane's description HTML (via transpose.from_html). Returns clean dict data — no HTML. Also checks completeness against the artifact type's standard (required fields, optional fields, suggested readiness).

If no Plane issue is linked or no artifact exists, returns `{artifact_type: None, data: None, source: "none"}`.

## Parameters

- `task_id` (string) — Task ID. Uses current task from context if empty.

## Chain Operations

```
fleet_artifact_read(task_id)
├── RESOLVE: task_id (from param or ctx.task_id)
├── LOAD TASK: mc.get_task(board_id, task_id)
├── CHECK: task has plane_issue_id + workspace + project_id?
│   └── NO → return {artifact_type: None, data: None, source: "none"}
├── LOAD PLANE ISSUE: plane.list_issues(workspace, project_id) → find by issue ID
├── CHECK: issue has description_html?
│   └── NO → return {artifact_type: None, data: None, source: "none"}
├── EXTRACT: transpose.from_html(description_html)
│   └── Finds <span class="fleet-data" style="display:none">{json}</span>
│   └── HTML-unescapes → JSON parses → returns dict (the artifact object)
├── DETECT TYPE: transpose.get_artifact_type(description_html)
│   └── Reads data-type attribute from fleet-artifact-start marker
├── CHECK COMPLETENESS: artifact_tracker.check_artifact_completeness(type, object)
│   ├── Maps filled required fields → required_pct (0-100)
│   ├── Maps total fields → overall_pct
│   ├── Lists missing_required fields
│   ├── Calculates suggested_readiness (8-tier scale: 0% → 0, <25% → 10, ... 100% → 95)
│   └── is_complete = all required fields present
└── RETURN: {ok, artifact_type, data (dict), source: "plane",
            completeness: {required_pct, is_complete, missing_required, suggested_readiness}}
```

No events emitted. No state changed. Pure read.

## How Artifacts Are Stored on Plane

Plane issues hold artifacts in their `description_html` field using the fleet marker system:

```html
<span class="fleet-artifact-start" data-type="plan"></span>
<!-- Rich HTML rendering for humans to read -->
<h2>Implementation Plan: Add Auth Middleware</h2>
<blockquote>Verbatim: "Add JWT middleware..."</blockquote>
<ol><li>Create middleware module</li><li>Add tests</li></ol>
<!-- Hidden JSON blob — the actual source of truth -->
<span class="fleet-data" style="display:none">{"title":"Add Auth...","steps":["Create..."]}</span>
<span class="fleet-artifact-end"></span>
```

**Key:** Content OUTSIDE the fleet-artifact-start/end markers is NEVER touched by fleet tools. PO can add manual notes alongside fleet artifacts.

The JSON blob IS the source of truth — the visible HTML is a rendering. Agents work with the dict. Humans see the HTML. Both are always in sync via transpose.

## Who Uses It

| Role | When | Why |
|------|------|-----|
| Any agent | Before updating artifact | Read current state before modifying |
| Fleet-ops | During review | Check artifact completeness against standard |
| PM | Task management | View artifact progress, suggested readiness |
| Orchestrator | Context refresh | Include artifact state in agent's pre-embed (Step 0) |

## Relationships

- READS FROM: mc_client.py (task + Plane link), plane_client.py (issue description_html)
- USES: transpose.py (from_html — extracts JSON blob from HTML, get_artifact_type — reads data-type)
- USES: artifact_tracker.py (check_artifact_completeness — maps fields to readiness)
- USES: standards.py (implicitly — artifact_tracker checks against registered standards)
- NO EVENTS: pure read
- PRECEDES: fleet_artifact_update (read before updating)
- COMPLEMENTS: fleet_artifact_create (create initializes, read retrieves, update modifies)
- CONSUMED BY: context_assembly.py (artifact section of assemble_task_context)
- FEEDS: agent's understanding of current artifact state (what's filled, what's missing)
- CONNECTS TO: methodology — suggested_readiness from artifact completeness feeds the readiness system (but PO SETS readiness, tool only SUGGESTS)

## 7 Artifact Types With Renderers

| Type | Key Required Fields | Typical Producer |
|------|-------------------|-----------------|
| analysis_document | title, scope, current_state, findings, implications | Architect, Engineer |
| investigation_document | title, scope, findings (+ options, recommendations) | Architect, Engineer |
| plan | title, requirement_reference, approach, target_files, steps, acceptance_criteria_mapping | Architect, Engineer, PM |
| progress_update | (varies) | Any agent |
| bug | title, steps_to_reproduce, expected_behavior, actual_behavior, environment, impact | QA, Engineer |
| completion_claim | pr_url, summary, acceptance_criteria_check, files_changed | Workers (at fleet_task_complete) |
| pull_request | title, description, changes, testing, task_reference | Workers (at fleet_task_complete) |

## 5 Artifact Types WITHOUT Renderers (designed but not built)

| Type | Who Produces | Blocks |
|------|-------------|--------|
| security_assessment | DevSecOps | Security contribution flow |
| qa_test_definition | QA | Test predefinition contribution flow |
| ux_spec | UX | UX contribution flow |
| documentation_outline | Writer | Doc contribution flow |
| compliance_report | Accountability | Compliance reporting |
