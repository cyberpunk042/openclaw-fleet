# pr-review-toolkit

**Type:** Claude Code Plugin (Official Anthropic)
**Source:** Anthropic marketplace
**Installed for:** Fleet-Ops

## What It Does

Launches 5 parallel Sonnet agents to review a pull request simultaneously. Each agent examines different aspects — code quality, test coverage, security patterns, architecture alignment, style consistency. Results are aggregated into a comprehensive review report.

## Fleet Use Case

Fleet-ops is the final review authority. When fleet_approve processes a task, pr-review-toolkit provides 5 independent perspectives on the PR. This massively enhances review depth — fleet-ops gets 5× the analysis without 5× the time.

Aligns with the 7-step review protocol:
- Step 2 (READ THE DIFF) → 5 agents read the diff in parallel
- Step 6 (QUALITY CHECK) → each agent checks a different quality dimension

## Relationships

- INSTALLED FOR: fleet-ops
- USED IN: review (7-step review protocol)
- CONNECTS TO: fleet_approve tool (review results inform approval decision)
- CONNECTS TO: /diff command (PR diff is input to review)
- CONNECTS TO: /pr-comments command (review generates comments)
- CONNECTS TO: fleet-review skill (skill invokes the review workflow)
- CONNECTS TO: doctor laziness detection (5-agent review cannot be done in <30s)
