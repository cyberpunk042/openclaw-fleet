# ops-rollback

**Type:** Skill (AICP)
**Location:** devops-expert-local-ai/.claude/skills/ops-rollback/SKILL.md
**Invocation:** /ops-rollback
**Effort:** high
**Allowed tools:** Read, Write, Edit, Bash, Glob, Grep

## Purpose

Rollback deployment to last known good state. Identifies the good target, executes rollback (revert deploy, restore database if needed), verifies with smoke tests, generates post-mortem template, and updates deployment log. Preserves failed deployment logs for analysis.

## Process

1. Identify current broken state and last good deployment
2. Execute rollback (revert deploy, restore database if needed)
3. Verify rollback succeeded (smoke tests against rolled-back version)
4. Generate post-mortem template (for ops-incident to fill)
5. Update deployment log

## Rules

- Verify rollback target is ACTUALLY GOOD before rolling back (don't roll back to another broken state)
- PRESERVE logs and state from the failed deployment for post-mortem
- Notify stakeholders of the rollback

## Assigned Roles

| Role | Priority | Why |
|------|----------|-----|
| DevOps | ESSENTIAL | Rollback is DevOps emergency procedure |
| Engineer | RECOMMENDED | May need to rollback their deployment |

## Methodology Stages

| Stage | Usage |
|-------|-------|
| work | Execute rollback (immediate, during incident) |

## Relationships

- PAIRED WITH: ops-deploy (deploy creates the state that rollback may revert)
- TRIGGERS: ops-incident (rollback happens DURING incident response)
- FOLLOWED BY: pm-retrospective (post-mortem after rollback stabilizes)
- PRODUCES: deployment log update, post-mortem template
- CONNECTS TO: fleet_alert (notify stakeholders of rollback)
- CONNECTS TO: incident-cycle composite (rollback is step in incident response chain)
- CONNECTS TO: storm system (rollback may be needed during STORM/CRITICAL)
- CONNECTS TO: §50 crisis response playbook (rollback is documented procedure)
