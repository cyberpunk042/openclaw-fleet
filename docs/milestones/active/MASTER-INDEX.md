# Master Index — All Fleet Documents & Milestones

**Date:** 2026-03-31
**Status:** ACTIVE — honest assessment of every document and milestone
**Rule:** "Not live tested = not finished." Code existing ≠ done.

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Live tested and verified |
| 🔨 | Code exists, unit tested, NOT live tested |
| 📐 | Design complete, code NOT written |
| 📝 | Design document, planning/reference |
| ⏳ | Future (depends on hardware/ecosystem) |

---

## 1. All Documents in This Directory (36 files + 4 subdirectories)

### Foundation Systems (Live Verified ✅)

| Document | Milestones | Status | Live Tested |
|----------|-----------|--------|-------------|
| `milestone-plan-three-systems.md` | 44 (A01-G05) | ✅ 44/44 VERIFIED | Yes — VERIFICATION-MATRIX.md |
| `VERIFICATION-MATRIX.md` | — | ✅ 69/69 checks passed | Yes — 2026-03-30 |
| `three-systems-runtime.md` | — | ✅ Runtime scenarios verified | Yes |
| `fleet-event-bus-architecture.md` | M-EB01–20 | ✅ 17/20 done | Yes — events flowing |
| `fleet-event-bus-audit.md` | — | ✅ Code audit complete | Yes |

### Strategic Systems (Code Exists, NOT Live Tested 🔨)

| Document | Milestones | Status | What's Missing |
|----------|-----------|--------|----------------|
| `labor-attribution-and-provenance.md` | M-LA01–08 | 🔨 744 unit tests | Live test with real agent producing stamps |
| `budget-mode-system.md` | M-BM01–06 | 🔨 Unit + integration tests | Live test: budget mode constraining real dispatch |
| `multi-backend-routing-engine.md` | M-BR01–08 | 🔨 Unit + integration tests | Live test: routing task to LocalAI vs Claude |
| `iterative-validation-and-challenge-loops.md` | M-IV01–08 | 🔨 Unit tests | Live test: challenge validating real agent work |
| `model-upgrade-path.md` | M-MU01–08 | 🔨 Unit tests, KV cache applied | Live test: shadow routing real inference |
| `storm-prevention-system.md` | M-SP01–09 | 🔨 Unit + integration tests | Live test: storm detection triggering real response |
| `integration-testing-plan.md` | W1–W8 | 🔨 23 integration tests pass | Cross-system wiring verified, not runtime |
| `context-window-awareness-and-control.md` | — | 🔨 Statusline deployed | Agent compaction protocol not built |

### Design Documents (Not Yet Implemented 📐)

| Document | Milestones | Key PO Requirement |
|----------|-----------|-------------------|
| `agent-command-center.md` | — | *"agents need a command center that will guide them"* |
| `agent-rework.md` | AR-01–20 | *"massive review and rework... make all agent start with the right data"* |
| `context-bundles.md` | CB01–05 | *"pre-injected / pre-embedded data, like the current task"* |
| `fleet-control-surface.md` | M-CS01–10 | *"I should be able to Pause and even Stop"* |
| `transpose-layer.md` | T01–T07 | *"TRANSPOSE... DATA → RICH HTML... and in reverse"* |
| `fleet-operations-protocol.md` | M61–80 | *"every manual step is a bug"* |
| `phase-a-code-delivery.md` | M61–64 | Agent push + PR on completion |
| `phase-f1-foundation-skills.md` | M81–86 | *"making it smart and tooling for the agent"* |
| `phase-f2-agent-communication.md` | M87–91 | *"WE need order and logic for when to use what"* |
| `phase-f3-irc-the-lounge.md` | M92–96 | *"setup this so I can talk with the AI messages"* |
| `phase-f4-governance-agent.md` | M97–102 | *"one agent that will keep order in all this"* |
| `skills-ecosystem.md` | M48–52 | Skills registry and per-agent assignment |
| `standards-and-discipline.md` | M44–47 | Conventional commits, shared coding standards |
| `navigability-and-traceability.md` | M57–60 | Commit ↔ task linking, trace tool |
| `observability-and-channels.md` | M53–56 | WebSocket monitor, unified dashboard |

### Planning & Vision Documents 📝

| Document | Purpose |
|----------|---------|
| `fleet-vision-architecture.md` | Code-verified system map (731 lines) |
| `fleet-vision-architecture-part2.md` | Part 2: gateway, data flow, gaps (478 lines) |
| `unified-implementation-plan.md` | Merged AR + extension → U-01 to U-38 |
| `implementation-roadmap.md` | 5-wave sequencing for strategic milestones |
| `fleet-extension-milestones.md` | 30 extension milestones (Waves 6-11) |
| `fleet-autonomy-milestones.md` | Hierarchical task management design |
| `strategic-vision-localai-independence.md` | 5-stage LocalAI offload vision |

