# Path to Live — From Documentation to Running Fleet

**Date:** 2026-04-02
**Status:** PLANNING — ordered work from current state to live operation
**Updated:** Expanded from 12 to 24 steps based on full vision mapping (§27-§43)
**Depends on:** fleet-vision-architecture.md §33 (complete gap registry)

---

## 1. Where We Are (2026-04-02)

### Built and Tested (code exists, unit tested)
- 94 core modules across 20 systems
- 1800+ unit tests, 23 integration tests
- Orchestrator runs (9-step cycle, target 16 — brain spec in fleet-elevation/04)
- Gateway integration (WebSocket RPC, prune/compact/inject)
- Event bus (47 event types, 6 surfaces, routing)
- Methodology (5 stages, stage gating on MCP tools)
- Immune system (4/11 detections, teaching, self-healing)
- 25 MCP tools (stage-gated, event chains)
- Budget system (tempo setting + real OAuth quota monitoring)
- Storm prevention (9 indicators, circuit breakers)
- Agent lifecycle (ACTIVE→IDLE→SLEEPING, content-aware)
- Session telemetry adapter (W8, 230 lines, 30 tests — NOT WIRED)
- Backend router (7 backend mode combos — NOT WIRED to orchestrator)
- B0 complete (agent directory cleanup)
- B0.5 complete (8 per-type standards)
- B0.8 complete (contamination cleanup)

### Standards Created (quality gates for all work below)
- 8 per-type standard docs in `docs/milestones/active/standards/`
- Master index: `agent-file-standards.md`
- Rule: read standard FIRST, validate AFTER

### Vision Documentation (enables correct implementation)
- 43-section fleet-vision-architecture.md (4400+ lines)
- 18 diagrams in fleet-master-diagrams.md
- Complete gap registry (§33): 23 categories, 130+ pieces, ~200-400h
- Complete flow documentation: task lifecycle, OCMC/Brain/Gateway protocol,
  contribution flow, review flow, cross-cutting scenarios
- Anti-corruption 3-line defense, autocomplete chain engineering,
  phase system, trail system, notification routing, brain layers 2+3

### NOT Built (see §33 for complete list)
- 5 MCP tools (fleet_contribute, fleet_request_input, fleet_gate_request,
  fleet_phase_advance, fleet_transfer)
- 5 existing tools need chain elevation
- 8 brain modules (contributions, session_manager, heartbeat_gate,
  phase_system, trail_recorder, chain_registry, logic_engine, autocomplete)
- Autocomplete chain engineering (core design principle)
- Phase system (delivery phases + standards + gates)
- Trail & audit system
- Skills/plugins/commands not deployed to agents
- Prompt caching not enabled
- Agent files: 0/70+ written to spec
- 6 IaC scripts not built
- 7 of 11 disease detections not built
- Brain idle evaluation not built
- Readiness regression not built
- Cowork + transfer protocols not built
- Stage gating bug (fleet_commit WORK-only, should be stages 2-5)

### Never Done
- ONE live test with a real agent doing real work through full lifecycle

---

## 2. The Ordered Path (24 Steps)

### PHASE A: FOUNDATION (Steps 1-4)

#### Step 1: Fix Gateway Injection (B0.7) — CRITICAL

**What:** Modify `_build_agent_context()` in executor.py AND ws_server.py.
- Read ALL 8 files in order: IDENTITY→SOUL→CLAUDE→TOOLS→AGENTS→context→HEARTBEAT
- Fix char limits: CLAUDE.md=4000 (was 2000), context=8000 each (was 1000)
- Make injection order configurable or document fixed order

**Why first:** Writing agent files is pointless if gateway doesn't inject them.
**Time:** 2-4 hours.

#### Step 2: Fix Stage Gating Bug (B-01)

**What:** In mcp/tools.py, change `fleet_commit` from WORK_ONLY to stages 2-5
(analysis, investigation, reasoning, work). Only CONVERSATION blocks commits.
`fleet_task_complete` correctly stays WORK-only.

**Why:** Agents produce artifacts (analysis docs, investigation reports, design
artifacts) in stages 2-4. They can't commit those with current gating.
**Time:** 1-2 hours.

#### Step 3: Build IaC Scripts (B3)

