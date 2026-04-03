# Work Backlog — Every Gap Consolidated

> **Every "What's Needed" from all 22 system docs, consolidated into
> one prioritized backlog. Categorized by what BLOCKS live testing vs
> what improves quality vs what's future optimization.**

---

## 1. BLOCKERS — Must Fix Before First Live Test

### B0: Agent Directory Cleanup — DONE ✅

Completed 2026-04-01. Templates in git (`_template/`), agent runtime
dirs fully untracked (71 files). `.gitignore` updated. Committed.

### B0.5: Per-Type Standards — DONE ✅

Completed 2026-04-01. 8 per-type standard docs in `docs/milestones/active/standards/`.
Master index: `agent-file-standards.md`. These gate B1-B4 and all future work.

### B0.7: Gateway Injection Order — CRITICAL DISCOVERY (2026-04-01)

**Source:** SPEC-TO-CODE §5 (divergences), gateway/executor.py:94-119, gateway/ws_server.py:335-353
**Discovery:** Gateway currently reads ONLY `CLAUDE.md` + `context/` files.
It does NOT read IDENTITY.md, SOUL.md, TOOLS.md, AGENTS.md, or HEARTBEAT.md.
The entire 8-file onion architecture injection order is NOT IMPLEMENTED.
Additionally, `ws_server.py` truncates CLAUDE.md to 2000 chars (not 4000)
and context files to 1000 chars each (not 8000).
**Work:**
1. Modify `_build_agent_context()` in both executor.py and ws_server.py
2. Read ALL 8 files in correct order: IDENTITY→SOUL→CLAUDE→TOOLS→AGENTS→context→HEARTBEAT
3. Apply correct char limits: CLAUDE.md=4000, context files=8000 each
4. Make injection order configurable via agent.yaml or config
**Why blocker:** Without this, agents get NO identity, NO values, NO tools
documentation, NO synergy knowledge, NO heartbeat protocol. Writing B1-B4
files is pointless if the gateway doesn't inject them.
**Effort:** 2-4 hours (modify 2 Python files + test)

### B0.8: Contamination Cleanup — DONE ✅

Completed 2026-04-01. Removed all fabricated specifics:
- Budget modes: 6 invented modes → tempo setting only
- Router: uses backend_mode from FleetControlState (7 combos)
- CostTicker/cost envelopes: removed (fabricated USD tracking)
- budget_mode removed from incident reports, labor stamps, storm system
- All docs cleaned (~40 files). 1730 tests pass.

### B0.9: Settings Wiring — OCMC → Brain → Gateway

