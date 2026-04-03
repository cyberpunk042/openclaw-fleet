"""Flow 1: Task Dispatch — Router → Stamp → Challenge.

Tests the dispatch path: router picks cheapest capable backend,
labor stamp records provenance, challenge engine validates work.
"""

from fleet.core.backend_router import route_task
from fleet.core.labor_stamp import (
    LaborStamp,
    assemble_stamp,
    mark_challenge_skipped,
)
from fleet.core.models import TaskCustomFields

from .conftest import make_task


def test_dispatch_complex_task():
    """Complex task routed to Claude opus."""
    task = make_task(story_points=5, task_type="story")
    decision = route_task(task, agent_name="worker")
    assert decision.backend == "claude-code"
    assert decision.model == "opus"


def test_dispatch_simple_task():
    """Simple task routed to cheapest capable backend."""
    task = make_task(story_points=1, task_type="subtask")
    decision = route_task(task, agent_name="worker")
    # Should prefer free backend for trivial tasks
    assert decision.backend in ("localai", "claude-code")


def test_dispatch_security_agent():
    """Security agent never routed to free/trainee."""
    task = make_task(story_points=1, task_type="subtask")
    decision = route_task(task, agent_name="devsecops-expert")
    assert decision.confidence_tier not in ("trainee", "community")


def test_dispatch_stamp_records_backend():
    """Labor stamp records the backend from routing decision."""
    task = make_task(story_points=3)
    decision = route_task(task, agent_name="worker")

    stamp = LaborStamp(
        agent_name="worker",
        backend=decision.backend,
        model=decision.model,
    )
    assert stamp.backend == decision.backend
    assert stamp.model == decision.model


def test_dispatch_challenge_skip():
    """Stamp can record a skipped challenge."""
    stamp = LaborStamp(
        agent_name="worker",
        backend="localai",
        model="hermes-3b",
    )
    mark_challenge_skipped(stamp, reason="deferred")
    assert stamp.challenge_skipped is True
    assert stamp.challenge_skip_reason == "deferred"
