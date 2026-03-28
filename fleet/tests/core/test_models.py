"""Tests for fleet core domain models."""

from fleet.core.models import (
    Agent,
    AgentRole,
    AlertSeverity,
    Approval,
    Commit,
    CommitType,
    FleetContext,
    Project,
    Task,
    TaskCustomFields,
    TaskStatus,
    TaskType,
)


def test_task_short_id():
    task = Task(id="3402f526-78c2-455f-b7fb-f21765d67593", board_id="b", title="Test", status=TaskStatus.INBOX)
    assert task.short_id == "3402f526"


def test_task_status_values():
    assert TaskStatus.INBOX.value == "inbox"
    assert TaskStatus.IN_PROGRESS.value == "in_progress"
    assert TaskStatus.REVIEW.value == "review"
    assert TaskStatus.DONE.value == "done"


def test_project_github_url():
    proj = Project(name="nnrt", owner="cyberpunk042", repo="Narrative-to-Neutral-Report-Transformer")
    assert proj.github_url == "https://github.com/cyberpunk042/Narrative-to-Neutral-Report-Transformer"


def test_commit_short_sha():
    commit = Commit(sha="8223d7cabcdef123456", message="test")
    assert commit.short_sha == "8223d7c"


def test_commit_type_enum():
    assert CommitType.FEAT.value == "feat"
    assert CommitType.FIX.value == "fix"
    assert CommitType.DOCS.value == "docs"


def test_alert_severity_enum():
    assert AlertSeverity.CRITICAL.value == "critical"
    assert AlertSeverity.LOW.value == "low"


def test_task_custom_fields_defaults():
    fields = TaskCustomFields()
    assert fields.project is None
    assert fields.pr_url is None
    assert fields.branch is None


def test_agent_defaults():
    agent = Agent(id="test", name="architect")
    assert agent.role == AgentRole.WORKER
    assert agent.status == "offline"
    assert agent.model == "sonnet"


def test_approval_defaults():
    approval = Approval(
        id="a1", board_id="b1", task_id="t1",
        action_type="review", confidence=92.5,
    )
    assert approval.status == "pending"
    assert approval.confidence == 92.5
    assert approval.rubric_scores == {}


def test_fleet_context_structure():
    ctx = FleetContext(
        task=Task(id="t1", board_id="b1", title="Test", status=TaskStatus.INBOX),
        project=Project(name="nnrt", owner="o", repo="r"),
        agent=Agent(id="a1", name="sw-eng"),
    )
    assert ctx.task.title == "Test"
    assert ctx.project.name == "nnrt"
    assert ctx.agent.name == "sw-eng"
    assert ctx.recent_memory == []


def test_task_type_enum():
    assert TaskType.EPIC.value == "epic"
    assert TaskType.STORY.value == "story"
    assert TaskType.SUBTASK.value == "subtask"
    assert TaskType.BLOCKER.value == "blocker"
    assert TaskType.REQUEST.value == "request"
    assert TaskType.CONCERN.value == "concern"


def test_task_custom_fields_hierarchy():
    fields = TaskCustomFields(parent_task="abc123", task_type="subtask", plan_id="dspd-s1")
    assert fields.parent_task == "abc123"
    assert fields.task_type == "subtask"
    assert fields.plan_id == "dspd-s1"


def test_task_blocked_fields():
    task = Task(
        id="t1", board_id="b1", title="Test", status=TaskStatus.INBOX,
        is_blocked=True, blocked_by_task_ids=["t2", "t3"],
        auto_created=True,
    )
    assert task.is_blocked is True
    assert len(task.blocked_by_task_ids) == 2
    assert task.auto_created is True
    assert task.due_at is None


def test_task_defaults_not_blocked():
    task = Task(id="t1", board_id="b1", title="Test", status=TaskStatus.INBOX)
    assert task.is_blocked is False
    assert task.blocked_by_task_ids == []
    assert task.auto_created is False