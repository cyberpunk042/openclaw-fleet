# feature-test

**Type:** Skill (AICP Lifecycle)
**Location:** devops-expert-local-ai/.claude/skills/feature-test/
**Invocation:** /feature-test
**Effort:** medium
**Roles:** Software Engineer, QA Engineer

## What It Does

Write and run tests for a feature. Covers: reading feature requirements, identifying test scenarios (happy path, edge cases, error cases), writing tests, running the test suite, verifying coverage. Updates project state with test results.

## Fleet Use Case

Engineer writes tests during WORK stage as part of implementation. QA writes test definitions during CONTRIBUTION — structured criteria (TC-001, TC-002) that the engineer must satisfy. Both use feature-test but at different stages: QA defines, engineer implements.

## Relationships

- USED BY: software-engineer (WORK stage), qa-engineer (WORK + CONTRIBUTION)
- CONNECTS TO: TDD skill (test-first methodology)
- CONNECTS TO: foundation-testing skill (testing infrastructure)
- CONNECTS TO: fleet-test skill (fleet-specific test analysis)
- CONNECTS TO: pytest-mcp (test failure analysis, coverage)
- CONNECTS TO: quality-coverage skill (coverage verification)
