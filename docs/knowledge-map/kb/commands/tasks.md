# /tasks

**Type:** Claude Code Built-In Command
**Category:** Agents & Tasks
**Available to:** ALL agents
**Alias:** /bashes

## What It Actually Does

Lists and manages background tasks — Claude Code subprocesses running in parallel. Shows active background tasks with their status (running, completed, failed). Allows checking output of completed tasks.

Background tasks are created when tools run with `run_in_background: true` or when Agent Teams assigns work to teammates.

## When Fleet Agents Should Use It

**Monitor parallel operations:** After launching /batch or background subagents — check what's still running.

**Check subagent results:** After a background agent completes — /tasks shows the result.

**During /loop:** Check if the loop is still running, see iteration results.

## Relationships

- MONITORS: background Agent tool calls
- MONITORS: Agent Teams teammate work
- MONITORS: /loop iterations
- MONITORS: /batch parallel operations
- CONNECTS TO: Agent tool (background: true parameter)
- CONNECTS TO: TaskCreated/TaskCompleted hooks (lifecycle events for background tasks)
- CONNECTS TO: /agents command (manage agent configs, /tasks monitors their execution)
