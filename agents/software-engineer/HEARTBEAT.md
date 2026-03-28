# HEARTBEAT.md — Software Engineer

On each heartbeat, check for implementation work and fix tasks.

## Tasks

### 1. Check Assignments
Call `fleet_agent_status()`. Look for tasks assigned to you:
- Implementation tasks → plan, accept, begin
- Fix tasks from QA → read feedback, fix root cause, re-submit

### 2. Fix Tasks (High Priority)
If qa-engineer or fleet-ops created a fix task for you:
- Read the failure details carefully
- Fix the ROOT CAUSE, not just the symptom
- Add tests that would have caught the issue
- Re-submit for review

### 3. In-Progress Work
If you have an in_progress task:
- Post progress update via `fleet_task_progress()`
- If blocked → `fleet_pause()` immediately

### 4. Proactive
If no assigned work:
- Check for tasks in inbox that match your capabilities
- Check board memory for implementation needs that haven't been tasked yet

## Rules
- Run tests before completing ANY task
- Create follow-up tasks when you discover problems
- HEARTBEAT_OK means no work available