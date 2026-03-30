# Work Protocol

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Part of:** Methodology System (document 6)

---

## PO Requirements (Verbatim)

> "the only moment when you can write work would be when the readiness
> is at 99 or 100%."

> "If I take a task unready I must talk with the PO till he tell me its
> ready.. in conversation protocol and/or analysis protocol and/or
> investigation protocol, till it can be in reasoning and/or work protocol
> and whatnot."

---

## What the Work Protocol Is

The work protocol governs how agents execute — write code, produce
deliverables, create PRs, commit changes. This is the only protocol
where finished work is produced.

An agent can only enter work protocol when task readiness is at 99-100%.
Everything before this — conversation, analysis, investigation,
reasoning — prepares the agent to work correctly.

---

## What the Agent Does in Work Protocol

1. **Executes the plan.** The plan was established and confirmed in
   reasoning protocol. The agent follows it.

2. **Produces deliverables.** Code, PRs, configuration changes,
   documentation — whatever the task requires.

3. **Follows the methodology.** Conventional commits, proper testing,
   task lifecycle stages (PRE/PROGRESS/POST), required MCP tool calls.

4. **Stays within scope.** Works from the verbatim requirements and the
   confirmed plan. Does not deviate. Does not add unrequested scope.

5. **Is monitored by the immune system.** The doctor watches for disease
   during work — deviation, laziness, confident-but-wrong, scope creep.

---

## Entry Conditions

- Task readiness at 99-100%
- PO has confirmed requirements are understood
- Plan has been established and confirmed
- Verbatim requirements are populated on the task

---

## Exit Conditions

- Work is complete per acceptance criteria
- PR submitted (if code task)
- Task moved to review
- All required artifacts produced

---

## Relationship to Immune System

The work protocol is where the immune system is most active. During
conversation, analysis, investigation, and reasoning, the agent is
THINKING — producing iterative documents, not deliverables. Disease
during thinking is corrected through conversation with PO.

During work, the agent is PRODUCING — writing code, committing changes.
Disease during production is caught by the immune system's doctor.
The doctor can prune, force compact, or trigger rules reinjection if
the agent starts drifting during work.

---

## Relationship to Existing Fleet Systems

Work protocol maps to much of what the fleet already has:
- Task lifecycle (PRE/PROGRESS/POST stages)
- MCP tools (fleet_task_accept, fleet_commit, fleet_task_complete)
- Skill enforcement (required tools per task type)
- Review chain (fleet-ops reviews completed work)
- PR workflow (branch, commit, PR, review, merge)

The methodology system formalizes what exists and adds the pre-work
protocols that are currently missing.

---

## Mapping to Existing Fleet Task Lifecycle

The fleet already has a task lifecycle in `fleet/core/task_lifecycle.py`
with three stages: PRE, PROGRESS, POST. The work protocol encompasses
and extends this:

| Existing Stage | What It Does | Work Protocol Enhancement |
|---------------|-------------|--------------------------|
| **PRE** | Agent must call fleet_read_context, fleet_task_accept with plan | Plan already validated during reasoning protocol. PRE confirms the agent is starting from the confirmed plan. |
| **PROGRESS** | Agent commits code, calls fleet_commit | Standards enforcement — conventional commits, proper testing. Immune system monitors for disease during this stage. |
| **POST** | Agent calls fleet_task_complete, PR created, review gates populated | Completion claim checked against methodology standards — acceptance criteria, required artifacts, verbatim requirement addressed. |

The work protocol adds:
- Entry gate: readiness must be 99-100% (doesn't exist today)
- Plan must reference verbatim requirement (doesn't exist today)
- Stage-aware tool enforcement: MCP tools that are only available
  during work protocol (fleet_commit, fleet_task_complete)
- Immune system monitoring throughout (doesn't exist today)
- Standards for what "complete" looks like (from 07-standards-and-examples.md)

## MCP Tools in Work Protocol

| Tool | Work Protocol Role |
|------|-------------------|
| fleet_read_context | Read task spec including verbatim requirement — always first |
| fleet_task_accept | Plan submission — already validated in reasoning, confirmed here |
| fleet_commit | Commit code — conventional format, task ID reference |
| fleet_task_complete | Completion claim — checked against standards |
| fleet_chat | Communication — status updates to team |
| fleet_alert | Raise issues — blocking problems, discovered risks |
| fleet_escalate | Escalate to human — when agent can't proceed |

Tools NOT available during work protocol that belong to earlier stages:
- fleet_task_create is available (agent may discover need for subtasks)
- But agents should not be doing investigation or analysis work during
  work protocol — that should have been completed in earlier stages

## Review Chain

After fleet_task_complete, the task enters the review chain:
1. fleet-ops reviews the completed work
2. Review checks against the verbatim requirement and acceptance criteria
3. Approved → done
4. Rejected → corrections needed → task may loop back

The immune system monitors the review chain too — a rubber stamp review
(approved in < 30 seconds without reading the diff) is a disease signal.

---

## Open Questions

- Can work protocol loop back to earlier protocols? (Agent realizes
  mid-work that the plan is wrong — does it go back to reasoning?
  To conversation?) The task_stage would need to move backward and
  readiness would decrease.
- How strictly does the agent follow the plan vs adapt as it works?
  Minor adaptations are natural. Major changes suggest the plan was
  wrong and the agent should loop back to reasoning.
- What checkpoints exist during work protocol? The immune system
  monitors continuously but should there be explicit methodology
  checkpoints (e.g., after first commit, after tests pass)?
- How does the PO get visibility into work-in-progress? Through the
  event stream? Through task comments? Through the OCMC UI?