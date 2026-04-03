# /claude-api

**Type:** Claude Code Bundled Skill (invoked as slash command)
**Category:** Agents & Tasks
**Available to:** ALL agents

## What It Actually Does

Loads the Claude API (Anthropic API) reference documentation into the conversation context. Provides access to API specs, tool use patterns, SDK usage, model capabilities, and integration patterns. This is a bundled skill — it uses the Skill tool internally to load structured API documentation.

## When Fleet Agents Should Use It

**Architect:** When designing API integrations, evaluating model capabilities, or planning tool use patterns for fleet tools.

**Software Engineer:** When implementing API calls to Claude (e.g., the AICP backend integration in `aicp/backends/claude_code.py`), understanding tool use schema, or debugging API responses.

**DevOps:** When configuring API keys, rate limits, or backend routing between LocalAI and Claude.

**Any agent building MCP tools:** Understanding how tool use works at the API level helps write better fleet MCP tools (fleet/mcp/tools.py).

## Why This Matters for Fleet

The fleet uses Claude as a backend. Understanding the API is critical for:
- AICP router decisions (when to route to Claude vs LocalAI)
- Token optimization (prompt caching, efficient tool use)
- Model selection (opus vs sonnet capabilities)
- Error handling (rate limits, auth failures, API errors)
- Future: direct API calls from LocalAI for hybrid routing

## Relationships

- CONNECTS TO: AICP router (aicp/core/router.py — routes between Claude and LocalAI)
- CONNECTS TO: AICP Claude backend (aicp/backends/claude_code.py)
- CONNECTS TO: gateway (uses Claude CLI as subprocess)
- CONNECTS TO: budget system (API costs tracked via LaborStamp)
- CONNECTS TO: session_manager.py (rate limit awareness from API)
- CONNECTS TO: storm monitor (rate_limit indicator from API errors)
- CONNECTS TO: /model and /effort (control API parameters)
