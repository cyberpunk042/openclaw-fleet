# Fleet Elevation — Milestones Summary

**Date:** 2026-03-30
**Status:** Design — full milestone breakdown for all 21 documents
**Part of:** Fleet Elevation (document 22 of 22)

---

## PO Requirements (Verbatim)

> "Do not be afraid if this is 20+ new milestones documents we need
> everything I said."

> "No small feat. no hacks, no quickfix. this is a long and arduous
> task, we are not in a rush. take your time to do this well."

> "the fleet is ready when I say so."

---

## Implementation Phases

The fleet elevation is organized into implementation phases (not to
be confused with delivery phases). Each phase builds on the previous.

### Phase A: Data Model and Configuration
Foundation changes that everything else depends on.

**A1: Delivery phase data model**
- Add delivery_phase, phase_progression to TaskCustomFields
- Create fleet/core/phases.py
- Add phase custom field to configure-board.sh
- Add phase labels to Plane
- Tests: phase progression, inheritance, config-driven phases

**A2: Contribution data model**
- Add contribution_type, contribution_target to TaskCustomFields
- Add coworkers field to TaskCustomFields
- Create fleet/core/contributions.py
- Tests: contribution lifecycle, propagation

**A3: Trail data model**
- Create fleet/core/trail.py
- Trail recording and retrieval from board memory
- Trail event types and formatting
- Tests: trail recording, reconstruction

**A4: Configuration expansion**
- config/fleet.yaml: phases, contributions, chains, notifications
- config/chains.yaml: chain handler definitions
- config/brain.yaml: brain configuration
- Config loader updates to handle new sections

### Phase B: Brain Redesign
The orchestrator evolves from simple dispatcher to intelligent brain.

**B1: Chain registry**
- Create fleet/core/chain_registry.py
- Event → handler mapping with cascade control
- Handler base class and interface
- Config-driven chain loading
- Tests: dispatch, cascade depth, handler evaluation

**B2: Standard chain handlers**
- Create fleet/core/chain_handlers.py
- Handlers for: stage change, readiness change, completion,
  contribution, phase, approval, rejection
- Each handler: should_fire evaluation, execute logic, event emission
- Tests: per-handler unit tests

**B3: Logic engine**
- Create fleet/core/logic_engine.py
- 10-gate dispatch evaluation
- Phase-aware dispatch decisions
- Contribution-aware dispatch decisions
- Tests: gate evaluation, edge cases, failure reasons

**B4: Autocomplete chain builder**
- Create fleet/core/autocomplete.py
- Per-role, per-stage chain construction
- Contribution injection into context
- Phase standards injection
- Tests: chain content for each role × stage

**B5: Orchestrator integration**
- Refactor fleet/cli/orchestrator.py
- Add steps: event queue, gate processing, contribution management,
  cross-task propagation
- Wire chain registry into cycle
- Wire logic engine into dispatch
- Wire autocomplete builder into context refresh
- Tests: full cycle integration

### Phase C: Contribution System
Cross-agent synergy becomes operational.

**C1: Contribution opportunity creation**
- Brain creates contribution tasks based on config rules
- Stage-triggered and phase-aware
- Duplicate prevention
- Tests: contribution creation rules, phase filtering

**C2: Contribution propagation**
- Contributions propagate from contribution task to target task
- Target task context updated with contributor data
- Notification to task owner
- Tests: propagation, context inclusion

**C3: Contribution MCP tools**
- fleet_contribute(task_id, type, content) — new tool
- fleet_request_input(task_id, role, question) — new tool
- fleet_transfer(task_id, to_agent, context) — new tool
- fleet_gate_request(task_id, gate_type, summary) — new tool
- Tests: tool integration, chain firing

**C4: Contribution validation**
- Fleet-ops review includes contribution verification
- Accountability generator checks contribution coverage
- Doctor detects contribution avoidance
- Tests: validation flow

### Phase D: Agent File Redesign
Every agent's files rewritten for the elevated fleet.

**D1: Template system**
- agents/_template/ with complete file set
- Template validation script (scripts/validate-agents.sh)
- Template includes: SRP sections, onion structure markers,
  role-specific placeholders

