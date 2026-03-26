# Phase 5: The Accountability Generator Drives Development

## Context

Phase 4 (M20-M25) proved the fleet works: agents specialize, tasks flow through Mission Control, code gets produced, multiple projects are targeted. Now the fleet has a real mission.

The Accountability Generator (ocf-tag) drives the development of its 3 core product dependencies while holding the fleet to high standards. Each milestone tests and evolves the tooling alongside the product work.

## Core Products to Build

| Product | ID | Description | Dependency |
|---------|-----|-------------|-----------|
| NNRT | 0 | Narrative-to-Neutral Report Transformer | Foundation — everything needs it |
| Factual Engine | 1 | Core reasoning and fact-processing | Depends on NNRT |
| Factual Platform | 3 | Public-facing delivery platform | Depends on Engine + NNRT |

## Principles

- ocf-tag sets requirements and holds agents accountable
- High standards, no regression
- Every deviation must be an improvement
- Each milestone tests the infrastructure AND produces product work
- Long journey — no compression, no shortcuts

---

## M26: ocf-tag as Driver — Requirements and Governance

**Goal**: ocf-tag defines what it needs from each product and how it will hold agents accountable.

**Work**:
1. ocf-tag agent (via Architect) produces requirements documents for each product:
   - NNRT requirements: what it must do, input/output formats, quality standards
   - Factual Engine requirements: reasoning capabilities, accuracy thresholds
   - Factual Platform requirements: user-facing features, persistence guarantees
2. ocf-tag defines acceptance criteria and quality gates
3. ocf-tag defines its governance role: how it reviews work, flags regressions, escalates
4. Create MC board groups: one per product (NNRT, Engine, Platform)
5. Create tasks in MC for the first design work

**Infrastructure tested**: Agent collaboration, MC board management, requirements flow

---

## M27: NNRT — Architecture and Design

**Goal**: Architect designs NNRT with ocf-tag reviewing the design.

**Work**:
1. Architect agent designs NNRT architecture:
   - Input: narrative text (news articles, press releases, speeches, social media)
   - Processing: bias detection, framing identification, fact extraction, language neutralization
   - Output: neutral factual report with sourced claims
2. ocf-tag reviews the architecture against its requirements
3. Architect revises based on ocf-tag feedback
4. Final design approved and documented

**Infrastructure tested**: Agent-to-agent review flow, iterative design, requirements enforcement

---

## M28: NNRT — Foundation Implementation

**Goal**: Engineer builds NNRT foundation with QA testing and ocf-tag validating.

**Work**:
1. Scaffold NNRT as a new project (or module in OCF)
2. Engineer implements core pipeline:
   - Text ingestion
   - Sentence-level analysis
   - Bias/framing detection (rule-based first, ML later)
   - Neutral rewrite generation
   - Source attribution
3. QA writes comprehensive tests
4. ocf-tag validates output quality against requirements
5. Technical Writer documents the API

**Infrastructure tested**: Full fleet collaboration, multi-file code generation, test-driven development

---

## M29: NNRT — Iteration and Quality

**Goal**: Improve NNRT based on real test cases. ocf-tag drives the quality bar.

**Work**:
1. ocf-tag provides test cases: real narrative texts that must be neutralized
2. Engineer + QA iterate on accuracy
3. ocf-tag reviews each iteration: does it meet the standard?
4. Regression tests added for every fixed case
5. Performance benchmarks established

**Infrastructure tested**: Iterative improvement loop, regression prevention, quality metrics

---

## M30: Factual Engine — Architecture

**Goal**: Architect designs the Factual Engine with NNRT as a dependency.

**Work**:
1. Architect designs:
   - Fact verification pipeline
   - Confidence scoring
   - Contradiction detection
   - Source chain tracking
   - Claim-to-outcome linking
2. Design integrates with NNRT (neutralized input) and Intake layer (structured data)
3. ocf-tag reviews against requirements
4. Architecture documented and approved

**Infrastructure tested**: Cross-product design, dependency management

---

## M31: Factual Engine — Core Implementation

**Goal**: Engineer builds Factual Engine core with full testing.

**Work**:
1. Implement:
   - Fact extraction from neutralized text
   - Confidence scoring algorithm
   - Contradiction detection between claims
   - Source chain builder
2. Integration with NNRT and Intake layer
3. QA comprehensive testing
4. ocf-tag validates reasoning quality

