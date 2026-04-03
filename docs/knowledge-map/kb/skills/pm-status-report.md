# pm-status-report

**Type:** Skill (AICP)
**Location:** devops-expert-local-ai/.claude/skills/pm-status-report/SKILL.md
**Invocation:** /pm-status-report
**Effort:** medium
**Allowed tools:** Read, Write, Edit, Bash, Glob, Grep

## Purpose

Generate a stakeholder status report: progress since last report, upcoming work, blockers, metrics (tests, coverage, cost, tokens), and decisions needed from PO. Writes to `docs/status/` with date-stamped filename.

## Process

1. Read project state, recent git history, task history, metrics
2. Generate report with 5 sections:
   - **Progress** — what was completed since last report
   - **Upcoming** — what's planned next
   - **Blockers** — what's stuck
   - **Metrics** — tests passing, coverage, cost, token usage
   - **Decisions needed** — what needs PO input
3. Write to `docs/status/` with date-stamped filename

## Assigned Roles

| Role | Priority | Why |
|------|----------|-----|
| PM | ESSENTIAL | PM generates stakeholder reports |
| Fleet-ops | RECOMMENDED | Fleet health reporting |
| Accountability | RECOMMENDED | Compliance status reporting |

## Methodology Stages

| Stage | Usage |
|-------|-------|
| work | Generate the report |
| any | Can be triggered at sprint boundaries |

## Relationships

- DEPENDS ON: pm-assess (assessment feeds the report — assess THEN report)
- READS: project state, git log, task history, metrics
- PRODUCES: date-stamped status report in docs/status/
- CONNECTS TO: fleet_plane_comment (post report summary on Plane)
- CONNECTS TO: fleet_notify_human (notify PO report is ready)
- CONNECTS TO: fleet-sprint skill (sprint boundary triggers report)
- CONNECTS TO: /cost command (token usage for metrics section)
- CONNECTS TO: LaborStamp analytics (cost per agent/model for metrics)
- CONNECTS TO: velocity.py (sprint velocity for metrics)
- CONNECTS TO: release-cycle composite (status report is step 6 of 6)