**Standard:** `standards/iac-mcp-standard.md`

```
scripts/provision-agents.sh      — template → agent dirs
scripts/setup-agent-tools.sh     — per-agent mcp.json from config
scripts/install-plugins.sh       — Claude-Mem, Context7 per role
scripts/generate-tools-md.sh     — TOOLS.md from code + call trees
scripts/generate-agents-md.sh    — AGENTS.md from synergy matrix
scripts/validate-agents.sh       — validate ALL files against standards
```

Plus Makefile targets: `make provision`, `make setup-tools`, `make validate`, `make setup`
**Time:** 4-8 hours.

#### Step 4: Deploy Ecosystem Tier 1 (E-01 to E-04)

**What:** Config changes only, no code, zero risk:
- E-01: Enable prompt caching (`cacheRetention` per agent) → 90% savings
- E-02: Install Claude-Mem (all agents) → cross-session memory
- E-03: Install Context7 (architect + engineer) → library docs
- E-04: Filesystem MCP (per agent-tooling.yaml) → structured file ops

**Why early:** 40-60% cost reduction before agents start burning tokens.
**Time:** 1-2 hours.

### PHASE B: AGENT IDENTITY (Steps 5-9)

#### Step 5: Write agent.yaml ×10 (B4)

**Standard:** `standards/agent-yaml-standard.md`
14 required fields per agent. Fleet identity, roles, capabilities.
**Validate:** `scripts/validate-agents.sh`
**Time:** 2-4 hours.

#### Step 6: Write IDENTITY.md + SOUL.md ×10

**Standard:** `standards/identity-soul-standard.md`
Inner layer files: fleet identity, top-tier expert definition,
10 anti-corruption rules, per-role values, humility.
**Time:** 4-8 hours.

#### Step 7: Write Agent CLAUDE.md ×10 (B1 — HEAVIEST WORK)

**Standard:** `standards/claude-md-standard.md`
8 required sections, max 4000 chars, per-role content from fleet-elevation specs.
Must include: stage-specific tool/skill/command recommendations,
anti-corruption summary, context awareness protocol.
**Read before each:** standard, fleet-elevation/{role}, fleet-elevation/20, fleet-elevation/15.
**Time:** 20-40 hours (2-4h per agent × 10).

#### Step 8: Write HEARTBEAT.md ×5 (B2)

**Standard:** `standards/heartbeat-md-standard.md`
5 unique types: PM, Fleet-ops (7-step review), Architect, DevSecOps,
Worker (with per-role variation table for engineer/devops/QA/writer/UX/accountability).
**Time:** 5-10 hours.

#### Step 9: Generate TOOLS.md + AGENTS.md ×10

Via IaC scripts (from Step 3):
- `scripts/generate-tools-md.sh` — chain-aware tool reference per role
  Includes: MCP tools, skills, built-in commands, stage recommendations
- `scripts/generate-agents-md.sh` — synergy matrix per role
  Includes: who contributes what, when to reach out, collaboration patterns

**Time:** 1-2 hours (script execution + review).

### PHASE C: BRAIN EVOLUTION (Steps 10-14)

#### Step 10: Build Autocomplete Chain Builder

**What:** `fleet/core/autocomplete.py`
- `assemble_task_chain(agent, task, contributions, phase_standards)`
- `assemble_heartbeat_chain(agent, fleet_state, tasks, messages)`
- `inject_verbatim_anchors(chain, verbatim)` — verbatim at multiple points
- `inject_contributions(chain, contributions)` — colleague inputs visible

Update `context_writer.py` to use autocomplete.py instead of raw concatenation.

**Why now:** Every step after this depends on correct context chain assembly.
Agents get data in the ORDER that drives correct behavior.
**Time:** 4-8 hours.

#### Step 11: Build Trail Recorder

**What:** `fleet/core/trail_recorder.py`
- `record_trail_event(task_id, event_type, details, agent)`
- `get_trail(task_id)` → chronological list
- `check_trail_completeness(task_id)` → % complete
- 30+ trail event types enum
- Board memory storage with tags: trail + task:{id} + type

Wire into every MCP tool call and brain decision.

**Why now:** Trail enables review (fleet-ops Step 4) and accountability.
Without trail, fleet-ops can't verify agent work.
**Time:** 4-8 hours.

