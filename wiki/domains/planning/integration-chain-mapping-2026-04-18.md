---
title: "Integration Chain Mapping — OpenFleet Position 2026-04-18"
type: reference
domain: planning
status: active
created: 2026-04-18
updated: 2026-04-19
tags: [integration, second-brain, chain, planning, adherence, progress, openfleet]
confidence: high
sources:
  - id: brain-integration-chain
    type: documentation
    project: devops-solutions-research-wiki
    path: wiki/spine/references/second-brain-integration-chain.md
    title: "Operations Plan — Second Brain Integration Chain — Complete Walkthrough"
  - id: session-2026-04-16
    type: documentation
    file: wiki/log/2026-04-16-second-brain-integration-session.md
    title: "Second Brain Integration — First Live Session"
  - id: handoff-2026-04-17
    type: documentation
    file: docs/milestones/active/session-handoff-2026-04-17.md
    title: "Session Handoff 2026-04-17"
---

# Integration Chain Mapping — OpenFleet Position 2026-04-18

## Summary

OpenFleet's position on the brain's 17-step second-brain integration chain (7 phases: Discovery → Identity → Methodology → Standards → Work Loop → Feedback → Local/Remote). Step-by-step scorecard as of 2026-04-18 with evidence and next actions. The chain is the brain's prescribed path for any project adopting the second-brain system; this page tracks where we are, what closed in the 2026-04-16 and 2026-04-17 sessions, and what remains. Parallels [[First Consumer Walkthrough OpenArms 2026-04-16]] style — makes operational depth visible.

## Scorecard by Phase

### Phase 1 — Discovery (Steps 1-3)

| Step | Title | State | Evidence |
|------|-------|-------|----------|
| 1 | First Contact | ✅ full | `gateway orient` runs cleanly; "NEXT: what-do-i-need" guidance surfaced |
| 2 | Auto-Detect Identity | ✅ full | Gateway reads our CLAUDE.md identity table (heading `## Identity Profile (...)`, 2026-04-17 rename enabled parser match) |
| 3 | Browse Tree | ✅ full | `gateway navigate` + `gateway status` both functional |

### Phase 2 — Identity (Steps 4-5)

| Step | Title | State | Evidence |
|------|-------|-------|----------|
| 4 | Declare Identity Profile | ⚠️ partial-by-design | CLAUDE.md declares STABLE fields only (Type/Domain/Phase/Scale/Second-Brain). Consumer-property fields (Execution Mode/PM Level/Trust Tier/SDLC Profile) deliberately omitted per brain's own principle `Execution Mode Is a Consumer Property, Not a Project Property`. Full profile in [[OpenFleet — Identity Profile]]. |
| 5 | Select SDLC Profile | ⚠️ undeclared | Brain's simplified/default/full profiles not explicitly selected. Our 5-tier quality vocabulary (Expert/Capable/Flagship-local/Lightweight/Direct) is orthogonal — a quality dimension, not an SDLC profile. Resolution: document our tier system as a profile adaptation, or declare one of brain's profiles as the default. |

### Phase 3 — Methodology (Steps 6-8)

| Step | Title | State | Evidence |
|------|-------|-------|----------|
| 6 | Understand Models | ⚠️ divergent vocabulary | Our [[Methodology Models Rationale]] defines 7 models; brain defines 9. Our stages (conversation → analysis → investigation → reasoning → work → review) vs brain's (document → design → scaffold → implement → test). Both valid per brain's own "per-project adaptation" allowance; divergence is undeclared formally. See [[Shared Models Integration — LLM Wiki + Methodology in OpenFleet]]. |
| 7 | Learn Stages per Task Type | ✅ mapped | Our config/methodology.yaml maps task_type → required stages. `gateway query --model <type> --full-chain` works against our local methodology via the brain-seeded `wiki/config/methodology.yaml` (2026-04-17). |
| 8 | Get Stage Details per Domain | ⚠️ partial | `wiki/config/domain-profiles/` seeded from brain; OpenFleet-specific overrides not authored. `gateway query --stage document --domain typescript` returns brain defaults, not fleet-calibrated values. |

### Phase 4 — Standards (Steps 9-11)

| Step | Title | State | Evidence |
|------|-------|-------|----------|
| 9 | Review Quality Standards | ✅ large | Per-type standards read for concept/lesson (2026-04-17/18). 22 per-type standards in brain's `wiki/spine/standards/`; more remain to absorb as we author new types. |
| 10 | Get Templates | ✅ seeded | `wiki/config/templates/` = 19 wiki templates + 7 methodology templates, verbatim from brain (2026-04-16). |
| 11 | Frontmatter Fields | ✅ seeded | `wiki/config/wiki-schema.yaml` verbatim brain (strict). Field reference in brain's `frontmatter-field-reference.md`. |

