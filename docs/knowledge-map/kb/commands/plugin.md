# /plugin

**Type:** Claude Code Built-In Command
**Category:** Agents & Tasks
**Available to:** ALL agents (managed by fleet-ops / IaC)

## What It Actually Does

Manages Claude Code plugins. Plugins extend Claude Code with new skills, hooks, MCP servers, and agent configurations. /plugin can:
- List installed plugins
- Install plugins from the marketplace or GitHub
- Remove plugins
- View plugin details

Plugins are installed per-project in `.claude/plugins/`. Each plugin provides a combination of skills, hooks, agents, and settings.

## When Fleet Agents Should Use It

**Fleet agents do NOT install plugins at runtime.** Plugin provisioning is handled by:
- IaC scripts (install-plugins.sh — idempotent, config-driven)
- agent-tooling.yaml (defines which plugins per role)
- setup-agent-tools.sh (orchestrates full toolchain setup)

**Fleet-ops uses /plugin** to audit installed plugins during health checks — verify the right plugins are installed for each agent role.

**Debugging:** If a skill from a plugin isn't working, /plugin shows if the plugin is actually installed.

## Plugin Ecosystem in Fleet Context

| Plugin | Stars | Roles | What It Provides |
|--------|-------|-------|-----------------|
| Superpowers | 132K | ALL dev | TDD methodology, 20+ skills |
| claude-mem | 45K | ALL | Cross-session memory, 4 MCP tools |
| safety-net | 1K | ALL | Hook catches destructive commands |
| pr-review-toolkit | Official | FLEET-OPS | 5 parallel Sonnet review agents |
| context7 | 47K | ENG, ARCH | Library/framework documentation |
| hookify | Official | DEVOPS | Natural-language hook creation |

## Relationships

- CONNECTS TO: /skills (plugins provide skills — /skills lists them)
- CONNECTS TO: /hooks (plugins provide hooks — /hooks shows them)
- CONNECTS TO: install-plugins.sh (IaC script for plugin provisioning)
- CONNECTS TO: agent-tooling.yaml (defines per-role plugin assignments)
- CONNECTS TO: .claude/plugins/ directory (where plugins are installed)
- CONNECTS TO: claude plugin install (CLI command — what /plugin wraps)
- CONNECTS TO: Plugin KB entries (kb/plugins/ — individual plugin documentation)
