# fleet_artifact_update

**Type:** MCP Tool (read-modify-write via Plane HTML)
**System:** S08 (MCP Tools), S10 (Transpose Layer)
**Module:** fleet/mcp/tools.py:2194-2284
**Stage gating:** None — agents update artifacts at any stage (analysis docs, investigation reports, plans, code artifacts)

## Purpose

Update a field of an existing artifact on the task's linked Plane issue. This is the PROGRESSIVE WORK tool — agents fill artifact fields incrementally across multiple orchestrator cycles. The tool reads the current object from Plane's description HTML (via transpose.from_html), merges the update (APPEND for lists, REPLACE for scalars), re-renders to HTML (via transpose.to_html), writes back to Plane, and checks completeness against the artifact type standard.

Completeness rises as fields are filled: 20% → 50% → 100%. When artifact_tracker suggests readiness increase, PO reviews and decides.

## Parameters

- `artifact_type` (string, required) — Type: analysis_document, investigation_document, plan, bug, progress_update, completion_claim, pull_request
- `field` (string, required) — Field name to update (title, scope, findings, steps, etc. — per artifact type schema)
- `value` (string) — String value for scalar fields
- `values` (list[string]) — List of strings for list fields (e.g., findings, steps)
- `append` (boolean, default false) — If True, APPEND to existing list instead of replacing. Critical for progressive work — agent adds findings one at a time.
- `task_id` (string) — Task ID. Uses current task if empty.

## Chain Operations

```
fleet_artifact_update(artifact_type, field, value/values, append, task_id)
├── RESOLVE: task_id
├── LOAD TASK: mc.get_task(board_id, task_id)
├── READ CURRENT: get Plane issue description_html
│   └── plane.list_issues(workspace, project_id) → find issue → description_html
├── EXTRACT CURRENT OBJECT: transpose.from_html(current_html) → dict (or empty {})
├── MERGE UPDATE:
│   ├── append=True AND field is list → current_obj[field].extend(values) or .append(value)
│   └── append=False → current_obj[field] = values (if list) or value (if scalar)
├── RE-RENDER: transpose.to_html(artifact_type, updated_obj) → new HTML
│   └── Rich HTML rendering + hidden JSON blob updated
├── WRITE TO PLANE: plane.update_issue(ws, project_id, issue_id, description_html=new_html)
│   └── Content OUTSIDE fleet-artifact markers preserved (PO notes safe)
├── CHECK COMPLETENESS: artifact_tracker.check_artifact_completeness(type, obj)
│   ├── required_pct: % of required fields filled
│   ├── is_complete: all required fields present
│   ├── missing_required: list of missing field names
│   └── suggested_readiness: 8-tier scale (0→0, <25%→10, <40%→20, ... 100%→95)
├── POST COMMENT: "Artifact updated ({type}): {field} | {completeness_summary}"
└── RETURN: {ok, artifact_type, field, object (full current), completeness}
```

## Merge Behavior (APPEND vs REPLACE)

```python
# append=True with list field (e.g., adding findings one at a time):
current: {"findings": ["Finding A"]}
call: field="findings", values=["Finding B"], append=True
result: {"findings": ["Finding A", "Finding B"]}

# append=False (default) replaces:
current: {"scope": "old scope"}
call: field="scope", value="new scope", append=False
result: {"scope": "new scope"}

# append=True with scalar (appends value to list):
current: {"findings": ["Finding A"]}
call: field="findings", value="Finding C", append=True
result: {"findings": ["Finding A", "Finding C"]}
```

This enables progressive artifact work — agents call fleet_artifact_update multiple times across cycles, each time adding a finding, a step, an option. Completeness rises incrementally.

## Who Uses It

| Role | Artifact Type | Fields They Update | Stage |
|------|-------------|-------------------|-------|
| Architect | analysis_document | scope, current_state, findings (append), implications | analysis |
| Architect | investigation_document | findings (append), options (append), recommendations | investigation |
| Architect | plan | approach, target_files, steps (append), criteria_mapping | reasoning |
| Engineer | plan | steps (append), risks | reasoning |
| Engineer | completion_claim | pr_url, summary, acceptance_criteria_check, files_changed | work |
| QA | bug | steps_to_reproduce, expected_behavior, actual_behavior | analysis |
| Writer | (all types) | documentation fields | work |
| DevSecOps | (security artifacts — not yet implemented) | threat_assessment, requirements | investigation |

## Relationships

- DEPENDS ON: Plane configured + issue linked to task
- READS: plane_client.py (current description_html)
- USES: transpose.py (from_html to extract, to_html to re-render)
- USES: artifact_tracker.py (check_artifact_completeness after update)
- USES: standards.py (implicitly — completeness checks against registered standards)
- WRITES TO: Plane issue description_html (plane.update_issue)
- POSTS: MC task comment (completeness summary after update)
- PRESERVES: content outside fleet-artifact markers (PO notes safe)
- COMPLEMENTS: fleet_artifact_create (initialize), fleet_artifact_read (inspect), this (modify)
- CONNECTS TO: methodology — completeness → suggested_readiness → readiness system (but PO SETS readiness)
- CONNECTS TO: preembed.py (artifact completeness injected into agent's task context at Step 0)
- PROGRESSIVE PATTERN: multiple calls across cycles → completeness rises → PO reviews at 100% → readiness 99 → work unlocked
