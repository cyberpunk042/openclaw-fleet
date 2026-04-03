# /statusline

**Type:** Claude Code Built-In Command
**Category:** Configuration
**Available to:** ALL agents

## What It Actually Does

Configures the Claude Code status line — the persistent bar at the bottom of the terminal showing session state. Can display: model name, effort level, context usage, cost, session ID, custom fields. Configurable via settings or this command.

## When Fleet Agents Should Use It

**Fleet agents generally don't interact with /statusline.** The gateway manages the terminal environment. Status information flows through different channels in fleet:
- Agent status → fleet_agent_status tool → OCMC board
- Context usage → session telemetry → session_manager.py
- Cost → LaborStamp → budget system
- Model → set by gateway dispatch

**Manual operator sessions:** When a human runs Claude Code directly, /statusline helps track session state visually.

**Debugging:** Fleet-ops may inspect the statusline configuration to verify agent environment setup.

## Relationships

- CONNECTS TO: /config (statusline is a setting)
- CONNECTS TO: /context (context grid is a richer view of context usage)
- CONNECTS TO: /cost (cost display — statusline shows running total)
- CONNECTS TO: /usage (rate limit — statusline can show remaining quota)
- CONNECTS TO: session telemetry (fleet's equivalent of statusline data)
- CONNECTS TO: AICP statusline IaC (devops-expert-local-ai .claude/settings.json)
