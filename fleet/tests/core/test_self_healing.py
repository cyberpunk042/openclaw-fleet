"""Tests for self-healing actions."""

from datetime import datetime

from fleet.core.health import HealthIssue, HealthReport
from fleet.core.self_healing import plan_healing_actions


def _report(*issues: HealthIssue) -> HealthReport:
    return HealthReport(timestamp=datetime.now(), issues=list(issues))


def test_stale_in_progress_creates_check_task():
    report = _report(HealthIssue(
        severity="high", category="task",
        title="Stale in_progress: Build API client",
        details="In progress for 12h", agent_name="software-engineer",
    ))
    actions = plan_healing_actions(report, [])
    assert len(actions) == 1
    assert actions[0].action == "check_stuck_agent"
    assert actions[0].target_agent == "software-engineer"


def test_stale_review_nudges_fleet_ops():
    report = _report(HealthIssue(
        severity="medium", category="task",
        title="Stale review: S1-5 PlaneClient",
        details="In review for 30h",
    ))
    actions = plan_healing_actions(report, [])
    assert actions[0].action == "nudge_reviewer"
    assert actions[0].target_agent == "fleet-ops"


def test_unassigned_routes_to_pm():
    report = _report(HealthIssue(
        severity="low", category="task",
        title="Unassigned inbox: New feature request",
        details="In inbox for 4h",
    ))
    actions = plan_healing_actions(report, [])
    assert actions[0].action == "route_unassigned"
    assert actions[0].target_agent == "project-manager"


def test_offline_agent_creates_restart():
    report = _report(HealthIssue(
        severity="high", category="agent",
        title="Agent offline with active task: devops",
        details="Offline for 3h", agent_name="devops",
    ))
    actions = plan_healing_actions(report, [])
    assert actions[0].action == "restart_agent"
    assert "devops" in actions[0].task_description


def test_critical_unresolvable_escalates():
    report = _report(HealthIssue(
        severity="critical", category="service",
        title="MC API unreachable",
        details="500 errors for 10 minutes",
    ))
    actions = plan_healing_actions(report, [])
    assert actions[0].escalate is True


def test_multiple_issues_produce_multiple_actions():
    report = _report(
        HealthIssue(severity="high", category="task", title="Stale in_progress: X", details=""),
        HealthIssue(severity="medium", category="task", title="Stale review: Y", details=""),
        HealthIssue(severity="low", category="task", title="Unassigned inbox: Z", details=""),
    )
    actions = plan_healing_actions(report, [])
    assert len(actions) == 3