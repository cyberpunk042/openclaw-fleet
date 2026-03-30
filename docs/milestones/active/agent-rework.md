# Agent Rework — Making 10 Agents Alive

**Date:** 2026-03-30
**Status:** Design — from live testing findings
**Scope:** Rewrite every agent's heartbeat, context, and task handling
to use the systems we built

---

## PO Requirements (Verbatim)

> "Lets do a massive review and rework and make sure all agent start with
> the right data and context and tools and standards and directives and
> everything that make them an alive employee..."

> "Its not just about during task, its about your imprint and what is
> related to your imprint and the state and aliveness of it..."

> "Every agent must have an adapted task handling and heartbeat."

> "they will need to be able to work through the stage and iterate through
> their ops board tasks and add their segments and artifact and inprint
> everywhere"

> "it must be pre-embedded into its heartbeat with not only the ocmc board
> but also the related plane data if connected and existing."

> "just like the PM would probably talk to the architect and the software
> engineer or whoever of concern in order to move forward the progress of
> the tasks."

---

## The Problem Found in Live Testing

6 tasks sitting in inbox. Nobody assigning them. Nobody working on them.
PM is online but doesn't assign agents. fleet-ops is online but doesn't
manage the board. Agents heartbeat but don't DO their jobs.

Root cause: every agent's heartbeat was written BEFORE the methodology
system, teaching system, immune system, transpose layer, and context
system existed. Agents don't know about stages, readiness, artifacts,
verbatim requirements, or progressive work.

---

## What Every Agent Needs

### Pre-Embedded Context
- Role identity and responsibilities
- Current fleet state (mode, phase, backend)
- Assigned tasks with stage + readiness
- Messages and directives
- Role-specific data (PM gets unassigned count, fleet-ops gets approval count)

### Heartbeat That Does The Job
- First call: `fleet_heartbeat_context()` for role-specific awareness
- Check messages, directives, events
- Role-specific actions (PM assigns, fleet-ops reviews, architect designs)
- Progressive work on in-progress tasks
- Communication with other agents when needed

### Task Handling Through Stages
- Read task context: `fleet_task_context(task_id)`
- Follow methodology protocol for current stage
- Create/update artifacts progressively
- Check completeness, suggest readiness increases
- Leave traces (comments, events, sub-tasks)

---

## Per-Agent Rework

### project-manager (THE DRIVER)

The PM is the most critical agent. It drives the board.

HEARTBEAT must include:
- Check unassigned inbox tasks → ASSIGN agents based on task content + role
- Check task quality → rewrite vague tasks with clear requirements
- Set task_stage and initial readiness
- Set verbatim requirements (from PO directives or Plane issues)
- Check Plane sprint data → pull priorities to OCMC board
- Break down epics into stories/tasks via fleet_task_create
- Track sprint velocity
- Communicate with agents about their assignments
- Report to PO on progress

PRE-EMBEDDED: unassigned task count, sprint progress, Plane sprint data,
blocked task list, agent availability

### fleet-ops (THE BOARD LEAD)

fleet-ops manages quality, reviews, and board health.

HEARTBEAT must include:
- Process pending approvals with real review (not rubber stamps)
- Check methodology compliance — are agents following their stage protocol?
- Check readiness progression — are tasks advancing?
- Detect stale tasks, stuck agents, quality issues
- Manage the review queue
- Respond to escalations
- Budget monitoring

PRE-EMBEDDED: approval queue, review count, health alerts, budget status

### architect

HEARTBEAT must include:
- Design review for tasks in analysis/investigation stages
- Complexity assessment for new tasks
- Architecture guidance for implementation tasks
- Progressive artifact work on design documents
- Communication with PM and developers about approach

PRE-EMBEDDED: design tasks needing review, complexity flags

### devsecops-expert

HEARTBEAT must include:
- Security review for PRs and completed tasks
- Dependency audit
- Infrastructure health check
- Security findings reporting

PRE-EMBEDDED: security tasks, PR review queue

### software-engineer, devops-expert, qa-engineer, etc.

HEARTBEAT must include:
- Check assigned tasks and their stages
- Follow methodology protocol for current stage
- Progressive artifact work
- Report progress, blockers
- Communicate with PM and peers

PRE-EMBEDDED: assigned tasks with stage + readiness

---

## What Needs Building

1. Rewrite PM HEARTBEAT.md — the most critical, drives everything
2. Rewrite fleet-ops HEARTBEAT.md — quality and review
3. Rewrite architect HEARTBEAT.md — design and complexity
4. Rewrite devsecops HEARTBEAT.md — security
5. Rewrite worker HEARTBEAT.md template — all other agents
6. Update agent.yaml for each agent — mission, capabilities
7. Create/update CLAUDE.md per agent — project-specific rules
8. Wire pre-embedded data into gateway heartbeat delivery
9. Test each agent's heartbeat LIVE — one at a time
10. Verify the fleet operates as a team

This is 100+ live tests once agents are reworked.