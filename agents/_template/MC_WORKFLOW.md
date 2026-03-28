## Mission Control Workflow

You are part of the OpenClaw Fleet, coordinated through Mission Control (MC).

### Your Tools

You have fleet tools as native tool calls. **Use them for ALL fleet operations.**

| Tool | When to Use |
|------|------------|
| `fleet_read_context` | **FIRST thing every session** — get task, project, URLs, team state |
| `fleet_task_accept` | When starting a task — pass your brief plan |
| `fleet_task_progress` | When you have a progress update to share |
| `fleet_commit` | When you have changes to commit — pass files + message |
| `fleet_task_complete` | **When done** — handles push, PR, IRC, custom fields, everything |
| `fleet_alert` | When you find a security/quality/architecture concern |
| `fleet_pause` | When stuck, uncertain, or blocked — stop and escalate |

### Your Workflow

```
1. fleet_read_context()              → understand task, project, context
2. fleet_task_accept(plan="...")     → tell MC you're starting
3. [do your work — read, think, edit, test]
4. fleet_commit(files=[...], message="feat(scope): ...") → after each change
5. fleet_task_progress(done="...", next_step="...")       → if working a while
6. fleet_task_complete(summary="...")  → ONE CALL handles everything
7. fleet_pause(reason="...", needed="...")  → if blocked, STOP and wait
```

### What fleet_task_complete Does For You

When you call `fleet_task_complete`, the system handles:
- Push your branch to remote
- Create a PR with changelog, diff table, and all URLs
- Set task custom fields (branch, pr_url)
- Post structured completion comment to MC
- Notify IRC #fleet and #reviews
- Post to board memory
- Move task to review

**You do NOT need to push, create PRs, construct URLs, or notify IRC yourself.**

### What fleet_commit Does For You

When you call `fleet_commit`, the system handles:
- Validate conventional commit format
- Inject task reference [task:XXXXXXXX] automatically
- Stage the specified files
- Create the commit

**You do NOT need to run git add or git commit yourself.**

### Rules

- **ALWAYS** call `fleet_read_context` first
- **ALWAYS** call `fleet_task_accept` before starting work
- **ALWAYS** call `fleet_task_complete` when done (not raw git/curl)
- **NEVER** construct curl commands to MC API — use fleet tools
- **NEVER** manually push branches or create PRs — fleet_task_complete does it
- **NEVER** manually post to IRC — fleet tools handle notifications
- If you're stuck: `fleet_pause` — do NOT continue guessing

## Git & Commit Standards

### Conventional Commits (Required)

Every commit MUST follow this format:
```
type(scope): description [task:XXXXXXXX]
```

**Types:** feat, fix, docs, refactor, test, chore, ci, style, perf
**Scope:** module or area affected
**Task reference:** added automatically by fleet_commit

### Commit Discipline

- **Commit early and often.** Each commit = one logical change.
- **Never batch all changes** into a single commit at the end.
- Use `fleet_commit` for each logical change.

### Branch Naming

Your worktree branch is already set: `fleet/<your-agent-name>/<task-short-id>`
Do NOT create additional branches.