**D2: Per-agent CLAUDE.md (10 agents)**
- Role-specific rules for each agent
- Anti-corruption rules (shared section)
- Tool → chain documentation (role-specific)
- Stage-specific behavior (role-specific)
- Max 4000 chars per CLAUDE.md (gateway limit)

**D3: Per-agent TOOLS.md (10 agents)**
- Chain-aware tool documentation per role
- Which tools the role uses and when
- What chains fire on each tool call
- What the agent does NOT need to call manually

**D4: Per-agent IDENTITY.md + SOUL.md (10 agents)**
- Multi-fleet identity: fleet_id, fleet_number, username
- Role-specific values and boundaries
- Synergy points with other agents
- Place in the fleet

**D5: Per-agent HEARTBEAT.md review**
- Verify heartbeats align with contribution model
- Add contribution task handling
- Add cowork task handling
- Add phase awareness
- Verify autocomplete chain alignment

**D6: Per-agent AGENTS.md (10 agents)**
- Updated synergy knowledge per document 15
- Who contributes what to whom
- How to request input from colleagues

### Phase E: Standards and Phase System
Phase-aware standards become operational.

**E1: Phase-aware standards library**
- Update fleet/core/standards.py for phase context
- Add new artifact type standards (qa_test_def, security_req, etc.)
- Phase variants for each standard
- Tests: phase-aware completeness checking

**E2: Phase gate enforcement**
- Brain enforces PO gates at readiness 90%
- Brain enforces phase advancement gates
- fleet_phase_advance MCP tool
- Tests: gate blocking, PO approval flow

**E3: Phase events and display**
- Add phase event types to fleet/core/events.py
- Add phase event renderers to event_display.py
- IRC, board memory, ntfy routing for phase events
- Tests: event rendering, channel routing

### Phase F: Governance and Trails
PO governance model becomes operational.

**F1: Gate processing in brain**
- Brain reads gate requests from board memory
- Brain matches PO responses to gates
- Brain enforces: no dispatch past unapproved gates
- Tests: gate lifecycle

**F2: Readiness regression**
- Regression updates: readiness, stage, status
- Regression comment posted with PO feedback
- Event emitted, trail recorded
- Doctor signal on repeated rejection
- Tests: regression flow, stage mapping

**F3: Trail system**
- Trail events recorded at every lifecycle transition
- Trail reconstruction from board memory
- Accountability generator produces trail reports
- Tests: trail completeness for full lifecycle

**F4: Notification routing**
- Config-driven notification routing matrix
- Each event type → specific channels
- IRC channel structure: #fleet, #alerts, #reviews, #gates,
  #contributions, #sprint
- Tests: routing correctness

### Phase G: Multi-Fleet Identity
Fleet numbering and shared Plane support.

**G1: Fleet config and naming**
- fleet.id, fleet.number, fleet.name in config
- Agent naming: {fleet_id}-{role}
- Username generation
- Tests: naming, collision prevention

**G2: Plane attribution**
- Comment prefixing: [{fleet_id}-{role}]
- Label namespacing: {fleet_id}:stage:*, {fleet_id}:readiness:*
- Shared labels: phase:*, priority:*
- Tests: attribution, namespace isolation

**G3: Cross-fleet coordination**
- Two fleets on same Plane issue
- Each fleet's brain manages its own agents
- Plane is coordination layer
- Tests: multi-fleet scenario

### Phase H: Integration Testing and Validation
Prove it all works.

**H1: Flow simulations**
- Implement Flow 1-5 from document 19 as integration tests
- Full lifecycle: creation → contributions → dispatch → work →
  review → approval → done
- Phase advancement flow
- Rejection and regression flow
- Immune system intervention flow

**H2: Live fleet validation**
- Test against running MC backend
- Verify all new custom fields registered
- Verify chain handlers fire correctly
- Verify contributions propagate
- Verify trails are recorded
- Verify phase gates are enforced

**H3: Agent behavior validation**
- Deploy to running fleet
- Observe: do agents follow autocomplete chains?
- Observe: do contributions arrive in agent context?
- Observe: do agents reference contributions in their work?
- Observe: does the immune system detect new disease patterns?

---

## Implementation Order

