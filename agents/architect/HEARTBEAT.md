# HEARTBEAT.md — Architect

On each heartbeat, check for design work and review requests.

## Tasks

### 1. Check Assignments
Call `fleet_agent_status()`. Look for tasks assigned to you:
- Design tasks → plan approach, accept, begin
- Architecture review subtasks from fleet-ops → review and report

### 2. Architecture Review (If Requested)
When fleet-ops creates a review subtask for you:
- Read the implementation against the original design intent
- Check: correct layer boundaries, no circular dependencies, proper abstractions
- Report: approve with notes, or flag via `fleet_alert(category="architecture")`

### 3. Proactive Design Health
If no assigned work:
- Check recently completed tasks for architectural drift
- Review board memory for design decisions that need documenting
- Identify patterns that should be standardized

## Rules
- Use extended thinking for complex design analysis
- Post design decisions to board memory with tags [decision, architecture]
- HEARTBEAT_OK means no work available and architecture is healthy