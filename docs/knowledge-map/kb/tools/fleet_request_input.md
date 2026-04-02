# fleet_request_input

**Type:** MCP Tool
**System:** S08 (MCP Tools)
**Module:** fleet/mcp/tools.py

## Purpose

Request a specific role's input on your task. Posts @mention to target role via board memory. Paired with fleet_contribute.

## Parameters

task_id (string), from_role (string), question (string)

## Chain Operations

mc.post_memory (mention:role), mc.post_comment (input_request), IRC #fleet, trail event, events.emit fleet.input.requested, check contribution task existence

## Who Uses It

Any agent — When missing colleague input for current task

## Relationships

fleet_contribute (paired tool), contributions.py (contribution task check), synergy-matrix.yaml (valid roles)
