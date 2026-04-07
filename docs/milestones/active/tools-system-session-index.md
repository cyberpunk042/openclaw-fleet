# Tools System Elevation — Session Index

**Date:** 2026-04-07
**Status:** Active session — planning and execution tracking
**Scope:** Complete tools system elevation across all 7 capability layers for 10 top-tier expert agents

---

## Session Context

This session regathered full context from compacted previous session, then conducted deep research across the entire fleet system — 31 fleet-elevation docs, 22 system docs, 8 standards, gateway automation capabilities, skills ecosystem, Claude Code extension points, and the full path-to-live.

The PO's direction: this is 42+ hours of work. No minimizing. No disconnected pieces. Each agent is a TOP-TIER EXPERT with their own tools, MCPs, chains, group calls, skills, plugins, CRONs, sub-agents, hooks, standing orders, and directives — generic AND role-specific, adapted per methodology stage.

---

## Documents Produced This Session

### Research & Analysis (8)

| # | Document | What It Covers |
|---|----------|---------------|
| 1 | [tool-chain-elevation-plan.md](tool-chain-elevation-plan.md) | Fleet group calls (Layer 1): tree execution, cross-platform propagation, per-tool gap analysis, chain builder inventory, ChainRunner evolution |
| 2 | [role-specific-tooling-elevation-plan.md](role-specific-tooling-elevation-plan.md) | Layers 2-7: MCP servers, plugins, skills, CRONs, sub-agents, hooks/standing orders/extended thinking. Current state, gaps, architecture |
| 3 | [gateway-automation-capabilities.md](gateway-automation-capabilities.md) | Full technical reference: CRONs, Tasks, TaskFlow, Hooks (14 gateway + 23 Claude Code events), Standing Orders, Heartbeat config |
| 4 | [skills-and-plugins-ecosystem-research.md](skills-and-plugins-ecosystem-research.md) | 5 skill sources, 32 official Anthropic plugins, 9 superpowers marketplace plugins, skill loading pipeline, stage-aware recommendation pattern |
| 5 | [strategic-agent-capabilities-research.md](strategic-agent-capabilities-research.md) | Sub-agents, Agent Teams, extended thinking, hook-based monitoring, session management, 9 strategic call dimensions |
| 6 | [tools-system-full-capability-map.md](tools-system-full-capability-map.md) | THE REAL SCOPE: 3-layer architecture, per-role group calls/skills/CRONs/sub-agents, review ecosystem, plugin details, secondary/backup roles, phase/labor/context connections |
| 7 | [tools-system-session-decisions.md](tools-system-session-decisions.md) | PO requirements verbatim, decisions made, open questions needing PO input, connections to existing work |
| 8 | [tools-system-directives-and-usage.md](tools-system-directives-and-usage.md) | HOW agents know when to use what: 7 directive types, injection order, input/output clarity, strategic features, autocomplete chain, immune system |
| 9 | [phase-a-operations-analysis.md](phase-a-operations-analysis.md) | EVERY operation in every elevated tree: 10 categories, what exists vs needs building, 9 new functions/modules, 18 conditional logic items, implementation order for Phase A |

### Pre-Existing (from previous session)

| Document | What It Covers |
|----------|---------------|
| [tool-chain-investigation.md](tool-chain-investigation.md) | Original investigation: what's wired vs disconnected, propagation model, dual-board strategy |

### Legacy Chunk Plans (from early this session — SUPERSEDED by revised phases below)

| Document | Status | Notes |
|----------|--------|-------|
| chunk-01 through chunk-09 | SUPERSEDED | Written before full capability map revealed real scope. Kept for reference but the revised 8-phase structure below replaces them. |

---

## Code Changes This Session

