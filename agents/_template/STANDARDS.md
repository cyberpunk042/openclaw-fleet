# Fleet Standards — Communication & Quality

How to communicate across fleet surfaces. Every other standard (git, code, testing,
workflow, methodology) lives in CLAUDE.md, HEARTBEAT.md, or task-context.md.

## Communication Surfaces

Three surfaces, three purposes. Use the RIGHT one every time.

### Task Comments

**For: information about THIS SPECIFIC TASK.**

| Situation | Action |
|-----------|--------|
| Starting work | Post acceptance with plan |
| Made progress | Post progress update |
| Blocked | Post blocker with reason + needed action |
| Completed | Post completion with PR, branch, files, commits — ALL as URLs |

Use templates from `agents/_template/markdown/comment-*.md`.

### Board Memory

**For: information that spans tasks — the fleet's knowledge base.**

| Situation | Template | Required Tags |
|-----------|----------|---------------|
| Security/quality/architecture concern | memory-alert.md | alert, {severity}, project:{name} |
| Decision made | memory-decision.md | decision, project:{name} |
| Improvement idea | memory-suggestion.md | suggestion, {area} |
| PR ready for review | inline | pr, review, project:{name} |
| Knowledge for other agents | inline | knowledge, project:{name} |

**Tags are MANDATORY. Untagged entries are useless.**

### IRC

**For: real-time alerts the human sees immediately.**

| Situation | Channel | Format |
|-----------|---------|--------|
| Task accepted | #fleet | `[agent] STARTED: title — task_url` |
| Task blocked | #fleet | `[agent] BLOCKED: title — reason — task_url` |
| PR ready | #fleet + #reviews | `[agent] PR READY: title — pr_url` |
| Security alert | #alerts | `[agent] CRITICAL: title — url` |

**EVERY IRC message MUST include a URL when one exists.**

### When to PAUSE

- Requirements unclear and guessing would waste work
- Change is high-risk (security, data, infrastructure)
- Multiple valid approaches — human should decide
- Blocked by another agent and they're not responding

**Post blocker comment + IRC alert. Then WAIT.**

### When to WARN

- Security vulnerability (CVE, exposed secret, vulnerable dependency)
- Quality issue (no tests, low coverage, code smell)
- Architecture concern (coupling, scaling, design debt)
- Workflow problem (broken automation, manual step that should be scripted)

## Cross-Referencing

- **EVERY** reference to a file, commit, PR, branch, or task MUST be a clickable URL
- Use the `fleet-urls` skill to resolve URLs from `config/url-templates.yaml`
- **NEVER** paste bare file paths — always GitHub URLs
- **NEVER** reference a task without its MC URL
- Use markdown link format: `[display text](url)`

## Output Quality

- Use templates from `agents/_template/markdown/`
- Exploit markdown: headers, tables, code blocks, checklists
- Every output must be **publication quality** — scannable, structured
- If it looks like a text dump, restructure it.
