# Agent Lifecycle and Strategic Claude Calls

**Date:** 2026-03-30
**Status:** Design — sleep/wake lifecycle, cost-aware operation
**Part of:** Fleet Elevation (document 23 — added to series)

---

## PO Requirements (Verbatim)

> "the agent need to be able to do silent heartbeat when they deem
> after a while that there is nothing new from the heartbeat, (2-3..)
> then it relay the work to the brain to actually do a compare and an
> automated work of the heartbeat in order to determine if it require
> a real heartbeat."

> "obviously if the PM or anyone would call for him he would answer
> promptly... even if it is asleep, it will do the whole wake process
> if he is called for duty and it will awake slowly if it starts to see
> update and promptly if they are related to him or his role."

> "Like any good employee on call who know he can relax a bit reduce
> cost and let the automated systems take the relay while there is
> nothing particular to work on anyway."

> "There is a whole lifecycle and a whole upgrade to it."

> "We will in general remember that we dont do claude call just for
> fun... we do them strategically with the right configurations
> appropriate to the case, this include everything including the effort
> setting and if we need to compact to start a plan or something else
> and whatnot."

---

## What This Document Covers

The complete agent lifecycle — from active work through idle,
sleeping, and back to active. How the brain takes over heartbeat
evaluation when agents sleep. How Claude calls are made strategically
with the right model, effort, session strategy, and timing. How all
the existing infrastructure (agent_lifecycle.py, fleet_mode.py,
budget_monitor.py, change_detector.py, gateway_client.py, executor.py)
connects to make this work.

---

## What Already Exists (Code Foundation)

### fleet/core/agent_lifecycle.py
Already implements:
- `AgentStatus` enum: ACTIVE, IDLE, SLEEPING, OFFLINE
- Time-based transitions: IDLE after 10min, SLEEPING after 30min,
  OFFLINE after 4h
- `needs_heartbeat()` — status-based intervals (ACTIVE: none,
  IDLE: 30min, SLEEPING: 2h)
- `wake()` — explicitly wake an agent
- `FleetLifecycle` — tracks all agents, `agents_needing_heartbeat()`,
  `is_fleet_idle()`

### fleet/core/fleet_mode.py
Already implements:
- Work mode: full-autonomous, project-management-work, local-work-only,
  finish-current-work, work-paused
- Cycle phase: execution, planning, analysis, investigation, review,
  crisis-management
- Backend mode: 7 combos of Claude/LocalAI/OpenRouter
- `should_dispatch()`, `get_active_agents_for_phase()`

### fleet/core/budget_monitor.py
Already implements:
- Real Claude OAuth quota reading via API
- QuotaReading: session_pct, weekly_all_pct, weekly_sonnet_pct
- Hard limits: weekly >= 90% → pause, session >= 95% → wait
- Fast-climb detection: +5% in 10min → pause
- Alert thresholds: 50%, 70%, 80%, 90% with severity levels

### fleet/core/change_detector.py
Already implements:
- ChangeDetector diffs task state between cycles
- Detects: task_created, task_status_changed, task_unblocked
- ChangeSet: new_tasks_in_review, new_tasks_done,
  new_tasks_in_inbox, tasks_unblocked, agents_went_offline
- `needs_review_wake` — fleet-ops should wake for reviews
- `needs_dispatch` — new inbox/unblocked tasks to dispatch

### fleet/infra/gateway_client.py
Already implements:
- `prune_agent()` — sessions.delete (kill session)
- `force_compact()` — sessions.compact (reduce context)
- `inject_content()` — chat.send (force content into session)
- `create_fresh_session()` — sessions.patch (new session)
- All via WebSocket JSON-RPC to gateway on ws://localhost:18789

### gateway/executor.py
Already implements:
- `execute_task()` — runs agent via Claude Code CLI
- Supports: model, effort, mode (think/edit), max_turns, timeout
- `_build_agent_context()` — reads CLAUDE.md + context/ files
- Context files: up to 8000 chars each, sorted, full content
- Returns: result, usage, cost_usd, model, error

---

