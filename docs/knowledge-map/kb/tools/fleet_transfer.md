# fleet_transfer

**Type:** MCP Tool (task management, handoff)
**System:** S08 (MCP Tools)
**Module:** fleet/mcp/tools.py:2665-2746+
**Stage gating:** None — transfers can happen at any stage

## Purpose

Transfer a task from one agent to another with context packaging. Reassigns the agent_name on the task, posts a transfer comment with the current stage, readiness, and a context summary, notifies the receiving agent via @mention, syncs to Plane, and records a trail event. The receiving agent gets the transfer context in their next heartbeat.

Used when: an agent is stuck and needs a different expertise, an agent goes offline with assigned work, PM reassigns based on workload, or a task transitions from one role's responsibility to another (e.g., architect designed it → engineer implements it).

## Parameters

- `task_id` (string, required) — Task to transfer
- `to_agent` (string, required) — Agent name to transfer to (e.g., "software-engineer", "architect")
- `context_summary` (string, required) — What you've done, where you left off, what remains. This is the HANDOFF — receiving agent starts from this context.

## Chain Operations

```
fleet_transfer(task_id, to_agent, context_summary)
├── LOAD TASK: mc.get_task(board_id, task_id)
│   ├── task_title
│   ├── stage (from custom_fields.task_stage)
│   └── readiness (from custom_fields.task_readiness)
├── REASSIGN: mc.update_task(board_id, task_id, custom_fields={agent_name: to_agent})
│   └── Task now assigned to new agent — orchestrator will dispatch to them
├── POST TRANSFER COMMENT:
│   ├── "Task transferred from {agent} to {to_agent}"
│   ├── "Stage: {stage} | Readiness: {readiness}%"
│   ├── "Context: {context_summary}"
│   └── This becomes the receiving agent's starting context
├── TRAIL: "Transfer: {agent} → {to_agent} task:{id} at stage:{stage} readiness:{readiness}"
│   └── tags: [trail, task:{task_id}, transfer, from:{agent}, to:{to_agent}]
├── NOTIFY RECEIVING AGENT:
│   ├── Board memory: @{to_agent} "Task transferred to you: {title}"
│   ├── Includes: stage, readiness, context_summary[:200]
│   └── Appears in receiving agent's MESSAGES section at next heartbeat
├── PLANE SYNC: if task linked to Plane issue:
│   └── plane.add_comment("Transferred from {agent} to {to_agent}")
├── IRC: "[transfer] {agent} → {to_agent}: {title[:50]}"
├── EVENT: fleet.task.transferred
│   └── from_agent, to_agent, task_id, stage
└── RETURN: {ok, from_agent, to_agent, task_id, stage, readiness}
```

## What the Receiving Agent Sees

At their next heartbeat, the receiving agent's fleet-context.md includes:
1. **MESSAGES section:** "@{to_agent} Task transferred to you: {title} (stage: {stage}, readiness: {readiness}%)"
2. **ASSIGNED TASKS section:** The task now appears in their assigned tasks
3. **Task comments:** Transfer comment with full context_summary

The receiving agent reads context → sees transfer → understands where the previous agent left off → continues from that stage.

## Who Uses It

| Role | To Whom | When |
|------|---------|------|
| PM | Any agent | Reassignment based on workload or expertise |
| Architect | Engineer | Design complete → handoff for implementation |
| Any agent | Any agent | Stuck/blocked → need different expertise |
| Orchestrator (health check) | Available agent | Agent went offline with assigned work |

## Relationships

- REASSIGNS: task via mc.update_task (agent_name field)
- POSTS: transfer comment on task (context handoff)
- NOTIFIES: receiving agent via board memory @mention
- RECORDS: trail event (transfer with from/to/stage/readiness)
- SYNCS: Plane issue comment
- NOTIFIES: IRC #fleet
- EMITS: fleet.task.transferred event
- CONNECTS TO: agent_lifecycle.py (receiving agent wakes from IDLE/SLEEPING)
- CONNECTS TO: orchestrator Step 0 (receiving agent's context refreshed with new task)
- CONNECTS TO: fleet-context.md Layer 6 (task appears in receiving agent's assigned tasks)
- CONNECTS TO: cowork protocol (§41 — transfer is full handoff; cowork is shared ownership)
- NOT YET IMPLEMENTED: full context packaging (§41.2 — should include artifacts, comments, contributions, trail summary). Current implementation passes context_summary as text; full packaging would gather all task artifacts and structure them for the receiving agent.
- CONNECTS TO: PM heartbeat (PM monitors for agents needing transfers — stuck, offline, wrong expertise)
