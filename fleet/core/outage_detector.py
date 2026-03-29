"""Outage and rate-limit detection — back off when APIs are failing.

Detects:
- MC API unreachable → pause operations
- Rate limits hit (429) → exponential backoff
- Gateway unreachable → pause dispatch
- Repeated failures → alert human via ntfy

The orchestrator checks outage state before each cycle.
If an outage is detected, the orchestrator reduces activity
or pauses entirely until the service recovers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class ServiceState:
    """Health state of a single service."""

    name: str
    healthy: bool = True
    consecutive_failures: int = 0
    last_failure_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    backoff_until: Optional[datetime] = None
    last_error: str = ""


class OutageDetector:
    """Tracks service health and implements backoff on failures."""

    def __init__(self) -> None:
        self._services: dict[str, ServiceState] = {
            "mc_api": ServiceState(name="Mission Control API"),
            "gateway": ServiceState(name="OpenClaw Gateway"),
            "github": ServiceState(name="GitHub API"),
        }

    def record_success(self, service: str) -> None:
        """Record a successful API call."""
        s = self._services.get(service)
        if s:
            s.healthy = True
            s.consecutive_failures = 0
            s.last_success_at = datetime.now()
            s.backoff_until = None

    def record_failure(self, service: str, error: str = "") -> None:
        """Record a failed API call."""
        now = datetime.now()
        s = self._services.get(service)
        if not s:
            return

        s.consecutive_failures += 1
        s.last_failure_at = now
        s.last_error = error

        # Exponential backoff: 30s, 60s, 120s, 240s, 480s (max 8 min)
        backoff_seconds = min(30 * (2 ** (s.consecutive_failures - 1)), 480)
        s.backoff_until = now + timedelta(seconds=backoff_seconds)

        if s.consecutive_failures >= 3:
            s.healthy = False

    def is_service_available(self, service: str, now: Optional[datetime] = None) -> bool:
        """Check if a service is available (not in backoff)."""
        now = now or datetime.now()
        s = self._services.get(service)
        if not s:
            return True

        if s.backoff_until and now < s.backoff_until:
            return False

        return True

    def should_run_cycle(self, now: Optional[datetime] = None) -> tuple[bool, str]:
        """Check if the orchestrator should run this cycle.

        Returns (should_run, reason).
        """
        now = now or datetime.now()
        mc = self._services.get("mc_api")

        if mc and not mc.healthy and mc.consecutive_failures >= 5:
            return False, f"MC API down: {mc.consecutive_failures} consecutive failures. Last: {mc.last_error}"

        if mc and mc.backoff_until and now < mc.backoff_until:
            remaining = (mc.backoff_until - now).total_seconds()
            return False, f"MC API backoff: {remaining:.0f}s remaining"

        return True, ""

    def get_alerts(self) -> list[str]:
        """Get alert messages for unhealthy services."""
        alerts = []
        for s in self._services.values():
            if not s.healthy:
                alerts.append(
                    f"{s.name}: DOWN ({s.consecutive_failures} failures, "
                    f"last: {s.last_error[:50]})"
                )
        return alerts

    def format_status(self) -> str:
        """Format service health for display."""
        lines = []
        for s in self._services.values():
            icon = "✅" if s.healthy else "❌"
            lines.append(f"{icon} {s.name}: {'healthy' if s.healthy else f'DOWN ({s.consecutive_failures} failures)'}")
        return " | ".join(lines)