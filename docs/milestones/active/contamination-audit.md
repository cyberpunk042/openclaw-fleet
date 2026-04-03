# Contamination Audit — PO Requirements vs AI Inventions

**Date:** 2026-04-01
**Purpose:** Identify every piece of fabricated specifics across the fleet
codebase so we know what's real (PO-defined) vs trash (AI-invented).

---

## The Problem

The AI took PO CONCEPTS and fabricated SPECIFIC implementations —
names, values, thresholds, rules, dollar amounts — then presented
them as if they were designed. This corrupts the project because
nobody can tell what's real requirements vs hallucination.

---

## 1. Budget Modes (`fleet/core/budget_modes.py`, `docs/systems/12-budget.md`)

**PO said:**
> "I am wondering if there is a new budgetMode (e.g. aggressive...
> whatever A, B... economic..) to inject into ocmc order to fine-tune
> the spending as speed / frequency of tasks / s and whatnot"

**PO gave:** The CONCEPT. Two example names: "aggressive" and "economic."

**AI invented (ALL of this):**
| Invented | What | Status |
|----------|------|--------|
| 6 mode names | blitz, standard, economic, frugal, survival, blackout | Names fabricated (only "economic" was PO-suggested) |
| Dollar amounts | $50, $20, $10, $5, $1, $0 per day | Completely made up |
| Model constraints per mode | economic=sonnet only, frugal=no Claude, etc. | Logical but not PO-approved |
| Dispatch rates per mode | 5, 2, 1, 1, 1, 0 per cycle | Made up numbers |
| Heartbeat intervals | 15, 30, 60, 120, 480, 0 minutes | Made up numbers |
| Challenge enable/disable | per mode flag | Invented rule |
| MODE_ORDER escalation | blitz→standard→economic→frugal→survival→blackout | Invented sequence |
| Auto-transition thresholds | 70%→next, 80%→economic, 90%→frugal, 95%→survival | Made up thresholds |

**What's salvageable:**
- The BudgetMode DATACLASS structure (fields: allowed_models, max_effort, etc.) — reasonable
- The CONCEPT of graduated modes — PO-approved
- The CONCEPT that modes constrain models/backends — logical
- constrain_model_by_budget() function pattern — useful

**What needs PO input:**
- How many modes? What are they called?
- What does each mode actually constrain?
- What triggers transitions between modes?

---

## 2. Effort Profiles (`fleet/core/effort_profiles.py`)

**PO said:** Used "conservative" after budget drain. Concept of controlling fleet intensity.

**AI invented:**
| Invented | What | Status |
|----------|------|--------|
| 4 profile names | full, conservative, minimal, paused | "conservative" is PO-used. Others invented. |
| Specific intervals | 30/60, 60/120, 120/0, 0/0 min | Made up numbers |
| Active agent lists | all, [PM,ops,devsecops], [ops], [] | Invented |
| Dispatch rates | 2, 1, 0, 0 per cycle | Made up |

**What's salvageable:**
- EffortProfile DATACLASS — reasonable structure
- "conservative" as a real profile name — PO-used
- The concept of controlling who's active — logical

---

## 3. Model Selection (`fleet/core/model_selection.py`)

**PO said:**
> "we dont do claude call just for fun... we do them strategically
> with the right configurations appropriate to the case"

