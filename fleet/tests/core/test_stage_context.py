"""Tests for fleet.core.stage_context — stage-aware protocol instructions."""

import pytest
from fleet.core.stage_context import (
    get_stage_instructions,
    get_stage_summary,
)
from fleet.core.methodology_config import get_methodology_config


class TestStageInstructions:
    def test_all_stages_have_instructions(self):
        cfg = get_methodology_config()
        for stage_def in cfg.stages:
            text = get_stage_instructions(stage_def.name)
            assert len(text) > 100, f"Stage {stage_def.name} has short/empty protocol"

    def test_conversation_prohibits_code(self):
        text = get_stage_instructions("conversation")
        assert "Do NOT write code" in text
        assert "Do NOT commit" in text
        assert "fleet_commit" in text

    def test_analysis_prohibits_solutions(self):
        text = get_stage_instructions("analysis")
        assert "Do NOT produce solutions" in text

    def test_investigation_prohibits_decisions(self):
        text = get_stage_instructions("investigation")
        assert "Do NOT decide" in text

    def test_reasoning_references_verbatim(self):
        text = get_stage_instructions("reasoning")
        assert "verbatim requirement" in text

    def test_work_has_core_tools(self):
        """Work protocol mentions commit and complete. fleet_read_context and
        fleet_task_accept are role-level instructions in CLAUDE.md, not stage protocol."""
        text = get_stage_instructions("work")
        assert "fleet_commit" in text
        assert "fleet_task_complete" in text

    def test_work_prohibits_scope_creep(self):
        text = get_stage_instructions("work")
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
