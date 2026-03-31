"""Tests for event chain building."""

from fleet.core.event_chain import (
    EventSurface,
    build_alert_chain,
    build_contribution_chain,
    build_gate_request_chain,
    build_phase_advance_chain,
    build_rejection_chain,
    build_sprint_complete_chain,
    build_task_complete_chain,
    build_transfer_chain,
)


def test_task_complete_chain_has_all_surfaces():
    chain = build_task_complete_chain(
        task_id="t1", agent_name="devops", summary="Added docker config",
        pr_url="https://github.com/test/pr/1", branch="fleet/devops/t1",
        project="dspd",
    )
    assert chain.operation == "task_complete"
    assert len(chain.internal_events) >= 2  # status + approval + memory
    assert len(chain.public_events) >= 1    # push + PR
    assert len(chain.channel_events) >= 1   # IRC
    assert len(chain.notify_events) >= 1    # ntfy
    assert len(chain.meta_events) >= 1      # metrics


def test_task_complete_chain_no_code():
    chain = build_task_complete_chain(
        task_id="t1", agent_name="architect", summary="Designed architecture",
    )
    assert len(chain.public_events) == 0  # No branch/PR


def test_alert_chain_critical():
    chain = build_alert_chain(
        agent_name="devsecops-expert", severity="critical",
        title="CVE found", details="Details", category="security",
    )
    assert len(chain.internal_events) == 1
    assert len(chain.channel_events) == 1
    irc = chain.channel_events[0]
    assert irc.params["channel"] == "#alerts"  # Critical goes to #alerts

    notify = chain.notify_events[0]
    assert notify.params["priority"] == "urgent"


def test_alert_chain_medium():
    chain = build_alert_chain(
        agent_name="qa-engineer", severity="medium",
        title="Test coverage low", details="50% coverage",
    )
    irc = chain.channel_events[0]
    assert irc.params["channel"] == "#fleet"  # Medium goes to #fleet

    notify = chain.notify_events[0]
    assert notify.params["priority"] == "important"


def test_sprint_complete_chain():
    chain = build_sprint_complete_chain(
        plan_id="dspd-s1", total_tasks=8, story_points=24,
    )
    assert chain.operation == "sprint_complete"
    assert len(chain.internal_events) == 1
    assert len(chain.channel_events) == 1
    assert len(chain.notify_events) == 1
    assert "dspd-s1" in chain.channel_events[0].params["message"]


def test_chain_required_vs_optional():
    chain = build_task_complete_chain(
        task_id="t1", agent_name="devops", summary="Test",
    )
    required = [e for e in chain.events if e.required]
    optional = [e for e in chain.events if not e.required]
    assert len(required) >= 2   # Status update + approval are required
    assert len(optional) >= 1   # IRC, ntfy, metrics are optional


# ─── Contribution Chain ──────────────────────────────────────────────


def test_contribution_chain_structure():
    chain = build_contribution_chain(
        agent_name="qa-engineer",
        target_task_id="t1",
        target_task_title="Implement CI pipeline",
        contribution_type="qa_test_definition",
        summary="5 test criteria defined",
    )
    assert chain.operation == "contribution"
    assert chain.source_agent == "qa-engineer"
    assert chain.task_id == "t1"


def test_contribution_chain_has_trail():
    chain = build_contribution_chain(
        agent_name="architect",
        target_task_id="t1",
        target_task_title="Add auth",
        contribution_type="design_input",
    )
    trail_events = [
        e for e in chain.internal_events
        if "trail" in e.params.get("tags", [])
    ]
    assert len(trail_events) >= 1
    assert "contribution_received" in trail_events[0].params["tags"]


def test_contribution_chain_has_irc():
    chain = build_contribution_chain(
        agent_name="qa-engineer",
        target_task_id="t1",
        target_task_title="Add auth",
        contribution_type="qa_test_definition",
    )
    assert len(chain.channel_events) >= 1
    assert chain.channel_events[0].params["channel"] == "#contributions"


def test_contribution_chain_trail_is_optional():
    chain = build_contribution_chain(
        agent_name="qa-engineer",
        target_task_id="t1",
        target_task_title="Test",
        contribution_type="qa_test_definition",
    )
    trail_events = [
        e for e in chain.events
        if "trail" in e.params.get("tags", [])
    ]
    for te in trail_events:
        assert te.required is False  # trail must never break the chain


# ─── Gate Request Chain ──────────────────────────────────────────────


def test_gate_request_chain_structure():
    chain = build_gate_request_chain(
        agent_name="project-manager",
        task_id="t1",
        task_title="Add CI/CD",
        gate_type="readiness_90",
        summary="Plan confirmed, all contributions received",
    )
    assert chain.operation == "gate_request"
    assert chain.task_id == "t1"


def test_gate_request_has_po_required_tag():
    chain = build_gate_request_chain(
        agent_name="project-manager",
        task_id="t1",
        task_title="Add CI/CD",
        gate_type="readiness_90",
        summary="Ready",
    )
    memory_events = [
        e for e in chain.internal_events
        if e.action == "post_board_memory" and "po-required" in e.params.get("tags", [])
    ]
    assert len(memory_events) >= 1


