"""Tests for change detection between orchestrator cycles."""

from fleet.core.change_detector import ChangeDetector
from fleet.core.models import Task, TaskCustomFields, TaskStatus


def _task(id: str, status: str = "inbox", blocked: bool = False, title: str = "Test") -> Task:
    return Task(
        id=id, board_id="b1", title=title,
        status=TaskStatus(status),
        is_blocked=blocked,
    )


def test_first_cycle_detects_all_as_new():
    detector = ChangeDetector()
    tasks = [_task("t1"), _task("t2", "review")]
    changes = detector.detect(tasks)
    assert len(changes.changes) == 2
    assert all(c.change_type == "task_created" for c in changes.changes)


def test_no_changes_on_same_state():
    detector = ChangeDetector()
    tasks = [_task("t1", "inbox"), _task("t2", "done")]
    detector.detect(tasks)
    # Same state again
    changes = detector.detect(tasks)
    assert not changes.has_changes


def test_status_change_detected():
    detector = ChangeDetector()
    detector.detect([_task("t1", "inbox")])
    changes = detector.detect([_task("t1", "review")])
    assert changes.has_changes
    assert changes.changes[0].change_type == "task_status_changed"
    assert changes.changes[0].old_value == "inbox"
    assert changes.changes[0].new_value == "review"


def test_new_review_task_tracked():
    detector = ChangeDetector()
    detector.detect([_task("t1", "inbox")])
    changes = detector.detect([_task("t1", "review")])
    assert "t1" in changes.new_tasks_in_review
    assert changes.needs_review_wake


def test_new_done_task_tracked():
    detector = ChangeDetector()
    detector.detect([_task("t1", "review")])
    changes = detector.detect([_task("t1", "done")])
    assert "t1" in changes.new_tasks_done


def test_unblocked_task_detected():
    detector = ChangeDetector()
    detector.detect([_task("t1", "inbox", blocked=True)])
    changes = detector.detect([_task("t1", "inbox", blocked=False)])
    assert "t1" in changes.tasks_unblocked
    assert changes.needs_dispatch


def test_new_inbox_task_needs_dispatch():
    detector = ChangeDetector()
    detector.detect([])
    changes = detector.detect([_task("t1", "inbox")])
    assert "t1" in changes.new_tasks_in_inbox
    assert changes.needs_dispatch


def test_no_review_wake_when_no_review_changes():
    detector = ChangeDetector()
    detector.detect([_task("t1", "done")])
    changes = detector.detect([_task("t1", "done")])
    assert not changes.needs_review_wake