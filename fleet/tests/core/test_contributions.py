"""Comprehensive tests for contribution system.

Tests check_contribution_completeness and detect_contribution_opportunities
against REAL config/synergy-matrix.yaml.
"""

from fleet.core.contributions import (
    check_contribution_completeness,
    detect_contribution_opportunities,
    load_synergy_matrix,
    get_skip_types,
    ContributionStatus,
)


# ─── Synergy matrix loading ─────────────────────────────────────────


def test_synergy_matrix_loads():
    matrix = load_synergy_matrix()
    assert "software-engineer" in matrix
    assert "architect" in matrix
    assert len(matrix) > 0


def test_synergy_matrix_engineer_has_architect():
    matrix = load_synergy_matrix()
    engineer_specs = matrix.get("software-engineer", [])
    architect_spec = [s for s in engineer_specs if s.role == "architect"]
    assert len(architect_spec) > 0
    assert architect_spec[0].contribution_type == "design_input"
    assert architect_spec[0].priority == "required"


def test_synergy_matrix_engineer_has_qa():
    matrix = load_synergy_matrix()
    engineer_specs = matrix.get("software-engineer", [])
    qa_spec = [s for s in engineer_specs if s.role == "qa-engineer"]
    assert len(qa_spec) > 0
    assert qa_spec[0].contribution_type == "qa_test_definition"
    assert qa_spec[0].priority == "required"


def test_skip_types():
    skip = get_skip_types()
    assert "subtask" in skip
    assert "blocker" in skip
    assert "spike" in skip
    assert "concern" in skip


# ─── check_contribution_completeness — skip types ────────────────────


def test_subtask_skips_contributions():
    """Subtasks skip contributions entirely."""
    status = check_contribution_completeness(
        task_id="t1",
        target_agent="software-engineer",
        task_type="subtask",
        received_types=[],
    )
    assert status.all_received is True
    assert status.required == []
    assert status.completeness_pct == 100.0


def test_blocker_skips_contributions():
    status = check_contribution_completeness(
        task_id="t1",
        target_agent="software-engineer",
        task_type="blocker",
        received_types=[],
    )
    assert status.all_received is True


def test_spike_skips_contributions():
    status = check_contribution_completeness(
        task_id="t1",
        target_agent="software-engineer",
        task_type="spike",
        received_types=[],
    )
    assert status.all_received is True


# ─── check_contribution_completeness — engineer ──────────────────────


def test_engineer_task_no_contributions_received():
    """Engineer task type needs architect design_input + QA tests."""
    status = check_contribution_completeness(
        task_id="t1",
        target_agent="software-engineer",
        task_type="task",
        received_types=[],
    )
    assert status.all_received is False
    assert "design_input" in status.required
    assert "qa_test_definition" in status.required
    assert "design_input" in status.missing
    assert "qa_test_definition" in status.missing
    assert status.completeness_pct == 0.0


def test_engineer_task_architect_only():
    """Engineer received architect input but not QA."""
    status = check_contribution_completeness(
        task_id="t1",
        target_agent="software-engineer",
        task_type="task",
        received_types=["design_input"],
    )
    assert status.all_received is False
    assert "design_input" in status.received
    assert "qa_test_definition" in status.missing
    assert status.completeness_pct == 50.0


def test_engineer_task_all_received():
    """Engineer received both required contributions."""
    status = check_contribution_completeness(
        task_id="t1",
        target_agent="software-engineer",
        task_type="task",
        received_types=["design_input", "qa_test_definition"],
    )
    assert status.all_received is True
    assert len(status.missing) == 0
    assert status.completeness_pct == 100.0


def test_engineer_task_extra_contributions_ok():
    """Extra contributions beyond required don't cause issues."""
    status = check_contribution_completeness(
        task_id="t1",
        target_agent="software-engineer",
        task_type="task",
        received_types=["design_input", "qa_test_definition", "ux_spec", "security_requirement"],
    )
    assert status.all_received is True


# ─── check_contribution_completeness — architect ──────────────────────


def test_architect_needs_feasibility():
    """Architect tasks need feasibility_assessment from engineer (recommended, not required)."""
    status = check_contribution_completeness(
        task_id="t1",
        target_agent="architect",
        task_type="task",
        received_types=[],
    )
    # Check what architect requires — may be empty if no "required" priority
    matrix = load_synergy_matrix()
    arch_specs = matrix.get("architect", [])
    required = [s for s in arch_specs if s.priority == "required"]
    if required:
        assert status.all_received is False
    else:
        assert status.all_received is True  # no required contributions


# ─── check_contribution_completeness — unknown agent ──────────────────


def test_unknown_agent_no_requirements():
    """Agent not in synergy matrix has no contribution requirements."""
    status = check_contribution_completeness(
        task_id="t1",
        target_agent="nonexistent-agent",
        task_type="task",
        received_types=[],
    )
    assert status.all_received is True
    assert status.required == []


# ─── detect_contribution_opportunities ─────────────────────────────────


def test_detect_opportunities_for_engineer_task():
    """Engineer task should generate contribution opportunities."""
    opps = detect_contribution_opportunities(
        task_id="t1",
        target_agent="software-engineer",
        task_type="task",
    )
    # Should have at least architect + QA opportunities
    roles = [o.contributor_role for o in opps]
    assert "architect" in roles
    assert "qa-engineer" in roles


def test_detect_opportunities_for_subtask():
    """Subtasks generate no contribution opportunities."""
    opps = detect_contribution_opportunities(
        task_id="t1",
        target_agent="software-engineer",
        task_type="subtask",
    )
    assert len(opps) == 0


def test_detect_opportunities_for_blocker():
    """Blockers generate no contribution opportunities."""
    opps = detect_contribution_opportunities(
        task_id="t1",
        target_agent="software-engineer",
        task_type="blocker",
    )
    assert len(opps) == 0


def test_opportunity_has_correct_fields():
    opps = detect_contribution_opportunities(
        task_id="t1",
        target_agent="software-engineer",
        task_type="story",
    )
    if opps:
        opp = opps[0]
        assert opp.target_task_id == "t1"
        assert opp.target_agent == "software-engineer"
        assert opp.contributor_role != ""
        assert opp.contribution_type != ""
        assert opp.priority in ("required", "recommended")
