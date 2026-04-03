# System 07: Orchestrator — The Autonomous Brain

**Type:** Fleet System (CENTRAL — touches every other system)
**ID:** S07
**Files:** orchestrator.py (1378 lines), context_assembly.py (331), preembed.py (170), context_writer.py (86), role_providers.py (181), change_detector.py (123), smart_chains.py (171), driver.py (155)
**Total:** 2,595 lines across 8 modules
**Tests:** 75+

## What This System Does

The fleet's central brain. The ONLY component that sees full fleet state and makes coordination decisions. Runs every 30 seconds (scales with budget_mode: 5s turbo → 60s economic) as a deterministic Python daemon. Executes 9 steps per cycle: refresh contexts, security scan, immune system, review approvals, wake drivers, dispatch tasks, process directives, evaluate parents, health check.

**Key principle:** The orchestrator NEVER creates Claude Code sessions directly. It writes context files to disk → gateway reads them at agent heartbeat → files injected into system prompt. Orchestrator controls WHAT agents see, gateway controls WHEN they see it.

## Pre-Checks (Any Can Abort the Cycle)

| Check | Source | Behavior |
|-------|--------|----------|
| Storm Monitor | storm_monitor.py | CRITICAL → halt. STORM → 0 dispatch. WARNING → max 1. |
| Gateway Duplication | gateway_guard.py | Duplicate → storm indicator (March catastrophe root cause) |
| Fleet Mode | fleet_mode.py | work-paused → skip dispatch |
| Budget Monitor | budget_monitor.py | ≥90% weekly or ≥95% session → pause dispatch |

## 9 Steps (Executed in Order)

### Step 0: Context Refresh — MOST IMPORTANT
Write `context/fleet-context.md` + `context/task-context.md` for ALL agents every cycle. Data is FULL, not compressed. Each agent gets:
- Assigned tasks (full detail via format_task_full)
- Messages (@mentions from board memory)
- PO directives (parsed from board memory)
- Role-specific data via 5 providers:
  - fleet_ops_provider: pending_approvals, review_queue, offline_agents
  - pm_provider: unassigned_tasks, blocked_tasks, sprint_progress
  - architect_provider: tasks_needing_design_review
  - devsecops_provider: security_tasks, PRs_needing_review
  - worker_provider: task_count, in_review_count
- Fleet state (work_mode, cycle_phase, backend_mode, budget_mode)
- Events since last heartbeat

### Step 1: Security Scan
behavioral_security.py scans new/changed tasks. Critical → security_hold + ntfy PO.

### Step 2: Doctor (Immune System)
doctor.py runs detection cycle (4 of 11 detections). Returns DoctorReport → skip flagged agents, block flagged tasks. Inject teaching lessons via gateway.

### Step 3: Ensure Review Approvals
Create approval objects for tasks in REVIEW status so fleet-ops can process them.

### Step 4: Wake Drivers
PM wakes if unassigned inbox tasks exist (120s cooldown). Fleet-ops wakes if tasks in review (120s cooldown). Waking = inject_content() via gateway WebSocket RPC.

### Step 5: Dispatch Ready Tasks
Find unblocked inbox tasks with assigned agents. 10 gate checks:
1. work_mode allows dispatch?
2. Storm severity allows?
3. Budget quota safe?
4. Task readiness ≥ 99?
5. Task has assigned agent?
6. Task not blocked by dependencies?
7. Agent not already busy (max 1 concurrent)?
8. Agent not flagged by doctor?
9. Agent active in current phase?
10. Max dispatch per cycle not exceeded?

ALL gates pass → dispatch. Task scoring (priority + dependency depth + wait time + type) determines order. Route via backend_router. Save DispatchRecord. Inject task pre-embed. Notify IRC.

### Step 6: Process Directives
Parse PO directives from board memory. Route to target agent's heartbeat context.

### Step 7: Evaluate Parents
When ALL children of a parent task are DONE → parent moves to REVIEW. Recursive check (grandparent too).

### Step 8: Health Check
Detect stuck tasks (in_progress >8h), offline agents with work, stale dependencies. Self-healing creates remediation tasks or escalates.

## Daemon Loop

```python
while True:
    # Budget-mode-aware sleep
    effective_interval = base_interval * tempo_multiplier
    # turbo=5s, aggressive=15s, standard=30s, economic=60s
    
    state = await run_orchestrator_cycle(mc, irc, board_id, config)
    
    # MC down → disable all gateway CRONs (zero consumption)
    # MC up → re-enable CRONs, provision agents, resume
    
    await asyncio.sleep(effective_interval)
```

## Persistent State Across Cycles

Fleet lifecycle, health profiles, storm monitor, budget monitor, change detector, wake cooldown timestamps, previous fleet_state (for change detection).

## Relationships

- READS FROM: mc_client.py (tasks, agents, memory, approvals, board)
- WRITES TO: agents/{name}/context/*.md (file-based context delivery)
- CONTROLS: gateway_client.py (inject, prune, compact, enable/disable CRONs)
- USES: ALL systems (S01-S22) — the brain coordinates everything
- CONNECTS TO: S01 methodology (stage checks, readiness gates)
- CONNECTS TO: S02 immune system (Step 2 — doctor report)
- CONNECTS TO: S03 teaching (inject lessons from doctor interventions)
- CONNECTS TO: S04 event bus (emit mode_changed, dispatch, transition events)
- CONNECTS TO: S05 control surface (read fleet_config every cycle)
- CONNECTS TO: S06 agent lifecycle (lifecycle state affects dispatch)
- CONNECTS TO: S08 MCP tools (dispatch triggers tool sessions)
- CONNECTS TO: S11 storm (pre-check every cycle)
- CONNECTS TO: S12 budget (pre-check, dispatch gate)
- CONNECTS TO: S13 labor (dispatch records intent for LaborStamp)
- CONNECTS TO: S14 router (route_task for backend selection)
- CONNECTS TO: S17 Plane (sync daemon, plane_sync)
- CONNECTS TO: S19 session (context assembly, pre-embed, context writer)
- NOT YET IMPLEMENTED: brain-evaluated heartbeats (heartbeat_gate.py not wired), contribution subtask creation at reasoning stage, full role-specific pre-embed (AR-01), strategic Claude call config (model/effort/session per situation), brain Steps 1b/3b/4b/9/10/11/12 (from 13-step design target)

## For LightRAG Entity Extraction

Key entities: Orchestrator (9-step cycle), OrchestratorState (counters: tasks_dispatched, approvals_processed, etc.), FleetControlState, DoctorReport, ChangeSet, DispatchRecord, role_provider (5 types).

Key relationships: Orchestrator READS fleet state. Orchestrator WRITES context files. Orchestrator DISPATCHES tasks. Orchestrator WAKES drivers. Storm GATES the cycle. Budget GATES dispatch. Doctor SKIPS flagged agents. Fleet mode FILTERS active agents. Parent evaluation PROMOTES completed parents.

The orchestrator is the HUB — it connects to every other system. Any change to any system eventually flows through the orchestrator cycle.