#### Step 12: Wire Fleet Settings (B0.9)

**What:**
1. `backend_mode → router` — orchestrator passes to route_task()
2. `budget_mode → tempo` — tempo_multiplier to cycle interval + CRONs
3. Gateway CRON sync — update heartbeat configs when tempo changes
4. LocalAI health check — router checks localhost:8090/v1/models
5. Verify work_mode propagation end-to-end

**Time:** 4-8 hours.

#### Step 13: Enhance Pre-Embed Per Role (AR-01)

Update role_providers.py:
- PM: Plane sprint data, unassigned count, pending gates
- Fleet-ops: full approval context (requirement + criteria + PR + trail)
- Architect: tasks needing design (with full context)
- Workers: artifact completeness + suggested readiness + contributions
- All: context % + rate limit % (informational)

**Time:** 4-8 hours.

#### Step 14: Wire Session Telemetry (H2)

**What:** Orchestrator calls session_telemetry.py adapter methods:
- `to_labor_fields()` → LaborStamp
- `to_claude_health()` → ClaudeHealth (quota tracking)
- `to_storm_indicators()` → StormMonitor (context_pressure, quota_pressure)
- `to_cost_delta()` → BudgetMonitor

Adapter exists (230 lines, 30 tests). Just needs wiring.
**Time:** 2-4 hours.

### PHASE D: FIRST LIVE TEST (Step 15)

#### Step 15: Minimum Viable Live Test

```
1. Create task on OCMC (manually)
2. Set: agent=software-engineer, stage=work, readiness=99
3. Set: requirement_verbatim="Add a README.md to fleet/core/"
4. Start orchestrator daemon
5. Orchestrator dispatches task to agent
6. Agent receives full autocomplete chain context
7. Agent reads context → follows CLAUDE.md protocol
8. Agent calls fleet_commit → fleet_task_complete
9. Task moves to review, trail recorded
10. Fleet-ops heartbeats → sees pending approval → REAL review
11. Fleet-ops reviews (7 steps) → approves with reasoning
12. Brain transitions REVIEW → DONE
13. Event chain fires to all 6 surfaces
14. Verify: IRC, Plane, ntfy, trail, labor stamp all correct
```

**Tests:** Dispatch, agent identity (onion injection), stage protocol,
MCP tools, event chains, approval flow, autocomplete effectiveness,
trail recording, settings propagation.

**Skips:** Contribution flow, PM assignment, stage progression
from conversation→work, session management, brain evaluation.

**Time:** 2-4 hours to set up + observe + iterate.

### PHASE E: CROSS-AGENT SYNERGY (Steps 16-18)

#### Step 16: Build Contribution Flow (H1)

**Standard:** `standards/brain-modules-standard.md`

1. Build `fleet_contribute` MCP tool (12+ chain operations)
2. Build `fleet_request_input` MCP tool
3. Build `fleet/core/contributions.py` — brain creates contribution tasks
   per synergy matrix when task enters REASONING
4. Build `config/synergy-matrix.yaml` — configurable contribution rules
5. Update pre-embed: "INPUTS FROM COLLEAGUES" section in autocomplete chain
6. Build contribution completeness checking (all required received?)
7. Wire dispatch gate: block until required contributions received

**Time:** 8-16 hours.

#### Step 17: Build Phase System

1. Build `fleet_gate_request` MCP tool (8+ chain operations)
2. Build `fleet_phase_advance` MCP tool
3. Build `fleet/core/phase_system.py` — phase advancement + standards
4. Create `config/phases.yaml` — PO defines quality bars per phase
5. Wire `check_phase_standards()` into dispatch gates
6. Wire phase-aware standards injection into autocomplete chain
7. Wire phase-aware contribution requirements

**Time:** 4-8 hours.

#### Step 18: Build Session Management (Brain Step 10)

