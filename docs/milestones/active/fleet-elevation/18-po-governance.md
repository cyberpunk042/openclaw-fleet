# PO Governance Model

**Date:** 2026-03-30
**Status:** Design — PO authority, gates, approval chain
**Part of:** Fleet Elevation (document 18 of 22)

---

## PO Requirements (Verbatim)

> "As much as I can accept a task to move forward in readiness I can
> reject or even regress the progress."

> "This need meticulous thinking logical transition and time for approval
> and even approvals only me can answers."

> "So many in the early stage of question and answer and things no one
> is able to answer and at some point clearly addressed to the PO."

> "the PM always making sure things reach me if I might miss something
> or it detects it requires more attention or general more questions and
> need clarification..."

> "I am the PO"

> "Me first then PM then people individually to some degree with my
> confirmation and on their own tasks."

---

## What This Document Covers

The PO governance model — how the PO (the user) maintains control
over the fleet. The PO is the ultimate authority. They can accept,
reject, or regress. Certain decisions can ONLY be made by the PO.
The PM ensures the PO doesn't miss anything. The fleet operates
under the PO's authority, not autonomously.

---

## The PO's Authority

### What ONLY the PO Can Do
- Approve readiness past 90% (the work gate)
- Approve delivery phase advancement (any phase → next phase)
- Regress readiness to any value at any time
- Regress delivery phase to any earlier phase
- Override fleet-ops approval or rejection decisions
- Change fleet work mode (full-autonomous → paused, etc.)
- Change fleet cycle phase (execution → planning, etc.)
- Post directives that override all other priorities
- Define requirements (verbatim — the anchor for all work)
- Accept or reject the fleet's output

### What the PM Can Do (With PO Confirmation)
- Advance readiness from 0 to 89% (below the PO gate)
- Assign agents to tasks
- Break epics into subtasks
- Set task fields (type, stage, readiness, story_points, phase)
- Route questions to the PO
- Manage sprint planning and execution
- Resolve blockers (within their authority)

### What Agents Can Do (On Their Own Tasks)
- Advance readiness within their current stage's range
  (e.g., analysis stage: 20% → 40%)
- But NOT past stage boundaries without PM involvement
- And NEVER past 90% without PO approval

### What Fleet-Ops Can Do
- Approve or reject work in review
- But PO can override fleet-ops decisions
- Fleet-ops cannot advance readiness past review gates

---

## Strategic Checkpoints

Readiness values 0, 50, and 90 are strategic checkpoints:

### Checkpoint 0% — Task Birth
The task exists but nothing is confirmed. Requirements may be vague.
The PO or PM will clarify through conversation protocol.

### Checkpoint 50% — Direction Confirmed
The task has clear requirements and the direction is confirmed by
the PO. Investigation is complete, options are understood. This is
the "are we building the right thing?" checkpoint.

At 50%: PO is notified. PO can:
- Confirm direction → work continues toward reasoning
- Redirect → requirements change, readiness may regress
- Defer → task deprioritized

### Checkpoint 90% — Plan Confirmed (PO GATE)
The plan exists, references the verbatim requirement, and is ready
for execution. This is the "go build it" gate. ONLY the PO can
approve this.

At 90%: PO MUST approve. No work can begin without this gate.
PO can:
- Approve → readiness advances to 99%, work stage begins
- Reject → readiness regresses, agent returns to reasoning
- Modify → PO adjusts requirements, readiness stays at 90%

---

## Phase Gates

Phase advancement is ALWAYS a PO gate. Moving from POC → MVP,
MVP → staging, staging → production — each requires explicit PO
approval.