| File | Change | Status | Quality |
|------|--------|--------|---------|
| scripts/push-soul.sh | Per-agent mcp.json deployment + .claude/skills/ symlink | DONE | Solid |
| fleet/core/chain_runner.py | 3 new handler actions (update_custom_fields, update_labels, create_issue) | DONE | Solid |
| fleet/core/event_chain.py | 8 new chain builders | DONE | Chain builders provide propagation layer |
| fleet/mcp/tools.py | ALL 16 state-modifying tools elevated to match fleet-elevation/24 + fleet_phase_advance built | DONE | Full elevated trees — verbatim check, security_hold, contribution completeness, readiness regression, sprint progress, doctor signaling, context packaging, notify_contributors, auto-gate at 90%, phase standards check |
| fleet/core/phases.py | check_phase_standards() + PhaseStandardResult | DONE | Evaluates task against PO-defined quality bars |
| fleet/core/plan_quality.py | check_plan_references_verbatim() | DONE | Key term extraction, coverage analysis |
| fleet/core/contributor_notify.py | notify_contributors() | DONE | NEW — mentions contributors at review stage |
| fleet/core/transfer_context.py | package_transfer_context() + TransferPackage | DONE | NEW — gathers all data for task handoff |
| fleet/core/context_writer.py | append_contribution_to_task_context() | DONE | Embeds contributions into target agent's context |
| fleet/core/velocity.py | update_sprint_progress_for_task() | DONE | Sprint metrics after task completion |
| fleet/core/doctor.py | signal_rejection() | DONE | Feeds rejection signals to immune system |
| fleet/core/context_assembly.py | Phase data + contribution status sections | DONE | Context now includes phase standards + contribution completeness |
| fleet/core/preembed.py | Phase standards + required contributions in pre-embed | DONE | Agent sees quality bars and required inputs before starting |
| fleet/tests/core/test_new_chain_builders.py | 17 tests for chain builders (all pass) | DONE | 42 total tests, 0 failures |

**Phase A complete.** All generic fleet tools match fleet-elevation/24 elevated trees. 7 new building block modules. Context system includes phase + contribution data. 42 tests pass, 0 regressions.

---

## Revised Trajectory — 8 Phases

### PHASE A: Foundation Infrastructure
**Status:** COMPLETE
**Scope:** Evolved ChainRunner. All 16 state-modifying tools elevated to match fleet-elevation/24 FULLY. 7 building block modules built. Phase config verified (already flexible). Context system updated with phase + contribution data.
**Scale completed:** 16 tool rewrites + 7 new modules + context assembly + preembed updates. 42 tests, 0 failures.
**Depends on:** Nothing (foundation infrastructure exists)
**Blocks:** Everything else

**Sub-items:**
- A1: ChainRunner evolution — methodology verification, contribution completeness, security holds, readiness regression, phase standards, context packaging, sprint progress, doctor signaling
- A2: Rewrite all 30 fleet tool trees to match fleet-elevation/24 elevated trees FULLY
- A3: Phase config evolution (flexible predefinable groups, per-epic assignment)
- A4: Context system quadrant updates (phase standards, contribution status, skill recommendations)

### PHASE B: MCP + Plugin Deployment
**Status:** NOT STARTED (push-soul.sh fix done)
**Scope:** Verify all MCP server packages per role. Verify and install all plugins per role. Evaluate unassigned plugins. Fix full deployment pipeline. End-to-end workspace verification.
**Scale:** 10 MCP server types + 13 plugin types + evaluation of 10+ additional plugins
**Depends on:** Phase A (stable tools.py before verifying MCP integration)
**Blocks:** Phase C (role-specific tools registered on same MCP server), Phase D (plugin skills)

**Sub-items:**
- B1: Verify all MCP server packages (npm/npx availability, compatibility)
- B2: Verify and install all configured plugins per role
- B3: Evaluate unassigned plugins (feature-dev, code-review, serena, episodic-memory, etc.)
- B4: Fix full deployment pipeline (mcp.json + skills + plugins → workspaces)
- B5: End-to-end workspace verification (each agent has all configured tools)

### PHASE C: Role-Specific Group Calls (BIGGEST PHASE)
**Status:** NOT STARTED
**Scope:** Design group call architecture. Build ~35-40 role-specific group calls as new MCP tools, each with tree execution, input validation, chain propagation, and tests.
**Scale:** ~35-40 NEW tools, each comparable to fleet_task_complete in complexity
**Depends on:** Phase A (ChainRunner capable), Phase B (MCP servers verified)
**Blocks:** Phase G (configs must document these tools)

