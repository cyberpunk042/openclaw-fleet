# Project Manager — Full Directive Design

**Date:** 2026-03-30
**Status:** Design — deep directive mapping
**Part of:** Agent Rework (document 4 of 13)

---

## PO Requirements (Verbatim)

> "project-manager work being in its process attached to its heartbeat
> like even its handling a task for unblocking for whatever reason like
> review or whatnot"

> "just like the PM would probably talk to the architect and the software
> engineer or whoever of concern in order to move forward the progress of
> the tasks."

> "agents need to call the right things that will do the right chains of
> actions... you dont want to have to manually update everywhere"

> "we need to do the right directive so the AI know if it need to use
> this bus or this bus and know that it will do this chain naturally"

> "adding a comment on a fleet task if related to a PM task we might want
> to propagate by default like we want to keep track of each ops tasks
> per PM tasks"

> "its all about focusing on the current task for heartbeat and following
> a logical pattern with the injected data making sure we interconnect
> the idea and set a proper autocomplete chain"

> "make sure that the moment to create the artifact(s) its easy and
> natural and intelligent"

---

## PM's World

The PM sees (pre-embedded, FULL, not compressed):
- The OCMC board with ALL tasks — title, description, stage, readiness,
  agent, story points, priority, comments, Plane link
- Plane sprint data — current cycle, active issues, priorities, modules
- Agent status — who's online, who's idle, who's busy with what task
- Messages, directives, events since last heartbeat
- Each task's artifact state and completeness

The PM acts through tools that trigger automatic chains:
- `fleet_task_create()` → task created + event emitted + IRC + Plane sync
- `fleet_artifact_update()` → fields updated + Plane label/HTML sync +
  event emitted + completeness checked
- `fleet_chat()` → board memory + IRC + mention routing to target agent
- Task comments → agent sees on next heartbeat + Plane sync if linked

The PM calls ONE tool. The infrastructure handles propagation.

---

## PM Heartbeat: The Full Directive

### Phase 1: Read Pre-Embedded Context

Everything is already there. The PM reads:
- Inbox tasks (assigned and unassigned) with full descriptions
- Unassigned count and list
- Sprint metrics (done/total/blocked/velocity)
- Agent availability (online, idle, busy, offline)
- Plane sprint (current cycle, issues, priorities)
- PO directives
- Messages from agents
- Events since last heartbeat

No tools called for this. Data is PRE-EMBEDDED.

### Phase 2: PO Directives (Highest Priority)

If PO directive exists → execute immediately:
- "Start AICP Stage 1" → create tasks, assign agents, set priorities
- "Pause fleet" → the control surface handles this, PM acknowledges
- "Focus on security" → reprioritize tasks, assign devsecops

### Phase 3: Process Unassigned Tasks

For EACH unassigned inbox task:

**Evaluate the task content:**
- What is being asked? (read title + description)
- Is there a verbatim requirement? If not, derive from description
  or post question to PO
- What type is this? (epic/story/task/bug/spike)
- How complex? (story points estimate)
- Who should work on it?

**Decide the entry point:**

```
Task is clear with specific requirements and target files?
  → stage=reasoning, readiness=80-90
  → Assign specialist agent
  → Post comment: "Assigned to {agent}. Requirements are clear.
    Produce a plan that addresses the verbatim requirement."

Task has requirements but needs analysis?
  → stage=analysis, readiness=30-50
  → Assign agent with domain expertise
  → Post comment: "Assigned for analysis. Examine the codebase
    areas mentioned and produce findings."

Task is vague, needs PO clarification?
  → stage=conversation, readiness=5-20
  → Assign agent OR keep unassigned
  → Post comment: "@human This task needs clarification: {what's unclear}"
  → Set readiness=5 (barely started)

Task is an epic that needs breakdown?
  → Create subtasks via fleet_task_create:
    - Each subtask: title, description, parent_task, task_type, agent,
      stage, readiness, story_points
    - Set dependencies between subtasks (depends_on)
  → Post comment on epic: "Broken down into {N} subtasks: {list}"
  → Set epic stage=reasoning (PM is planning it)
```

**The tool calls and their chains:**

