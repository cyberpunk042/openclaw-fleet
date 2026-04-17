# Methodology Profiles

## What Is a Methodology Profile?

A methodology profile defines **HOW stages are executed** — what is emphasized,
what flows first, which artifacts matter most, and what signature practices
characterize the style.

It is NOT:

| It is not... | Because... |
|---|---|
| An SDLC profile | SDLC profiles (`wiki/config/sdlc-profiles/`) define project-level policy: how much methodology a project needs, enforcement level, upgrade triggers |
| A methodology model | Models (`wiki/config/methodology.yaml`) define named sequences (feature-development, bug-fix, research) — which stages apply and what artifacts they require |
| A domain profile | Domain profiles (`wiki/config/domain-profiles/`) define technology-specific overrides: gate commands, path patterns, forbidden zones |
| A replacement for methodology.yaml | Profiles LAYER ON TOP of methodology.yaml definitions — they do not duplicate or replace them |

**The relationship:**

```
methodology.yaml         — universal stage vocabulary, models, artifact chains
  + SDLC profile         — project-level policy (how much methodology?)
  + domain profile       — technology-specific overrides (how to run gates?)
  + methodology profile  — execution EMPHASIS (what to prioritize within stages?)
```

All four compose together. A project may run the `default` SDLC profile,
the `typescript` domain profile, and the `spec-driven` methodology profile
simultaneously. There is no conflict — they operate on different dimensions.

---

## Why Profiles Exist

Classic methodology assumes a generic context. AI-era development has fractured
into distinct workflows that require different emphasis:

- **Spec-driven workflows** need heavy Document stages producing executable specs.
  The rest of the pipeline flows from those specs mechanically.

- **Multi-persona AI workflows** need phase-based collaboration between specialized
  agents. The concept of "stages" maps to "phases" with different artifacts.

- **Test-driven workflows** invert the scaffold stage: tests are written with
  real assertions before implementation exists. Placeholders are anti-patterns.

- **Standard stage-gated workflows** distribute effort evenly. Every stage gets
  deliberate attention. No single stage dominates.

Profiles capture these differences as machine-parseable configuration rather
than informal conventions that get forgotten between sessions.

---

## The 4 Profiles

### 1. `stage-gated` — The Goldilocks Default

**Style:** Balanced progress through all five stages with enforced gates.

**When to use:** Most features, modules, and epics. New domains. Projects where
the solution is not fully known and thorough documentation prevents rework.

**Key characteristics:**
- Uniform effort distribution across all 5 stages
- Every stage transition has explicit gate checks
- Integration-wiring is a required artifact (proves new code is reachable)
- Iterative depth: document stage is multi-pass, not one-shot
- Compatible with all SDLC profiles

**What this wiki already does.** Naming it makes it selectable and comparable.

---

### 2. `spec-driven` — Specs as Source of Truth

**Style:** Heavy Document stage producing executable specs that GENERATE the plan.

**When to use:** Compliance-driven work. API contracts with external parties. Features
where rework cost is very high. Large features spanning multiple sessions or agents
(spec is the handoff artifact).

**Key characteristics:**
- Document stage carries ~45% of total effort
- Constitution-md (9 articles) is required before design begins
- `[NEEDS CLARIFICATION]` markers block stage advancement until resolved
- Research agents run concurrently with spec authoring
- Plan is GENERATED from spec sections — traceability is bidirectional
- Spec checklists become test stubs; test stubs become assertions

**Sources:** spec-kit (GitHub), OpenSpec framework.

---

### 3. `agile-ai` — Multi-Persona AI Collaboration

**Style:** Multiple specialized personas across Analysis → Planning → Solutioning →
Implementation phases. Party mode activates all personas in one session.

**When to use:** Strategic features needing multiple expertise domains. Ambiguous
epics where structured exploration is needed before committing. PRFAQ stress-testing
before large builds.

**Key characteristics:**
- 5 personas: PM, Architect, Developer, UX, TEA
- PRFAQ (working-backwards press release + FAQ) required for large features
- 60+ structured brainstorming techniques — AI as facilitator, not generator
- Phase → stage mapping: Analysis/Planning/Solutioning/Implementation
- Persona sign-off gates at stage transitions
- Party mode: all personas active in one session for kickoffs

**Sources:** BMAD (Breakthrough Method for Agile AI Development).

---

### 4. `test-driven` — Tests Before Code

**Style:** Failing tests as specifications. Red → Green → Refactor as atomic cycle.
Scaffold tests have REAL assertions, not placeholders.

**When to use:** Critical path code where regressions are costly. Library or utility
code with well-defined interfaces. Refactoring work where behavior must be preserved.
Pairs with spec-driven (spec checklists become test cases).

