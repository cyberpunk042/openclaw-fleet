# Brain Modules Standard — Orchestrator, Chain Registry, Session Management

**Date:** 2026-04-01
**Status:** ACTIVE STANDARD
**Type:** Module standard (Python code)
**Source:** fleet-elevation/04 (brain architecture), fleet-elevation/23 (lifecycle), System 22 §4.7 (session management)
**Location:** `fleet/core/` and `fleet/cli/orchestrator.py`

---

## 1. Purpose

The brain is the fleet's central intelligence — deterministic Python
logic that runs every 30 seconds. No AI. No LLM calls. Pure rule
evaluation. The brain does everything that CAN be done without AI,
leaving agents to do only what REQUIRES AI.

> "The Brain is not called brain for nothing it is a critical part for
> the cortexes / agents to do their part."

---

## 2. Existing Modules (Verified in Code)

| Module | Lines | What It Does | Status |
|--------|-------|-------------|--------|
| orchestrator.py | ~1378 | 9-step main cycle, dispatch, wake, health | Exists, needs extension to 13 steps |
| preembed.py | 171 | Build heartbeat pre-embed, format_task_full | Exists, needs role data expansion |
| context_assembly.py | 250+ | Assemble heartbeat + task context | Exists, needs autocomplete chain |
| stage_context.py | 215 | Stage instructions (MUST/MUST NOT/CAN) | Exists, complete |
| role_providers.py | 80+ | PM, fleet-ops, architect role data | Exists, needs devsecops + worker providers |
| agent_lifecycle.py | 100+ | ACTIVE→IDLE→SLEEPING→OFFLINE | Exists, needs brain evaluation |
| budget_modes.py | varies | Fleet tempo setting | Exists, mode definitions TBD |
| fleet_mode.py | varies | work_mode × cycle_phase × backend_mode | Exists, complete |
| smart_chains.py | varies | DispatchContext, CompletionChain | Exists |
| doctor.py | 250+ | Disease detection (4/11 implemented) | Exists, needs 7 more |
| teaching.py | 80+ | Lesson adaptation, injection, evaluation | Exists |
| storm_monitor.py | varies | 9 indicators, 5 severity levels | Exists |
| budget_monitor.py | varies | OAuth quota reading, thresholds | Exists |
| session_telemetry.py | 230 | Parse Claude Code JSON → fleet modules | Exists |
| change_detector.py | varies | Diff task state between cycles | Exists |

---

## 3. New Modules to Create (9 modules)

### 3.1 fleet/core/chain_registry.py

**Responsibility:** Event → handler mapping. When events fire, handlers react.
**Source:** fleet-elevation/04 (Layer 2: Chain Registry)

```python
class ChainRegistry:
    """Event → handler mapping. Deterministic chains."""

    def __init__(self, config: dict):
        self._handlers: dict[str, list[ChainHandler]] = {}
        self._config = config
        self._max_cascade_depth = 5

    def register(self, event_type: str, handler: ChainHandler): ...
    async def dispatch(self, event: Event, depth: int = 0): ...
```

