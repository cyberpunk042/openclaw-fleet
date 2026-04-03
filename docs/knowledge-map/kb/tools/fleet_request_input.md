# fleet_request_input

**Type:** MCP Tool (communication, contribution request)
**System:** S08 (MCP Tools)
**Module:** fleet/mcp/tools.py:2481-2562
**Stage gating:** None — agents can request input at any stage

## Purpose

Request a specific role's expertise on your task. When you need a colleague's input (architect for design guidance, QA for test criteria, devsecops for security review), this tool posts an @mention to that role via board memory and a typed comment on your task. The mentioned role sees the request in their next heartbeat context (MESSAGES section).

Paired with fleet_contribute — you request, they contribute. If no contribution task exists yet for this role on your task, PM should create one.

## Parameters

- `task_id` (string, required) — YOUR task ID (the task you need input on)
- `from_role` (string, required) — Role to request from: architect, qa-engineer, devsecops-expert, devops, ux-designer, technical-writer
- `question` (string, required) — What you need — be specific. "Need design guidance for auth middleware" not "need help."

## Chain Operations

```
fleet_request_input(task_id, from_role, question)
├── POST BOARD MEMORY: 
│   ├── content: "[{agent}] @{from_role} Input requested for task:{id}: {question}"
│   ├── tags: [chat, mention:{from_role}, task:{task_id}, from:{agent}, input_request]
│   └── This makes it appear in the target role's MESSAGES section at next heartbeat
├── POST TASK COMMENT: "Input requested from @{from_role}: {question}"
│   └── Type: input_request (typed comment for trail/filtering)
├── TRAIL: "Input requested: {agent} → @{from_role} for task:{id}"
│   └── tags: [trail, task:{task_id}, input_request]
├── IRC: "[request] {agent} → @{from_role}: {question[:60]}"
│   └── IRC #fleet for fleet-wide visibility
├── EVENT: fleet.input.requested
│   └── subject: task_id, requester: agent, target_role: from_role
└── RETURN: {ok, requester, target_role, task_id}
```

## The Request → Contribution Flow

```
1. Engineer needs architect's design input for auth middleware
2. Engineer calls: fleet_request_input(task_id, "architect", "Need patterns for JWT middleware")
3. Board memory: @architect mention posted
4. Architect's next heartbeat: sees request in MESSAGES section
5. If contribution task exists: architect works on it → fleet_contribute delivers input
6. If no contribution task: PM sees the @mention → creates contribution subtask
7. Architect's contribution appears in engineer's INPUTS FROM COLLEAGUES section
8. Engineer references architect's design in implementation
```

## Who Uses It

| Role | From Role | When | Why |
|------|-----------|------|-----|
| Engineer | architect | Before implementation | Need design guidance, pattern selection |
| Engineer | qa-engineer | Before/during work | Need test criteria, edge case definition |
| Engineer | devsecops-expert | Security-relevant tasks | Need security requirements |
| Architect | engineer | During design | Need feasibility assessment |
| Any agent | any role | When missing expertise | Request colleague's specialized knowledge |

## Relationships

- PAIRED WITH: fleet_contribute (this requests, that delivers)
- POSTS TO: board memory (mention:{from_role} tag → appears in target's heartbeat context)
- POSTS TO: task comments (input_request typed comment)
- RECORDS: trail event (input_request)
- NOTIFIES: IRC #fleet
- EMITS: fleet.input.requested event
- CONNECTS TO: contributions.py (brain checks if contribution task exists for this role)
- CONNECTS TO: synergy-matrix.yaml (defines valid contribution relationships)
- CONNECTS TO: PM workflow (PM may need to create contribution subtask if one doesn't exist)
- CONNECTS TO: fleet-context.md Layer 6 MESSAGES section (target role sees the request)
- CONSUMED BY: orchestrator Step 0 (request appears in target's context refresh)
