# Task Lifecycle — Complete Redesign

**Date:** 2026-03-30
**Status:** Design — every state, stage, phase, gate, relation, trail
**Part of:** Fleet Elevation (document 21 of 22)

---

## PO Requirements (Verbatim)

> "Remember there are also operational modes right now that have to be
> respected and events and notifications and sub-tasks and comments and
> relations and cowork and stages and gates and states and transfer of
> task, trails, mentions, X type of new [child] tasks and whatnot."

> "Things can evolve. The requirements, the things to test, the phases
> of the task, the various data blob for whatever different type we need
> + the main one and so on."

> "This need meticulous thinking logical transition and time for approval
> and even approvals only me can answers."

---

## What This Document Covers

The COMPLETE task lifecycle — every dimension, every transition, every
actor, every gate. This is where all other documents converge: stages,
phases, contributions, gates, reviews, rejections, trails, relations,
transfers, cowork, child tasks, artifacts, comments, events.

---

## Task Dimensions

A task has multiple simultaneous dimensions:

| Dimension | Values | Tracks |
|-----------|--------|--------|
| **Status** | inbox, in_progress, review, done | Where in the lifecycle |
| **Stage** | conversation, analysis, investigation, reasoning, work | What kind of work is being done |
| **Readiness** | 0-100% (valid: 0,5,10,20,30,50,70,80,90,95,99,100) | How ready for execution |
| **Phase** | ideal, conceptual, poc, mvp, staging, production | How mature the deliverable is |
| **Type** | epic, story, task, subtask, bug, spike, blocker, request, concern | What kind of task |

Each dimension is tracked as a custom field. Each dimension has its
own progression rules. Together they define the task's complete state.

---

## Status Lifecycle

```
INBOX → IN_PROGRESS → REVIEW → DONE
  ↑                      │
  │                      │ (rejection)
  │                      ↓
  └────────────── IN_PROGRESS (regressed)
```

### INBOX
Task is created but not being worked on.
- PM triages: sets fields, assigns agent
- Brain dispatches when all gates pass
- Tasks can sit in inbox indefinitely

### IN_PROGRESS
Agent is actively working on the task.
- Agent follows methodology stage protocol
- Readiness progresses through stages
- Contributions are created and received
- Gates are encountered and (hopefully) passed

### REVIEW
Task is complete, awaiting review and approval.
- Fleet-ops reviews against verbatim, trail, standards
- QA validates against predefined tests
- DevSecOps reviews security
- PO has final say

### DONE
Task is approved and complete.
- Trail finalized
- Sprint progress updated
- Documentation updated
- Parent task evaluated

---

## Relation Types

Tasks relate to each other in multiple ways:

### Parent / Child
```
Epic: "Add auth system"
├── Subtask: "Design data model" (parent_task = epic)
├── Subtask: "Implement middleware" (parent_task = epic)
├── Subtask: "Write tests" (parent_task = epic)
└── Subtask: "Document API" (parent_task = epic)
```
Propagation: child completion → parent summary. All children done →
parent to review.

### Dependency (Blocks / Blocked-by)
```
"Design data model" ──blocks──→ "Implement middleware"
```
The blocked task cannot be dispatched until the blocker is done.
MC handles this natively with `depends_on` and `is_blocked`.

### Contribution (Contributes-to)
```
"[qa_test_def] Implement middleware" ──contributes_to──→ "Implement middleware"
```
The contribution task's output is propagated to the target task's
context. NEW relation type.

### Spawned-from
```
Epic "Add auth system" ──spawned──→ Subtask "Design data model"
```
Traceability: this task was created from that parent by the PM or
brain. Different from parent/child in that spawned-from records HOW
the task was born (PM breakdown vs brain chain vs agent discovery).

### Related-to
```
"Add auth system" ──related_to──→ "Security audit"
```
Informational relation: these tasks are connected but don't block
each other. Useful for cross-referencing.

---

## Child Task Types

The PO mentioned "X type of new [child] tasks." Different subtask
types serve different purposes:

### Implementation Subtask
Standard subtask from epic breakdown. Has its own stage progression.
Created by PM.

### Contribution Subtask
Created by brain's chain registry when contributions are needed.
Small, focused. One heartbeat cycle.
`contribution_type` and `contribution_target` custom fields.

### Bug / Fix Subtask
Discovered during implementation. Created by the implementing agent
via fleet_task_create. Linked to parent. PM reviews and prioritizes.

### Blocker Subtask
Something blocking progress. Created by PM or agent. Urgent priority.
Must be resolved before parent can advance.

