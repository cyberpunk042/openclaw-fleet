# quality-coverage

**Type:** Skill (AICP Lifecycle)
**Location:** devops-expert-local-ai/.claude/skills/quality-coverage/
**Invocation:** /quality-coverage
**Effort:** medium
**Roles:** QA Engineer, Accountability Generator

## What It Does

Verify test coverage: run coverage analysis, identify untested code paths, evaluate coverage against targets, produce a coverage report. Covers line coverage, branch coverage, and function coverage.

## Fleet Use Case

QA verifies coverage during REVIEW — are the engineer's changes adequately tested? Accountability generator includes coverage metrics in compliance reports. Fleet targets comprehensive testing — the fleet has 67+ test files in the AICP project and growing test suites in fleet.

## Relationships

- USED BY: qa-engineer (REVIEW), accountability-generator (ANALYSIS)
- CONNECTS TO: pytest-mcp (coverage reports, test analysis)
- CONNECTS TO: feature-test skill (tests produce coverage)
- CONNECTS TO: TDD skill (TDD naturally produces high coverage)
- CONNECTS TO: fleet-ops review (Step 4 — trail includes test results)
- CONNECTS TO: foundation-testing skill (testing infrastructure)