### Subdirectories

| Directory | Files | Content | Status |
|-----------|-------|---------|--------|
| `immune-system/` | 7 docs | Doctor, diseases, detection, response, integration | ✅ Live verified |
| `teaching-system/` | 1 doc | Lessons, injection, comprehension | ✅ Live verified |
| `methodology-system/` | 8 docs | 5 stage protocols, standards, custom fields | ✅ Live verified |
| `fleet-elevation/` | 31 docs | Complete agent architecture redesign | 📐 Design only |
| `agent-rework/` | 14 docs | Pre-embed, waking, per-role heartbeats | 📐 Design only |
| `context-system/` | 8 docs | Context bundles, MCP upgrade, heartbeat pre-embed | 📐 Design only |

---

## 2. Complete Milestone Registry

### Verified Complete ✅

| Set | ID Range | Count | Document |
|-----|----------|-------|----------|
| Three Systems | A01–G05 | 44 | milestone-plan-three-systems.md |
| Event Bus | M-EB01–20 | 17/20 | fleet-event-bus-architecture.md |

### Code Exists, Not Live Tested 🔨

| Set | ID Range | Count | Document | Tests |
|-----|----------|-------|----------|-------|
| Labor Attribution | M-LA01–08 | 8 | labor-attribution-and-provenance.md | 44 unit |
| Budget Mode | M-BM01–06 | 6 | budget-mode-system.md | 93 unit |
| Multi-Backend Router | M-BR01–08 | 8 | multi-backend-routing-engine.md | 73 unit |
| Iterative Validation | M-IV01–08 | 8 | iterative-validation-and-challenge-loops.md | 178 unit |
| Model Upgrade | M-MU01–08 | 8 | model-upgrade-path.md | 130 unit |
| Storm Prevention | M-SP01–09 | 9 | storm-prevention-system.md | 90 unit |
| Cross-System Wiring | W1–W8 | 8 | integration-testing-plan.md | 23 integration |
| Session Telemetry | W8 | 1 | (in integration-testing-plan.md) | 30 unit |

### Design Complete, Not Implemented 📐

| Set | ID Range | Count | Document |
|-----|----------|-------|----------|
| Control Surface | M-CS01–10 | 7 | fleet-control-surface.md |
| Transpose Layer | T01–T07 | 7 | transpose-layer.md |
| Context Bundles | CB01–05 | 5 | context-bundles.md |
| Agent Rework | AR-01–20 | 20 | agent-rework.md + agent-rework/ |
| Standards | M44–47 | 4 | standards-and-discipline.md |
| Skills | M48–52 | 5 | skills-ecosystem.md |
| Observability | M53–56 | 4 | observability-and-channels.md |
| Traceability | M57–60 | 4 | navigability-and-traceability.md |
| Code Delivery | M61–64 | 4 | phase-a-code-delivery.md |
| Operations | M61–80 | 20 | fleet-operations-protocol.md |
| Foundation Skills | M81–86 | 6 | phase-f1-foundation-skills.md |
| Agent Communication | M87–91 | 5 | phase-f2-agent-communication.md |
| IRC/Lounge | M92–96 | 5 | phase-f3-irc-the-lounge.md |
| Governance | M97–102 | 6 | phase-f4-governance-agent.md |
| Unified Plan | U-01–38 | 38 | unified-implementation-plan.md |

### Operational Readiness (Blocked)

| ID | What | Blocker |
|----|------|---------|
| #17 | Execute one real task end-to-end | Agent CLAUDE.md not per spec |
| #18 | PM first heartbeat with Plane | Pre-embed not fully role-specific |
| #19 | AICP Stage 1 complete | LocalAI not connected to fleet |
| #20 | Fleet 24h observation | Requires #17-19 |
| #21 | Resume autonomous flow | Requires #17-20 |

---

## 3. Milestone Count — Honest

