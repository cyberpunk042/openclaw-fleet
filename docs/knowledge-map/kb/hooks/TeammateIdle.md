# TeammateIdle

**Type:** Claude Code Hook (lifecycle event)
**Category:** Agent Teams (fires when a teammate is about to idle)
**Handler types:** command, http, prompt, agent
**Can block:** YES (can assign new work to prevent idling)

## What It Actually Does

Fires when an Agent Teams teammate is about to go idle — it has no more tasks in its queue. The handler can assign new work (preventing the idle), let it idle (save resources), or trigger load balancing across teammates.

## Fleet Use Case: Load Balancing + Task Queue

```
TeammateIdle fires (teammate about to idle)
├── Check task queue:
│   ├── Are there unassigned tasks? → assign next task
│   ├── Are there contribution requests waiting? → assign contribution
│   ├── Are sibling teammates overloaded? → steal work
│   └── Nothing to do? → let idle (save tokens)
├── Load balancing:
│   ├── Check teammate workload distribution
│   ├── Rebalance if one teammate has 5 tasks and another has 0
│   └── Consider task priority when redistributing
├── Logging:
│   ├── Trail event: teammate_idle
│   ├── Duration of idle period (if not assigned work)
│   └── Storm indicator: agent_thrashing if repeatedly idle
└── Return: new task assignment or {} (let idle)
```

## Why Fleet-Ops Cares

TeammateIdle is relevant when Agent Teams is used for within-task parallelism:
- Architect spawns 3 teammates to research architecture options → one finishes early → TeammateIdle fires → assign next research area
- QA spawns test teammates → one finishes its test suite → TeammateIdle → assign remaining tests

In the broader fleet (not Agent Teams), the equivalent is the orchestrator's wake/dispatch cycle — agents go idle between dispatches, handled by orchestrator not this hook.

## Relationships

- FIRES ON: Agent Teams teammate about to idle
- CAN BLOCK: yes (assign work to prevent idling)
- CONNECTS TO: Agent Teams (teammate lifecycle)
- CONNECTS TO: TaskCreated/TaskCompleted hooks (task assignment chain)
- CONNECTS TO: storm monitor (agent_thrashing indicator — wake with no work repeatedly)
- CONNECTS TO: orchestrator (fleet-level equivalent of idle detection)
- CONNECTS TO: fleet-ops role (load balancing decisions)
- TIER: 3 in implementation priority (Agent Teams integration, low priority)
