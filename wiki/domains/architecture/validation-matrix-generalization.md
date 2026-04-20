---
title: "Validation Matrix Generalization — 5 Templates Replace 29 Handcrafted Scenarios"
type: reference
domain: architecture
layer: 4
status: synthesized
confidence: medium
maturity: seed
created: 2026-04-20
updated: 2026-04-20
tags: [analysis, validation-matrix, proto-programming, templates, context-injection, generalization, openfleet]
sources:
  - id: brain-structured-context-proto-programming
    type: documentation
    project: devops-solutions-research-wiki
    path: wiki/lessons/03_validated/context-engineering/structured-context-is-proto-programming-for-ai-agents.md
    title: "Structured Context Is Proto-Programming for AI Agents"
  - id: session-2026-04-19
    type: documentation
    file: wiki/log/2026-04-19-session-brain-integration.md
    title: "Session — 2026-04-19 Brain Integration"
---

# Validation Matrix Generalization — 5 Templates Replace 29 Handcrafted Scenarios

## Summary

Brain cites our `validation-matrix/` 29-file corpus as a proto-programming exemplar and simultaneously identifies the improvement vector: the 29 handcrafted scenarios compose from **~5 structural templates + condition parameters**, not 29 independently-designed outputs. This analysis enumerates the templates, maps each scenario to its template and parameter set, and identifies the duplication that generalization would eliminate (~65-line HEARTBEAT.md protocol block copy-pasted across 7 HB files alone). Output is a template schema; implementation (generator + test fixtures) is out of scope for this exploration.

## Corpus Shape

29 files across 3 prefixes:

| Prefix | Count | Output files | Source of variance |
|--------|-------|--------------|--------------------|
| FL-* (Fleet scenario) | 3 | `fleet-context.md` | Phase, fleet-online count, crisis focus |
| HB-* (Heartbeat) | 7 | `fleet-context.md` + `HEARTBEAT.md` protocol | Assigned tasks, messages, directives, role data, events, tier |
| TK-* (Task) | 19 | `task-context.md` + optional `knowledge-context.md` | Stage, injection mode, tier, task type, contribution state, rejection |

## The 5 Templates

### T1 — Fleet Scenario (FL-only)

**Output surface:** `fleet-context.md` (no HEARTBEAT.md)
**Instances:** FL-01, FL-03 (+ FL-02 implied from gap in numbering)
**Skeleton:**

```
# MODE: heartbeat | injection: full | generated: {{timestamp}}
# HEARTBEAT CONTEXT
Agent: {{agent}}
Role: {{role}}
Fleet: {{online}}/10 online | Mode: {{mode}} | Phase: {{phase}} | Backend: {{backend}}

## PO DIRECTIVES  → {{directives_block | "None."}}
## MESSAGES       → {{messages_block | "None."}}
## ASSIGNED TASKS → {{tasks_block | "None."}}
## STANDING ORDERS (authority: {{authority}})
{{standing_orders_block}}
## EVENTS SINCE LAST HEARTBEAT → {{events_block | "None."}}
```

**Parameters:** `agent`, `role`, `online` (N/10), `mode` ∈ {full-autonomous, semi-autonomous, planning}, `phase` ∈ {planning, execution, crisis}, `backend`, `directives[]`, `messages[]`, `tasks[]`, `events[]`, `authority` ∈ {conservative, balanced, aggressive}.

### T2 — Heartbeat (HB-*)

**Output surface:** `fleet-context.md` + `HEARTBEAT.md` protocol (65+ identical lines duplicated across all 7 HB files)
**Instances:** HB-01, HB-02, HB-03, HB-04, HB-05, HB-06, HB-20 (T5-condensed variant)
**Skeleton:**

```
# T1 skeleton (fleet-context.md)
# + ROLE DATA block (my tasks, contribution tasks, contributions received, in review)
# + HEARTBEAT.md appended verbatim from shared template
```

**Parameters:** all T1 params + `role_data` (task counts, contribution status).
**Duplication eliminated:** 7 × 65 = **455 duplicated lines** from HEARTBEAT.md alone if lifted to template.

### T3 — Task with Full Injection (default TK-*)

**Output surface:** `task-context.md` + `knowledge-context.md`
**Instances:** TK-01, TK-02, TK-03, TK-04, TK-06, TK-07, TK-08, TK-09, TK-10, TK-11, TK-12, TK-13, TK-25, TK-27, TK-29, TK-34, TK-42 (17 of 19)
**Skeleton:**

