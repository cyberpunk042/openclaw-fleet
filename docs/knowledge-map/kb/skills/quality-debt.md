# quality-debt

**Type:** Skill (AICP Lifecycle)
**Location:** devops-expert-local-ai/.claude/skills/quality-debt/
**Invocation:** /quality-debt
**Effort:** medium
**Roles:** QA Engineer, Technical Writer, Accountability Generator

## What It Does

Identify technical debt: code smells, missing tests, outdated patterns, documentation gaps, dependency staleness. Produces a prioritized debt inventory with estimated effort and risk per item.

## Fleet Use Case

QA identifies code-level debt during ANALYSIS. Writer identifies documentation gaps. Accountability generator includes debt metrics in compliance reports. Fleet values "keep modules small and focused" — debt identification catches SRP violations and module bloat.

## Relationships

- USED BY: qa-engineer, technical-writer, accountability-generator
- CONNECTS TO: quality-audit skill (broader audit includes debt)
- CONNECTS TO: quality-coverage skill (missing tests = debt)
- CONNECTS TO: refactor-extract/split skills (debt remediation)
