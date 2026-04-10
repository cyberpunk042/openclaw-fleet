# Task: Work stage, BLOCKED by dependency

**Expected:** Blocked task. Should show BLOCKED in task detail and action directive should tell agent to report via fleet_pause().

## task-context.md

```
# MODE: task | injection: full | model: feature-development | generated: 01:06:45
# Your task data is pre-embedded below. fleet_read_context() only if you need fresh data or a different task.

# YOU ARE: software-engineer

# YOUR TASK: Add fleet health dashboard
- ID: task-a1b
- Priority: high
- Type: story
- Story Points: 5
- Description: Dashboard with agent grid, task pipeline, storm, budget
- BLOCKED by: task-blo

# YOUR STAGE: work

# READINESS: 99%

## VERBATIM REQUIREMENT
> Add health dashboard with agent grid

## Current Stage: WORK

Execute the confirmed plan. Stay in scope.

### MUST:
- Execute the plan confirmed in reasoning stage
- Stay within scope — verbatim requirement and confirmed plan only
- Consume all contributions before implementing
- Commit each logical change via fleet_commit
- Complete via fleet_task_complete when done

### MUST NOT:
- Do NOT deviate from the confirmed plan
- Do NOT add unrequested scope
- Do NOT modify files outside the plan's target
- Do NOT skip tests

## INPUTS FROM COLLEAGUES
### Required Contributions
- **design_input** from architect — *awaiting delivery*
- **qa_test_definition** from qa-engineer — *awaiting delivery*

If any contribution above shows *awaiting delivery* → `fleet_request_input()`. Do NOT proceed without required contributions in work stage.

## WHAT TO DO NOW
BLOCKED — required contributions missing: design_input, qa_test_definition. Call `fleet_request_input()` for each missing contribution. Do NOT start implementation without required inputs.

```
