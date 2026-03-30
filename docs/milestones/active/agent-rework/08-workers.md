# Worker Agents — Full Directive Design

**Date:** 2026-03-30
**Status:** Design — deep directive mapping
**Part of:** Agent Rework (document 8 of 13)

---

## Worker Agent Roles

- **software-engineer** — code implementation, features, bug fixes
- **devops-expert** — infrastructure, CI/CD, scripts, deployment
- **qa-engineer** — testing, quality verification, test plans
- **technical-writer** — documentation, guides, API docs
- **ux-designer** — UI/UX design, component design, wireframes
- **accountability-generator** — compliance, audit, governance reports

---

## Worker's World

Every worker sees (pre-embedded, FULL):
- Assigned tasks with ALL details — title, description, verbatim
  requirement, stage, readiness, story points, comments, artifact state
- In-progress task artifact (if exists) — the structured object showing
  what was done in previous cycles, what's missing, completeness
- Task comments from PM, other agents, PO — the progressive work trail
- Messages mentioning this agent
- Directives from PO
- Fleet state and events
- Standards for the artifact type they're working on

---

## Worker Heartbeat: The Full Directive

### Phase 1: Read Pre-Embedded Context

All data already there. Worker reads assigned tasks, artifact state,
messages, directives.

### Phase 2: Directives and Messages

PO directives first. Messages second.

### Phase 3: Work on Assigned Tasks

For EACH assigned task, the worker follows the methodology protocol
for the CURRENT STAGE. The stage determines what the worker does.

The data makes this natural — the pre-embed includes the stage and
the stage instructions. The worker reads them and follows them.

**Conversation stage — Understand:**
```
Pre-embedded: task with verbatim requirement (maybe incomplete)
Worker reads: "This task says to add fleet controls to the UI"
Worker thinks: "Where in the UI? The requirement doesn't specify."
Worker acts:
  - Post task comment: "The requirement says 'OCMC UI' but doesn't
    specify where. Should this be in the header? The sidebar? A new
    page? @project-manager can you clarify?"
  - Do NOT produce code or plans
  - Do NOT call fleet_commit
```
Chain: comment posted → PM sees on next heartbeat → Plane sync if linked

**Analysis stage — Examine:**
```
Pre-embedded: task with requirement + artifact state (maybe empty)
Worker reads: "I need to analyze the header structure"
Worker acts:
  - Read relevant code files
  - Build analysis artifact progressively:
    fleet_artifact_update("analysis_document", "scope", "DashboardShell.tsx header")
    fleet_artifact_update("analysis_document", "findings", append=True,
      value={"title": "...", "finding": "...", "files": [...]})
  - Each update: chain triggers Plane HTML + completeness check
  - Post comment summarizing findings
  - Do NOT produce solutions yet
```

**Investigation stage — Research:**
```
Pre-embedded: task + analysis findings
Worker reads: "Analysis found X. Now I need to research approaches."
Worker acts:
  - Research multiple options
  - Build investigation artifact with options + tradeoffs:
    fleet_artifact_update("investigation_document", "options", values=[...])
  - Post findings to PM or architect for input
  - Do NOT decide on approach yet
```

**Reasoning stage — Plan:**
```
Pre-embedded: task + analysis + investigation + verbatim requirement
Worker reads: "Requirements are clear, analysis and research done.
  I need to produce a plan."
Worker acts:
  - Create plan artifact referencing verbatim requirement:
    fleet_artifact_create("plan", "Implementation Plan")
    fleet_artifact_update("plan", "requirement_reference", task.verbatim)
    fleet_artifact_update("plan", "target_files", values=[...])
    fleet_artifact_update("plan", "steps", values=[...])
  - Each update: completeness increases → readiness suggestion increases
  - Post plan summary for PM/PO review
  - When PO confirms → readiness reaches 99
```

**Work stage — Execute (only when readiness >= 99):**
```
Pre-embedded: task + confirmed plan + full artifact
Worker reads: "Plan confirmed. Readiness 99%. Time to execute."
Worker acts:
  - Follow the plan steps
  - fleet_commit() for each logical change
    Chain: commit recorded → event emitted → progress tracked
  - fleet_task_complete(summary) when all steps done
    Chain: push branch → create PR → update task fields →
           post completion comment → notify IRC → move to review →
           create approval for fleet-ops
  - Do NOT deviate from plan
  - Do NOT add unrequested scope
```

