# fleet_gate_request

**Type:** MCP Tool (governance, PO gate)
**System:** S08 (MCP Tools), S01 (Methodology)
**Module:** fleet/mcp/tools.py:2564-2663
**Stage gating:** None — gates can be requested at any stage (but typically at readiness 50% or 90%)

## Purpose

Request PO approval at a methodology readiness gate. Tasks have two checkpoints where PO confirmation is needed: readiness 50% (direction checkpoint — "am I on the right track?") and readiness 90% (final gate — "my plan is ready, approve to proceed to work"). Posts the request to board memory with `po-required` tag, notifies PO via ntfy (high priority), marks the gate as pending on the task, and records a trail event.

The PO sees the request on ntfy, reviews the plan/progress, and either advances readiness (approving the gate) or provides feedback. Brain Step 3b (not yet implemented) would process gate decisions automatically.

## Parameters

- `task_id` (string, required) — Task requiring PO gate approval
- `gate_type` (string, required) — Gate type: "readiness_50" (direction), "readiness_90" (final), "phase_advance"
- `summary` (string, required) — What you've done and why PO approval is needed

## Chain Operations

```
fleet_gate_request(task_id, gate_type, summary)
├── LOAD TASK: mc.get_task(board_id, task_id) → get task_title
├── POST BOARD MEMORY: 
│   ├── content: "GATE REQUEST ({gate_type})\nTask: {title}\nAgent: {agent}\nSummary: {summary}"
│   ├── tags: [gate, po-required, {gate_type}, task:{task_id}, from:{agent}]
│   └── "po-required" tag means PO MUST see and decide
├── SET GATE PENDING: mc.update_task → custom_fields.gate_pending = gate_type
│   └── Orchestrator Step 3b (not built) would check this field
├── NOTIFY PO: ntfy high priority
│   ├── title: "Gate: {gate_type}"
│   ├── message: "Task: {task_title}\n{summary}"
│   └── PO sees on phone, reviews, decides
├── IRC: "[gate] {gate_type}: {task_title} — PO approval needed"
│   └── Would go to #gates channel when it exists (currently #fleet)
├── TRAIL: "Gate requested: {gate_type} by {agent} for task:{id}"
│   └── tags: [trail, task:{task_id}, gate_requested]
├── EVENT: fleet.gate.requested
│   └── gate_type, task_id, agent
└── RETURN: {ok, gate_type, task_id, status: "pending_po_approval"}
```

## The Gate Flow

```
Task in REASONING stage, readiness at 85%:
1. Agent completes plan, references verbatim, specifies target files
2. Agent calls: fleet_gate_request(task_id, "readiness_90", "Plan complete, refs verbatim...")
3. PO receives ntfy: "Gate: readiness_90 — Task: Add auth middleware"
4. PO reviews plan on OCMC/Plane
5. PO approves: sets readiness to 99 on OCMC
6. Orchestrator detects readiness >= 99: task eligible for dispatch
7. Task dispatched to agent for WORK stage
```

Without the gate, readiness stays below 99 and the task is never dispatched for work. The gate ensures PO confirms the approach before implementation begins.

## Who Uses It

| Role | Gate Type | When |
|------|-----------|------|
| PM | readiness_50 | Task has progressed through analysis/investigation — direction check |
| PM | readiness_90 | Plan is complete — final gate before work authorization |
| Any agent | readiness_90 | Plan confirmed, requesting PO sign-off |
| PM | phase_advance | Deliverable ready for next phase (poc→mvp, mvp→staging, etc.) |

## Relationships

- POSTS TO: board memory (gate + po-required tags — PO sees in OCMC)
- SETS ON TASK: gate_pending custom field (marks which gate is awaiting PO)
- NOTIFIES: PO via ntfy high priority (phone notification)
- NOTIFIES: IRC #fleet (would be #gates when channel exists)
- RECORDS: trail event (gate_requested)
- EMITS: fleet.gate.requested event
- CONNECTS TO: methodology.py (readiness gates at 50% and 90%)
- CONNECTS TO: orchestrator Step 3b (not built — would process gate decisions)
- CONNECTS TO: fleet_task_progress (readiness advances after PO approves gate)
- CONNECTS TO: notification routing (should route to #gates channel — not yet created)
- CONNECTS TO: PO daily workflow (§48 — gate requests are "Action Needed" level)
- BLOCKS: dispatch to work stage until PO sets readiness >= 99
- PO AUTHORITY: only PO can approve gates — agents cannot self-authorize
