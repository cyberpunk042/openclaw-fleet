# fleet_transfer

**Type:** MCP Tool
**System:** S08 (MCP Tools)
**Module:** fleet/mcp/tools.py

## Purpose

Transfer task to another agent with full context packaging. Reassigns agent_name, posts transfer comment with stage/readiness/context, notifies receiving agent.

## Parameters

task_id (string), to_agent (string), context_summary (string)

## Chain Operations

mc.update_task (agent_name), mc.post_comment (transfer type), mc.post_memory (trail+transfer), mc.post_memory (mention:to_agent), Plane sync, IRC #fleet, events.emit fleet.task.transferred

## Who Uses It

PM (reassignment), any agent (handoff) — Task needs different expertise or agent is stuck/offline

## Relationships

contributions.py (context packaging includes contributions received), trail system (records from/to/stage/readiness), agent_lifecycle.py (receiving agent wakes)
