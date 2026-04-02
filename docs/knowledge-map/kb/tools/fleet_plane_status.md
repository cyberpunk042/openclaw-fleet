# fleet_plane_status

**Type:** MCP Tool (Plane integration)
**System:** S08 (MCP Tools), S17 (Plane)
**Module:** fleet/mcp/tools.py

## Purpose

Get Plane project status: sprint progress, modules, recent activity. Read-only.

## Parameters

workspace (string, optional), project (string, optional)

## Chain Operations

plane.list_issues, plane.list_cycles, return project overview

## Who Uses It

PM, fleet-ops — Sprint awareness during heartbeat

## Relationships

plane_client.py (Plane REST API), fleet-plane skill, PM heartbeat
