"""Tests for MCClient parsing and helpers."""

from fleet.infra.mc_client import MCClient, _parse_datetime


def test_parse_task_basic():
    data = {
        "id": "abc-123", "board_id": "b1", "title": "Test task",
        "status": "inbox", "priority": "high",
        "custom_field_values": {"project": "fleet"},
    }
    task = MCClient._parse_task(data)
    assert task.id == "abc-123"
    assert task.title == "Test task"
    assert task.status.value == "inbox"
    assert task.priority == "high"
    assert task.custom_fields.project == "fleet"
    assert task.is_blocked is False
    assert task.auto_created is False


def test_parse_task_hierarchy_fields():
    data = {
        "id": "abc-123", "board_id": "b1", "title": "Subtask",
        "status": "inbox",
        "custom_field_values": {
            "parent_task": "parent-1",
            "task_type": "subtask",
            "plan_id": "dspd-s1",
            "story_points": 5,
            "sprint": "S1",
        },
    }
    task = MCClient._parse_task(data)
    assert task.custom_fields.parent_task == "parent-1"
    assert task.custom_fields.task_type == "subtask"
    assert task.custom_fields.plan_id == "dspd-s1"
    assert task.custom_fields.story_points == 5
    assert task.custom_fields.sprint == "S1"


def test_parse_task_blocked_fields():
    data = {
        "id": "abc-123", "board_id": "b1", "title": "Blocked task",
        "status": "inbox",
        "is_blocked": True,
        "blocked_by_task_ids": ["dep-1", "dep-2"],
        "depends_on_task_ids": ["dep-1", "dep-2"],
        "auto_created": True,
        "due_at": "2026-04-01T12:00:00Z",
        "custom_field_values": {},
    }
    task = MCClient._parse_task(data)
    assert task.is_blocked is True
    assert task.blocked_by_task_ids == ["dep-1", "dep-2"]
    assert task.depends_on == ["dep-1", "dep-2"]
    assert task.auto_created is True
    assert task.due_at is not None


def test_parse_task_timestamps():
    data = {
        "id": "abc-123", "board_id": "b1", "title": "Test",
        "status": "done",
        "created_at": "2026-03-28T10:00:00Z",
        "updated_at": "2026-03-28T12:30:00Z",
        "custom_field_values": {},
    }
    task = MCClient._parse_task(data)
    assert task.created_at is not None
    assert task.updated_at is not None


def test_parse_datetime_valid():
    dt = _parse_datetime("2026-03-28T10:00:00Z")
    assert dt is not None
    assert dt.year == 2026
    assert dt.month == 3
    assert dt.day == 28


def test_parse_datetime_none():
    assert _parse_datetime(None) is None
    assert _parse_datetime("") is None


def test_parse_datetime_invalid():
    assert _parse_datetime("not-a-date") is None


def test_parse_task_missing_optional_fields():
    """Minimal task data — all optional fields absent."""
    data = {
        "id": "min-1", "board_id": "b1", "title": "Minimal",
        "status": "inbox",
    }
    task = MCClient._parse_task(data)
    assert task.id == "min-1"
    assert task.custom_fields.parent_task is None
    assert task.custom_fields.task_type is None
    assert task.is_blocked is False
    assert task.blocked_by_task_ids == []
    assert task.depends_on == []
    assert task.auto_created is False
    assert task.due_at is None