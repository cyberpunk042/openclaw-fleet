# foundation-ci

**Type:** Skill (AICP)
**Location:** devops-expert-local-ai/.claude/skills/foundation-ci/SKILL.md
**Invocation:** /foundation-ci
**Effort:** medium
**Allowed tools:** Read, Write, Edit, Bash, Glob, Grep

## Purpose

Generate a CI/CD pipeline appropriate for the project's tech stack. Auto-detects stack from manifests, creates GitHub Actions workflow with lint→test→build steps, adds README status badge, and creates Makefile targets that mirror CI steps so developers can run locally what CI runs.

## Process

1. Detect project tech stack from manifests and source
2. Generate `.github/workflows/ci.yml`:
   - Trigger on push and PR to main
   - Matrix testing if multiple versions needed
   - Lint step (ruff/eslint/clippy — fail fast before tests)
   - Test step with coverage
   - Build step
   - Optional deploy step (commented out, ready to enable)
3. Add status badge to README
4. Create `Makefile` targets mirroring CI steps (run locally what CI runs remotely)

## Rules

- CI must PASS on current codebase before committing the workflow
- Keep pipeline FAST — lint fails before tests run (fail fast)
- Cache dependencies for speed
- Use SPECIFIC action versions, not @latest (security + reproducibility)

## Assigned Roles

| Role | Priority | Why |
|------|----------|-----|
| DevOps | ESSENTIAL | CI/CD is core DevOps responsibility |
| Engineer | RECOMMENDED | Engineers need to understand and run CI locally |

## Methodology Stages

| Stage | Usage |
|-------|-------|
| work | Set up CI pipeline for new or existing project |

## Relationships

- FOLLOWS: foundation-deps (dependencies must be defined for CI to install them)
- FOLLOWS: foundation-testing (tests must exist for CI to run them)
- CONNECTS TO: foundation-docker (CI can build Docker images)
- CONNECTS TO: ops-deploy (CI can trigger deployment — deploy step)
- CONNECTS TO: GitHub Actions MCP server (manage workflows programmatically)
- CONNECTS TO: fleet_task_complete (fleet completion triggers tests → CI validates)
- CONNECTS TO: release-cycle composite (CI is part of quality gate chain)
- CONNECTS TO: fleet-ops review Step 4 (verify CI passes in trail check)
- CONNECTS TO: pr_hygiene.py (PR must pass CI before merge)
- KEY PRINCIPLE: Makefile mirrors CI — `make test` runs same as CI test step. Developer never wonders "will CI pass?" because they run the same commands locally.
- OUR FLEET: uses `python -m pytest fleet/tests/` with 1732+ tests, ruff for linting
