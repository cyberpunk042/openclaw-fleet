# Accountability Generator

A structured pipeline for capturing, assembling, and normalizing accountability claims.

## Overview

The Accountability Generator is a multi-layer pipeline that transforms raw information about public actors, institutions, and events into structured, evidence-backed accountability records.

```
[Intake Layer]         [Structuring Layer]        [Future: Tagging / Output]
  ClaimStore      →    StructuredClaimStore   →    ocf-tag consumer
  (source data)        (normalized entities)
```

## Architecture

### Layer 1: Intake

The Intake layer is the entry point. It validates, assembles, and persists raw claim data.

**Entry point:** `IntakeService` in `src/intake.py`

```python
from src.storage import InMemoryClaimStore
from src.intake import IntakeService

store = InMemoryClaimStore()
service = IntakeService(store)

claim = service.create_claim(
    title="Minister approved contract without tendering",
    summary="Contract awarded directly to connected firm.",
    start=date(2024, 3, 1),
    tags=["procurement", "conflict-of-interest"],
)
```

#### Domain Model

```
Claim (root aggregate)
├── id: str                    # 12-char hex (UUID-derived)
├── title: str
├── summary: str
├── status: ClaimStatus        # DRAFT → UNDER_REVIEW → SUBSTANTIATED | UNSUBSTANTIATED | DISPUTED
├── actors: list[Actor]
├── actions: list[Action]
├── evidence: list[Evidence]
├── timeline: Timeline | None
└── tags: list[str]

Actor
├── id, name, role, organization
└── aliases: list[str]

Evidence
├── id, type (EvidenceType), source, description
├── obtained_at: date | None
└── reliability_note: str

Action
├── id, description
├── actor_ids: list[str]       # must reference actors on the same Claim
├── evidence_ids: list[str]    # must reference evidence on the same Claim
└── timeline: Timeline | None

Timeline (value object, frozen)
├── start: date
├── end: date | None
└── description: str
```

#### Claim Lifecycle

```
DRAFT → UNDER_REVIEW → SUBSTANTIATED
                     → UNSUBSTANTIATED
                     → DISPUTED
```

Use `IntakeService.update_status(claim_id, ClaimStatus.UNDER_REVIEW)` to advance state.

#### Storage

`ClaimStore` is a Protocol (interface). Swap implementations without changing service code:

| Implementation      | Use case                        |
|---------------------|---------------------------------|
| `InMemoryClaimStore` | Tests, local development        |
| _(future)_ SQL / file store | Production persistence   |

---

### Layer 2: Structuring _(designed, not yet implemented)_

The Structuring layer consumes `Claim` aggregates from Intake and normalizes them into typed entities for downstream analysis.

**Trigger:** When a Claim reaches `UNDER_REVIEW` status (sync call or event-driven).

**Design principle:** Read-only access to Intake; writes only to its own `StructuredClaimStore`. Re-runnable without side effects.

#### Key Entities

| Entity | Purpose |
|---|---|
| `NormalizedActor` | Canonical name, institutional affiliations, roles |
| `Institution` | Government, corporate, NGO, media |
| `Decision` | Policy, judicial, executive, legislative, financial decisions |
| `Dependency` | Causal, temporal, evidential, or thematic links between claims |
| `Impact` | Financial, reputational, legal, social, physical consequences |
| `Contradiction` | Factual, temporal, testimonial, or documentary conflicts |
| `ConfidenceScore` | 0.0–1.0 score with method and rationale on every entity |
| `NormalizedTimeline` | Typed date range with precision level |

#### Pipeline Pattern

```
StructuringPipeline
├── ActorNormalizationStep
├── InstitutionExtractionStep
├── DecisionClassificationStep
├── DependencyResolutionStep
├── ImpactAssessmentStep
├── ContradictionDetectionStep
└── ConfidenceScoringStep
```

Each step: `(claim: Claim, partial: StructuredClaim) -> StructuredClaim`. Composable and independently testable.

---

## Running Tests

```bash
cd agents/accountability-generator
python3 -m pytest tests/ -v
```

Expected: **32 tests pass** across `test_intake.py`, `test_models.py`, `test_storage.py`.

---

## Known Limitations (tracked for fix)

| Issue | Location | Risk |
|---|---|---|
| Short IDs (12-char hex, 48-bit) | `models.py` — all entities | Birthday collision ~1% at 1M records |
| Silent field drop | `intake.py:create_claim` — `end`/`timeline_description` ignored if `start=None` | Data loss |
| No `created_at`/`updated_at` on `Claim` | `models.py` | Incomplete audit trail |
| No `list_claims()` on `IntakeService` | `intake.py` | Callers must access store directly |

---

## Project Structure

```
agents/accountability-generator/
├── src/
│   ├── models.py       # Domain model: Claim, Actor, Evidence, Action, Timeline
│   ├── intake.py       # IntakeService — public API for Layer 1
│   └── storage.py      # ClaimStore protocol + InMemoryClaimStore
└── tests/
    ├── test_intake.py  # IntakeService tests (16 tests)
    ├── test_models.py  # Domain model tests (10 tests)
    └── test_storage.py # Storage tests (6–7 tests)
```
