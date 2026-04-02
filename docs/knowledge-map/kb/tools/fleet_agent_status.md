# fleet_agent_status

**Type:** MCP Tool (read-only)
**System:** S08 (MCP Tools)
**Module:** fleet/mcp/tools.py
**Stage gating:** None — allowed in ALL stages

## Purpose

Check fleet health: agents online/offline, tasks by status, pending approvals, recent activity. Read-only snapshot of fleet state. No side effects.

## Parameters

None required.

## Chain Operations

```
fleet_agent_status
├── mc.list_agents()              → all agents with status
├── mc.list_tasks(board_id)       → tasks grouped by status
├── mc.list_approvals(board_id)   → pending approvals count
└── return: {agents, task_counts, pending_approvals}
```

## Who Uses It

| Role | When | Why |
|------|------|-----|
| PM | Heartbeat | Check who's available for assignment |
| Fleet-ops | Heartbeat | Monitor fleet health, offline agents |
| Any agent | Investigation | Understand fleet state before decisions |

## Relationships

- READ-ONLY: no events emitted, no state changed
- READS FROM: mc_client.py (agents, tasks, approvals)
- USED BY: PM (assignment decisions), fleet-ops (health monitoring)
- CONNECTS TO: agent_lifecycle.py (agent status: ACTIVE/IDLE/SLEEPING/OFFLINE)
- CONNECTS TO: health.py (stuck detection, offline detection)
