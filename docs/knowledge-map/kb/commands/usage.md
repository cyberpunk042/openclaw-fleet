# /usage

**Type:** Claude Code Slash Command
**Category:** Built-in
**Available to:** ALL

## Purpose

Show plan usage limits and rate limit status (5h + 7d windows).

## When to Use

Check remaining quota before heavy operations. Near rate limit rollover awareness.

## Methodology Stages

any (critical near limits)

## Relationships

budget_monitor.py (quota checking), CW-07 rate limit awareness, session_manager.py (rollover)
