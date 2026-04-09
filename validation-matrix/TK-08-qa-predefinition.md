# Task: QA predefining test criteria (TC-XXX)

**Expected:** QA producing TC-XXX criteria. Phase-appropriate (MVP = main flows + critical edges).

## task-context.md

```
# MODE: task | injection: full
# Your task data is pre-embedded below. fleet_read_context() only if you need fresh data or a different task.

# YOU ARE: qa-engineer

# YOUR TASK: Contribute qa_test_definition for: fleet health dashboard
- ID: task-qa-
- Priority: medium
- Type: subtask

# YOUR STAGE: reasoning

# READINESS: 80% (PO-set — gates dispatch)

## VERBATIM REQUIREMENT
> Define structured TC-XXX test criteria for the fleet health dashboard story

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
*(No contributions required.)*

## WHAT TO DO NOW
Produce a plan that REFERENCES the verbatim requirement above. Specify target files and acceptance criteria mapping.

## WHAT HAPPENS WHEN YOU ACT
- `fleet_artifact_create/update()` → Plane HTML + completeness check
- `fleet_chat()` → board memory + IRC + agent mentions
- Every tool call fires automatic chains — you don't update multiple places manually.

```
