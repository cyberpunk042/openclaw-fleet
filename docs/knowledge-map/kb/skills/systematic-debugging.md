# Systematic Debugging

**Type:** Skill (Superpowers Plugin)
**Source:** superpowers plugin (obra/superpowers, 132K stars)
**Invocation:** Used with /debug command
**Roles:** Software Engineer, QA Engineer, DevOps

## What It Does

4-phase structured debugging methodology: (1) Reproduce — confirm the issue exists and define expected vs actual behavior. (2) Isolate — narrow down the cause through bisection, logging, or elimination. (3) Fix — apply the minimum change that resolves the root cause. (4) Verify — confirm the fix works and no regressions.

Replaces guessing-and-hoping with systematic investigation. Each phase must complete before advancing.

## Fleet Use Case

Engineer uses during WORK and INVESTIGATION stages when encountering bugs. QA uses during test failure analysis. DevOps uses for infrastructure issues. The /debug command activates systematic debugging — it's not just a log level toggle.

## Relationships

- PROVIDED BY: superpowers plugin (obra/superpowers)
- USED BY: software-engineer, qa-engineer, devops (WORK and INVESTIGATION stages)
- CONNECTS TO: /debug command (activates the systematic debugging workflow)
- CONNECTS TO: pytest-mcp (test failure analysis feeds debugging phase 2)
- CONNECTS TO: ops-incident skill (incident response uses systematic debugging)
- CONNECTS TO: fleet_alert tool (if debugging reveals a systemic issue)