| What PM does | Tool | Chain triggered |
|-------------|------|-----------------|
| Set agent | Update task custom field agent_name | → OCMC updated → Plane sync → event → IRC |
| Set stage | Update task custom field task_stage | → OCMC updated → Plane label → event → methodology active |
| Set readiness | Update task custom field task_readiness | → OCMC updated → Plane label → event |
| Set verbatim | Update task custom field requirement_verbatim | → OCMC updated → Plane HTML inject → event |
| Set type | Update task custom field task_type | → OCMC updated → methodology stages determined |
| Set points | Update task custom field story_points | → OCMC updated → Plane estimate |
| Create subtask | fleet_task_create with parent_task | → Task created → parent linked → event → IRC |
| Post comment | Task comment | → Visible to agent → Plane comment sync |
| Announce | fleet_chat with mentions | → Board memory → IRC → agent heartbeat routing |
| Escalate | fleet_escalate | → Board memory → ntfy to PO → IRC #alerts |

### Phase 4: Monitor In-Progress Tasks

For tasks that are assigned and in-progress:

**Check progression signals:**
- Has the agent posted comments or updated artifacts since last heartbeat?
- Is readiness increasing?
- Has the stage advanced?
- Are there new blockers?

**Respond to stagnation:**
- No update in 2+ cycles: "@{agent} What's the status on {task}?"
- No update in 4+ cycles: Consider reassignment or breaking the task smaller
- Agent offline with in-progress task: Alert fleet-ops

**Advance stages when ready:**
- If methodology checks pass for current stage → advance to next stage
- Post comment: "Stage advancing from {from} to {to}. {instructions for next stage}"
- Update task_stage field → chain triggers Plane label + event

### Phase 5: Track PM-Level Tasks

The PM has its own tasks (sprint planning, epic breakdown, roadmap).
For these tasks, PM follows the same methodology stages:

**PM creates artifacts for its own work:**
```
fleet_artifact_create("plan", "Sprint 2 Planning")
  → Object created → HTML in Plane → completeness check

fleet_artifact_update("plan", "steps", values=[...])
  → Object updated → HTML re-rendered → completeness increases
  → Readiness suggestion updated

fleet_artifact_update("plan", "requirement_reference", "PO said: ...")
  → Verbatim anchored → plan now traceable to PO's words
```

Each PM task tracks fleet ops tasks related to it. When a subtask
completes, it propagates to the parent's artifact — the PM sees
"3/5 subtasks done" and updates the parent accordingly.

### Phase 6: Sprint Management

Every few cycles (not every heartbeat), PM posts sprint summary:

```
fleet_chat(
  "Sprint S1: 5/15 done (33%), 3 in progress, 1 blocked.
   Blocker: Task #42 needs PO clarification.
   Velocity: 8 SP/week. On track for completion by Friday.
   Action: Posted question to PO on #42.",
  mention="all"
)
```

Chain: board memory (tagged [sprint, progress]) → IRC #fleet → all
agents see in next heartbeat

### Phase 7: Plane Integration

PM is the primary Plane user in the fleet:
- Plane sprint data pre-embedded → PM sees current priorities
- New Plane issues → PM creates OCMC tasks for them
- Plane module leads → PM respects assigned leads
- Cross-reference: every OCMC task from Plane has plane_issue_id
  linking back. PM can reference Plane URLs in comments.

PM doesn't sync manually. The sync daemon handles field propagation.
PM manages TASKS. Infrastructure manages SYNC.

### Phase 8: Inter-Agent Communication

The PM communicates proactively, not just reactively:

**Assigning work:** Comment on task + fleet_chat mention
**Design needed:** Message architect with specific context
**Testing needed:** Create QA task + assign qa-engineer
**Security concern:** Flag devsecops-expert
**Documentation needed:** Create doc task + assign technical-writer
**Status request:** Comment on task or direct fleet_chat

Each communication automatically routes through the event bus.
The PM doesn't think about routing — the tools handle it.

---

## What Makes This Natural for the AI

The pre-embedded data sets up the context. The autocomplete chain:

1. AI reads: "6 unassigned tasks in inbox"
2. AI reads task #1: title, description, no agent
3. AI naturally continues: "This task is about X, the right agent is Y"
4. AI calls: update agent_name to Y
5. AI naturally continues: "The task needs analysis first, readiness is about 30"
6. AI calls: update task_stage, task_readiness
7. AI naturally continues: "I should tell the agent what to focus on"
8. AI posts: comment explaining assignment

The pattern flows naturally from the data. The AI doesn't need to
think about what to do — the data makes the right action obvious.
The tools handle the chains. The AI follows the pattern.

---

## Open Questions

- How does PM decide initial readiness? Need a clear decision tree
  that PM can follow.
- How does PM handle conflicting priorities from Plane vs PO directives?
- What's the PM's DSPD roadmap work when idle? Standing task or ad-hoc?
- How does PM track velocity? Story points per time period?
- Should PM have a "planning artifact" that accumulates sprint plans?