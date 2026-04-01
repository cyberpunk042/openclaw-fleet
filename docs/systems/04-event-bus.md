# Event Bus — The Fleet's Nervous System

> **4 files. 1248 lines. 47 event types. Every operation produces events across 6 surfaces.**
>
> The event bus is the fleet's nervous system. Every action — task
> completion, alert, stage change, disease detection, sprint milestone
> — produces events that propagate across MC, GitHub, IRC, ntfy, Plane,
> and metrics. One tool call → multi-surface publishing. Tolerates partial
> failure (IRC down doesn't block task completion). Agent feeds are
> filtered projections of events with seen/unseen tracking.

---

## 1. Why It Exists

Without the event bus, each subsystem would need to know about every
other subsystem. Task completion would need to call MC API, then
GitHub API, then IRC, then ntfy, then Plane, then metrics — each
with its own error handling. Adding a new surface would require
modifying every operation.

The event bus inverts this:

```
BEFORE: Each tool knows every surface
  fleet_task_complete → MC API
  fleet_task_complete → GitHub API
  fleet_task_complete → IRC
  fleet_task_complete → ntfy
  fleet_task_complete → Plane
  fleet_task_complete → metrics

AFTER: Each tool produces a chain, runner handles surfaces
  fleet_task_complete → EventChain
      ↓
  ChainRunner executes:
      ├── INTERNAL → MC API
      ├── PUBLIC → GitHub API
      ├── CHANNEL → IRC
      ├── NOTIFY → ntfy
      ├── PLANE → Plane API
      └── META → metrics
```

Adding a new surface = modify the chain runner, not every tool.

### PO Requirement (Verbatim)

> "no matter from where I mention, that it be internal chat or Plane,
> or if I change something manually on the platform, you must detect
> and record the event and do the appropriate chain of operations"

---

## 2. How It Works

### 2.1 The Event Flow

```
Something happens (agent calls tool, orchestrator acts, watcher detects)
  ↓
Event created: create_event(type, source, subject, recipient, ...)
  ↓
Event stored: EventStore.append(event) → .fleet-events.jsonl
  ↓
Chain built: build_task_complete_chain() or build_alert_chain() etc.
  ↓
Chain executed: ChainRunner processes each event in chain
  ├── INTERNAL events → MC API (required — failure = chain failure)
  ├── PUBLIC events → GitHub API (required for code tasks)
  ├── CHANNEL events → IRC (optional — failure tolerated)
  ├── NOTIFY events → ntfy (optional — failure tolerated)
  ├── PLANE events → Plane API (optional — only if Plane configured)
  └── META events → metrics/quality (optional)
  ↓
Result: ChainResult(executed=N, failed=M, errors=[...])
  ↓
Agent feeds built: route_event() determines which agents get which events
  ↓
Agent heartbeat: context includes relevant events since last heartbeat
```

### 2.2 The 6 Event Surfaces

```
┌──────────────────────────────────────────────────────────┐
│                    EVENT SURFACES                          │
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ INTERNAL │  │  PUBLIC  │  │ CHANNEL  │               │
│  │          │  │          │  │          │               │
│  │ MC API:  │  │ GitHub:  │  │ IRC:     │               │
│  │ - tasks  │  │ - push   │  │ - #fleet │               │
│  │ - memory │  │ - PR     │  │ - #alerts│               │
│  │ - approve│  │ - commit │  │ - #review│               │
│  │          │  │          │  │          │               │
│  │ REQUIRED │  │ REQUIRED │  │ OPTIONAL │               │
│  └──────────┘  └──────────┘  └──────────┘               │
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │  NOTIFY  │  │  PLANE   │  │   META   │               │
│  │          │  │          │  │          │               │
│  │ ntfy:    │  │ Plane:   │  │ System:  │               │
│  │ - PO     │  │ - labels │  │ - metrics│               │
│  │   mobile │  │ - state  │  │ - quality│               │
│  │ - urgent │  │ - comment│  │ - checks │               │
│  │          │  │          │  │          │               │
│  │ OPTIONAL │  │ OPTIONAL │  │ OPTIONAL │               │
│  └──────────┘  └──────────┘  └──────────┘               │
│                                                           │
│  Required events: failure = chain failure                  │
│  Optional events: failure tolerated (logged, not blocking) │
└──────────────────────────────────────────────────────────┘
```

### 2.3 The 47 Event Types

Organized by domain:

```
Task lifecycle (9):
  fleet.task.created, accepted, progress, completed,
  approved, rejected, dispatched, blocked, unblocked

Plane lifecycle (6):
  fleet.plane.issue_created, issue_updated, issue_commented,
  cycle_started, cycle_completed, sync

GitHub lifecycle (6):
  fleet.github.pr_created, pr_merged, pr_commented,
  ci_passed, ci_failed, review_requested

Agent lifecycle (4):
  fleet.agent.online, offline, heartbeat, stuck

Communication (4):
  fleet.chat.message, mention
  fleet.alert.posted
  fleet.escalation

System (4):
  fleet.system.sync, health, config_changed, gateway_restart

Immune system (5):
  fleet.immune.disease_detected, agent_pruned,
  context_compacted, teaching_triggered, escalated_to_po

Teaching system (5):
  fleet.teaching.lesson_started, practice_attempted,
  comprehension_verified, comprehension_failed, escalated_to_prune

Methodology system (5):
  fleet.methodology.stage_changed, readiness_changed,
  check_passed, check_failed, protocol_violation
```

Naming convention: `fleet.{domain}.{action}`

### 2.4 Event Routing — 5 Levels

```
Level 1: DIRECT        event.recipient = "software-engineer" → only that agent
Level 2: PRIORITY      fleet.escalation → always fleet-ops (hard-coded)
Level 3: MENTIONS      event.mentions = ["architect"] → mentioned agents
Level 4: TAG MATCH     event.tags ∩ agent.subscriptions → matching agents
Level 5: BROADCAST     event.recipient = "all" → everyone
```

Tag subscriptions per agent (event_router.py:30-71):
- fleet-ops subscribes to: review, alert, escalation, quality, security, governance
- project-manager subscribes to: plan, sprint, velocity, backlog, plane, unassigned
- architect subscribes to: architecture, design, system, pattern, complexity
- software-engineer subscribes to: implement, code, feature, fix, refactor
- qa-engineer subscribes to: test, qa, quality, coverage, regression
- devops subscribes to: docker, ci, cd, pipeline, deploy, infrastructure
- devsecops-expert subscribes to: security, cve, vulnerability, audit
- technical-writer subscribes to: documentation, readme, changelog, docs
- ux-designer subscribes to: ui, ux, interface, accessibility
- accountability-generator subscribes to: accountability, transparency, evidence

### 2.5 Chain Builders — 8 Predefined Chains

| Builder | Lines | Surfaces Used | Purpose |
|---------|-------|--------------|---------|
| `build_task_complete_chain` | 107-177 | ALL 6 | Task done → status, approval, memory, push, PR, IRC, ntfy, Plane, metrics |
| `build_alert_chain` | 180-207 | INTERNAL + CHANNEL + NOTIFY | Alert → memory, IRC (#alerts or #fleet), ntfy |
| `build_contribution_chain` | 227-265 | INTERNAL + CHANNEL + PLANE | Contribution → trail, IRC #contributions, Plane comment |
| `build_gate_request_chain` | 268-313 | INTERNAL + CHANNEL + NOTIFY | PO gate → memory (po-required), IRC #gates, ntfy important |
| `build_rejection_chain` | 316-361 | INTERNAL + CHANNEL | Rejection → memory (mention rejected agent), IRC #reviews, trail |
| `build_phase_advance_chain` | 364-411 | INTERNAL + CHANNEL + NOTIFY | Phase advance → memory (milestone), IRC #fleet + #sprint, ntfy |
| `build_transfer_chain` | 414-449 | INTERNAL + CHANNEL | Transfer → memory (mention receiving agent), IRC #fleet, trail |
| `build_sprint_complete_chain` | 452-475 | INTERNAL + CHANNEL + NOTIFY | Sprint done → memory, IRC #fleet, ntfy |

Every chain includes a `_trail_event()` for accountability trail reconstruction.

---

## 3. File Map

```
fleet/core/
├── events.py         CloudEvents schema, EventStore, agent feeds   (332 lines)
├── event_chain.py    Chain builders, 6 surfaces, 8 predefined chains (475 lines)
├── event_router.py   5-level routing, tag subscriptions, feed builder (218 lines)
└── event_display.py  Per-surface rendering (IRC, Plane, ntfy, etc.)  (223 lines)
```

Total: **1248 lines** across 4 modules.

---

## 4. Per-File Documentation

### 4.1 `events.py` — CloudEvents Store (332 lines)

#### Constants

| Name | Type | Size |
|------|------|------|
| `EVENT_TYPES` | dict[str, str] | 47 event types with descriptions |

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `FleetEvent` | 113-167 | CloudEvents-format event with fleet extensions. Properties: recipient, priority, mentions, tags, surfaces, actions, refs. Auto-generates UUID and timestamp. |
| `EventStore` | 204-333 | Persistent JSONL store (.fleet-events.jsonl). Methods: append, query (with agent/subject/type/time/unseen filters), mark_seen, count_unseen. Per-agent seen tracking in .fleet-events.seen.json. |

#### Functions

| Function | Lines | What It Does |
|----------|-------|-------------|
| `create_event(type, source, subject, recipient, priority, mentions, tags, surfaces, actions, refs, **extra)` | 169-198 | Factory function. Creates FleetEvent with standard fields + extra data. |

#### EventStore.query() — Filter Parameters

| Param | Type | Effect |
|-------|------|--------|
| `agent_name` | str | Filter to events relevant to this agent (direct, mention, PM/lead roles) |
| `subject` | str | Filter to events about this task/agent/issue |
| `event_types` | list | Filter to specific event types |
| `since` | str | Filter to events after this ISO timestamp |
| `unseen_only` | bool | Filter to events agent hasn't seen |
| `limit` | int | Max events returned (default 50) |

Agent relevance logic (query, lines 288-301):
- recipient = "all" → relevant to everyone
- recipient = agent_name → relevant to that agent
- agent_name in mentions → relevant
- PM gets "pm" and "unassigned" recipients
- fleet-ops gets "lead" and "ops" recipients

### 4.2 `event_chain.py` — Multi-Surface Chains (475 lines)

#### Enums

| Name | Values |
|------|--------|
| `EventSurface` | INTERNAL, PUBLIC, CHANNEL, NOTIFY, PLANE, META |

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `Event` | 33-43 | Single chain event: surface, action, params, required bool, result, error, executed |
| `EventChain` | 47-86 | Operation's event list. Method: `add(surface, action, params, required)`. Properties per surface type. |
| `ChainResult` | 88-103 | Execution result: total, executed, failed, errors. Property: `ok` (True if no required failures). |

#### Chain Builders (8 functions, lines 105-475)

See table in Section 2.5 above. Each builder creates an EventChain with events across relevant surfaces. Every chain includes trail events for accountability.

#### Helper

| Function | Lines | What It Does |
|----------|-------|-------------|
| `_trail_event(task_id, type, content, agent)` | 210-224 | Creates INTERNAL board memory event tagged with "trail" + task + type. Required=False — trail must never break chains. |

### 4.3 `event_router.py` — 5-Level Routing (218 lines)

#### Constants

| Name | Type | Purpose |
|------|------|---------|
| `AGENT_TAG_SUBSCRIPTIONS` | dict[str, list[str]] | What tags each of 10 agents subscribes to |
| `PRIORITY_ROUTES` | dict[str, dict] | Event types that always route to specific agents |

#### Functions

| Function | Lines | What It Does |
|----------|-------|-------------|
| `route_event(event, all_agents)` | 120-181 | 5-level routing: direct → priority → mentions → tags → broadcast. Returns RoutingResult with recipients and reason. |
| `build_agent_feed(events, agent_name, limit)` | 184-219 | Filters events to agent-relevant ones. Sorts by priority then time. Returns formatted feed for heartbeat context. |

#### Priority Routes (always-routed event types)

| Event Type | Always Goes To | Priority |
|-----------|---------------|----------|
| `fleet.escalation` | fleet-ops | urgent |
| `fleet.task.blocked` | project-manager | important |
| `fleet.alert.posted` | fleet-ops | important |
| `fleet.plane.issue_created` | project-manager | info |
| `fleet.plane.cycle_started` | project-manager, fleet-ops | important |
| `fleet.github.ci_failed` | assigned agent | urgent |
| `fleet.agent.offline` | fleet-ops | important |
| `fleet.agent.stuck` | fleet-ops, project-manager | urgent |

### 4.4 `event_display.py` — Per-Surface Rendering (223 lines)

#### Functions

| Function | Lines | What It Does |
|----------|-------|-------------|
| `render_irc(event)` | 21-100+ | Renders event as compact one-line IRC message with emoji. 30+ templates for different event types. |
| `render_plane(event)` | — | Renders as rich HTML for Plane comments |
| `render_ntfy(event)` | — | Renders as title + body for ntfy push |
| `render_heartbeat(event)` | — | Renders as structured data for agent context |
| `render_memory(event)` | — | Renders as tagged, searchable board memory entry |

IRC rendering examples:
```
[agent] ✅ Task completed: Add fleet controls...
[fleet-ops] ❌ Rejected: Missing acceptance criteria...
[doctor] 🔬 protocol_violation detected on software-engineer...
[teaching] ✅ software-engineer comprehension verified
[methodology] 📊 abc123 stage: analysis → reasoning
```

---

## 5. Dependency Graph

```
events.py           ← standalone (uuid, json, datetime)
    ↑
event_chain.py      ← standalone (uses EventSurface enum only)
    ↑
event_router.py     ← imports FleetEvent from events, AGENT_CAPABILITIES from routing
    ↑
event_display.py    ← imports FleetEvent from events
```

No circular dependencies. events.py and event_chain.py can be used independently.

---

## 6. Consumers (15 non-test modules)

| Layer | Module | What It Imports | How It Uses It |
|-------|--------|----------------|---------------|
| **Chain Runner** | `chain_runner.py` | ChainResult, Event, EventChain, EventSurface, EventStore, create_event | Executes chains, persists events |
| **Orchestrator** | `orchestrator.py` | create_event, EventStore | Emits mode changes, dispatch events |
| **Sync** | `sync.py` | create_event, EventStore | Emits sync events |
| **MCP Tools** | `tools.py` | build_task_complete_chain, build_agent_feed, create_event, EventStore | Tools build chains, query feeds |
| **Context Assembly** | `context_assembly.py` | build_agent_feed | Builds agent event feed for heartbeat context |
| **Methodology** | `methodology.py` | create_event, EventStore | Emits stage_changed events |
| **Teaching** | `teaching.py` | create_event, EventStore | Emits teaching events |
| **Cross-Refs** | `cross_refs.py` | FleetEvent | Cross-reference automation |
| **Config Watcher** | `config_watcher.py` | EventStore, create_event | Emits config change events |
| **OCMC Watcher** | `ocmc_watcher.py` | EventStore, create_event | Emits OCMC change events |
| **Plane Watcher** | `plane_watcher.py` | EventStore, create_event | Emits Plane change events |
| **Event Display** | `event_display.py` | FleetEvent | Renders events per surface |
| **Event Router** | `event_router.py` | FleetEvent | Routes events to agents |

---

## 7. Design Decisions

### Why CloudEvents, not custom schema?

CloudEvents is a CNCF standard. It provides: specversion, type, source,
id, time — all standardized. Fleet extensions (recipient, priority,
mentions, tags) are stored in the `data` payload for compatibility.
Any CloudEvents-compatible tool can process fleet events.

### Why JSONL storage, not a database?

JSONL is append-only, requires no server, survives crashes (partial
writes are just truncated lines), and is grep-friendly. For a fleet
of 10 agents producing ~100 events/hour, JSONL scales fine. A database
would add complexity (schema, migrations, connections) without benefit.

### Why required vs optional events in chains?

Not all surfaces are equally important. If IRC is down, the task should
still complete. But if MC API fails to update the task status, that's
a real failure. Required events fail the chain. Optional events log
errors but don't block.

### Why per-agent seen tracking?

Without seen tracking, agents would re-process events on every heartbeat.
With seen tracking, agents only see new events. The seen set is persisted
in `.fleet-events.seen.json` and survives restarts.

### Why tag-based routing, not role-based only?

Tags are more flexible than roles. An architect cares about "architecture"
events regardless of who sent them. A QA engineer cares about "test"
events even from other agents. Tag subscriptions let events find the
right audience without the sender needing to know who that audience is.

### Why trail events in every chain?

The accountability generator needs to reconstruct complete task history.
Trail events tagged with `trail` + `task:{id}` enable querying all
events for any task. Every chain records what happened, who did it,
and when — even if the primary action was on a different surface.

---

## 8. Storage

### Event Store Location

```
.fleet-events.jsonl      — append-only event log (one JSON object per line)
.fleet-events.seen.json  — per-agent seen event IDs
```

Both files are gitignored (runtime state, not IaC).

### Event Record Format

```json
{
  "specversion": "1.0",
  "id": "uuid-here",
  "type": "fleet.task.completed",
  "source": "fleet/mcp/tools/fleet_task_complete",
  "subject": "task-uuid-here",
  "time": "2026-03-31T15:42:00Z",
  "data": {
    "recipient": "all",
    "priority": "info",
    "mentions": [],
    "tags": ["completed", "project:fleet"],
    "surfaces": ["internal", "public", "channel"],
    "agent": "software-engineer",
    "summary": "Added fleet controls to header bar"
  }
}
```

### Seen Tracking Format

```json
{
  "fleet-ops": ["uuid-1", "uuid-2", "uuid-3"],
  "project-manager": ["uuid-1", "uuid-4"],
  "software-engineer": ["uuid-2"]
}
```

---

## 9. Data Shapes

### EventChain (task completion)

```python
EventChain(
    operation="task_complete",
    source_agent="software-engineer",
    task_id="abc123",
    events=[
        Event(surface=INTERNAL, action="update_task_status", required=True),
        Event(surface=INTERNAL, action="create_approval", required=True),
        Event(surface=INTERNAL, action="post_board_memory", required=False),
        Event(surface=PUBLIC, action="push_branch", required=True),
        Event(surface=PUBLIC, action="create_pr", required=True),
        Event(surface=CHANNEL, action="notify_irc", required=False),
        Event(surface=NOTIFY, action="ntfy_publish", required=False),
        Event(surface=PLANE, action="update_issue_state", required=False),
        Event(surface=META, action="update_metrics", required=False),
    ]
)
```

### RoutingResult

```python
RoutingResult(
    event_id="uuid-here",
    event_type="fleet.alert.posted",
    recipients=["devsecops-expert", "fleet-ops"],
    reason="tag_match:security"
)
```

### Agent Feed Entry

```python
{
    "id": "uuid-here",
    "type": "fleet.task.completed",
    "time": "2026-03-31T15:42:00Z",
    "priority": "info",
    "data": {"agent": "software-engineer", "summary": "..."},
    "routing_reason": "tag_match:implement,code"
}
```

---

## 10. What's Needed

### Remaining Milestones

| ID | What | Status |
|----|------|--------|
| M-EB02 | CloudEvents SDK integration | Design only |
| M-EB03 | Agent feed design doc | Design only |
| M-EB04 | Sync map documentation | Design only |
| M-EB05 | Mention routing design | Design only |

### Functional Gaps

- **Chain runner execution** — `chain_runner.py` exists but not all
  surface handlers are complete (Plane surface handlers partial)
- **Bidirectional Plane events** — Plane changes detected but not
  all change types emit events
- **Mention routing in heartbeat** — events with `mention:{agent}`
  are stored but not reliably surfaced in heartbeat pre-embed
- **Event cleanup** — JSONL grows without bound. No rotation or
  archival strategy implemented.

### Test Coverage

| File | Tests | Coverage |
|------|-------|---------|
| `test_events.py` | 20+ | Event creation, store, query, routing |
| `test_event_chain.py` | 15+ | Chain building, surface filtering |
| `test_event_router.py` | 15+ | 5-level routing, tag matching |
| `test_event_display.py` | 10+ | IRC rendering |
| **Total** | **60+** | Core logic covered. Missing: chain execution, Plane integration |
