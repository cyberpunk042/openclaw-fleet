# Missing Plans Inventory — 24 Plans Not Yet Written

**Date:** 2026-04-02
**Context:** 825 milestones compressed into 6 plans. This document
inventories the 24 missing plans that need to be written before
implementation can proceed correctly.

**Written (6):**
- plan-01: Safety + Memory (claude-mem, safety-net, pyright-lsp, hooks)
- plan-02: Methodology + Skills (Superpowers, skill deployment)
- plan-03: MCP Servers (Context7, security, pytest, Plane, GitHub)
- plan-04: Hooks Infrastructure (Tier 1 + Tier 2)
- plan-05: Knowledge Map Navigator (navigator module, integrations)
- plan-06: Agent Files (70+ files — LAST)

---

## Missing Plans

### 7. Brain Architecture Evolution
7 missing orchestrator steps (1b event queue, 3b gate processing,
4b contribution management, 9 cross-task propagation, 10 session
management, 11 extended health+budget, 12 extended directives).
chain_registry.py (Layer 2 event-driven). logic_engine.py (Layer 3
rule-based configurable gates). The 9→16 step brain redesign.
**Source:** §33.4, fleet-elevation/04, System 7

### 8. Contribution System Wiring
10 pieces. fleet_contribute tool exists but: brain creating subtasks
at reasoning stage, dispatch gate blocking until contributions received,
PM notification when all arrive, pre-embed contributions into worker
context, build_contribution_chain() wiring, contribution completeness
checking, anti-pattern detection (siloed work, ghost contributions).
**Source:** §33.5, §30, fleet-elevation/15, System 7

### 9. Trail System Wiring
trail_recorder.py exists but: wire into all 29 MCP tools (every tool
call → trail event), wire into orchestrator (dispatch, transitions,
doctor), trail completeness checking in fleet-ops review (Step 4),
accountability generator consuming trail, trail reconstruction from
board memory.
**Source:** §33.7, §38, System 13

### 10. Storm Prevention Deployment
Wave 1 M-SP01 to M-SP06. Storm monitor has 9 indicators but:
session telemetry not feeding them (W8 adapter → to_storm_indicators),
indicator #10 aggregate_context not implemented, post-incident reports
not auto-posted, circuit breakers exist but not tested end-to-end,
de-escalation tuning, prevention recommendations engine.
**Source:** implementation-roadmap Wave 1, System 11

### 11. Labor Attribution Wiring
Wave 1 M-LA01 to M-LA05. LaborStamp exists (25 fields) but:
session telemetry not feeding real values (tokens=0 hardcoded in
tools.py:695), heartbeat stamp not called by orchestrator,
lines_added/removed not populated from git diff, fleet.labor.recorded
event not emitted, only 8 of 15+ fields written to TaskCustomFields,
analytics dashboard not built.
**Source:** implementation-roadmap Wave 1, System 13, §44

### 12. Challenge System Wiring
Largest system (2831 lines, 235 tests). NOTHING connected to runtime:
challenge results not available to fleet-ops during review, automated
challenges never tested against real code diffs, cross-model with
LocalAI not integrated, deferred queue drain not in orchestrator,
teaching signals not feeding teaching system, not invoked from
fleet_task_complete.
**Source:** implementation-roadmap Wave 3, System 15, §59

### 13. Session Telemetry Wiring
Adapter exists (230 lines, 30 tests). Orchestrator doesn't call:
to_labor_fields() → LaborStamp, to_claude_health() → ClaudeHealth,
to_storm_indicators() → StormMonitor, to_cost_delta() → BudgetMonitor.
Every system that needs real session data runs on estimates or zeros.
This is the data pipeline that feeds storm, budget, labor, health.
**Source:** H2, System 19, every system doc mentions "W8 not wired"

### 14. Readiness/Progress Completion
task_progress field added to models.py but: fleet_task_complete doesn't
set to 70 (WORK_COMPLETE), challenge system doesn't set to 80
(CHALLENGE_PASSED), fleet_approve doesn't set to 90 (REVIEW_PASSED),
brain doesn't transition at 100 (DONE), Plane sync doesn't have
progress labels, pre-embed doesn't show both readiness + progress.
**Source:** §45, §33.24

