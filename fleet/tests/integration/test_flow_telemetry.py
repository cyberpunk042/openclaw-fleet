"""Flow 5: Session Telemetry — Session JSON → All Systems.

Tests that Claude Code session data feeds real values into
LaborStamp, ClaudeHealth, and StormMonitor.
"""

from fleet.core.backend_health import ClaudeHealth
from fleet.core.labor_stamp import LaborStamp
from fleet.core.session_telemetry import (
    ingest,
    to_claude_health,
    to_cost_delta,
    to_labor_fields,
    to_storm_indicators,
)
from fleet.core.storm_monitor import StormMonitor

from .conftest import SAMPLE_SESSION_JSON


def test_telemetry_ingest():
    """Parse real session JSON, verify all fields extracted."""
    snap = ingest(SAMPLE_SESSION_JSON)
    assert snap.model_id == "claude-opus-4-6"
    assert snap.context_window_size == 1_000_000
    assert snap.context_label == "1M"
    assert snap.context_used_pct == 42.0
    assert snap.total_cost_usd == 0.15
    assert snap.five_hour_used_pct == 23.5
    assert snap.seven_day_used_pct == 41.2
    assert snap.total_lines_added == 256
    assert snap.cache_read_tokens == 2000


def test_telemetry_to_labor():
    """Session data populates LaborStamp with real values."""
    snap = ingest(SAMPLE_SESSION_JSON)
    fields = to_labor_fields(snap)

    # Create stamp with session-derived fields
    stamp = LaborStamp(
        agent_name="worker",
        backend="claude-code",
        **{k: v for k, v in fields.items() if k in (
            "model", "model_version", "duration_seconds",
            "estimated_tokens", "estimated_cost_usd",
            "session_type", "lines_added", "lines_removed",
            "cache_read_tokens",
        )},
    )

    assert stamp.model == "claude-opus-4-6"
    assert stamp.duration_seconds == 180
    assert stamp.estimated_tokens == 195_000
    assert stamp.estimated_cost_usd == 0.15
    assert stamp.lines_added == 256
    assert stamp.lines_removed == 31
    assert stamp.cache_read_tokens == 2000


def test_telemetry_to_health():
    """Session quota feeds ClaudeHealth, triggers quota_warning at 80%."""
    snap = ingest(SAMPLE_SESSION_JSON)
    fields = to_claude_health(snap)

    health = ClaudeHealth(
        status="up",
        last_check=0.0,
        **{k: v for k, v in fields.items() if k in (
            "quota_used_pct", "latency_ms", "model_available",
            "weekly_quota_used_pct", "context_window_size",
        )},
    )

    assert health.quota_used_pct == 23.5
    assert health.quota_warning is False  # 23.5 < 80
    assert health.weekly_quota_used_pct == 41.2
    assert health.weekly_quota_warning is False  # 41.2 < 80
    assert health.context_window_size == 1_000_000
    assert health.latency_ms == 2300.0

    # Now test with high quota
    high_snap = ingest({
        **SAMPLE_SESSION_JSON,
        "rate_limits": {
            "five_hour": {"used_percentage": 85.0},
            "seven_day": {"used_percentage": 92.0},
        },
    })
    high_fields = to_claude_health(high_snap)
    high_health = ClaudeHealth(
        status="up",
        last_check=0.0,
        quota_used_pct=high_fields.get("quota_used_pct", 0),
        weekly_quota_used_pct=high_fields.get("weekly_quota_used_pct", 0),
    )
    assert high_health.quota_warning is True   # 85 >= 80
    assert high_health.weekly_quota_warning is True  # 92 >= 80
    assert high_health.weekly_quota_critical is False  # 92 < 95


def test_telemetry_context_storm():
    """Context at 90% triggers storm indicator."""
    high_context = {
        **SAMPLE_SESSION_JSON,
        "context_window": {
            **SAMPLE_SESSION_JSON["context_window"],
            "used_percentage": 92,
        },
        "rate_limits": {
            "five_hour": {"used_percentage": 85.0},
            "seven_day": {"used_percentage": 45.0},
        },
    }
    snap = ingest(high_context)
    indicators = to_storm_indicators(snap)

    names = [name for name, _ in indicators]
    assert "context_pressure" in names
    assert "quota_pressure_5h" in names

    # Feed into storm monitor
    monitor = StormMonitor()
    for name, value in indicators:
        monitor.report_indicator(name, value)

    # Indicators are registered
    assert "context_pressure" in monitor._indicators
    assert "quota_pressure_5h" in monitor._indicators


def test_telemetry_cost_delta():
    """to_cost_delta computes incremental cost from session snapshots."""
    snap = ingest(SAMPLE_SESSION_JSON)

    # First call — full cost
    delta = to_cost_delta(snap, previous_cost=0.0)
    assert delta == 0.15

    # Second call — incremental
    snap2 = ingest({
        **SAMPLE_SESSION_JSON,
        "cost": {**SAMPLE_SESSION_JSON["cost"], "total_cost_usd": 4.50},
    })
    delta2 = to_cost_delta(snap2, previous_cost=0.15)
    assert abs(delta2 - 4.35) < 0.01