**Infrastructure tested**: Multi-module integration, complex business logic

---

## M32: ocf-tag Layer 2 — Structuring

**Goal**: With NNRT and Factual Engine available, build Layer 2.

**Work**:
1. Structuring layer:
   - Normalize intake data using NNRT
   - Score confidence using Factual Engine
   - Detect contradictions
   - Build actor-decision-impact chains
2. Integration tests with Layer 1 (Intake)
3. ocf-tag self-validates: does the structuring meet its own standards?

**Dependency**: NNRT (M28-29) + Factual Engine (M31)

---

## M33: Factual Platform — Architecture

**Goal**: Architect designs the public-facing platform.

**Work**:
1. Platform architecture:
   - Web application (what framework, what hosting)
   - Public API for querying accountability data
   - Dashboard for accountability scores
   - Persistence layer (nothing disappears)
   - Search and discovery
2. UX Designer proposes interface
3. ocf-tag reviews against platform requirements
4. Architecture approved

**Infrastructure tested**: UX agent involvement, platform design

---

## M34: Factual Platform — Foundation

**Goal**: Build the initial platform scaffold.

**Work**:
1. Scaffold the web application
2. Implement:
   - Public read API
   - Basic dashboard
   - Claim/evidence viewer
   - Search
3. Connect to Factual Engine and NNRT
4. DevOps sets up deployment
5. QA tests, ocf-tag validates

**Infrastructure tested**: Full-stack development, DevOps agent, deployment

---

## M35: ocf-tag Layers 3-4 — Mapping and Pressure Generation

**Goal**: With platform available, build the high-impact layers.

**Work**:
1. Layer 3 (Mapping):
   - Responsibility chains
   - Knowledge graphs
   - Consequence maps
   - Visualization via Factual Platform
2. Layer 4 (Pressure Generation):
   - Accountability reports via NNRT
   - Public dashboards via Platform
   - Contradiction flags via Factual Engine
   - Accountability scores

**Dependency**: All 3 products at sufficient maturity

---

## M36: ocf-tag Layer 5 — Persistence

**Goal**: The final layer — nothing disappears.

**Work**:
1. Immutable audit trail
2. Edit visibility (all changes tracked)
3. Claim-to-outcome linking across time
4. Narrative reset prevention
5. Integration with Factual Platform for public persistence

---

## M37: Hardening — Gateway, Skills, Infrastructure

**Goal**: Harden everything that was built along the way.

**Work**:
1. Gateway: proper service management, error recovery, monitoring
2. Skills: test every skill against real projects, fix what's broken
3. MC integration: explore approval flows, webhooks, board groups fully
4. CI/CD for all projects
5. Documentation pass across everything
6. Regression test suite for the full system

---

## M38: Fleet Maturity — Agent Evolution

**Goal**: Agents evolve based on what was learned.

**Work**:
1. Review agent CLAUDE.md files — are they accurate after all this work?
2. Add specialized skills per agent based on proven workflows
3. Create reusable pipeline templates for common agent collaboration patterns
4. ocf-tag retrospective: what worked, what didn't, what to improve
5. Plan next phase

---

## Dependency Graph

```
M26 (ocf-tag requirements)
  │
  ├── M27 (NNRT design)
  │     │
  │     ├── M28 (NNRT implementation)
  │     │     │
  │     │     └── M29 (NNRT iteration)
  │     │
  │     └──────────────── M30 (Engine design)
  │                         │
  │                         └── M31 (Engine implementation)
  │                               │
  │                               └── M32 (ocf-tag Layer 2)
  │
  ├── M33 (Platform design)
  │     │
  │     └── M34 (Platform foundation)
  │           │
  │           └── M35 (ocf-tag Layers 3-4)
  │                 │
  │                 └── M36 (ocf-tag Layer 5)
  │
  └── M37 (Hardening) ── runs alongside everything
        │
        └── M38 (Fleet maturity)
```

## Notes

- M33-34 can start in parallel with M30-31 (Platform design doesn't need Engine)
- M37 (Hardening) is ongoing, not a single milestone — it happens throughout
- Each milestone should produce working, tested, documented output
- ocf-tag is involved in EVERY milestone as reviewer and requirements enforcer
- This is 13 milestones (M26-M38). At the current pace, this is substantial work.