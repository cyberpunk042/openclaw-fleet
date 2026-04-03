# Verification (Before Completion)

**Type:** Skill (Superpowers Plugin)
**Source:** superpowers plugin (obra/superpowers, 132K stars)
**Invocation:** Invoked as part of superpowers workflow
**Roles:** Software Engineer

## What It Does

Systematic verification that changes actually work before marking a task complete. Runs through: does the fix address the original issue? Do all tests pass? Are there regression risks? Does the change match the plan? Is the scope correct (no unrequested changes)?

Prevents the "it compiles so it works" trap — forces explicit verification against acceptance criteria.

## Fleet Use Case

Engineer uses verification before fleet_task_complete. The methodology requires "stay within scope (verbatim + plan)" — verification checks this systematically. Fleet-ops review (Step 3: VERIFY ACCEPTANCE CRITERIA) expects the engineer already verified.

## Relationships

- PROVIDED BY: superpowers plugin (obra/superpowers)
- USED BY: software-engineer (WORK stage, before fleet_task_complete)
- CONNECTS TO: fleet_task_complete tool (verification BEFORE completion)
- CONNECTS TO: fleet-ops review (Step 3 — engineer pre-verified, fleet-ops re-verifies)
- CONNECTS TO: TDD skill (TDD provides tests, verification runs them)
- CONNECTS TO: quality-coverage skill (verification includes coverage check)
