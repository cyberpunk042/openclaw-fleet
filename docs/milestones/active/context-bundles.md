# Context Bundles — Pre-Embedded Data for Tasks and Heartbeats

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Scope:** Aggregated pre-injected data bundles for task work and heartbeats

---

## PO Requirements (Verbatim)

> "we are going to have to upgrade mcp group calls and pre-injected /
> pre-embeded data, like the current task."

> "We want to be able to aggregate the information, so the AI can for
> example get all the related work on his task and the comments and
> activies. the transposed data blob, the custom field and state and
> stage and such."

> "Heartbeat too will have its pre-embedded data but not the same as
> the task, more focused on the events and messages and other role
> related responsabilities."

---

## What This Means

Two different data aggregation patterns for two different agent contexts:

### 1. Task Context Bundle

When an agent is working on a task, it needs EVERYTHING about that task
in one aggregated call:

- **Transposed artifact object** — the structured data from the transpose
  layer. What's been built so far. The analysis findings, the plan steps,
  the investigation options.
- **Custom fields** — readiness, stage, verbatim requirement, story points,
  complexity, agent assignment, project, branch, PR URL
- **State and stage** — OCMC status, Plane state, methodology stage,
  what protocol to follow
- **Comments** — all task comments showing progressive work across cycles.
  What the agent did before. What the PO said. What reviewers flagged.
- **Activity history** — events related to this task. Dispatches,
  completions, rejections, mode changes that affected it.
- **Related sub-tasks** — if this is an epic, what children exist and
  their status. If this is a subtask, what's the parent and siblings.
- **Artifact completeness** — how complete is the artifact against the
  standard. What fields are missing. What readiness level is suggested.

All of this in ONE call. Pre-aggregated. The agent doesn't make 5
separate MCP calls to assemble its working context. It calls one tool
and gets the full bundle.

### 2. Heartbeat Context Bundle

When an agent wakes up between tasks (heartbeat), it needs different
data — NOT task-specific. Fleet-wide awareness:

- **Events** — what happened since last heartbeat. Mentions, alerts,
  mode changes, other agents' completions.
- **Messages** — board memory chat messages addressed to this agent.
  @mentions. Directives from PO.
- **Role-related responsibilities** — fleet-ops needs pending approvals.
  PM needs unassigned tasks. Architect needs design reviews. Each agent
  gets data relevant to their ROLE, not a generic dump.
- **Fleet state** — work mode, cycle phase, backend mode. How many
  agents online. What's blocked.
- **Assigned tasks summary** — what tasks this agent has, their stages
  and readiness. Not the full task context — just the summary so the
  agent knows what to work on next.

Different data. Different purpose. Different bundle.

---

## Current State

### fleet_read_context (existing)

Currently `fleet_read_context` returns a mix of task and fleet data:
- task info (if task_id provided)
- URLs
- board memory (last 5 entries)
- recent decisions, alerts, escalations
- chat messages mentioning this agent
- team activity
- sprint context
- fleet health
- event feed

This tries to do both task context and heartbeat context in one call.
It doesn't do either well:
- Task context is shallow — no artifact object, no comments, no
  activity history, no sub-tasks, no completeness
- Heartbeat context is not role-specific — every agent gets the same
  generic data regardless of their responsibilities

### HeartbeatBundle (existing)

`fleet/core/heartbeat_context.py` builds a bundle with:
- assigned tasks (id, title, status, priority, readiness, stage, verbatim)
- chat messages
- domain events (filtered by agent capabilities)
- sprint summary
- stage instructions
- fleet control state
- fleet health

This is closer to the heartbeat need but still not role-specific.

---

## What Needs to Change

### Task Context: fleet_task_context (new or upgraded fleet_read_context)

A single MCP call that aggregates everything about a task:

