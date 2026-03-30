"""Integration tests — all diseases detected + all lessons adapted.

Verifies every disease in the catalogue can be detected and every
lesson template produces a valid adapted lesson with exercise.
"""

import pytest
from fleet.core.teaching import (
    DiseaseCategory,
    TEMPLATES,
    adapt_lesson,
    format_lesson_for_injection,
    evaluate_response,
    LessonOutcome,
)
from fleet.core.doctor import (
    detect_protocol_violation,
    detect_laziness,
    detect_stuck,
    detect_correction_threshold,
    Detection,
    AgentHealth,
    Severity,
    ResponseAction,
    decide_response,
)


# ═══ ALL DISEASE CATEGORIES HAVE LESSONS ══════════════════════════════


class TestAllDiseasesHaveLessons:
    """Every disease category that has a template produces valid lessons."""

    @pytest.mark.parametrize("disease", [
        DiseaseCategory.DEVIATION,
        DiseaseCategory.LAZINESS,
        DiseaseCategory.CONFIDENT_BUT_WRONG,
        DiseaseCategory.PROTOCOL_VIOLATION,
        DiseaseCategory.ABSTRACTION,
        DiseaseCategory.CODE_WITHOUT_READING,
        DiseaseCategory.SCOPE_CREEP,
        DiseaseCategory.COMPRESSION,
    ])
    def test_lesson_template_exists(self, disease):
        assert disease in TEMPLATES, f"No template for {disease.value}"

    @pytest.mark.parametrize("disease", [
        DiseaseCategory.DEVIATION,
        DiseaseCategory.LAZINESS,
        DiseaseCategory.CONFIDENT_BUT_WRONG,
        DiseaseCategory.PROTOCOL_VIOLATION,
        DiseaseCategory.ABSTRACTION,
        DiseaseCategory.CODE_WITHOUT_READING,
        DiseaseCategory.SCOPE_CREEP,
        DiseaseCategory.COMPRESSION,
    ])
    def test_lesson_adapts_with_context(self, disease):
        context = {
            "requirement_verbatim": "Add controls to header",
            "agent_plan": "Create sidebar page",
            "current_stage": "conversation",
            "allowed_actions": "discuss, ask, propose",
            "what_agent_did": "committed code",
            "what_agent_built": "sidebar page",
            "agent_interpretation": "I thought UI meant sidebar",
            "requirement_summary": "update all 7 call sites",
            "what_is_missing": "4 call sites not updated",
            "file_path": "DashboardShell.tsx",
            "function_name": "render()",
            "extra_work": "refactored variable names",
            "scope_description": "2000+ hour immune system",
            "what_agent_produced": "5 bullet points",
        }
        lesson = adapt_lesson(disease, "test-agent", "task-1", context)
        assert lesson.content, f"Empty lesson content for {disease.value}"
        assert lesson.exercise.instruction, f"Empty exercise for {disease.value}"
        assert lesson.exercise.verification_hint, f"Empty hint for {disease.value}"

    @pytest.mark.parametrize("disease", [
        DiseaseCategory.DEVIATION,
        DiseaseCategory.LAZINESS,
        DiseaseCategory.CONFIDENT_BUT_WRONG,
        DiseaseCategory.PROTOCOL_VIOLATION,
        DiseaseCategory.ABSTRACTION,
        DiseaseCategory.CODE_WITHOUT_READING,
        DiseaseCategory.SCOPE_CREEP,
        DiseaseCategory.COMPRESSION,
    ])
    def test_lesson_formats_for_injection(self, disease):
        lesson = adapt_lesson(disease, "agent", "t1", {
            "requirement_verbatim": "test req",
            "agent_plan": "test plan",
            "current_stage": "conversation",
            "allowed_actions": "discuss",
            "what_agent_did": "committed",
            "what_agent_built": "wrong thing",
            "agent_interpretation": "wrong",
            "requirement_summary": "do everything",
            "what_is_missing": "most of it",
            "file_path": "file.py",
            "function_name": "func()",
            "extra_work": "extra stuff",
            "scope_description": "big scope",
            "what_agent_produced": "small output",
        })
        text = format_lesson_for_injection(lesson)
        assert "TEACHING SYSTEM" in text
        assert "Exercise" in text
        assert "pruned" in text.lower()
        assert disease.value in text

    @pytest.mark.parametrize("disease", [
        DiseaseCategory.NOT_LISTENING,
        DiseaseCategory.CONTEXT_CONTAMINATION,
        DiseaseCategory.CASCADING_FIX,
    ])
    def test_diseases_without_templates_get_fallback(self, disease):
        """Diseases without specific templates get a generic lesson."""
        lesson = adapt_lesson(disease, "agent", "t1", {})
        assert lesson.content  # fallback content
        assert lesson.exercise.instruction  # fallback exercise


