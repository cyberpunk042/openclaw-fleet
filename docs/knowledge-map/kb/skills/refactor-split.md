# refactor-split

**Type:** Skill (AICP Lifecycle)
**Location:** devops-expert-local-ai/.claude/skills/refactor-split/
**Invocation:** /refactor-split
**Effort:** medium
**Roles:** Software Engineer

## What It Does

Split a large module into smaller, focused modules. Analyze the current module's responsibilities, identify natural boundaries, plan the split (which functions/classes go where, how imports change), execute the split, update all references, verify tests pass.

## Fleet Use Case

Engineer uses when a module exceeds manageable size or mixes responsibilities (SRP violations). The fleet codebase values "keep modules small and focused. One responsibility per file." refactor-split enforces this principle.

## Relationships

- USED BY: software-engineer (WORK stage)
- CONNECTS TO: refactor-extract skill (extract is single function/class, split is full module)
- CONNECTS TO: architecture-review skill (architect validates split boundaries)
- CONNECTS TO: fleet_commit tool (commit split as separate change)
