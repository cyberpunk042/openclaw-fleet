# Notifications — Multi-Channel Routing & Cross-References

> **3 files. 536 lines. Routes fleet events to the right channel at the
> right priority. Cross-references automatically link related items
> across ALL surfaces so nothing exists in isolation.**
>
> Notifications are NOT just alerts. They're the visibility layer that
> ensures: when an agent completes a task with a PR, the Plane issue
> gets the PR link, IRC shows the review request, ntfy pings the PO
> if it's important, and board memory records the completion — all
> automatically. Without this, surfaces are disconnected islands.

---

## 1. Why It Exists

The fleet operates across 6 surfaces: MC (internal), GitHub (public),
IRC (channel), ntfy (push), Plane (project), and system metrics.
Without notification routing, these surfaces are disconnected:

- Agent completes task on OCMC → PO checks Plane → sees nothing
- PR merged on GitHub → OCMC task still shows "in review"
- Security alert posted → PO doesn't know until they check IRC
- Sprint starts in Plane → agents don't know unless PM tells them

Notification routing + cross-references make every surface aware of
what happened on every other surface. The PO never needs to check
multiple places — everything propagates automatically.

### PO Requirement (Verbatim)

> "always cross reference, like when updating a task on Plane you can
> say it in the internal chat naturally"

---

## 2. How It Works

### 2.1 Notification Classification & Routing

```
Fleet event arrives (from event bus)
  ↓
NotificationRouter classifies:
  ├── INFO events → ntfy "progress" topic
  │   (quiet — in notification history, no alert sound)
  │   task_done, pr_merged, sprint_milestone, sprint_complete
  │
  ├── IMPORTANT events → ntfy "review" topic
  │   (prominent — badge + sound on PO's phone)
  │   review_needed, escalation, sprint_milestone
  │
  └── URGENT events → ntfy "alert" topic + Windows toast
      (immediate — full-screen notification + sound)
      security_alert, agent_stuck, blocker, agent_offline
  ↓
Deduplication check:
  Same event_type + same source_agent within 300s cooldown?
  → suppress (prevents heartbeat spam)
  ↓
Route to ntfy with:
  title, message, priority, click_url, tags (admonition emoji)
```

### 2.2 Cross-Reference Generation

When an event happens on ONE surface, cross-references propagate
to OTHER surfaces automatically:

```
┌─────────────────────────────────────────────────────────────┐
│              CROSS-REFERENCE MATRIX                          │
│                                                              │
│  EVENT                    │ GENERATES REFS ON                │
│  ─────────────────────────┼──────────────────────────────── │
│  fleet.task.completed     │ Plane (PR link comment)          │
│  (with PR)                │ IRC #reviews (review request)    │
│                           │ Board memory (completion record) │
│                                                              │
│  fleet.plane.issue_created│ Board memory (new issue note)    │
│                           │ IRC #fleet (announcement)        │
│                                                              │
│  fleet.github.pr_merged   │ Plane (PR merged comment)        │
│  (by human)               │ IRC #fleet (human merged notice) │
│                                                              │
│  fleet.chat.mention       │ IRC #fleet (cross-post @mention) │
│  fleet.plane.commented    │ IRC #fleet (cross-post @mention) │
│                                                              │
│  fleet.plane.cycle_started│ IRC #sprint (announcement)       │
│                           │ Board memory (sprint record)     │
│                                                              │
│  fleet.plane.cycle_done   │ IRC #fleet (celebration)         │
│                           │ Board memory (velocity note)     │
│                                                              │
│  fleet.alert.posted       │ IRC #alerts (critical/high)      │
│  (critical/high)          │                                  │
│                                                              │
│  fleet.task.blocked       │ IRC #fleet (blocker notice)      │
│                                                              │
│  fleet.escalation         │ IRC #alerts (escalation)         │
│                           │ Board memory (human attention)   │
└─────────────────────────────────────────────────────────────┘
```

Each cross-reference is a `CrossReference` dataclass:
```python
CrossReference(
    target_surface="plane",    # where to post
    action="comment",          # what to do (comment, link, memory, notify)
    content="OCMC task completed by architect. PR: https://...",
    target_id="",              # issue ID, channel name (filled by caller)
    source_event_id="uuid",    # traceability back to original event
)
```

`generate_cross_refs(event)` is pure logic — it reads an event and
returns a list of references. The CALLER executes them via the
appropriate clients (Plane client, IRC client, MC client).

### 2.3 URL Resolution

All URLs are config-driven via `config/url-templates.yaml`:

```yaml
github:
  pr: "https://github.com/{owner}/{repo}/pull/{pr_number}"
  compare: "https://github.com/{owner}/{repo}/compare/main...{branch}"
  tree: "https://github.com/{owner}/{repo}/tree/{branch}"
  file: "https://github.com/{owner}/{repo}/blob/{branch}/{path}"
  commit: "https://github.com/{owner}/{repo}/commit/{sha}"

mc:
  task: "http://localhost:8000/boards/{board_id}/tasks/{task_id}"
  board: "http://localhost:8000/boards/{board_id}"
```