## What Needs to Change — The Elevation

### Current Problem
The lifecycle transitions are TIME-BASED: idle after 10min, sleep
after 30min. But time alone doesn't capture what the PO described.

The PO said: "when they deem after a while that there is nothing
new from the heartbeat, (2-3..)" — the agent ITSELF notices nothing
is new after 2-3 heartbeats. This is CONTENT-AWARE sleep, not just
time-based sleep.

And: "then it relay the work to the brain to actually do a compare"
— the brain takes over with DETERMINISTIC evaluation. No Claude call
for "is there something for me?" The brain KNOWS by reading the data.

### Content-Aware Lifecycle — The Missing Piece (Rectified 2026-04-01)

The agent lifecycle tracks CONTENT, not just TIME. After 1 HEARTBEAT_OK,
the brain takes over evaluation. No intermediate states — one proper
heartbeat with nothing to do is enough to relay to the brain.

```python
@dataclass
class AgentState:
    name: str
    status: AgentStatus
    last_active_at: Optional[datetime] = None
    last_heartbeat_at: Optional[datetime] = None
    current_task_id: Optional[str] = None
    consecutive_heartbeat_ok: int = 0     # 1 = brain takes over
    last_heartbeat_data_hash: str = ""    # hash of data at last heartbeat
```

The `consecutive_heartbeat_ok` counter is key. After 1 HEARTBEAT_OK,
`brain_evaluates` becomes True. The cron still fires, the brain
intercepts, evaluates deterministically (free), and only fires a
real Claude heartbeat if a wake trigger is found.

The `last_heartbeat_data_hash` captures what the agent's pre-embed
data looked like. If the hash hasn't changed, there's literally
nothing new — the brain can skip evaluation entirely.

### Agent States (Rectified 2026-04-01)

```python
class AgentStatus(str, Enum):
    ACTIVE = "active"       # Working on a task
    IDLE = "idle"           # 1 HEARTBEAT_OK — brain takes over
    SLEEPING = "sleeping"   # Been idle a long time (30min+)
    OFFLINE = "offline"     # Been idle very long time (4h+)
```

NO DROWSY state. States are VISIBILITY LABELS — they tell the PO
and dashboard how long an agent has been idle. They do NOT change
responsiveness. ALL states respond to wake triggers identically.

The lifecycle:

```
ACTIVE: Agent has work. Real Claude sessions.
   ↓ (task completes, no new assignment, 1 HEARTBEAT_OK)
IDLE: Brain takes over. Cron fires, brain intercepts.
   Silent heartbeat if nothing. Real heartbeat if wake trigger.
   Wake triggers: task assignment, @mention, tag, PO directive.
   ↓ (30 min idle)
SLEEPING: Same as IDLE — brain still intercepts every cron fire.
   Status label for visibility: "this agent has been idle a while."
   ↓ (4 hours idle)
OFFLINE: Same as SLEEPING — status label for "idle very long."
   ↓ (wake trigger detected by brain)
ACTIVE: Brain fires real heartbeat with strategic config.
   Agent works. Cycle restarts.
   ↓ (agent has work)
ACTIVE
```

---

## Brain-Evaluated Heartbeat — The Relay

When an agent has brain_evaluates=True (after 1 HEARTBEAT_OK), the brain does the heartbeat
evaluation INSTEAD of making a Claude call. This happens every
orchestrator cycle (30s):

