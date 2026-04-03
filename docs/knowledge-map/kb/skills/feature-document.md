# feature-document

**Type:** Skill (AICP Lifecycle)
**Location:** devops-expert-local-ai/.claude/skills/feature-document/
**Invocation:** /feature-document
**Effort:** medium
**Roles:** Technical Writer

## What It Does

Document a feature: read the implementation, extract the user-facing behavior, write documentation covering usage, configuration, API reference, and examples. Updates existing docs or creates new ones. Documentation is a living system — update or delete, never leave stale.

## Fleet Use Case

Writer uses during WORK stage and autonomously during heartbeats (writer-heartbeat-autonomous intent). Scans for completed tasks without documentation, stale Plane pages, outdated READMEs. The methodology note says "documentation is a LIVING SYSTEM" — feature-document enforces this.

## Relationships

- USED BY: technical-writer (WORK stage, heartbeat-autonomous)
- CONNECTS TO: fleet_artifact_create tool (documentation artifacts)
- CONNECTS TO: fleet_commit tool (commit doc changes)
- CONNECTS TO: pm-changelog skill (changelog from feature changes)
- CONNECTS TO: ars-contexta plugin (extract knowledge from conversation)
- CONNECTS TO: fleet-plane skill (update Plane pages)
