# /permissions

**Type:** Claude Code Built-In Command
**Category:** Configuration
**Available to:** ALL agents (managed by fleet-ops / IaC)

## What It Actually Does

Manages allow/ask/deny permission rules. Controls which tools the agent can use without prompting, which require approval, and which are blocked. Six permission modes exist: default, acceptEdits, plan, auto, dontAsk, bypassPermissions.

In fleet context, agents run with pre-configured permissions — the gateway sets the permission mode, and IaC scripts provision the allow/deny lists per role.

## When Fleet Agents Should Use It

**Fleet agents do NOT modify their own permissions.** Permissions are provisioned:
- Gateway sets permission mode (typically `auto` for fleet agents)
- IaC scripts configure per-tool allow/deny lists
- Agent-tooling.yaml defines which tools each role can access

**Fleet-ops uses /permissions** to audit an agent's current permission state during debugging.

**DevSecOps uses it** to verify security-sensitive tools are properly restricted.

## Permission Modes in Fleet Context

| Mode | Fleet Usage |
|------|-------------|
| `auto` | Default for fleet agents — background classifier auto-approves |
| `plan` | Read-only mode — matches Think mode in AICP |
| `acceptEdits` | For agents that only need file editing |
| `bypassPermissions` | NEVER for fleet agents — security risk |

## Relationships

- CONNECTS TO: /config (permissions are a subset of config)
- CONNECTS TO: PermissionRequest hook (fires when permission dialog appears)
- CONNECTS TO: PermissionDenied hook (fires when auto mode denies a tool)
- CONNECTS TO: PreToolUse hook (stage gating — structural enforcement beyond permissions)
- CONNECTS TO: guardrails system (AICP Think/Edit/Act modes map to permission modes)
- CONNECTS TO: IaC scripts (provision-agent-files.sh sets permissions)
- CONNECTS TO: gateway (sets permission mode per agent dispatch)
