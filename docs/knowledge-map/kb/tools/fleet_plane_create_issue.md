# fleet_plane_create_issue

**Type:** MCP Tool (Plane integration)
**System:** S08 (MCP Tools), S17 (Plane)
**Module:** fleet/mcp/tools.py

## Purpose

Create an issue in Plane. Used by PM to create work items from OCMC sprint planning.

## Parameters

title (string), description (string, optional), state (string, optional), priority (string, optional), labels (list, optional)

## Chain Operations

plane.create_issue (workspace, project, fields), return issue_id

## Who Uses It

PM — Create Plane issues during sprint planning

## Relationships

plane_client.py, fleet-plane skill, PM workflow
