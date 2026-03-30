# Investigation Protocol

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Part of:** Methodology System (document 4)

---

## PO Requirements (Verbatim)

> "If I take a task unready I must talk with the PO till he tell me its
> ready.. in conversation protocol and/or analysis protocol and/or
> investigation protocol, till it can be in reasoning and/or work protocol
> and whatnot."

> "they can present me research and analysis document or planning document
> or investigation documents and whatnot and that it can be iterative."

> "we need to explore the situation and investigate and research and be
> sure we have the right ways to keep a healthy fleet"

---

## What the Investigation Protocol Is

The investigation protocol governs how agents research solutions, explore
options, and investigate approaches. The agent looks outward — at
possibilities, patterns, prior art, technical options.

This is distinct from analysis (which examines what exists) and reasoning
(which decides on an approach). Investigation is about exploring the
solution space.

---

## What the Agent Does in Investigation Protocol

1. **Researches.** Explores options, reads documentation, examines how
   similar problems were solved, looks at what the platform supports.

2. **Produces investigation documents.** Research findings, option
   comparisons, technical explorations. Iterative, presented to PO.

3. **Explores thoroughly.** Does not settle on the first option found.
   Investigates the full landscape before presenting findings.

4. **Does NOT decide.** Investigation presents options and findings.
   Decisions happen in reasoning protocol, confirmed by PO.

5. **Does NOT produce code.** Investigation produces documents, not
   deliverables.

---

## When an Agent Enters Investigation Protocol

- After analysis has established the current state
- The agent needs to explore solutions before reasoning about approach
- The PO directs the agent to investigate
- The task requires research (spike, exploration, technical assessment)

---

## Artifacts

Investigation documents may include:
- Research findings — what was found, sources, evidence
- Option comparison — multiple approaches with tradeoffs
- Technical exploration — how something works, what's possible
- Prior art — how similar problems were solved elsewhere
- Platform capability assessment — what the existing platform supports

All iterative. All presented to PO. The investigation that produced the
immune system research findings (devops-control-plane rules, academic
papers, fleet existing systems) is an example of this protocol in action.

---

## Investigation vs Analysis — The Boundary

Investigation looks OUTWARD. Analysis looks INWARD.

Analysis examines what exists in the codebase and current state.
Investigation researches what's possible — solutions, patterns, prior
art, platform capabilities, external knowledge.

Example from this session:
- Analysis: reading DashboardShell.tsx to understand the header structure
- Investigation: researching the devops-control-plane 24 rules,
  academic papers on AI agent failure modes, the gateway session APIs

Investigation may discover things that change the understanding from
analysis. For example, investigating the gateway APIs revealed that
`sessions.delete`, `sessions.compact`, and `chat.send` already exist —
which changed the analysis of what the doctor needs architecturally.

---

## Examples of Investigation Artifacts

**Research findings:**
The immune system research document (04-research-findings.md) is an
example of investigation output — compiled from the devops-control-plane
rules, academic papers, and practical evidence.

**Platform capability assessment:**
"The MC frontend uses Next.js 16, React 19, Radix UI. Custom fields
support 9 types. SSE streams exist for tasks, memory, agents, approvals.
The OrgSwitcher in the header uses Radix Select — the same component
can be used for fleet control dropdowns."

**Option exploration:**
"Three approaches to rules reinjection: (1) in-session via chat.send,
(2) persistent via context/ files, (3) heartbeat context injection.
Gateway investigation shows options 1 and 2 are supported by existing
APIs."

---

## Open Questions

- What readiness percentage range corresponds to investigation protocol?
- How deep should investigation go? When is it thorough enough?
- Can investigation produce recommendations or is that reasoning's job?
- How does the PO review investigation findings?
- What triggers transition from investigation to reasoning?
- Can investigation reveal that the task requirements need changing?
  (Loop back to conversation protocol?)