"""Tests for remote change detection."""

from fleet.core.models import Task, TaskCustomFields, TaskStatus
from fleet.core.remote_watcher import classify_human_comment, classify_pr_change


def _task(pr_url: str = "https://github.com/test/pr/1", agent: str = "devops") -> Task:
    return Task(
        id="t1", board_id="b1", title="Test", status=TaskStatus.REVIEW,
        custom_fields=TaskCustomFields(pr_url=pr_url, agent_name=agent),
    )


def test_pr_merged():
    change = classify_pr_change(_task(), pr_state="MERGED", previous_state="OPEN")
    assert change is not None
    assert change.source == "github_pr_merged"
    assert "done" in change.action_needed.lower()


def test_pr_closed():
    change = classify_pr_change(_task(), pr_state="CLOSED", previous_state="OPEN")
    assert change is not None
    assert change.source == "github_pr_closed"
    assert "rework" in change.action_needed.lower() or "abandoned" in change.action_needed.lower()


def test_pr_no_change():
    change = classify_pr_change(_task(), pr_state="OPEN", previous_state="OPEN")
    assert change is None


def test_human_comment_fix_request():
    change = classify_human_comment(_task(), "Please fix the error handling for when Plane is unreachable")
    assert "implement" in change.action_needed.lower() or "change" in change.action_needed.lower()
    assert change.target_agent == "devops"


def test_human_comment_approval():
    change = classify_human_comment(_task(), "LGTM, looks good to merge")
    assert "approve" in change.action_needed.lower() or "merge" in change.action_needed.lower()


def test_human_comment_rejection():
    change = classify_human_comment(_task(), "Reject this, we're going a different direction")
    assert "reject" in change.action_needed.lower() or "close" in change.action_needed.lower()


def test_human_comment_question():
    change = classify_human_comment(_task(), "Why did you use this pattern? Can you explain??")
    assert "answer" in change.action_needed.lower() or "question" in change.action_needed.lower()