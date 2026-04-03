# fleet_heartbeat_context

**Type:** MCP Tool (read-only, role-specific)
**System:** S08 (MCP Tools), S19 (Session/Context)
**Module:** fleet/mcp/tools.py:2096-2140
**Stage gating:** None

## Purpose

Get role-specific heartbeat data in one call. Returns the same comprehensive data that the orchestrator pre-embeds into fleet-context.md, but on-demand. The key difference: this uses role_providers.py to deliver ROLE-SPECIFIC data — fleet-ops gets pending approvals and review queue, PM gets unassigned tasks and sprint progress, architect gets tasks needing design review, workers get their task count and review status.

The result is assembled by context_assembly.assemble_heartbeat_context() with the full ROLE_PROVIDERS mapping.

## Parameters

None (uses agent_name from session context to determine role).

## Chain Operations

```
fleet_heartbeat_context()
├── RESOLVE: agent_name from ctx.agent_name
├── DETERMINE ROLE: agent_roles.AGENT_ROLES[agent_name] → primary_role
├── LOAD: mc.list_tasks(board_id) → all tasks
├── LOAD: mc.list_agents() → all agents
├── ASSEMBLE: context_assembly.assemble_heartbeat_context(
│     agent_name, role, tasks, agents, mc, board_id, event_store, ROLE_PROVIDERS)
│   ├── Fleet state (work_mode, cycle_phase, backend_mode)
│   ├── PO directives (from board memory, filtered for this agent or "all")
│   ├── Messages (@mentions for this agent from board memory)
│   ├── Assigned tasks (FULL detail — verbatim, stage, readiness, artifacts)
│   ├── Role-specific data via ROLE_PROVIDERS:
│   │   ├── fleet_ops_provider():
│   │   │   ├── pending_approvals (list with task_id, confidence, action_type)
│   │   │   ├── review_queue (tasks in "review" status)
│   │   │   └── offline_agents (agents not responding)
│   │   ├── pm_provider():
│   │   │   ├── unassigned_tasks (inbox with no agent — PM must assign)
│   │   │   ├── blocked_tasks (dependency not met)
│   │   │   └── sprint_progress (done/total, velocity)
│   │   ├── architect_provider():
│   │   │   └── tasks_needing_design (high complexity or design_review tag)
│   │   ├── devsecops_provider():
│   │   │   ├── security_tasks (security-tagged tasks)
│   │   │   └── prs_needing_review (PRs with security implications)
│   │   └── worker_provider():
│   │       ├── task_count (assigned to this agent)
│   │       └── in_review_count (this agent's tasks in review)
│   └── Events since last heartbeat (filtered by agent's tag subscriptions)
└── RETURN: assembled heartbeat bundle with ok=True
```

## Who Uses It

| Role | What They Get | What They Do With It |
|------|-------------|---------------------|
| Fleet-ops | pending_approvals, review_queue | Process reviews via fleet_approve |
| PM | unassigned_tasks, blocked, sprint | Assign via fleet_task_create, unblock, plan |
| Architect | tasks_needing_design | Contribute design_input via fleet_contribute |
| DevSecOps | security_tasks, PRs | Security review, contribute security_requirement |
| Workers | task_count, in_review | Focus on assigned work, wait on reviews |
| ALL | directives, messages, events | Act on PO directives first, respond to mentions |

## Relationships

- READS FROM: mc_client.py (tasks, agents, board memory), event store (agent feed)
- USES: context_assembly.py (assemble_heartbeat_context), role_providers.py (5 role-specific providers)
- USES: agent_roles.py (AGENT_ROLES — determine role from agent name)
- SAME DATA AS: fleet-context.md Layer 6 (pre-embedded by orchestrator every 30s)
- ON-DEMAND vs PRE-EMBEDDED: fleet-context.md is written BEFORE agent wakes; this tool is called BY the agent for fresh data
- CONNECTS TO: heartbeat_gate.py (brain evaluates same data to decide wake vs silent — FREE Python, no Claude call)
- CONNECTS TO: HEARTBEAT.md Layer 8 (agent reads this data, then follows HEARTBEAT.md priority order)
- CONNECTS TO: driver.py (driver agents use this data to create their own work)
- FEEDS: agent's heartbeat decision (directives → messages → core job → proactive → health → HEARTBEAT_OK)
