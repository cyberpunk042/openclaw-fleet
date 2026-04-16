# Task: Work stage, full injection, contributions MISSING

**Expected:** Contributions required but NOT received. Should see 'fleet_request_input()' directive. Should NOT proceed.

## task-context.md

```
# MODE: task | injection: full | model: feature-development | generated: 20:24:15
# Your task data is pre-embedded below. fleet_read_context() only if you need fresh data or a different task.
# FLEET: full-autonomous | execution | claude

# YOU ARE: software-engineer

# YOUR TASK: Add fleet health dashboard
- ID: task-a1b
- Priority: high
- Type: story
- Story Points: 5
- Description: Dashboard with agent grid, task pipeline, storm, budget

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

## DELIVERY PHASE: mvp
- **tests:** main flows and critical edges
- **docs:** setup, usage, API for public
- **security:** auth, validation, dep audit

## WHAT TO DO NOW
BLOCKED — required contributions missing: design_input, qa_test_definition. Call `fleet_request_input()` for each missing contribution. Do NOT start implementation without required inputs.

```

## knowledge-context.md

```
## Stage: WORK — Resources Available

### Skills:
- /fleet-engineer-workflow — contribution consumption, TDD, conventional commits
- /fleet-completion-checklist — 8-point pre-completion check
- /test-driven-development (superpowers) — RED-GREEN-REFACTOR cycle
- /verification-before-completion (superpowers) — run tests before claiming done

### Sub-agents:
- **test-runner** (sonnet) — run pytest in isolated context
- **code-explorer** (sonnet) — trace execution paths

### MCP: fleet · filesystem · github · playwright
### Plugins: claude-mem · safety-net · context7 · superpowers · pyright-lsp

```
