# /rewind

**Type:** Claude Code Built-In Command
**Category:** Session Management
**Available to:** ALL agents
**Alias:** /checkpoint

## What It Actually Does

Rewinds the conversation AND/OR code to a previous point. Claude Code creates automatic checkpoints — snapshots of conversation state and file state at key moments. /rewind lets you go back to any checkpoint, undoing both conversation turns AND file changes made since that point.

This is the UNDO mechanism. If an implementation approach went wrong, /rewind takes you back to before you started — conversation context restored, files reverted.

## When Fleet Agents Should Use It

**Wrong implementation approach:** Engineer implemented step 2 of their plan but the approach is wrong. /rewind to before step 2 → try a different approach. Files revert to pre-step-2 state.

**Cascading fix disease:** Agent fixed one thing, broke another, fixed that, broke a third. Instead of continuing the cascade: /rewind to before the first fix → rethink the approach.

**Accidental scope creep:** Agent started modifying files outside the plan. /rewind to before the off-plan changes → stay in scope.

**After /diff reveals problems:** Agent reviews their changes with /diff → sees issues → /rewind to before the problematic changes.

## What Gets Reverted

- Conversation turns after the checkpoint → removed
- File changes after the checkpoint → reverted (git state restored)
- Tool results after the checkpoint → removed

## What Does NOT Get Reverted

- claude-mem observations → persisted in SQLite, not conversation
- Board memory posts → already posted to MC API
- IRC notifications → already sent
- Events emitted → already in JSONL event store
- Git commits already pushed → already on remote

So: local conversation + local files revert. External actions don't.

## Relationships

- CREATES: automatic checkpoints at key moments (file writes, tool calls)
- REVERTS: conversation turns + file changes to checkpoint state
- DOES NOT REVERT: external actions (MC posts, IRC, events, pushed commits)
- CONNECTS TO: /diff command (review changes → decide to rewind)
- CONNECTS TO: cascading_fix disease (rewind is the CURE — stop cascading, go back)
- CONNECTS TO: scope_creep disease (rewind off-plan changes)
- CONNECTS TO: Esc-Esc shortcut (quick rewind to last checkpoint in CLI)
- CONNECTS TO: git worktrees (rewind within worktree doesn't affect other worktrees)
- CONNECTS TO: verification-before-completion skill (Superpowers — if verification fails, rewind)
