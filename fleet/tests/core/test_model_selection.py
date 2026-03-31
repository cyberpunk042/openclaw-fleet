"""Tests for dynamic model and effort selection."""

from fleet.core.model_selection import select_model_for_task
from fleet.core.models import Task, TaskCustomFields, TaskStatus


def _task(
    sp: int = 0, task_type: str = "task", model: str = "",
) -> Task:
    return Task(
        id="t1", board_id="b1", title="Test", status=TaskStatus.INBOX,
        custom_fields=TaskCustomFields(
            story_points=sp, task_type=task_type, model=model,
        ),
    )


def test_explicit_override():
    config = select_model_for_task(_task(model="opus"), "devops")
    assert config.model == "opus"
    assert "explicit" in config.reason


def test_large_task_gets_opus():
    config = select_model_for_task(_task(sp=13), "software-engineer")
    assert config.model == "opus"
    assert config.effort == "high"


def test_epic_gets_opus_max():
    config = select_model_for_task(_task(task_type="epic"), "project-manager")
    assert config.model == "opus"
    assert config.effort == "max"


def test_blocker_gets_opus():
    config = select_model_for_task(_task(task_type="blocker"), "devops")
    assert config.model == "opus"
    assert config.effort == "high"


def test_medium_story_gets_opus():
    config = select_model_for_task(_task(sp=5, task_type="story"), "software-engineer")
    assert config.model == "opus"


def test_simple_subtask_gets_sonnet_low():
    config = select_model_for_task(_task(sp=1, task_type="subtask"), "software-engineer")
    assert config.model == "sonnet"
    assert config.effort == "low"


def test_deep_reasoning_agent_medium_task():
    # architect with sp=5 should get opus
    config = select_model_for_task(_task(sp=5), "architect")
    assert config.model == "opus"
    assert "deep reasoning" in config.reason


def test_worker_agent_medium_task_stays_sonnet():
    # software-engineer with sp=5 but not a story → sonnet high
    config = select_model_for_task(_task(sp=5), "software-engineer")
    assert config.model == "sonnet"
    assert config.effort == "high"


def test_standard_task():
    config = select_model_for_task(_task(sp=3), "devops")
    assert config.model == "sonnet"
    assert config.effort == "medium"


def test_default_no_sp():
    config = select_model_for_task(_task(), "software-engineer")
    assert config.model == "sonnet"


# ─── Budget Mode Constraints ────────────────────────────────────────


def test_economic_blocks_opus():
    """Economic mode should downgrade opus to sonnet."""
    config = select_model_for_task(_task(sp=13), "architect", budget_mode="economic")
    assert config.model == "sonnet"
    assert "constrained" in config.reason


def test_blitz_allows_opus():
    config = select_model_for_task(_task(sp=13), "architect", budget_mode="blitz")
    assert config.model == "opus"


def test_survival_blocks_all_claude():
    config = select_model_for_task(_task(sp=3), "software-engineer", budget_mode="survival")
    assert "blocked" in config.reason


def test_no_budget_mode_no_constraint():
    config = select_model_for_task(_task(sp=13), "architect", budget_mode="")
    assert config.model == "opus"  # Unconstrained


def test_economic_caps_effort():
    """Economic mode caps effort at medium."""
    config = select_model_for_task(_task(task_type="epic"), "architect", budget_mode="economic")
    assert config.effort == "medium"  # Capped from max