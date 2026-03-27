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

## Communication

- Be concise in task comments
- Use structured formats (lists, code blocks) for readability
- Reference files with relative paths from project root
- Reference tasks with `[task:XXXXXXXX]` format