### Phase 4: Progressive Work Across Cycles

If worker has an in-progress task from a previous cycle:

```
Pre-embedded: task + artifact with previous work
Worker reads: "Last cycle I added 3 findings. Missing: implications.
  Completeness: 60%. Suggested readiness: 50."
Worker acts:
  - Continue from where left off
  - fleet_artifact_update to add implications
  - Completeness now 100% → suggested readiness 90
  - Post comment: "Analysis complete. All findings documented."
```

The artifact state tells the worker EXACTLY where they left off and
what's still needed. No need to re-read the whole history.

### Phase 5: Communication

Workers communicate when needed:
- **Blocked:** post comment + fleet_chat PM: "@project-manager blocked on {task}: {reason}"
- **Question:** post task comment: "@project-manager I need clarity on {what}"
- **Progress:** post task comment: "Updated {artifact}. Completeness now {X}%."
- **Design input:** fleet_chat architect: "@architect need design guidance on {task}"
- **Done:** fleet_task_complete handles all notifications automatically

### Phase 6: Idle

If no tasks assigned and no messages:
- HEARTBEAT_OK
- Do NOT create unnecessary work
- Do NOT call tools for no reason

---

## Per-Role Specifics

### software-engineer
- Analysis: examines code, traces call sites, reads tests
- Investigation: researches patterns, libraries, approaches
- Work: writes code, writes tests, conventional commits, PR
- Artifacts: analysis_document → plan → pull_request → completion_claim

### devops-expert
- Analysis: examines infrastructure, scripts, configs, Docker
- Investigation: researches deployment patterns, IaC approaches
- Work: writes scripts, configs, Dockerfiles, setup automation
- Artifacts: analysis_document → plan → pull_request → completion_claim

### qa-engineer
- Analysis: examines test coverage, identifies gaps
- Investigation: researches test strategies, tools
- Work: writes test plans, test cases, test code, runs tests
- Artifacts: analysis_document → plan → completion_claim (test results)

### technical-writer
- Analysis: examines existing docs, identifies gaps
- Investigation: researches doc standards, audience needs
- Work: writes documentation, guides, API references
- Artifacts: analysis_document → plan → completion_claim

### ux-designer
- Analysis: examines existing UI, identifies UX issues
- Investigation: researches UI patterns, component libraries
- Work: produces design specs, wireframes, component designs
- Artifacts: analysis_document → investigation_document → plan

### accountability-generator
- Analysis: examines compliance state, governance gaps
- Investigation: researches requirements, standards
- Work: produces health reports, audit trails, compliance docs
- Artifacts: analysis_document → completion_claim

---

## Tool → Chain Map for Workers

| Action | Tool | Chain |
|--------|------|-------|
| Create artifact | `fleet_artifact_create(type, title)` | Object → Plane HTML → completeness |
| Update artifact | `fleet_artifact_update(type, field, value)` | Object → Plane HTML → completeness → readiness suggestion |
| Ask question | task comment | → PM sees → Plane sync |
| Report blocker | `fleet_chat("blocked: {why}", mention="project-manager")` | Board memory → PM heartbeat → IRC |
| Commit code | `fleet_commit(files, message)` | Git commit → event → progress tracked |
| Complete task | `fleet_task_complete(summary)` | Push → PR → task fields → comment → IRC → review → approval created |
| Request design | `fleet_chat("need design input", mention="architect")` | Board memory → architect heartbeat → IRC |

---

## Natural Autocomplete Pattern

Worker's pre-embed includes: task with requirement, current stage,
artifact with what's done and what's missing.

AI reads: "Task: Add readiness field. Stage: work. Readiness: 99%.
Plan says: 1) Add to configure-board.sh, 2) Add to models.py,
3) Add to mc_client.py. All steps from confirmed plan."

Natural continuation: implement step 1 → fleet_commit → implement
step 2 → fleet_commit → implement step 3 → fleet_commit →
fleet_task_complete.

The plan steps are the autocomplete chain. The AI follows them
sequentially. Each tool handles propagation.