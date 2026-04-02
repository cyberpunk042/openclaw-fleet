# fleet_artifact_create

**Type:** MCP Tool
**System:** S08 (MCP Tools)
**Module:** fleet/mcp/tools.py

## Purpose

Create a structured artifact on Plane. Renders object → rich HTML via transpose layer, embeds hidden JSON data blob, checks completeness against standard.

## Parameters

artifact_type (string: analysis_document, investigation_document, plan, bug, progress_update, completion_claim, pull_request), title (string), plus type-specific fields

## Chain Operations

transpose.to_html (render), Plane update_issue (HTML), artifact_tracker.check_completeness, mc.post_comment, events.emit fleet.artifact.created, trail event, suggest readiness if completeness high

## Who Uses It

All agents — When producing stage-appropriate artifacts

## Relationships

transpose.py (bidirectional object↔HTML), standards.py (required fields per type), artifact_tracker.py (completeness %), Plane (HTML display), 7 renderers implemented + 5 missing