### Research Spike
Time-boxed investigation. Created by PM when a question needs
answering before work can proceed. No deliverable expected — only
findings.

---

## Cowork — Multiple Agents on One Task

Tasks have one OWNER (agent_name) and optional COWORKERS:

```
Task: "Implement auth middleware"
  Owner: software-engineer
  Coworkers: devops (infrastructure), technical-writer (docs)
```

### How Cowork Works
- `coworkers` custom field: list of agent names
- All coworkers see the task in their COWORK TASKS section
- All coworkers can: post comments, create artifacts, fleet_commit
- ONLY the owner can: call fleet_task_complete
- Brain dispatches to owner; notifies coworkers
- Trail records who did what (commits attributed to committer)
- Completion claim lists all contributors' work

### When Cowork Happens
- Task has both code and infrastructure components
- Task needs documentation alongside implementation
- Crisis response: fleet-ops + DevSecOps cowork
- Epic breakdown: PM + architect cowork to plan subtasks

---

## Transfer Protocol

When a task moves from one agent to another:

### Transfer Flow
1. Source agent completes their stage work (e.g., architect finishes
   design at reasoning stage)
2. PM or brain triggers transfer: agent_name changes
3. Brain packages transfer context:
   - Source agent's artifacts (design plan, analysis, investigation)
   - Source agent's comments (decisions, rationale)
   - Source agent's contributions (design_input, security_req, etc.)
   - Current stage and readiness
4. Transfer context written to receiving agent's task-context.md
5. Event: fleet.task.transferred
6. Trail records: "Transferred from {source} to {target} at stage
   {stage}, readiness {readiness}%"

### Receiving Agent's Context
```
## TRANSFER CONTEXT
This task was transferred from architect at reasoning stage (80%).

### What architect provided:
- Design plan: {plan summary}
- Target files: {file list}
- Constraints: {constraint list}
- Approach: {approach description}

### What's expected of you:
Continue from reasoning stage. The plan is above. Your job is to
refine it with your expertise and advance toward work stage.
```

---

## Trails — The Complete Audit Record

Every task accumulates a trail — the chronological record of
everything that happened:

```
TRAIL for task "Implement auth middleware":

[2026-03-28 10:00] CREATED by PM. Type: subtask. Parent: "Add auth system"
[2026-03-28 10:00] ASSIGNED to architect. Stage: analysis. Readiness: 10%
[2026-03-28 10:30] STAGE: analysis → investigation. Readiness: 10% → 30%
  Authorized by: PM. Analysis document: complete.
[2026-03-28 11:00] STAGE: investigation → reasoning. Readiness: 30% → 50%
  Authorized by: PM. Investigation document: 3 options explored.
[2026-03-28 11:00] CHECKPOINT: 50%. PO notified.
[2026-03-28 11:15] CONTRIBUTION: qa-engineer posted qa_test_definition (5 criteria)
[2026-03-28 11:20] CONTRIBUTION: devsecops-expert posted security_requirement
[2026-03-28 11:30] STAGE: reasoning. Readiness: 50% → 88%
  Plan artifact: complete. All contributions received.
[2026-03-28 11:35] GATE REQUEST: readiness 90%. Routed to PO.
[2026-03-28 12:00] PO GATE: APPROVED. Readiness: 88% → 99%.
[2026-03-28 12:00] TRANSFER: architect → software-engineer. Stage: work.
[2026-03-28 12:05] DISPATCHED to software-engineer.
[2026-03-28 12:30] COMMIT: feat(auth): add JWT middleware [abc12345]
[2026-03-28 12:45] COMMIT: test(auth): add middleware tests [abc12345]
[2026-03-28 13:00] COMPLETED: fleet_task_complete called.
  PR: github.com/owner/repo/pull/42. Status → review.
[2026-03-28 13:05] QA VALIDATION: 5/5 predefined tests addressed. ✓
[2026-03-28 13:10] SECURITY REVIEW: no findings. ✓
[2026-03-28 13:15] FLEET-OPS REVIEW: approved. Trail complete. Verbatim match.
[2026-03-28 13:15] STATUS: review → done.
[2026-03-28 13:15] PARENT UPDATED: "Add auth system" — 2/4 children done.
```

The trail is reconstructable from board memory entries tagged
`trail` + `task:{id}`. The accountability generator can produce
this trail at any time.

---

## Comments — Typed and Structured

Comments carry metadata beyond just text:

