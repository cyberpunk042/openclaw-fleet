"""Accountability Generator — Storage Interface.

Defines the abstract storage protocol and a concrete in-memory
implementation for development and testing.
"""

from __future__ import annotations

from typing import Protocol, Sequence

from .models import Claim


class ClaimStore(Protocol):
    """Abstract interface for persisting and retrieving claims."""

    def save(self, claim: Claim) -> None:
        """Persist a claim. Overwrites if the id already exists."""
        ...

    def get(self, claim_id: str) -> Claim | None:
        """Return a claim by id, or None if not found."""
        ...

    def list_all(self) -> Sequence[Claim]:
        """Return all stored claims."""
        ...

    def delete(self, claim_id: str) -> bool:
        """Delete a claim by id. Returns True if it existed."""
        ...


class InMemoryClaimStore:
    """Dictionary-backed claim store for tests and local development."""

    def __init__(self) -> None:
        self._claims: dict[str, Claim] = {}

    def save(self, claim: Claim) -> None:
        self._claims[claim.id] = claim

    def get(self, claim_id: str) -> Claim | None:
        return self._claims.get(claim_id)

    def list_all(self) -> Sequence[Claim]:
        return list(self._claims.values())

    def delete(self, claim_id: str) -> bool:
        return self._claims.pop(claim_id, None) is not None
