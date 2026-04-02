# fleet_artifact_update

**Type:** MCP Tool
**System:** S08 (MCP Tools)
**Module:** fleet/mcp/tools.py

## Purpose

Update a field of an existing artifact. Merges update into current object (APPEND for lists, REPLACE for scalars), re-renders HTML, preserves content outside markers.

## Parameters

artifact_type (string), field (string), value (any)

## Chain Operations

transpose.from_html (extract current), merge update, transpose.to_html (re-render), Plane update_issue, artifact_tracker.check_completeness, mc.post_comment, events.emit fleet.artifact.updated, trail event

## Who Uses It

All agents — Progressive artifact work across multiple cycles

## Relationships

transpose.py (bidirectional), artifact_tracker.py (completeness tracking), standards.py (field validation)
