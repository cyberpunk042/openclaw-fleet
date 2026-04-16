# Task: Concern — investigation only, no implementation

**Expected:** Concern task. Research model. Analysis + investigation only. NO work stage, NO code output.

## task-context.md

```
# MODE: task | injection: full | model: research | generated: 20:24:15
# Your task data is pre-embedded below. fleet_read_context() only if you need fresh data or a different task.
# FLEET: full-autonomous | execution | claude

# YOU ARE: software-engineer

# YOUR TASK: Investigate orchestrator memory growth over 48h
- ID: task-con
- Priority: high
- Type: concern

# YOUR STAGE: analysis

# READINESS: 30%

## VERBATIM REQUIREMENT
> The orchestrator process grows from 200MB to 1.2GB over 48 hours. Find the root cause.

## Current Stage: ANALYSIS

You are in the analysis protocol. Examine what exists.

### What you MUST do:
- Read and examine the codebase, existing implementation, architecture
- Produce an analysis document in wiki/domains/ (knowledge layer)
- Reference SPECIFIC files and line numbers — not vague descriptions
- Present findings to the PO via task comments
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
- PO reviewed the findings
- Implications for the task are clear

Your job is to UNDERSTAND WHAT EXISTS, not to solve the problem.

## INPUTS FROM COLLEAGUES
*(No contributions required.)*

## WHAT TO DO NOW
Examine the codebase. Produce an analysis document in wiki/domains/ with file and line references. Do NOT produce solutions yet.

```
