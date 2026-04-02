# fleet_plane_update_issue

**Type:** MCP Tool (Plane integration)
**System:** S08 (MCP Tools), S17 (Plane)
**Module:** fleet/mcp/tools.py

## Purpose

Update a Plane issue — change state, priority, labels, or assignment.

## Parameters

issue_id (string), plus update fields (state, priority, labels, assignee)

## Chain Operations

plane.update_issue (workspace, project, issue_id, fields)

## Who Uses It

PM — Sprint management

## Relationships

plane_client.py, plane_methodology.py (methodology labels)
