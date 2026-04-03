# /compact

**Type:** Claude Code Slash Command
**Category:** Built-in
**Available to:** ALL

## Purpose

Compact conversation with optional preservation instructions. Specify what to keep: 'retain task context, plan, contributions'.

## When to Use

Near 70% context used. Between logical tasks. Before rate limit rollover. After long investigation phase.

## Methodology Stages

any (critical near 70% context)

## Relationships

session_manager.py (brain Step 10), CW-03 strategic compaction, PreCompact hook (save state before), PostCompact hook (verify after)