### Phase 5 — Work Loop (Steps 12-14)

| Step | Title | State | Evidence |
|------|-------|-------|----------|
| 12 | Follow Stage Sequence | ⚠️ partial-fleet-vs-wiki | Our orchestrator follows fleet methodology (config/methodology.yaml — fleet dispatched work). Wiki-content work in this repo should follow the newly-seeded `wiki/config/methodology.yaml` (2026-04-17 seed) — not yet stress-tested in a real authoring cycle. |
| 13 | Track Readiness and Progress | ❌ unseparated | Brain treats readiness (definition) and progress (execution) as INDEPENDENT dimensions (99→100 = human-only on BOTH). Our frontmatter uses a single `readiness` field. Separation is a schema change pending PO approval. |
| 14 | Handle Impediments | ❌ not systematic | Brain's `impediment_type` enum (technical / dependency / decision / environment / clarification / scope / external / quality) not systematically applied in our backlog frontmatter. |

### Phase 6 — Feedback (Steps 15-16)

| Step | Title | State | Evidence |
|------|-------|-------|----------|
| 15 | Contribute Learnings | 🟡 active | 7 contributions pending-review in brain (updated 2026-04-18 handoff): 6 in brain's `wiki/log/` + 1 lesson in brain's `wiki/lessons/00_inbox/`. Includes compliance-checker correction + amendment, Walkthrough C ground-truth, identity-parser + forwarder-contribute-target remark, 5-candidate behavioral-failure detection rules (OpenFleet doctor.py), AGENTS.md Layer-1 completion correction, and verify-before-contributing lesson (5 evidence items — above ≥3 threshold). Brain's commit `154bc58` fixed the forwarder-contribute-target issue upstream. |
| 16 | Scan Project for Brain | ⚠️ stale | `pipeline scan /home/jfortin/openfleet/` was last run at some point (session doc mentions README/CLAUDE/AGENTS/docs/architecture copied into brain's `raw/articles/`). Not re-run since infrastructure changes in 2026-04-17 (new root AGENTS.md 222L, CLAUDE.md restructure to 118L, new `.claude/rules/` directory). |

### Phase 7 — Mode (Step 17)

| Step | Title | State | Evidence |
|------|-------|-------|----------|
| 17 | Choose Mode | ✅ full | Local + sister-project + MCP. Brain at `/home/jfortin/devops-solutions-research-wiki`. `.mcp.json` wired. Forwarders `tools/lint.py`, `tools/evolve.py`, `tools/gateway.py` route to brain's venv with `--wiki-root` pointing at us. |

## Aggregate Progress

| Bucket | Count | Examples |
|--------|-------|----------|
| ✅ full | 8 | 1, 2, 3, 7, 9, 10, 11, 17 |
| ⚠️ partial | 6 | 4 (by design), 5, 6, 8, 12, 16 |
| 🟡 active | 1 | 15 (contributions pending-review) |
| ❌ unstarted | 2 | 13 (readiness/progress split), 14 (impediment_type) |

**Score: 9/17 full-or-active, 6/17 partial, 2/17 unstarted.**

Compare to brain-reported OpenArms first-consumer walkthrough (2026-04-16): 10/17 steps at varying states. OpenFleet is at comparable depth with a different gap profile — we're stronger on infrastructure (tools/, config/, contributions pipeline) and weaker on work-loop adoption (readiness/progress, impediment_type).

## What Closed in the 2026-04-17 Session

| Item | Before | After |
|------|--------|-------|
| `wiki/config/methodology.yaml` | missing | seeded verbatim from brain (657L) |
| Gateway identity detection | parser missed our heading | heading renamed `Project Identity` → `Identity Profile` |
| Walkthrough C accuracy | 3 claims aspirational/outdated | correction filed (brain/log/, pending-review) |
| Orphan pages in wiki | 2 (identity-profile, verify-before-contributing) | 0 — both linked from new `_index.md` hubs |
| Advisory unstyled concept pages | 3 | 0 — callouts per concept-page-standard |
| Cross-domain relationships from planning | 0 | 2 (lint-counted; more outbound links added but counter undercounts em-dash titles) |
| Contributions misfiled in our own log | 2 | 0 — removed; re-filed directly against brain |

## What Closed in the 2026-04-19 Session

45 brain documents absorbed in a /loop SWALLOW session (11 foundational models + 16 per-type standards + 7 model-standards + 7 lessons + 4 patterns). No scorecard cells FLIPPED from partial→full, but several cells gained explicit brain-validation evidence that refines our self-assessment:

| Item | Before | After |
|------|--------|-------|
| Step 9 (Review Quality Standards) evidence | "Per-type standards read for concept/lesson" | **All 23 per-type + model-standards absorbed** (concept, pattern, lesson, domain-overview, decision, source-synthesis, session-handoff, note, epic, reference, task, comparison, deep-dive, evolution, learning-path, operations-plan + 7 model-standards + root llm-wiki-standards) |
| Step 6 (Understand Models) evidence | "Our 7 models vs brain's 9" | Confirmed by reading all 11 brain foundational/ecosystem/depth/quality/agent-config models directly. Our 4:1:1 plan:execute:review split is brain-recognizable adaptation (plan-heavy research-oriented). |
| Step 15 contribution count | "5 contributions pending-review" | Updated to 7 per handoff (edit above) |
| Fleet-runtime enforcement claim | "Operationally Tier 2+" (undifferentiated) | **Split refined in [[operational-depth-gaps]]**: fleet-runtime L2-3 brain-validated; Claude-Code-session L0-1 remaining gap |
| Brain recognition of OpenFleet architecture | Implicit | Explicit: [model-claude-code](../../../../devops-solutions-research-wiki/wiki/spine/models/agent-config/model-claude-code.md) line 274, [three-lines-of-defense](../../../../devops-solutions-research-wiki/wiki/patterns/03_validated/enforcement/three-lines-of-defense-immune-system-for-agent-quality.md), [plan-execute-review](../../../../devops-solutions-research-wiki/wiki/patterns/03_validated/architecture/plan-execute-review-cycle.md) *"most mechanically pure implementation"*, [deterministic-shell-llm-core](../../../../devops-solutions-research-wiki/wiki/patterns/03_validated/architecture/deterministic-shell-llm-core.md) canonical instance, [model-ecosystem](../../../../devops-solutions-research-wiki/wiki/spine/models/ecosystem/model-ecosystem.md) PM-Level table at L2→L3 |
| Session-resilient knowledge capture | Session findings ephemeral | Memory file [project_brain_validates_openfleet_architecture.md](../../../../../.claude/projects/-home-jfortin-openfleet/memory/project_brain_validates_openfleet_architecture.md) created — survives context compaction per brain's [context-compaction-is-a-reset-event](../../../../devops-solutions-research-wiki/wiki/lessons/03_validated/context-engineering/context-compaction-is-a-reset-event.md) lesson |

**Newly identified P2/P3 candidates** (editorial, not schema-gated):
- Validation-matrix generalization: brain observed our 29 handcrafted files could compose from ~5 structural templates + condition parameters
- `.claude/hooks/*` for Claude-Code session enforcement (OpenArms v10 pattern: 215-line hook set → 0% stage violations in that context)
- CLAUDE.md 358L migration to `.claude/rules/*` toward brain's <200L invariant
- Evolution cadence operational workflow (`pipeline chain review` after sessions)
- Epic Done When: migrate from "common verification gates" boilerplate to epic-specific verifiable outputs

## Next Actions

### High leverage, safe unilateral

- Re-run `pipeline scan ../openfleet/` from brain side to refresh our imprint in `raw/articles/` with the 2026-04-17 infrastructure.
- Author operational-depth pages closing `too_few_pages` on planning/ecosystem/cross-domain — this page is one of them.
- Continue reading per-type standards for types we'll author next (lesson-page-standards, decision-page-standards, deep-dive-page-standards).

### Needs PO approval

- Readiness / progress schema separation (Step 13) — schema change, affects all backlog frontmatter.
- Impediment-type adoption (Step 14) — new enum, retrofit on existing backlog.
- Stage-vocabulary alignment decision (Step 6) — keep ours / adopt brain's / formally declare our vocabulary as an adaptation profile.
- SDLC profile selection (Step 5) — pick simplified/default/full, or document why our tier system replaces this choice.

## Relationships

- BUILDS ON: [[OpenFleet — Identity Profile]]
- BUILDS ON: [[Path-to-Live Reconciliation — Where We Are]]
- DERIVED FROM: [[Shared Models Integration — LLM Wiki + Methodology in OpenFleet]]
- DERIVED FROM: [[Methodology Models Rationale]]
- DERIVED FROM: [[Tier Rendering Design Rationale]]
- RELATES TO: [[Verify Before Contributing to External Knowledge Systems]]
- RELATES TO: [[Critical Review Findings — Context Injection Scenarios]]
- FEEDS INTO: future integration work on Steps 13, 14, 5, 6
