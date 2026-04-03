# quality-lint

**Type:** Skill (AICP Lifecycle)
**Location:** devops-expert-local-ai/.claude/skills/quality-lint/
**Invocation:** /quality-lint
**Effort:** medium
**Roles:** Software Engineer, QA Engineer

## What It Does

Run linting and auto-fix code style issues. Checks formatting, import order, type annotations, naming conventions. Uses project-configured linters (ruff, eslint, etc.) and applies safe auto-fixes.

## Fleet Use Case

Engineer runs as part of WORK stage cleanup before fleet_commit. QA uses as a quality gate — lint failures indicate code that doesn't meet standards. Fleet convention: `ruff check` + `ruff format` for Python projects.

## Relationships

- USED BY: software-engineer (WORK), qa-engineer (REVIEW)
- CONNECTS TO: fleet_commit tool (lint before commit)
- CONNECTS TO: ESLint MCP (JavaScript/TypeScript linting)
- CONNECTS TO: pyright-lsp plugin (type checking complement)
