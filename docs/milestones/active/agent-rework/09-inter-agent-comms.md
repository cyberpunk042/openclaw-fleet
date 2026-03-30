# Inter-Agent Communication — Full Chain Design

**Date:** 2026-03-30
**Status:** Design — deep communication chain mapping
**Part of:** Agent Rework (document 9 of 13)

---

## PO Requirements (Verbatim)

> "just like the PM would probably talk to the architect and the software
> engineer or whoever of concern in order to move forward the progress of
> the tasks."

> "adding a comment on a fleet task if related to a PM task we might want
> to propagate by default like we want to keep track of each ops tasks
> per PM tasks"

---

## Communication Surfaces

### Task Comments (MC API)
- Specific to a task
- Visible to assigned agent on next heartbeat (pre-embedded)
- Syncs to Plane issue comment if task is linked
- Progressive work trail — every cycle's work is a comment

### Board Memory (fleet_chat)
- Fleet-wide, tagged, searchable
- @mentions route to specific agent's heartbeat context
- Posted to IRC automatically
- Archived for history

### IRC (#fleet, #reviews, #alerts)
- Real-time notifications from event chains
- Human can see in The Lounge (localhost:9000)
- Not persisted in agent context — board memory is the persistent surface

### ntfy (push notifications)
- PO mobile alerts for escalations
- Critical events only

---

## Communication Chain Map

### PM → Agent (task assignment)

```
PM assigns task → tool: update agent_name field
Chain:
  1. OCMC custom field updated
  2. Plane label synced (on next sync cycle)
  3. Event emitted: fleet.task.dispatched
  4. IRC notification: "[PM] Assigned {task} → {agent}"
  5. PM posts task comment: "Assigned to you. Focus on {X}.
     Verbatim requirement: {verbatim}. Stage: {stage}."
  6. Comment → agent sees on next heartbeat (pre-embedded)
  7. Comment → Plane issue comment (sync)
```

The agent doesn't need to be told separately — the assignment
triggers the chain and the comment arrives pre-embedded.

### Agent → PM (question about requirements)

```
Agent in conversation stage, requirement unclear:
  Tool: task comment "The requirement says 'OCMC UI' but doesn't
    specify where. @project-manager can you clarify?"
Chain:
  1. Comment posted on task
  2. PM sees comment pre-embedded on next heartbeat
  3. Comment syncs to Plane issue
  4. IRC: "[{agent}] Question on {task}"
```

PM reads the question on next heartbeat and responds with another
comment → agent sees the answer pre-embedded on their next heartbeat.

### PM → Architect (design request)

```
PM needs architecture input on a task:
  Tool: fleet_chat("@architect Need design input on {task}: {context}",
    mention="architect")
Chain:
  1. Board memory entry created (tagged: design, mention:architect)
  2. IRC: "[PM] @architect Need design input..."
  3. Architect sees message pre-embedded on next heartbeat
  4. Architect reads task context and responds
```

OR PM creates a design subtask:
```
  Tool: fleet_task_create(
    title="Design review: {task}",
    agent_name="architect",
    parent_task=original_task_id,
    task_type="spike",
    task_stage="analysis",
  )
Chain:
  1. Task created on OCMC
  2. Linked to parent task
  3. Event emitted
  4. IRC notification
  5. Architect sees assignment pre-embedded on next heartbeat
```

### Architect → Engineers (design guidance)

```
Architect completes design, needs engineer to implement:
  Tool: task comment on implementation task:
    "Architecture decision: Use Radix Select in DashboardShell header.
     Target files: DashboardShell.tsx, FleetControlBar.tsx.
     Pattern: same as OrgSwitcher. See analysis artifact for details."
Chain:
  1. Comment on task
  2. Engineer sees pre-embedded
  3. Syncs to Plane
```

### Engineer → Engineer (peer communication)

```
software-engineer needs devops help:
  Tool: fleet_chat("@devops Need help with Docker config for {task}",
    mention="devops")
Chain:
  1. Board memory → devops heartbeat → IRC
```

### Agent → fleet-ops (escalation)

```
Agent stuck, needs human or authority decision:
  Tool: fleet_escalate(
    title="Stuck on {task}: {what}",
    details="I've tried {X} but {Y} fails because {Z}. Need {decision}."
  )
Chain:
  1. Board memory entry (tagged: escalation, human-attention)
  2. IRC #alerts
  3. ntfy push to PO
  4. fleet-ops sees on next heartbeat
```

### fleet-ops → Agent (review feedback)

```
fleet-ops rejects task with feedback:
  Tool: fleet_approve(id, "rejected", "The work doesn't match the
    requirement. Requirement says 'header bar' but your code creates
    a sidebar page. Please re-read the verbatim requirement.")
Chain:
  1. Rejection recorded on task
  2. Task stays in review status
  3. Event emitted: fleet.task.rejected
  4. IRC #reviews: "[fleet-ops] Rejected {task}: {reason}"
  5. Agent sees rejection pre-embedded on next heartbeat
  6. Agent re-reads requirement and corrects
```

---

## Propagation: Fleet Task ↔ PM Task

> "adding a comment on a fleet task if related to a PM task we might want
> to propagate by default"

When a fleet ops task (the agent's work) is linked to a PM task
(the parent epic/story):

**Comment propagation:**
- Agent completes subtask → comment on subtask
- Subtask completion → parent task gets a comment:
  "Subtask '{title}' completed by {agent}. {summary}"
- This happens automatically via the orchestrator's parent evaluation:
  when all children are done → parent moves to review

**Progress propagation:**
- Subtask artifact completeness → reflects in parent's tracking
- PM sees: "Epic: 3/5 subtasks done" in pre-embedded data
- Sprint progress aggregates subtask story points

**The chain is automatic.** The agent works on their task. The
infrastructure propagates to the parent. The PM sees the aggregate.

---

## What Needs Building

### Already exists:
- fleet_chat → board memory + IRC + mention routing
- Task comments → MC API
- fleet_escalate → board memory + ntfy + IRC
- fleet_approve → approval chain + event + IRC
- Event emitting from all tools

### Needs building/fixing:
- Task comment → Plane sync (comments don't currently sync to Plane)
- Parent task comment propagation (subtask done → parent comment)
- Pre-embedded comments for agents (comments on their tasks)
- PM pre-embedded: aggregate subtask progress per parent
- @mention routing to pre-embedded data (currently only board memory)

---

## Open Questions

- Should Plane comments sync to OCMC task comments? Bidirectional?
- How many comments to pre-embed? All? Last N? Since last heartbeat?
- Should there be a "conversation thread" per task visible to all
  participants, or just the assigned agent?
- How does the PO participate in task conversations? Through Plane
  comments? Through board memory?