```
Phase A (foundation)     ← data model, everything depends on this
    ↓
Phase B (brain)          ← chain registry, logic engine, autocomplete
    ↓
Phase J (tool trees)     ← tree execution engine, tool upgrades
    ↓
Phase C (contributions)  ← cross-agent synergy
    ↓
Phase D (agent files)    ← agent awareness of new systems
    ↓
Phase E (standards)      ← phase-aware quality enforcement
    ↓
Phase F (governance)     ← PO gates, readiness regression
    ↓
Phase G (multi-fleet)    ← fleet identity, naming, attribution
    ↓
Phase I (lifecycle)      ← sleep/wake, strategic calls, cost-awareness
    ↓
Phase K (change mgmt)    ← requirement evolution, config versioning
    ↓
Phase H (validation)     ← prove it all works, end-to-end flows
```

Phase I (lifecycle) is added before validation because it affects
how agents operate during validation testing.

### Phase I: Agent Lifecycle and Strategic Calls (NEW)

Per document 23. Evolves existing infrastructure.

**I1: Content-aware lifecycle transitions**
- Add DROWSY status to agent_lifecycle.py
- Add consecutive_heartbeat_ok counter
- Add last_heartbeat_data_hash for content comparison
- Transition from time-based to content-aware sleep
- Tests: lifecycle state transitions, content detection

**I2: Brain-evaluated heartbeat**
- _evaluate_sleeping_agent() in orchestrator
- Role-specific wake triggers (PM: unassigned, fleet-ops: reviews,
  architect: design needs, QA: test predefinition)
- Prompt vs gradual wake urgency
- Tests: wake trigger evaluation per role, urgency classification

**I3: Strategic call decisions**
- decide_claude_call() — model, effort, session, turns, mode
- Budget-aware call reduction
- Effort profile integration
- Tests: decision matrix for all situation × config combinations

**I4: Change detector per-agent tracking**
- Per-agent mention detection in board memory
- Per-agent contribution task detection
- Per-agent assignment detection
- ChangeSet gains agent-specific fields
- Tests: per-agent change detection accuracy

**I5: Gateway integration**
- configure_heartbeat() in gateway_client.py
- executor.py accepts brain's config override
- HEARTBEAT_OK feedback channel to orchestrator
- Tests: gateway respects brain's configuration

**I6: Lifecycle configuration**
- Per-agent lifecycle config in fleet.yaml
- Call strategy config (models, effort, session, turns)
- Role-specific overrides (PM/fleet-ops stay awake longer)
- Tests: config loading, override resolution

Each phase has its own tests. Tests run after each phase. Later phases
build on earlier phases but don't break them.

---

## Estimated Scope

### Phase J: Tool Call Trees (doc 24)

**J1: Tree execution engine**
- Create fleet/core/tool_trees.py — parallel/sequential tree executor
- Operation abstraction: critical (stop on fail) vs non-critical (continue)
- Cascade support: tree operations can emit events → more trees
- Tests: parallel execution, failure isolation, cascade depth

**J2: Upgrade existing tool trees**
- fleet_task_complete: 12+ operation tree (doc 24)
- fleet_commit: 6 operation tree
- fleet_artifact_create/update: completeness + phase standards
- All 25 existing tools reviewed for tree completeness
- Tests: per-tool tree verification

**J3: New tool implementations**
- fleet_contribute: 10+ operation tree
- fleet_transfer: context packaging, notification
- fleet_request_input: mention routing, contribution check
- fleet_gate_request: PO notification chain
- fleet_phase_advance: standards check, PO gate
- Tests: new tool integration tests

### Phase K: Change Management (doc 27)

**K1: Requirement change detection**
- change_detector: detect verbatim/description changes per task
- Event: fleet.task.requirement_changed
- Chain: notify agent, evaluate severity, invalidate contributions
- Tests: change detection, severity evaluation, contribution invalidation

**K2: Evolution support**
- Config versioning (git-tracked, conventional commits)
- Standard evolution cycle (gap → update → teaching → detection)
- Agent file evolution with template validation
- Tests: config reload, standard update propagation

---

## Estimated Scope

