# refactor-architecture

**Type:** Skill (AICP Lifecycle)
**Location:** devops-expert-local-ai/.claude/skills/refactor-architecture/
**Invocation:** /refactor-architecture
**Effort:** high
**Roles:** Architect

## What It Does

Restructure project architecture: move code between layers, restructure directories, realign module boundaries with architectural patterns (DDD, Onion, Clean Architecture). Higher-impact than extract or split — changes the overall structure.

## Fleet Use Case

Architect uses when the codebase has drifted from its intended architecture. Requires investigation (current vs intended structure), reasoning (proposed new structure), then work (execute restructuring). The methodology says "without architecture steps before executing, engineers make too many mistakes" — this skill IS those architecture steps.

## Relationships

- USED BY: architect (WORK stage — rare, usually transfers to engineers)
- CONNECTS TO: architecture-propose skill (propose the new architecture)
- CONNECTS TO: architecture-review skill (review the restructured result)
- CONNECTS TO: /batch command (parallel changes across multiple files)
- CONNECTS TO: fleet_contribute tool (design_input for engineers doing the work)
