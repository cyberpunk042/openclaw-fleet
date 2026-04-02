# fleet_plane_sync

**Type:** MCP Tool (Plane integration)
**System:** S08 (MCP Tools), S17 (Plane)
**Module:** fleet/mcp/tools.py

## Purpose

Trigger Plane ↔ OCMC sync. Bidirectional: ingests new Plane issues as OCMC tasks, pushes completions back.

## Parameters

direction (string: pull, push, both)

## Chain Operations

plane_sync.ingest_from_plane (Plane→OCMC), plane_sync.push_completions_to_plane (OCMC→Plane), sync methodology fields

## Who Uses It

PM, fleet-ops — Bidirectional sync during sprint

## Relationships

plane_sync.py (bidirectional sync), plane_methodology.py (stage/readiness labels), config_sync.py (YAML persistence)