1. Build `fleet/core/session_manager.py`
2. Two parallel countdowns: context remaining + rate limit session
3. Per-agent context evaluation (needs context? over threshold? dump?)
4. Aggregate fleet math (5×200K = 1M on rollover risk)
5. Progressive rate limit awareness (85% prepare, 90% force)
6. Smart artifacts dumping (heavy context → synthesized artifact)
7. Compaction staggering (don't compact all 10 agents at once)

**Time:** 4-8 hours.

### PHASE F: FULL LIFECYCLE TEST (Step 19)

#### Step 19: Full Lifecycle Live Test

```
1. PM heartbeats → sees unassigned task → assigns with ALL fields
2. Engineer heartbeats → sees task in conversation stage
3. Engineer asks questions via fleet_chat → PO clarifies
4. Stage advances: conversation → analysis → investigation → reasoning
5. At each stage: agent produces artifact, fleet_commit saves it
6. Task enters REASONING → brain creates contribution subtasks:
   - architect: design_input
   - qa-engineer: qa_test_definition
   - devsecops: security_requirement (if applicable)
7. Contributions arrive → pre-embedded in engineer's autocomplete chain
8. Engineer plans → references verbatim + contributions → readiness ~90%
9. fleet_gate_request → PO confirms → readiness 99
10. Engineer implements → fleet_commit × N → fleet_task_complete
11. Trail: every action recorded (30+ event types)
12. Challenge engine evaluates (if wired)
13. Fleet-ops reviews → 7-step REAL review against verbatim + trail
14. Fleet-ops approves → DONE → event chain fires to all 6 surfaces
15. Plane updated, IRC notified, ntfy to PO, trail complete
16. Parent task evaluated (if this was a subtask)
```

**Time:** 4-8 hours to observe + iterate. Requires all previous steps.

### PHASE G: HARDENING (Steps 20-22)

#### Step 20: Build Brain Idle Evaluation (H5)

**What:** `fleet/core/heartbeat_gate.py`
When agent has `brain_evaluates=True` (after 1 HEARTBEAT_OK):
- Brain evaluates wake triggers in Python ($0, no Claude call):
  - Direct mention? Task assigned? Contribution? Directive? Role trigger?
- Wake trigger found → fire real heartbeat with strategic config
- Nothing found → silent OK

**Impact:** ~70% cost reduction on idle fleet.
**Time:** 4-8 hours.

#### Step 21: Expand Disease Detections (M1)

Implement 7 missing detections in doctor.py:
- abstraction, code_without_reading, scope_creep, cascading_fix,
  context_contamination, not_listening, compression
Plus 2 new: contribution_avoidance, synergy_bypass

**Time:** 8-16 hours.

#### Step 22: Build Readiness Regression + Cowork + Transfer

Three operational protocols:
1. **Readiness regression:** mc.update_task regression on rejection/disease,
   event chain, context refresh with feedback
2. **Cowork:** owner vs coworker permissions, trail attribution
3. **Transfer:** fleet_transfer tool, context packaging, handoff

**Time:** 8-16 hours.

### PHASE H: ECOSYSTEM & OPTIMIZATION (Steps 23-24)

#### Step 23: Deploy Ecosystem Tier 2

After live testing confirms base works:
- E-05-07: Per-agent MCP servers (GitHub, Playwright, Docker)
- E-08: Per-agent skills from config/agent-tooling.yaml
- E-09: LocalAI RAG → fleet (wire AICP rag.py + kb.py)
- E-10: Batch API for non-urgent work (50% savings)
- Evaluate: E-11 Agent Teams pilot on one multi-agent task

**Time:** 8-16 hours.

#### Step 24: 24-Hour Fleet Observation

Operational readiness — fleet runs autonomously for 24 hours:
- PO monitors via Plane + IRC + ntfy
- Storm prevention detects and responds to issues
- Budget system tracks and constrains costs
- Session management handles rate limit windows across agents
- Immune system detects and corrects diseases (now 11/11)
- Brain evaluation prevents idle costs (~70% savings)
- All agents follow per-type standards
- Contributions flow between specialists
- Reviews are REAL (7-step, no rubber stamps)
- Trail is complete for every task

**Time:** 24 hours observation.

---

## 3. What We Skip (For Now)

- **Brain Layer 2 (chain registry)** — can operate with direct calls first
- **Brain Layer 3 (logic engine)** — hardcoded gates work for MVP
- **Multi-fleet identity** — needs second machine
- **AICP ↔ Fleet bridge** — optimize after base works
- **LocalAI v4.0 agents** — evaluate after base works
- **Dual GPU / TurboQuant / cluster peering** — hardware dependent
- **OpenRouter free tier client** — after LocalAI routing proven
- **Notification channels #gates + #contributions** — IRC works, optimize later
- **5 missing artifact renderers** — build as needed per role
- **Agent Teams full integration** — pilot in Tier 2, full after

---

## 4. Documentation That Enables Each Step

| Step | Standard | Design Docs | Vision §§ |
|------|----------|-------------|-----------|
| 1. Gateway injection | — | — | §28.4, §33.2-3 |
| 2. Stage gating fix | — | — | §33.1 |
| 3. IaC scripts | iac-mcp-standard.md | fleet-elevation/02 | §33.19 |
| 4. Ecosystem Tier 1 | — | ecosystem-deployment-plan | §34.6 |
| 5. agent.yaml | agent-yaml-standard.md | fleet-elevation/16 | — |
| 6. IDENTITY+SOUL | identity-soul-standard.md | fleet-elevation/02,20 | §39, §40 |
| 7. CLAUDE.md | claude-md-standard.md | fleet-elevation/02,05-14,20 | §34.5, §39.5 |
| 8. HEARTBEAT.md | heartbeat-md-standard.md | agent-rework/04-08 | §31 |
| 9. TOOLS+AGENTS | tools-agents-standard.md | fleet-elevation/24 | §34.1-3 |
| 10. Autocomplete | context-files-standard.md | fleet-elevation/20 | §36 |
| 11. Trail | brain-modules-standard.md | fleet-elevation/04 | §38 |
| 12. Wire settings | — | fleet-master-diagrams §10-11 | §28.5, §29 |
| 13. Pre-embed | context-files-standard.md | agent-rework/02 | §27.5 |
| 14. Session telemetry | — | — | §35.8-9 |
| 15. MVP test | — | — | §27 |
| 16. Contributions | brain-modules-standard.md | fleet-elevation/15 | §30 |
| 17. Phase system | — | fleet-elevation/03 | §37 |
| 18. Session mgmt | brain-modules-standard.md | System 22 §4.7 | §35 |
| 19. Full test | — | agent-rework/13 | §27, §31 |
| 20. Brain evaluation | brain-modules-standard.md | fleet-elevation/23 | §33.21 |
| 21. Disease detections | — | — | §33.16 |
| 22. Regression+cowork | — | — | §41 |
| 23. Ecosystem Tier 2 | iac-mcp-standard.md | ecosystem-deployment-plan | §34.6 |
| 24. 24h observe | — | — | §32 |

---

## 5. Estimated Timeline

| Phase | Steps | Work | Hours | Cumulative |
|-------|-------|------|-------|-----------|
| **A: Foundation** | 1-4 | Gateway fix + stage fix + IaC + Tier 1 | 8-16h | 8-16h |
| **B: Agent Identity** | 5-9 | All 70+ agent files written to spec | 32-64h | 40-80h |
| **C: Brain Evolution** | 10-14 | Autocomplete + trail + settings + pre-embed + telemetry | 18-36h | 58-116h |
| **D: First Test** | 15 | MVP live test | 2-4h | 60-120h |
| **E: Cross-Agent** | 16-18 | Contributions + phases + session mgmt | 16-32h | 76-152h |
| **F: Full Test** | 19 | Full lifecycle test | 4-8h | 80-160h |
| **G: Hardening** | 20-22 | Brain eval + diseases + regression/cowork | 20-40h | 100-200h |
| **H: Ecosystem** | 23-24 | Tier 2 + 24h observation | 32-40h | 132-240h |

**Realistic timeline:** 6-12 weeks of focused work.

**The heaviest work is Phase B** (agent identity files — 32-64 hours).
Each CLAUDE.md must be written with deep understanding of the role,
methodology, contribution model, autocomplete chain, anti-corruption rules,
skills, commands, and stage-specific behavior. This is NOT template filling.

**The most impactful work is Phase C** (brain evolution — 18-36 hours).
Autocomplete chain engineering, trail recording, settings wiring, and
pre-embed enhancement make everything else work correctly.

**Quality gate:** Every step validates against its per-type standard.
No file committed without passing `scripts/validate-agents.sh`.
Standards FIRST, then build. Read the design docs. Read the code.