### 15. Agent Signatures Completion
LaborStamp 25 fields mostly empty: add context_window_size, budget_mode,
context_used_pct, rate_limit_pct. Wire session telemetry → stamp
assembly. Populate lines_added/removed from git diff. Emit
fleet.labor.recorded event. Mini-signatures on trail events (agent +
model + context%). Review signature on fleet_approve (reviewer identity,
duration, criteria checked). Write all 15+ fields to TaskCustomFields.
**Source:** §44, §33.25

### 16. Disease Detection Expansion
7 of 11 detections not implemented in doctor.py: abstraction (compare
agent terms vs PO verbatim), code_without_reading (tool call order),
scope_creep (committed files vs plan target_files), cascading_fix
(fix→break chain), context_contamination (patterns across compaction),
not_listening (same correction repeated), compression (task scope vs
plan scope). Plus 3 missing teaching templates: cascading_fix,
context_contamination, not_listening.
**Source:** §33.16, System 2, System 3

### 17. Notification Routing Completion
2 missing IRC channels (#gates, #contributions). 5 missing notification
routes (contribution→target, gate→PO, phase→fleet, QA→reviews,
security→reviews). ntfy fleet-gates and fleet-review topics not
configured. Cross-reference execution: generate_cross_refs() returns
refs but no caller executes them. The Lounge web IRC deployment.
**Source:** §33.14, §42, System 18

### 18. Anti-Corruption Structural (Line 1)
Beyond safety-net and hooks: autocomplete chain engineering (data
ordering prevents disease — depends on navigator), contribution
requirements as dispatch block (gate won't open without required
contributions), phase-aware standards injection (agent sees quality
bar for current phase), verbatim anchoring in every context level
(appears in task pre-embed, heartbeat, plan, completion, review).
Stage reversion on rejection/disease.
**Source:** §39, §33.16, §36

### 19. Cowork + Transfer Protocols
Cowork: owner vs coworker distinction, coworker permissions (can
commit/artifact, can't complete), brain dispatches to owner and
notifies coworkers, trail records who did what. Transfer: fleet_transfer
tool exists but context packaging (artifacts, comments, contributions,
trail summary), receiving agent gets transfer context in task-context.md,
trail records transfer with source/target/stage/readiness.
**Source:** §41, §33.17

### 20. Pre-Embed Per Role
Currently generic for all agents. PM needs: Plane sprint data,
unassigned task count + details, pending gates. Fleet-ops needs:
full approval context (requirement + criteria + PR + trail). Workers
need: artifact completeness + suggested readiness + contributions
received. Architect needs: tasks needing design with full context.
All agents need: delivery phase visible, both readiness + progress,
context % + rate limit %.
**Source:** U-02, U-13, U-14, H3, System 7, System 19

### 21. Context Strategy (CW-03 to CW-10)
CW-03 strategic compaction protocol per role. CW-04 efficient
regathering per role. CW-07 rate limit rollover awareness in brain.
CW-08 pre-rollover preparation (force compact at 85%). CW-09
context-proportional awareness (1M managed aggressively). CW-10
multi-agent rollover coordination (stagger compactions). Smart
artifacts dumping (heavy context → synthesized artifact). config/
fleet.yaml session_management section.
**Source:** §35, §33.11, System 19, System 22

### 22. Operational Protocols
PO daily workflow runbook (morning check, active work, escalation
levels, weekly cadence, emergency procedures). Crisis response playbook
(budget drain, MC down, gateway down, bad agent output, storm
escalation — 5 scenarios). Canonical deployment specification (Docker
services, ports, startup sequence, health checks). Sprint/PM ceremony
protocols (planning, velocity, backlog, retrospectives). Agent
permissions formalization (bypassPermissions → formal matrix).
**Source:** §48, §50, §49, §52, §53, §33.28-33.33

### 23. LightRAG Deployment
Phase 1: deploy LightRAG Docker service (port 9621), configure
embedding (LocalAI bge-m3 CPU), entity extraction (Claude or LocalAI).
Phase 2: OCMC sync (board memory → LightRAG ingestion). Phase 3:
agent MCP tool (fleet_query_knowledge). Phase 4: cross-project mesh
(AICP + Fleet + DSPD + NNRT in one graph). Phase 5: Plane artifact
sync (sprint plans, decisions, outcomes).
**Source:** §46, §33.26, U-21 to U-23

### 24. LocalAI Routing
Actually connecting LocalAI to fleet dispatch. Health check (GET
/v1/models), model swap management (single-active-backend, 8GB VRAM),
skip-swap logic, warm pool (keep most-used loaded), pre-warming,
fallback chain (LocalAI → Claude), confidence tier assignment (trainee),
challenge requirement for trainee output, cost tracking ($0 for local).
**Source:** §23, §94, System 14, strategic-vision Stage 2-3

### 25. Multi-Backend Routing (Waves 2-5)
Wave 2: backend registry (4 backends defined), routing decision engine,
fallback chain, OpenRouter free tier client (29 models), per-backend
circuit breakers. Wave 4: model evaluation (Qwen3.5 benchmarks),
shadow routing, default promotion. Wave 5: dual GPU, cluster peering,
Codex CLI adversarial, backend health dashboard, AICP router unification.
**Source:** implementation-roadmap Waves 2-5, System 14, System 16

### 26. Cross-Project Integration
AICP RAG → fleet (wire kb.py via MCP server or API), AICP ↔ Fleet
router bridge (router_unification.py), NNRT integration (project
registration + repo access), cross-project cost attribution (project
field on DispatchRecord + LaborStamp). LightRAG as cross-project
knowledge mesh.
**Source:** §51, §33.31, U-36, L5

### 27. Live Testing
35 agent behavior tests (§82): 10 PM tests, 7 fleet-ops tests, 8
worker tests, 10 system flow tests. Gateway integration (8-file onion
verified with real agent). LocalAI integration (heartbeat on hermes-3b,
MCP tool calling via LocalAI). 24h fleet observation with storm
protection active. Minimum viable live test (single agent full cycle).
Full lifecycle live test (PM→assignment→stages→work→review→done).
**Source:** §82, path-to-live Steps 15+19+24, U-26 to U-31

### 28. Economic Model
ROI analysis per LocalAI stage. Cost-per-task breakdown by type/model/
backend. LocalAI payback timeline. Budget variance tracking (actual vs
projected). Sprint cost reporting. Model-specific cost analysis.
**Source:** §47, §33.27

### 29. Multi-Fleet Identity
Fleet Alpha + Fleet Bravo naming. Shared Plane (no collision strategy).
Agent naming ({fleet_id}-{role}). Git attribution (fleet-prefixed
branches). Cross-fleet contribution. Infrastructure per fleet (separate
MC, gateway, orchestrator). LocalAI cluster peering.
**Source:** §67, §91, L7

### 30. Ecosystem Completion
E-05 to E-15 from ecosystem deployment plan: GitHub MCP per agent,
Playwright MCP per agent, Docker MCP per agent, per-agent skills from
config, LocalAI RAG → fleet, Batch API, Agent Teams evaluation, AICP
bridge, LocalAI v4.0 agents evaluation, OpenRouter client, multi-fleet.
**Source:** ecosystem-deployment-plan, §34.6

---

## Summary

| Category | Plans Written | Plans Missing | Total Needed |
|----------|-------------|--------------|-------------|
| Capabilities (install/deploy) | 3 (01,02,03) | 2 (23,30) | 5 |
| Enforcement (hooks/anti-corruption) | 1 (04) | 2 (18,16) | 3 |
| Knowledge Map | 1 (05) | 0 | 1 |
| Agent Files | 1 (06) | 0 | 1 |
| Brain/Orchestrator | 0 | 3 (07,08,13) | 3 |
| System Wiring | 0 | 5 (09,10,11,12,14) | 5 |
| Data Model | 0 | 2 (15,21) | 2 |
| Protocols | 0 | 2 (19,22) | 2 |
| Infrastructure | 0 | 3 (20,24,25) | 3 |
| Integration | 0 | 2 (26,29) | 2 |
| Testing | 0 | 1 (27) | 1 |
| Economics | 0 | 2 (28,17) | 2 |
| **Total** | **6** | **24** | **30** |