`UrlResolver.resolve()` takes project + task_id + branch + PR number
and returns `ResolvedUrls` with all URLs filled. Shorthand methods:
`task_url()`, `pr_url()`, `file_url()`.

### 2.4 Admonition Tags (Visual Classification)

ntfy supports emoji tags for visual classification:

| Event Type | Tags | Visual on Phone |
|-----------|------|----------------|
| task_done | ✅ white_check_mark | Green check |
| pr_merged | 🚀 rocket | Rocket |
| sprint_milestone | 🎉 tada, sprint | Party |
| sprint_complete | 🏆 trophy, sprint | Trophy |
| review_needed | 👀 eyes, review | Eyes |
| escalation | 🚨 rotating_light | Red siren |
| security_alert | 🔒 lock, security | Lock |
| agent_stuck | ⚠️ warning, agent | Warning |
| agent_offline | 🔴 red_circle, agent | Red dot |
| blocker | 🚫 no_entry, blocker | Stop sign |
| suggestion | 💡 bulb, suggestion | Light bulb |
| digest | 📰 newspaper, daily | Newspaper |
| infrastructure | 🔧 wrench, infra | Wrench |

PO glances at phone → emoji tells them what kind of event
BEFORE reading the text.

---

## 3. File Map

```
fleet/core/
├── notification_router.py  Classification, routing, deduplication   (156 lines)
├── cross_refs.py           Event→cross-reference generation          (238 lines)
└── urls.py                 Config-driven URL resolution              (142 lines)
```

Total: **536 lines** across 3 modules.

---

## 4. Per-File Documentation

### 4.1 `notification_router.py` — Classify & Route (156 lines)

#### Enums & Constants

| Name | Purpose |
|------|---------|
| `NotificationLevel` | Enum: INFO, IMPORTANT, URGENT |
| `ADMONITION_TAGS` | dict[event_type → list[emoji_tags]] — 13 event types with visual tags |

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `Notification` | 46-57 | title, message, level, event_type, source_agent, click_url, tags, dedup_key |
| `NotificationRouter` | 59-156 | Classify events, route to ntfy topics, cooldown-based dedup (300s). |

#### Key Logic

```python
# Classification (simplified)
if event_type in urgent_types:
    level = URGENT  → ntfy alert topic + Windows toast
elif event_type in important_types:
    level = IMPORTANT  → ntfy review topic
else:
    level = INFO  → ntfy progress topic

# Deduplication
dedup_key = f"{event_type}:{source_agent}"
if dedup_key in recent (within cooldown_seconds):
    → suppress
```

### 4.2 `cross_refs.py` — Cross-Reference Engine (238 lines)

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `CrossReference` | 29-36 | target_surface, action (comment/link/memory/notify), content, target_id, source_event_id |

#### Functions

| Function | Lines | What It Does |
|----------|-------|-------------|
| `generate_cross_refs(event)` | 39-231 | Takes FleetEvent → returns list[CrossReference]. Pure logic — no side effects. Handles 9 event types with surface-specific references. |
| `format_cross_ref_summary(refs)` | 234-239 | Format as "3 cross-refs → irc, ocmc, plane" for logging. |

#### Event → Cross-Reference Mappings (9 handled)

| Event | Refs Generated |
|-------|---------------|
| `fleet.task.completed` | Plane comment (PR link) + IRC #reviews + board memory |
| `fleet.plane.issue_created` | Board memory + IRC #fleet |
| `fleet.github.pr_merged` | Plane comment + IRC #fleet (if human merged) |
| `fleet.chat.mention` | IRC #fleet (cross-post per mentioned agent) |
| `fleet.plane.issue_commented` | IRC #fleet (cross-post per mentioned agent) |
| `fleet.plane.cycle_started` | IRC #sprint + board memory |
| `fleet.plane.cycle_completed` | IRC #fleet + board memory |
| `fleet.alert.posted` | IRC #alerts (if critical/high) |
| `fleet.task.blocked` | IRC #fleet |
| `fleet.escalation` | IRC #alerts + board memory (human attention) |

### 4.3 `urls.py` — URL Resolution (142 lines)

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `ResolvedUrls` | 16-32 | task, board, pr, compare, tree URLs + commits + files lists |
| `UrlResolver` | 34-143 | Config-driven resolution. `resolve()` fills all URLs from project + templates. Shorthand: `task_url()`, `pr_url()`, `file_url()`. |

---

## 5. Dependency Graph

```
notification_router.py  ← standalone (dataclasses, enum)

cross_refs.py           ← imports FleetEvent from events

urls.py                 ← imports Project from models
```

No circular dependencies. All three consumed by different layers.

---

## 6. Consumers

