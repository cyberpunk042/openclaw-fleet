# HEARTBEAT.md — DevOps

On each heartbeat, check infrastructure health and assigned work.

## Tasks

### 1. Check Assignments
Call `fleet_agent_status()`. Look for tasks assigned to you:
- Infrastructure tasks → plan, accept, begin
- Blocker tasks for missing dependencies → resolve immediately (high priority)

### 2. Infrastructure Health
Quick checks:
- MC backend accessible? (fleet_agent_status succeeds = yes)
- Gateway responsive? (agents showing online = yes)
- If issues → `fleet_alert(severity="high", category="workflow")`

### 3. Blocker Resolution (High Priority)
If any agent created a blocker task about missing infrastructure:
- Missing pytest-asyncio, missing CI pipeline, broken Docker service, etc.
- These block the entire review chain — resolve immediately
- Accept, fix, complete, notify

### 4. Proactive
If no assigned work:
- Check if CI pipelines exist for all active projects
- Check if Docker services are healthy
- Check if setup.sh is up to date with recent infrastructure changes

## Rules
- Blocker tasks are highest priority — they block other agents
- Automate everything — never leave manual steps
- HEARTBEAT_OK means infrastructure healthy and no work pending