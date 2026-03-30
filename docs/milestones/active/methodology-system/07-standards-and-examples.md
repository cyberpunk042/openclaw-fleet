# Standards and Examples — What "Done Right" Looks Like

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Part of:** Methodology System (document 7)

---

## PO Requirements (Verbatim)

> "the methodologies will want to enforce the high standards and provide
> examples of those, to be sure we stay structured and consistent and do
> not produce partial outputs."

> "some standards exist but it will evolve too greatly and in general to
> cover the methodologies and all that it involves and requires to work."

> "e.g. A Full Task, a Full Bug, etc...."

---

## What This Is

The methodology system enforces high standards for everything agents
produce. Not just "follow the protocol" but "produce work that meets
THIS standard." Every artifact type has a definition of what "complete"
and "correct" looks like, with examples.

This prevents:
- Partial outputs (agent produces half a task and claims done)
- Sloppy work (agent skips fields, leaves things blank, cuts corners)
- Inconsistency (every agent formats things differently)
- Low quality (agent produces something technically valid but not
  up to standard)

The standards are enforced through methodology checks at each stage.
The immune system detects when standards aren't met. The teaching
system teaches agents what the standards are through adapted lessons
with examples.

---

## Standards Evolve

This is a living system, not a static document. Standards evolve as:
- The fleet works and the PO identifies quality gaps
- New artifact types are created
- Existing standards prove insufficient
- New protocols need their own standards
- The PO's expectations grow as the fleet matures

Standards must be stored in a way that allows evolution — adding new
standards, refining existing ones, deprecating outdated ones. Not
hardcoded.

---

## Artifact Standards — What "Complete" Looks Like

### A Full Task

A task that is ready for work (99-100% readiness) must have:

- **Title:** Clear, specific, actionable. Not vague. Not a goal — an
  action. "Add FleetControlBar component to DashboardShell header"
  not "improve the OCMC UI."
- **Verbatim requirement:** PO's exact words. Populated. Not empty.
- **Description:** Enough context that the agent doesn't need to guess.
  References to design documents, codebase locations, related tasks.
- **Acceptance criteria:** Specific, checkable conditions. Not "it works"
  but "three Select dropdowns visible in header on all authenticated
  pages, reading/writing fleet_config via board PATCH API."
- **Task type:** Epic, story, task, subtask, bug, spike — correctly set.
- **Stage:** Appropriate to where the task is in its journey.
- **Readiness:** Reflects actual readiness, confirmed by PO.
- **Assignment:** Appropriate agent assigned based on role and capability.
- **Priority:** Set correctly.
- **Story points:** Estimated.
- **Project:** Set.
- **Dependencies:** If any, linked.

**Example of a full task:**
```
Title: Add task_readiness integer custom field to OCMC fleet board
Type: task
Priority: high
Story Points: 3
Assigned: devops-expert
Project: Fleet
Stage: work
Readiness: 99%

Verbatim Requirement:
"TASK READINESS = CUSTOM FIELD. (ON THE BOARD AND ON THE PROJECT
MANAGEMENT....)"
"the only moment when you can write work would be when the readiness
is at 99 or 100%."

Description:
Add an integer custom field (0-100) called task_readiness to the fleet
board. This is the first of three new custom fields for the methodology
system. The field tracks how ready a task is for work — agents cannot
enter work protocol until readiness is 99-100%.

Implementation: Add the field via configure-board.sh using the MC custom
fields API. Update mc_client.py to parse the field. Update models.py to
include it in TaskCustomFields. Update orchestrator.py to check readiness
before dispatch.

Files: scripts/configure-board.sh, fleet/infra/mc_client.py,
fleet/core/models.py, fleet/cli/orchestrator.py

Acceptance Criteria:
- [ ] Custom field exists on fleet board (verify via MC API)
- [ ] Field visible on task cards in OCMC UI
- [ ] mc_client parses task_readiness from custom field values
- [ ] TaskCustomFields model has task_readiness: int = 0
- [ ] Orchestrator skips tasks with readiness < 99
- [ ] Test: create task with readiness 0, confirm not dispatched
- [ ] Test: set readiness to 99, confirm dispatched
```

**Example of a BAD task (what the immune system would flag):**
```
Title: Fix the UI
Type: task
Priority: medium
Description: (empty)
Acceptance Criteria: (empty)
Readiness: 0%
```

This task has no verbatim requirement, no description, no acceptance
criteria, vague title. An agent dispatched on this WILL deviate because
there's nothing to anchor to. The methodology system should not allow
this task to reach work stage. Task readiness should stay at 0% until
the PO provides substance.

---

### A Full Bug Report

When an agent or the PO reports a bug, it must include:

- **Title:** Specific. What's broken, where. "Orchestrator crashes with
  NameError on DRIVER_AGENTS constant" not "orchestrator broken."
- **Steps to reproduce:** Concrete sequence that triggers the bug.
- **Expected behavior:** What should happen.
- **Actual behavior:** What actually happens. Include error messages,
  logs, stack traces.
- **Environment:** Which system, which version, what configuration.
- **Impact:** How severe. What's affected. Who's blocked.
- **Evidence:** Screenshots, log excerpts, error output.