# ═══ ALL DETECTION PATTERNS ═══════════════════════════════════════════


class TestAllDetectionPatterns:
    """Every detection function produces valid Detection objects."""

    def test_protocol_violation_detected(self):
        d = detect_protocol_violation("agent", "t1", "conversation", ["fleet_commit"])
        assert d is not None
        assert d.disease == DiseaseCategory.PROTOCOL_VIOLATION
        assert d.severity in (Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL)
        assert d.signal
        assert d.agent_name == "agent"
        assert d.task_id == "t1"

    def test_laziness_fast_completion(self):
        d = detect_laziness("agent", "t1", story_points=5, time_to_complete_minutes=1)
        assert d is not None
        assert d.disease == DiseaseCategory.LAZINESS

    def test_laziness_partial_criteria(self):
        d = detect_laziness("agent", "t1", story_points=None, time_to_complete_minutes=None,
                           acceptance_criteria_total=10, acceptance_criteria_met=3)
        assert d is not None
        assert d.disease == DiseaseCategory.LAZINESS

    def test_stuck_detected(self):
        d = detect_stuck("agent", "t1", minutes_since_last_activity=120, has_commits=False)
        assert d is not None
        assert d.suggested_action == ResponseAction.FORCE_COMPACT

    def test_correction_threshold(self):
        d = detect_correction_threshold("agent", "t1", 3)
        assert d is not None
        assert d.disease == DiseaseCategory.CONFIDENT_BUT_WRONG
        assert d.suggested_action == ResponseAction.PRUNE


# ═══ RESPONSE DECISION MATRIX ════════════════════════════════════════


class TestResponseDecisionMatrix:
    """All severity × history combinations produce correct responses."""

    @pytest.mark.parametrize("severity,expected", [
        (Severity.LOW, ResponseAction.TRIGGER_TEACHING),
        (Severity.MEDIUM, ResponseAction.TRIGGER_TEACHING),
        (Severity.HIGH, ResponseAction.TRIGGER_TEACHING),  # first time
        (Severity.CRITICAL, ResponseAction.PRUNE),
    ])
    def test_first_time_responses(self, severity, expected):
        det = Detection("agent", "t1", DiseaseCategory.DEVIATION, severity, "test")
        health = AgentHealth(agent_name="agent")
        assert decide_response(det, health) == expected

    def test_repeat_offender_high_gets_pruned(self):
        det = Detection("agent", "t1", DiseaseCategory.DEVIATION, Severity.HIGH, "test")
        health = AgentHealth(agent_name="agent", total_lessons=2)
        assert decide_response(det, health) == ResponseAction.PRUNE

    def test_three_corrections_always_prunes(self):
        det = Detection("agent", "t1", DiseaseCategory.DEVIATION, Severity.LOW, "test")
        health = AgentHealth(agent_name="agent", correction_count=3)
        assert decide_response(det, health) == ResponseAction.PRUNE

    def test_in_lesson_no_action(self):
        det = Detection("agent", "t1", DiseaseCategory.DEVIATION, Severity.HIGH, "test")
        health = AgentHealth(agent_name="agent", is_in_lesson=True)
        assert decide_response(det, health) == ResponseAction.NONE

    def test_stuck_gets_compact(self):
        det = Detection("agent", "t1", DiseaseCategory.DEVIATION, Severity.LOW, "stuck",
                        suggested_action=ResponseAction.FORCE_COMPACT)
        health = AgentHealth(agent_name="agent")
        assert decide_response(det, health) == ResponseAction.FORCE_COMPACT


# ═══ LESSON EVALUATION ════════════════════════════════════════════════


class TestLessonEvaluation:
    """Comprehension evaluation works correctly."""

    def test_empty_response_fails(self):
        lesson = adapt_lesson(DiseaseCategory.DEVIATION, "a", "t", {
            "requirement_verbatim": "x", "agent_plan": "y"})
        assert evaluate_response(lesson, "") == LessonOutcome.NO_CHANGE

    def test_short_acknowledgment_fails(self):
        lesson = adapt_lesson(DiseaseCategory.DEVIATION, "a", "t", {
            "requirement_verbatim": "x", "agent_plan": "y"})
        assert evaluate_response(lesson, "I understand.") == LessonOutcome.NO_CHANGE

    def test_substantive_response_passes(self):
        lesson = adapt_lesson(DiseaseCategory.DEVIATION, "a", "t", {
            "requirement_verbatim": "x", "agent_plan": "y"})
        response = (
            "I see the mistake. The requirement says X but I was doing Y. "
            "I should have read the verbatim requirement more carefully instead "
            "of interpreting it my own way."
        )
        assert evaluate_response(lesson, response) == LessonOutcome.COMPREHENSION_VERIFIED