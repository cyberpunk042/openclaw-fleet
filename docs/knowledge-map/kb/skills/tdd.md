# TDD (Test-Driven Development)

**Type:** Skill (Superpowers Plugin)
**Source:** superpowers plugin (obra/superpowers, 132K stars)
**Invocation:** /tdd or invoked as skill by superpowers
**Roles:** Software Engineer, QA Engineer

## What It Does

TRUE Test-Driven Development workflow: write test FIRST, watch it fail (red), write minimum code to pass (green), refactor (clean). Not "write code then add tests" — the test comes FIRST and drives the implementation.

The superpowers plugin enforces the discipline: it prompts for the test before any implementation, verifies the test fails, then guides implementation until the test passes.

## Fleet Use Case

Engineer and QA use TDD during WORK stage. The methodology says "follow conventions (conventional commits, testing), stay within scope." TDD ensures tests exist BEFORE code — fleet-ops can verify during review that tests were written first (trail timestamps).

## Relationships

- PROVIDED BY: superpowers plugin (obra/superpowers)
- USED BY: software-engineer (WORK stage), qa-engineer (WORK stage)
- CONNECTS TO: feature-test skill (complementary — TDD is the methodology, feature-test is the execution)
- CONNECTS TO: foundation-testing skill (testing infrastructure that TDD runs on)
- CONNECTS TO: fleet-test skill (QA validates test results from TDD)
- CONNECTS TO: pytest-mcp (test failure analysis, coverage, debug traces)
- CONNECTS TO: verification skill (verify changes after TDD cycle)
