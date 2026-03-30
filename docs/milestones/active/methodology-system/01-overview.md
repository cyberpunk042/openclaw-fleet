# Methodology System — Overview

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Scope:** The protocols that govern how agents work through phases,
the custom fields that track progress, and the task readiness system

---

## PO Requirements (Verbatim)

> "we are going to need Protocols and to have the AI respect those
> protocols and make sure we can watch them following those protocol."

> "If I take a task unready I must talk with the PO till he tell me its
> ready.. in conversation protocol and/or analysis protocol and/or
> investigation protocol, till it can be in reasoning and/or work protocol
> and whatnot."

> "The increase of Readiness has to come from a clear evaluation and
> confirmed with the PO."

> "TASK READINESS = CUSTOM FIELD. (ON THE BOARD AND ON THE PROJECT
> MANAGEMENT....)"

> "we will need a series of new Custom Fields for OCMC and Plane"

> "the only moment when you can write work would be when the readiness
> is at 99 or 100%."

> "they can present me research and analysis document or planning document
> or investigation documents and whatnot and that it can be iterative."

> "I am the PO"

> "Me first then PM then people individually to some degree with my
> confirmation and on their own tasks."

---

## What the Methodology System Is

The methodology system defines HOW agents work. It provides the
protocols for each phase of work, the custom fields that track where
a task is in its journey, and the readiness system that gates execution.

It is separate from the immune system (which catches agents when they
DON'T follow methodology) and the teaching system (which educates agents
on methodology).

---

## Methodology = Stage Custom Field + Protocol Per Stage

> "the methodologies ? its just linked to another custom field its relative
> to the stage of work on a task / issue or module, when in that stage you
> need to respect the current protocol that relate to the current phase of
> the task."

The methodology system is a custom field that tracks the stage of work
on a task, issue, or module. Each stage has a corresponding protocol.
When you're in that stage, you respect that protocol.

This is not just "thinking vs working" — it's what KIND of thinking and
what KIND of work. Analysis is a different kind of thinking than
investigation. Document production is a different kind of work than
code production. Each stage has its own methodology checks specific to
the task/module requirements.

> "not only not confusing work with thinking but what kind of thinking and
> what kind of work based of this thinking if there is need for documents
> for example"

> "as the stage passes their methodology checks per the tasks / module
> requirements then it can do the next stage till it reaches the most
> advanced stage and will most likely be the time to pass to 99 or 100%
> readiness."

### Stage Progression

Tasks progress through stages. Each stage has methodology checks. When
the checks pass for the current stage (per the task/module requirements),
the task can advance to the next stage. The stages progress toward
readiness — the most advanced stage is when readiness reaches 99-100%.

Not every task goes through every stage. A simple task with clear
requirements may skip early stages. A complex vague task needs every
stage. The task/module requirements determine which stages are needed
and what checks each stage requires.

### Methodology Checks Are Per-Task, Not Generic

The checks are specific to the task and module, not the same for every
task. An epic about building the immune system has different analysis
checks than a bug fix on the sync worker. The methodology system must
support task-specific and module-specific check definitions.

What this looks like in practice:
- A task's requirements (or the module it belongs to) define which
  stages are needed and what each stage's completion criteria are
- An epic might require: conversation (PO alignment) → analysis
  (codebase examination) → investigation (research options) → reasoning
  (architecture plan) → work (implementation)
- A bug fix might require: analysis (reproduce and trace) → reasoning
  (fix plan) → work (fix and test)
- A spike/research task might require: conversation → investigation →
  reasoning (findings document) — no work stage at all
- Each stage's checks are defined per task type and can be customized
  per module

This means the methodology system needs:
- Default stage requirements per task type (epic, story, task, bug, spike)
- Module-level overrides (the immune system module might require deeper
  investigation than a documentation module)
- Task-level overrides (PO can add or skip stages for any specific task)
- Check definitions that reference the task's verbatim requirement
  and acceptance criteria

### The Protocols

Each stage has a protocol:

### Conversation Protocol
How agents discuss with the PO to understand requirements. The agent
extracts knowledge and meaning from the PO. Does NOT produce finished
work.

### Analysis Protocol
How agents analyze problems, the codebase, the context. Produces
analysis documents — iterative, work-in-progress.

### Investigation Protocol
How agents research solutions, explore options. Produces investigation
and research documents.

