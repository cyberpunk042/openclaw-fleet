# WorktreeRemove

**Type:** Claude Code Hook (lifecycle event)
**Category:** Workspace (fires when a git worktree is removed)
**Handler types:** command, http, prompt, agent
**Can block:** NO (observation only)

## What It Actually Does

Fires when a git worktree is removed (via ExitWorktree tool or automatic cleanup). The handler can perform cleanup operations — remove temporary files, record trail events, update resource counts.

## Fleet Use Case: Cleanup + Trail

```
WorktreeRemove fires (worktree being removed)
├── Cleanup:
│   ├── Remove worktree-specific temp files
│   ├── Clean up agent config copies
│   ├── Decrement active worktree count
│   └── Release any locks held in worktree
├── Trail recording:
│   ├── Trail event: worktree_removed
│   ├── Which branch, which agent
│   ├── Duration of worktree existence
│   └── Whether changes were committed from worktree
├── Merge status:
│   ├── Were worktree changes merged? → log success
│   ├── Were changes abandoned? → log and flag
│   └── Orphan branches? → alert fleet-ops
└── Return: {} (observation only)
```

## Relationships

- FIRES ON: git worktree removal (ExitWorktree tool, automatic cleanup)
- CANNOT BLOCK: observation only (removal already happening)
- CONNECTS TO: WorktreeCreate hook (complementary — create/remove pair)
- CONNECTS TO: ExitWorktree tool (triggers removal)
- CONNECTS TO: /batch command (cleans up worktrees after parallel operations)
- CONNECTS TO: Agent tool (automatic cleanup when isolation: "worktree" agent finishes)
- CONNECTS TO: trail system (trail.worktree.removed event)
- TIER: low priority (cleanup, not critical path)