**Standards:**
- Loaded from `config/chains.yaml` at startup
- Max cascade depth = 5 (prevents infinite loops)
- Each handler has `should_fire()` and `execute()` methods
- Handlers return `ChainResult` with optional emitted events
- Partial failure tolerated (one handler failing doesn't break chain)
- Tests: event dispatched → correct handlers fire, cascade depth enforced

### 3.2 fleet/core/chain_handlers.py

**Responsibility:** Standard handler implementations.
**Source:** fleet-elevation/04 (Registered Chains section)

**Handlers needed:**
| Handler | Fires On | Does |
|---------|----------|------|
| create_contribution_opportunities | fleet.methodology.stage_changed (to_stage=reasoning) | Create contribution tasks per matrix |
| notify_stage_change | fleet.methodology.stage_changed | IRC #fleet, board memory |
| checkpoint_notification | fleet.methodology.readiness_changed (at 50) | Notify PO |
| gate_enforcement | fleet.methodology.readiness_changed (at 90) | Require PO approval |
| create_pr | fleet.task.completed | GitHub PR creation |
| move_to_review | fleet.task.completed | MC task status → review |
| create_approval | fleet.task.completed | MC approval object |
| evaluate_parent | fleet.task.completed | All children done → parent to review |
| propagate_contribution | fleet.contribution.posted | Add to target task context |
| transition_to_done | fleet.approval.approved | Task → done |
| regress_task | fleet.approval.rejected | Readiness regressed, agent notified |

**Standards:**
- Each handler is a separate class implementing ChainHandler
- `should_fire()` checks config conditions
- `execute()` performs the action, returns ChainResult
- All handlers have unit tests
- Handlers log their actions for debugging

### 3.3 fleet/core/logic_engine.py

**Responsibility:** Multi-condition dispatch evaluation (10 gates).
**Source:** fleet-elevation/04 (Layer 3: Logic Engine, Dispatch Decision)

```python
async def should_dispatch(
    task: Task,
    agent: Agent,
    doctor_report: DoctorReport,
    fleet_state: FleetControlState,
    contributions: dict,
    phase_config: dict,
    session_state: SessionState,  # NEW: rate limit awareness
) -> tuple[bool, str]:
```

**10 dispatch gates:**
1. Fleet mode allows dispatch
2. Agent active for current cycle phase
3. Task unblocked
4. Agent online
5. Agent not busy
6. Doctor hasn't flagged agent
7. Readiness appropriate for stage
8. PO gate passed (at 90%)
9. Required contributions received
10. Phase prerequisites met

**Plus session management gate (NEW):**
11. Rate limit position safe for this context size (don't dispatch 1M near rollover)

**Standards:**
- Each gate is a separate function returning (bool, reason)
- Gate order matters — cheap checks first
- All gates have unit tests with clear pass/fail cases
- Failure returns SPECIFIC reason (not just "blocked")

### 3.4 fleet/core/autocomplete.py

**Responsibility:** Build engineered autocomplete chain for dispatch.
**Source:** fleet-elevation/04 (Autocomplete Chain Builder)

```python
async def build_autocomplete_chain(
    task: Task, agent: Agent,
    contributions: dict, phase_config: dict, role_config: dict,
) -> str:
```

**Chain order (per context-files-standard.md §3):**
1. Identity grounding
2. Verbatim requirement
3. Stage protocol
4. Colleague contributions
5. Phase standards
6. Action directive
7. Chain documentation

**Standards:**
- Produces markdown string for task-context.md
- Order is FIXED (not configurable — it IS the autocomplete chain)
- Verbatim requirement NEVER summarized
- Contributions included when available
- Stage protocol from stage_context.py
- Action directive role-specific and stage-specific

### 3.5 fleet/core/session_manager.py

**Responsibility:** Rate limit session management, context evaluation.
**Source:** System 22 §4.7, PO requirements (2026-04-01)

```python
@dataclass
class SessionEvaluation:
    agent_name: str
    context_tokens: int        # current context size
    needs_context: bool        # predicted upcoming work needs this context?
    should_compact: bool       # brain recommends compaction
    should_dump: bool          # brain recommends dump to artifacts
    reason: str                # why this decision
    allow_budget_overflow: bool # ok to go over 90% for compaction cost

class SessionManager:
    def evaluate_fleet_sessions(
        self, agents: list[AgentState],
        rate_limit: RateLimitState,
        tasks: list[Task],
    ) -> list[SessionEvaluation]: ...

    def aggregate_context_cost(
        self, agents: list[AgentState],
    ) -> int: ...  # total tokens across fleet

    def should_dispatch_large_context(
        self, task_complexity: str,
        rate_limit: RateLimitState,
    ) -> tuple[bool, str]: ...
```

**Decision logic (from PO requirements):**
- Agent > ~40-80K tokens + no predicted work → dump to artifacts
- Agent > ~40-80K tokens + related work coming → prepare synthesised re-injection
- Near rollover + heavy contexts → force compact (allow >90% for compaction cost)
- Near rollover → don't dispatch 1M context tasks
- Aggregate math: 5×200K = 1M on rollover ≈ 50% of x5 Pro window

**Standards:**
- Thresholds configurable via config/fleet.yaml session_management section
- Decisions logged for debugging
- All decision paths have unit tests
- Integrates with budget_monitor.py (rate limit data) and session_telemetry.py (context data)

### 3.6 fleet/core/heartbeat_gate.py (NEW — 2026-04-01)

**Responsibility:** Silent heartbeat interception. The brain's filter
between gateway cron firing and Claude call.
**Source:** fleet-elevation/23, System 06 §0, PO requirement

PO requirement (verbatim):
> "the agent need to be able to do silent heartbeat when they deem
> after a while that there is nothing new from the heartbeat, (2-3..)
> then it relay the work to the brain to actually do a compare and an
> automated work of the heartbeat in order to determine if it require
> a real heartbeat."

```python
class HeartbeatGate:
    """Intercepts cron heartbeat firing and decides: Claude call or silent OK.
    
    The cron NEVER stops. The agent is always on call. This gate is
    the filter between the cron firing and the Claude call happening.
    """

    def evaluate(
        self,
        agent_state: AgentState,
        tasks: list[Task],
        changes: ChangeSet,
        board_memory: list,
        contributions: dict,
        directives: list,
    ) -> HeartbeatDecision:
        """Decide whether to fire a real Claude heartbeat or respond silently.
        
        For ACTIVE/IDLE agents: always fire real heartbeat.
        For IDLE/SLEEPING agents: evaluate deterministically (FREE).
        """
        if agent_state.status in (AgentStatus.ACTIVE, AgentStatus.IDLE):
            return HeartbeatDecision(fire_real=True, reason="Agent active/idle")
        
        # Brain evaluates — _evaluate_sleeping_agent() from fleet-elevation/23
        wake = _evaluate_sleeping_agent(
            agent_state.name, agent_state, tasks, changes,
            board_memory, contributions, directives,
        )
        
        if wake.should_wake:
            call = decide_claude_call(agent_state, wake, ...)
            return HeartbeatDecision(
                fire_real=True,
                reason=wake.reason,
                claude_config=call,  # model, effort, session strategy
            )
        
        return HeartbeatDecision(
            fire_real=False,
            reason="Silent heartbeat OK — nothing for this agent",
        )

@dataclass
class HeartbeatDecision:
    fire_real: bool              # True = make Claude call, False = silent OK
    reason: str                  # why this decision
    claude_config: Optional[ClaudeCallDecision] = None  # if fire_real, how to call
```

**Architecture:**
```
Gateway cron fires → HeartbeatGate.evaluate() → fire_real?
  YES → Claude call with strategic config (model, effort, session)
  NO  → silent OK logged, $0 cost
```

**Standards:**
- Gate evaluates in < 10ms (deterministic Python, no I/O except MC reads already cached)
- Never blocks the cron — either fires Claude call or returns immediately
- All wake triggers from fleet-elevation/23 implemented
- Logs every decision for debugging
- Session manager (§3.5) feeds additional context (rate limit state, context size)
- Unit tests for each wake trigger path + each silent OK path

### 3.7 fleet/core/trail.py

**Responsibility:** Trail recording and retrieval.
**Source:** fleet-elevation/04 (Trail System Integration)

**Standards:**
- Records to board memory with `trail` + `task:{id}` tags
- Reconstructable by tag filter
- Event types: stage_transition, contribution_received, approval_decision, po_gate, phase_advance

### 3.7 fleet/core/propagation.py

**Responsibility:** Cross-task data propagation.
**Source:** fleet-elevation/04 (Cross-Task Propagation)

**Propagation types:**
- Child → parent (comments, completions, artifacts)
- Contribution → target task (contribution data → context)
- Transfer → receiving agent (context packaging)

### 3.8 fleet/core/contributions.py

**Responsibility:** Contribution opportunity management.
**Source:** fleet-elevation/04 (Contribution Opportunity Creation), fleet-elevation/15

**Standards:**
- Reads contribution matrix from config
- Creates tasks when stage/phase conditions met
- Checks for existing contributions (no duplicates)
- Phase-aware: POC requires fewer contributions than production

---

## 4. Module Code Standards

ALL new modules follow:

| Standard | What It Means |
|----------|--------------|
| SRP | One module = one concern. No multi-purpose modules. |
| Type hints | All public functions have parameter and return type hints |
| Docstrings | All public functions have docstrings (what, not how) |
| Tests | Unit tests in fleet/tests/ mirroring module path |
| No circular imports | Dependencies point inward (core → infra, not reverse) |
| Config from YAML | Thresholds, matrices, settings from config files |
| Conventional commits | `feat(brain):`, `fix(chain):`, `refactor(dispatch):` |
| Error handling | Fail loudly in dev, gracefully in production |
| Logging | Structured logging for all decisions and state changes |
| No hardcoded values | Agent names, thresholds, intervals from config |

---

## 5. Orchestrator Evolution

Current: 9 steps (Steps 0-8)
Target: 13 steps (Steps 0-12)

| Step | Current | Target | New Module |
|------|---------|--------|-----------|
| 0 | Context refresh | Context refresh + autocomplete chain | autocomplete.py |
| 1 | Security scan | Process event queue (chain registry) | chain_registry.py |
| 2 | Doctor | Doctor (+ 7 new detections) | doctor.py (extend) |
| 3 | Ensure approvals | Gate processing (PO gates) | logic_engine.py |
| 4 | Wake drivers | Contribution management | contributions.py |
| 5 | Dispatch | Dispatch (10 gates via logic engine) | logic_engine.py |
| 6 | Process directives | Approval & transition | — |
| 7 | Evaluate parents | Parent evaluation | — |
| 8 | Health check | Driver management (PM/fleet-ops wake) | — |
| 9 | — | Cross-task propagation | propagation.py |
| 10 | — | Session management | session_manager.py |
| 11 | — | Health & budget | — |
| 12 | — | Directives | — |

**Transition strategy (from fleet-elevation/31):**
- Extend, don't rewrite — add new steps alongside existing
- Test each new step independently before integrating
- One phase at a time — complete Phase A, verify, THEN Phase B
- Existing tests must pass (or be updated for new behavior)

---

## 6. Config Extensions

### config/fleet.yaml additions

```yaml
session_management:
  context_dump_threshold: 50000    # tokens — agents over this with no work → dump
  rate_limit_awareness_threshold: 85  # % — start progressive awareness
  rate_limit_active_threshold: 90    # % — actively manage
  allow_compaction_over_budget: true  # allow >90% for compaction cost
  aggregate_warning_pct: 50          # warn if fleet context > this % of remaining quota

brain:
  cycle_interval: 30
  max_dispatch_per_cycle: 2
  max_cascade_depth: 5

chains:
  # loaded from config/chains.yaml (separate file for readability)

autocomplete:
  chain_order:
    - identity
    - verbatim_requirement
    - stage_protocol
    - colleague_contributions
    - phase_standards
    - action_directive
    - chain_documentation
```

---

## 7. Relationship to Other Standards

| Standard Doc | Relationship |
|-------------|-------------|
| context-files-standard.md | Brain GENERATES context/ files. Standard enforced in brain code (preembed, autocomplete). |
| heartbeat-md-standard.md | Brain writes context that HEARTBEAT.md acts on. Brain adjusts directives per state. |
| iac-mcp-standard.md | Brain reads configs deployed by IaC. Brain doesn't deploy — it consumes. |
| claude-md-standard.md | Brain doesn't modify CLAUDE.md. But CLAUDE.md rules shape what brain expects from agents. |
| agent-yaml-standard.md | Brain reads agent.yaml for roles, capabilities, heartbeat config. |
