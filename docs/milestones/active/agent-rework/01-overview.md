# Agent Rework — Overview

**Date:** 2026-03-30
**Status:** Design — from live testing findings
**Scope:** Every agent in the fleet needs reworking to use the systems
we built and actually do their job

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

> "Its important that the main first mission is to make localAI functional
> and then make it more and more reliable to offload as much as possible"

> "the orchestrator should be waking the project-manager and the fleet-ops
> if there are items in the Inbox unassigned then it would instantly
> heartbeat and the project manager heartbeat above else is about the
> level of effort of a task for anyone"

> "project-manager work being in its process attached to its heartbeat
> like even its handling a task for unblocking for whatever reason like
> review or whatnot"

---

## What Live Testing Found

6 tasks in inbox. Nobody assigning. Nobody working. PM and fleet-ops
online but not acting. Zero heartbeat events producing work. Agents
heartbeat but only report HEARTBEAT_OK.

Root cause: agents don't know about the new systems. Heartbeats written
before methodology, immune system, teaching system, transpose layer,
context system, and control surface existed.

---

## What "Alive Employee" Means

An alive employee:
- Has their own imprint — identity, responsibilities, expertise
- Knows the state of their work and the fleet
- Gets FULL context pre-embedded — not compressed, not requiring calls
- Does their job during heartbeat — PM assigns, fleet-ops reviews,
  architect designs, engineers implement
- Works through methodology stages progressively
- Builds artifacts and leaves traces
- Communicates with colleagues
- Follows standards
- Responds to directives
- Iterates across cycles — picks up where they left off

---

## What Needs to Change

### Pre-Embedded Data (NOT compressed)

Each agent gets their FULL role-specific data pre-embedded before they
even start thinking. Not a summary. Not a compact version. The FULL
data they need.

The pre-embed module needs rework — it currently produces 300-char
summaries. That's the compression disease. It should deliver the full
context assembly output in a format the agent reads directly.

### Orchestrator Waking

The orchestrator must WAKE the PM and fleet-ops when:
- Unassigned tasks in inbox → wake PM to assign
- Pending approvals → wake fleet-ops to review
- This means sending a gateway message that triggers their heartbeat

Currently: orchestrator just sends IRC notification. Must trigger
actual agent heartbeat via gateway.

### Heartbeats Per Role

Each role needs a completely different heartbeat. Not a template with
minor variations. A deeply role-specific heartbeat that reflects what
this specific employee does.

### Task Handling

Every agent must know about methodology stages. Their task handling
must follow the protocol for the current stage. They must build
artifacts progressively. They must track completeness.

### Inter-Agent Communication

Agents must talk to each other. PM talks to architect about design.
Architect talks to engineers about implementation. fleet-ops talks
to everyone about quality. This happens through fleet_chat, task
comments, and board memory.

---

## Documents in This Series

1. **01-overview.md** — this document
2. **02-pre-embedded-data.md** — full context delivery, not compressed
3. **03-orchestrator-waking.md** — trigger agent heartbeats on demand
4. **04-project-manager.md** — PM role, responsibilities, heartbeat
5. **05-fleet-ops.md** — fleet-ops role, responsibilities, heartbeat
6. **06-architect.md** — architect role, responsibilities, heartbeat
7. **07-devsecops.md** — security role, responsibilities, heartbeat
8. **08-workers.md** — engineer roles, QA, devops, writer, UX
9. **09-inter-agent-comms.md** — how agents communicate and collaborate
10. **10-standards-integration.md** — how standards are enforced per role
11. **11-plane-integration.md** — Plane data in agent context
12. **12-milestones.md** — full milestone breakdown
13. **13-live-test-plan.md** — 100+ live tests to verify agents work