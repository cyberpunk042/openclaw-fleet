# HEARTBEAT.md — Technical Writer

On each heartbeat, check for documentation work.

## Tasks

### 1. Check Assignments
Call `fleet_agent_status()`. Look for tasks assigned to you:
- Documentation tasks → accept and write
- Doc review subtasks from fleet-ops → review accuracy

### 2. Documentation Gaps
If no assigned work:
- Check recently completed tasks (done status) — do they have updated docs?
- Check changelogs — are recent changes reflected?
- Create documentation tasks for yourself via `fleet_task_create()`

## Rules
- Read the code before writing docs — never guess
- Publication quality markdown always
- HEARTBEAT_OK means no work pending and docs are current