| Comment Type | Posted By | Content |
|-------------|-----------|---------|
| assignment | PM | Assignment details, expectations |
| question | Any agent | Questions to PM or PO |
| progress | Working agent | Progress update with details |
| finding | Analysis agent | Analysis/investigation finding |
| contribution | Contributing agent | Structured contribution data |
| decision | PO/PM | Strategic decision with rationale |
| review | Fleet-ops | Review decision with specifics |
| validation | QA | Test validation results |
| security_review | DevSecOps | Security review findings |
| rejection | Fleet-ops/PO | Rejection with specific feedback |
| regression | PO | Readiness regression with reason |
| gate_request | PM | Gate request with evidence |
| gate_decision | PO | Gate approval/rejection |

Each comment type produces a different trail event. The accountability
generator reads typed comments to verify process adherence.

---

## Mentions — Structured Routing

When a comment or chat mentions an agent:
- `@project-manager` → PM sees it in MESSAGES section
- `@architect` → Architect sees it with task context
- `@human` or `@po` → ntfy notification to PO
- `@lead` → Fleet-ops sees it
- `@all` → Every agent sees it

Mentions route through board memory tags (`mention:{agent_name}`).
The brain includes mentioned messages in the target agent's heartbeat
pre-embed. The mention is NOT just a notification — it includes the
task context so the recipient understands what they're being asked.

---

## Events Emitted Throughout Lifecycle

Every lifecycle transition emits events that feed the chain registry:

```
Task birth:        fleet.task.created
Assignment:        fleet.task.assigned
Dispatch:          fleet.task.dispatched
Stage change:      fleet.methodology.stage_changed
Readiness change:  fleet.methodology.readiness_changed
Checkpoint:        fleet.methodology.checkpoint_reached
Gate request:      fleet.gate.requested
Gate decision:     fleet.gate.decided
Contribution:      fleet.contribution.posted
Transfer:          fleet.task.transferred
Commit:            fleet.task.commit
Completion:        fleet.task.completed
Review start:      fleet.review.started
QA validation:     fleet.review.qa_validated
Security review:   fleet.review.security_completed
Approval:          fleet.approval.approved
Rejection:         fleet.approval.rejected
Regression:        fleet.methodology.readiness_regressed
Phase advance:     fleet.phase.advanced
Phase regress:     fleet.phase.regressed
Parent evaluated:  fleet.task.parent_evaluated
Done:              fleet.task.done
```

Each event triggers chain handlers. The brain dispatches them
through the chain registry. Notifications route to correct channels.
Trail events are recorded.

---

## How Operational Modes Affect the Lifecycle

### full-autonomous
Full lifecycle active. All stages, gates, contributions, reviews.

### project-management-work
Only PM and fleet-ops advance tasks. Other agents work only on
assigned in_progress tasks. No new contributions created.

### local-work-only
No new dispatches. In-progress tasks continue. No new gates or
phase decisions.

### finish-current-work
Complete in_progress tasks, process reviews, then stop. No new
inbox → in_progress transitions.

### work-paused
No lifecycle transitions. Tasks frozen in current state.

---

## Data Model Summary

### Custom Fields on Task
```
task_type:           epic/story/task/subtask/bug/spike/blocker/request/concern
task_stage:          conversation/analysis/investigation/reasoning/work
task_readiness:      0-100 (integer)
delivery_phase:      ideal/conceptual/poc/mvp/staging/production
phase_progression:   standard/release/custom
agent_name:          assigned agent
parent_task:         parent task ID
contribution_type:   qa_test_def/design_input/security_req/ux_spec/etc.
contribution_target: target task ID
coworkers:           list of agent names
story_points:        1/2/3/5/8/13
requirement_verbatim: PO's exact words
project:             which project
branch:              git branch
pr_url:              PR link
security_hold:       true/false
plan_id:             sprint/plan grouping
```

### Relations
```
parent_task:        parent/child hierarchy
depends_on:         blocking dependency
contribution_target: contribution relation
spawned_from:       creation traceability (may use parent_task + auto_created)
related_to:         informational relation (board memory tags)
```

---

## Open Questions

- How many simultaneous in_progress tasks can an agent have?
  (Currently 1 via dispatch gate. Cowork tasks are additional.)
- Should contribution tasks count toward agent "busy" status?
  (They're small — maybe agents can have 1 main task + N contribution
  tasks?)
- How do we handle tasks that span multiple sprints?
  (Task stays in_progress across sprint boundary?)
- Should there be a "cancelled" status? (Task no longer needed)
- How do we handle requirement changes mid-task?
  (Verbatim changes → readiness regresses → stages restart?)