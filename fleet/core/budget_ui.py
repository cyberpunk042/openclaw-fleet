"""Budget mode UI data provider.

Provides data for the OCMC header bar budget controls:
- Current budget mode (tempo setting)
- Per-order budget mode overrides
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional


# ─── Per-Order Budget Override ─────────────────────────────────


@dataclass
class BudgetOverride:
    """A per-order budget mode override."""

    order_id: str
    budget_mode: str
    reason: str = ""
    set_by: str = "PO"
    set_at: float = 0.0

    def __post_init__(self) -> None:
        if not self.set_at:
            self.set_at = time.time()

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "budget_mode": self.budget_mode,
            "reason": self.reason,
            "set_by": self.set_by,
        }


class BudgetOverrideManager:
    """Manages per-order budget mode overrides.

    Fleet-wide budget mode is the default. Individual orders
    can override it.
    """

    def __init__(self) -> None:
        self._overrides: dict[str, BudgetOverride] = {}

    def set_override(
        self, order_id: str, budget_mode: str, reason: str = "",
    ) -> BudgetOverride:
        override = BudgetOverride(
            order_id=order_id, budget_mode=budget_mode, reason=reason,
        )
        self._overrides[order_id] = override
        return override

    def get_override(self, order_id: str) -> Optional[BudgetOverride]:
        return self._overrides.get(order_id)

    def clear_override(self, order_id: str) -> bool:
        if order_id in self._overrides:
            del self._overrides[order_id]
            return True
        return False

    def effective_mode(self, order_id: str, fleet_mode: str) -> str:
        """Get the effective budget mode for an order."""
        override = self._overrides.get(order_id)
        if override:
            return override.budget_mode
        return fleet_mode

    @property
    def active_overrides(self) -> list[BudgetOverride]:
        return list(self._overrides.values())

    def to_dict(self) -> dict:
        return {
            "total_overrides": len(self._overrides),
            "overrides": {
                oid: o.to_dict() for oid, o in self._overrides.items()
            },
        }


# ─── Board Config Payload ──────────────────────────────────────


def budget_ui_payload(
    budget_mode: str,
    override_mgr: Optional[BudgetOverrideManager] = None,
) -> dict:
    """Build the payload to PATCH into board.fleet_config."""
    payload = {
        "budget_mode": budget_mode,
    }
    if override_mgr:
        payload["budget_overrides"] = override_mgr.to_dict()
    return payload
