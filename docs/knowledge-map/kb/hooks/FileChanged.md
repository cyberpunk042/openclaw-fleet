# FileChanged

**Type:** Claude Code Hook (lifecycle event)
**Category:** Workspace (fires when a watched file changes)
**Handler types:** command, http, prompt, agent
**Can block:** NO (observation only)

## What It Actually Does

Fires when a file being watched by Claude Code changes on disk (external modification, not by Claude itself). The handler can react to changes — useful for config hot-reload, detecting external edits, or watching for deployment artifacts.

## Fleet Use Case: Config Hot-Reload + Change Detection

```
FileChanged fires (watched file changed on disk)
├── Identify what changed:
│   ├── CLAUDE.md → re-inject instructions
│   ├── agent.yaml → reload agent configuration
│   ├── agent-tooling.yaml → reload tool assignments
│   ├── fleet_config (board) → detect PO setting changes
│   └── .claude/settings.json → propagate config changes
├── React:
│   ├── Config file → hot-reload without session restart
│   ├── CLAUDE.md → notify agent of instruction changes
│   ├── Test results file → trigger QA review
│   └── Deployment marker → notify DevOps of completion
├── Logging:
│   ├── Trail event: file_changed
│   ├── Which file, modification timestamp
│   └── Whether hot-reload was triggered
└── Return: {} (observation only)
```

## Why MEDIUM Priority for Fleet

FileChanged enables hot-reload patterns:
- PO updates agent-tooling.yaml → agents pick up new tool assignments without restart
- PO modifies CLAUDE.md → agent sees updated instructions next turn
- CI pipeline writes test results → QA agent detects and reviews

Without this hook, config changes require a full session restart.

## Relationships

- FIRES ON: external file modification (not Claude's own edits)
- CANNOT BLOCK: observation only
- CONNECTS TO: ConfigChange hook (ConfigChange is settings-specific; FileChanged is general)
- CONNECTS TO: InstructionsLoaded hook (CLAUDE.md change → re-inject)
- CONNECTS TO: agent-tooling.yaml (tool assignment changes)
- CONNECTS TO: hot-reload patterns (config changes without restart)
- CONNECTS TO: fleet-ops role (config monitoring)
- TIER: 3 in implementation priority (operational improvement)