| Layer | Module | What It Uses | How |
|-------|--------|-------------|-----|
| **Orchestrator** | `orchestrator.py` | NotificationRouter | Wake notifications, health alerts, mode change notifications |
| **MCP Tools** | `tools.py` | NotificationRouter | fleet_alert → classify + route. fleet_escalate → URGENT. fleet_notify_human → direct push. |
| **MCP Tools** | `tools.py` | UrlResolver | Resolve task/PR/file URLs for comments, PR bodies, IRC messages |
| **Event Bus** | `event_chain.py` | — (indirect) | CHANNEL + NOTIFY surface events eventually use notification routing |
| **Storm** | `storm_integration.py` | — (indirect) | WARNING+ → IRC #alerts + ntfy PO |
| **Templates** | `comment.py`, `pr.py`, `irc.py` | UrlResolver | Embed clickable links in all fleet output |

---

## 7. Design Decisions

### Why 3 notification levels, not 5?

INFO / IMPORTANT / URGENT maps directly to ntfy's topic model.
Each topic has different behavior on PO's phone:
- INFO: silent, in notification history
- IMPORTANT: badge + sound
- URGENT: full-screen + sound + vibrate

More levels would require more ntfy topics and more complex routing.
Three covers: "FYI", "please look", and "drop everything."

### Why cooldown-based dedup, not event-ID based?

Event-ID dedup suppresses exact duplicates. But fleet produces
SIMILAR events repeatedly (agent heartbeats, storm indicators
re-firing, health checks re-detecting same stuck task). Cooldown-based
(same type + source within 300s) catches these repetitions. An agent
heartbeating every 30s would produce 120 notifications/hour without
cooldown.

### Why cross-refs as pure functions, not side effects?

`generate_cross_refs(event)` returns a LIST of actions. It doesn't
execute them. The CALLER chooses how to execute (Plane client, IRC
client, MC client). This separation means: cross-ref logic is
testable without mocking clients, and execution can be batched,
retried, or skipped per surface.

### Why config-driven URL templates?

URLs change per environment (localhost vs production, different
ports, different GitHub orgs). Config-driven means: change
`config/url-templates.yaml`, all URLs update. No code changes.
No hardcoded localhost:8000 scattered across modules.

---

## 8. IRC Channels

```
#fleet           — general fleet activity, task updates, sprint progress
#alerts          — critical/high alerts, security findings, storm warnings
#reviews         — PR reviews, approval notifications, review requests
#sprint          — sprint milestones, velocity updates, cycle start/end
#gates           — PO gate requests (phase advancement), approval needed
#contributions   — cross-agent contribution postings
```

The Lounge (web IRC client on localhost:9000) gives the PO:
- Persistent connections (doesn't disconnect on browser close)
- Link previews (PR URLs show title and status)
- Full-text search across message history
- Mobile-responsive (works on phone)
- Multiple channel view (see all activity at once)

---

## 9. Data Shapes

### Notification

```python
Notification(
    title="Task completed: Add fleet controls",
    message="software-engineer completed task abc123. PR: https://...",
    level=NotificationLevel.INFO,
    event_type="task_done",
    source_agent="software-engineer",
    click_url="https://github.com/org/repo/pull/42",
    tags=["white_check_mark"],
    dedup_key="task_done:software-engineer",
)
```

### CrossReference

```python
CrossReference(
    target_surface="plane",
    action="comment",
    content="OCMC task completed by software-engineer. PR: https://github.com/org/repo/pull/42\nAdded fleet controls to header bar",
    target_id="",  # filled by caller with Plane issue ID
    source_event_id="event-uuid-here",
)
```

### ResolvedUrls

```python
ResolvedUrls(
    task="http://localhost:8000/boards/board-id/tasks/task-id",
    board="http://localhost:8000/boards/board-id",
    pr="https://github.com/org/fleet/pull/42",
    compare="https://github.com/org/fleet/compare/main...fleet/engineer/abc123",
    tree="https://github.com/org/fleet/tree/fleet/engineer/abc123",
    commits=[
        {"sha": "abc123...", "short": "abc123", "url": "https://github.com/org/fleet/commit/abc123..."}
    ],
    files=[
        {"path": "DashboardShell.tsx", "url": "https://github.com/org/fleet/blob/fleet/engineer/abc123/DashboardShell.tsx"}
    ],
)
```

---

## 10. What's Needed

### Infrastructure
- The Lounge deployment (M92-96) — web IRC client for PO visibility
- IRC channel creation (#fleet, #alerts, #reviews, #sprint, #gates, #contributions)
- ntfy topic configuration (progress, review, alert) with per-topic behavior

### Integration
- Cross-reference execution — `generate_cross_refs()` returns refs but
  no caller currently executes them via Plane/IRC/MC clients
- Daily digest generation — fleet-ops or governance agent posts
  daily summary to #fleet and board memory
- Mention routing from Plane comments to agent heartbeat context

### Test Coverage

| File | Tests | Coverage |
|------|-------|---------|
| `test_notification_router.py` | 15+ | Classification, routing, dedup |
| `test_cross_refs.py` | 10+ | Event → ref mapping per event type |
| `test_urls.py` | 10+ | Template resolution, shorthand methods |
| **Total** | **35+** | Core logic covered. Missing: execution integration |