**Example of a full bug report:**
```
Title: Orchestrator crashes with NameError: DRIVER_AGENTS not defined
Type: bug
Priority: urgent
Assigned: devops-expert

Steps to Reproduce:
1. Start fleet daemons with `fleet daemon all`
2. Wait for orchestrator cycle (30s)
3. Orchestrator crashes on dispatch step

Expected: Orchestrator completes cycle without error
Actual: NameError: name 'DRIVER_AGENTS' is not defined
  File: fleet/cli/orchestrator.py, line 142
  Traceback: (attached)

Environment: Fleet on WSL2, MC running, 10 agents online
Impact: Orchestrator down, no tasks dispatched, fleet idle

Root Cause (if known): DRIVER_AGENTS constant was referenced but
never defined. Previously was in a config file that got removed.

Fix: Inline the default list ['project-manager', 'fleet-ops']
```

---

### A Full Analysis Document

When an agent produces an analysis document (analysis protocol stage):

- **Title:** What was analyzed.
- **Scope:** What was examined, what was excluded.
- **Current state:** What exists today. Specific files, components,
  line numbers. Not vague descriptions.
- **Findings:** What was discovered. Concrete observations.
- **Implications:** What this means for the task.
- **Open questions:** What couldn't be determined from analysis alone.

**Example:** The gateway session API investigation from this session
is an analysis document. It examined specific files, documented specific
APIs (sessions.delete, sessions.compact, chat.send), identified what
each API does, and stated implications for the doctor's architecture.

---

### A Full Investigation Document

When an agent produces a research/investigation document:

- **Title:** What was investigated.
- **Scope:** What was researched, what sources were consulted.
- **Findings:** What was found, organized by topic. Sources cited.
- **Options:** If multiple approaches exist, each described with
  tradeoffs.
- **Recommendations:** What the investigation suggests (NOT decisions —
  reasoning protocol decides).
- **Open questions:** What the investigation couldn't answer.

**Example:** The immune system research findings document
(04-research-findings.md) is an investigation document. It covers
compounding errors, context degradation, review blindness, sycophancy,
and the devops-control-plane rules — with sources, findings, and
implications.

---

### A Full Plan (Reasoning Document)

When an agent produces a plan (reasoning protocol stage):

- **Title:** What's being planned.
- **Requirement:** Verbatim requirement quoted.
- **Approach:** What will be done. Specific files, components, changes.
- **Target files:** Exactly which files will be modified or created.
- **Steps:** Ordered implementation steps.
- **Dependencies:** What must exist before each step.
- **Acceptance criteria mapping:** How each criterion will be met.
- **Risks:** What could go wrong.

The plan must reference the verbatim requirement explicitly and show
how the approach addresses it.

---

### A Full PR

When an agent submits a pull request:

- **Title:** Short, specific. Conventional commit format.
- **Description:** What was done and why. References the task.
- **Changes:** What files were modified and why.
- **Testing:** What tests were run. Results.
- **Task reference:** Links to OCMC task and Plane issue.
- **Acceptance criteria:** Which criteria this PR addresses.
- **Commits:** Conventional commit format. One logical change per commit.

---

### A Full Completion Claim

When an agent calls fleet_task_complete:

- **PR URL:** Link to the pull request.
- **Summary:** What was done.
- **Acceptance criteria check:** Each criterion addressed with evidence.
- **Tests:** Test results or confirmation.
- **Files changed:** List of files modified.
- **Commits:** List of commits with conventional messages.

A completion claim that says "done" with no evidence is incomplete.
The methodology system should reject it. The immune system should
flag it as laziness.

---

## Standards for Protocols

Each methodology protocol also has output standards:

| Protocol | Expected Output | Standard |
|----------|----------------|----------|
| Conversation | Questions, proposals | Specific, grounded in the task, references PO's words |
| Analysis | Analysis document | Examines actual code, cites files/lines, not vague |
| Investigation | Research document | Multiple sources, options explored, findings cited |
| Reasoning | Plan document | Maps to verbatim requirement, specifies target files |
| Work | Code + PR | Conventional commits, tests, PR with description |

---

## How Standards Are Enforced

1. **Methodology checks:** Each stage has checks that verify the output
   meets the standard for that stage. Task can't advance if checks fail.
2. **Immune system:** Detects when output doesn't meet standards
   (laziness — partial output, deviation — wrong standard applied).
3. **Teaching system:** When an agent produces substandard work, the
   lesson includes the relevant standard and examples of what "done
   right" looks like. The agent practices producing standard-quality
   output.
4. **PO review:** PO can reject work that doesn't meet standards and
   decrease readiness.

---

## Evolution

New standards will be needed as:
- New artifact types are created (e.g., security audit reports,
  architecture decision records)
- Existing standards prove insufficient (e.g., PR descriptions need
  more detail)
- The PO identifies quality gaps
- New protocols are added
- The fleet matures and expectations rise

Standards are stored in a format that allows easy addition and
modification — not hardcoded into the system.

---

## Open Questions

- Where do standards live? Config files? Markdown in a standards
  directory? Database?
- How do agents access standards? Injected in heartbeat context?
  Available as reference? Loaded per-stage?
- How detailed should standards be? Too detailed → agents can't process
  them. Too brief → agents produce minimum quality.
- How do methodology checks verify standards compliance? Deterministic
  checks (field populated, criteria addressed) or semantic (quality
  of the content)?
- Who creates and maintains standards? PO? PM? fleet-ops?
- How do standards interact with the teaching system? When an agent
  fails a standard, the lesson should include the relevant standard
  and example. How is this connected?