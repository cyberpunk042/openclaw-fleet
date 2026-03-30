"""Tests for fleet.core.stage_context — stage-aware protocol instructions."""

import pytest
from fleet.core.stage_context import (
    STAGE_INSTRUCTIONS,
    get_stage_instructions,
    get_stage_summary,
)
from fleet.core.methodology import Stage


class TestStageInstructions:
    def test_all_stages_have_instructions(self):
        for stage in Stage:
            assert stage in STAGE_INSTRUCTIONS
            assert len(STAGE_INSTRUCTIONS[stage]) > 100

    def test_conversation_prohibits_code(self):
        text = STAGE_INSTRUCTIONS[Stage.CONVERSATION]
        assert "Do NOT write code" in text
        assert "Do NOT commit" in text
        assert "fleet_commit" in text

    def test_analysis_prohibits_solutions(self):
        text = STAGE_INSTRUCTIONS[Stage.ANALYSIS]
        assert "Do NOT produce solutions" in text

    def test_investigation_prohibits_decisions(self):
        text = STAGE_INSTRUCTIONS[Stage.INVESTIGATION]
        assert "Do NOT decide" in text

    def test_reasoning_references_verbatim(self):
        text = STAGE_INSTRUCTIONS[Stage.REASONING]
        assert "verbatim requirement" in text

    def test_work_has_tool_sequence(self):
        text = STAGE_INSTRUCTIONS[Stage.WORK]
        assert "fleet_read_context" in text
        assert "fleet_task_accept" in text
        assert "fleet_commit" in text
        assert "fleet_task_complete" in text

    def test_work_prohibits_scope_creep(self):
        text = STAGE_INSTRUCTIONS[Stage.WORK]
        assert "Do NOT add unrequested scope" in text


class TestGetStageInstructions:
    def test_valid_stage(self):
        text = get_stage_instructions("conversation")
        assert "CONVERSATION" in text
        assert len(text) > 100

    def test_work_stage(self):
        text = get_stage_instructions("work")
        assert "WORK" in text

    def test_unknown_stage(self):
        assert get_stage_instructions("nonexistent") == ""

    def test_empty_stage(self):
        assert get_stage_instructions("") == ""


class TestGetStageSummary:
    def test_conversation(self):
        s = get_stage_summary("conversation")
        assert "PO" in s
        assert "code" in s.lower()

    def test_work(self):
        s = get_stage_summary("work")
        assert "plan" in s.lower()

    def test_unknown(self):
        s = get_stage_summary("unknown_stage")
        assert "unknown_stage" in s