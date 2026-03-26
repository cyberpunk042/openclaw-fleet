"""Tests for InMemoryClaimStore."""

from agents.accountability_generator.src.models import Claim
from agents.accountability_generator.src.storage import InMemoryClaimStore


class TestInMemoryClaimStore:
    def _make_store(self) -> InMemoryClaimStore:
        return InMemoryClaimStore()

    def test_save_and_get(self) -> None:
        store = self._make_store()
        claim = Claim(title="Test")
        store.save(claim)
        assert store.get(claim.id) is claim

    def test_get_missing_returns_none(self) -> None:
        store = self._make_store()
        assert store.get("nonexistent") is None

    def test_list_all_empty(self) -> None:
        store = self._make_store()
        assert store.list_all() == []

    def test_list_all(self) -> None:
        store = self._make_store()
        c1 = Claim(title="A")
        c2 = Claim(title="B")
        store.save(c1)
        store.save(c2)
        assert len(store.list_all()) == 2

    def test_overwrite(self) -> None:
        store = self._make_store()
        claim = Claim(id="fixed", title="v1")
        store.save(claim)
        claim.title = "v2"
        store.save(claim)
        assert store.get("fixed").title == "v2"  # type: ignore[union-attr]
        assert len(store.list_all()) == 1

    def test_delete_existing(self) -> None:
        store = self._make_store()
        claim = Claim(title="Gone")
        store.save(claim)
        assert store.delete(claim.id) is True
        assert store.get(claim.id) is None

    def test_delete_missing(self) -> None:
        store = self._make_store()
        assert store.delete("nope") is False
