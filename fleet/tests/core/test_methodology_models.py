"""Tests for methodology model selection — MethodologyConfig.select_model_for_task().

Verifies that the condition evaluator correctly maps task attributes to
named methodology models from config/methodology.yaml.
"""

import pytest
from fleet.core.methodology_config import (
    get_methodology_config,
    reload_methodology_config,
    _evaluate_condition,
    _evaluate_clause,
)


@pytest.fixture(autouse=True)
def _fresh_config():
    """Reload config for each test to avoid stale cache."""
    reload_methodology_config()
    yield


class TestClauseEvaluator:
    """Unit tests for the clause evaluation primitives."""

    def test_is_set_truthy(self):
        assert _evaluate_clause("contribution_type is set", {"contribution_type": "design_input"})

    def test_is_set_empty(self):
        assert not _evaluate_clause("contribution_type is set", {"contribution_type": ""})

    def test_gte_match(self):
        assert _evaluate_clause("labor_iteration >= 2", {"labor_iteration": 3})

    def test_gte_below(self):
        assert not _evaluate_clause("labor_iteration >= 2", {"labor_iteration": 1})

    def test_eq_match(self):
        assert _evaluate_clause("priority = urgent", {"priority": "urgent"})

    def test_eq_no_match(self):
        assert not _evaluate_clause("priority = urgent", {"priority": "high"})

    def test_in_match(self):
        assert _evaluate_clause("task_type in [spike, concern]", {"task_type": "spike"})

    def test_in_no_match(self):
        assert not _evaluate_clause("task_type in [spike, concern]", {"task_type": "story"})

    def test_and_all_match(self):
        fields = {"task_type": "blocker", "priority": "urgent"}
        assert _evaluate_condition("task_type = blocker AND priority = urgent", fields)

    def test_and_partial_match(self):
        fields = {"task_type": "blocker", "priority": "high"}
        assert not _evaluate_condition("task_type = blocker AND priority = urgent", fields)


class TestModelSelection:
    """Integration tests against real config/methodology.yaml rules."""

    def test_contribution_type_set(self):
        cfg = get_methodology_config()
        model = cfg.select_model_for_task(contribution_type="design_input")
        assert model.name == "contribution"

    def test_rework_iteration(self):
        cfg = get_methodology_config()
        model = cfg.select_model_for_task(labor_iteration=2)
        assert model.name == "rework"

    def test_spike_research(self):
        cfg = get_methodology_config()
        model = cfg.select_model_for_task(task_type="spike")
        assert model.name == "research"

    def test_concern_research(self):
        cfg = get_methodology_config()
        model = cfg.select_model_for_task(task_type="concern")
        assert model.name == "research"

    def test_blocker_urgent_hotfix(self):
        cfg = get_methodology_config()
        model = cfg.select_model_for_task(task_type="blocker", priority="urgent")
        assert model.name == "hotfix"

    def test_blocker_non_urgent_not_hotfix(self):
        cfg = get_methodology_config()
        model = cfg.select_model_for_task(task_type="blocker", priority="high")
        assert model.name == "feature-development"

    def test_fleet_ops_review(self):
        cfg = get_methodology_config()
        model = cfg.select_model_for_task(agent_name="fleet-ops", task_status="review")
        assert model.name == "review"

    def test_default_feature_development(self):
        cfg = get_methodology_config()
        model = cfg.select_model_for_task(task_type="story")
        assert model.name == "feature-development"
