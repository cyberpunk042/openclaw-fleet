# WorktreeCreate

**Type:** Claude Code Hook (lifecycle event)
**Category:** Workspace (fires when a git worktree is created)
**Handler types:** command, http, prompt, agent
**Can block:** YES (can reject worktree creation)

## What It Actually Does

Fires when Claude Code creates a git worktree (via EnterWorktree tool or /batch operations). Worktrees allow parallel work on different branches without switching the main working directory. The handler can set up the worktree environment, copy agent config, or block creation.

## Fleet Use Case: Worktree Environment Setup

```
WorktreeCreate fires (worktree being created)
├── Setup environment:
│   ├── Copy .claude/ config to worktree
│   ├── Copy agent-specific settings
│   ├── Set up hooks in worktree
│   └── Initialize trail for worktree session
├── Validation:
│   ├── Is worktree creation allowed for this agent role?
│   ├── Resource check: how many worktrees already exist?
│   ├── If too many: exit code 2 → reject (prevent resource exhaustion)
│   └── If allowed: proceed with setup
├── Trail recording:
│   ├── Trail event: worktree_created
│   ├── Branch name, worktree path
│   └── Parent task context
└── Return: {} or exit code 2 (reject)
```

## Fleet Usage

Worktrees are used in fleet for:
- **/batch operations:** Parallel changes across multiple branches — each change in its own worktree
- **Agent isolation:** Agent tool with `isolation: "worktree"` runs subagent in isolated copy
- **Review workflows:** Fleet-ops reviews a PR in a worktree without affecting main checkout
- **Feature branches:** Engineer creates worktree for each task branch

## Relationships

- FIRES ON: git worktree creation (EnterWorktree tool, /batch)
- CAN BLOCK: yes (exit code 2 — reject creation)
- CONNECTS TO: WorktreeRemove hook (complementary — create/remove pair)
- CONNECTS TO: /batch command (creates worktrees for parallel operations)
- CONNECTS TO: Agent tool (isolation: "worktree" parameter)
- CONNECTS TO: EnterWorktree/ExitWorktree tools (worktree management)
- CONNECTS TO: trail system (trail.worktree.created event)
- CONNECTS TO: ENG and DEVOPS roles (primary worktree users)
- TIER: 3 in implementation priority (workspace management)
