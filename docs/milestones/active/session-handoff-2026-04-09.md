# Session Handoff — 2026-04-09

## What This Session Did

Large session focused on E001 (Agent Directive Chain) with work touching E002, E003, E007, E010. 80+ files changed.

## What Was Actually Done (Verified)

### Code Changes (real, tested, 2385 tests passing)
- **generate-tools-md.py** rewritten — filters by tool-roles.yaml. TOOLS.md reduced from 15-18K to 2-5K per agent.
- **10 CLAUDE.md templates** rewritten — 8 sections per standard, <4000 chars. Mode-aware (injection:full vs injection:none).
- **11 HEARTBEAT.md templates** rewritten — priority order (PO→messages→core→idle).
- **agent.yaml** provisioning script — 14 fields per standard.
- **intent-map.yaml** expanded — 33→45 intents, pack_skills + sub_agents.
- **preembed.py** task-context.md — 10-section autocomplete chain order + mode indicator.
- **preembed.py** heartbeat — sections always present (PO DIRECTIVES, MESSAGES, ASSIGNED TASKS even when empty).
- **orchestrator.py** — contribution auto-creation (Step 2.5) + dispatch gate (blocks work without contributions) + phase gate (blocks at PO gates) + trail recording + PO gate auto-processing.
- **event_chain.py** — parent task comment propagation on child complete/reject.
- **doctor.py** — 7 new disease detection functions (11 total).
- **teaching.py** — 3 new lesson templates (11 total).
- **model_selection.py** — rejection escalation (effort +1 on rework). NOTE: budget mode caps were added then REVERTED — budget mode only controls tempo, not model/effort.
- **context_strategy.py** — new module for context/rate limit awareness. Thresholds: 93% context (7% remaining) = prepare, 95% (5%) = extract. Rate limit: 85% = prepare, 90% = manage. From PO's CW requirements doc.
- **role_providers.py** — worker provider has contribution awareness. Registry fixed (devops-expert → devops).
- **labor_stamp.py** — trainee flagging (is_trainee, trainee_warning, provenance_line, full_signature).
- **methodology.yaml** — work protocol updated: "pre-embedded in your context" not "call fleet_read_context first."
- **tool-chains.yaml** — 11 tools with ins/outs/middles documentation.
- **skill-stage-mapping.yaml** — 5 ecosystem packs mapped.
- **standing-orders.yaml** — writer raised to standard authority with proactive staleness scan.
- **agent-autonomy.yaml** — per-role lifecycle timing (PM 15min sleep, accountability 60min).
- **13 custom /commands** in .claude/commands/.
- **1 new skill** (fleet-build-order).
- **Templates** — comment.py and pr.py updated for trainee flagging.

### Design/Research Documents (in wiki/domains/)
- tools-md-redesign.md — three-layer model design
- agent-ecosystem-allocation.md — per-role skill/plugin/pack allocation (1100+ skills researched)
- navigator-intent-gap-analysis.md — 33/80 coverage, 19 gaps identified
- navigator-intent-expansion.md — 19 new intents designed
- generate-tools-md-redesign.md — pipeline algorithm spec
- chain-bus-audit.md — E002 Phase 0
- brain-audit.md — E003 Phase 0
- context-strategy-design.md — CW-based thresholds
- effort-escalation-design.md — NOTE: budget mode section is WRONG, was reverted in code
- deterministic-bypass-design.md — gate auto-processing
- operational-modes-design.md — heartbeat vs task distinction
- adaptive-context-injection-design.md — NOTE: REINVENTS existing Navigator/intent-map architecture. Should be DELETED or heavily reworked to reference existing systems.
- validation-issues-catalog.md — 50 issues found across 15 scenarios
- path-to-live-reconciliation.md — 24 steps mapped to epics

### 17 Epics Expanded
All from skeleton to full content with PO quotes, goals, existing foundation, phases, relationships.

### Validation Matrix
15 scenarios in validation-matrix/ — 5 heartbeat + 10 task mode. Line-by-line review identified 50 issues.

## What Is BROKEN (Honest)

