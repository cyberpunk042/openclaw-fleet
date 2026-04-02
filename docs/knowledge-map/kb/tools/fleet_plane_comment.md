# fleet_plane_comment

**Type:** MCP Tool (Plane integration)
**System:** S08 (MCP Tools), S17 (Plane)
**Module:** fleet/mcp/tools.py

## Purpose

Post a comment on a Plane issue. For updates, mentions, and cross-surface communication.

## Parameters

issue_id (string), comment (string)

## Chain Operations

plane.add_comment (workspace, project, issue_id, comment)

## Who Uses It

PM, writer, any agent — Cross-surface communication

## Relationships

plane_client.py, cross_refs.py (cross-reference generation)
