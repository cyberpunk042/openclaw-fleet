"""Tests for fleet.core.methodology — methodology stage progression."""

import pytest
from fleet.core.methodology import (
    Stage,
    STAGE_ORDER,
    get_required_stages,
    get_next_stage,
    get_initial_stage,
    check_conversation_stage,
    check_analysis_stage,
    check_investigation_stage,
    check_reasoning_stage,
    check_work_stage,
    suggest_readiness_for_stage,
    snap_readiness,
)


class TestStageOrder:
    def test_five_stages(self):
        assert len(STAGE_ORDER) == 5

    def test_conversation_first(self):
        assert STAGE_ORDER[0] == Stage.CONVERSATION

    def test_work_last(self):
        assert STAGE_ORDER[-1] == Stage.WORK


class TestGetRequiredStages:
    def test_epic_all_stages(self):
        stages = get_required_stages("epic")
        assert len(stages) == 5
        assert stages[0] == Stage.CONVERSATION
        assert stages[-1] == Stage.WORK

    def test_task_minimal(self):
        stages = get_required_stages("task")
        assert stages == [Stage.REASONING, Stage.WORK]

    def test_bug_starts_at_analysis(self):
        stages = get_required_stages("bug")
        assert stages[0] == Stage.ANALYSIS

    def test_spike_no_work(self):
        stages = get_required_stages("spike")
        assert Stage.WORK not in stages

    def test_unknown_type_defaults(self):
        stages = get_required_stages("unknown")
        assert stages == [Stage.REASONING, Stage.WORK]

    def test_override(self):
        stages = get_required_stages("epic", override=["analysis", "work"])
        assert stages == [Stage.ANALYSIS, Stage.WORK]


class TestGetNextStage:
    def test_conversation_to_analysis(self):
        required = get_required_stages("epic")
        assert get_next_stage("conversation", required) == Stage.ANALYSIS

    def test_reasoning_to_work(self):
        required = get_required_stages("task")
        assert get_next_stage("reasoning", required) == Stage.WORK

    def test_last_stage_returns_none(self):
        required = get_required_stages("task")
        assert get_next_stage("work", required) is None

    def test_skipped_stage_finds_next(self):
        # Story skips analysis and investigation
        required = get_required_stages("story")
        assert get_next_stage("conversation", required) == Stage.REASONING

    def test_invalid_stage(self):
        required = get_required_stages("task")
        result = get_next_stage("invalid", required)
        assert result == Stage.REASONING  # first required stage


class TestGetInitialStage:
    def test_new_epic_starts_at_conversation(self):
        assert get_initial_stage("epic") == Stage.CONVERSATION

    def test_new_task_starts_at_reasoning(self):
        assert get_initial_stage("task") == Stage.REASONING

    def test_high_readiness_skips_to_reasoning(self):
        stage = get_initial_stage("epic", has_verbatim_requirement=True, readiness=90)
        assert stage == Stage.REASONING

    def test_very_high_readiness_skips_to_work(self):
        stage = get_initial_stage("epic", has_verbatim_requirement=True, readiness=99)
        assert stage == Stage.WORK

    def test_medium_readiness_skips_conversation(self):
        stage = get_initial_stage("epic", has_verbatim_requirement=True, readiness=50)
        assert stage == Stage.ANALYSIS  # first non-conversation stage

    def test_no_verbatim_starts_at_beginning(self):
        stage = get_initial_stage("epic", has_verbatim_requirement=False, readiness=90)
        assert stage == Stage.CONVERSATION  # no shortcut without verbatim


class TestConversationChecks:
    def test_all_passed(self):
        result = check_conversation_stage(
            has_verbatim_requirement=True,
            has_po_response=True,
            open_questions=0,
        )
        assert result.can_advance
        assert result.all_passed
        assert result.passed_count == 3

    def test_missing_verbatim(self):
        result = check_conversation_stage(
            has_verbatim_requirement=False,
            has_po_response=True,
            open_questions=0,
        )
        assert not result.can_advance

    def test_open_questions(self):
        result = check_conversation_stage(
            has_verbatim_requirement=True,
            has_po_response=True,
            open_questions=2,
        )
        assert not result.can_advance


class TestAnalysisChecks:
    def test_complete(self):
        result = check_analysis_stage(
            has_analysis_document=True,
            po_reviewed=True,
        )
        assert result.can_advance

    def test_no_document(self):
        result = check_analysis_stage(
            has_analysis_document=False,
            po_reviewed=True,
        )
        assert not result.can_advance


class TestInvestigationChecks:
    def test_complete(self):
        result = check_investigation_stage(
            has_research_document=True,
            multiple_options_explored=True,
            po_reviewed=True,
        )
        assert result.can_advance

    def test_single_option(self):
        result = check_investigation_stage(
            has_research_document=True,
            multiple_options_explored=False,
            po_reviewed=True,
        )
        assert not result.can_advance


class TestReasoningChecks:
    def test_complete(self):
        result = check_reasoning_stage(
            has_plan=True,
            plan_references_verbatim=True,
            plan_specifies_files=True,
            po_confirmed_plan=True,
        )
        assert result.can_advance

    def test_plan_no_verbatim_reference(self):
        result = check_reasoning_stage(
            has_plan=True,
            plan_references_verbatim=False,
            plan_specifies_files=True,
            po_confirmed_plan=True,
        )
        assert not result.can_advance

    def test_po_not_confirmed(self):
        result = check_reasoning_stage(
            has_plan=True,
            plan_references_verbatim=True,
            plan_specifies_files=True,
            po_confirmed_plan=False,
        )
        assert not result.can_advance


class TestWorkChecks:
    def test_complete(self):
        result = check_work_stage(
            readiness=99,
            has_commits=True,
            has_pr=True,
            acceptance_criteria_met=True,
            required_tools_called=True,
        )
        assert result.can_advance

    def test_low_readiness(self):
        result = check_work_stage(
            readiness=80,
            has_commits=True,
            has_pr=True,
            acceptance_criteria_met=True,
            required_tools_called=True,
        )
        assert not result.can_advance

    def test_no_pr(self):
        result = check_work_stage(
            readiness=99,
            has_commits=True,
            has_pr=False,
            acceptance_criteria_met=True,
            required_tools_called=True,
        )
        assert not result.can_advance


class TestReadiness:
    def test_suggest_conversation(self):
        assert suggest_readiness_for_stage(Stage.CONVERSATION) == 10

    def test_suggest_investigation(self):
        assert suggest_readiness_for_stage(Stage.INVESTIGATION) == 50

    def test_suggest_work(self):
        assert suggest_readiness_for_stage(Stage.WORK) == 99

    def test_snap_exact(self):
        assert snap_readiness(50) == 50

    def test_snap_close(self):
        assert snap_readiness(47) == 50

    def test_snap_low(self):
        assert snap_readiness(3) == 5

    def test_snap_high(self):
        assert snap_readiness(97) == 95