| Category | Count | Status |
|----------|-------|--------|
| Live verified ✅ | 61 | Three Systems (44) + Event Bus (17) |
| Code exists 🔨 | 56 | Strategic (47) + Wiring (8) + Telemetry (1) |
| Design only 📐 | ~133 | AR(20) + U(38) + M44-102(~59) + CS(7) + T(7) + CB(5) |
| Blocked | 5 | Operational readiness (#17-21) |
| **Total** | **~255** | **61 verified, 56 coded, ~133 designed, 5 blocked** |

---

## 4. PO Requirements — Quoted, Not Lost

Every document contains PO requirements. Key quotes that drive everything:

**On agents:**
> "every role are top tier expert of their profession" (fleet-elevation/02)
> "massive review and rework... make all agent start with the right data" (agent-rework.md)
> "agents need a command center that will guide them" (agent-command-center.md)

**On process:**
> "every manual step is a bug" (fleet-operations-protocol.md)
> "Build the safety net before the trapeze" (implementation-roadmap.md)
> "I should be able to Pause and even Stop" (fleet-control-surface.md)

**On quality:**
> "TRANSPOSE... DATA → RICH HTML... and in reverse" (transpose-layer.md)
> "making it smart and tooling for the agent and making it easy" (phase-f1)
> "WE need order and logic for when to use what" (phase-f2)
> "quote back in a document that prove we have this awareness and control" (context-window)

**On cost:**
> "the fleet cp is also going to have to keep track of the plan usage" (storm-prevention)
> "budget mode to fine-tune the spending" (budget-mode-system.md)
> "the main first mission is to make localAI functional" (strategic-vision)

**On standards:**
> "strong OOP and SRP and remember code hygiene" (agent-command-center.md)
> "do not corrupt or minimize or compress" (strategic-vision)
> "PO's words are sacrosanct" (fleet-elevation/20)

---

## 5. Critical Path — What Blocks Everything

```
BLOCKER: 0/10 agent CLAUDE.md follow fleet-elevation specs
  → Agents don't have anti-corruption rules
  → Agents don't follow stage protocol properly
  → Blocks ALL live testing

BLOCKER: Contribution flow not implemented
  → fleet_contribute MCP tool doesn't exist
  → Brain doesn't create contribution subtasks
  → Specialists can't provide input before work
  → Blocks full agent synergy

BLOCKER: Template files not deployed
  → MC_WORKFLOW.md, STANDARDS.md, MC_API_REFERENCE.md in _template/ only
  → Workers may run without workflow instructions
  → Blocks proper agent behavior

BLOCKER: Pre-embed not fully per-role
  → PM doesn't get Plane sprint data
  → Workers don't get artifact completeness
  → Blocks effective heartbeats
```

First live test requires fixing blockers 1 + 3 minimum.

BLOCKER: Ecosystem not deployed
  → 0/10 agents have role-specific MCP servers
  → 0/10 agents have specialized plugins
  → Prompt caching not enabled (90% savings available)
  → Blocks agent effectiveness and cost control

---

## 5b. New Documentation (2026-04-01)

| Document | Lines | What It Covers |
|----------|-------|---------------|
| `docs/systems/01-21` | 9,491 | 21 per-system documentation files (code-verified, high standard) |
| `docs/ARCHITECTURE.md` | 291 | Fleet-wide system map, interconnection matrix, data flows |
| `docs/systems/21-agent-tooling.md` | 439 | Per-role MCP/plugins/skills via IaC specification |
| `ecosystem-deployment-plan.md` | 454 | 15 items across 3 tiers: immediate/evaluation/strategic |
| `fleet-vision-architecture.md` + part2 | 1,209 | Code-verified system map (94 modules, 25 MCP tools) |

---

## 6. Design Document References

| Topic | Primary Design Doc | Supporting Docs |
|-------|-------------------|-----------------|
| Agent architecture | fleet-elevation/02 | agent-rework/01-14 |
| Per-role specs | fleet-elevation/05-14 | agent-rework/04-08 |
| AI behavior | fleet-elevation/20 | immune-system/02-06 |
| Cross-agent synergy | fleet-elevation/15 | agent-rework/09 |
| Agent lifecycle | fleet-elevation/23 | — |
| Delivery phases | fleet-elevation/03 | config/phases.yaml |
| Brain/orchestrator | fleet-elevation/04 | agent-rework/03 |
| Multi-fleet identity | fleet-elevation/16 | — |
| Standards framework | fleet-elevation/17 | standards-and-discipline.md |
| PO governance | fleet-elevation/18 | — |
| Flow validation | fleet-elevation/19 | — |
| Task lifecycle | fleet-elevation/21 | — |
| Tool call catalog | fleet-elevation/24 | — |
| Config reference | fleet-elevation/26 | — |
| Codebase inventory | fleet-elevation/28 | fleet-vision-architecture.md |
| Lessons learned | fleet-elevation/29 | — |
| Strategy synthesis | fleet-elevation/30 | — |
| Transition strategy | fleet-elevation/31 | — |
