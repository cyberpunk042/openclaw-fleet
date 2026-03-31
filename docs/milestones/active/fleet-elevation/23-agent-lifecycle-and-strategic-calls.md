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

The complete agent lifecycle — from active work through idle, drowsy,
sleeping, and back to active. How the brain takes over heartbeat
evaluation when agents sleep. How Claude calls are made strategically
with the right model, effort, session strategy, and timing. How all
the existing infrastructure (agent_lifecycle.py, effort_profiles.py,
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

### fleet/core/effort_profiles.py
Already implements:
- Four profiles: full, conservative, minimal, paused
- Per-profile: max_dispatch, heartbeat intervals, allow_opus,
  allow_dispatch, allow_heartbeats, active_agents list
- `is_agent_active()` — check if agent is allowed under profile
- Profile read from config/fleet.yaml

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

### Content-Aware Sleep — The Missing Piece

The agent lifecycle needs to track not just TIME since last activity,
but CONTENT since last heartbeat:

```python
@dataclass
class AgentState:
    name: str
    status: AgentStatus
    last_active_at: Optional[datetime] = None
    last_heartbeat_at: Optional[datetime] = None
    current_task_id: Optional[str] = None

    # NEW: content-aware fields
    consecutive_heartbeat_ok: int = 0     # how many HEARTBEAT_OK in a row
    last_heartbeat_data_hash: str = ""    # hash of data at last heartbeat
    last_wake_trigger: str = ""           # what caused the last wake
    drowsy_since: Optional[datetime] = None  # when did drowsy start
```

The `consecutive_heartbeat_ok` counter is key. When the agent does
a real heartbeat and responds HEARTBEAT_OK, the orchestrator
increments this counter. After the PO's threshold (2-3), the agent
transitions to a BRAIN-EVALUATED state.

The `last_heartbeat_data_hash` captures what the agent's pre-embed
data looked like. If the hash hasn't changed, there's literally
nothing new — the brain can skip the Claude call without even
evaluating content.

### New Agent Status: DROWSY

Between IDLE and SLEEPING, there's a new state:

```python
class AgentStatus(str, Enum):
    ACTIVE = "active"       # Working on a task
    IDLE = "idle"           # Awake, watching (1 HEARTBEAT_OK)
    DROWSY = "drowsy"       # 2-3 HEARTBEAT_OK — brain can evaluate
    SLEEPING = "sleeping"   # Brain evaluates, no Claude calls
    OFFLINE = "offline"     # Extended sleep, longer wake time
```

The lifecycle becomes:

```
ACTIVE: Agent has work. Real heartbeats. Full Claude sessions.
   ↓ (task completes, no new assignment)
IDLE: 1 HEARTBEAT_OK. Still doing real heartbeats.
   ↓ (2nd HEARTBEAT_OK)
DROWSY: Agent signaled "nothing for me." Brain starts evaluating.
   Real heartbeat still happens but at reduced frequency.
   Brain compares data hash — if same, skip next heartbeat entirely.
   ↓ (3rd+ HEARTBEAT_OK or brain determines nothing new)
SLEEPING: No Claude calls. Brain evaluates every cycle (30s).
   Deterministic check: mentions? assignments? contributions?
   ↓ (mention, assignment, contribution, directive)
WAKING: Brain triggers wake.
   Prompt: fresh session, immediate attention.
   Gradual: compact session, lightweight check next cycle.
   ↓ (agent has work)
ACTIVE
```

---

## Brain-Evaluated Heartbeat — The Relay

When an agent is DROWSY or SLEEPING, the brain does the heartbeat
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
> with the right configurations appropriate to the case"

When the brain DOES decide to wake an agent, it makes strategic
decisions about HOW:

### The Call Decision Model

```python
@dataclass
class ClaudeCallDecision:
    """What the brain decides for each Claude call."""

    should_call: bool           # call Claude at all?
    model: str = "sonnet"       # opus, sonnet (future: localai)
    effort: str = "high"        # low, medium, high, max
    session_strategy: str = ""  # fresh, continue, compact
    max_turns: int = 10
    mode: str = "think"         # think, edit, act
    reason: str = ""            # why this configuration
```

### Decision Matrix

| Situation | Model | Effort | Session | Turns | Why |
|-----------|-------|--------|---------|-------|-----|
| Agent sleeping, nothing new | NO CALL | — | — | — | Brain handles deterministically |
| Agent sleeping, gradual wake | sonnet | medium | compact | 5 | Lightweight check, minimal cost |
| Agent sleeping, prompt wake (mention) | sonnet | high | fresh | 10 | Direct request, clean context |
| Agent sleeping, prompt wake (task) | Per task complexity | high | fresh | 15 | Real work, appropriate model |
| Agent active, heartbeat check | sonnet | medium | continue | 5 | Status check, keep context |
| Agent active, complex task work | opus | high | continue | 25 | Deep reasoning, full effort |
| Agent active, simple contribution | sonnet | medium | fresh | 10 | Focused micro-task |
| Agent active, context bloated | sonnet | high | compact then continue | 15 | Strip drift first |
| Agent needs planning | opus | high | plan mode | 20 | Structured planning |
| Crisis response | opus | max | fresh | 30 | Full power, urgent |
| Budget at 80%+ | sonnet | medium | compact | 5 | Conserve budget |
| Budget at 90%+ | NO CALL | — | — | — | Pause fleet |

### How the Brain Decides

```python
async def decide_claude_call(
    agent_state: AgentState,
    wake_decision: WakeDecision,
    task: Optional[Task],
    budget: BudgetMonitor,
    effort_profile: EffortProfile,
) -> ClaudeCallDecision:
    """Strategic decision about whether and how to call Claude."""

    # Budget gate — if budget is critical, don't call
    safe, reason = budget.check_quota()
    if not safe:
        return ClaudeCallDecision(
            should_call=False,
            reason=f"Budget blocked: {reason}",
        )

    # Sleeping agent with no wake trigger → no call
    if not wake_decision.should_wake:
        return ClaudeCallDecision(
            should_call=False,
            reason="Agent sleeping, nothing new",
        )

    # Effort profile gate — is this agent allowed?
    if not is_agent_active(effort_profile, agent_state.name):
        return ClaudeCallDecision(
            should_call=False,
            reason=f"Agent not active in {effort_profile.name} profile",
        )

    # Determine model based on task complexity + profile
    model = "sonnet"  # default
    if task and task.custom_fields.complexity == "high":
        model = "opus" if effort_profile.allow_opus else "sonnet"
    if task and task.custom_fields.task_type == "epic":
        model = "opus" if effort_profile.allow_opus else "sonnet"
    if wake_decision.urgency == "gradual":
        model = "sonnet"  # gradual wake = lightweight

    # Determine effort based on situation
    effort = "high"  # default
    if wake_decision.urgency == "gradual":
        effort = "medium"
    if agent_state.consecutive_heartbeat_ok > 0 and not task:
        effort = "medium"  # just checking, not working
    if budget._last_reading and budget._last_reading.weekly_all_pct > 70:
        effort = "medium"  # budget conscious

    # Determine session strategy
    session = wake_decision.session_strategy or "continue"
    if agent_state.status == AgentStatus.SLEEPING:
        session = "fresh"  # sleeping agents get clean context
    if agent_state.status == AgentStatus.DROWSY:
        session = "compact"  # drowsy agents get lean context

    # Determine max turns
    turns = 10
    if wake_decision.urgency == "gradual":
        turns = 5
    if task and task.custom_fields.task_type in ("epic", "story"):
        turns = 20
    if task and task.custom_fields.task_stage == "work":
        turns = 25

    # Determine mode
    mode = "think"
    if task and task.custom_fields.task_stage == "work":
        mode = "edit"  # work stage needs file access

    return ClaudeCallDecision(
        should_call=True,
        model=model,
        effort=effort,
        session_strategy=session,
        max_turns=turns,
        mode=mode,
        reason=f"Wake {wake_decision.urgency}: {wake_decision.reason}",
    )
```

---

## Session Strategy — When to Compact, Fresh, Continue

> "this include everything including the effort setting and if we need
> to compact to start a plan or something else"

### Fresh Session
Create a new session from scratch. Clean context, no accumulated drift.

When:
- Agent was SLEEPING and prompt wakes (clean slate)
- New task assigned (different context than previous)
- Agent was pruned by immune system (regrowth)
- Context is so bloated that compact won't help

How (existing infrastructure):
```python
await prune_agent(session_key)           # kill old session
await create_fresh_session(session_key)  # new session
# Gateway reads agent files on next heartbeat → clean context
```

### Compact Session
Reduce existing session context. Strip drift, keep essentials.

When:
- Agent is DROWSY and gradual wakes (lean check)
- Agent has been active for many cycles (context accumulated)
- Before starting a plan (clean thinking space)
- Budget is getting high (reduce per-call token count)

How (existing infrastructure):
```python
await force_compact(session_key)  # gateway compacts session
# Next heartbeat has leaner context
```

### Continue Session
Keep existing session. Context preserved for progressive work.

When:
- Agent is ACTIVE with in-progress task (multi-cycle work)
- Agent's artifact is partially built (needs continuity)
- Context is still clean (not bloated yet)

How:
Nothing to do — gateway continues the existing session naturally.

---

## The Full Cycle — How It All Connects

### Orchestrator Cycle (every 30s)

```
1. Read tasks and agents from MC
2. Update FleetLifecycle with current activity
   → each agent's status updated: ACTIVE/IDLE/DROWSY/SLEEPING
3. For each SLEEPING/DROWSY agent:
   → _evaluate_sleeping_agent() — deterministic, free
   → If wake needed: decide_claude_call() — strategic config
   → If wake prompt: gateway command (fresh/compact session)
   → If wake gradual: mark for next heartbeat with config
   → If no wake: skip — zero cost
4. Check BudgetMonitor — safe to dispatch?
5. Read EffortProfile — which agents allowed?
6. Run rest of cycle (doctor, dispatch, chains, etc.)
7. For agents that need heartbeats (per lifecycle intervals):
   → Write context/ files with pre-embed data
   → Gateway picks up on next heartbeat
   → Heartbeat fires with brain's chosen config
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
   If consecutive_heartbeat_ok >= threshold → signal drowsy
→ Brain reads result:
   If HEARTBEAT_OK and consecutive >= 2 → status = DROWSY
   If HEARTBEAT_OK and consecutive >= 3 → status = SLEEPING
   If agent worked → status = ACTIVE, consecutive = 0
```

### Cost Flow

```
Agent ACTIVE:    Claude calls at normal intervals, normal cost
Agent IDLE:      Claude calls at 30min intervals, reduced cost
Agent DROWSY:    Claude calls at 60min intervals, minimal effort
Agent SLEEPING:  ZERO Claude calls, brain evaluates for free
Agent WAKING:    ONE Claude call with strategic config, targeted cost

10 agents, 7 sleeping:
  3 active × normal cost
  7 sleeping × $0
  Brain evaluation × $0 (Python logic)
  = ~70% cost reduction on idle agents
```

---

## Configuration

### Per-Agent Lifecycle Config

```yaml
# config/fleet.yaml — lifecycle section

lifecycle:
  defaults:
    drowsy_after_heartbeat_ok: 2    # HEARTBEAT_OK count → drowsy
    sleeping_after_heartbeat_ok: 3  # HEARTBEAT_OK count → sleeping
    offline_after_hours: 4          # hours sleeping → offline

  # Role-specific overrides
  overrides:
    project-manager:
      drowsy_after_heartbeat_ok: 4  # PM stays awake longer
      sleeping_after_heartbeat_ok: 6
      wake_sensitivity: high        # wakes on indirect triggers too
    fleet-ops:
      drowsy_after_heartbeat_ok: 4
      sleeping_after_heartbeat_ok: 6
      wake_sensitivity: high
    architect:
      drowsy_after_heartbeat_ok: 2
      sleeping_after_heartbeat_ok: 3
      wake_sensitivity: medium
    software-engineer:
      drowsy_after_heartbeat_ok: 2
      sleeping_after_heartbeat_ok: 3
      wake_sensitivity: low         # only direct assignment/mention
    # ... other agents use defaults
```

### Strategic Call Config

```yaml
# config/fleet.yaml — call strategy section

call_strategy:
  models:
    complex_task: opus              # architecture, security, investigation
    standard_task: sonnet           # implementation, review, routine
    lightweight_check: sonnet       # heartbeat check, status
    future_local: hermes-3b         # LocalAI target for simple ops

  effort:
    complex_reasoning: high
    standard_work: high
    status_check: medium
    gradual_wake: medium
    budget_conscious: medium        # when weekly > 70%

  session:
    sleeping_prompt_wake: fresh
    sleeping_gradual_wake: compact
    drowsy_check: compact
    active_progressive: continue
    active_new_task: fresh
    active_bloated: compact
    before_planning: compact        # clean space for plan mode
    after_prune: fresh              # regrowth

  max_turns:
    heartbeat_check: 5
    simple_contribution: 10
    standard_task: 15
    complex_task: 25
    crisis: 30
```

---

## Interaction With Existing Systems

### agent_lifecycle.py Changes
- Add DROWSY status between IDLE and SLEEPING
- Add `consecutive_heartbeat_ok` counter
- Add `last_heartbeat_data_hash` for content-aware comparison
- Transition logic: time-based → content-aware (HEARTBEAT_OK count)
- Keep time-based as FALLBACK (if agent never responds, time still works)

### effort_profiles.py Changes
- Profiles now interact with lifecycle: profile can force specific
  agents to sleep (minimal profile sleeps all except fleet-ops)
- Profile determines model/effort caps that strategic decisions
  respect (conservative profile caps at sonnet)
- Profile can set wake_sensitivity overrides

### budget_monitor.py Changes
- Budget status feeds into strategic call decisions
- At 70%+ weekly → effort drops to medium, model stays sonnet
- At 80%+ weekly → reduce heartbeat frequency for active agents
- At 90%+ weekly → pause all except fleet-ops monitoring
- Fast-climb → immediate pause signal to lifecycle

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
| Stepped away, phone on | DROWSY | Brain monitors, agent checks less often |
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

- Lifecycle transitions: ACTIVE → IDLE → DROWSY → SLEEPING based
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
| `fleet/core/agent_lifecycle.py` | Add DROWSY, consecutive counter, data hash, content-aware transitions |
| `fleet/core/effort_profiles.py` | Lifecycle interaction, model/effort caps per profile |
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