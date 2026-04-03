# System 04: Event Bus — The Fleet's Nervous System

**Type:** Fleet System
**ID:** S04
**Files:** events.py, event_chain.py, event_router.py, event_display.py
**Total:** 1,248 lines
**Tests:** 60+

## What This System Does

Every fleet operation produces CloudEvents that propagate across 6 surfaces. One tool call → multi-surface publishing. The event bus inverts dependencies: instead of each tool knowing every surface (MC, GitHub, IRC, ntfy, Plane, metrics), tools produce event CHAINS and the chain runner handles surfaces. Adding a new surface = modify the runner, not every tool. Tolerates partial failure — IRC down doesn't block task completion.

PO requirement: "no matter from where I mention, that it be internal chat or Plane, or if I change something manually on the platform, you must detect and record the event and do the appropriate chain of operations"

## 6 Event Surfaces

| Surface | Target | Required? | Failure Behavior |
|---------|--------|-----------|------------------|
| INTERNAL | MC API (tasks, comments, memory, approvals) | YES | Chain fails |
| PUBLIC | GitHub (push, PR, review) | YES for code | Chain fails |
| CHANNEL | IRC (#fleet, #alerts, #reviews) | NO | Tolerated — logged |
| NOTIFY | ntfy (mobile push to PO) | NO | Tolerated |
| PLANE | Plane API (issue state, comments) | NO | Only if Plane configured |
| META | Metrics, quality tracking | NO | Tolerated |

Required surfaces failing = chain failure. Optional surfaces failing = logged but operation succeeds.

## 47 Event Types (9 domains)

Fleet naming: `fleet.{domain}.{action}`

| Domain | Types | Examples |
|--------|-------|---------|
| task | 9 | created, assigned, dispatched, stage_changed, readiness_changed, completed, transferred, done, regressed |
| plane | 6 | issue_created, issue_updated, issue_commented, cycle_started, cycle_completed, sync_completed |
| github | 6 | pr_created, pr_merged, pr_reviewed, branch_pushed, commit_created, pr_closed |
| agent | 4 | status_changed, heartbeat, wake, sleep |
| communication | 4 | chat_message, mention, directive_received, escalation |
| system | 4 | mode_changed, tempo_changed, cycle_completed, error |
| immune | 5 | disease_detected, lesson_injected, comprehension_verified, agent_pruned, security_hold |
| teaching | 5 | lesson_created, exercise_submitted, comprehension_evaluated, lesson_completed, lesson_failed |
| methodology | 5 | stage_changed, readiness_changed, checkpoint_reached, gate_requested, plan_accepted |

## 8 Event Chain Builders

One tool call → chain fires across surfaces:

| Builder | Surfaces Hit | Triggered By |
|---------|-------------|-------------|
| build_task_complete_chain | ALL 6 | fleet_task_complete |
| build_alert_chain | INTERNAL + CHANNEL + NOTIFY | fleet_alert |
| build_contribution_chain | INTERNAL + CHANNEL + PLANE | fleet_contribute |
| build_gate_request_chain | INTERNAL + CHANNEL + NOTIFY | fleet_gate_request |
| build_rejection_chain | INTERNAL + CHANNEL + PLANE | fleet_approve (rejected) |
| build_phase_advance_chain | INTERNAL + CHANNEL + NOTIFY | phase advancement |
| build_transfer_chain | INTERNAL + CHANNEL + PLANE | fleet_transfer |
| build_sprint_complete_chain | INTERNAL + CHANNEL + NOTIFY + PLANE | sprint completion |

## 5-Level Event Routing

Events reach the right agents through tiered routing:

```
1. DIRECT    → explicit recipient in event
2. PRIORITY  → hardcoded (e.g., escalation always to fleet-ops)
3. MENTIONS  → agents mentioned in event content
4. TAG MATCH → agent tag subscriptions by domain interest
5. BROADCAST → all agents (fallback)
```

Each of 10 agents has tag subscriptions matching their expertise.

## Storage

- JSONL append-only: `.fleet-events.jsonl`
- Per-agent seen tracking: `.fleet-events.seen.json`
- EventStore supports query with: agent, subject, type, time, unseen filters
- No database needed

## Agent Feeds

`build_agent_feed()` filters events to agent-relevant ones, sorted by priority then time. Included in heartbeat context (fleet-context.md Layer 6, EVENTS section).

## Relationships

- CONSUMED BY: orchestrator.py (emits events, processes chains)
- CONSUMED BY: every MCP tool (emit events on actions)
- CONSUMED BY: preembed.py (agent feeds in heartbeat context)
- CONNECTS TO: S01 methodology (stage_changed, readiness_changed events)
- CONNECTS TO: S02 immune system (disease_detected, agent_pruned events)
- CONNECTS TO: S03 teaching (lesson_injected, comprehension events)
- CONNECTS TO: S07 orchestrator (emits system events, processes chains)
- CONNECTS TO: S08 MCP tools (tools fire event chains)
- CONNECTS TO: S11 storm (storm events: severity_changed)
- CONNECTS TO: S17 Plane (PLANE surface handler syncs events to Plane)
- CONNECTS TO: S18 notifications (events routed to IRC/ntfy)
- CONNECTS TO: PostToolUse hook (automatic trail event after every tool call)
- CONNECTS TO: chain_registry.py (future Layer 2 — event-driven handlers)
- NOT YET IMPLEMENTED: event cleanup/rotation, full Plane surface handlers, mention routing reliability, chain_registry event-driven pattern

## For LightRAG Entity Extraction

Key entities: FleetEvent (CloudEvent format), EventStore (JSONL), EventChain, ChainRunner, ChainResult, EventSurface (6 types), EventRouter, agent tag subscriptions.

Key relationships: Tool FIRES chain. ChainRunner EXECUTES across surfaces. EventRouter MATCHES events to agents. EventStore PERSISTS events. Agent feeds FILTER events per agent. Events PROPAGATE from source to 6 surfaces.
