# /config

**Type:** Claude Code Built-In Command
**Category:** Configuration
**Available to:** ALL agents (but typically managed by fleet-ops or PO)

## What It Actually Does

Opens Claude Code settings. Allows viewing and modifying configuration including permission modes, model defaults, effort levels, hooks, and other runtime settings. Settings are persisted across sessions in `~/.claude/settings.json` (user-level) or `.claude/settings.json` (project-level).

## When Fleet Agents Should Use It

**Fleet agents rarely use /config directly.** Configuration is managed through:
- Agent YAML configs (config/agents/*.yaml)
- Agent-tooling.yaml (per-role tool assignments)
- .claude/settings.json (pre-provisioned by IaC scripts)
- Gateway environment variables

**Fleet-ops may use it** to inspect current agent configuration during health checks or debugging.

**PO uses it** during manual sessions to adjust settings.

## Relationships

- CONNECTS TO: .claude/settings.json (where settings are persisted)
- CONNECTS TO: /permissions (subset — permission rules specifically)
- CONNECTS TO: /hooks (subset — hook configurations specifically)
- CONNECTS TO: ConfigChange hook (fires when config file changes)
- CONNECTS TO: IaC scripts (setup-agent-tools.sh provisions settings)
- MANAGED BY: agent-tooling.yaml (fleet's config-as-code approach)
