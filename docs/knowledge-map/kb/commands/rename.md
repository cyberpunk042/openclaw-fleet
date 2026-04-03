# /rename

**Type:** Claude Code Built-In Command
**Category:** Session Management
**Available to:** ALL agents

## What It Actually Does

Renames the current session. Sessions are identified by an auto-generated ID, but /rename lets agents give them a human-readable name. This makes /resume easier — instead of remembering a session ID, agents can resume by name.

## When Fleet Agents Should Use It

**Between-task clarity:** After starting work on a new task — rename the session to match the task ID (e.g., "TASK-42-auth-middleware"). Makes session recovery meaningful.

**Before /export:** Give the session a descriptive name before exporting so the archive is identifiable.

**After gateway restart:** If session was auto-named, rename to reflect the work context.

## Relationships

- COMPLEMENTS: /resume (resume by name instead of ID)
- COMPLEMENTS: /export (named exports are identifiable)
- CONNECTS TO: SessionStart hook (session naming at start)
- CONNECTS TO: trail system (session name in trail events)
