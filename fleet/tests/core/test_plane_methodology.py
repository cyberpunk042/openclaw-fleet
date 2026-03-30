"""Tests for fleet.core.plane_methodology — Plane methodology integration."""

import pytest
from fleet.core.plane_methodology import (
    VALID_READINESS,
    VALID_STAGES,
    extract_stage_from_labels,
    extract_readiness_from_labels,
    extract_verbatim_from_html,
    inject_verbatim_into_html,
    extract_methodology_state,
    build_label_updates,
)


class TestExtractStage:
    def test_no_stage_label(self):
        assert extract_stage_from_labels(["agent:pm", "blocked"]) is None

    def test_single_stage(self):
        assert extract_stage_from_labels(["stage:conversation"]) == "conversation"

    def test_stage_with_other_labels(self):
        assert extract_stage_from_labels(["agent:pm", "stage:reasoning", "infra"]) == "reasoning"

    def test_all_valid_stages(self):
        for stage in VALID_STAGES:
            assert extract_stage_from_labels([f"stage:{stage}"]) == stage

    def test_invalid_stage_ignored(self):
        assert extract_stage_from_labels(["stage:invalid"]) is None

    def test_multiple_stages_returns_last(self):
        assert extract_stage_from_labels(["stage:conversation", "stage:work"]) == "work"


class TestExtractReadiness:
    def test_no_readiness_label(self):
        assert extract_readiness_from_labels(["agent:pm"]) == 0

    def test_single_readiness(self):
        assert extract_readiness_from_labels(["readiness:50"]) == 50

    def test_all_valid_readiness(self):
        for val in VALID_READINESS:
            assert extract_readiness_from_labels([f"readiness:{val}"]) == val

    def test_invalid_readiness_ignored(self):
        assert extract_readiness_from_labels(["readiness:42"]) == 0

    def test_multiple_readiness_returns_highest(self):
        assert extract_readiness_from_labels(["readiness:30", "readiness:70"]) == 70

    def test_non_numeric_ignored(self):
        assert extract_readiness_from_labels(["readiness:abc"]) == 0


class TestExtractVerbatim:
    def test_no_verbatim(self):
        assert extract_verbatim_from_html("<p>Just a description</p>") is None

    def test_empty_html(self):
        assert extract_verbatim_from_html("") is None

    def test_none_html(self):
        assert extract_verbatim_from_html(None) is None

    def test_verbatim_present(self):
        html = (
            '<span class="fleet-verbatim" style="display:none">Add controls to the header bar</span>\n'
            '<blockquote><strong>Verbatim Requirement (PO)</strong><br/>\n'
            'Add controls to the header bar\n'
            '</blockquote>\n'
            '<p>More description</p>'
        )
        assert extract_verbatim_from_html(html) == "Add controls to the header bar"

    def test_verbatim_fallback_blockquote(self):
        """Falls back to blockquote if span marker missing (legacy)."""
        html = (
            '<blockquote><strong>Verbatim Requirement (PO)</strong><br/>\n'
            'The exact words from PO\n'
            '</blockquote>'
        )
        result = extract_verbatim_from_html(html)
        assert "The exact words from PO" in result


class TestInjectVerbatim:
    def test_inject_into_empty(self):
        result = inject_verbatim_into_html("", "Build the thing")
        assert "Build the thing" in result
        assert "fleet-verbatim" in result
        assert "<blockquote>" in result

    def test_inject_prepends(self):
        result = inject_verbatim_into_html("<p>Existing desc</p>", "Build the thing")
        assert result.index("fleet-verbatim") < result.index("Existing desc")

    def test_inject_replaces_existing(self):
        html = (
            '<span class="fleet-verbatim" style="display:none">Old requirement</span>\n'
            '<blockquote><strong>Verbatim Requirement (PO)</strong><br/>\n'
            'Old requirement\n'
            '</blockquote>\n'
            '<p>Description</p>'
        )
        result = inject_verbatim_into_html(html, "New requirement")
        assert "New requirement" in result
        assert "Old requirement" not in result
        assert "<p>Description</p>" in result

    def test_inject_only_one_section(self):
        result = inject_verbatim_into_html("", "Test")
        assert result.count("fleet-verbatim") == 1


class TestExtractMethodologyState:
    def test_full_state(self):
        labels = ["agent:pm", "stage:reasoning", "readiness:90"]
        html = (
            '<span class="fleet-verbatim" style="display:none">Build the immune system</span>\n'
            '<blockquote><strong>Verbatim Requirement (PO)</strong><br/>\n'
            'Build the immune system</blockquote>'
        )
        state = extract_methodology_state(labels, html)
        assert state.task_stage == "reasoning"
        assert state.task_readiness == 90
        assert state.requirement_verbatim == "Build the immune system"

    def test_empty_state(self):
        state = extract_methodology_state([], "")
        assert state.task_stage is None
        assert state.task_readiness == 0
        assert state.requirement_verbatim is None


class TestBuildLabelUpdates:
    def test_add_stage(self):
        result = build_label_updates(["agent:pm"], stage="work")
        assert "stage:work" in result
        assert "agent:pm" in result

    def test_replace_stage(self):
        result = build_label_updates(["stage:conversation", "agent:pm"], stage="reasoning")
        assert "stage:reasoning" in result
        assert "stage:conversation" not in result
        assert "agent:pm" in result

    def test_add_readiness(self):
        result = build_label_updates(["agent:pm"], readiness=50)
        assert "readiness:50" in result

    def test_replace_readiness(self):
        result = build_label_updates(["readiness:30", "agent:pm"], readiness=90)
        assert "readiness:90" in result
        assert "readiness:30" not in result

    def test_snap_to_nearest(self):
        result = build_label_updates([], readiness=47)
        assert "readiness:50" in result

    def test_snap_to_nearest_low(self):
        result = build_label_updates([], readiness=3)
        assert "readiness:5" in result

    def test_both_stage_and_readiness(self):
        result = build_label_updates(["agent:pm"], stage="work", readiness=99)
        assert "stage:work" in result
        assert "readiness:99" in result
        assert "agent:pm" in result

    def test_none_values_no_change(self):
        result = build_label_updates(["agent:pm", "stage:analysis"])
        assert "agent:pm" in result
        assert "stage:analysis" not in result  # removed when no new stage specified