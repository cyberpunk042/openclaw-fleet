"""Tests for fleet health monitoring."""

from datetime import datetime, timedelta

from fleet.core.health import assess_fleet_health
from fleet.core.models import Agent, Task, TaskCustomFields, TaskStatus


def _task(
    id: str = "t1", status: str = "inbox", agent: str = "",
    title: str = "Test", assigned_id: str = "",
    updated_at: datetime | None = None, created_at: datetime | None = None,
    blocked: bool = False, blocked_by: list[str] | None = None,
) -> Task:
    return Task(
        id=id, board_id="b1", title=title, status=TaskStatus(status),
        assigned_agent_id=assigned_id or None,
        custom_fields=TaskCustomFields(agent_name=agent),
        updated_at=updated_at, created_at=created_at,
        is_blocked=blocked, blocked_by_task_ids=blocked_by or [],
    )


def _agent(name: str, status: str = "online", id: str = "", last_seen: datetime | None = None) -> Agent:
    return Agent(id=id or f"id-{name}", name=name, status=status, last_seen=last_seen)


def test_healthy_fleet():
    now = datetime.now()
    tasks = [_task(status="done")]
    agents = [_agent("devops")]
    report = assess_fleet_health(tasks, agents, now)
    assert report.healthy
    assert report.agents_online == 1


def test_stale_in_progress_detected():
    now = datetime.now()
    tasks = [_task(status="in_progress", updated_at=now - timedelta(hours=10))]
    agents = [_agent("devops")]
    report = assess_fleet_health(tasks, agents, now)
    assert report.tasks_stale == 1
    assert any("Stale in_progress" in i.title for i in report.issues)


def test_stale_review_detected():
    now = datetime.now()
    tasks = [_task(status="review", updated_at=now - timedelta(hours=30))]
    agents = [_agent("fleet-ops")]
    report = assess_fleet_health(tasks, agents, now)
    assert any("Stale review" in i.title for i in report.issues)


def test_unassigned_inbox_detected():
    now = datetime.now()
    tasks = [_task(status="inbox", created_at=now - timedelta(hours=3))]
    agents = [_agent("devops")]
    report = assess_fleet_health(tasks, agents, now)
    assert any("Unassigned inbox" in i.title for i in report.issues)


def test_offline_agent_with_work_detected():
    now = datetime.now()
    tasks = [_task(status="in_progress", assigned_id="id-devops")]
    agents = [_agent("devops", status="offline", id="id-devops", last_seen=now - timedelta(hours=3))]
    report = assess_fleet_health(tasks, agents, now)
    assert any("Agent offline" in i.title for i in report.issues)


def test_stale_dependency_detected():
    now = datetime.now()
    tasks = [
        _task(id="blocker", status="done"),
        _task(id="blocked", status="inbox", blocked=True, blocked_by=["blocker"]),
    ]
    agents = [_agent("devops")]
    report = assess_fleet_health(tasks, agents, now)
    assert any("Stale dependency" in i.title for i in report.issues)


def test_blocked_count():
    now = datetime.now()
    tasks = [_task(blocked=True), _task(id="t2", blocked=True)]
    agents = [_agent("devops")]
    report = assess_fleet_health(tasks, agents, now)
    assert report.tasks_blocked == 2