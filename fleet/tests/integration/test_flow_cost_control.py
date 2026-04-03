"""Flow 4: Cost Control — Budget override management.

Tests per-order budget mode overrides.
"""

from fleet.core.budget_ui import BudgetOverrideManager


def test_override_effective_mode():
    """PO override for specific orders."""
    mgr = BudgetOverrideManager()
    base_mode = "standard"

    mgr.set_override("ORDER-42", "turbo", reason="PO: critical delivery")
    effective = mgr.effective_mode("ORDER-42", base_mode)
    assert effective == "turbo"

    effective_other = mgr.effective_mode("ORDER-99", base_mode)
    assert effective_other == "standard"