**Sub-items:**
- C1: Group call architecture design (registration, tree builder pattern, per-role vs shared)
- C2: PM group calls (~5: sprint standup, epic breakdown, contribution check, gate route, blocker resolve)
- C3: Fleet-ops group calls (~4: real review, board health, compliance spot check, budget assessment)
- C4: Architect group calls (~4: design contribution, codebase assessment, option comparison, complexity estimate)
- C5: DevSecOps group calls (~6: dependency audit, code scan, secret scan, PR security review, security contribution, infra health)
- C6: Engineer group calls (~3: contribution check, implementation cycle, fix task response)
- C7: DevOps group calls (~4: infra health, deployment contribution, CI/CD review, phase infrastructure)
- C8: QA group calls (~4: test predefinition, test validation, coverage analysis, acceptance criteria review)
- C9: Writer group calls (~3: staleness scan, doc contribution, doc from completion)
- C10: UX group calls (~2: spec contribution, accessibility audit)
- C11: Accountability group calls (~3: trail reconstruction, sprint compliance, pattern detection)

### PHASE D: Skills
**Status:** NOT STARTED
**Scope:** Ecosystem evaluation per role. Build foundation skills (M81-M86). Build/install generic methodology skills. Build/install role-specific skills (40+ per role). Stage-aware mapping.
**Scale:** 10-20 generic + 80-100 role-specific skills (many from ecosystem, some custom)
**Depends on:** Phase B (plugin skills available), Phase C (group calls exist to reference)
**Blocks:** Phase G (skills must exist for TOOLS.md)

**Sub-items:**
- D1: Ecosystem evaluation per role (1000+ available → what fits?)
- D2: Foundation skills (M81-M86: URLs, templates, PR, comments, memory, IRC)
- D3: Generic methodology skills (10-20 shared)
- D4: Role-specific skills (40+ per role × 10 roles, phased by priority)
- D5: Stage-aware mapping (config/skill-stage-mapping.yaml)

### PHASE E: CRONs + Standing Orders
**Status:** NOT STARTED
**Scope:** Design standing orders per role (PO input needed). Design CRONs per role. Config + sync script. Fleet state integration.
**Scale:** ~20-25 CRONs + 10 standing order programs
**Depends on:** Phase C (group calls that CRONs invoke), Phase D (skills that CRONs reference)
**Blocks:** Phase G (CRONs documented in TOOLS.md)

**Sub-items:**
- E1: Standing order design per role (requires PO input on autonomous authority)
- E2: CRON design per role (schedules, models, effort, delivery)
- E3: config/agent-crons.yaml + scripts/sync-agent-crons.sh
- E4: Fleet state integration (pause/budget awareness)

### PHASE F: Sub-Agents + Hooks + Thinking
**Status:** NOT STARTED
**Scope:** Custom sub-agent definitions per role. Agent Teams evaluation. Per-role hook configurations. Stage-aware effort. Monitoring hooks.
**Scale:** ~10-15 sub-agents + per-role hook configs + effort system + monitoring
**Depends on:** Phase B (plugin sub-agents available), Phase D (skills sub-agents reference)
**Blocks:** Phase G (sub-agents/hooks in TOOLS.md)

**Sub-items:**
- F1: Custom sub-agent definitions per role
- F2: Agent Teams evaluation (complement or conflict with orchestrator?)
- F3: Per-role hook configurations (quality enforcement, behavioral, session)
- F4: Stage-aware effort system (connect brain decisions to session effort)
- F5: Monitoring hooks (PO observation stream)
- F6: Security hook content detection fix

### PHASE G: Generation Pipeline + Configs
**Status:** NOT STARTED
**Scope:** Write tool-chains.yaml from scratch (ALL tools). Validate tool-roles.yaml. Update agent-tooling.yaml. Create skill-stage-mapping.yaml, agent-crons.yaml. Rewrite generate-tools-md.sh for all 7 layers with directives and input/output clarity.
**Scale:** Complete config rewrite + generation pipeline rewrite
**Depends on:** ALL previous phases (configs document what actually exists)
**Blocks:** Phase H (TOOLS.md generation)

**Sub-items:**
- G1: tool-chains.yaml from scratch (30 generic + 35-40 role-specific tools)
- G2: tool-roles.yaml validation + evolution (per-role filtering accurate)
- G3: agent-tooling.yaml update (real skills, verified plugins, all role tools)
- G4: skill-stage-mapping.yaml creation
- G5: agent-crons.yaml creation
- G6: Rewrite generate-tools-md.sh (all 7 layers, directives, input/output/impact)
- G7: Generate TOOLS.md for all 10 agents