```python
async def _evaluate_sleeping_agent(
    agent_name: str,
    agent_state: AgentState,
    tasks: list[Task],
    changes: ChangeSet,
    board_memory: list,
    contributions: dict,
    directives: list,
) -> WakeDecision:
    """Deterministic heartbeat evaluation — no Claude call.

    The brain checks everything the agent would have checked
    in its heartbeat, but does it with Python logic for free.
    """
    # PROMPT WAKE triggers (immediate attention needed)

    # 1. Direct mention in board memory?
    agent_mentions = [
        m for m in board_memory
        if f"mention:{agent_name}" in (m.tags or [])
        and m.created_at > agent_state.last_heartbeat_at
    ]
    if agent_mentions:
        return WakeDecision(
            should_wake=True,
            urgency="prompt",
            reason=f"Mentioned by {agent_mentions[0].source}",
            session_strategy="fresh",
        )

    # 2. Task assigned to this agent in inbox?
    new_assignments = [
        t for t in tasks
        if t.custom_fields.agent_name == agent_name
        and t.status == TaskStatus.INBOX
    ]
    if new_assignments:
        return WakeDecision(
            should_wake=True,
            urgency="prompt",
            reason=f"Task assigned: {new_assignments[0].title[:40]}",
            session_strategy="fresh",
        )

    # 3. Contribution task created for this agent?
    new_contributions = [
        t for t in tasks
        if t.custom_fields.agent_name == agent_name
        and t.custom_fields.contribution_type
        and t.status == TaskStatus.INBOX
    ]
    if new_contributions:
        return WakeDecision(
            should_wake=True,
            urgency="prompt",
            reason=f"Contribution needed: {new_contributions[0].title[:40]}",
            session_strategy="fresh",
        )

    # 4. PO directive targeting this agent?
    agent_directives = [
        d for d in directives
        if d.target_agent in (agent_name, "all")
        and d.created_at > agent_state.last_heartbeat_at
    ]
    if agent_directives:
        return WakeDecision(
            should_wake=True,
            urgency="prompt",
            reason="PO directive",
            session_strategy="fresh",
        )

    # GRADUAL WAKE triggers (attention may be needed soon)

    # 5. Role-specific data changed?
    role_triggers = _check_role_triggers(agent_name, tasks, changes)
    if role_triggers:
        return WakeDecision(
            should_wake=True,
            urgency="gradual",
            reason=role_triggers,
            session_strategy="compact",
        )

    # 6. General board activity increased significantly?
    if changes.has_changes and len(changes.changes) > 5:
        return WakeDecision(
            should_wake=True,
            urgency="gradual",
            reason=f"Board activity: {len(changes.changes)} changes",
            session_strategy="compact",
        )

    # STAY SLEEPING — nothing for this agent
    return WakeDecision(should_wake=False)


def _check_role_triggers(
    agent_name: str,
    tasks: list[Task],
    changes: ChangeSet,
) -> str:
    """Role-specific wake triggers — what would make THIS role care."""

    # fleet-ops: new tasks in review
    if agent_name == "fleet-ops" and changes.needs_review_wake:
        return f"New review tasks: {len(changes.new_tasks_in_review)}"

    # PM: unassigned tasks in inbox
    if agent_name == "project-manager" and changes.new_tasks_in_inbox:
        return f"Unassigned inbox tasks: {len(changes.new_tasks_in_inbox)}"

    # architect: tasks entering reasoning that need design input
    if agent_name == "architect":
        design_needed = [
            t for t in tasks
            if t.custom_fields.task_stage == "reasoning"
            and t.custom_fields.task_type in ("epic", "story")
            and not _has_contribution(t.id, "design_input")
        ]
        if design_needed:
            return f"Tasks need design input: {len(design_needed)}"

    # QA: tasks entering reasoning that need test predefinition
    if agent_name == "qa-engineer":
        tests_needed = [
            t for t in tasks
            if t.custom_fields.task_stage == "reasoning"
            and not _has_contribution(t.id, "qa_test_definition")
        ]
        if tests_needed:
            return f"Tasks need test predefinition: {len(tests_needed)}"

    # DevSecOps: PRs needing security review
    if agent_name == "devsecops-expert":
        security_needed = [
            t for t in tasks
            if t.status == TaskStatus.REVIEW
            and t.custom_fields.pr_url
            and not _has_contribution(t.id, "security_review")
        ]
        if security_needed:
            return f"PRs need security review: {len(security_needed)}"

    return ""  # No role-specific trigger
```

This is the "relay." The brain does what a heartbeat would do —
check messages, check tasks, check contributions — but does it with
PYTHON LOGIC. Zero Claude tokens. Every 30 seconds. For free.

---

## Strategic Claude Call Decisions