```python
fleet_task_context(task_id) -> {
    "task": {
        "id": "...",
        "title": "...",
        "status": "...",
        "readiness": 80,
        "stage": "analysis",
        "requirement_verbatim": "Add controls to the header bar",
        "custom_fields": { ... all fields ... },
    },
    "artifact": {
        "type": "analysis_document",
        "data": { ... the transposed object ... },
        "completeness": {
            "required_pct": 60,
            "missing": ["findings", "implications"],
            "suggested_readiness": 50,
        },
    },
    "comments": [
        {"author": "human", "content": "Focus on the header section", "time": "..."},
        {"author": "architect", "content": "Found 3 sections in DashboardShell", "time": "..."},
    ],
    "activity": [
        {"type": "dispatched", "time": "..."},
        {"type": "artifact_updated", "field": "scope", "time": "..."},
    ],
    "related_tasks": [
        {"id": "...", "title": "...", "status": "...", "relation": "child"},
    ],
    "stage_instructions": "... protocol text for current stage ...",
    "plane": {
        "issue_id": "...",
        "state": "...",
        "labels": [...],
    },
}
```

### Heartbeat Context: fleet_heartbeat_context (upgraded)

Role-specific data for between-task awareness:

```python
fleet_heartbeat_context(agent_name) -> {
    "agent": "fleet-ops",
    "role_data": {
        # Role-specific — fleet-ops gets approval queue
        "pending_approvals": [...],
        "review_queue": [...],
        "health_alerts": [...],
    },
    "messages": [
        {"from": "human", "content": "Review the CI tasks", "time": "..."},
    ],
    "events_since_last": [
        {"type": "task.completed", "agent": "architect", "task": "...", "time": "..."},
        {"type": "immune.agent_pruned", "agent": "backend-dev", "time": "..."},
    ],
    "fleet_state": {
        "work_mode": "full-autonomous",
        "cycle_phase": "execution",
        "backend_mode": "claude",
    },
    "assigned_tasks": [
        {"id": "...", "title": "...", "readiness": 80, "stage": "analysis"},
    ],
    "directives": [
        {"content": "Start working on AICP Stage 1", "from": "human"},
    ],
}
```

### Role-Specific Data

Each agent role gets different heartbeat data:

| Role | Gets |
|------|------|
| **fleet-ops** | Pending approvals, review queue, health alerts, budget status |
| **project-manager** | Unassigned tasks, sprint progress, velocity, Plane updates |
| **architect** | Design review requests, architecture alerts, complexity flags |
| **devsecops-expert** | Security findings, dependency alerts, PR security reviews |
| **qa-engineer** | Test failures, coverage reports, quality flags |
| **software-engineer** | Assigned work, PR feedback, merge conflicts |
| **devops-expert** | Infrastructure alerts, deployment status, config changes |
| **technical-writer** | Documentation tasks, completed features needing docs |
| **ux-designer** | UI tasks, design review requests |
| **accountability-generator** | Compliance checks, audit items |

---

## Milestones

### CB01: Task Context Bundle
- Aggregate task data: custom fields, artifact object, completeness,
  comments, activity, related tasks, stage instructions, Plane state
- Single MCP tool call returns the full bundle
- Replace or extend fleet_read_context for task-specific use

### CB02: Heartbeat Context Bundle Upgrade
- Role-specific data per agent type
- Events since last heartbeat
- Messages and directives
- Fleet state summary
- Upgrade existing HeartbeatBundle

### CB03: Role Data Providers
- Per-role data functions: fleet-ops gets approvals, PM gets sprint data
- Pluggable — new roles can add their own data providers
- Each provider returns role-specific data dict

### CB04: MCP Group Calls
- fleet_task_context(task_id) — the one call for task work
- fleet_heartbeat_context() — the one call for between-task
- Pre-injected data — agent gets everything it needs without
  making multiple calls

### CB05: Comment and Activity Aggregation
- Task comments from OCMC + Plane (bidirectional)
- Activity events filtered for this task
- Progressive work trail — what was done each cycle

---

## Relationship to Other Systems

### Transpose Layer
The task context bundle includes the transposed artifact object
and its completeness. The bundle reads from the transpose layer.

### Methodology System
The bundle includes stage instructions and readiness. The methodology
system provides this data.

### Immune System
The heartbeat bundle includes health alerts from the doctor. The
immune system feeds into the bundle.

### Standards Library
The artifact completeness in the task bundle comes from checking
against the standards library.

---

## Open Questions

- Should the task context bundle be cached per cycle? Or fresh every call?
- How much comment history to include? All? Last N? Since last heartbeat?
- Should the heartbeat bundle include task context for in-progress tasks?
  Or keep them completely separate?
- How does the bundle handle tasks that aren't linked to Plane issues?
  (OCMC-only tasks have no Plane artifact)