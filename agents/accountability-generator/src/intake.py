"""Accountability Generator — Intake Service.

Provides the public API for creating and assembling claims.
The IntakeService orchestrates domain objects and delegates
persistence to a ClaimStore.
"""

from __future__ import annotations

from datetime import date

from .models import (
    Action,
    Actor,
    Claim,
    ClaimStatus,
    Evidence,
    EvidenceType,
    Timeline,
)
from .storage import ClaimStore


class IntakeError(Exception):
    """Raised when an intake operation fails validation."""


class IntakeService:
    """Assembles accountability claims from raw inputs.

    This is the entry point for the Intake layer. External callers
    create a claim, attach actors / evidence / actions, and persist
    through the injected store.
    """

    def __init__(self, store: ClaimStore) -> None:
        self._store = store

    # ── Claim lifecycle ────────────────────────────────────────

    def create_claim(
        self,
        title: str,
        summary: str = "",
        *,
        start: date | None = None,
        end: date | None = None,
        timeline_description: str = "",
        tags: list[str] | None = None,
    ) -> Claim:
        """Create a new draft claim and persist it."""
        if not title.strip():
            raise IntakeError("Claim title must not be empty")

        timeline = (
            Timeline(start=start, end=end, description=timeline_description)
            if start is not None
            else None
        )

        claim = Claim(
            title=title.strip(),
            summary=summary.strip(),
            timeline=timeline,
            tags=tags or [],
        )
        self._store.save(claim)
        return claim

    def get_claim(self, claim_id: str) -> Claim:
        """Retrieve a claim or raise."""
        claim = self._store.get(claim_id)
        if claim is None:
            raise IntakeError(f"Claim not found: {claim_id}")
        return claim

    def update_status(self, claim_id: str, status: ClaimStatus) -> Claim:
        """Transition a claim to a new status."""
        claim = self.get_claim(claim_id)
        claim.status = status
        self._store.save(claim)
        return claim

    # ── Actors ─────────────────────────────────────────────────

    def add_actor(
        self,
        claim_id: str,
        name: str,
        *,
        role: str = "",
        organization: str = "",
        aliases: list[str] | None = None,
    ) -> Actor:
        """Add an actor to a claim."""
        if not name.strip():
            raise IntakeError("Actor name must not be empty")

        claim = self.get_claim(claim_id)
        actor = Actor(
            name=name.strip(),
            role=role.strip(),
            organization=organization.strip(),
            aliases=aliases or [],
        )
        claim.actors.append(actor)
        self._store.save(claim)
        return actor

    # ── Evidence ───────────────────────────────────────────────

    def add_evidence(
        self,
        claim_id: str,
        description: str,
        *,
        evidence_type: EvidenceType = EvidenceType.DOCUMENT,
        source: str = "",
        obtained_at: date | None = None,
        reliability_note: str = "",
    ) -> Evidence:
        """Attach a piece of evidence to a claim."""
        if not description.strip():
            raise IntakeError("Evidence description must not be empty")

        claim = self.get_claim(claim_id)
        evidence = Evidence(
            type=evidence_type,
            source=source.strip(),
            description=description.strip(),
            obtained_at=obtained_at,
            reliability_note=reliability_note.strip(),
        )
        claim.evidence.append(evidence)
        self._store.save(claim)
        return evidence

    # ── Actions ────────────────────────────────────────────────

    def add_action(
        self,
        claim_id: str,
        description: str,
        *,
        actor_ids: list[str] | None = None,
        evidence_ids: list[str] | None = None,
        start: date | None = None,
        end: date | None = None,
        timeline_description: str = "",
    ) -> Action:
        """Record a discrete action within a claim.

        actor_ids and evidence_ids must reference entities already
        attached to the claim.
        """
        if not description.strip():
            raise IntakeError("Action description must not be empty")

        claim = self.get_claim(claim_id)

        resolved_actor_ids = actor_ids or []
        resolved_evidence_ids = evidence_ids or []

        # Validate references
        known_actor_ids = {a.id for a in claim.actors}
        for aid in resolved_actor_ids:
            if aid not in known_actor_ids:
                raise IntakeError(f"Unknown actor id: {aid}")

        known_evidence_ids = {e.id for e in claim.evidence}
        for eid in resolved_evidence_ids:
            if eid not in known_evidence_ids:
                raise IntakeError(f"Unknown evidence id: {eid}")

        timeline = (
            Timeline(start=start, end=end, description=timeline_description)
            if start is not None
            else None
        )

        action = Action(
            description=description.strip(),
            actor_ids=resolved_actor_ids,
            evidence_ids=resolved_evidence_ids,
            timeline=timeline,
        )
        claim.actions.append(action)
        self._store.save(claim)
        return action
