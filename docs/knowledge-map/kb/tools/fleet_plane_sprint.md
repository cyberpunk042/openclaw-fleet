# fleet_plane_sprint

**Type:** MCP Tool (Plane integration)
**System:** S08 (MCP Tools), S17 (Plane)
**Module:** fleet/mcp/tools.py

## Purpose

Get current sprint details: issues, progress, velocity. Read-only.

## Parameters

workspace (string, optional), project (string, optional)

## Chain Operations

plane.list_cycles (current), plane.list_issues (in cycle), calculate velocity, return sprint data

## Who Uses It

PM — Sprint management during heartbeat

## Relationships

velocity.py (sprint metrics), fleet-sprint skill, PM pre-embed
