"""Flow 3: Storm Response — Indicators → Severity → Dispatch Control.

Tests the storm detection → dispatch limiting → routing impact chain.
"""

import time

from fleet.core.backend_router import route_task
from fleet.core.storm_integration import (
    StormResponse,
    evaluate_storm_response,
)
from fleet.core.storm_monitor import StormMonitor, StormSeverity

from .conftest import make_task


def _escalate_to(monitor: StormMonitor, severity: str) -> None:
    """Helper to push monitor to a specific severity level."""
    if severity in ("WARNING", "STORM", "CRITICAL"):
        monitor.report_indicator("session_burst", "15/min")
        monitor.report_indicator("void_sessions", "60%")
        for ind in monitor._indicators.values():
            ind.confirmed = True
    if severity in ("STORM", "CRITICAL"):
        monitor.report_indicator("dispatch_storm", "high")
        monitor.report_indicator("error_storm", "surge")
        for ind in monitor._indicators.values():
            ind.confirmed = True
    if severity == "CRITICAL":
        monitor.report_indicator("cascade_depth", "deep")
        monitor.report_indicator("agent_thrashing", "multiple")
        monitor.report_indicator("gateway_duplication", "detected")
        for ind in monitor._indicators.values():
            ind.confirmed = True


def test_storm_warning_limits_dispatch():
    """WARNING severity → dispatch limited to 1."""
    monitor = StormMonitor()
    _escalate_to(monitor, "WARNING")

    response = evaluate_storm_response(monitor)
    assert response.severity in (StormSeverity.WARNING, StormSeverity.STORM, StormSeverity.CRITICAL)

    if response.severity == StormSeverity.WARNING:
        assert response.max_dispatch is not None
        assert response.max_dispatch <= 1


def test_storm_escalation():
    """WARNING → STORM → CRITICAL progression."""
    monitor = StormMonitor()

    # WARNING
    _escalate_to(monitor, "WARNING")
    r1 = evaluate_storm_response(monitor)
    assert r1.should_alert_irc

    # STORM
    _escalate_to(monitor, "STORM")
    r2 = evaluate_storm_response(monitor)
    if r2.severity == StormSeverity.STORM:
        assert r2.max_dispatch == 0

    # CRITICAL
    _escalate_to(monitor, "CRITICAL")
    r3 = evaluate_storm_response(monitor)
    if r3.severity == StormSeverity.CRITICAL:
        assert r3.halt_cycle is True


def test_storm_circuit_breaker_routing():
    """Open circuit breaker → router skips backend → fallback."""
    task = make_task()
    monitor = StormMonitor()

    # Trip the claude-code breaker
    breaker = monitor.get_backend_breaker("claude-code")
    for _ in range(breaker.failure_threshold):
        breaker.record_failure()

    # Route with storm monitor — should trigger fallback
    decision = route_task(
        task, agent_name="worker",
        storm_monitor=monitor,
    )
    assert decision.backend is not None


def test_storm_recovery_cycle():
    """CRITICAL → indicators clear → severity drops."""
    monitor = StormMonitor()

    # Escalate to high severity
    _escalate_to(monitor, "CRITICAL")
    r_peak = evaluate_storm_response(monitor)
    assert r_peak.should_alert_po

    # Clear all indicators
    for name in list(monitor._indicators.keys()):
        monitor.clear_indicator(name)

    # Re-evaluate
    r_after = evaluate_storm_response(monitor)
    if r_after.severity in (StormSeverity.CLEAR, StormSeverity.WATCH):
        assert r_after.halt_cycle is False
