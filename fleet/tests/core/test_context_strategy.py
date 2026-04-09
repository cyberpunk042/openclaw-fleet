"""Tests for fleet.core.context_strategy — progressive response to context pressure.

Thresholds from PO requirements (CW doc):
  Context: 7% remaining (93% used) = prepare, 5% remaining (95% used) = extract
  Rate limit: 85% = prepare, 90% = manage
"""

import pytest
from fleet.core.context_strategy import (
    ContextStrategy,
    ContextAction,
    RateLimitAction,
)


@pytest.fixture
def strategy():
    return ContextStrategy()


class TestContextEvaluation:
    def test_normal_below_thresholds(self, strategy):
        ev = strategy.evaluate("engineer", context_pct=50.0, rate_limit_pct=40.0)
        assert ev.context_action == ContextAction.NORMAL
        assert ev.rate_limit_action == RateLimitAction.NORMAL
        assert ev.message == ""

    def test_context_normal_at_90(self, strategy):
        """90% context is NORMAL — prepare starts at 93% (7% remaining)."""
        ev = strategy.evaluate("engineer", context_pct=90.0)
        assert ev.context_action == ContextAction.NORMAL

    def test_context_prepare_at_93(self, strategy):
        """93% context = 7% remaining → PREPARE (save state to artifacts)."""
        ev = strategy.evaluate("engineer", context_pct=93.5)
        assert ev.context_action == ContextAction.PREPARE
        assert "PREPARE" in ev.message

    def test_context_extract_at_95(self, strategy):
        """95% context = 5% remaining → EXTRACT (dump everything NOW)."""
        ev = strategy.evaluate("engineer", context_pct=96.0)
        assert ev.context_action == ContextAction.EXTRACT
        assert "EXTRACT" in ev.message

    def test_rate_limit_normal_at_80(self, strategy):
        """80% rate limit is still NORMAL — prepare starts at 85%."""
        ev = strategy.evaluate("engineer", rate_limit_pct=80.0)
        assert ev.rate_limit_action == RateLimitAction.NORMAL

    def test_rate_limit_conserve_at_85(self, strategy):
        """85% rate limit → CONSERVE (start preparing, controlled transition)."""
        ev = strategy.evaluate("engineer", rate_limit_pct=87.0)
        assert ev.rate_limit_action == RateLimitAction.CONSERVE

    def test_rate_limit_critical_at_90(self, strategy):
        """90% rate limit → CRITICAL (actively managing, compact heavy contexts)."""
        ev = strategy.evaluate("engineer", rate_limit_pct=91.0)
        assert ev.rate_limit_action == RateLimitAction.CRITICAL

    def test_both_pressures(self, strategy):
        ev = strategy.evaluate("engineer", context_pct=94.0, rate_limit_pct=88.0)
        assert ev.context_action == ContextAction.PREPARE
        assert ev.rate_limit_action == RateLimitAction.CONSERVE

    def test_zero_pct_means_no_data(self, strategy):
        ev = strategy.evaluate("engineer", context_pct=0.0, rate_limit_pct=0.0)
        assert ev.context_action == ContextAction.NORMAL
        assert ev.rate_limit_action == RateLimitAction.NORMAL


class TestDispatchDecision:
    def test_dispatch_allowed_below_90(self, strategy):
        assert strategy.should_dispatch(80.0) is True

    def test_dispatch_blocked_at_90(self, strategy):
        """90% rate limit → stop dispatching new work."""
        assert strategy.should_dispatch(91.0) is False


class TestCompactionStagger:
    def test_compact_when_above_threshold(self, strategy):
        assert strategy.should_compact_agent("engineer", 96.0) is True

    def test_no_compact_below_threshold(self, strategy):
        assert strategy.should_compact_agent("engineer", 90.0) is False

    def test_stagger_prevents_simultaneous(self, strategy):
        strategy.record_compaction("architect")
        assert strategy.should_compact_agent("engineer", 96.0) is False

    def test_stagger_allows_after_cooldown(self, strategy):
        from datetime import datetime, timedelta
        strategy._last_compact["architect"] = datetime.now() - timedelta(seconds=200)
        assert strategy.should_compact_agent("engineer", 96.0) is True
