# /hooks

**Type:** Claude Code Built-In Command
**Category:** Configuration
**Available to:** ALL agents (managed by fleet-ops / IaC)

## What It Actually Does

Displays the currently configured hooks — which hook events have handlers, what type of handler (command, http, prompt, agent), and their matchers. Shows the hook configuration from `.claude/settings.json` and project settings.

26 hook event types exist. Each can have multiple handlers. Handlers fire deterministically — every time the event occurs, 100% reliable. This makes hooks the enforcement layer (Line 1 anti-corruption: structural prevention).

## When Fleet Agents Should Use It

**Debugging hook behavior:** When a hook seems to not fire, or fires unexpectedly — /hooks shows the actual configuration.

**Fleet-ops health checks:** Verify all expected hooks are configured for an agent. Missing hooks = missing enforcement.

**After IaC provisioning:** Verify that setup-agent-tools.sh correctly configured the hooks.

## What Fleet Agents Should NOT Do

Agents should NOT modify hooks at runtime. Hooks are provisioned through:
- IaC scripts (setup-agent-tools.sh)
- .claude/settings.json (project-level)
- Agent-tooling.yaml (defines which hooks per role)

## Relationships

- CONNECTS TO: /config (hooks are part of config)
- SHOWS: all 26 hook event types and their handlers
- CONNECTS TO: analysis-05-hooks-branch.md (hook classification per role)
- CONNECTS TO: IaC scripts (provision hooks per agent role)
- CONNECTS TO: Line 1 anti-corruption (hooks ARE the structural prevention layer)
- CONNECTS TO: PreToolUse (safety-net pattern — most critical hook)
- CONNECTS TO: PostToolUse (trail recording pattern — every tool call logged)
- CONNECTS TO: SessionStart (knowledge map injection pattern)
