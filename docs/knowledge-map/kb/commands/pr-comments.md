# /pr-comments

**Type:** Claude Code Built-In Command
**Category:** Git & Code
**Available to:** Fleet-ops (primary), Engineer (feedback processing)

## What It Actually Does

Fetches GitHub PR review comments for the current branch or a specified PR number. Shows inline code comments, review decisions, and conversation threads from the PR on GitHub. This brings external review feedback INTO the Claude Code session.

## When Fleet Agents Should Use It

**Fleet-ops during 7-step review:** After reading the diff (/diff), fleet-ops checks /pr-comments to see if there are existing review comments from other reviewers (architect, QA, devsecops) or from previous review rounds.

**Engineer after rejection:** Task was rejected by fleet-ops. Engineer runs /pr-comments to read the rejection feedback — what needs to change, which criteria weren't met, what fleet-ops specifically flagged.

**After codex adversarial review:** If codex-plugin-cc ran a review, the results are posted as PR comments. /pr-comments retrieves them for the agent to process.

## Relationships

- USED IN: fleet-ops review Step 2 (read PR feedback from other reviewers)
- USED IN: engineer rework (read rejection feedback)
- CONNECTS TO: fleet_approve (rejection feedback posted as PR comments)
- CONNECTS TO: codex-plugin-cc (adversarial review results as PR comments)
- CONNECTS TO: /diff command (diff shows changes, pr-comments shows feedback ON changes)
- CONNECTS TO: receiving-code-review skill (Superpowers — structured feedback processing)
- CONNECTS TO: readiness regression (rejection → readiness drops → engineer reads feedback → reworks)
- CONNECTS TO: gh_client.py (fetches from GitHub API)
