# feature-plan

**Type:** Skill (AICP Lifecycle)
**Location:** devops-expert-local-ai/.claude/skills/feature-plan/
**Invocation:** /feature-plan
**Effort:** medium
**Roles:** Architect, Software Engineer, Project Manager

## What It Does

Plan changes for a feature. Reads project context and requirements, analyzes the codebase impact, produces a structured plan with target files, expected changes, and verification steps. The plan becomes the contract for implementation.

## Fleet Use Case

Architect uses during REASONING to produce the implementation blueprint. Engineer uses to plan before implementing. PM uses to estimate effort and break into subtasks. The methodology requires "plan referencing verbatim, specify target files" — feature-plan enforces this structure.

## Relationships

- USED BY: architect (REASONING), software-engineer (REASONING), project-manager (REASONING)
- CONNECTS TO: writing-plans skill (superpowers — detailed task breakdown)
- CONNECTS TO: fleet_task_accept tool (plan submitted as acceptance)
- CONNECTS TO: fleet_artifact_create tool (plan as artifact)
- CONNECTS TO: architecture-propose skill (architecture feeds plan)
- CONNECTS TO: /plan command (enter plan mode during planning)
