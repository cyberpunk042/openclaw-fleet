"""Tests for the 8 new chain builders added for tool tree elevation."""

from fleet.core.event_chain import (
    EventSurface,
    build_comment_chain,
    build_accept_chain,
    build_commit_chain,
    build_task_create_chain,
    build_pause_chain,
    build_escalation_chain,
    build_progress_chain,
    build_artifact_chain,
)


# ─── build_comment_chain ────────────────────────────────────────────


def test_comment_chain_with_task_and_mention():
    chain = build_comment_chain(
        agent_name="engineer",
        task_id="t1",
        content="Is this the right pattern?",
        mention="architect",
    )
    assert chain.operation == "chat_message"
    assert chain.source_agent == "engineer"
    assert chain.task_id == "t1"

    # Should have Plane comment + trail (mention is not PO so no ntfy)
    plane_events = [e for e in chain.events if e.surface == EventSurface.PLANE]
    assert len(plane_events) == 1
    assert "architect" not in [e.params.get("title", "") for e in chain.events
                                if e.surface == EventSurface.NOTIFY]

    # Trail always present when task_id given
    trail = [e for e in chain.events if "trail" in str(e.params.get("tags", []))]
    assert len(trail) == 1


def test_comment_chain_po_mention_triggers_ntfy():
    chain = build_comment_chain(
        agent_name="pm",
        task_id="t1",
        content="Need your decision",
        mention="human",
    )
    ntfy = chain.notify_events
    assert len(ntfy) == 1
    assert ntfy[0].params["priority"] == "important"


def test_comment_chain_no_task_no_trail():
    chain = build_comment_chain(
        agent_name="engineer",
        content="General FYI",
    )
    # No task_id → no Plane, no trail
    assert len(chain.events) == 0


# ─── build_accept_chain ─────────────────────────────────────────────


def test_accept_chain_has_plane_and_trail():
    chain = build_accept_chain(
        agent_name="engineer",
        task_id="t1",
        task_title="Add type hints",
        plan_summary="Will add type hints to core module",
    )
    assert chain.operation == "task_accept"

    plane = [e for e in chain.events if e.surface == EventSurface.PLANE]
    assert len(plane) == 1
    assert "Plan accepted" in plane[0].params["comment"]

    trail = [e for e in chain.events if "trail" in str(e.params.get("tags", []))]
    assert len(trail) == 1
    assert "plan_accepted" in trail[0].params["tags"][1] or "plan_accepted" in str(trail[0].params)


# ─── build_commit_chain ─────────────────────────────────────────────


def test_commit_chain_has_comment_plane_trail():
    chain = build_commit_chain(
        agent_name="engineer",
        task_id="t1",
        message="feat(core): add type hints",
        sha="abc1234",
        files=["fleet/core/engine.py", "fleet/core/models.py"],
    )
    assert chain.operation == "task_commit"

    # MC comment with commit summary
    internal = [e for e in chain.events
                if e.surface == EventSurface.INTERNAL and e.action == "post_comment"]
    assert len(internal) == 1
    assert "abc1234" in internal[0].params["comment"]

    # Plane comment
    plane = [e for e in chain.events if e.surface == EventSurface.PLANE]
    assert len(plane) == 1

    # Trail
    trail = [e for e in chain.events if "trail" in str(e.params.get("tags", []))]
    assert len(trail) == 1


# ─── build_task_create_chain ─────────────────────────────────────────


def test_task_create_chain_with_parent_and_project():
    chain = build_task_create_chain(
        creator="pm",
        task_id="new1",
        task_title="Design auth middleware",
        parent_task_id="epic1",
        agent_name="architect",
        task_type="story",
        project="fleet",
    )
    assert chain.operation == "task_create"

    # Parent comment
    internal = [e for e in chain.events
                if e.surface == EventSurface.INTERNAL and e.action == "post_comment"]
    assert len(internal) == 1
    assert internal[0].params["task_id"] == "epic1"

    # Plane issue creation
    plane = [e for e in chain.events
             if e.surface == EventSurface.PLANE and e.action == "create_issue"]
    assert len(plane) == 1

    # Trail
    trail = [e for e in chain.events if "trail" in str(e.params.get("tags", []))]
    assert len(trail) == 1


def test_task_create_chain_no_parent_no_project():
    chain = build_task_create_chain(
        creator="engineer",
        task_id="new2",
        task_title="Fix bug",
    )
    # No parent → no parent comment
    internal = [e for e in chain.events
                if e.surface == EventSurface.INTERNAL and e.action == "post_comment"]
    assert len(internal) == 0

    # No project → no Plane issue
    plane = [e for e in chain.events if e.surface == EventSurface.PLANE]
    assert len(plane) == 0

    # Trail always present
    trail = [e for e in chain.events if "trail" in str(e.params.get("tags", []))]
    assert len(trail) == 1


# ─── build_pause_chain ──────────────────────────────────────────────


def test_pause_chain_has_pm_mention_plane_trail():
    chain = build_pause_chain(
        agent_name="engineer",
        task_id="t1",
        task_title="Add controls",
        reason="Blocked on architect design",
        needed="Need design input from architect",
    )
    assert chain.operation == "task_paused"

    # Board memory with PM mention (exclude trail events which are also post_board_memory)
    memory = [e for e in chain.events
              if e.surface == EventSurface.INTERNAL and e.action == "post_board_memory"
              and "trail" not in str(e.params.get("tags", []))]
    assert len(memory) == 1
    assert "mention:project-manager" in memory[0].params["tags"]

    # Plane comment
    plane = [e for e in chain.events if e.surface == EventSurface.PLANE]
    assert len(plane) == 1

    # Trail
    trail = [e for e in chain.events if "trail" in str(e.params.get("tags", []))]
    assert len(trail) == 1


