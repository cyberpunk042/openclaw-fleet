# OCMC Fingerprint Removal

## Summary

Remove "openclaw" identifiers from Mission Control API responses that leak into Claude Code sessions via MCP tools.

## Problem

The MC agent model has a field `openclaw_session_id` returned in every agent API response. When fleet MCP tools fetch agent data, this field flows through Claude Code's conversation to Anthropic's API — exposing "openclaw" in the data.

## Critical Fix

**Field: `openclaw_session_id` in agent model/schema**

- `backend/app/models/agents.py:28` — column definition
- `backend/app/schemas/agents.py:239` — exposed in `AgentRead` response schema
- Returned by: `GET /agents`, `POST /agents`, `PATCH /agents/{agent_id}`, `POST /agents/{agent_id}/heartbeat`
- Migration files: `backend/migrations/versions/658dca8f4a11_init.py`

**Approach:** Rename to `session_id` via:
1. New Alembic migration renaming the column
2. Update model, schema, and all backend references
3. Apply as a fleet patch (same pattern as existing patches/)

## Moderate Fixes

**Frontend branding (~15 strings):**
- `frontend/src/app/layout.tsx:13` — page title "OpenClaw Mission Control"
- `frontend/src/components/templates/LandingShell.tsx` — logo, footer, copyright
- `frontend/src/components/organisms/LandingHero.tsx:37` — hero text
- `frontend/src/components/molecules/HeroCopy.tsx:6`
- `frontend/src/app/gateways/` — gateway description text
- `frontend/src/app/invite/page.tsx:85`

**Approach:** Fleet UI patch (same pattern as existing 0005/0006 patches) or sed in apply-patches.sh.

**Docker compose name:**
- `compose.yml:1` — `name: openclaw-mission-control`

**Approach:** Override in fleet's docker compose invocation or patch.

## Out of Scope

- Backend service module path `app/services/openclaw/` — internal code, never in API responses
- Test fixtures — test code, not deployed
- Migration SQL comments — code, not in responses

## Implementation

All changes delivered as fleet patches in `patches/` — applied by `scripts/apply-patches.sh`. No upstream fork of MC needed.
