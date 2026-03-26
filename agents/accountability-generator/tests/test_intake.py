"""Tests for the IntakeService."""

from datetime import date

import pytest

from agents.accountability_generator.src.intake import IntakeError, IntakeService
from agents.accountability_generator.src.models import ClaimStatus, EvidenceType
from agents.accountability_generator.src.storage import InMemoryClaimStore


@pytest.fixture
def svc() -> IntakeService:
    return IntakeService(InMemoryClaimStore())


class TestCreateClaim:
    def test_minimal(self, svc: IntakeService) -> None:
        claim = svc.create_claim("Budget irregularities")
        assert claim.title == "Budget irregularities"
        assert claim.status is ClaimStatus.DRAFT

    def test_with_timeline(self, svc: IntakeService) -> None:
        claim = svc.create_claim(
            "Late payments",
            start=date(2024, 1, 1),
            end=date(2024, 6, 30),
        )
        assert claim.timeline is not None
        assert claim.timeline.start == date(2024, 1, 1)

    def test_with_tags(self, svc: IntakeService) -> None:
        claim = svc.create_claim("Tagged", tags=["finance", "public"])
        assert claim.tags == ["finance", "public"]

    def test_empty_title_raises(self, svc: IntakeService) -> None:
        with pytest.raises(IntakeError, match="title"):
            svc.create_claim("   ")

    def test_strips_whitespace(self, svc: IntakeService) -> None:
        claim = svc.create_claim("  padded  ", summary="  s  ")
        assert claim.title == "padded"
        assert claim.summary == "s"

    def test_persisted(self, svc: IntakeService) -> None:
        claim = svc.create_claim("Persisted")
        fetched = svc.get_claim(claim.id)
        assert fetched.id == claim.id


class TestGetClaim:
    def test_missing_raises(self, svc: IntakeService) -> None:
        with pytest.raises(IntakeError, match="not found"):
            svc.get_claim("bad-id")


class TestUpdateStatus:
    def test_transition(self, svc: IntakeService) -> None:
        claim = svc.create_claim("Status test")
        updated = svc.update_status(claim.id, ClaimStatus.UNDER_REVIEW)
        assert updated.status is ClaimStatus.UNDER_REVIEW


class TestAddActor:
    def test_basic(self, svc: IntakeService) -> None:
        claim = svc.create_claim("Actor test")
        actor = svc.add_actor(claim.id, "Jane Doe", role="Mayor")
        assert actor.name == "Jane Doe"
        assert actor.role == "Mayor"
        assert len(svc.get_claim(claim.id).actors) == 1

    def test_empty_name_raises(self, svc: IntakeService) -> None:
        claim = svc.create_claim("Actor test")
        with pytest.raises(IntakeError, match="name"):
            svc.add_actor(claim.id, "  ")


class TestAddEvidence:
    def test_basic(self, svc: IntakeService) -> None:
        claim = svc.create_claim("Evidence test")
        ev = svc.add_evidence(
            claim.id,
            "Bank statement showing transfer",
            evidence_type=EvidenceType.RECORD,
            source="bank_stmt_2024.pdf",
        )
        assert ev.type is EvidenceType.RECORD
        assert ev.source == "bank_stmt_2024.pdf"
        assert len(svc.get_claim(claim.id).evidence) == 1

    def test_empty_description_raises(self, svc: IntakeService) -> None:
        claim = svc.create_claim("Evidence test")
        with pytest.raises(IntakeError, match="description"):
            svc.add_evidence(claim.id, "")


class TestAddAction:
    def test_with_refs(self, svc: IntakeService) -> None:
        claim = svc.create_claim("Action test")
        actor = svc.add_actor(claim.id, "John")
        ev = svc.add_evidence(claim.id, "Receipt")
        action = svc.add_action(
            claim.id,
            "Approved fraudulent expense",
            actor_ids=[actor.id],
            evidence_ids=[ev.id],
            start=date(2024, 3, 15),
        )
        assert action.actor_ids == [actor.id]
        assert action.evidence_ids == [ev.id]
        assert action.timeline is not None

    def test_unknown_actor_raises(self, svc: IntakeService) -> None:
        claim = svc.create_claim("Action test")
        with pytest.raises(IntakeError, match="Unknown actor"):
            svc.add_action(claim.id, "Bad ref", actor_ids=["fake"])

    def test_unknown_evidence_raises(self, svc: IntakeService) -> None:
        claim = svc.create_claim("Action test")
        with pytest.raises(IntakeError, match="Unknown evidence"):
            svc.add_action(claim.id, "Bad ref", evidence_ids=["fake"])

    def test_empty_description_raises(self, svc: IntakeService) -> None:
        claim = svc.create_claim("Action test")
        with pytest.raises(IntakeError, match="description"):
            svc.add_action(claim.id, "   ")