### PHASE H: Validation + Deployment
**Status:** NOT STARTED
**Scope:** Config cross-validation. TOOLS.md accuracy per agent. Workspace deployment. Smoke test. Documentation updates.
**Depends on:** Phase G
**Blocks:** Live fleet operation with proper tooling

**Sub-items:**
- H1: Config cross-validation (all configs internally consistent)
- H2: TOOLS.md accuracy verification per agent (spot-check tools, skills, chains)
- H3: Workspace deployment verification (all files reach all workspaces)
- H4: Smoke test (1 agent end-to-end with generic + role-specific tools)
- H5: Documentation updates (STATUS-TRACKER, MASTER-INDEX, path-to-live)

---

## Dependency Chain

```
PHASE A (foundation)
  ↓
PHASE B (MCP + plugins)
  ↓
PHASE C (role-specific group calls)  ←── BIGGEST: ~35-40 new tools
  ↓
PHASE D (skills)                     ←── MOST ITEMS: 80-100+ skills
  ↓
PHASE E (CRONs + standing orders)    ←── NEEDS PO INPUT on authority
  ↓
PHASE F (sub-agents + hooks + thinking)
  ↓
PHASE G (generation pipeline + configs)
  ↓
PHASE H (validation + deployment)
```

Some parallelism possible:
- Phase D can START during Phase C (foundation skills don't depend on role group calls)
- Phase E standing order DESIGN can start during Phase C (writing authority docs)
- Phase F sub-agent EVALUATION can start during Phase B (plugin sub-agents)

---

## Cross-References

| Document | Relationship |
|----------|-------------|
| [path-to-live.md](path-to-live.md) | Phase A maps to path-to-live Phase C. Phase B maps to Phase A Step 4. Phase C is NEW (not in original path). Phase D maps to Phase B Step 9. Phase G-H map to Phase B Step 9 + Phase D. |
| [fleet-elevation/05-14](fleet-elevation/) | Per-role specs — source of truth for role-specific capabilities |
| [fleet-elevation/24](fleet-elevation/24-tool-call-tree-catalog.md) | Tool call tree catalog — target for Phase A elevated trees |
| [fleet-elevation/04](fleet-elevation/04-the-brain.md) | Brain design — chain registry, strategic calls |
| [fleet-elevation/23](fleet-elevation/23-agent-lifecycle-and-strategic-calls.md) | Strategic calls — effort, model, context decisions |
| [fleet-elevation/15](fleet-elevation/15-cross-agent-synergy.md) | Synergy matrix — contribution model |
| [fleet-elevation/20](fleet-elevation/20-ai-behavior.md) | Anti-corruption — directives as structural prevention |
| [systems/04](../../../docs/systems/04-event-bus.md) | Event bus — chain propagation target |
| [systems/08](../../../docs/systems/08-mcp-tools.md) | MCP tools system reference |
| [systems/21](../../../docs/systems/21-agent-tooling.md) | Agent tooling system reference |
| [standards/tools-agents-standard.md](standards/tools-agents-standard.md) | TOOLS.md validation criteria |
| [ecosystem-deployment-plan.md](ecosystem-deployment-plan.md) | Ecosystem items E-01 through E-15 |
| [skills-ecosystem.md](skills-ecosystem.md) | Skills milestones M48-M52 |
| [phase-f1-foundation-skills.md](phase-f1-foundation-skills.md) | Foundation skills M81-M86 |
| [context-system/01-08](context-system/) | Context delivery mechanism for directives |
| [methodology-system/01-06](methodology-system/) | Stage protocols — per-stage capability recommendations |

---

## Rules

1. **Plan before execute** — understand the full scope before coding
2. **Full coverage** — no stubs, no partial delivery, no "done" at 5%
3. **Dependency order** — follow the phase chain
4. **Match fleet-elevation/24** — every tool tree matches the design spec FULLY
5. **Directives with every capability** — when/how/input/impact/output for everything
6. **Verify before advancing** — each phase verified before next starts
7. **Update this index** — as phases complete
8. **No premature configs** — tool-chains.yaml and TOOLS.md wait for Phase G after all capabilities exist
