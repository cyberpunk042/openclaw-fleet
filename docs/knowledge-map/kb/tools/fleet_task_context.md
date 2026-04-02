# fleet_task_context

**Type:** MCP Tool (read-only, assembled)
**System:** S08 (MCP Tools), S19 (Session)
**Module:** fleet/mcp/tools.py
**Stage gating:** None — allowed in ALL stages

## Purpose

Get EVERYTHING about your current task in one call. Returns the fully assembled task context bundle including methodology state, artifact state, contributions, comments, activity, and related tasks. Uses context_assembly.py for comprehensive aggregation.

## Parameters

- `task_id` (string, optional) — defaults to current task from context

## Chain Operations

```
fleet_task_context
├── context_assembly.assemble_task_context(task, mc, board_id, plane)
│   ├── task core (id, title, status, priority, description)
│   ├── custom fields (readiness, stage, verbatim, project, branch)
│   ├── methodology (stage, instructions, required stages, next stage)
│   ├── artifact (type, data, completeness from Plane HTML via transpose)
│   ├── comments (typed, with contributor attribution, last 20)
│   ├── activity (events for this task, last 15)
│   └── related tasks (parent, children, dependencies)
└── return: assembled context bundle (cached per cycle)
```

## Who Uses It

| Role | When | Why |
|------|------|-----|
| Any agent | When fleet_read_context doesn't provide enough detail | Full assembled context |
| Fleet-ops | During review | Complete task state for 7-step review |

## Relationships

- READ-ONLY: no events, no state changes
- USES: context_assembly.py (same aggregation as orchestrator Step 0)
- CACHED: per orchestrator cycle (10 agents = 1 actual assembly)
- ALTERNATIVE TO: fleet_read_context (this returns more structured data)
- CONNECTS TO: methodology.py (stage + readiness), transpose.py (artifact data), plane_client.py (artifact HTML)
