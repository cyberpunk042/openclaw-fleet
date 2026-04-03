# Writing Plans

**Type:** Skill (Superpowers Plugin)
**Source:** superpowers plugin (obra/superpowers, 132K stars)
**Invocation:** /writing-plans or invoked as skill by superpowers
**Roles:** Architect, Project Manager

## What It Does

Structured plan writing methodology — breaks work into 2-5 minute tasks with exact file paths and verification steps. Each task specifies: what to change, which file, what the change looks like, how to verify it worked. Plans are executable — not vague direction.

The output is a list of concrete steps where each step is small enough to complete without losing context.

## Fleet Use Case

Architect writes implementation plans during REASONING stage that engineers execute during WORK stage. PM writes sprint plans that break epics into tasks. The methodology requires "plan referencing verbatim, specify target files, map criteria to steps" — writing-plans enforces this structure.

## Relationships

- PROVIDED BY: superpowers plugin (obra/superpowers)
- USED BY: architect (REASONING stage), project-manager (REASONING stage)
- CONNECTS TO: fleet_task_accept tool (plan submitted via task_accept)
- CONNECTS TO: /plan command (enter plan mode while writing plans)
- CONNECTS TO: fleet_artifact_create tool (plan as artifact)
- CONNECTS TO: architecture-propose skill (architecture decisions expressed as plans)
- CONNECTS TO: pm-plan skill (PM-level planning)
- CONNECTS TO: fleet-plan skill (sprint task decomposition)
