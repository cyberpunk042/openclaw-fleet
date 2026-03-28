# Fleet Standards

Read this document at session start. These standards apply to ALL fleet agents.

## Git

- **Conventional commits**: `type(scope): description [task:XXXXXXXX]`
- **Frequent commits**: one logical change per commit, never batch
- **Branch naming**: `fleet/<agent>/<task-short>` (auto-created by dispatch)
- **No force-push**, no rebase of shared branches
- See MC_WORKFLOW.md for full commit format reference

## Python

- **Type hints** on all public functions
- **Docstrings** on public classes and non-obvious functions
- **Formatting**: ruff (line-length 100, target py311)
- **Imports**: stdlib → third-party → local, sorted
- **No hardcoded paths** — use environment variables or config
- **No secrets in code** — use env vars or `.env` (gitignored)

## Bash

- **Shebang**: `#!/usr/bin/env bash`
- **Strict mode**: `set -euo pipefail`
- **Portable**: no bashisms that break on other systems, no hardcoded user paths
- **Quote variables**: `"$VAR"` not `$VAR`
- **Functions** for reusable logic, main flow at bottom

## Testing

- Every feature needs tests
- Tests go alongside source (or in `tests/` mirroring source structure)
- Run existing tests before committing: `pytest` or equivalent
- Don't break existing tests

## Security

- No secrets in commits (tokens, keys, passwords)
- No hardcoded machine-specific paths (use `$HOME`, `$FLEET_DIR`, config)
- Validate inputs at boundaries
- Workspace dirs with credentials are gitignored

## Task Workflow

- Read TOOLS.md for credentials at session start
- Update task status via MC API (in_progress → review/done)
- Post progress comments for visibility
- Include structured references in completion comments (branch, commits, files)
- If blocked, post a comment explaining what you need — don't silently fail

## Communication Decision Matrix

Three surfaces, three purposes. Use the RIGHT one every time.

### Task Comments (fleet-comment skill)

**For: information about THIS SPECIFIC TASK.**

| Situation | Action |
|-----------|--------|
| Starting work | Post acceptance with plan |
| Made progress | Post progress update |
| Blocked | Post blocker with reason + needed action |
| Completed | Post completion with PR, branch, files, commits — ALL as URLs |

Use templates from `agents/_template/markdown/comment-*.md`.

### Board Memory (fleet-memory skill)

**For: information that spans tasks — the fleet's knowledge base.**

| Situation | Template | Required Tags |
|-----------|----------|---------------|
| Security/quality/architecture concern | memory-alert.md | alert, {severity}, project:{name} |
| Decision made | memory-decision.md | decision, project:{name} |
| Improvement idea | memory-suggestion.md | suggestion, {area} |
| PR ready for review | inline | pr, review, project:{name} |
| Knowledge for other agents | inline | knowledge, project:{name} |

**Tags are MANDATORY. Untagged entries are useless.**

### IRC (fleet-irc skill)

**For: real-time alerts the human sees immediately.**

| Situation | Channel | Format |
|-----------|---------|--------|
| Task accepted | #fleet | `[agent] ▶️ STARTED: title — task_url` |
| Task blocked | #fleet | `[agent] 🚫 BLOCKED: title — reason — task_url` |
| PR ready | #fleet + #reviews | `[agent] ✅ PR READY: title — pr_url` |
| Security alert | #alerts | `🔴 [agent] CRITICAL: title — url` |
| Suggestion | #fleet | `💡 [agent] SUGGESTION: title` |

**EVERY IRC message MUST include a URL when one exists.**

### Creating Follow-Up Tasks (fleet-task-create skill)

**When you discover work SEPARATE from your current task:**

- Bug found → create task for software-engineer
- Missing docs → create task for technical-writer
- Architecture concern → create task for architect
- Test gap → create task for qa-engineer
- Infra issue → create task for devops

New task must reference the parent task. Post to board memory: "Proposed task: {title} for @{agent}".

### When to PAUSE and Escalate (fleet-pause skill)

**Stop and ask when:**

- Requirements are unclear and guessing would waste work
- Change is high-risk (security, data, infrastructure)
- Multiple valid approaches — human should decide
- Another agent's work blocks yours and they're not responding
- You've been working without progress for too long

**How:** Post blocker comment + IRC alert + board memory if it affects others.
**Then WAIT.** Do not continue guessing.

### When to WARN (fleet-alert skill)

**Proactively alert when you notice:**

- Security vulnerability (CVE, exposed secret, vulnerable dependency)
- Quality issue (no tests, low coverage, code smell)
- Missing capability (need a skill, an agent, or knowledge)
- Workflow problem (broken automation, manual step that should be scripted)
- Architecture concern (coupling, scaling, design debt)

### Cross-Referencing

- **EVERY** reference to a file, commit, PR, branch, or task MUST be a clickable URL
- Use the `fleet-urls` skill to resolve URLs from `config/url-templates.yaml`
- **NEVER** paste bare file paths — always GitHub URLs
- **NEVER** reference a task without its MC URL
- Use markdown link format: `[display text](url)`

### Markdown Quality

- Use templates from `agents/_template/markdown/`
- Exploit markdown: headers, tables, code blocks, emoji, checklists
- Every output must be **publication quality** — visually appealing and scannable
- If it looks like a text dump, it's wrong. Restructure it.