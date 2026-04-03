# fleet_agent_status

**Type:** MCP Tool (read-only)
**System:** S08 (MCP Tools), S06 (Agent Lifecycle)
**Module:** fleet/mcp/tools.py:1506-1561
**Stage gating:** None — allowed in ALL stages

## Purpose

Fleet health snapshot for situational awareness. Returns agents with their status, tasks grouped by status (inbox/in_progress/review/done), blocked task count, unassigned inbox count, and pending approvals with confidence scores. No arguments needed. No side effects — pure read.

## Parameters

None.

## What It Actually Returns

From reading the code (lines 1513-1561):

**Agents list:** For each agent (excluding Gateway): name, status (from MC API — maps to ACTIVE/IDLE/SLEEPING/OFFLINE in agent_lifecycle.py), id.

**Task counts:** Tasks grouped by status value (inbox, in_progress, review, done). Plus:
- `blocked_tasks` — count of tasks with `is_blocked=True` (dependency not met)
- `unassigned_inbox` — count of inbox tasks with NO `assigned_agent_id` (these are what PM needs to assign)

**Pending approvals:** List of pending approvals with: id, task_id (first 8 chars), confidence score (0-100, set by fleet_task_complete based on tests + compliance), action_type.

## Chain Operations

```
fleet_agent_status()
├── ctx.resolve_board_id()
├── mc.list_agents()
│   └── filter: exclude "Gateway" agents
│   └── return: [{name, status, id}, ...]
├── mc.list_tasks(board_id)
│   ├── group by status → counts dict
│   ├── count is_blocked → blocked_tasks
│   └── count inbox + no assigned_agent_id → unassigned_inbox
├── mc.list_approvals(board_id, status="pending")
│   └── return: [{id, task_id, confidence, action_type}, ...]
└── return: {board_id, agents, task_counts, blocked_tasks,
             unassigned_inbox, pending_approvals}
```

No events emitted. No state changed. No trail recorded.

## Who Uses It

| Role | When | What They Look For |
|------|------|-------------------|
| PM | Every heartbeat | `unassigned_inbox` > 0 → need to assign. `blocked_tasks` > 0 → need to unblock. |
| Fleet-ops | Every heartbeat | `pending_approvals` list → reviews to process. Agent status → offline agents with assigned work. |
| Any agent | Investigation | Fleet state before making decisions (who's available, what's queued). |

## Relationships

- READS FROM: mc_client.py (3 API calls: agents, tasks, approvals)
- NO EVENTS: pure read-only, no side effects
- COMPLEMENTS: fleet_heartbeat_context (this is simpler — just counts; heartbeat_context includes role-specific data, directives, messages)
- USED BY PM TO: detect unassigned tasks → call fleet_task_create to assign
- USED BY FLEET-OPS TO: detect pending approvals → call fleet_approve to review
- CONNECTS TO: agent_lifecycle.py (agent status values), health.py (stuck/offline detection uses same data), orchestrator Step 4 (wake drivers when unassigned/pending detected)
- DATA OVERLAPS WITH: fleet-context.md Layer 6 (pre-embedded fleet state includes same counts — this tool is on-demand, context is pre-embedded)