| Phase | New Files | Modified Files | New Tests |
|-------|-----------|---------------|-----------|
| A | 3 | 4 | ~40 |
| B | 5 | 2 | ~80 |
| C | 1 | 4 | ~50 |
| D | 0 | 60+ (agent files) | ~30 |
| E | 0 | 4 | ~40 |
| F | 0 | 3 | ~30 |
| G | 0 | 5 | ~20 |
| I | 0 | 7 | ~40 |
| J | 1 | 25 (tools.py + per tool) | ~60 |
| K | 0 | 3 | ~20 |
| H | 3 | 0 | ~50 |
| **Total** | **13** | **115+** | **~460** |

Adding to existing: 821 tests + 460 = ~1280 tests.

---

## Cross-Cutting Requirements for ALL Phases

### PO Requirements (Verbatim)

> "Use TDD when possible with high critical level tests and pessimistic
> ones with smart assertions and logics."

> "we need to use design patterns, know when to do a builder, a cache,
> an index, a mediator, an API, a core, a module"

> "we should be mindful of standards like cloudevents and such"

> "we will need to write diagrams too"

> "its important to respect pattern and to know when to evolve and
> refactor, and when to change and when to remove and when to upgrade"

### TDD Approach
Every phase uses Test-Driven Development where possible:
1. Write test cases first (red) — pessimistic, critical-level
2. Implement to make tests pass (green)
3. Refactor while keeping tests green
4. Smart assertions: verify behavior, not implementation wiring
5. Critical tests must NEVER be skipped

### Design Pattern Application Per Phase
- **Phase A:** Repository pattern for data access, Factory for model creation
- **Phase B:** Mediator (chain registry), Observer (event handlers), Strategy (dispatch gates), Builder (autocomplete chain)
- **Phase C:** Factory (contribution creation), Adapter (contribution propagation)
- **Phase D:** Template Method (agent file structure)
- **Phase E:** Strategy (phase-aware standards), Decorator (phase checking)
- **Phase F:** Chain of Responsibility (gate processing)
- **Phase G:** Abstract Factory (fleet-specific identity)
- **Phase H:** Integration test patterns, simulation patterns

### Industry Standards
- Events: evaluate CloudEvents specification for event format
- API: OpenAPI for any exposed interfaces
- Monitoring: OpenTelemetry for observability
- Commits: Conventional Commits (already adopted)
- Config: YAML standards for configuration

### Diagrams (per Document 19)
15 diagrams to be produced during implementation:
- Architecture (3): system map, onion layers, data flow
- Lifecycle (4): task states, stage progression, phase progression, two-axis
- Chains (3): event flow, contribution flow, completion flow
- Agent (2): synergy matrix, communication map
- Operational (3): orchestrator cycle, dispatch tree, immune system flow

Diagrams are produced as Mermaid (version-controlled) and/or ASCII
(embeddable in agent context). Maintained as the system evolves.

---

## Verification

Each phase verified by:
1. `pytest fleet/tests/ -v` — all pass (TDD: tests exist BEFORE code)
2. Specific flow validation per document 19
3. Design pattern review: correct pattern for the problem?
4. Standards compliance: SRP, Domain, Onion respected?
5. Live testing against running fleet infrastructure
6. Diagrams updated to reflect implemented state
7. PO review: "the fleet is ready when I say so"

---

## What This Means

This is not a quick project. It's a comprehensive redesign of how
10 AI agents — each a top-tier expert of their profession — work
together as a team of specialists. Every system gets touched. Every
agent gets new files. New concepts (phases, contributions, trails,
cowork, transfers, gates) get implemented. The brain becomes
significantly smarter. Design patterns are applied correctly.
Industry standards are respected. TDD with pessimistic tests ensures
reliability. The quality bar rises across the board.

The PO said: "No small feat. No hacks. No quickfix. This is long
and arduous work. Take your time to do this well."

> "The words and titles I used are not for nothing. there is a huge
> difference between any general agent..... those are top tier wise
> agent."

That's what this is. 22 documents of design. 8 implementation phases.
~340 new tests. 80+ files modified. 12 new modules. 15 diagrams.
TDD. Design patterns. Industry standards. Top-tier agents.

And it's ready when the PO says so.