### Reasoning Protocol
How agents think through approaches, make decisions, plan
implementation. Produces planning documents.

### Work Protocol
How agents execute — write code, produce artifacts, create PRs. The
only protocol where finished deliverables are produced. Only entered at
99-100% readiness.

---

## Module-Level Methodology

> "its relative to the stage of work on a task / issue or module"

The PO specified that methodology applies to MODULES too, not just
individual tasks. A module in Plane is a grouping of related issues —
like "Immune System" or "Sync Worker" or "Control Surface."

Module-level methodology means:
- The module itself has a stage (conversation, analysis, investigation,
  reasoning, work)
- The module stage represents the overall phase of that body of work
- Individual tasks within the module can be at different stages, but
  the module stage provides the overall context
- A module in "investigation" phase means the team is still exploring
  solutions for that body of work — individual tasks within it might
  be at conversation (clarifying specific requirements) or analysis
  (examining specific code areas)

This is how the PO manages large bodies of work. The immune system
is a module. It went through conversation (this session's discussion),
investigation (the devops-control-plane and research analysis), and is
now in reasoning (planning milestones). Individual tasks within it
will enter their own stages as the module progresses.

Module-level stage tracking uses the same custom field (task_stage)
but on Plane modules rather than individual issues.

---

## Task Readiness

> "TASK READINESS = CUSTOM FIELD. (ON THE BOARD AND ON THE PROJECT
> MANAGEMENT....)"

Task readiness is a percentage (0-100) tracked as a custom field on
both OCMC and Plane.

- Work protocol is only entered at 99-100% readiness
- Lower readiness levels correspond to earlier protocols
- Readiness increases through clear evaluation confirmed with the PO
- Agents can leave comments to discuss readiness with the PO
- The PO confirms, readiness increases

**Who can increase readiness:**
- PO — any value, ultimate authority
- PM — with PO confirmation
- Individual agents — on their own tasks, to some degree, with PO
  confirmation. They communicate with the PO through comments.

**The doctor has nothing to do with readiness.** (PO explicitly stated)

---

## Custom Fields

The methodology system needs new custom fields on OCMC and Plane.
Identified so far:

### task_readiness
- Type: integer (percentage, 0-100)
- On: OCMC board AND Plane issues
- Visibility: always
- Default: 0

### requirement_verbatim
- Type: text_long
- On: OCMC board AND Plane issues
- Visibility: always
- Read-only for agents, writable by PO and PM

### Additional fields — to be identified
More fields will emerge as each protocol is designed. This is a series
of new custom fields, not just two.

Detailed field definitions in: `new-custom-fields.md`

---

## The PO Role

> "I am the PO"

The PO (Product Owner) is the user. The PO:
- Defines requirements (verbatim — the first cure)
- Is the ultimate authority on what is being asked
- Confirms readiness increases
- Receives questions about requirements from any agent
- Participates in conversation protocol when agents need alignment

**Requirement questions always go to PO.**

The PM manages work but does not define requirements. PM asks the PO
when uncertain about requirements, same as any agent.

Technical questions (how to implement) can go between agents. Requirement
questions (what to implement) go to PO.

---

## Observability

> "make sure we can watch them following those protocol"

Each protocol must be observable:
- Which protocol an agent is currently in
- What the agent produced during that protocol
- How readiness changed and who authorized changes
- Whether protocols were followed or skipped

Specific observability mechanisms to be designed per protocol.

---

## Documents in This Series

1. **01-overview.md** — this document
2. **02-conversation-protocol.md** — how agents discuss with PO
3. **03-analysis-protocol.md** — how agents analyze the problem space
4. **04-investigation-protocol.md** — how agents research solutions
5. **05-reasoning-protocol.md** — how agents plan their approach
6. **06-work-protocol.md** — how agents execute (only at 99-100% readiness)
7. **07-standards-and-examples.md** — what "done right" looks like for every artifact type
8. **new-custom-fields.md** — field definitions for OCMC and Plane

---

## Open Questions

- What readiness percentage maps to which protocol?
- What are the specific rules for each protocol?
- Can an agent move backward through protocols?
- What artifacts does each protocol produce?
- How is protocol observability tracked? Custom fields? Events? Both?
- How do these protocols relate to the existing task lifecycle
  (PRE/PROGRESS/POST)?
- How does the sync worker handle the new custom fields between OCMC
  and Plane?