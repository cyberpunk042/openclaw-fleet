# The Accountability Generator — Full Vision

## Role in the Fleet

The Accountability Generator (ocf-tag) is not just an agent — it is a **driver**. It drives the development of its own dependencies by holding other agents accountable. It sets requirements, enforces standards, catches regressions, and ensures every deviation is an improvement.

## Core Products (Dependencies)

ocf-tag cannot deliver its mission until these products reach sufficient maturity:

### 1. Factual Engine
The core reasoning and fact-processing engine. Takes raw claims, evidence, and data and produces verified, structured factual outputs. This is the computational backbone that powers everything else.

### 0. NNRT — Narrative-to-Neutral Report Transformer
Transforms biased, narrative-driven content into neutral, factual reports. Strips spin, identifies framing, normalizes language, preserves substance. Numbered 0 because it's a foundational capability that the Factual Engine depends on.

### 3. Factual Platform / Online
The public-facing platform that delivers factual products to users. The online presence where accountability becomes visible, searchable, and persistent.

## How ocf-tag Drives Development

The Accountability Generator doesn't wait passively for its dependencies to be built. It actively:

1. **Sets requirements** — defines what the Factual Engine needs to do, what NNRT must handle, what the Platform must deliver
2. **Sets standards** — high standards, non-negotiable, for code quality, factual accuracy, and system reliability
3. **Holds agents accountable** — tracks whether the Architect's designs meet requirements, whether the Engineer's code meets standards, whether QA actually catches regressions
4. **Ensures no regression** — every change must be an improvement. Deviations from the plan are only acceptable if they make things better.
5. **Drives its own design** — works with the Architect agent to design itself, its layers, and the layers of its dependencies
6. **Drives other agents' design** — helps the Architect design the other agents, ensuring they're capable of meeting ocf-tag's requirements

## The Development Flow

This is a long journey. Multiple milestones. Each milestone tests and evolves every piece:

```
ocf-tag (driver)
  │
  ├── Sets requirements for ──→ Factual Engine
  │                              │
  │                              ├── Depends on ──→ NNRT (Narrative-to-Neutral)
  │                              │
  │                              └── Powers ──→ Factual Platform
  │
  ├── Holds accountable ──→ Architect (designs meet requirements?)
  │                     ──→ Software Engineer (code meets standards?)
  │                     ──→ QA Engineer (regressions caught?)
  │                     ──→ DevOps (infrastructure reliable?)
  │                     ──→ Technical Writer (docs accurate?)
  │                     ──→ UX Designer (platform usable?)
  │
  └── Evolves itself ──→ Its own 5 layers mature as dependencies mature
```

## The 5 Layers (Revisited with Dependencies)

### Layer 1: Intake (BUILT — 584 lines)
Collects claims, evidence, actors, actions, timelines.
**Needs**: NNRT to neutralize incoming narratives before structuring.

### Layer 2: Structuring
Normalizes into actors, institutions, decisions, dependencies, impacts, contradictions, timelines, confidence levels.
**Needs**: Factual Engine for confidence scoring and contradiction detection.

### Layer 3: Mapping
Builds responsibility chains, decision trees, knowledge graphs, consequence maps.
**Needs**: Factual Engine for relationship validation. Factual Platform for visualization.

### Layer 4: Pressure Generation
Produces reports, dashboards, contradiction flags, accountability scores.
**Needs**: NNRT for neutral report generation. Factual Platform for delivery.

### Layer 5: Persistence
Ensures nothing disappears, edits visible, claims linked to outcomes.
**Needs**: Factual Platform for public persistence. Factual Engine for link integrity.

## Principles

- High requirements, high standards, no compromise
- Every deviation must be an improvement
- No regression — ever
- ocf-tag is the conscience of the fleet
- This is infrastructure, not activism
- Long journey, no shortcuts