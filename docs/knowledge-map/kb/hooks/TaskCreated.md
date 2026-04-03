# TaskCreated

**Type:** Claude Code Hook (lifecycle event)
**Category:** Workflow (fires when a task is created)
**Handler types:** command, http, prompt, agent
**Can block:** YES (can reject task creation)

## What It Actually Does

Fires when a task is created — either a background task (via Agent tool with run_in_background), or a teammate task (via Agent Teams). The handler can validate the task, modify it, or block its creation.

## Fleet Use Case: Task Validation + Auto-Assignment

```
TaskCreated fires (task being created)
├── Validate task fields:
│   ├── Does it have required fields? (title, description, assignee)
│   ├── Does it match methodology requirements?
│   ├── Is the creator authorized to create this type of task?
│   └── If invalid: exit code 2 → reject creation
├── Auto-assignment:
│   ├── Based on task type → assign to appropriate role
│   ├── Based on current load → assign to least-busy agent
│   └── Based on expertise → match agent skills to task requirements
├── Trail recording:
│   ├── Trail event: task_created
│   ├── Creator, assignee, task details
│   └── Contribution requirements (from synergy matrix)
├── Notify:
│   ├── If PM task → notify PM
│   ├── If contribution task → notify target agent
│   └── If sprint task → update sprint progress
└── Return: {} or exit code 2 (reject)
```

## Two-Level Task Model Context

In fleet, a single Plane issue can generate thousands of OCMC tasks:
- PM reads Plane issue → creates PM task on OCMC
- PM breaks down into subtasks → fleet_task_create for each
- Each subtask may need contributions → more tasks created
- TaskCreated fires for EACH of these OCMC task creations

This hook is NOT about Plane issue creation — it's about OCMC task lifecycle.

## Relationships

- FIRES ON: task creation (background or teammate)
- CAN BLOCK: yes (exit code 2 — reject creation with reason)
- CONNECTS TO: TaskCompleted hook (complementary — creation/completion pair)
- CONNECTS TO: fleet_task_create tool (fleet's task creation mechanism)
- CONNECTS TO: PM workflow (PM creates tasks from Plane issues)
- CONNECTS TO: contribution system (tasks may be contribution requests)
- CONNECTS TO: trail system (trail.task.created event)
- CONNECTS TO: sprint progress (velocity.py — new task affects sprint metrics)
- TIER: 2 in implementation priority (workflow automation)
