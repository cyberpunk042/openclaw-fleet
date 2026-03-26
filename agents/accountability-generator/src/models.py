"""Accountability Generator — Domain Model.

Defines the core entities for accountability claims:
Claim (root aggregate), Actor, Action, Evidence, Timeline.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date
from enum import Enum


# ── Value Objects ──────────────────────────────────────────────


class EvidenceType(Enum):
    DOCUMENT = "document"
    TESTIMONY = "testimony"
    RECORD = "record"
    MEDIA = "media"
    COMMUNICATION = "communication"


class ClaimStatus(Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    SUBSTANTIATED = "substantiated"
    UNSUBSTANTIATED = "unsubstantiated"
    DISPUTED = "disputed"


@dataclass(frozen=True)
class Timeline:
    """A bounded time range with optional precision note."""

    start: date
    end: date | None = None
    description: str = ""


# ── Entities ───────────────────────────────────────────────────


@dataclass
class Actor:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    role: str = ""
    organization: str = ""
    aliases: list[str] = field(default_factory=list)


@dataclass
class Evidence:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    type: EvidenceType = EvidenceType.DOCUMENT
    source: str = ""
    description: str = ""
    obtained_at: date | None = None
    reliability_note: str = ""


@dataclass
class Action:
    """A discrete act by one or more actors, backed by evidence."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    description: str = ""
    actor_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    timeline: Timeline | None = None


# ── Root Aggregate ─────────────────────────────────────────────


@dataclass
class Claim:
    """Central unit of accountability. Everything hangs off a Claim."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = ""
    summary: str = ""
    status: ClaimStatus = ClaimStatus.DRAFT
    actors: list[Actor] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    timeline: Timeline | None = None
    tags: list[str] = field(default_factory=list)
