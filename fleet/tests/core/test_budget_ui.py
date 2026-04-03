"""Tests for budget mode UI data provider."""

from fleet.core.budget_ui import (
    BudgetOverride,
    BudgetOverrideManager,
    budget_ui_payload,
)


# ─── BudgetOverride ───────────────────────────────────────────


def test_override_defaults():
    o = BudgetOverride(order_id="ORD-1", budget_mode="turbo")
    assert o.set_by == "PO"
    assert o.set_at > 0


def test_override_to_dict():
    o = BudgetOverride(
        order_id="ORD-1", budget_mode="turbo", reason="urgent fix",
    )
    d = o.to_dict()
    assert d["order_id"] == "ORD-1"
    assert d["budget_mode"] == "turbo"
    assert d["reason"] == "urgent fix"


# ─── BudgetOverrideManager ────────────────────────────────────


def test_manager_set_override():
    m = BudgetOverrideManager()
    o = m.set_override("ORD-1", "turbo", "urgent")
    assert o.budget_mode == "turbo"
    assert len(m.active_overrides) == 1


def test_manager_get_override():
    m = BudgetOverrideManager()
    m.set_override("ORD-1", "turbo")
    assert m.get_override("ORD-1") is not None
    assert m.get_override("ORD-2") is None


def test_manager_clear_override():
    m = BudgetOverrideManager()
    m.set_override("ORD-1", "turbo")
    assert m.clear_override("ORD-1")
    assert not m.clear_override("ORD-1")
    assert len(m.active_overrides) == 0


def test_manager_effective_mode_with_override():
    m = BudgetOverrideManager()
    m.set_override("ORD-1", "turbo")
    assert m.effective_mode("ORD-1", "standard") == "turbo"


def test_manager_effective_mode_no_override():
    m = BudgetOverrideManager()
    assert m.effective_mode("ORD-1", "standard") == "standard"


def test_manager_to_dict():
    m = BudgetOverrideManager()
    m.set_override("ORD-1", "turbo")
    m.set_override("ORD-2", "economic")
    d = m.to_dict()
    assert d["total_overrides"] == 2
    assert "ORD-1" in d["overrides"]
    assert "ORD-2" in d["overrides"]


# ─── budget_ui_payload ─────────────────────────────────────────


def test_payload_basic():
    p = budget_ui_payload("standard")
    assert p["budget_mode"] == "standard"


def test_payload_with_overrides():
    m = BudgetOverrideManager()
    m.set_override("ORD-1", "turbo")
    p = budget_ui_payload("standard", m)
    assert "budget_overrides" in p
    assert p["budget_overrides"]["total_overrides"] == 1
