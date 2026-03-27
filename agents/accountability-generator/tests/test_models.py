"""Tests for the domain model dataclasses."""

from datetime import date

from src.models import (
    Action,
    Actor,
    Claim,
    ClaimStatus,
    Evidence,
    EvidenceType,
    Timeline,
)


class TestTimeline:
    def test_frozen(self) -> None:
        t = Timeline(start=date(2024, 1, 1))
        try:
            t.start = date(2025, 1, 1)  # type: ignore[misc]
            assert False, "Should have raised"
        except AttributeError:
            pass

    def test_defaults(self) -> None:
        t = Timeline(start=date(2024, 6, 1))
        assert t.end is None
        assert t.description == ""


class TestActor:
    def test_auto_id(self) -> None:
        a = Actor(name="Jane")
        assert len(a.id) == 32  # full uuid4 hex (128-bit)

    def test_aliases_default(self) -> None:
        a = Actor()
        assert a.aliases == []


class TestEvidence:
    def test_default_type(self) -> None:
        e = Evidence()
        assert e.type is EvidenceType.DOCUMENT

    def test_custom_type(self) -> None:
        e = Evidence(type=EvidenceType.MEDIA)
        assert e.type is EvidenceType.MEDIA


class TestAction:
    def test_default_lists(self) -> None:
        a = Action(description="did a thing")
        assert a.actor_ids == []
        assert a.evidence_ids == []
        assert a.timeline is None


class TestClaim:
    def test_defaults(self) -> None:
        c = Claim(title="Test claim")
        assert c.status is ClaimStatus.DRAFT
        assert c.actors == []
        assert c.actions == []
        assert c.evidence == []
        assert c.tags == []

    def test_unique_ids(self) -> None:
        c1 = Claim()
        c2 = Claim()
        assert c1.id != c2.id
