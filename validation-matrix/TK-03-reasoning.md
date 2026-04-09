# Task: Reasoning stage — produce plan, NOT implement

**Expected:** PLAN only. NO code. NO commits. Reference verbatim. fleet_commit should NOT appear in recommended actions.

## task-context.md

```
# MODE: task | injection: full
# Your task data is pre-embedded below. fleet_read_context() only if you need fresh data or a different task.

# YOU ARE: software-engineer

# YOUR TASK: Add fleet health dashboard
- ID: task-a1b
- Priority: high
- Type: story
- Description: Dashboard with agent grid, task pipeline, storm, budget

# YOUR STAGE: reasoning

# READINESS: 85% (PO-set — gates dispatch)

## VERBATIM REQUIREMENT
> Add health dashboard with agent grid, task pipeline, storm indicator, budget gauge

## Current Stage: REASONING

You are in the reasoning protocol. Plan your approach.

### What you MUST do:
- Decide on an approach based on requirements + analysis + investigation
- Produce an implementation plan
- The plan MUST reference the verbatim requirement explicitly
- Specify target files and components
- Map acceptance criteria to specific implementation steps
- Present the plan to the PO for confirmation

### What you MUST NOT do:
- Do NOT start implementing yet
- Do NOT call fleet_task_complete

### What you CAN produce:
- Implementation plans with specific file/component references
- Design decisions with justification
- Task breakdown (subtasks if needed via fleet_task_create)
- Acceptance criteria mapping
- Commits of planning documents (fleet_commit allowed)
- Plan submission (fleet_task_accept allowed)

### How to advance:
- Plan exists and references the verbatim requirement
- Plan specifies target files
- PO confirmed the plan
- Readiness reaches 99-100%

Your job is to PLAN, not to execute.

## INPUTS FROM COLLEAGUES
Required contributions (received content appears below if delivered):
- **design_input** from architect
- **qa_test_definition** from qa-engineer

If contributions are NOT shown below → `fleet_request_input()`. Do NOT proceed without required contributions in work stage.

## WHAT TO DO NOW
Produce a plan that REFERENCES the verbatim requirement above. Specify target files and acceptance criteria mapping.

## WHAT HAPPENS WHEN YOU ACT
- `fleet_artifact_create/update()` → Plane HTML + completeness check
- `fleet_chat()` → board memory + IRC + agent mentions
- Every tool call fires automatic chains — you don't update multiple places manually.

```

## knowledge-context.md

```
## Stage: REASONING — Resources Available

### Skills:
- /fleet-implementation-planning — map plan to files and changes
- /writing-plans (superpowers) — detailed implementation roadmap
- /brainstorming (superpowers) — explore approaches

### Sub-agents:
- **code-explorer** (sonnet) — understand codebase before planning

### MCP: fleet · filesystem · github · context7

```