def test_gate_request_has_ntfy():
    chain = build_gate_request_chain(
        agent_name="pm",
        task_id="t1",
        task_title="Test",
        gate_type="phase_advance",
        summary="Ready for MVP",
    )
    assert len(chain.notify_events) >= 1
    assert chain.notify_events[0].params["priority"] == "important"


def test_gate_request_goes_to_gates_channel():
    chain = build_gate_request_chain(
        agent_name="pm",
        task_id="t1",
        task_title="Test",
        gate_type="readiness_90",
        summary="Ready",
    )
    irc = chain.channel_events[0]
    assert irc.params["channel"] == "#gates"


# ─── Rejection Chain ─────────────────────────────────────────────────


def test_rejection_chain_structure():
    chain = build_rejection_chain(
        reviewer_name="fleet-ops",
        task_id="t1",
        task_title="Implement search",
        agent_name="software-engineer",
        reason="Doesn't match verbatim requirement",
        regressed_readiness=70,
        regressed_stage="reasoning",
    )
    assert chain.operation == "rejection"
    assert chain.task_id == "t1"


def test_rejection_mentions_agent():
    chain = build_rejection_chain(
        reviewer_name="fleet-ops",
        task_id="t1",
        task_title="Test",
        agent_name="engineer",
        reason="Wrong approach",
    )
    memory_events = [
        e for e in chain.internal_events
        if e.action == "post_board_memory"
    ]
    assert any("mention:engineer" in e.params.get("tags", []) for e in memory_events)


def test_rejection_has_trail():
    chain = build_rejection_chain(
        reviewer_name="fleet-ops",
        task_id="t1",
        task_title="Test",
        agent_name="engineer",
        reason="Wrong",
    )
    trail_events = [
        e for e in chain.events
        if "trail" in e.params.get("tags", [])
    ]
    assert len(trail_events) >= 1


def test_rejection_goes_to_reviews_channel():
    chain = build_rejection_chain(
        reviewer_name="fleet-ops",
        task_id="t1",
        task_title="Test",
        agent_name="engineer",
        reason="Wrong",
    )
    irc = chain.channel_events[0]
    assert irc.params["channel"] == "#reviews"


# ─── Phase Advance Chain ─────────────────────────────────────────────


def test_phase_advance_chain_structure():
    chain = build_phase_advance_chain(
        task_id="t1",
        task_title="NNRT Search",
        from_phase="poc",
        to_phase="mvp",
    )
    assert chain.operation == "phase_advance"
    assert chain.task_id == "t1"


def test_phase_advance_has_milestone_tag():
    chain = build_phase_advance_chain(
        task_id="t1",
        task_title="NNRT Search",
        from_phase="poc",
        to_phase="mvp",
    )
    memory_events = [
        e for e in chain.internal_events
        if e.action == "post_board_memory"
    ]
    assert any("milestone" in e.params.get("tags", []) for e in memory_events)


def test_phase_advance_notifies_fleet_and_sprint():
    chain = build_phase_advance_chain(
        task_id="t1",
        task_title="Test",
        from_phase="mvp",
        to_phase="staging",
    )
    channels = [e.params["channel"] for e in chain.channel_events]
    assert "#fleet" in channels
    assert "#sprint" in channels


def test_phase_advance_has_trail():
    chain = build_phase_advance_chain(
        task_id="t1",
        task_title="Test",
        from_phase="poc",
        to_phase="mvp",
        approved_by="po",
    )
    trail_events = [
        e for e in chain.events
        if "trail" in e.params.get("tags", [])
    ]
    assert len(trail_events) >= 1
    assert "po" in trail_events[0].params["content"]


# ─── Transfer Chain ──────────────────────────────────────────────────


def test_transfer_chain_structure():
    chain = build_transfer_chain(
        from_agent="architect",
        to_agent="software-engineer",
        task_id="t1",
        task_title="Implement auth",
        stage="work",
        readiness=99,
    )
    assert chain.operation == "transfer"
    assert chain.source_agent == "architect"


def test_transfer_mentions_receiving_agent():
    chain = build_transfer_chain(
        from_agent="architect",
        to_agent="software-engineer",
        task_id="t1",
        task_title="Test",
    )
    memory_events = [
        e for e in chain.internal_events
        if e.action == "post_board_memory"
    ]
    assert any(
        "mention:software-engineer" in e.params.get("tags", [])
        for e in memory_events
    )


def test_transfer_has_trail():
    chain = build_transfer_chain(
        from_agent="architect",
        to_agent="engineer",
        task_id="t1",
        task_title="Test",
        stage="reasoning",
        readiness=80,
    )
    trail_events = [
        e for e in chain.events
        if "trail" in e.params.get("tags", [])
    ]
    assert len(trail_events) >= 1
    content = trail_events[0].params["content"]
    assert "architect" in content
    assert "engineer" in content
    assert "reasoning" in content