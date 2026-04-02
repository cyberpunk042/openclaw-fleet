# fleet_gate_request

**Type:** MCP Tool
**System:** S08 (MCP Tools)
**Module:** fleet/mcp/tools.py

## Purpose

Request PO approval at a readiness gate (50% direction, 90% final). Posts to board memory with po-required tag, notifies PO via ntfy high priority.

## Parameters

task_id (string), gate_type (string: readiness_50, readiness_90, phase_advance), summary (string)

## Chain Operations

mc.post_memory (gate+po-required tags), mc.update_task (gate_pending field), ntfy high priority to PO, IRC #fleet, trail event, events.emit fleet.gate.requested

## Who Uses It

PM (primary), any agent — When task reaches 50% or 90% readiness checkpoints

## Relationships

methodology.py (readiness gates), orchestrator Step 3b (gate processing), fleet_approve (PO decides)