### Phase Gate Flow
1. PM assesses phase standards are met
2. PM calls fleet_gate_request with evidence
3. Brain routes to PO (ntfy + IRC #gates + board memory)
4. PO reviews evidence
5. PO decides:
   - Approve → phase advances, new standards apply
   - Reject → stays at current phase, feedback provided
   - Regress → phase goes backward (rare but possible)

---

## Readiness Regression

The PO's most powerful governance tool. At any time, the PO can
regress readiness:

### Minor Regression (99% → 95%)
"Fix this specific issue and resubmit."
- Task stays in current stage
- Agent addresses the issue
- Re-review after fix

### Moderate Regression (99% → 70%)
"The plan needs rethinking."
- Task returns to reasoning stage
- Agent produces new plan addressing PO feedback
- PO re-approves at 90% gate before work resumes

### Major Regression (99% → 30%)
"This doesn't match what I asked for."
- Task returns to analysis stage
- Agent re-examines the problem space
- Full stage progression from analysis → work needed
- Much more expensive, signals fundamental misunderstanding

### Complete Regression (99% → 0%)
"Start over. The understanding is wrong."
- Task returns to conversation stage
- Agent discusses with PO to rebuild understanding
- Full stage progression from conversation → work needed
- Immune system flags: this was a critical failure

### What Regression Records
Every regression is:
- Logged in the task trail (stage, readiness, reason)
- Event emitted: fleet.methodology.readiness_regressed
- Comment posted with PO's specific feedback
- Immune system notified (detection signal if repeated)
- Sprint progress adjusted

---

## The PM as PO Filter

The PM ensures the PO isn't overwhelmed:

### What PM Filters
- Routine status updates → PM handles, PO gets sprint summary
- Agent questions about implementation details → PM answers
- Blocker resolution within PM scope → PM handles
- Simple task assignment decisions → PM decides

### What PM Routes to PO
- Gate requests (readiness 90%, phase advancement)
- Requirement questions (what to build, not how)
- Strategic decisions (priority changes, scope changes)
- Escalations (blockers PM can't resolve)
- Compliance concerns (from accountability generator)
- Security alerts (from DevSecOps)

### How PM Routes
PM doesn't just forward raw data. PM SUMMARIZES and HIGHLIGHTS:

"PO: Task 'Add CI/CD' is at readiness 88%. Plan references your
requirement: 'Add CI/CD to NNRT with GitHub Actions.' Architect
confirmed design. QA predefined 5 tests. All contributions received.
Ready for your 90% gate approval. Decision needed: approve to
proceed to implementation?"

vs.

"PO: task needs review." ← This is lazy routing. The immune system
detects this.

---

## PO Interaction Channels

### Directives (PO → Fleet)
PO posts to board memory with [directive] tag:
- "All agents focus on NNRT this sprint"
- "Architect: review security module before implementation"
- "Pause all non-critical work"

Directives override everything. Brain routes to target agents.
Agents see directives as highest priority in their heartbeat.

### Gate Decisions (PO → Specific Task)
PO approves/rejects via board memory with [gate, po-decision] tag:
- "Approved: task ABC readiness 90%"
- "Rejected: plan doesn't address {verbatim}. Regress to 70%."

Brain processes gate decisions and updates task state.

### Requirements (PO → Task)
PO posts requirements as task comments or updates verbatim field.
Requirements are sacrosanct — agents must not deform them.

### Feedback (PO → Agent/Fleet)
PO corrects agent work via task comments.
Corrections tracked by immune system. 3 corrections = doctor signal.

### ntfy Notifications (Fleet → PO)
PO receives push notifications for:
- Gate requests (readiness 90%, phase advancement)
- Security alerts (critical/high severity)
- Escalations from PM or fleet-ops
- Budget warnings (critical threshold)

---

## Governance in Each Work Mode

### full-autonomous
- Full governance chain active
- All gates enforced
- Agents work, PM routes, PO decides at gates
- Maximum PO engagement at strategic checkpoints

### project-management-work
- Only PM and fleet-ops fully active
- PO involved in planning decisions
- No implementation without PO returning to full-autonomous
- PO works with PM on sprint planning

### local-work-only
- PO is doing manual work
- Fleet continues current tasks only
- No new dispatches, minimal PO interruptions
- Only critical alerts reach PO

### finish-current-work
- Wind-down mode
- Complete and review what's in progress
- PO receives completion notifications
- No new gates or phase decisions

### work-paused
- Fleet frozen
- PO may be making structural changes
- No notifications except critical alerts

---

## Open Questions

- How does the PO approve gates efficiently? (Board memory tag?
  Dedicated Plane comment? Custom UI?)
- Should gate requests have a timeout? (If PO doesn't respond in
  X hours, PM escalates?)
- How does governance work when PO is unavailable for extended periods?
  (Delegate authority to PM for specific scope?)
- Should there be a "PO dashboard" showing all pending decisions?