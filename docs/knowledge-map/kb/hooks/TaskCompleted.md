# TaskCompleted

**Type:** Claude Code Hook (lifecycle event)
**Category:** Workflow (fires when a task completes)
**Handler types:** command, http, prompt, agent
**Can block:** YES (exit code 2 — can reject the completion)

## What It Actually Does

Fires when a background task or subagent task completes. In Agent Teams, this fires when a teammate finishes their assigned task. The handler can: observe (log completion), react (trigger downstream actions), or block (reject the completion if quality check fails).

## Fleet Use Case: Task Completion Chain

```
TaskCompleted fires (task finished)
├── Record trail event: task completed with results
├── Trigger downstream:
│   ├── If all sibling tasks done → parent task advances
│   ├── If contribution task → notify target agent
│   ├── If sprint task → update sprint progress
│   └── If review task → trigger fleet-ops review
├── Quality check (optional — can block):
│   ├── Run automated pattern check on results
│   └── If issues: exit code 2 → "quality issues found, rework needed"
└── Return: {} or exit 2 with feedback
```

## Relationships

- FIRES ON: background task or teammate task completion
- CAN BLOCK: yes (exit code 2 — reject completion)
- CONNECTS TO: Agent Teams (teammate completes → lead notified)
- CONNECTS TO: orchestrator Step 7 (_evaluate_parents — all children done → parent to review)
- CONNECTS TO: fleet_task_complete (fleet tool version of task completion)
- CONNECTS TO: contribution system (contribution task done → check completeness)
- CONNECTS TO: sprint progress (velocity.py — task completion updates sprint metrics)
- CONNECTS TO: trail system (trail.task.completed event)
