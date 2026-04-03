# PostCompact

**Type:** Claude Code Hook (lifecycle event)
**Category:** Session Lifecycle (fires after context compaction)
**Handler types:** command, http, prompt, agent
**Can block:** NO
**Matcher:** `manual` (user triggered /compact), `auto` (automatic at ~95%)

## What It Actually Does

Fires AFTER context compaction completes. The conversation has been compressed — the handler can verify that critical context survived, re-inject anything that was lost, and confirm the agent is in a good state to continue.

Paired with PreCompact (which saves state BEFORE compression). PostCompact is the VERIFICATION step.

## Fleet Use Case: Context Recovery Verification

```
PostCompact fires (compaction just completed)
├── Check: does agent still know current task ID?
│   ├── Read from .claude/memory/ or claude-mem
│   └── If lost: re-inject task context from brain's latest files
├── Check: does agent still know its role?
│   └── CLAUDE.md re-read from disk (always survives) — should be fine
├── Check: were key decisions preserved?
│   ├── Read PreCompact saved state
│   └── Compare with current context
├── If critical context lost:
│   ├── Inject from knowledge map (SessionStart-like injection)
│   └── Inject from claude-mem search (find recent observations)
└── Return: {} (acknowledged)
```

## Relationships

- FIRES AFTER: /compact or auto-compact at ~95%
- PAIRED WITH: PreCompact (save state → compact → verify state)
- CONNECTS TO: SessionStart hook (trigger="compact" — fires nearby, can also inject)
- CONNECTS TO: claude-mem (search for recent observations to verify context)
- CONNECTS TO: .claude/memory/ (check saved state from PreCompact)
- CONNECTS TO: CW-04 (efficient regathering protocol)
- CONNECTS TO: session_manager.py (brain's compaction decisions)
- KEY INSIGHT: compaction is LOSSY. Even with good /compact instructions, details are lost. PostCompact + PreCompact together form the safety net: save before, verify after.
