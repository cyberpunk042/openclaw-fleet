# Reasoning Protocol

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Part of:** Methodology System (document 5)

---

## PO Requirements (Verbatim)

> "If I take a task unready I must talk with the PO till he tell me its
> ready.. in conversation protocol and/or analysis protocol and/or
> investigation protocol, till it can be in reasoning and/or work protocol
> and whatnot."

---

## What the Reasoning Protocol Is

The reasoning protocol governs how agents think through approaches,
make decisions, and plan implementation. The agent has understood the
requirements (conversation), analyzed the current state (analysis),
explored options (investigation), and now decides on an approach.

This is the last protocol before work. The agent produces plans and
gets PO confirmation before executing.

---

## What the Agent Does in Reasoning Protocol

1. **Decides on an approach.** Based on the requirements, analysis, and
   investigation findings. Makes explicit choices about how to implement.

2. **Produces planning documents.** Implementation plans, design
   decisions, approach documentation. Iterative, presented to PO.

3. **Maps approach to specifics.** Which files, which components, which
   patterns. The plan is concrete enough that execution is
   straightforward.

4. **Gets PO confirmation.** The PO reviews the approach and confirms
   or corrects. Readiness increases toward 99-100%.

5. **Does NOT produce code yet.** Reasoning produces plans, not
   deliverables. Code comes in work protocol.

---

## When an Agent Enters Reasoning Protocol

- After investigation has explored the solution space
- The agent has enough information to make decisions
- Readiness is approaching the threshold for work
- The PO directs the agent to plan its approach

---

## Artifacts

Reasoning documents may include:
- Implementation plan — what to do, in what order
- Design decisions — why this approach over alternatives
- Approach documentation — how it will work
- Task breakdown — if the task needs to be split into subtasks

All iterative. All presented to PO. The PO confirms the approach
before the agent transitions to work protocol.

---

## Relationship to Task Readiness

Reasoning protocol is where readiness should approach 99-100%. The
agent understands what's being asked (conversation), knows the current
state (analysis), has explored options (investigation), and has a plan
(reasoning). If the PO confirms the plan, readiness is at 99-100% and
the agent can enter work protocol.

---

## Reasoning vs Other Stages

Reasoning is where DECISIONS are made. Earlier stages gather information.
Later stages execute decisions.

- Conversation: "What do you want?" → understanding the requirement
- Analysis: "What exists?" → understanding the current state
- Investigation: "What's possible?" → exploring options
- **Reasoning: "What should we do?"** → choosing the approach
- Work: "Do it." → executing the chosen approach

The key output of reasoning is a PLAN — specific enough that execution
is straightforward. The plan maps the requirement to specific files,
components, and changes. It's grounded in analysis and investigation
findings.

---

## Examples of Reasoning Artifacts

**Implementation plan:**
"To add the FleetControlBar to the header:
1. Create FleetControlBar.tsx with three Radix Select dropdowns
2. Modify DashboardShell.tsx to import and render FleetControlBar
   in the center section after OrgSwitcher
3. FleetControlBar reads fleet_config from board snapshot on mount
4. On dropdown change, PATCH board fleet_config
5. Subscribe to SSE for external state changes
Target files: DashboardShell.tsx, FleetControlBar.tsx (new)"

**Design decision:**
"The doctor should run as a step in the orchestrator cycle rather than
a separate daemon, because: the orchestrator already runs every 30s,
the doctor needs the same data the orchestrator already fetches (tasks,
agents, custom fields), and adding a step avoids a new process to manage."

These examples are grounded — they reference specific files, specific
APIs, specific architectural decisions. Not abstract. Not vague.

---

## Connection to fleet_task_accept

The existing `fleet_task_accept` MCP tool is where agents submit their
plan when accepting a task. In the methodology system, this becomes the
formal plan submission point during reasoning protocol:

- Agent produces plan
- Agent calls `fleet_task_accept(plan="...")`
- Plan is checked against verbatim requirement (methodology check)
- If plan passes, PO reviews and confirms
- Readiness increases toward 99-100%
- Agent transitions to work protocol

This connects the existing MCP tool to the methodology system without
building a new mechanism.

---

## Open Questions

- What readiness percentage range corresponds to reasoning protocol?
- How detailed must the plan be before work can start?
- Can reasoning skip back to investigation if the agent realizes it
  needs more research?
- How does the PO confirm the plan? Comment? Readiness field update?
  Both?
- Does reasoning produce formal documents or can it be comment-based?
- What methodology checks validate a plan against the verbatim
  requirement?