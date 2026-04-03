# superpowers

**Type:** Claude Code Plugin (development methodology)
**Source:** github.com/obra/superpowers — 132,053 stars (most starred plugin in the ecosystem)
**Official:** Anthropic marketplace member
**Assigned to:** ALL development agents (evaluate first — autonomy adaptation needed)

## What It Actually Is

Not a collection of utilities — a COMPLETE SOFTWARE DEVELOPMENT METHODOLOGY enforced through skills. 14 core skills that trigger AUTOMATICALLY (mandatory, not suggestions). The plugin fundamentally changes HOW Claude Code does development: brainstorm before code, TDD enforcement (deletes code written before tests), plans broken into 2-5 minute tasks, subagent-driven development with two-stage review.

This is the HOW layer. Our fleet methodology defines WHAT stages to go through (conversation→analysis→investigation→reasoning→work). Superpowers defines HOW to execute within those stages — especially the work stage.

## 14 Core Skills

| Skill | What It Enforces |
|-------|-----------------|
| **brainstorming** | Socratic design refinement BEFORE any code. Forces thinking before building. |
| **writing-plans** | Plans broken into 2-5 minute tasks with EXACT file paths and verification steps. "Clear enough for an enthusiastic junior dev with poor taste, no judgment, no project context, and an aversion to testing." |
| **executing-plans** | Batch execution with human checkpoints. Not autonomous — checks in. |
| **subagent-driven-development** | Each task dispatched to FRESH subagent with two-stage review: (1) spec compliance, (2) code quality. |
| **test-driven-development** | TRUE TDD: write failing test → watch it fail → write minimal code → watch it pass → commit. **DELETES code written before tests.** |
| **systematic-debugging** | 4-phase root cause: reproduce → isolate → understand → fix. No guessing. |
| **verification-before-completion** | Ensures it is ACTUALLY fixed. Not "it compiles" = done. |
| **requesting-code-review** | Pre-review checklist before submitting work. |
| **receiving-code-review** | Structured response to review feedback. |
| **using-git-worktrees** | Parallel development branches for isolation. |
| **finishing-a-development-branch** | Merge/PR decision workflow. |
| **dispatching-parallel-agents** | Concurrent subagent workflows for parallelism. |
| **writing-skills** | Meta-skill for creating new skills. |
| **using-superpowers** | Introduction to the skills system. |

Plus 5 experimental in superpowers-lab: finding-duplicate-functions, mcp-cli, slack-messaging, using-tmux, windows-vm.

## The Methodology Synergy

```
OUR 5-STAGE METHODOLOGY (WHAT to do):
  conversation → analysis → investigation → reasoning → work

SUPERPOWERS (HOW to do it):
  brainstorming → writing-plans → TDD → verification → review

FLEET GUARDRAILS (WHAT NOT to do):
  no code before work stage, one step at a time, PO approves, 10 anti-corruption rules

THREE LAYERS TOGETHER = most rigorous agent development workflow in the ecosystem
```

## Adaptation Needed for Fleet

**The conflict:** Superpowers assumes AUTONOMOUS multi-hour execution. An agent gets a task, brainstorms, plans, implements with TDD, verifies, reviews — all in one long session without checking in.

**Our model:** "One step at a time. Present the plan, wait for 'go', then execute." Fleet guardrails require PO checkpoints.

**Adaptation options:**
1. Install whole plugin and add fleet-specific rules that override autonomy (CLAUDE.md says "check in at each milestone")
2. Cherry-pick the 6 methodology skills into our own skills system (lose auto-updates but gain control)
3. Install and configure to work alongside our stage protocol (both enforce, but different aspects)

**Which skills are most valuable without full autonomy:**
- brainstorming (before code — aligns with REASONING stage)
- test-driven-development (TDD — aligns with WORK stage quality)
- systematic-debugging (4-phase — aligns with INVESTIGATION)
- verification-before-completion (verify — aligns with fleet_task_complete pre-check)
- writing-plans (specific plans — aligns with fleet_task_accept)

## Relationships

- INSTALLED BY: /plugin install superpowers (Anthropic marketplace)
- LAYERS ON TOP OF: our 5-stage methodology (complementary, not competing)
- CONNECTS TO: stage_context.py (stage protocol + Superpowers methodology = double enforcement)
- CONNECTS TO: fleet_task_accept (writing-plans skill feeds the plan quality)
- CONNECTS TO: fleet_task_complete (verification-before-completion skill adds pre-completion check)
- CONNECTS TO: /debug command (systematic-debugging skill is the deep version)
- CONNECTS TO: /plan command (writing-plans skill is the deep version)
- CONNECTS TO: Agent Teams (subagent-driven-development maps to our dispatch model)
- CONNECTS TO: quality-coverage skill (TDD enforces test-first coverage)
- CONNECTS TO: fleet_commit (TDD: test → fail → code → pass → commit — each commit carries evidence)
- CONNECTS TO: anti-corruption (structural prevention — TDD DELETES code without tests, brainstorming prevents jumping to code)
- CONFLICTS WITH: fleet guardrails (autonomy level needs throttling)
- PENDING PO DECISION: D2 (whole plugin vs cherry-pick)
