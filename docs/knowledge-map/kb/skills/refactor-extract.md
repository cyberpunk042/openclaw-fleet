# refactor-extract

**Type:** Skill (AICP Lifecycle)
**Location:** devops-expert-local-ai/.claude/skills/refactor-extract/
**Invocation:** /refactor-extract
**Effort:** medium
**Roles:** Software Engineer

## What It Does

Extract refactoring: identify code that should be separated into its own module, class, or function. Read the codebase, identify extraction candidates (repeated patterns, oversized functions, mixed responsibilities), plan the extraction, execute it, verify tests still pass.

## Fleet Use Case

Engineer uses during WORK stage when a task involves improving code structure. The methodology says "stay within scope" — refactor-extract only extracts what's needed for the current task, not speculative cleanup. Architect may recommend extraction targets via design_input contribution.

## Relationships

- USED BY: software-engineer (WORK stage)
- CONNECTS TO: refactor-split skill (split is broader than extract)
- CONNECTS TO: refactor-architecture skill (architecture-level refactoring)
- CONNECTS TO: architecture-review skill (architect validates extraction)
- CONNECTS TO: fleet_commit tool (commit extraction as separate change)
