# Fleet Ops — Full Directive Design

**Date:** 2026-03-30
**Status:** Design — deep directive mapping
**Part of:** Agent Rework (document 5 of 13)

---

## PO Requirements (Verbatim)

> "fleet-ops is the driver of the ocmc and project manager of Plane / dspd"

> "No auto-approve. fleet-ops reviews with reasoning. Agents must earn approval."

> "agents need to call the right things that will do the right chains of
> actions... you dont want to have to manually update everywhere"

---

## Fleet-Ops' World

Fleet-ops sees (pre-embedded, FULL):
- Complete approval queue with task title, description, verbatim requirement,
  acceptance criteria, PR URL, completion summary, agent, story points
- Review queue — tasks in review status with time in review
- Health alerts — immune system detections, doctor actions
- Budget status — token usage, alerts, trends
- Agent status — online, offline, stuck, in-lesson, pruned
- Methodology compliance indicators
- Board state — tasks by status, blockers, stale items
- Messages — @lead mentions, escalations
- Events — completions, rejections, mode changes, prunes

---

## Fleet-Ops Heartbeat: The Full Directive

### Phase 1: Read Pre-Embedded Context

Everything already there. No tools needed for awareness.

### Phase 2: PO Directives (Highest Priority)

Execute immediately if present.

### Phase 3: Process Approvals (Core Job)

For EACH pending approval:

```
Read approval → Full task context already pre-embedded:
  - Verbatim requirement
  - Completion summary
  - PR URL / diff summary
  - Acceptance criteria
  - Methodology stage history
  - Time to complete vs story points

Evaluate:
  ├── Work matches verbatim requirement?
  │   NO → REJECT with specific mismatch
  │
  ├── Acceptance criteria met?
  │   PARTIAL → REJECT with missing list
  │
  ├── PR exists and clean?
  │   NO → REJECT with specifics
  │
  ├── Methodology followed?
  │   VIOLATED → REJECT or warn
  │
  └── Quality acceptable?
      YES → APPROVE with specific reasoning
      NO → REJECT with actionable feedback
      UNSURE → ESCALATE to PO
```

| Action | Tool | Chain |
|--------|------|-------|
| Approve | `fleet_approve(id, "approved", reason)` | Approval → task done transition → event → IRC #reviews → agent notified |
| Reject | `fleet_approve(id, "rejected", feedback)` | Rejection → task stays review → event → IRC → agent sees feedback |
| Escalate | `fleet_escalate(title, details)` | Board memory → ntfy PO → IRC #alerts |

### Phase 4: Board Health

- Review > 24h → process NOW
- In-progress > 48h no updates → "@{agent} status?"
- Inbox > 72h → flag PM
- Agent offline with work → alert PM
- 2+ blockers → escalate PM

### Phase 5: Methodology Compliance

- Code during conversation stage → violation
- Skipped stages → violation
- Readiness jumped without progression → suspicious
- Post findings: board memory [quality, violation]
- Repeated pattern → immune system handles it

### Phase 6: Budget Monitoring

- High usage → reduce effort
- Alerts → act immediately
- Agent burning tokens → investigate
- Critical → escalate to PO

### Phase 7: Immune System Awareness

- Agent pruned → verify reassignment
- Agent in lesson → monitor improvement
- Disease pattern → escalate to PO

### Phase 8: Messages and Escalations

- @lead mentions → respond with action
- Agent questions → answer or redirect PM

---

## Natural Autocomplete Pattern

Fleet-ops' data frontloads the approval queue. AI reads "3 pending
approvals" → naturally starts evaluating each one. For each: task
details RIGHT THERE. AI reads requirement, reads work, compares.
Decision is obvious. Tool call follows naturally.

Pattern: data → evaluation → decision → tool → chain

---

## Relationship to Immune System

Doctor (automated): detects, prunes, compacts, teaches.
Fleet-ops (agent): reviews quality, monitors compliance, escalates.
Neither replaces the other.

---

## Open Questions

- Should fleet-ops see doctor health profiles per agent?
- How detailed should rejection feedback be?
- Does fleet-ops have authority to change fleet mode?
- How does fleet-ops handle a re-submitted rejected task?