**Source:** fleet-vision-architecture §22, fleet-master-diagrams §10-11
**What works:** work_mode gates dispatch ✓, cycle_phase filters agents ✓
**What's not wired:**
1. backend_mode → router (code ready, orchestrator doesn't pass it yet)
2. budget_mode → tempo (mode definitions TBD, CRON sync TBD)
3. Gateway CRON sync when tempo changes
4. LocalAI health check in dispatch loop
**Why blocker:** Settings on OCMC must actually DO things. PO changes
backend_mode to "claude" → router must stop sending to LocalAI.
PO pauses → fleet must actually pause.
**Effort:** 4-8 hours

### B1: Agent CLAUDE.md (0/10 per spec)

**Standard:** `standards/claude-md-standard.md` — READ THIS FIRST
**Source:** SPEC-TO-CODE §1.2, fleet-elevation/02+05-14+20, AR-10
**Systems:** All agents
**Work:** Write role-specific CLAUDE.md for all 10 agents following the standard:
- 8 required sections in order (Core Responsibility → Anti-Corruption)
- Max 4000 chars (budget allocation in standard)
- Per-role content from fleet-elevation/{role} specs
- Context awareness (both countdowns: context remaining + rate limit)
- Annotated example in standard (Architect, ~2810 chars)

**Read before writing:** standards/claude-md-standard.md (structure), fleet-elevation/{role number} (content), fleet-elevation/20 (anti-corruption rules)
**Validate after writing:** scripts/validate-agents.sh
**Effort:** 20-40 hours (2-4h per agent × 10 agents)

### B2: Agent HEARTBEAT.md (1/10 per spec)

**Standard:** `standards/heartbeat-md-standard.md` — READ THIS FIRST
**Source:** SPEC-TO-CODE §2, fleet-elevation/05-14, agent-rework/04-08
**Systems:** All agents
**Work:** 5 unique heartbeats per standard:
- PM: full template in standard (task assignment, contribution check, gate routing, sprint)
- Fleet-ops: full template in standard (7-step REAL review, trail verification, board health)
- Architect: full template in standard (stage-driven, design contributions, architecture health)
- DevSecOps: full template in standard (security contributions, PR review, security_hold, crisis)
- Worker: template with per-role variations table (engineer/devops/QA/writer/UX/accountability)

**Validate after writing:** scripts/validate-agents.sh
**Effort:** 5-10 hours

### B3: Template Files + IaC Scripts

**Standard:** `standards/iac-mcp-standard.md` — READ THIS FIRST
**Source:** SPEC-TO-CODE §1.1, fleet-vision-architecture-part2 §27
**Work:** Build the 6 IaC scripts defined in the standard:
- scripts/provision-agents.sh (master provisioning)
- scripts/setup-agent-tools.sh (mcp.json from config)
- scripts/install-plugins.sh (Claude-Mem, Context7 per role)
- scripts/generate-tools-md.sh (TOOLS.md from code + call trees)
- scripts/generate-agents-md.sh (AGENTS.md from synergy matrix)
- scripts/validate-agents.sh (validation against all standards)
Plus Makefile targets: provision, setup-tools, validate-agents, setup
**Effort:** 4-8 hours

### B4: Agent.yaml Updates

**Standard:** `standards/agent-yaml-standard.md` — READ THIS FIRST
**Source:** SPEC-TO-CODE §2 (AR-09)
**Work:** Write all 10 agent.yaml with 14 required fields per standard:
name, display_name, fleet_id, fleet_number, username, type, mode, backend,
model, mission, capabilities, roles.primary, roles.contributes_to, heartbeat_config
Per-role values table in standard.
**Validate after writing:** scripts/validate-agents.sh
**Effort:** 2-4 hours

---

## 2. HIGH PRIORITY — Needed for Effective Fleet Operation

### H1: Contribution Flow (fleet_contribute)

**Source:** fleet-elevation/15, SPEC-TO-CODE §1.3, INTEGRATION.md Flow 6
**Systems:** MCP Tools, Orchestrator, Context, Methodology
**Work:**
1. Build `fleet_contribute` MCP tool
2. Build brain logic: task enters REASONING → create parallel contribution subtasks
3. Build `fleet_request_input` MCP tool
4. Pre-embed contributions into worker task context
**Chain builder exists:** `build_contribution_chain()` in event_chain.py
**Effort:** 8-16 hours

### H2: Session Telemetry Wired to Runtime

**Source:** docs/systems/19-session, every system doc mentions "W8 not wired"
**Systems:** Labor, Budget, Storm, Health (all waiting for real data)
**Work:** Orchestrator calls `to_labor_fields()`, `to_claude_health()`, `to_storm_indicators()`, `to_cost_delta()` from session_telemetry.py
**Adapter exists:** 230 lines, 30 tests. Just needs wiring.
**Effort:** 2-4 hours

### H3: Full Pre-Embed per Role (AR-01)

**Source:** agent-rework/02, docs/systems/19-session, SPEC-TO-CODE §2
**Systems:** Context, Orchestrator
**Work:**
- PM gets Plane sprint data in pre-embed
- Workers get artifact completeness + suggested readiness
- All agents get contributions received (after H1)
**Effort:** 4-8 hours

### H4: Standards Injection (AR-14)

**Source:** fleet-elevation/17, docs/systems/09-standards
**Systems:** Standards, Context
**Work:** Inject relevant standards into agent context based on current task artifact type. Agent producing an analysis_document should see analysis_document standard in context.
**Effort:** 2-4 hours

### H5: Silent Heartbeats — Brain Interception Layer

**Source:** fleet-elevation/23, docs/systems/06-agent-lifecycle §0, 22-agent-intelligence
**Systems:** Lifecycle, Orchestrator, Gateway
**Architecture (2026-04-01):** Cron NEVER stops. Brain INTERCEPTS before Claude call:
- Gateway cron fires for agent (every configured interval)
- Brain checks lifecycle state BEFORE making Claude call
- IDLE/SLEEPING → brain evaluates deterministically (FREE):
  mentions? tasks? contributions? directives? role triggers?
- Wake trigger found → fire real heartbeat with strategic config
- Nothing found → silent heartbeat OK, $0
- Agent is always on call. Brain is the filter.
**Data structures exist:** consecutive_heartbeat_ok, last_heartbeat_data_hash in AgentState
**Work:**
1. Build brain interception hook between cron firing and Claude call
2. Implement `_evaluate_sleeping_agent()` (designed in fleet-elevation/23)
3. Implement `decide_claude_call()` for strategic config on wake
4. Optional: per-agent cron interval adjustment via gateway_client.py
**Effort:** 4-8 hours
**Impact:** ~70% cost reduction on idle fleet

### H6: Ecosystem Tier 1

**Source:** ecosystem-deployment-plan.md
**Work:**
- E-01: Enable prompt caching (90% savings, config change)
- E-02: Install Claude-Mem plugin (cross-session memory)
- E-03: Install Context7 plugin (library docs for architect+engineer)
- E-04: Filesystem MCP per agent (structured file ops)
**Effort:** 1-2 hours
**Impact:** 40-60% cost reduction, better agent awareness

### H7: Qwen3.5 Models

**Source:** docs/systems/16-models §8
**Work:** Download Qwen3.5-4B and Qwen3.5-9B GGUF. Create model YAML configs. Run `make optimize-models`. Benchmark against fleet prompts.
**Effort:** 2-4 hours

---

## 3. MEDIUM PRIORITY — Quality Improvements

### M1: Missing Disease Detections (7 of 11)

**Source:** docs/systems/02-immune-system §8
**Work:** Implement: abstraction, code_without_reading, scope_creep, cascading_fix, context_contamination, not_listening, compression
**Depends on:** Some need contribution flow (contribution_avoidance, synergy_bypass)
**Effort:** 8-16 hours

### M2: Missing Artifact Renderers (5)

**Source:** docs/systems/10-transpose §10
**Work:** Add renderers for: security_assessment, qa_test_definition, ux_spec, documentation_outline, compliance_report
**Effort:** 4-8 hours

### M3: Challenge → Review Flow Connection

**Source:** docs/systems/15-challenge §9
**Work:** Challenge results available to fleet-ops during review. Trainee tier triggers challenge before approval.
**Effort:** 4-8 hours

### M4: Cross-Reference Execution

**Source:** docs/systems/18-notifications §10
**Work:** `generate_cross_refs()` returns refs but no caller executes them. Wire into event chain execution.
**Effort:** 2-4 hours

### M5: Event Cleanup

**Source:** docs/systems/04-event-bus §10
**Work:** JSONL grows without bound. Implement rotation/archival strategy.
**Effort:** 2-4 hours

### M6: HeartbeatBundle ↔ Preembed Unification

**Source:** docs/systems/19-session §7
**Work:** heartbeat_context.py and preembed.py produce overlapping data. Unify into one path.
**Effort:** 4-8 hours

### M7: Phase Gate Enforcement

**Source:** docs/systems/01-methodology §10, SPEC-TO-CODE §1.1
**Work:** Orchestrator enforces PO approval at phase boundaries. `is_phase_gate()` exists, enforcement doesn't.
**Effort:** 2-4 hours

### M8: Escalation Logic

**Source:** docs/systems/22-agent-intelligence §2
**Work:** Dynamic escalation of effort/model/source/session based on complexity, confidence, budget, outcomes. `decide_claude_call()` in orchestrator.
**Effort:** 4-8 hours

---

## 4. LOW PRIORITY — Future Optimization

### L1: Per-Agent Autonomy Config

**Source:** docs/systems/22-agent-intelligence §1
**Work:** `config/agent-autonomy.yaml` with per-role thresholds and wake triggers
**Effort:** 2-4 hours

### L2: OpenRouter Client

**Source:** docs/systems/14-router §9, ecosystem plan
**Work:** Build client for 29 free models
**Effort:** 4-8 hours

### L3: The Lounge Deployment (M92-96)

**Source:** docs/systems/18-notifications §10
**Work:** Deploy web IRC client for PO visibility
**Effort:** 2-4 hours

### L4: LocalAI RAG → Fleet

**Source:** docs/systems/22-agent-intelligence §3.3, ecosystem plan E-09
**Work:** Wire AICP rag.py + kb.py into fleet agent context
**Effort:** 8-16 hours

### L5: AICP ↔ Fleet Bridge

**Source:** docs/systems/14-router §9, ecosystem plan E-12
**Work:** router_unification.py bridge
**Effort:** 8-16 hours

### L6: FleetControlBar Frontend (M-CS01-10)

**Source:** docs/systems/05-control-surface §10
**Work:** TSX component in DashboardShell.tsx header
**Effort:** 8-16 hours

### L7: Multi-Fleet Identity

**Source:** SPEC-TO-CODE §1.3, fleet-elevation/16
**Work:** Agent naming, shared Plane, cross-fleet coordination
**Depends on:** Second machine
**Effort:** 8-16 hours

### L8: TurboQuant Integration

**Source:** docs/systems/16-models §8.3
**Work:** When llama.cpp merges (Q3 2026), update model YAMLs
**Depends on:** llama.cpp merge
**Effort:** 1-2 hours (config only)

### L9: Agent Teams Evaluation

**Source:** docs/systems/21-agent-tooling §8.4, ecosystem plan E-11
**Work:** Enable `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`, pilot on one epic
**Effort:** 4-8 hours

### L10: Batch API

**Source:** ecosystem plan E-10
**Work:** Route non-urgent work through Batch API (50% savings)
**Effort:** 2-4 hours

---

---

## 5. DISCOVERED GAPS (2026-04-02 Vision Mapping)

Full details: `fleet-vision-architecture.md §33` (23 categories, 130+ pieces)

### Code Bugs
- **B-01:** fleet_commit gated to WORK only (should be stages 2-5)
- **B-02:** Gateway truncates CLAUDE.md to 2000 chars (spec: 4000)
- **B-03:** Gateway only reads 3 of 8 agent files
- **B-04:** backend_mode not passed to router
- **B-05:** budget_mode definitions empty

### Missing Layers (entire systems not built)
- **Contribution system:** 10 pieces (fleet_contribute, brain module, synergy config, pre-embed, completeness, dispatch gate, anti-patterns)
- **Phase system:** 9 pieces (fleet_gate_request, fleet_phase_advance, phase_system.py, phases.yaml, standards injection, contribution requirements)
- **Trail & audit:** 6 pieces (trail_recorder.py, 30+ event types, board memory storage, consumers)
- **Autocomplete chain:** 8 pieces (autocomplete.py, chain assembly, verbatim anchoring, contribution embedding, phase standards embedding)
- **Session management:** brain Step 10 (session_manager.py, two countdowns, aggregate math, smart artifacts dumping, compaction stagger)
- **Brain idle evaluation:** heartbeat_gate.py (~70% cost reduction)

### Missing Ecosystem Deployment
- Skills: 85 exist, 0 deployed to agent workspaces
- Plugins: Claude-Mem + Context7 designed, 0 installed
- Commands: /plan, /compact, /context — 0 agents trained
- Prompt caching: 90% savings available, not enabled
- Per-agent MCP servers: agent-tooling.yaml defined, 0 deployed
- Agent Teams: not evaluated

### Missing Anti-Corruption
- Line 1 (structural prevention): 0% built
- Line 2 (detection): 36% built (4/11 diseases)
- Line 3 (correction): mechanism exists, 7 diseases can't trigger it
- Readiness regression: not built

### Missing Operational Protocols
- Cowork (multiple agents on one task): not built
- Transfer (task handoff): not built
- Notification routing: 2 IRC channels missing, 2 ntfy topics missing

---

## 6. Summary

| Category | Items | Total Effort | Status |
|----------|-------|-------------|--------|
| **BLOCKERS** (must fix) | B0-B4 + B-01 to B-05 | 35-71 hours | B0 ✅, B0.5 ✅, B0.8 ✅, rest pending |
| **HIGH** (needed for operation) | H1-H7 | 23-46 hours | Pending |
| **MEDIUM** (quality) | M1-M8 | 30-60 hours | Pending |
| **LOW** (future) | L1-L10 | 47-98 hours | Pending |
| **DISCOVERED** (§33 gaps) | 23 categories | ~200-400 hours | Identified 2026-04-02 |
| **TOTAL** | **54+ items** | **~335-675 hours** | |

**Path to live: 24 steps, 8 phases, 132-240 hours, 6-12 weeks.**
See `path-to-live.md` for ordered work breakdown.

**Complete gap registry:** `fleet-vision-architecture.md §33`
**Complete vision:** `fleet-vision-architecture.md` (43 sections, 4400+ lines)
**Complete diagrams:** `fleet-master-diagrams.md` (18 diagrams)

**Quality gate:** All per-type standards in `docs/milestones/active/standards/` must be followed.
No agent file committed without passing `scripts/validate-agents.sh`.