```
# MODE: task | injection: full | model: {{model}} | generated: {{ts}}
# YOU ARE: {{agent}}
# YOUR TASK: {{task_title}}
  - ID, Priority, Type, Story Points, Parent, Description
# YOUR STAGE: {{stage}}
# READINESS: {{readiness}}%
# PROGRESS: {{progress}}%

## VERBATIM REQUIREMENT → {{verbatim}}
## Current Stage: {{STAGE_UPPER}}
{{stage_protocol | "protocol block from config/methodology.yaml"}}

## CONFIRMED PLAN  → {{plan_block | omitted if stage < reasoning}}
## INPUTS FROM COLLEAGUES → {{contributions[]}}
## Required Contributions → {{contrib_summary}}
## DELIVERY PHASE: {{phase}} → {{phase_rubric}}
## WHAT TO DO NOW → {{directive_line}}

# knowledge-context.md
{{role_profile}} + {{stage_profile}} + {{tool_tables}} + {{related_systems}}
```

**Parameters:** `stage` ∈ {conversation, analysis, investigation, reasoning, work, review}, `model` ∈ {feature-development, contribution, rework, research, documentation, review, hotfix}, `task_type`, `readiness`, `progress`, `verbatim`, `plan?`, `contributions[]` (each with `type`, `from_role`, `status`, `content`), `delivery_phase` ∈ {poc, mvp, staging, production}, `authority`, `rejection_feedback?` (if iteration > 1).
**Stage protocol block** is itself a T3-sub-template looked up from `config/methodology.yaml` by `(model, stage)` — already generalized in config, but currently re-rendered per-scenario.

### T4 — Task with No Injection (TK-05 only)

**Output surface:** `task-context.md` stub only (no knowledge-context.md)
**Instances:** TK-05
**Skeleton:**

```
# MODE: task | injection: none
# YOU ARE: {{agent}}
# YOUR TASK: {{task_title}} ({{task_id}})
# YOUR STAGE: {{stage}}
## VERBATIM REQUIREMENT → {{verbatim}}
Call `fleet_read_context()` to load your full task context before proceeding.
```

**Parameters:** `agent`, `task_id`, `task_title`, `stage`, `verbatim`.
**Why separate template, not a T3 flag:** semantically T4 is the *inverse* of T3 — it validates the no-injection pathway where the agent MUST tool-call for context. Collapsing into T3 with an `injection=none` param is viable but obscures the intent. Tradeoff is a template choice, not a forced factoring.

### T5 — Tier-Condensed Variants (cross-cutting)

**Output surface:** same as parent (T2 or T3) but fields trimmed per tier
**Instances:** TK-30 (capable), TK-31 (lightweight), HB-20 (lightweight)
**Skeleton:** conditional rendering of parent template.

**Parameters (additive over parent):** `tier` ∈ {expert, capable, flagship-local, lightweight, direct}.
**Tier-driven transformations:**

| Tier | Contributions | Role tables | Plan depth | Fleet detail |
|------|---------------|-------------|------------|--------------|
| expert | full content | full | full | full |
| capable | status-only summary | core fields | summary | online count only |
| flagship-local | full content | core fields | full | full |
| lightweight | omitted | omitted | title only | online count only |
| direct | stub stage protocol | omitted | omitted | N/A |

**Why not a separate template:** T5 is a *projection* over T2/T3, not a distinct output shape. Should be implemented as a transform pipeline applied after parent rendering.

## Mapping Table — All 29 Files

| Scenario | Template | Key parameters |
|----------|----------|----------------|
| FL-01 | T1 | phase=planning, online=2, directives=none |
| FL-03 | T1 | phase=crisis, online=2, focus=fleet-ops |
| HB-01 | T2 | tasks=0, messages=0, events=0 |
| HB-02 | T2 | tasks=[task-a1b/work], contribs-received=2 |
| HB-03 | T2 | messages=[mention] |
| HB-04 | T2 | role=fleet-ops, reviews-pending=N |
| HB-05 | T2 | role=pm, tasks-unassigned=N |
| HB-06 | T2 | directives=[urgent] |
| HB-20 | T2+T5 | tier=lightweight |
| TK-01 | T3 | stage=work, contribs=[design, qa], plan present |
| TK-02 | T3 | stage=work, contribs=missing |
| TK-03 | T3 | stage=reasoning |
| TK-04 | T3 | stage=conversation, readiness=10 |
| TK-05 | T4 | injection=none |
| TK-06 | T3 | stage=work, iteration=2, rejection_feedback set |
| TK-07 | T3 | role=architect, stage=work (contribution-producing) |
| TK-08 | T3 | role=qa, stage=work (predefinition) |
| TK-09 | T3 | plane-mvp context variant |
| TK-10 | T3 | stage=work, progress=70 |
| TK-11 | T3 | stage=analysis |
| TK-12 | T3 | stage=investigation |
| TK-13 | T3 | stage=work, blocked=true |
| TK-25 | T3 | task_type=subtask, skip_contributions=true |
| TK-27 | T3 | model=research, stage=investigation (spike) |
| TK-29 | T3 | verbatim=absent |
| TK-30 | T3+T5 | tier=capable |
| TK-31 | T3+T5 | tier=lightweight |
| TK-34 | T3 | role=engineer, stage=reasoning |
| TK-42 | T3 | concern variant — fleet_alert scenario |

