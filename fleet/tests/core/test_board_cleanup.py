"""Tests for board cleanup — noise identification."""

from datetime import datetime, timedelta

from fleet.core.board_cleanup import identify_noise_tasks, plan_cleanup
from fleet.core.models import Task, TaskCustomFields, TaskStatus


def _task(title: str, status: str = "done", plan_id: str = "", pr_url: str = "",
          updated_at: datetime | None = None) -> Task:
    return Task(
        id=f"id-{title[:8]}", board_id="b1", title=title,
        status=TaskStatus(status),
        custom_fields=TaskCustomFields(plan_id=plan_id, pr_url=pr_url),
        updated_at=updated_at,
    )


def test_heartbeat_is_noise():
    tasks = [_task("[heartbeat] project-manager periodic check")]
    noise, keep = identify_noise_tasks(tasks)
    assert len(noise) == 1
    assert len(keep) == 0


def test_review_process_is_noise():
    tasks = [_task("[review] Process 5 pending approvals")]
    noise, keep = identify_noise_tasks(tasks)
    assert len(noise) == 1


def test_resolve_conflict_is_noise():
    tasks = [_task("Resolve conflict: PR #7")]
    noise, keep = identify_noise_tasks(tasks)
    assert len(noise) == 1


def test_sprint_task_kept():
    tasks = [_task("S3-1: Configure Plane", plan_id="dspd-s3")]
    noise, keep = identify_noise_tasks(tasks)
    assert len(keep) == 1
    assert len(noise) == 0


def test_active_task_kept():
    tasks = [_task("[heartbeat] test", status="in_progress")]
    noise, keep = identify_noise_tasks(tasks)
    assert len(keep) == 1  # Active tasks always kept even if heartbeat


def test_recent_task_kept():
    now = datetime.now()
    tasks = [_task("Old heartbeat thing", updated_at=now - timedelta(days=1))]
    noise, keep = identify_noise_tasks(tasks, keep_recent_days=7, now=now)
    assert len(keep) == 1  # Recent enough


def test_pr_task_kept():
    tasks = [_task("Some task", pr_url="https://github.com/test/pr/1")]
    noise, keep = identify_noise_tasks(tasks)
    assert len(keep) == 1


def test_plan_cleanup_categorizes():
    tasks = [
        _task("[heartbeat] pm check"),
        _task("[heartbeat] ops check"),
        _task("[review] Process 3 pending"),
        _task("Resolve conflict: PR #5"),
        _task("S3-1: Real work", plan_id="s3"),
    ]
    result = plan_cleanup(tasks)
    assert result.archived == 4
    assert result.kept == 1
    assert result.categories.get("heartbeat") == 2
    assert result.categories.get("review_process") == 1
    assert result.categories.get("resolve_conflict") == 1