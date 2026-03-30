# Project Manager — Role, Responsibilities, Heartbeat

**Date:** 2026-03-30
**Status:** Design
**Part of:** Agent Rework (document 4 of 13)

---

## PO Requirements (Verbatim)

> "project-manager work being in its process attached to its heartbeat
> like even its handling a task for unblocking for whatever reason like
> review or whatnot"

> "just like the PM would probably talk to the architect and the software
> engineer or whoever of concern in order to move forward the progress of
> the tasks."

---

## The PM's Job

The PM is the DRIVER. Without PM action, nothing moves.

### Core Responsibilities

1. **Assign agents to unassigned tasks** — this is the #1 job. If a
   task is in inbox with no agent, the PM MUST assign one. This happens
   every heartbeat.

2. **Set task metadata** — task_type, task_stage, initial readiness,
   story points, verbatim requirement (from PO or Plane)

3. **Break down epics** — create subtasks, set dependencies, assign

4. **Manage sprint** — track velocity, report progress, plan next work

5. **Unblock** — if a task is blocked, PM resolves it: reassign, split,
   remove dependency, escalate

6. **Communicate** — talk to agents about their assignments, ask PO
   when requirements are unclear, coordinate between agents

7. **Plane integration** — pull priorities from Plane, keep OCMC and
   Plane in sync, manage the cross-platform view

### PM Heartbeat Flow

The PM heartbeat is NOT a quick check. It's the PM doing its job.
A PM task can span multiple fleet operation cycles. The PM's heartbeat
IS the PM's work.

1. Read pre-embedded context (full — messages, unassigned list, sprint,
   Plane data, events)
2. Handle PO directives first
3. Handle messages and agent requests
4. For each unassigned task: evaluate, set fields, assign agent
5. For each stuck task: investigate, communicate, resolve
6. For each epic: verify subtask coverage, create missing subtasks
7. Sprint summary when meaningful progress
8. Plane sync — pull new priorities, update statuses

### What PM Decides

- Who works on what (agent assignment)
- What type each task is (epic/story/task/bug/spike)
- What stage each task starts in (based on clarity)
- Initial readiness estimate
- Story point estimates
- How to break down complex work
- When to escalate to PO

### What PM Does NOT Decide

- Verbatim requirements — PO defines these. PM captures and sets them.
- Task readiness beyond initial — PO confirms readiness increases.
- Approvals — fleet-ops handles approvals, not PM.

---

## Pre-Embedded Data for PM

Full data, not compressed:
- All inbox tasks (assigned and unassigned) with descriptions
- Sprint progress (done/total/blocked)
- Agent status (who's online, who's idle, who's working on what)
- Recent events (completions, blocks, mode changes)
- Plane sprint data (if connected)
- PO directives
- Messages mentioning PM

---

## Open Questions

- How does PM decide which agent to assign? Based on task content keywords?
  Agent capabilities list? Previous assignments?
- How does PM set readiness? What criteria map to which percentage?
- How does PM interact with Plane? Read-only or also creates issues?
- What's the PM's DSPD roadmap work when idle?