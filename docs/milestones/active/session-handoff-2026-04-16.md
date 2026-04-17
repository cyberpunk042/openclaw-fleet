# Session Handoff — 2026-04-16

## Honest State

**TK-01 is ready for PO review.** 216 lines, 9020 chars. All 10 autocomplete chain sections populated with real content. Tier adaptation produces distinctly different output across expert/capable/lightweight. Model selection routes correctly across scenarios. 29 scenarios generated, 1 near-complete (TK-01), 28 partial.

**We are NOT done.** Only TK-01 has been brought to a high-value state. The other 28 scenarios are functional but have gaps (no events, static knowledge fallback, simpler confirmed plans). 62+ leaves from the 91+ decision tree still need scenarios. Zero scenarios are PO-CONFIRMED.

**2453 tests passing, 19 skipped. Clean working tree. All work on main.**

## Direction Forward

**Integrate with the second-brain** at `/home/jfortin/devops-solutions-research-wiki` (also known as `devops-solutions-information-hub` — same thing, different symlink name). This is the canonical wiki that the PO has been building. Even though it's unfinished, we read, absorb, integrate, and give inputs.

### Second-brain structure to absorb

- **wiki/spine/** — strategic architecture: 16 models, 15 page type standards, methodology system, adoption guide, evolution log
- **wiki/spine/models/foundation/** — model-llm-wiki.md, model-methodology.md, model-wiki-design.md (we've been referencing the first two; wiki-design is new)
- **wiki/spine/super-model/** — super-model composition (unexplored)
- **wiki/domains/** — domain-specific knowledge
- **wiki/patterns/**, **wiki/lessons/**, **wiki/decisions/**, **wiki/comparisons/**, **wiki/sources/** — the layered knowledge architecture
- **wiki/log/** — directives, session records, evolution notes

### 15 page types with standards (new to us)

concept, source-synthesis, comparison, reference, deep-dive, lesson, pattern, decision, domain-overview, evolution, learning-path, operations-plan, epic, task, note. Each has standards defining section-by-section quality bar, gold-standard exemplar, common failures, content thresholds, template reference.

**Our OpenFleet wiki/ uses some of these types but not the standards.** Examples: we have `type: concept` and `type: reference` pages but haven't applied the section quality bars. The second-brain has exemplars for each.

### Integration approach

1. **Read spine models first** — foundation/model-llm-wiki.md, foundation/model-methodology.md, foundation/model-wiki-design.md. We've partially integrated the first two; the third is new.
2. **Read page type standards** — understand what a concept page, a pattern page, a decision page are supposed to look like.
3. **Review our OpenFleet wiki/ against the standards** — many pages are drafts that don't meet the second-brain's quality bar.
4. **Provide input back** — the PO explicitly wants us to give inputs. Things we've learned building OpenFleet that should feed into the second-brain's methodology system, LLM wiki model, and page standards.

## What Was Delivered This Session

### Code fixes (8)

1. **Model selection clause evaluator** ([methodology_config.py:132-222](../../fleet/core/methodology_config.py#L132-L222)) — proper AND support, all 6 rules evaluated correctly, priority parameter added. Replaced hand-rolled string splitting that silently ignored AND clauses.
2. **YAML Rule 4 fixed** ([methodology.yaml:382](../../config/methodology.yaml#L382)) — `urgency = critical` → `priority = urgent`. The old rule referenced a field that didn't exist in the data model.
3. **Contribution marker preserved** ([preembed.py:344](../../fleet/core/preembed.py#L344)) — stopped stripping `<!-- CONTRIBUTIONS_ABOVE -->`. Both orchestrator and generator can now insert content at the marker.
4. **Fleet state in task preembed** ([preembed.py](../../fleet/core/preembed.py), [orchestrator.py:670](../../fleet/cli/orchestrator.py#L670)) — `# FLEET:` line in §0, passed from orchestrator fleet_state_dict.
5. **Contribution depth `status_only` and `summary`** ([preembed.py:268-285](../../fleet/core/preembed.py#L268-L285)) — previously fell through to `full_inline`. Now capable tier shows status-only, flagship shows summary.
6. **heartbeat_context.py dead code removed** ([heartbeat_context.py:296-298](../../fleet/core/heartbeat_context.py#L296-L298)) — wrong parameter call caught by bare except, silently failed. Removed.
7. **Structured `[CONFIRMED_PLAN]` marker** ([comment.py:22-28](../../fleet/templates/comment.py#L22-L28), [orchestrator.py:627-633](../../fleet/cli/orchestrator.py#L627-L633)) — fleet_task_accept comments now have explicit marker. Orchestrator loader uses marker first, falls back to substring matching.
8. **Navigator role-filtered methodology tables** ([navigator.py:444-524](../../fleet/core/navigator.py#L444-L524)) — methodology-manual.md tables have role annotations like `(devops)`, `(QA, engineer)`. Navigator now filters table rows to keep only engineer-relevant entries for engineer-work intent.

### Generator improvements (6)

- Navigator.assemble() integrated — real knowledge-context.md from 90+ KB entries
- Design plan fixture replaces TODO list (architecture, data flow, target files, patterns, constraints, acceptance criteria mapping)
- WHAT CHANGED event fixtures for TK-01
- Fleet state passed to all scenarios
- Data shape fixes: contributions_received dict shape, blocked_details, ID truncation, parent_task_title
- Capable tier scenarios correctly omit inline contribution content (tier depth = status_only)

### Navigator tuning

- Agent manual depth changed from `full` to `condensed` ([injection-profiles.yaml:27](../../docs/knowledge-map/injection-profiles.yaml#L27)) — the full identity is already in SOUL.md/CLAUDE.md static files
- Methodology section covers tools/skills/commands/MCP/plugins via its tables — Navigator skips the intent-specific branches for these to avoid duplication ([navigator.py:267-303](../../fleet/core/navigator.py#L267-L303))
- Parenthetical content filtered for role keywords only — `(FIRST)`, `(required before commits)` are kept (usage notes), `(devops)`, `(QA, engineer)` are filtered (role annotations)

### Tests (31 new)

- 18 model selection tests ([test_methodology_models.py](../../fleet/tests/core/test_methodology_models.py)) — 10 clause evaluator + 8 integration against real YAML rules
- 13 tier rendering tests ([test_tier_renderer.py](../../fleet/tests/core/test_tier_renderer.py) appended) — protocol trimming (4), adaptations (2), role data (4), action edge (1), source string integrity (1), flagship depth (1)

### Wiki artifacts (9)

- Analysis: [Context Injection Blockers](../../wiki/domains/architecture/analysis-context-injection-blockers.md)
- Investigation: [Context Injection Blocker Solutions](../../wiki/domains/architecture/investigation-context-injection-blockers.md)
- Plan: [Context Injection Blocker Fixes](../../wiki/domains/architecture/plan-context-injection-blockers.md) — execution plan for bugfix
- Analysis: [Output Quality Blockers](../../wiki/domains/architecture/analysis-output-quality-blockers.md) — 10 systemic issues preventing 200+ lines
- Investigation: [Output Quality Solutions](../../wiki/domains/architecture/investigation-output-quality-blockers.md)
- Plan: [TK-01 Golden Path](../../wiki/domains/architecture/plan-output-quality-tk01.md) — design plan
- Directive: [Plan Types](../../wiki/log/2026-04-11-directive-plan-types.md) — design plan vs operations plan distinction

## What Is NOT Done

### Scenarios still partial (28 of 29)

Only TK-01 has all features visible. Others have:
- Static knowledge fallback instead of Navigator
- No WHAT CHANGED events
- Simpler or missing confirmed plans (TK-03, TK-04, TK-09 before fix)
- Data shapes may still diverge from real providers in edge cases

### Scenarios not yet created (~62)

Gaps vs 91+ leaves in the decision tree:
- Documentation model (technical-writer task)
- Review model (fleet-ops fleet_approve flow)
- Hotfix model (blocker + urgent)
- Flagship_local tier (any stage)
- Heartbeat × capable or lightweight tier
- Analysis/investigation/reasoning at capable tier
- Analysis/investigation/reasoning at lightweight tier
- Multiple-tasks heartbeat
- Partial contribution received (some received, some missing)
- Progress milestones 80% (challenged), 90% (reviewed)
- Crisis/planning phase × task dispatch (not just heartbeat)

### Open design questions

- **tools_blocked per-model-per-stage** ([directive](../../wiki/log/2026-04-10-directive-multi-level-tasks.md)) — still global per-stage, PO identified this needs rethinking
- **context_assembly.py vs preembed.py** — two separate paths, context_assembly has richer data (comments, Plane artifacts, related tasks) that preembed lacks
- **Knowledge-map KB content gaps** — `fleet-engineer-workflow`, `fleet-contribution-consumption`, `fleet-conventional-commits`, `fleet-completion-checklist` referenced in intent-map but no KB entries exist (Navigator shows names only)
- **Second-brain page type alignment** — our wiki/ pages don't follow the 15 page type standards from the second-brain

## Anti-Patterns That Must Be Respected

The 15 anti-patterns from 2026-04-09 still apply. New ones identified this session:

16. **Presenting unfinished work as done.** Presented TK-01 multiple times claiming it was ready when the contribution content was missing, no events, generic protocol. The PO had to point out each time. Rule: review the output critically yourself before presenting.

17. **Jumping to quickfixes when the problem is systemic.** Tried to patch the marker stripping as a single edit when the output had 10 systemic issues. PO rejected multiple times. Rule: when every feature is absent from output, it's a design problem, not a bug.

18. **Skipping methodology stages.** Asked the PO what they think, jumped to code, dumped analysis+investigation+reasoning in one wall of text. The PO literally wants methodology stages followed: analysis (produce doc) → investigation (produce doc) → reasoning (produce plan) → work. Each stage pauses for review.

19. **Confusing operations plan with design plan.** Wrote "1. Create X. 2. Implement Y." and called it a plan. PO: "A plan is what we deliver and how we reach there, not a list of steps." Design plans describe architecture; operations plans are personal TODO lists not worth documenting.

20. **Inventing understanding instead of reading.** Listed "20+ systems" from general impression rather than reading each one. PO: "you are inventing everything out of hallucination." Must read each system's code and config before claiming understanding.

## Key References for Next Session

### OpenFleet

- [CLAUDE.md](../../CLAUDE.md) — Work Mode, Methodology, Documentation Layers, Current Focus
- [wiki/domains/architecture/context-injection-tree.md](../../wiki/domains/architecture/context-injection-tree.md) — 91+ leaf decision tree
- [wiki/domains/architecture/analysis-output-quality-blockers.md](../../wiki/domains/architecture/analysis-output-quality-blockers.md) — the 10 systemic issues and their resolutions
- [validation-matrix/TK-01-work-full-contrib.md](../../validation-matrix/TK-01-work-full-contrib.md) — the golden path for PO review

### Second-brain (NEW FOCUS)

- `/home/jfortin/devops-solutions-research-wiki/wiki/spine/_index.md` — entry point, 16 models, 15 page types
- `/home/jfortin/devops-solutions-research-wiki/wiki/spine/models/foundation/model-llm-wiki.md`
- `/home/jfortin/devops-solutions-research-wiki/wiki/spine/models/foundation/model-methodology.md`
- `/home/jfortin/devops-solutions-research-wiki/wiki/spine/models/foundation/model-wiki-design.md` (not yet integrated)
- `/home/jfortin/devops-solutions-research-wiki/wiki/spine/super-model/` (unexplored)
- Page type standards: concept-page-standards, pattern-page-standards, decision-page-standards, lesson-page-standards, reference-page-standards, etc.

## What the Next Session Should Do

**Phase 1: Read and absorb the second-brain** (do NOT rush)
1. Read `/home/jfortin/devops-solutions-research-wiki/wiki/spine/_index.md` — overview
2. Read each foundation model (llm-wiki, methodology, wiki-design)
3. Read super-model documents
4. Read the 15 page type standards — understand what each page type requires
5. Read domain overviews and several exemplar pages to see quality bar

**Phase 2: Identify integration points**
1. Compare our OpenFleet wiki/ structure to the second-brain structure
2. Identify which page types we have and which we're missing
3. Identify which of our pages don't meet the standards
4. Identify what OpenFleet learnings should feed into the second-brain

**Phase 3: Provide inputs back to the second-brain**
The PO wants us to give inputs. We've built a real context injection system — our learnings about:
- Tier-aware rendering (quality dimension at implementation level)
- Named methodology models with protocol_adaptations
- The 5 documentation layers in practice
- 15+20 anti-patterns from this session chain
...should feed back into the second-brain's methodology and standards.

**Phase 4: Only after alignment — continue scenario validation**
With the second-brain integration understood, return to validating TK-01 line by line, then TK-02, then onward through the tree. The scenarios must demonstrate the shared models correctly.

## Critical PO Directives (MUST remember)

1. "A plan is what we deliver and how we reach there" — not a list of steps
2. "Do not overestimate progress" — we're back on track, not done
3. "I would not overwhelm my trainee" — tier adaptation is about what the model can HANDLE, not what fits
4. "Work on main. No branches. No worktrees. No subagent ceremonies."
5. "PO confirms each scenario line by line — zero auto-approval"
6. "Analysis → investigation → reasoning → work — do not skip stages"
7. "The shared models apply at all levels: solo, assistant, fleet, platform"
8. "For things to become simple in programming they have to become complex first"
9. "Ops board tasks ≠ Plane tasks — different levels" (see [directive](../../wiki/log/2026-04-10-directive-multi-level-tasks.md))
10. "LLM Wiki IS the standard for ALL projects — no regression"

## Metrics

- 2453 tests passing (was 2423 at handoff 2026-04-10)
- 29 scenarios generated (same count, TK-01 dramatically improved)
- TK-01: 216 lines, 9020 chars (was 88 lines, 2546 chars)
- 44 files changed, 9 new wiki artifacts
- All work on main, clean tree, committed