# ─── build_escalation_chain ─────────────────────────────────────────


def test_escalation_chain_with_task():
    chain = build_escalation_chain(
        agent_name="engineer",
        task_id="t1",
        title="Need PO decision",
        details="Two valid approaches",
        question="Which should we use?",
    )
    assert chain.operation == "escalation"

    # Plane comment
    plane = [e for e in chain.events if e.surface == EventSurface.PLANE]
    assert len(plane) == 1

    # Trail
    trail = [e for e in chain.events if "trail" in str(e.params.get("tags", []))]
    assert len(trail) == 1


def test_escalation_chain_no_task():
    chain = build_escalation_chain(
        agent_name="pm",
        task_id="",
        title="Fleet concern",
        details="Budget running low",
    )
    # No task_id → no Plane, no trail
    assert len(chain.events) == 0


# ─── build_progress_chain ───────────────────────────────────────────


def test_progress_chain_at_50_has_irc():
    chain = build_progress_chain(
        agent_name="engineer",
        task_id="t1",
        task_title="Add controls",
        done="Implemented main component",
        next_step="Add tests",
        progress_pct=50,
    )
    assert chain.operation == "task_progress"

    # IRC at 50% checkpoint
    irc = [e for e in chain.events if e.surface == EventSurface.CHANNEL]
    assert len(irc) == 1
    assert "50%" in irc[0].params["message"]


def test_progress_chain_at_30_no_irc():
    chain = build_progress_chain(
        agent_name="engineer",
        task_id="t1",
        task_title="Add controls",
        done="Started work",
        progress_pct=30,
    )
    # No IRC at 30% (only at 50 and 90)
    irc = [e for e in chain.events if e.surface == EventSurface.CHANNEL]
    assert len(irc) == 0

    # But still has Plane + trail
    plane = [e for e in chain.events if e.surface == EventSurface.PLANE]
    assert len(plane) == 1

    trail = [e for e in chain.events if "trail" in str(e.params.get("tags", []))]
    assert len(trail) == 1


def test_progress_chain_at_90_has_irc():
    chain = build_progress_chain(
        agent_name="engineer",
        task_id="t1",
        task_title="Add controls",
        done="Almost done",
        progress_pct=90,
    )
    irc = [e for e in chain.events if e.surface == EventSurface.CHANNEL]
    assert len(irc) == 1
    assert "90%" in irc[0].params["message"]


# ─── build_artifact_chain ───────────────────────────────────────────


def test_artifact_created_chain():
    chain = build_artifact_chain(
        agent_name="architect",
        task_id="t1",
        artifact_type="analysis_document",
        completeness_pct=20,
        operation="artifact_created",
    )
    assert chain.operation == "artifact_created"

    # Trail only (Plane HTML handled by tool directly via transpose)
    trail = [e for e in chain.events if "trail" in str(e.params.get("tags", []))]
    assert len(trail) == 1
    assert "artifact_created" in str(trail[0].params)


def test_artifact_updated_chain():
    chain = build_artifact_chain(
        agent_name="architect",
        task_id="t1",
        artifact_type="analysis_document",
        field="findings",
        completeness_pct=60,
        operation="artifact_updated",
    )
    assert chain.operation == "artifact_updated"

    trail = [e for e in chain.events if "trail" in str(e.params.get("tags", []))]
    assert len(trail) == 1
    assert "field=findings" in trail[0].params["content"]


# ─── Cross-cutting: all trails are required=False ────────────────────


def test_all_trail_events_are_not_required():
    """Trail recording must never break the chain."""
    chains = [
        build_comment_chain("a", "t1", "msg", "b"),
        build_accept_chain("a", "t1", "title", "plan"),
        build_commit_chain("a", "t1", "msg", "sha"),
        build_task_create_chain("a", "t1", "title", "parent"),
        build_pause_chain("a", "t1", "title", "reason"),
        build_escalation_chain("a", "t1", "title", "details"),
        build_progress_chain("a", "t1", "title", progress_pct=50),
        build_artifact_chain("a", "t1", "type"),
    ]
    for chain in chains:
        for event in chain.events:
            if "trail" in str(event.params.get("tags", [])):
                assert not event.required, (
                    f"Trail event in {chain.operation} is required=True — "
                    f"trail must never break chains"
                )


# ─── Cross-cutting: all Plane events are required=False ──────────────


def test_all_plane_events_are_not_required():
    """Plane is optional — Plane events must not break chains."""
    chains = [
        build_comment_chain("a", "t1", "msg"),
        build_accept_chain("a", "t1", "title", "plan"),
        build_commit_chain("a", "t1", "msg", "sha"),
        build_task_create_chain("a", "t1", "title", project="fleet"),
        build_pause_chain("a", "t1", "title", "reason"),
        build_escalation_chain("a", "t1", "title", "details"),
        build_progress_chain("a", "t1", "title", progress_pct=50),
    ]
    for chain in chains:
        for event in chain.events:
            if event.surface == EventSurface.PLANE:
                assert not event.required, (
                    f"Plane event in {chain.operation} is required=True — "
                    f"Plane must never break chains"
                )