> "we dont do claude call just for fun... we do them strategically
> with the right configurations appropriate to the case, this include
> everything including the effort setting and if we need to compact
> to start a plan or something else and whatnot"

When the brain decides to fire a real Claude heartbeat (HeartbeatGate
found a wake trigger), it must configure the call strategically.
This is NOT a simple on/off — there are MANY dimensions the brain
weighs to determine the right configuration.

### The Decision Dimensions

Every Claude call has multiple configuration axes. The brain weighs
ALL of them for every call:

**1. Model Selection**
- Which model fits this work? Opus for deep reasoning (architecture,
  security, planning). Sonnet for standard work (implementation,
  review, routine). Future: LocalAI for simple evaluations.
- Constrained by: budget mode (economic blocks opus), work mode
  (conservative may cap at sonnet), task complexity, agent role.
- The 3-tier model applies: brain (free) → LocalAI (free) → Claude (paid).
  Use the cheapest tier that can handle it.

**2. Effort Level**
- Claude Code effort setting affects quality vs speed vs token usage.
- Constrained by: budget pressure, task importance, agent role.
- Higher effort = better output = more tokens = more cost.

**3. Context Size / Strategy**
- How much context does this call carry? 1M vs 200K.
- Does the agent have an existing session to continue, or start fresh?
- Constrained by: rate limit position (don't start 1M near rollover),
  agent context state (how much is already loaded), task relatedness
  (continue if same work, fresh if different).
- Session management (brain Step 10) feeds directly into this.

**4. Max Turns**
- How many tool-call cycles before stopping?
- Depends on: task complexity, stage (work stage needs more turns
  than a status check), whether this is a focused micro-task or
  a multi-cycle effort.

**5. Mode**
- Think (read-only analysis), Edit (file modifications),
  Act (run commands).
- Depends on: methodology stage (work stage needs edit,
  analysis stage needs think only).

**6. Budget Constraints**
- Current budget mode constrains which models and effort levels
  are allowed. Economic = sonnet only. Frugal = LocalAI only.
- Rate limit session position affects whether expensive calls
  are appropriate at this time.
**7. Agent Role**
- PM and fleet-ops default to opus (strategic reasoning).
- Workers default to sonnet (implementation work).
- Overridable per task complexity.
- Per agent-yaml-standard.md model selection table.

**8. Task Properties**
- Task type (epic vs subtask = different complexity).
- Task stage (conversation vs work = different capabilities needed).
- Delivery phase (production needs more thoroughness than POC).
- Story points (higher SP = more complex = potentially higher model).

**9. Fleet State**
- Storm severity affects what's allowed.
- How many agents are currently active (resource distribution).
- Aggregate fleet context vs remaining rate limit quota.

### What This Means in Practice

The brain doesn't have a fixed lookup table. It weighs these
dimensions together for each call. The infrastructure already
supports the configuration axes:

- `fleet_mode.py`: work_mode, backend_mode, cycle_phase
- `budget_monitor.py`: quota gates (safe to dispatch?)
- `budget_modes.py`: model constraints per mode
- `agent_lifecycle.py`: agent state + brain_evaluates flag
- `session_telemetry.py`: context size, rate limit position
- `storm_monitor.py`: severity affects allowed operations
- `agent.yaml`: per-agent default model
- `config/fleet.yaml`: configurable thresholds

The SPECIFIC values (which exact effort level for which exact
situation) will be determined through live testing and fine-tuning.
The structure supports adaptation — thresholds are in config YAML,
not hardcoded. The PO can adjust as the fleet operates and patterns
emerge.

> "like I said this will need find-tuning but we can come up with the
> right starting logic and make sure we can adapt and scale and make
> sure we can handle multple cases"

---

## Session Strategy — Separate from Lifecycle

> "this include everything including the effort setting and if we need
> to compact to start a plan or something else"

**Session decisions (compact, fresh, continue) are NOT lifecycle
decisions.** An agent that was SLEEPING for 30 minutes and wakes to
continue the SAME task doesn't need a fresh session — it still has
its context, its artifacts, its task state. Whether to compact or
continue depends on:

- The context state (how much is loaded, is it still relevant?)
- The cost situation (rate limit position, budget pressure)
- The task (same task continuing? different task? unrelated work?)
- Whether the agent was pruned by immune system (forced fresh)

A SLEEPING agent continuing its task = continue session.
A SLEEPING agent getting a completely unrelated new task = maybe fresh.
An agent near rate limit rollover with heavy context = compact.
An agent pruned by the immune system = forced fresh (regrowth).

These are session management decisions (brain Step 10, System 22 §4.7),
not lifecycle transitions. Lifecycle tells you the agent is IDLE or
SLEEPING. Session management decides what to do about the context.

Existing infrastructure for session operations:
```python
# gateway_client.py
await prune_agent(session_key)           # kill session (immune system)
await force_compact(session_key)         # reduce context
await create_fresh_session(session_key)  # new session
await inject_content(session_key, msg)   # add to session
```

---

## The Full Cycle — How It All Connects

### Orchestrator Cycle (every 30s)

```
1. Read tasks and agents from MC
2. Update FleetLifecycle with current activity
   → each agent's status updated: ACTIVE/IDLE/SLEEPING/OFFLINE
3. Cron fires for agents needing heartbeat:
   → HeartbeatGate evaluates: wake trigger found?
   → YES: fire real Claude heartbeat
   → NO: silent heartbeat OK ($0)
   → Wake triggers: task, mention, tag, directive, role-specific
4. Check BudgetMonitor — safe to dispatch?
5. Read FleetControlState — which agents allowed?
6. Run rest of cycle (13 steps per brain spec)
7. Write context/ files for agents with work
```

### Agent Heartbeat Flow

```
Gateway fires heartbeat for agent
→ Gateway reads agent files (IDENTITY, SOUL, CLAUDE, TOOLS, context/)
→ Gateway builds system prompt (injection order per doc 02)
→ Gateway calls Claude Code CLI with brain's config:
   model={brain chose}, effort={brain chose}, max_turns={brain chose}
→ Agent processes heartbeat:
   If work → ACTIVE, reset consecutive_heartbeat_ok
   If HEARTBEAT_OK → increment consecutive_heartbeat_ok
   If HEARTBEAT_OK → brain_evaluates = True (brain takes over)
→ Brain reads result:
   If HEARTBEAT_OK → brain_evaluates = True (brain takes over)
   If idle > 30 min → status = SLEEPING (visibility label)
   If idle > 4 hours → status = OFFLINE (visibility label)
   If agent worked → status = ACTIVE, consecutive = 0
```

### Cost Flow

```
Agent ACTIVE:   Real Claude sessions, agent drives work        $$$
Agent IDLE:     Cron fires → brain intercepts → silent OK ($0) $0
Agent SLEEPING: Same as IDLE, longer cron interval             $0
Agent WAKING:   Brain detects trigger → real heartbeat         $

10 agents, 7 idle/sleeping:
  3 active × normal cost
  7 idle/sleeping × $0 (brain evaluates for free)
  = ~70% cost reduction on idle agents
```

---

## Configuration

### Per-Agent Lifecycle Config

```yaml
# config/agent-autonomy.yaml (rectified 2026-04-01)

defaults:
  idle_after_heartbeat_ok: 1       # 1 HEARTBEAT_OK → brain takes over
  sleeping_after_seconds: 1800     # 30 min idle → SLEEPING (status label)
  offline_after_seconds: 14400     # 4 hours → OFFLINE (status label)

overrides:
  project-manager:
    wake_triggers:
      - unassigned_inbox
      - po_directive
      - blocked_task
  fleet-ops:
    wake_triggers:
      - pending_approval
      - security_alert
      - storm_warning
      - health_alert
  # ... see config/agent-autonomy.yaml for full list
```

### Strategic Call Config

Model and effort selection is handled by `model_selection.py` based on
task complexity (SP) and agent role. Session strategy depends on context
state. Turn counts are TBD — need live testing data.

These are NOT config values — they are runtime decisions made by
existing code (model_selection.py, backend_router.py).

---

## Interaction With Existing Systems

### agent_lifecycle.py Changes
- Add brain_evaluates property (True after 1 HEARTBEAT_OK)
- Add `consecutive_heartbeat_ok` counter
- Add `last_heartbeat_data_hash` for content-aware comparison
- Transition logic: time-based → content-aware (HEARTBEAT_OK count)
- Keep time-based as FALLBACK (if agent never responds, time still works)

### fleet_mode.py Changes
- work_mode gates dispatch (pause/resume/finish-current)
- backend_mode determines which backends the router can use (7 combos)
- cycle_phase filters active agents by phase

### budget_monitor.py Changes
- Budget status feeds into dispatch decisions
- check_quota() gates dispatch: weekly ≥ 90% → PAUSE
- Fast climb detection: +5% in 10min → PAUSE
- Fast-climb → immediate pause signal to lifecycle

### Session Management — Rate Limit Awareness (NEW — 2026-04-01)

PO requirement (verbatim):
> "if we reach the end of the reset I can surely tell you that we
> will force compact all conversation that are too last and will cause
> a spike, this is why we are aware and will not display a 1m context
> big quest when approaching that time"

> "if you are over 40 to 80 000 tokens or that you do not need to
> persist your session context... dump (as smart artifacts) it for a
> synthesised re-injection later if needed and/or simply a new task
> if not related. Only smart things. the brain is smart."

The `decide_claude_call` function and the brain's Step 10 must factor
rate limit session cycle awareness into every decision:

| Situation | Decision |
|-----------|----------|
| Rate limit at 85% used | Progressive awareness — no new 1M dispatches |
| Rate limit at 90% used | Active management — prepare heavy-context agents |
| Near rollover, agent >40-80K, no predicted work | Force compact / dump to artifacts |
| Near rollover, agent >40-80K, related work coming | Prepare synthesised re-injection |
| Near rollover, agent context unrelated to next work | Fresh session, no re-injection |
| Aggregate fleet context > 50% of remaining quota | Storm risk — stagger compactions |
| After rollover | Put agents back on track — fresh or re-inject |
| Compacting itself needs budget | Allow going over 90% for compaction cost |

The decision matrix (§Strategic Claude Call Decisions) needs these rows:
```
| Near rollover, heavy context | NO NEW DISPATCH | compact heavy agents | — | Prevent rollover spike |
| Near rollover, agent idle >40K | sonnet | medium | compact+dump | 5 | Dump to artifacts |
| After rollover, work continues | Per task | high | re-inject | 15 | Synthesised context |
| After rollover, new work | Per task | high | fresh | 15 | Clean start |
```

This connects to:
- Brain Step 10 (session management) in 04-the-brain.md
- System 22 §4.7 (rate limit session cycle awareness)
- Budget monitor (allows >90% for compaction cost)
- Storm prevention (aggregate context = storm indicator)

### change_detector.py Changes
- Add per-agent change tracking (what changed FOR each agent)
- Add mention detection (board memory with mention:{agent} since last check)
- Add contribution task detection (new contribution tasks per agent)
- ChangeSet gains: `agent_mentions`, `agent_new_contributions`,
  `agent_new_assignments`

### gateway_client.py Changes
- Add `configure_heartbeat(session_key, interval, model, effort)` —
  tell gateway to use specific config for next heartbeat
- This allows the brain to set per-agent heartbeat parameters
  that the gateway respects

### gateway/executor.py Changes
- Accept model/effort/mode/max_turns from brain's decision
  (currently reads from agent.yaml and task — needs brain override)
- Support "plan mode" session strategy (compact then structured
  planning prompt)
- Report HEARTBEAT_OK detection back to orchestrator (so
  consecutive counter can be updated)

---

## The On-Call Analogy — Complete

> "Like any good employee on call who know he can relax a bit reduce
> cost and let the automated systems take the relay while there is
> nothing particular to work on anyway."

The complete analogy:

| Employee State | Agent State | What Happens |
|---------------|-------------|-------------|
| At desk, working | ACTIVE | Full Claude sessions, productive work |
| At desk, no work | IDLE | Claude checks "anything for me?" |
| Stepped away, phone on | IDLE (brain takes over) | Brain monitors, agent still on call |
| At home, on call | SLEEPING | Brain monitors, zero calls, paged if needed |
| On vacation | OFFLINE | Extended absence, slow wake |
| Phone rings — direct | WAKING (prompt) | Drop everything, full attention |
| Sees Slack activity | WAKING (gradual) | Check in, assess if needed |

The automated systems (brain) monitor everything. The employee
(agent) only gets activated when there's real work that needs their
COGNITIVE ability. Everything that can be checked with data comparison
is handled by the automated systems for free.

---

## Connection to LocalAI Offload (AICP)

This lifecycle is where LocalAI integration makes strategic sense:

### Current: Binary (Claude or Nothing)
- SLEEPING: brain evaluates (deterministic, free, limited)
- ACTIVE: Claude call (powerful, expensive)

### Future: Three Tiers
- SLEEPING: brain evaluates (deterministic, free, limited)
- LIGHT WAKE: LocalAI evaluates (some AI reasoning, free, fast)
  "Is this mention relevant to me?" "Should I accept this task?"
  "Is this contribution request within my scope?"
- FULL WAKE: Claude evaluates (deep reasoning, paid, powerful)
  "Design the architecture." "Review this code." "Write this plan."

The sleep/wake lifecycle is the FIRST place where progressive offload
from Claude to LocalAI pays off. Simple evaluations that are too
complex for Python logic but don't need Claude-level reasoning —
that's LocalAI's sweet spot.

This connects directly to AICP's mission:
> "Progressive offload from Claude to LocalAI"

The lifecycle provides the FRAMEWORK for deciding what goes where.

---

## Testing Requirements

- Lifecycle transitions: ACTIVE → IDLE → SLEEPING → OFFLINE based
  on consecutive HEARTBEAT_OK count
- Brain evaluation: correctly identifies wake triggers for each role
- Prompt vs gradual wake: right urgency for right trigger
- Strategic call decisions: model/effort/session match situation
- Budget integration: calls reduce/stop as budget tightens
- Content-aware sleep: data hash comparison skips redundant checks
- Role-specific triggers: PM wakes for unassigned, fleet-ops for
  reviews, architect for design needs, QA for test predefinition
- Configuration: per-agent overrides respected
- Gateway interaction: brain's config reaches executor correctly
- Cost measurement: verify token reduction with sleeping agents

---

## Files to Modify

| File | Change |
|------|--------|
| `fleet/core/agent_lifecycle.py` | Add brain_evaluates property, 1 HEARTBEAT_OK threshold, ACTIVE→IDLE→SLEEPING→OFFLINE |
| `fleet/core/fleet_mode.py` | Lifecycle interaction, model/effort caps per profile |
| `fleet/core/budget_monitor.py` | Feed decisions to lifecycle, budget-aware call reduction |
| `fleet/core/change_detector.py` | Per-agent change tracking, mention/contribution detection |
| `fleet/infra/gateway_client.py` | configure_heartbeat() for brain-controlled parameters |
| `gateway/executor.py` | Accept brain's model/effort/session decisions, report HEARTBEAT_OK |
| `fleet/cli/orchestrator.py` | Integrate lifecycle evaluation into cycle, strategic call decisions |
| `config/fleet.yaml` | Lifecycle config, call strategy config |

---

## Open Questions

- How does the agent signal HEARTBEAT_OK to the orchestrator?
  (Currently the orchestrator doesn't read agent responses — the
  gateway manages sessions. Need a feedback channel.)
- Should the brain maintain a "data hash" per agent to detect
  changes, or should the change_detector handle this?
- How does the lifecycle interact with cowork? (Agent sleeping but
  is a coworker on an active task — should they stay awake?)
- Should there be a "snooze" option? (Agent wakes, decides nothing
  important, goes back to sleep for a specific duration.)
- How do we handle the transition from current time-based lifecycle
  to content-aware lifecycle? (Backward compatible? Or clean break?)