# fleet_plane_list_modules

**Type:** MCP Tool (Plane integration)
**System:** S08 (MCP Tools), S17 (Plane)
**Module:** fleet/mcp/tools.py

## Purpose

List modules (epics) in a Plane project with their status and lead.

## Parameters

workspace (string, optional), project (string, optional)

## Chain Operations

plane.list_modules (workspace, project), return modules with status

## Who Uses It

PM, architect — Epic-level project overview

## Relationships

plane_client.py, PM heartbeat (module awareness)
