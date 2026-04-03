# pyright-lsp

**Type:** Claude Code Plugin (LSP — Language Server Protocol)
**Source:** Official Anthropic (claude-plugins-official)
**Runtime:** pyright-langserver (continuous background process)
**Assigned to:** ALL Python agents

## What It Actually Is

A Language Server Protocol plugin that runs pyright as a continuous BACKGROUND process. After every file edit Claude makes, pyright analyzes the changed file and reports type errors, missing imports, incorrect function signatures, and other static analysis findings AUTOMATICALLY. No manual trigger — it's always on.

This is fundamentally different from running `pyright` as a Bash command. The LSP integration means:
- **Continuous:** diagnostics appear after EVERY edit, not when you remember to check
- **Incremental:** only re-analyzes changed files (fast)
- **Navigation:** jump to definition, find all references, get type info on hover
- **Import resolution:** knows which imports are valid, suggests missing ones

## Why This Matters for Fleet

Our ENTIRE codebase is Python (fleet/core/, fleet/cli/, fleet/mcp/, fleet/infra/). 94 core modules with type hints on public functions (per development conventions). pyright catches:

- Calling a function with wrong argument types
- Using a return value incorrectly (e.g., treating Optional as non-Optional)
- Missing imports after refactoring
- Accessing attributes that don't exist on a type
- Incompatible types in assignments

These errors would otherwise reach fleet-ops review or even production. pyright catches them at EDIT time — the cheapest possible fix point.

## What It Provides

**Automatic diagnostics (after every edit):**
```
fleet/core/models.py:124: error: Property "task_progress" does not exist on "TaskCustomFields"
fleet/mcp/tools.py:695: error: Argument of type "int" is not assignable to parameter "estimated_tokens" of type "float"
```

**Code navigation:**
- Jump to definition: "where is this function defined?"
- Find references: "what calls this function?"
- Type info: "what type does this return?"
- Import suggestions: "this name isn't imported — add `from fleet.core.models import Task`"

## Prerequisites

1. Install pyright binary: `npm i -g pyright`
2. Install plugin: `/plugin install pyright-lsp`
3. That's it — starts automatically on next session

## Assigned Roles

| Role | Why |
|------|-----|
| Engineer | Implementing Python code — catch type errors during coding |
| Architect | Reading/reviewing Python code — navigation helps understand structure |
| QA | Writing Python tests — catch test code errors |
| DevOps | Writing Python scripts/IaC — catch errors in infrastructure code |
| DevSecOps | Reviewing Python code — type info helps security analysis |
| PM | Not typically writing code — OPTIONAL |
| Writer | Not typically writing code — OPTIONAL |
| UX | Not typically writing code — OPTIONAL |
| Fleet-ops | Reviewing PRs — diagnostics highlight issues |
| Accountability | Not typically writing code — OPTIONAL |

## Methodology Stages

| Stage | Value |
|-------|-------|
| analysis | Navigation tools help understand existing code (jump to def, find refs) |
| investigation | Type info helps evaluate code patterns |
| work | PRIMARY — catch type errors during implementation |

## Relationships

- INSTALLED BY: scripts/install-plugins.sh (from agent-tooling.yaml)
- PREREQUISITE: pyright binary (npm i -g pyright) — add to scripts/install-dependencies.sh
- RUNS AS: background process (continuous, not per-command)
- COMPLEMENTS: quality-lint skill (linting is broader — pyright handles types specifically)
- COMPLEMENTS: ruff (Python linter for style — pyright handles types and imports)
- CONNECTS TO: PostToolUse hook (diagnostics run automatically after Write/Edit tools)
- CONNECTS TO: feature-implement skill (catch errors during implementation)
- CONNECTS TO: fleet_commit (commit with confidence — pyright already checked the code)
- CONNECTS TO: challenge_automated.py (automated challenges can include type check results)
- CONNECTS TO: anti-corruption (type system prevents "code that looks right but is wrong")
- CONNECTS TO: developer conventions (CLAUDE.md: "Python type hints on all public functions")
- OUR FLEET: 94 Python modules with type hints. pyright validates every edit against these hints.
- OTHER LSP PLUGINS AVAILABLE: clangd (C/C++), gopls (Go), typescript-lsp (TS), rust-analyzer (Rust), jdtls (Java) — for when fleet works on non-Python projects.
- ZERO DOWNSIDE: passive background process. No false positives on correct code. Only catches real type errors.
