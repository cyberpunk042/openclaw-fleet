# Analysis Protocol

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Part of:** Methodology System (document 3)

---

## PO Requirements (Verbatim)

> "If I take a task unready I must talk with the PO till he tell me its
> ready.. in conversation protocol and/or analysis protocol and/or
> investigation protocol, till it can be in reasoning and/or work protocol
> and whatnot."

> "they can present me research and analysis document or planning document
> or investigation documents and whatnot and that it can be iterative."

---

## What the Analysis Protocol Is

The analysis protocol governs how agents analyze problems, the codebase,
the context around a task. The agent examines what exists, understands
the current state, and documents its findings.

This is distinct from conversation (which is about understanding
requirements from the PO) and investigation (which is about researching
solutions). Analysis is about understanding the problem space and the
current state.

---

## What the Agent Does in Analysis Protocol

1. **Reads and examines.** The codebase, the existing implementation,
   the architecture, the dependencies, the related systems.

2. **Produces analysis documents.** Iterative, work-in-progress.
   Presented to PO for review. Documents what exists, what the current
   state is, what the implications are.

3. **Does NOT produce solutions.** Analysis is about understanding the
   problem, not solving it. Solutions come in reasoning protocol.

4. **Does NOT produce code.** Analysis produces documents, not
   deliverables.

---

## When an Agent Enters Analysis Protocol

- After conversation has established what's being asked (requirements
  are understood)
- The agent needs to understand the current state before it can
  investigate solutions or reason about approach
- The PO or the task directs the agent to analyze first

---

## Artifacts

Analysis documents may include:
- Current state assessment — what exists today
- Codebase examination — relevant files, components, architecture
- Impact analysis — what would be affected by changes
- Gap analysis — what's missing vs what's needed
- Dependency mapping — what depends on what

All iterative. All presented to PO. All work-in-progress until
confirmed.

---

## Analysis vs Investigation — The Boundary

Analysis looks INWARD — at what exists. It examines the codebase, the
current state, the architecture. It answers "what do we have?"

Investigation looks OUTWARD — at what's possible. It researches
solutions, explores options, examines prior art. It answers "what could
we do?"

Example from this session: when we needed to understand the OCMC header
for the control surface, the investigation of DashboardShell.tsx —
reading the component, understanding the structure, identifying where
controls could go — that was analysis. Researching AI agent failure
modes and the devops-control-plane rules — that was investigation.

In practice, an agent doing analysis reads code, examines files,
traces dependencies. An agent doing investigation reads documentation,
searches for patterns, explores external solutions.

---

## Examples of Analysis Artifacts

**Current state assessment:**
"The OCMC board currently has 14 custom fields. MC supports 9 field
types: text, text_long, integer, decimal, boolean, date, date_time,
url, json. The orchestrator reads custom fields in _parse_task() and
checks agent_name, project, complexity before dispatch."

**Codebase examination:**
"DashboardShell.tsx has three sections in the header: left (BrandMark,
260px), center (OrgSwitcher, flex-1), right (UserMenu, ml-auto). The
center section has room for additional components after the OrgSwitcher."

**Impact analysis:**
"Adding task_readiness to the dispatch filter affects
fleet/cli/orchestrator.py (dispatch logic), fleet/infra/mc_client.py
(field parsing), fleet/core/models.py (TaskCustomFields). No other
systems read this field currently."

These are real examples from this session's work — the analysis that
was done (sometimes well, sometimes poorly) to ground design decisions.

---

## Open Questions

- What readiness percentage range corresponds to analysis protocol?
- What's the expected format for analysis documents? Markdown? Task
  comments? Board memory?
- Can analysis happen in parallel with conversation? (Agent analyzes
  while waiting for PO response on conversation questions?)
- How does the PO review and confirm analysis findings?
- What methodology checks determine that analysis is complete for a
  given task type?
- What triggers transition from analysis to investigation or reasoning?