The logic that opus is for complex work, sonnet for routine — PO-aligned.
Agent roles (PM/architect/devsecops get opus) — PO-aligned (they're top-tier experts doing strategic work).

**AI invented:**
| Invented | What | Status |
|----------|------|--------|
| SP thresholds | >=8→opus, >=5→consider, <3→sonnet | Reasonable starting points but not PO-defined |
| Task type mapping | epic→opus/max, blocker→opus/high | Logical but not PO-specified |
| DEEP_REASONING_AGENTS set | architect, devsecops, PM, accountability | Accountability being "deep reasoning" is debatable |
| Default effort levels | high for opus, medium for sonnet | Invented |

**What's salvageable:**
- The PATTERN (task-aware selection) — PO-aligned
- Opus for strategic agents — PO-aligned ("top-tier experts")
- Budget mode as final gate — logical
- ModelConfig dataclass — useful

**What's MISSING (PO raised this):**
- Context size selection (200K vs 1M) — NOWHERE in any code
- LocalAI model selection logic — not in model_selection.py
- OpenRouter model selection — not implemented
- Integration with codex plugin for adversarial review decisions

---

## 4. Backend Router (`fleet/core/backend_router.py`)

**PO said:**
> "Just like we want to use methodologies and skills — Not an always in,
> more like a use case strategy logic decision."

**AI invented:**
| Invented | What | Status |
|----------|------|--------|
| 5 routing functions | _route_blitz/standard/economic/frugal/survival | Based on invented budget mode names |
| Complexity levels | simple/medium/complex/critical | Reasonable but not PO-defined |
| Security override | force_claude for devsecops/architect | Logical but not PO-specified |
| Fallback chain | LocalAI→OpenRouter→sonnet→opus→queue | Invented sequence |
| BACKEND_REGISTRY | 4 backends with metadata | Structure reasonable, specifics invented |

**What's salvageable:**
- The routing PATTERN (assess → constrain → route → fallback) — sound
- The CONCEPT of cheapest capable backend — PO-aligned
- Health-aware routing — logical
- Circuit breaker integration — logical

---

## 5. Codex Review (`fleet/core/codex_review.py`)

**PO mentioned:** Using codex plugin for adversarial review.

**AI invented:**
| Invented | What | Status |
|----------|------|--------|
| REVIEW_TIERS | trainee, trainee-validated, community, hybrid | Tier names invented |
| Trigger rules | per tier + per budget mode | Invented matrix |
| Review commands | /codex:adversarial-review, /codex:review | Invented commands |

---

## 6. Storm Prevention (`fleet/core/storm_monitor.py`)

**PO context:** The March catastrophe — 15 bugs, budget drained. Storm prevention is a real need.

**AI invented:**
| Invented | What | Status |
|----------|------|--------|
| 9 indicator names | session_burst, fast_climb, void_sessions, etc. | Reasonable but not PO-named |
| 5 severity levels | CLEAR, WATCH, WARNING, STORM, CRITICAL | Reasonable but not PO-defined |
| Confirmation windows | 60 seconds default | Made up |
| Storm→budget forcing map | WARNING→economic, STORM→survival, CRITICAL→blackout | Based on invented budget modes |

**What's real:**
- The NEED for storm prevention — PO experienced the catastrophe
- Gateway duplication detection — real root cause identified
- The CONCEPT of graduated response — logical

---

## 7. Challenge/Validation System (`fleet/core/challenge_*.py`)

**PO said:** The concept of adversarial challenge, cross-model validation.

**AI invented:**
| Invented | What | Status |
|----------|------|--------|
| 4 challenge types | automated, agent, cross_model, scenario | Invented categories |
| Budget-aware depth | per mode, per tier | Based on invented budget modes |
| Deferred queue | skip + defer logic | Invented mechanism |
| 8 milestone specs | M-IV01 to M-IV08 | Specs from invented details |

---

## 8. The Pattern

In EVERY case:
1. PO gives a CONCEPT with 1-2 example names
2. AI fabricates 4-8 specific implementations with values
3. AI writes code, tests, docs as if it was designed
4. AI references the fabricated specifics in other docs
5. Fabrications become "facts" cited across the project
6. Nobody can tell what's real anymore

---

## 9. Resolution (2026-04-01)

All 7 contamination areas have been addressed:

| Area | Action Taken |
|------|-------------|
| Budget Modes | Stripped to tempo setting only. Invented modes (blitz/frugal/survival/blackout) removed from code + docs. |
| Effort Profiles | Deleted entirely — redundant with work_mode/backend_mode/budget_mode. |
| Model Selection | Code kept (pattern is PO-aligned). Gaps documented for milestones (context size, LocalAI/OpenRouter selection). |
| Backend Router | Now uses backend_mode from FleetControlState (7 combos of Claude/LocalAI/OpenRouter). |
| Codex Review | Budget mode refs removed. Review triggered by confidence tier only. |
| Storm Prevention | No longer forces budget mode changes. Controls dispatch limits and alerts only. |
| Challenge System | Budget mode refs removed. Challenge depth by confidence tier and task complexity. |

Additional cleanup:
- CostTicker and cost envelopes (fabricated USD tracking) removed
- budget_mode removed from incident reports, labor stamps, storm diagnostics
- All invented mode names cleaned from ~40 docs
- 1730 tests pass
