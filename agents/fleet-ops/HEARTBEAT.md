# HEARTBEAT.md — Fleet Ops Governance

On each heartbeat, enforce fleet health, process approvals, and maintain standards.

## Tasks

### 1. Board Health Check

Call `fleet_agent_status()` to get fleet snapshot. Check:
- Tasks in inbox > 2 hours without assignment → alert via `fleet_alert()`
- Tasks in review > 24 hours without activity → alert + nudge
- Blocked tasks where blocker is done → flag stale dependency
- Agents offline > 2 hours → alert IRC #alerts

If all clear: proceed to next check.

### 2. Process Approvals

From `fleet_agent_status()` response, check `pending_approvals`.
- Approvals with confidence >= 80%: approve via `fleet_approve(approval_id, "approved")`
- Approvals with confidence < 80%: review the task context, post analysis comment
- Approvals pending > 48 hours: escalate to IRC #alerts

### 3. Quality Spot Check (every 3rd heartbeat)

Check recent completed tasks for:
- Structured comment format (## headers present?)
- PR URL in custom fields for code tasks
- Conventional commit format in branches
- Tags properly set on tasks

Post findings only if violations found via `fleet_alert(category="quality")`.

### 4. Daily Digest (once per day)

Check board memory for today's digest (tag: `daily`).
If none exists, generate and post:
- Task counts by status
- Active work list with agents
- Pending reviews with PR URLs
- Agent health (online/offline)
- Sprint velocity if applicable

Post to board memory with tags [report, digest, daily].

## Rules

- **Process approvals actively.** Don't just monitor — approve or reject.
- Use `fleet_approve()` for approvals, `fleet_alert()` for issues
- Use `fleet_agent_status()` as your primary data source
- Only alert if something is wrong
- HEARTBEAT_OK means nothing needed attention