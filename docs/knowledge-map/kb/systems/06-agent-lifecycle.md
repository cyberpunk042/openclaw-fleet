# System 06: Agent Lifecycle & Roles — States, Authority, Cost Control

**Type:** Fleet System
**ID:** S06
**Files:** agent_lifecycle.py (290+ lines), agent_roles.py (130+ lines), memory_structure.py, heartbeat_gate.py
**Total:** 423+ lines
**Tests:** 35+

## What This System Does

Two responsibilities: (1) manage agent states for cost control (ACTIVE→IDLE→SLEEPING→OFFLINE with brain-evaluated silent heartbeats), (2) define PR authority per role (who can reject, close, set security_hold). States are VISIBILITY LABELS — all agents respond to wake triggers identically. The brain is the FILTER between gateway cron and Claude calls.

PO requirement: "the agent need to be able to do silent heartbeat when they deem after a while that there is nothing new from the heartbeat, then it relay the work to the brain to actually do a compare and determine if it require a real heartbeat."

PO analogy: "Like any good employee on call who know he can relax a bit reduce cost and let the automated systems take the relay while there is nothing particular to work on anyway."

## Lifecycle States

```
ACTIVE    → has work, full Claude sessions
  ↓ 1 HEARTBEAT_OK (or no task for 10 min)
IDLE      → no work, brain takes over evaluation after 1 OK
  ↓ 3 consecutive HEARTBEAT_OK
SLEEPING  → brain evaluates deterministically (FREE, $0)
  ↓ 4 hours sleeping
OFFLINE   → extended absence, slow wake
```

**Wake triggers** reset ANY state to ACTIVE:
- Task assigned
- @mention
- Contribution task
- PO directive
- Role-specific trigger (PM: unassigned_inbox, fleet-ops: pending_approval, devsecops: security_alert)

## The Silent Heartbeat Architecture

Gateway cron NEVER stops. The brain INTERCEPTS before the Claude call:

```
Gateway cron fires for agent (every configured interval)
├── Brain intercepts BEFORE Claude call
├── Read agent lifecycle state
├── If ACTIVE: proceed → real Claude heartbeat ($$$)
├── If IDLE (1+ HEARTBEAT_OK): brain evaluates ($0):
│   ├── Direct mention? → WAKE
│   ├── Task assigned? → WAKE
│   ├── Contribution task? → WAKE
│   ├── PO directive? → WAKE
│   ├── Role-specific trigger? → WAKE
│   └── Nothing? → SILENT OK ($0)
└── Agent is ALWAYS on call. Brain is the filter.
```

**10 agents, 7 sleeping = ~70% cost reduction on idle fleet.**

## CRITICAL GAP

The brain interception layer does NOT exist yet. Currently:
- Gateway cron fires → Claude call happens immediately (no lifecycle check)
- SLEEPING agents still get expensive Claude calls
- heartbeat_gate.py module exists (built this session) but NOT wired into orchestrator
- Data structures exist: `consecutive_heartbeat_ok`, `last_heartbeat_data_hash` in AgentState

## PR Authority Matrix

| Role | Can Reject | Can Close | Security Hold | Final Authority |
|------|-----------|----------|--------------|----------------|
| Fleet-ops | Yes | Yes | No | YES (final) |
| DevSecOps | Yes | Yes | YES (only role) | No |
| Architect | Yes (design) | No | No | No |
| QA | Yes (quality) | No | No | No |
| PM | No | No | No | No |
| Workers | No | No | No | No |

Rejection by architect/QA/devsecops auto-creates fix task assigned to the original agent.

## Agent Memory Structure

Per-agent persistent memory in `.claude/memory/`:
- MEMORY.md — index (auto-managed)
- codebase_knowledge.md — patterns, architecture learned
- project_decisions.md — decisions with rationale
- task_history.md — completed work and lessons
- team_context.md — shared knowledge from board memory

Updated by claude-mem plugin. Read at session start for context recovery.

## Relationships

- CONSUMED BY: orchestrator.py (lifecycle state affects dispatch decisions)
- CONSUMED BY: heartbeat_gate.py (brain evaluates sleeping agents — built, not wired)
- CONSUMED BY: fleet_approve tool (PR authority checked via can_agent_reject, should_create_fix_task)
- CONSUMED BY: preembed.py (agent status in fleet-context.md)
- CONNECTS TO: S02 immune system (AgentHealth profiles + prune/regrow cycle)
- CONNECTS TO: S05 control surface (budget_mode affects heartbeat frequency)
- CONNECTS TO: S07 orchestrator (Step 4 wake drivers, Step 8 health check)
- CONNECTS TO: S12 budget (silent heartbeats = ~70% cost savings)
- CONNECTS TO: S13 labor (heartbeat_stamp.py tracks idle cost)
- CONNECTS TO: S22 agent intelligence (autonomy tuning per role)
- CONNECTS TO: gateway_client.py (CRON management — enable/disable/update)
- CONNECTS TO: claude-mem plugin (cross-session memory persists across state changes)
- CONNECTS TO: .claude/memory/ (file-based memory survives prune/compact)
- NOT YET IMPLEMENTED: brain interception (heartbeat_gate.py not in orchestrator), per-agent cron enable/disable (only all-or-nothing), per-agent interval adaptation, role-specific wake triggers (only PM and fleet-ops partially coded)

## For LightRAG Entity Extraction

Key entities: AgentStatus (ACTIVE/IDLE/SLEEPING/OFFLINE), AgentState (consecutive_heartbeat_ok, last_heartbeat_data_hash), FleetLifecycle, PRAuthority, AgentRole (10 defined), HeartbeatGate, WakeDecision (WAKE/SILENT/STRATEGIC).

Key relationships: Gateway cron FIRES heartbeat. Brain INTERCEPTS before Claude call. Brain EVALUATES sleeping agents ($0). Wake trigger RESETS to ACTIVE. Fleet-ops IS final authority. DevSecOps SETS security_hold. Rejection CREATES fix task. AgentHealth PERSISTS across cycles.
