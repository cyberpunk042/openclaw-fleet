"""Tests for remaining Phase A building blocks.

- signal_rejection (doctor.py)
- TransferPackage formatting (transfer_context.py)
- append_contribution_to_task_context (context_writer.py)
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from fleet.core.doctor import (
    signal_rejection,
    get_rejection_signals,
    clear_rejection_signals,
)
from fleet.core.transfer_context import TransferPackage


# ─── signal_rejection ──────────────────────────────────────────────────


def test_signal_rejection_stores():
    clear_rejection_signals("test-agent")
    signal_rejection("test-agent", "task-1", "fleet-ops", "Missing tests")
    signals = get_rejection_signals("test-agent")
    assert len(signals) == 1
    assert signals[0]["task_id"] == "task-1"
    assert signals[0]["reviewer"] == "fleet-ops"
    assert signals[0]["reason"] == "Missing tests"
    clear_rejection_signals("test-agent")


def test_signal_rejection_accumulates():
    clear_rejection_signals("test-agent")
    signal_rejection("test-agent", "task-1", "fleet-ops", "Issue 1")
    signal_rejection("test-agent", "task-2", "fleet-ops", "Issue 2")
    signal_rejection("test-agent", "task-3", "fleet-ops", "Issue 3")
    signals = get_rejection_signals("test-agent")
    assert len(signals) == 3
    clear_rejection_signals("test-agent")


def test_signal_rejection_per_agent():
    clear_rejection_signals("agent-a")
    clear_rejection_signals("agent-b")
    signal_rejection("agent-a", "task-1", "fleet-ops", "A issue")
    signal_rejection("agent-b", "task-2", "fleet-ops", "B issue")
    assert len(get_rejection_signals("agent-a")) == 1
    assert len(get_rejection_signals("agent-b")) == 1
    clear_rejection_signals("agent-a")
    clear_rejection_signals("agent-b")


def test_signal_rejection_max_20():
    clear_rejection_signals("test-agent")
    for i in range(25):
        signal_rejection("test-agent", f"task-{i}", "fleet-ops", f"Issue {i}")
    signals = get_rejection_signals("test-agent")
    assert len(signals) == 20  # capped at 20
    clear_rejection_signals("test-agent")


def test_clear_rejection_signals():
    signal_rejection("test-agent", "task-1", "fleet-ops", "Issue")
    clear_rejection_signals("test-agent")
    signals = get_rejection_signals("test-agent")
    assert len(signals) == 0


def test_get_signals_empty_agent():
    signals = get_rejection_signals("never-signaled-agent")
    assert signals == []


def test_signal_has_timestamp():
    clear_rejection_signals("test-agent")
    signal_rejection("test-agent", "task-1", "fleet-ops", "Issue")
    signals = get_rejection_signals("test-agent")
    assert "time" in signals[0]
    assert "T" in signals[0]["time"]  # ISO format has T separator
    clear_rejection_signals("test-agent")


# ─── TransferPackage ───────────────────────────────────────────────────


def test_transfer_package_basic():
    pkg = TransferPackage(
        task_id="t1",
        from_agent="architect",
        to_agent="software-engineer",
        stage="reasoning",
        readiness=85,
        context_summary="Design complete. Ready for implementation.",
    )
    assert pkg.task_id == "t1"
    assert pkg.from_agent == "architect"
    assert pkg.to_agent == "software-engineer"


def test_transfer_package_format_basic():
    pkg = TransferPackage(
        task_id="t1",
        from_agent="architect",
        to_agent="software-engineer",
        stage="reasoning",
        readiness=85,
        context_summary="Design complete.",
    )
    text = pkg.format_for_injection()
    assert "TRANSFER CONTEXT" in text
    assert "architect" in text
    assert "software-engineer" in text
    assert "reasoning" in text
    assert "85%" in text
    assert "Design complete." in text


def test_transfer_package_with_contributions():
    pkg = TransferPackage(
        task_id="t1",
        from_agent="architect",
        to_agent="software-engineer",
        stage="work",
        readiness=99,
        context_summary="All inputs received.",
        contributions=[
            {"type": "design_input", "from": "architect", "summary": "Use adapter pattern"},
            {"type": "qa_test_definition", "from": "qa-engineer", "summary": "5 test criteria"},
        ],
    )
    text = pkg.format_for_injection()
    assert "Contributions received" in text
    assert "design_input" in text
    assert "qa_test_definition" in text
    assert "adapter pattern" in text


def test_transfer_package_with_artifacts():
    pkg = TransferPackage(
        task_id="t1",
        from_agent="architect",
        to_agent="software-engineer",
        contributions=[],
        artifacts=[
            {"type": "analysis_document", "completeness_pct": 100},
            {"type": "plan", "completeness_pct": 80},
        ],
    )
    text = pkg.format_for_injection()
    assert "Artifacts" in text
    assert "analysis_document" in text
    assert "100%" in text


def test_transfer_package_with_trail():
    pkg = TransferPackage(
        task_id="t1",
        from_agent="architect",
        to_agent="software-engineer",
        trail_events=[
            "Stage: analysis → investigation",
            "Contribution: qa-engineer qa_test_definition",
            "Stage: investigation → reasoning",
        ],
    )
    text = pkg.format_for_injection()
    assert "Trail summary" in text
    assert "analysis → investigation" in text


def test_transfer_package_empty():
    pkg = TransferPackage(task_id="t1", from_agent="a", to_agent="b")
    text = pkg.format_for_injection()
    assert "TRANSFER CONTEXT" in text
    # No contributions, artifacts, or trail sections
    assert "Contributions" not in text
    assert "Artifacts" not in text
    assert "Trail" not in text


# ─── append_contribution_to_task_context ──────────────────────────────


def test_append_contribution_creates_section():
    """Test that appending a contribution adds the section to context."""
    # Use a temp directory to avoid touching real agent files
    with tempfile.TemporaryDirectory() as tmpdir:
        agent_dir = Path(tmpdir) / "test-agent" / "context"
        agent_dir.mkdir(parents=True)

        # Write initial context
        ctx_file = agent_dir / "task-context.md"
        ctx_file.write_text("# Existing task context\n\nSome data here.\n")

        # Patch AGENTS_DIR to use temp
        with patch("fleet.core.context_writer.AGENTS_DIR", Path(tmpdir)):
            from fleet.core.context_writer import append_contribution_to_task_context
            result = append_contribution_to_task_context(
                agent_name="test-agent",
                contribution_type="design_input",
                contributor="architect",
                content="Use the adapter pattern for the API integration.",
            )
            assert result is True

            # Verify content was appended
            updated = ctx_file.read_text()
            assert "# Existing task context" in updated  # original preserved
            assert "CONTRIBUTION: design_input" in updated
            assert "architect" in updated
            assert "adapter pattern" in updated


def test_append_contribution_deduplicates():
    """Second append of same type from same contributor is skipped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        agent_dir = Path(tmpdir) / "test-agent" / "context"
        agent_dir.mkdir(parents=True)
        ctx_file = agent_dir / "task-context.md"
        ctx_file.write_text("# Context\n")

        with patch("fleet.core.context_writer.AGENTS_DIR", Path(tmpdir)):
            from fleet.core.context_writer import append_contribution_to_task_context

            # First append
            append_contribution_to_task_context("test-agent", "design_input", "architect", "Content A")
            first_size = len(ctx_file.read_text())

            # Second append — same type + contributor → should skip
            append_contribution_to_task_context("test-agent", "design_input", "architect", "Content B")
            second_size = len(ctx_file.read_text())

            assert second_size == first_size  # no change — deduplicated


def test_append_different_types_both_added():
    """Different contribution types from different contributors both append."""
    with tempfile.TemporaryDirectory() as tmpdir:
        agent_dir = Path(tmpdir) / "test-agent" / "context"
        agent_dir.mkdir(parents=True)
        ctx_file = agent_dir / "task-context.md"
        ctx_file.write_text("# Context\n")

        with patch("fleet.core.context_writer.AGENTS_DIR", Path(tmpdir)):
            from fleet.core.context_writer import append_contribution_to_task_context

            append_contribution_to_task_context("test-agent", "design_input", "architect", "Design stuff")
            append_contribution_to_task_context("test-agent", "qa_test_definition", "qa-engineer", "Test criteria")

            content = ctx_file.read_text()
            assert "CONTRIBUTION: design_input" in content
            assert "CONTRIBUTION: qa_test_definition" in content
            assert "architect" in content
            assert "qa-engineer" in content
