# .claude/rules/work-mode.md — How Claude Operates in This Repo

> Extracted from prior `CLAUDE.md` lines 217-243 (Work Mode section). This file holds the detail; `CLAUDE.md` has a summary pointer.

## Context

OpenFleet is a platform project, not an AI assistant. OpenFleet produces the platform that manages AI assistants (via OpenArms runtime). The AI assistants have their own templates in `agents/_template/`. In this session you are likely a **solo coding AI helping the PO develop the platform** — not a fleet agent.

## Default Operation Mode

**Solo coding session on `main` branch:**
- Work on `main` — always. No feature branches unless the PO explicitly asks.
- Commit directly to main. The PO decides when and what to commit.
- No worktrees. Worktree mode is for AI assistants (OpenArms), not platform development.
- No git stash. Old fleet agent stashes are landmines in this repo.
- No subagent dispatch without pausing for PO review between each task.
- No skill ceremonies (brainstorming → writing-plans → subagent-driven-development chains) unless the PO explicitly asks for that workflow.

## Git Safety

**Before any git operation** ask: can you recover without destructive commands?

**BLOCKED commands** (do not run without explicit PO approval):
- `git restore`
- `git checkout -- .`
- `git reset --hard`
- `git stash drop`
- `git clean -f`
- `git push --force` (to main/master especially)

If you can't recover from an operation, don't do it.

## Output Discipline

**Read command output in FULL.** Never default to truncation. Internal tool output (gateway, view, pipeline, compliance, health) is curated — read every line. If you must truncate, state a REASON first.

**When producing work**: show the output. Wait for PO review. Do not chain multiple tasks without the PO seeing each result.

## Behavioral Rules

**When called out:** stop. Re-read what the PO said. Identify what you're actually missing. Do not say "you're right" and then repeat the same mistake.

**When told to investigate:** investigate. Do not propose fixes. Read code. Compare data shapes. Trace execution. Present findings. The PO decides what to fix and when.

**When producing or reviewing code:** every function that reads data from another module MUST be verified against the REAL data shape that module returns. Read the actual provider/consumer. Do not write code or tests against assumed data shapes. Test data in tests must match real provider output — if the test uses a different shape than the provider returns, the test is lying.

**Understanding before action.** When asked to understand the project, keep reading until told to stop. Do not present summaries prematurely. Synthesis ≠ restating documents.

**Grounded in reality.** Before proposing any work, state the current reality. Do not propose work that requires infrastructure or capabilities that don't exist yet.

**Do what is asked.** When given a task, do exactly that task. Do not optimize, narrow, or skip ahead. Do not ask "which subset?" when told to do the whole thing.

## PO Approval Boundary

**The PO (product owner) approves major changes.** Unilateral decisions on project standards, schemas, configs, or core brain files (CLAUDE.md, AGENTS.md) are forbidden. Pattern: propose → PO approves → execute.

**Safe unilateral work** (no approval needed unless the PO redirects):
- Reading the codebase, the brain, any documentation
- Running tools (gateway, view, pipeline post, lint, validate)
- Drafting in `docs/drafts/` or scratch locations
- Authoring new wiki pages that follow brain standards
- Closing mechanical lint/validate errors that require no judgment (frontmatter field additions, format migrations)
- Contributing observations to the brain via `gateway contribute`

**Needs PO approval before execution:**
- Changes to `CLAUDE.md`, `AGENTS.md`, `config/methodology.yaml`, `wiki/config/wiki-schema.yaml`
- New schemas, relaxed schemas, or any policy decision affecting how we measure quality
- Git operations that could lose work
- Adding or removing core framework files
- Restructuring root directories

## Verify Before Contributing

When using `gateway contribute` to write back to the brain: verify claims about OpenFleet's state before publishing. Self-failure 2026-04-16: contributed a correction claiming root AGENTS.md didn't exist — it did. One-line `ls` would have caught it. Amended via a second contribution. Principle: "Declarations aspirational until infrastructure verifies them" applies to my own contributions too.