Distribution: T1=2, T2=6 (+HB-20 with T5), T3=17 (+2 with T5), T4=1, T5=3-as-overlay.

## Duplication Inventory

Static duplication that would be eliminated by templating:

| Block | Copies today | Lines per copy | Total waste |
|-------|--------------|----------------|-------------|
| HEARTBEAT.md protocol | 7 (one per HB-*) | ~65 | ~455 |
| knowledge-context.md role block | 17 (one per T3) | ~90 | ~1,530 |
| Stage protocol MUST/MUST NOT | 17 (T3) × N stages | ~20 | duplicated per stage appearance |
| Standing orders block | 10 (in all T1/T2) | ~4 | ~40 |
| MODE header comment | 29 (all files) | ~3 | ~87 |

**Estimated total duplication:** ~2,100 lines that could compose from ~400 lines of shared template fragments.

## Implementation Considerations (Out Of Scope For This Doc)

If this generalization is adopted:

1. **Template engine choice:** Jinja2 (Python-native, already in stack via `tools/`) vs simple `str.format` vs our own stage-protocol composer. Jinja2 fits — skills, commands, many orchestrator paths already use it.
2. **Source of fragments:** `config/methodology.yaml` already holds stage protocols — the generator consumes them. `fleet/templates/validation-matrix/` would hold T1-T5 skeletons and overlay fragments (role blocks, tier projections).
3. **Scenario declarations:** a `validation-matrix/scenarios.yaml` enumerating each FL/HB/TK scenario with its template + parameter map. The 29 `.md` files become *generated outputs*, not sources.
4. **Round-trip invariant:** rendered output must remain `git diff`-clean vs the current handcrafted files after one-time curation. This is the externality check — if the generator produces different output than the handcrafted version, we know the template is missing a parameter.
5. **CI gate:** add a regeneration + diff check to catch drift (template change silently altering coverage scenarios). Same enforcement pattern as brain's `contribution-policy.yaml` compliance check.

## Risk — Why This Is Non-Trivial

- **Lossy compression risk:** Handcrafted scenarios carry subtle framing ("rejection feedback tone", "crisis focus wording") that parameter schemas will miss on first pass. Expect 2-3 iterations before coverage converges.
- **Parameter-space explosion:** T3's cartesian (6 stages × 7 models × 4 phases × 5 tiers × 3 task types × N role combinations) > 10K theoretical cells. Only ~17 exercised today. Template must NOT enumerate — it must parameterize lazily.
- **Coupling to methodology.yaml:** if methodology stages change, generator output changes, scenarios all regenerate. That's good for consistency but means validation-matrix stops being a stable reference corpus — it becomes a *derivation*. Consumers that used the files as fixtures need to treat them as generated artifacts.
- **Tradeoff vs brain's current citation:** brain cited our 29 handcrafted files as the proto-programming exemplar. Generalizing them *strengthens* the claim (structure-as-program becomes literal) but changes what brain links to. Coordinate via contribution.

## What This Analysis Is Not

This is a **design exploration**, not a plan or implementation. The template schema here is a first-cut hypothesis derived from 29-file structural reading; it will likely evolve during implementation. Concrete next actions are PO-gated:

- **PO approval required:** decision to proceed with generalization (affects fleet/templates/, config/, and brain-cited artifacts)
- **Upstream coordination required:** brain's citation in `structured-context-is-proto-programming-for-ai-agents.md` may need a follow-up note when generation lands

## Relationships

- DERIVED FROM: brain's [[structured-context-is-proto-programming-for-ai-agents|Structured Context Is Proto-Programming]] (explicit improvement vector)
- BUILDS ON: [[Methodology Models Rationale]] (stage × model table drives T3 parameterization)
- BUILDS ON: [[Context Injection Decision Tree]] (injection mode is the root split: T4 vs T1/T2/T3)
- BUILDS ON: [[Tier Rendering Design Rationale]] (T5 tier projections)
- RELATES TO: [[Critical Review Findings — Context Injection Scenarios]] (the scenarios this corpus validates against)
- RELATES TO: [[Validation Issues Catalog — Every Problem Found]]
- RELATES TO: [[Session — 2026-04-19 Brain Integration]] (safe-unilateral candidate flagged there)
- CONSTRAINS: any future addition to `validation-matrix/` — new scenarios should declare their template + parameters rather than be free-written
- FEEDS INTO: possible E002/E003 follow-on work if proto-programming pattern extends beyond validation into runtime context rendering