**Key characteristics:**
- Test list required as a Design stage artifact (before any scaffold)
- Scaffold tests must FAIL — error ≠ red, skip ≠ red
- Implement stage: make one test pass at a time, then refactor
- Single-step refactor: one change, run tests, repeat
- Bug-test-first: write a failing test for the bug before fixing it
- Coverage is a minimum gate, not a maximization target

---

## Choosing a Profile

| Situation | Recommended Profile |
|---|---|
| Standard feature in a production project | `stage-gated` |
| Compliance requirement, external API contract | `spec-driven` |
| Large strategic epic with ambiguous scope | `agile-ai` |
| Critical-path module, refactor, library | `test-driven` |
| Exploratory research spike | `stage-gated` with `research` model |
| Emergency with known fix | `stage-gated` with `hotfix` model |
| Spec exists, tests need to be authored first | `spec-driven` + `test-driven` together |

Profiles may be COMBINED. `spec-driven` + `test-driven` is a natural pair:
spec checklists become the test list; test list drives scaffold; scaffold produces
real failing tests derived from spec requirements.

---

## How Profiles Compose with Other Configuration

A project's effective methodology is the intersection of four layers:

```
1. methodology.yaml          — what stages and artifacts EXIST
2. SDLC profile              — which models are available, enforcement level
3. domain profile            — how gate commands are run, which paths are forbidden
4. methodology profile       — which artifacts to emphasize, signature practices
```

A profile CANNOT:
- Enable a stage that methodology.yaml does not define
- Override a domain profile's forbidden zone rules
- Bypass SDLC enforcement policy (e.g. required stage_gates)

A profile CAN:
- Shift effort weights between stages (document 45% vs 20%)
- Promote certain artifacts to required (where methodology.yaml marks them optional)
- Define signature practices that characterize the workflow style
- Restrict available models to those that fit the style
- Map non-standard phase names (e.g. BMAD's Analysis/Planning) to standard stages

The profile is a LENS, not an override. Methodology.yaml remains authoritative.

---

## Stage Emphasis and Artifact Preferences

Each profile's `stage_emphasis` block defines:

- `weight` — relative effort fraction (all weights across a profile should sum to ~1.0)
- `primary_artifacts` — what to produce in this stage (subset of methodology.yaml's allowed outputs)
- `key_gate_checks` — what must be true to advance (may add checks on top of methodology.yaml's defaults)

The `artifact_preferences` block marks artifacts as `preferred` or `deprioritized`.
These are GUIDANCE — they do not override methodology.yaml's `required` designations.
A deprioritized artifact that is `required` in methodology.yaml for a given model
is still required.

---

## Adding a New Profile

1. Identify the execution STYLE that needs to be captured. Ask:
   - Which stage carries the most effort? Why?
   - What signature practices characterize this workflow?
   - What artifacts are produced that standard methodology.yaml doesn't emphasize?
   - When is this profile the RIGHT choice vs. overkill?

2. Create `wiki/config/methodology-profiles/<name>.yaml` following the schema in
   the existing profiles. Required top-level keys:
   - `profile`, `description`, `style`
   - `derived_from` — source of the methodology inspiration (wiki page or external)
   - `applicability` — `best_for`, `not_for`, `compatible_with_sdlc_profiles`
   - `stage_emphasis` — all 5 stages with `weight`, `primary_artifacts`, `key_gate_checks`
   - `artifact_preferences` — `preferred` and `deprioritized` lists
   - `models` — subset of models available under this profile
   - `signature_practices` — 3-6 named practices that define the style
   - `adoption` — `prerequisites`, `typical_onboarding_time`, `migration_from_stage_gated`

3. Aim for 60-120 lines. A stub is useless — be substantive. Reference real source
   pages by slug where the methodology came from.

4. Add the profile to this README's "The 4 Profiles" section and the choosing table.

5. Run `python3 -m tools.pipeline post` to validate.

---

## File Index

| File | Profile | Style |
|---|---|---|
| `stage-gated.yaml` | Stage-Gated | Balanced 5-stage execution with enforced gates |
| `spec-driven.yaml` | Spec-Driven | Heavy Document → spec generates plan → mechanical downstream |
| `agile-ai.yaml` | Agile-AI | Multi-persona phases with party mode and PRFAQ |
| `test-driven.yaml` | Test-Driven | Red → Green → Refactor, real assertions before implementation |

---

## Related Configuration

- `wiki/config/methodology.yaml` — universal stage vocabulary and model definitions
- `wiki/config/sdlc-profiles/` — project-level enforcement policy
- `wiki/config/domain-profiles/` — technology-specific gate commands and path patterns
- `wiki/spine/models/foundation/model-methodology.md` — narrative explanation of models
- `wiki/spine/references/methodology-system-map.md` — full system map for navigation
