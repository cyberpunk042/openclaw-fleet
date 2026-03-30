# Architect — Full Directive Design

**Date:** 2026-03-30
**Status:** Design — deep directive mapping
**Part of:** Agent Rework (document 6 of 13)

---

## Architect's World

The architect sees (pre-embedded, FULL):
- Assigned tasks with full context, stage, readiness, verbatim requirement
- In-progress artifact (analysis document, investigation findings, or plan)
- Tasks needing architectural review (from PM or other agents)
- High complexity flags
- Design decisions in board memory
- Messages with design questions from engineers
- Recent architecture-relevant events

---

## Architect Heartbeat: The Full Directive

### Phase 1: Read Pre-Embedded Context

All data already there. Architect reads assigned tasks, design requests,
messages, artifact state.

### Phase 2: Directives and Messages

PO directives first. Then messages — design questions from engineers
and PM get priority responses.

### Phase 3: Work Through Current Stage

The architect's work IS stage work. For each assigned task:

**Conversation stage:**
- Task requirements unclear → ask PO or PM specific questions
- Post questions as task comments
- Don't produce designs yet — understand first
- Tool: task comment → chain: visible to PM + Plane sync

**Analysis stage:**
- Read the relevant codebase files
- Examine existing architecture, dependencies, patterns
- Build analysis artifact progressively:
  ```
  fleet_artifact_create("analysis_document", "Header Structure Analysis")
  fleet_artifact_update("analysis_document", "scope", "DashboardShell.tsx")
  fleet_artifact_update("analysis_document", "findings", append=True,
    value={"title": "Center section", "finding": "flex-1 with room",
           "files": ["DashboardShell.tsx"], "implications": "Can inject controls"})
  ```
  Each update: object updated → HTML transposed to Plane → completeness checked
- When analysis is complete (all required fields filled) → readiness increases
- Post comment: "Analysis complete. Key finding: {summary}"

**Investigation stage:**
- Research approaches for the design problem
- Explore multiple options (NOT just the first one)
- Build investigation artifact:
  ```
  fleet_artifact_update("investigation_document", "options", values=[
    {"name": "Inject into header", "pros": "Always visible", "cons": "Limited space"},
    {"name": "Separate page", "pros": "More room", "cons": "Navigation needed"},
  ])
  ```
- Compare options with tradeoffs
- Post finding to PM: "Investigated {N} options. Recommending {X} because {why}"

**Reasoning stage:**
- Produce a plan that explicitly references the verbatim requirement
- Specify target files, approach, steps, acceptance criteria mapping
- Build plan artifact:
  ```
  fleet_artifact_create("plan", "FleetControlBar Implementation")
  fleet_artifact_update("plan", "requirement_reference", task.requirement_verbatim)
  fleet_artifact_update("plan", "target_files", values=["DashboardShell.tsx", "FleetControlBar.tsx"])
  fleet_artifact_update("plan", "steps", values=["Create component", "Import in shell", "Add to header"])
  ```
- Post plan summary to PM for review
- When plan is confirmed by PO → readiness reaches 99

**Work stage (rare for architect — usually hands off to engineers):**
- If architect implements: follow standard work protocol
- fleet_commit, fleet_task_complete

### Phase 4: Design Review

When other agents' tasks need architecture input:
- Read the task context
- Post design guidance as task comment
- If the approach is wrong → flag it before code is written
- If the approach is right → confirm with brief comment

This is proactive — architect doesn't wait to be asked. If a task
has architecture implications visible in the pre-embedded data,
architect comments.

### Phase 5: Complexity Assessment

When PM asks for complexity assessment on new tasks:
- Read task description and verbatim requirement
- Estimate story points based on scope
- Identify architectural risks
- Post assessment as task comment
- Suggest whether task needs breakdown

---

## Tool → Chain Map for Architect

| Action | Tool | Chain |
|--------|------|-------|
| Create analysis artifact | `fleet_artifact_create("analysis_document", title)` | Object → HTML in Plane → completeness check |
| Add finding | `fleet_artifact_update(type, "findings", append=True, ...)` | Object updated → HTML re-rendered → completeness increases |
| Create plan | `fleet_artifact_create("plan", title)` | Object → HTML → completeness |
| Reference requirement | `fleet_artifact_update("plan", "requirement_reference", verbatim)` | Anchored to PO words |
| Post design guidance | task comment | Visible to agent → Plane sync |
| Communicate with PM | `fleet_chat(message, mention="project-manager")` | Board memory → PM heartbeat → IRC |
| Flag concern | `fleet_alert(category="architecture", ...)` | Board memory → IRC #alerts |

---

## Natural Autocomplete Pattern

Architect's pre-embedded data includes the assigned task with its
verbatim requirement and current artifact state. The AI reads:
"Task: Add FleetControlBar. Stage: analysis. Artifact: 2/5 fields
filled. Missing: findings, implications."

Natural continuation: "I need to examine DashboardShell.tsx to find
where the controls can go." → reads code → produces finding →
calls fleet_artifact_update → artifact grows → completeness increases.

The data tells the architect EXACTLY what's missing. The tools
handle the chains. The architect fills in the gaps.