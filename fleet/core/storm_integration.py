"""Orchestrator storm integration (M-SP08).

Provides the logic layer between the storm monitor and the orchestrator.
The orchestrator calls these functions at the start of every cycle to:

  1. Evaluate storm severity
  2. Apply graduated response (dispatch limiting)
  3. Track storm events for incident reporting
  4. Generate incident reports when storms end

This module does NOT import the orchestrator — it provides pure functions
that the orchestrator consumes. No side effects beyond the objects passed in.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from fleet.core.incident_report import IncidentReport, StormEvent
from fleet.core.storm_monitor import StormMonitor, StormSeverity, severity_index


# ─── Storm Response ───────────────────────────────────────────────


@dataclass
class StormResponse:
    """What the orchestrator should do based on storm evaluation."""

    severity: str = StormSeverity.CLEAR
    max_dispatch: Optional[int] = None       # None = don't override
    should_capture_diagnostic: bool = False
    should_alert_irc: bool = False
    should_alert_po: bool = False
    alert_message: str = ""
    halt_cycle: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "severity": self.severity,
            "max_dispatch": self.max_dispatch,
            "should_capture_diagnostic": self.should_capture_diagnostic,
            "should_alert_irc": self.should_alert_irc,
            "should_alert_po": self.should_alert_po,
            "halt_cycle": self.halt_cycle,
            "notes": self.notes,
        }


def evaluate_storm_response(
    monitor: StormMonitor,
    current_max_dispatch: int = 2,
) -> StormResponse:
    """Evaluate the storm monitor and determine what the orchestrator should do."""
    severity = monitor.evaluate()
    response = StormResponse(severity=severity)

    if severity == StormSeverity.CRITICAL:
        response.halt_cycle = True
        response.max_dispatch = 0
        response.should_capture_diagnostic = True
        response.should_alert_irc = True
        response.should_alert_po = True
        response.alert_message = (
            f"CRITICAL: {monitor.format_status()} — fleet frozen"
        )
        response.notes.append("STORM CRITICAL: fleet frozen — no dispatch")

    elif severity == StormSeverity.STORM:
        response.max_dispatch = 0
        response.should_capture_diagnostic = True
        response.should_alert_irc = True
        response.should_alert_po = True
        response.alert_message = (
            f"STORM: {monitor.format_status()} — dispatch paused"
        )
        response.notes.append("STORM: dispatch paused, monitoring only")

    elif severity == StormSeverity.WARNING:
        response.max_dispatch = min(current_max_dispatch, 1)
        response.should_capture_diagnostic = True
        response.should_alert_irc = True
        response.alert_message = (
            f"WARNING: {monitor.format_status()}"
        )
        response.notes.append("STORM WARNING: dispatch limited to 1")

    elif severity == StormSeverity.WATCH:
        response.notes.append(f"STORM WATCH: {monitor.format_status()}")

    return response


# ─── Storm Event Management ───────────────────────────────────────


class StormEventTracker:
    """Tracks storm events across orchestrator cycles."""

    def __init__(self) -> None:
        self._active_event: Optional[StormEvent] = None
        self._completed_reports: list[IncidentReport] = []
        self._max_reports = 20

    @property
    def has_active_event(self) -> bool:
        return self._active_event is not None

    @property
    def active_event(self) -> Optional[StormEvent]:
        return self._active_event

    @property
    def completed_reports(self) -> list[IncidentReport]:
        return list(self._completed_reports)

    @property
    def total_incidents(self) -> int:
        return len(self._completed_reports)

    def process_cycle(
        self,
        severity: str,
        indicators: list[str],
        response: StormResponse,
        void_sessions: int = 0,
        total_sessions: int = 0,
    ) -> Optional[IncidentReport]:
        """Process one orchestrator cycle's storm state."""
        is_storm_active = severity_index(severity) >= severity_index(
            StormSeverity.WARNING
        )

        if is_storm_active:
            if self._active_event is None:
                self._active_event = StormEvent()

            self._active_event.record_severity(severity)
            for ind in indicators:
                self._active_event.record_indicator(ind)

            if response.halt_cycle:
                self._active_event.record_response("halt cycle")
            if response.should_alert_po:
                self._active_event.record_response("alert PO")
            if response.max_dispatch is not None and response.max_dispatch == 0:
                self._active_event.record_response(
                    "disable dispatch", "max_dispatch=0",
                )

            return None

        else:
            if self._active_event is not None:
                self._active_event.close()
                report = self._active_event.to_report(
                    void_sessions=void_sessions,
                    total_sessions=total_sessions,
                )
                self._completed_reports.append(report)
                if len(self._completed_reports) > self._max_reports:
                    self._completed_reports = self._completed_reports[
                        -self._max_reports :
                    ]
                self._active_event = None
                return report

            return None

    def force_close(
        self,
        void_sessions: int = 0,
        total_sessions: int = 0,
        root_cause: str = "",
    ) -> Optional[IncidentReport]:
        """Force-close the active storm event."""
        if self._active_event is None:
            return None

        self._active_event.close()
        report = self._active_event.to_report(
            void_sessions=void_sessions,
            total_sessions=total_sessions,
            root_cause=root_cause,
        )
        self._completed_reports.append(report)
        if len(self._completed_reports) > self._max_reports:
            self._completed_reports = self._completed_reports[-self._max_reports:]
        self._active_event = None
        return report

    def status(self) -> dict:
        return {
            "active_event": self._active_event is not None,
            "peak_severity": (
                self._active_event.peak_severity if self._active_event else None
            ),
            "total_incidents": len(self._completed_reports),
        }


# ─── Dispatch Gate ────────────────────────────────────────────────


def should_dispatch(
    storm_response: StormResponse,
    agent_name: str,
    monitor: StormMonitor,
) -> tuple[bool, str]:
    """Check if a specific task dispatch should proceed."""
    if storm_response.halt_cycle:
        return False, f"storm {storm_response.severity}: fleet frozen"

    if storm_response.max_dispatch is not None and storm_response.max_dispatch <= 0:
        return False, f"storm {storm_response.severity}: dispatch disabled"

    breaker = monitor.get_agent_breaker(agent_name)
    if not breaker.check():
        return False, f"circuit breaker OPEN for {agent_name}"

    return True, "ok"


def record_dispatch_outcome(
    monitor: StormMonitor,
    agent_name: str,
    success: bool,
    void: bool = False,
) -> None:
    """Record the outcome of a dispatch for storm monitoring."""
    monitor.report_session(void=void)
    monitor.report_dispatch()

    breaker = monitor.get_agent_breaker(agent_name)
    if success and not void:
        breaker.record_success()
    elif not success or void:
        breaker.record_failure()
