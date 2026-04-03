# ConfigChange

**Type:** Claude Code Hook (lifecycle event)
**Category:** Configuration (fires when a config file changes)
**Handler types:** command, http, prompt, agent
**Can block:** YES (can reject the config change)

## What It Actually Does

Fires when Claude Code configuration files change (`.claude/settings.json`, project settings, etc.). The handler can react to changes (propagate them), validate changes (reject invalid config), or log for audit.

## Fleet Use Case: Hot-Reload + Change Propagation

```
ConfigChange fires (config file modified)
├── Identify what changed:
│   ├── Permission rules? → validate, propagate
│   ├── Hook configuration? → validate, reload
│   ├── Model/effort settings? → log change
│   ├── Budget mode? → propagate to all crons via update_cron_tempo()
│   └── Agent role config? → validate, reload context
├── Propagation:
│   ├── Budget mode change → all fleet daemons adjust intervals
│   ├── Permission change → re-evaluate current task permissions
│   ├── Hook change → reload hook handlers
│   └── Agent config change → re-inject context
├── Validation:
│   ├── Is the change valid? (schema check)
│   ├── Is it authorized? (PO-only settings)
│   ├── If invalid: exit code 2 → reject change
│   └── If valid: allow and propagate
├── Audit:
│   ├── Trail event: config_changed
│   ├── What changed, who changed it, when
│   └── Before/after values
└── Return: {} or exit code 2 (reject)
```

## Connection to Budget Mode

Budget mode changes flow through config:
1. PO changes budget_mode on OCMC board → fleet_config
2. Orchestrator reads new mode → updates FleetControlState
3. FleetControlState change → config propagation
4. ConfigChange hook fires → update_cron_tempo() adjusts all cron intervals
5. All daemons now run at new tempo (turbo 5s / aggressive 15s / standard 30s / economic 60s)

## Relationships

- FIRES ON: config file changes (settings.json, project config)
- CAN BLOCK: yes (exit code 2 — reject invalid config changes)
- CONNECTS TO: /config command (editing config triggers this hook)
- CONNECTS TO: budget_modes.py (budget mode changes propagated)
- CONNECTS TO: update_cron_tempo() (cron interval adjustment)
- CONNECTS TO: FileChanged hook (ConfigChange is config-specific; FileChanged is general)
- CONNECTS TO: trail system (trail.config.changed event)
- CONNECTS TO: fleet-ops role (config validation and propagation)
- TIER: 3 in implementation priority (convenience, not critical path)
