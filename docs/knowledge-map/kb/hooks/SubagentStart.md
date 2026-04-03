# SubagentStart

**Type:** Claude Code Hook (lifecycle event)
**Category:** Agent Teams (fires when a subagent spawns)
**Handler types:** command, http, prompt, agent
**Can block:** NO (observation only)

## What It Actually Does

Fires when a subagent is spawned via the Agent tool. The handler receives information about the subagent being created — its type, prompt, and configuration. Can be used to inject subagent-specific context, log creation events, or set up the subagent's environment.

## Fleet Use Case: Subagent Context + Logging

```
SubagentStart fires (subagent spawns)
├── Log creation:
│   ├── Trail event: subagent_started
│   ├── Which parent agent spawned it
│   ├── What type (general-purpose, Explore, Plan, etc.)
│   └── Task context inherited
├── Inject subagent context:
│   ├── Role-specific knowledge from map
│   ├── Current task details
│   └── Contribution requirements
├── Resource tracking:
│   ├── Count active subagents per agent
│   ├── Storm indicator: too many subagents = cascade_depth
│   └── Budget impact: subagent token consumption
└── Return: {} (observation only)
```

## Connection to Agent Teams

Agent Teams (experimental) uses SubagentStart when teammates spawn. In fleet context:
- Architect spawns Explore subagent for codebase research → SubagentStart fires
- Engineer spawns Plan subagent for implementation design → SubagentStart fires
- Fleet-ops spawns review subagent per pr-review-toolkit → SubagentStart fires

## Relationships

- FIRES ON: Agent tool creates a subagent
- CANNOT BLOCK: observation only
- CONNECTS TO: SubagentStop hook (complementary — start/stop pair)
- CONNECTS TO: Agent Teams (teammate spawning)
- CONNECTS TO: storm monitor (cascade_depth indicator — task-creates-task chains)
- CONNECTS TO: trail system (trail.subagent.started event)
- CONNECTS TO: budget system (subagent token consumption tracking)
- TIER: 3 in implementation priority (Agent Teams integration)
