# fleet_task_context

**Type:** MCP Tool (read-only, assembled)
**System:** S08 (MCP Tools), S19 (Session/Context)
**Module:** fleet/mcp/tools.py:2048-2094
**Stage gating:** None — allowed in ALL stages

## Purpose

Get EVERYTHING about a task in one call. Aggregates task data, custom fields, methodology state (stage, instructions, required stages, next stage), artifact object with completeness from Plane HTML, typed comments with attribution, activity events, and related tasks (parent, children, dependencies). Uses context_assembly.assemble_task_context() — the same aggregation the orchestrator uses in Step 0.

Also stores task_stage and task_readiness on the session context for stage enforcement by other tools (_check_stage_allowed). If the task has a project field, updates the session's project_name.

## Parameters

- `task_id` (string) — Task ID. Uses current task from context if empty.

## Chain Operations

```
fleet_task_context(task_id)
├── RESOLVE: task_id (from param or ctx.task_id)
├── LOAD: mc.get_task(board_id, task_id)
├── STORE ON CONTEXT: task_stage, task_readiness, task_id, project_name
│   └── These feed _check_stage_allowed for fleet_commit/fleet_task_complete
├── ASSEMBLE: context_assembly.assemble_task_context(task, mc, board_id, plane, event_store)
│   ├── task core: id, title, status, priority, description[:500]
│   ├── custom_fields: readiness, stage, requirement_verbatim, project,
│   │                   branch, pr_url, agent_name, story_points, complexity,
│   │                   task_type, parent_task, delivery_phase
│   ├── methodology: stage, stage_summary (from get_stage_summary),
│   │                stage_instructions (FULL MUST/MUST NOT/CAN from stage_context.py),
│   │                readiness, required_stages (per task_type), next_stage
│   ├── artifact: type, data (from Plane HTML via transpose.from_html),
│   │            completeness (required_pct, overall_pct, is_complete,
│   │            missing_required, suggested_readiness, summary)
│   ├── comments: last 20, each with author, content[:300], time
│   ├── activity: last 15 events for this task (type, time, agent, summary[:100])
│   └── related_tasks: children (parent_task == this task),
│                      parent (if parent_task set),
│                      dependencies (if depends_on set)
├── CACHED: per orchestrator cycle (cache key = task_id, cleared by clear_context_cache)
└── RETURN: full assembled bundle with ok=True
```

## Who Uses It

| Role | When | Why |
|------|------|-----|
| Any agent | Start of work | Load complete task state before beginning |
| Fleet-ops | During review | Full context for 7-step review (requirement, criteria, trail, artifact) |
| PM | Task management | Check task state, methodology progress, artifact completeness |
| Architect | Contribution | Read target task's full context before providing design_input |

## What Makes This Different from fleet_read_context

fleet_read_context loads task + board memory + URLs — the raw data.
fleet_task_context uses context_assembly.py to ASSEMBLE that data into a structured bundle with methodology state, artifact completeness, typed comments, and activity history. It's heavier but more comprehensive.

Both store task_stage/task_readiness on context for stage enforcement.

## Relationships

- READS FROM: mc_client.py (task, comments), plane_client.py (artifact HTML), event store (activity)
- USES: context_assembly.py (assemble_task_context — same as orchestrator Step 0)
- USES: methodology.py (required stages, next stage), stage_context.py (stage instructions + summary)
- USES: transpose.py (from_html — extract artifact from Plane HTML), artifact_tracker.py (completeness)
- STORES: task_stage + task_readiness on session context (feeds _check_stage_allowed)
- CACHED: per cycle (10 agents calling for same task = 1 actual assembly)
- COMPLEMENTS: fleet_read_context (raw data) vs this (assembled bundle)
- COMPLEMENTS: fleet_heartbeat_context (fleet-wide awareness vs task-specific detail)
- CONSUMED BY: agent's work decision-making (read context → decide what to do)
- CONNECTS TO: CLAUDE.md (agent reads assembled context and follows CLAUDE.md rules)
- CONNECTS TO: task-context.md Layer 7 (pre-embedded version of same data, written by orchestrator)
