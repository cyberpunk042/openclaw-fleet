# fleet_artifact_read

**Type:** MCP Tool
**System:** S08 (MCP Tools)
**Module:** fleet/mcp/tools.py

## Purpose

Read current artifact state from Plane. Extracts object from hidden JSON data blob, checks completeness. Read-only.

## Parameters

artifact_type (string, optional)

## Chain Operations

transpose.from_html (extract JSON blob), artifact_tracker.check_completeness, return object + completeness + suggested_readiness

## Who Uses It

All agents — Check artifact state before updating

## Relationships

transpose.py (extraction), artifact_tracker.py, standards.py
