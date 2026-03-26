"""Tests for gateway.models."""

from datetime import datetime, timezone

from gateway.models import Claim


def test_claim_defaults():
    claim = Claim(
        source="public-records",
        content="Entity X received funding",
        timestamp=datetime(2026, 1, 15, tzinfo=timezone.utc),
        confidence_level=0.85,
    )
    assert claim.source == "public-records"
    assert claim.content == "Entity X received funding"
    assert claim.confidence_level == 0.85
    assert claim.linked_actors == []
    assert isinstance(claim.id, str)
    assert len(claim.id) == 32  # uuid4 hex


def test_claim_with_actors():
    claim = Claim(
        source="interviews",
        content="Actor A met Actor B",
        timestamp=datetime(2026, 3, 1, tzinfo=timezone.utc),
        confidence_level=0.6,
        linked_actors=["actor-a", "actor-b"],
    )
    assert claim.linked_actors == ["actor-a", "actor-b"]


def test_claim_unique_ids():
    kwargs = dict(
        source="s",
        content="c",
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        confidence_level=0.5,
    )
    a = Claim(**kwargs)
    b = Claim(**kwargs)
    assert a.id != b.id


def test_claim_explicit_id():
    claim = Claim(
        id="custom-id",
        source="tip",
        content="Something happened",
        timestamp=datetime(2026, 2, 1, tzinfo=timezone.utc),
        confidence_level=0.3,
    )
    assert claim.id == "custom-id"
