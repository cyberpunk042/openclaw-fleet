# Task: Architect producing design_input contribution

**Expected:** Architect examining codebase for design. Should show CONTRIBUTION TASK section with target task verbatim, fleet_contribute() reference.

## task-context.md

```
# MODE: task | injection: full | model: contribution | generated: 01:06:45
# Your task data is pre-embedded below. fleet_read_context() only if you need fresh data or a different task.

# YOU ARE: architect

# YOUR TASK: Contribute design_input for: fleet health dashboard
- ID: task-con
- Priority: medium
- Type: subtask

# YOUR STAGE: analysis

# READINESS: 50%

## VERBATIM REQUIREMENT
> Provide design_input: approach, target files, patterns for the fleet health dashboard

## CONTRIBUTION TASK
**Type:** design_input
**Target task:** task-a1b
**Title:** Add fleet health dashboard to MC frontend
**Verbatim:** Add a health dashboard showing: agent grid (online/idle/sleeping/offline), task pipeline (inbox/progress/review/done counts), storm indicator with severity color, budget gauge with percentage
**Delivery phase:** mvp
**Stage:** work

Call `fleet_contribute()` when your contribution is ready.

## Current Stage: ANALYSIS

You are in the analysis protocol. Examine what exists.

### What you MUST do:
- Examine the codebase with the TARGET TASK's requirements in mind. Your output feeds into another agent's work.
- Read and examine the codebase, existing implementation, architecture
- Produce an analysis document in wiki/domains/ (knowledge layer)
- Reference SPECIFIC files and line numbers — not vague descriptions
- Produce findings relevant to the TARGET TASK shown above
- Identify implications for the task

### What you MUST NOT do:
- Do NOT produce solutions (that's reasoning stage)
- Do NOT write implementation code
- Do NOT call fleet_task_complete

### What you CAN produce:
- Analysis documents with file references
- Current state assessments
- Gap analysis
- Dependency mapping
- Impact analysis
- Commits of analysis documents (fleet_commit allowed)

### How to advance:
- Analysis document exists and covers the relevant codebase areas
- Contribution is complete and ready to deliver
- Implications for the task are clear

Your job is to UNDERSTAND WHAT EXISTS, not to solve the problem.

## INPUTS FROM COLLEAGUES
*(No contributions required.)*

## WHAT TO DO NOW
Examine the codebase. Produce an analysis document in wiki/domains/ with file and line references. Do NOT produce solutions yet.

```
