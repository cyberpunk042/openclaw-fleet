# /branch

**Type:** Claude Code Built-In Command
**Category:** Session Management
**Available to:** ALL agents (especially Architect, Engineer)
**Alias:** /fork

## What It Actually Does

Branches the conversation at the current point. Creates a fork — the current conversation continues as the main branch, and a new branch is created from this exact state. You can explore an alternative approach in the branch without losing the current conversation.

Think of it like git branches but for CONVERSATIONS. The main branch has your current approach. The fork has the alternative. You can switch between them.

## When Fleet Agents Should Use It

**Architect exploring design alternatives:** Architecture requires exploring 3+ options (per architecture-review standard). /branch at the decision point → explore option B in the branch → compare with option A in main → decide.

**Engineer trying risky approach:** Implementation plan has a step that might not work. /branch → try the risky approach in the branch → if it works, merge back; if not, switch to main and try something else.

**PM evaluating sprint options:** Two possible sprint plans with different task orderings. /branch → evaluate plan B in the branch → compare.

## How It Differs from /rewind

- **/rewind** goes BACK — undoes what you did, returns to earlier state
- **/branch** goes SIDEWAYS — creates parallel path from current state, keeps both

/rewind = "that was wrong, undo it"
/branch = "I want to try something ELSE while keeping THIS"

## Relationships

- CREATES: conversation fork from current state
- PRESERVES: both branches (main + fork) accessible
- CONNECTS TO: /plan command (plan mode + branch = explore alternative designs safely)
- CONNECTS TO: architecture-propose skill (min 3 options → branch per option)
- CONNECTS TO: investigation stage (explore alternatives in branches)
- CONNECTS TO: reasoning stage (evaluate approach options)
- CONNECTS TO: using-git-worktrees skill (Superpowers — git worktrees for code, /branch for conversations)
- CONNECTS TO: /rewind (alternative — /rewind goes back, /branch goes sideways)
- COST: each branch maintains its own context (both consume tokens when active)