### Critical Errors Made This Session
1. **Budget mode hallucination** — invented budget mode caps on model/effort. Budget mode ONLY controls tempo (CRON frequency). Was implemented, then had to be reverted after PO caught it. The effort-escalation-design.md still has wrong information.
2. **Context strategy thresholds were invented** — initially made up 70/80/90/95% thresholds. PO corrected to actual documented values (93%/95% from CW doc, 85%/90% rate limit). Fixed in code but the context-strategy-design.md and earlier design docs may have stale values.
3. **adaptive-context-injection-design.md** — reinvents the Navigator/intent-map/injection-profiles system that already exists. Should not be used as-is. Reference the existing knowledge-map architecture instead.
4. **operational-modes-design.md** — partially useful (heartbeat vs task distinction) but overengineers with new parameters when the existing AgentStatus + HeartbeatDecision + injection already handle this.

### 50 Validation Issues (Unresolved)
Full catalog at wiki/domains/architecture/validation-issues-catalog.md. The critical ones:

- **A1:** HEARTBEAT.md is static for all states — fixed partially (sections always present) but HEARTBEAT.md itself doesn't adapt
- **A3/F1/F2:** Role data dumps raw Python dicts — UNFIXED
- **B1:** Contribution content is "check comments" not inline — partial fix (preservation during refresh) but fragile
- **H5:** Confirmed plan not visible in task context — UNFIXED
- **H6:** Previous stage findings not visible — UNFIXED
- **H11/H12:** Rejection rework invisible (no iteration, no feedback) — UNFIXED
- **I1:** Contribution tasks can't see target task — UNFIXED
- **I5:** Methodology protocols are role-generic — UNFIXED
- **J1:** Work protocol doesn't adapt to progress % — UNFIXED

### Runtime Files Are Stale
The template rewrites (CLAUDE.md, HEARTBEAT.md) are in agents/_template/ but the runtime files in agents/{name}/ still have OLD content from previous sessions. push-agent-framework.sh hasn't been run. The validation matrix showed old heartbeat files for PM and fleet-ops.

## Honest Progress Against Full Vision

44 PO requirements from the 2026-04-08 vision:
- Done: ~16 (36%)
- Partial: ~15 (34%)
- Not started: ~13 (30%)

Most "done" items are agent file rewrites and wiki infrastructure. The deeper architectural problems (adaptive injection, role-specific protocols, contribution content in context, rejection visibility) are IDENTIFIED but NOT SOLVED.

## Files That Should Be Reviewed With Skepticism
- wiki/domains/architecture/effort-escalation-design.md — budget mode section is wrong
- wiki/domains/architecture/adaptive-context-injection-design.md — reinvents existing Navigator architecture
- wiki/domains/architecture/context-strategy-design.md — thresholds were corrected but design doc may be stale
- wiki/domains/architecture/operational-modes-design.md — overengineered, existing systems handle most of this
- wiki/backlog/modules/_index.md — module "done" counts are optimistic

## Key PO Corrections This Session
1. Budget mode = tempo ONLY. Not model/effort caps.
2. Context thresholds: 7% remaining = prepare (93% used), 5% = extract (95%). Rate limit: 85% = prepare, 90% = manage. From CW requirements doc.
3. fleet_read_context is for loading DIFFERENT task data or refreshing stale data when injection is full. Not "FIRST call every session."
4. Heartbeat and task are two different operational modes — different directives, different context needs.
5. Don't reinvent what exists (Navigator, intent-map, injection-profiles). Fix the implementation.
6. Don't claim done when validation shows 50 open issues.
7. The 78 fleet skills are just our custom layer — the full ecosystem has 1100+ skills across packs (superpowers, ring, trailofbits, etc).
8. Stay on the foundation chain (E001→E002→E003→E007). No bifurcations.

## What the Next Session Should Do
1. Read the validation-issues-catalog.md (50 issues)
2. Read the existing Navigator architecture (docs/knowledge-map/)
3. Fix the 15 critical issues WITHIN the existing architecture
4. Regenerate validation matrix after fixes
5. Review each scenario line-by-line with PO
6. Don't write new design documents — fix the code
