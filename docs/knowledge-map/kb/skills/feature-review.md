# feature-review

**Type:** Skill (AICP Lifecycle)
**Location:** devops-expert-local-ai/.claude/skills/feature-review/
**Invocation:** /feature-review
**Effort:** medium
**Roles:** QA Engineer

## What It Does

Review a feature implementation against requirements. Reads the code changes, compares to the original plan and acceptance criteria, checks test coverage, identifies issues. Produces a structured review with pass/fail per criterion.

## Fleet Use Case

QA uses during REVIEW stage to validate the engineer's implementation against the predefined test criteria (TC-001, TC-002). The review checks: does the code match the plan? Do tests pass? Is coverage adequate? Any security concerns? The output feeds fleet-ops' 7-step review.

## Relationships

- USED BY: qa-engineer (REVIEW stage)
- CONNECTS TO: fleet-test skill (test execution + analysis)
- CONNECTS TO: fleet-ops review (QA review feeds fleet-ops Step 3)
- CONNECTS TO: /diff command (review code changes)
- CONNECTS TO: quality-coverage skill (coverage verification)
- CONNECTS TO: fleet_contribute tool (qa_test_definition — QA's predefined criteria)
