# feature-implement

**Type:** Skill (AICP Lifecycle)
**Location:** devops-expert-local-ai/.claude/skills/feature-implement/
**Invocation:** /feature-implement
**Effort:** medium
**Roles:** Software Engineer

## What It Does

Execute the implementation operation for a feature. Standardized 6-step lifecycle: read project context, analyze needs, plan changes, execute modifications, verify with tests, update project state. Maintains state in .aicp/state.yaml for continuity across sessions.

## Fleet Use Case

Engineer's primary skill during WORK stage. After reading architect's design input and QA's test definitions, feature-implement drives the actual coding. The lifecycle steps map to fleet methodology: context (fleet_read_context) → plan (fleet_task_accept) → execute (code) → verify (tests) → complete (fleet_task_complete).

## Relationships

- USED BY: software-engineer (WORK stage)
- CONNECTS TO: fleet_task_accept tool (plan step → accept with plan)
- CONNECTS TO: fleet_commit tool (execute step → commit per change)
- CONNECTS TO: fleet_task_complete tool (verify step → complete task)
- CONNECTS TO: feature-test skill (verify step runs tests)
- CONNECTS TO: TDD skill (test-first within implementation)
- CONNECTS TO: feature-plan skill (plan step of the lifecycle)
