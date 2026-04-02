# fleet_heartbeat_context

**Type:** MCP Tool (read-only, role-specific)
**System:** S08 (MCP Tools), S19 (Session)
**Module:** fleet/mcp/tools.py
**Stage gating:** None

## Purpose

Get role-specific heartbeat data in one call. Returns the same data the orchestrator pre-embeds into fleet-context.md, but on-demand. Includes role-specific data from role_providers.py.

## Parameters

None required (uses agent name from context).

## Chain Operations

```
fleet_heartbeat_context
├── context_assembly.assemble_heartbeat_context(agent, mc, board_id)
│   ├── fleet state (work_mode, cycle_phase, backend_mode)
│   ├── directives (PO directives for this agent)
│   ├── messages (@mentions since last heartbeat)
│   ├── assigned tasks (FULL detail)
│   ├── role_providers.py:
│   │   ├── fleet_ops_provider → pending_approvals, review_queue, offline_agents
│   │   ├── pm_provider → unassigned_tasks, blocked_tasks, sprint_progress
│   │   ├── architect_provider → tasks_needing_design
│   │   ├── devsecops_provider → security_tasks, PRs_needing_review
│   │   └── worker_provider → task_count, in_review_count
│   └── events (relevant events since last heartbeat)
└── return: role-specific heartbeat bundle
```

## Who Uses It

| Role | When | Why |
|------|------|-----|
| ALL agents | Heartbeat start | Load role-specific awareness data |

## Relationships

- READ-ONLY: no events, no state changes
- USES: context_assembly.py, role_providers.py (5 role-specific providers)
- SAME DATA AS: fleet-context.md (Layer 6) — but on-demand vs pre-embedded
- CONNECTS TO: preembed.py (formats the same data for context files)
- CONNECTS TO: heartbeat_gate.py (brain evaluates this data to decide wake/silent)
