# Task: QA predefining test criteria (TC-XXX)

**Expected:** QA producing TC-XXX criteria. Phase-appropriate (MVP = main flows + critical edges).

## task-context.md

```
# MODE: task | injection: full | model: contribution | generated: 01:06:45
# Your task data is pre-embedded below. fleet_read_context() only if you need fresh data or a different task.

# YOU ARE: qa-engineer

# YOUR TASK: Contribute qa_test_definition for: fleet health dashboard
- ID: task-qa-
- Priority: medium
- Type: subtask

# YOUR STAGE: reasoning

# READINESS: 80%

## VERBATIM REQUIREMENT
> Define structured TC-XXX test criteria for the fleet health dashboard story

## CONTRIBUTION TASK
**Type:** qa_test_definition
**Target task:** task-a1b

Call `fleet_contribute()` when your contribution is ready.

## Current Stage: REASONING

You are in the reasoning protocol. Plan your approach.

### What you MUST do:
- Produce your contribution artifact. Call fleet_contribute() when ready.
- Decide on an approach based on requirements + analysis + investigation
- Produce a qa_test_definition: TC-XXX structured test criteria with priority and type
- The plan MUST reference the verbatim requirement explicitly
- Specify target files and components
- Map acceptance criteria to specific implementation steps
- Produce your contribution. Call `fleet_contribute()` when ready

### What you MUST NOT do:
- Do NOT start implementing yet
- Do NOT call fleet_task_complete

### What you CAN produce:
- QA test definitions structured as TC-XXX with priority and type
- Design decisions with justification
- Task breakdown (subtasks if needed via fleet_task_create)
- Acceptance criteria mapping
- Commits of planning documents (fleet_commit allowed)
- Plan submission (fleet_task_accept allowed)

### How to advance:
- Plan exists and references the verbatim requirement
- Plan specifies target files
- Contribution is ready to deliver via fleet_contribute()
- Readiness reaches 99-100%

Your job is to PLAN, not to execute.

## INPUTS FROM COLLEAGUES
*(No contributions required.)*

## WHAT TO DO NOW
Produce a plan in docs/superpowers/plans/ or as a task comment. Reference the verbatim requirement explicitly. Use `fleet_task_accept()` to submit for PO confirmation.

```
