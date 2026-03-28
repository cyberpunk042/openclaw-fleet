# HEARTBEAT.md — Worker Agent

On each heartbeat, check for work and report status.

## Tasks

### 1. Check Assignments

Call `fleet_agent_status()`. Look for tasks assigned to you in inbox status.
If you have assigned work: call `fleet_task_accept()` to start.

### 2. Report Status

If you have an in_progress task:
- Post a progress update via `fleet_task_progress()`
- If blocked: use `fleet_pause()` to escalate

If you have no work: HEARTBEAT_OK.

## Rules

- HEARTBEAT_OK means no work available.
- Accept and start tasks promptly when assigned.
- If stuck, pause immediately — don't spin.