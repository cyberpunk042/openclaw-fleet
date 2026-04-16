"""Tests for fleet.core.tier_renderer — TierRenderer and tier profile loading."""

import pytest
from fleet.core.tier_renderer import TierRenderer, load_tier_rules
from fleet.core.models import Task, TaskCustomFields, TaskStatus


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _make_task(**kwargs) -> Task:
    defaults = {
        "id": "task-abcdef12",
        "board_id": "board-1",
        "title": "Design the new header component",
        "status": TaskStatus.IN_PROGRESS,
        "description": "Add FleetControlBar to DashboardShell",
        "priority": "high",
        "custom_fields": TaskCustomFields(
            task_readiness=80,
            task_stage="reasoning",
            requirement_verbatim="Add three Select dropdowns to the DashboardShell header bar",
            project="fleet",
        ),
    }
    defaults.update(kwargs)
    return Task(**defaults)


# ─── TestTierProfileLoading ───────────────────────────────────────────────────


class TestTierProfileLoading:
    def test_load_expert_profile(self):
        rules = load_tier_rules("expert")
        assert rules["task_detail"] == "full"

    def test_load_capable_profile(self):
        rules = load_tier_rules("capable")
        assert rules["task_detail"] == "core_fields"

    def test_load_lightweight_profile(self):
        rules = load_tier_rules("lightweight")
        assert rules["chain_awareness"] == "omit"

    def test_flagship_extends_capable(self):
        """flagship_local extends capable — overrides applied on top of base."""
        capable = load_tier_rules("capable")
        flagship = load_tier_rules("flagship_local")
        # Inherits base capable values
        assert flagship["task_detail"] == capable["task_detail"]
        assert flagship["messages"] == capable["messages"]
        # Overrides
        assert flagship["contributions"] == "summary"
        assert flagship["role_data"] == "counts_plus_top5"
        assert flagship["events_limit"] == 8
        # Not equal to capable's overridden values
        assert flagship["events_limit"] != capable["events_limit"]

    def test_unknown_tier_defaults_to_expert(self):
        """Unknown tier name falls back to expert rules."""
        expert = load_tier_rules("expert")
        unknown = load_tier_rules("totally_unknown_tier_xyz")
        assert unknown["task_detail"] == expert["task_detail"]
        assert unknown["role_data"] == expert["role_data"]

    def test_description_stripped(self):
        """description key must NOT appear in returned rules."""
        for tier in ("expert", "capable", "flagship_local", "lightweight"):
            rules = load_tier_rules(tier)
            assert "description" not in rules


# ─── TestFormatRoleData ───────────────────────────────────────────────────────


class TestFormatRoleData:
    def test_fleet_ops_no_raw_dicts(self):
        """Output must NOT contain raw dict repr — must have formatted lines."""
        renderer = TierRenderer("expert")
        data = {
            "pending_approvals": 2,
            "approval_details": [
                {"id": "apr-001", "task_id": "task-abc", "status": "pending"},
                {"id": "apr-002", "task_id": "task-def", "status": "pending"},
            ],
            "review_queue": [
                {"id": "task-111", "title": "Review header PR", "agent": "architect"},
            ],
            "offline_agents": ["devops", "qa-engineer"],
        }
        result = renderer.format_role_data("fleet-ops", data)
        # Must NOT contain raw dict repr
        assert "{'id'" not in result
        assert "{'task_id'" not in result
        # Must have formatted lines
        assert "## ROLE DATA" in result
        assert "apr-001" in result
        assert "task-abc" in result
        assert "pending" in result
        assert "Review header PR" in result
        assert "architect" in result
        assert "devops" in result

    def test_pm_no_raw_dicts(self):
        """PM role data: formatted task list, priorities visible."""
        renderer = TierRenderer("expert")
        data = {
            "unassigned_tasks": 3,
            "unassigned_details": [
                {"id": "task-aaa", "title": "Build login page", "priority": "high"},
                {"id": "task-bbb", "title": "Fix auth bug", "priority": "critical"},
            ],
            "blocked_tasks": 1,
            "progress": "5/15 done",
        }
        result = renderer.format_role_data("project-manager", data)
        assert "{'id'" not in result
        assert "## ROLE DATA" in result
        assert "task-aaa" in result
        assert "Build login page" in result
        assert "high" in result
        assert "critical" in result
        assert "5/15 done" in result

    def test_worker_contributions_formatted(self):
        """Worker contributions_received shown as 'type (from, status)' not raw dict."""
        renderer = TierRenderer("expert")
        data = {
            "my_tasks_count": 2,
            "contributions_received": [
                {"type": "qa_test_definition", "from": "qa-engineer", "status": "ready"},
                {"type": "design_input", "from": "architect", "status": "pending"},
            ],
        }
        result = renderer.format_role_data("software-engineer", data)
        assert "{'type'" not in result
        assert "## ROLE DATA" in result
        # Must show type (from, status) format
        assert "qa_test_definition (qa-engineer, ready)" in result
        assert "design_input (architect, pending)" in result

    def test_worker_contributions_received_dict_shape(self):
        """Worker contributions_received as dict keyed by task ID (real provider shape)."""
        renderer = TierRenderer("expert")
        data = {
            "my_tasks_count": 1,
            "contributions_received": {
                "task-a1b": [
                    {"type": "design_input", "from": "architect", "status": "done"},
                    {"type": "qa_test_definition", "from": "qa-engineer", "status": "done"},
                ]
            },
        }
        result = renderer.format_role_data("software-engineer", data)
        assert "{'type'" not in result
        assert "task-a1b" in result
        assert "design_input" in result
        assert "architect" in result
        assert "qa_test_definition" in result
        assert "qa-engineer" in result

    def test_lightweight_counts_only(self):
        """Lightweight tier: counts shown, no item detail lines."""
        renderer = TierRenderer("lightweight")
        data = {
            "pending_approvals": 4,
            "approval_details": [
                {"id": "apr-001", "task_id": "task-abc", "status": "pending"},
                {"id": "apr-002", "task_id": "task-def", "status": "pending"},
            ],
            "review_queue": [
                {"id": "task-111", "title": "Review header PR", "agent": "architect"},
            ],
        }
        result = renderer.format_role_data("fleet-ops", data)
        assert "## ROLE DATA" in result
        assert "4" in result  # count present
        # No item detail lines (no individual approval IDs)
        assert "apr-001" not in result
        assert "apr-002" not in result
        assert "Review header PR" not in result

    def test_empty_data_returns_empty(self):
        """Empty data dict returns empty string."""
        renderer = TierRenderer("expert")
        result = renderer.format_role_data("fleet-ops", {})
        assert result == ""


# ─── TestFormatRejectionContext ───────────────────────────────────────────────


class TestFormatRejectionContext:
    def test_iteration_1_empty(self):
        """Iteration 1 (first attempt) returns empty string."""
        renderer = TierRenderer("expert")
        result = renderer.format_rejection_context(1, "some feedback")
        assert result == ""

    def test_iteration_2_shows_feedback(self):
        """Iteration 2: shows iteration number, feedback, eng_fix_task_response."""
        renderer = TierRenderer("expert")
        feedback = "The implementation misses edge case handling for empty inputs."
        result = renderer.format_rejection_context(2, feedback)
        assert "iteration 2" in result
        assert "eng_fix_task_response" in result
        assert feedback in result
        assert "ROOT CAUSE" in result

    def test_iteration_3_shows_warning(self):
        """Iteration 3+: shows WARNING about escalation."""
        renderer = TierRenderer("expert")
        result = renderer.format_rejection_context(3, "Still failing tests.")
        assert "WARNING" in result
        assert "escalated" in result.lower() or "escalation" in result.lower()
        assert "3" in result


# ─── TestFormatActionDirective ────────────────────────────────────────────────


class TestFormatActionDirective:
    def test_work_progress_0(self):
        """Progress 0 in work stage mentions fleet_task_accept."""
        renderer = TierRenderer("expert")
        result = renderer.format_action_directive("work", 0, 1)
        assert "fleet_task_accept" in result

    def test_work_progress_70(self):
        """Progress 70 in work stage mentions test/testing."""
        renderer = TierRenderer("expert")
        result = renderer.format_action_directive("work", 70, 1)
        assert "test" in result.lower()

    def test_work_progress_90(self):
        """Progress 90 in work stage mentions fleet_task_complete."""
        renderer = TierRenderer("expert")
        result = renderer.format_action_directive("work", 90, 1)
        assert "fleet_task_complete" in result

    def test_work_rework(self):
        """Iteration >= 2 in work stage mentions REWORK and eng_fix_task_response."""
        renderer = TierRenderer("expert")
        result = renderer.format_action_directive("work", 50, 2)
        assert "REWORK" in result
        assert "eng_fix_task_response" in result

    def test_conversation_stage(self):
        """Conversation stage directive mentions clarifying questions."""
        renderer = TierRenderer("expert")
        result = renderer.format_action_directive("conversation", 0, 1)
        assert "clarif" in result.lower() or "question" in result.lower()

    def test_reasoning_stage(self):
        """Reasoning stage directive mentions plan."""
        renderer = TierRenderer("expert")
        result = renderer.format_action_directive("reasoning", 0, 1)
        assert "plan" in result.lower()

    def test_one_line_depth_returns_single_sentence(self):
        """one_line depth returns just the first sentence (no backtick tool names)."""
        renderer = TierRenderer("lightweight")
        result = renderer.format_action_directive("work", 0, 1)
        # Should be short — one sentence only
        assert len(result) < 100
        # Should still indicate starting work
        assert "work" in result.lower() or "start" in result.lower()


# ─── TestFormatContributionTaskContext ────────────────────────────────────────


class TestFormatContributionTaskContext:
    def test_no_contribution_type_empty(self):
        """No contribution_type → returns empty string."""
        renderer = TierRenderer("expert")
        result = renderer.format_contribution_task_context("", "task-abcdef12")
        assert result == ""

    def test_contribution_with_target(self):
        """With target task: shows title, verbatim, fleet_contribute."""
        renderer = TierRenderer("expert")
        target = _make_task(
            id="task-target1",
            title="Implement dashboard header",
            custom_fields=TaskCustomFields(
                requirement_verbatim="Add three Select dropdowns to the DashboardShell header bar",
                delivery_phase="mvp",
                task_stage="work",
            ),
        )
        result = renderer.format_contribution_task_context(
            "qa_test_definition", "task-target1", target
        )
        assert "## CONTRIBUTION TASK" in result
        assert "qa_test_definition" in result
        assert "Implement dashboard header" in result
        assert "Select dropdowns" in result
        assert "mvp" in result
        assert "fleet_contribute" in result

    def test_contribution_without_target_task(self):
        """Without target Task object: shows type, short target ID, fleet_contribute."""
        renderer = TierRenderer("expert")
        result = renderer.format_contribution_task_context(
            "design_input", "task-12345678", None
        )
        assert "## CONTRIBUTION TASK" in result
        assert "design_input" in result
        assert "task-123" in result  # short ID (first 8 chars)
        assert "fleet_contribute" in result


# ─── TestFormatStageProtocol ──────────────────────────────────────────────────


class TestFormatStageProtocol:
    def test_reasoning_engineer_says_implementation(self):
        """Reasoning stage for software-engineer mentions 'implementation plan'."""
        renderer = TierRenderer("expert")
        result = renderer.format_stage_protocol("reasoning", "software-engineer")
        assert "implementation plan" in result.lower()

    def test_reasoning_architect_says_design_input(self):
        """Reasoning stage for architect mentions design_input."""
        renderer = TierRenderer("expert")
        result = renderer.format_stage_protocol("reasoning", "architect")
        assert "design_input" in result

    def test_reasoning_qa_says_test_criteria(self):
        """Reasoning stage for qa-engineer mentions qa_test_definition or test criteria."""
        renderer = TierRenderer("expert")
        result = renderer.format_stage_protocol("reasoning", "qa-engineer")
        assert "qa_test_definition" in result or "test criteria" in result.lower()

    def test_work_stage_not_role_specific(self):
        """Work stage protocol is the same for all roles and contains 'WORK'."""
        renderer = TierRenderer("expert")
        result_eng = renderer.format_stage_protocol("work", "software-engineer")
        result_arch = renderer.format_stage_protocol("work", "architect")
        assert result_eng == result_arch
        assert "WORK" in result_eng

    def test_work_rework_adapts_protocol(self):
        """BUG-03: Work protocol adapts for rework — no 'Execute the confirmed plan'."""
        renderer = TierRenderer("expert")
        result = renderer.format_stage_protocol("work", "software-engineer", iteration=2)
        assert "ROOT CAUSE" in result
        assert "rejection feedback" in result.lower()
        # Should NOT say "Execute the confirmed plan"
        assert "Execute the confirmed plan" not in result


# ─── TestTrimProtocolForTier ─────────────────────────────────────────────────


class TestTrimProtocolForTier:
    def test_must_must_not_on_analysis(self):
        """Capable tier on analysis: strips CAN and How to advance, keeps MUST/MUST NOT."""
        renderer = TierRenderer("capable")
        result = renderer.format_stage_protocol("analysis", "software-engineer")
        assert "MUST do" in result or "MUST:" in result
        assert "MUST NOT" in result
        assert "What you CAN" not in result
        assert "How to advance" not in result

    def test_must_must_not_on_work(self):
        """Capable tier on work: returned unchanged (work has no CAN/advance sections)."""
        expert = TierRenderer("expert")
        capable = TierRenderer("capable")
        expert_result = expert.format_stage_protocol("work", "software-engineer")
        capable_result = capable.format_stage_protocol("work", "software-engineer")
        # Work protocol has no CAN/advance to strip, so must_must_not = full
        assert "MUST:" in capable_result
        assert "MUST NOT:" in capable_result

    def test_short_rules_on_reasoning(self):
        """Lightweight tier on reasoning: condenses to MUST/MUST NOT lines."""
        renderer = TierRenderer("lightweight")
        result = renderer.format_stage_protocol("reasoning", "software-engineer")
        assert result.startswith("MUST:")
        # Should be compact — no ### headers, no full paragraphs
        assert "###" not in result
        line_count = len([l for l in result.split("\n") if l.strip()])
        assert line_count <= 4

    def test_short_rules_on_work(self):
        """Lightweight tier on work: extracts MUST/MUST NOT from ### MUST: format."""
        renderer = TierRenderer("lightweight")
        result = renderer.format_stage_protocol("work", "software-engineer")
        assert "MUST:" in result
        assert "###" not in result


# ─── TestProtocolAdaptations ─────────────────────────────────────────────────


class TestProtocolAdaptations:
    def test_contribution_replaces_po_references(self):
        """is_contribution=True replaces PO review language with contribution language."""
        renderer = TierRenderer("expert")
        result = renderer.format_stage_protocol(
            "reasoning", "architect", is_contribution=True,
        )
        assert "fleet_contribute" in result
        # Should NOT reference PO confirmation for contributions
        assert "PO confirmed the plan" not in result

    def test_model_protocol_adaptation_inserted(self):
        """Config-driven protocol_adaptation from contribution model is inserted."""
        renderer = TierRenderer("expert")
        result = renderer.format_stage_protocol(
            "analysis", "architect", model_name="contribution",
        )
        assert "TARGET TASK" in result


# ─── TestFormatRoleDataExtended ──────────────────────────────────────────────


class TestFormatRoleDataExtended:
    def test_architect_role_data(self):
        """Architect data: design_tasks and high_complexity formatted."""
        renderer = TierRenderer("expert")
        data = {
            "design_tasks": [
                {"id": "task-d1", "title": "Design auth module", "stage": "reasoning"},
                {"id": "task-d2", "title": "Design cache layer", "stage": "analysis"},
            ],
            "high_complexity": [
                {"id": "task-hc1", "title": "Migrate database schema"},
            ],
        }
        result = renderer.format_role_data("architect", data)
        assert "## ROLE DATA" in result
        assert "Design auth module" in result
        assert "reasoning" in result
        assert "Migrate database schema" in result
        assert "{'id'" not in result

    def test_devsecops_role_data(self):
        """DevSecOps data: security_tasks and PRs needing review formatted."""
        renderer = TierRenderer("expert")
        data = {
            "security_tasks": [
                {"id": "task-s1", "title": "Audit auth middleware"},
            ],
            "prs_needing_security_review": [
                {"id": "task-pr1", "title": "Add API endpoint", "pr": "https://github.com/org/repo/pull/99"},
            ],
        }
        result = renderer.format_role_data("devsecops-expert", data)
        assert "## ROLE DATA" in result
        assert "Audit auth middleware" in result
        assert "https://github.com/org/repo/pull/99" in result
        assert "{'id'" not in result

    def test_capable_tier_counts_plus_top3(self):
        """Capable tier: counts shown, max 3 items listed."""
        renderer = TierRenderer("capable")
        data = {
            "pending_approvals": 5,
            "approval_details": [
                {"id": f"apr-{i}", "task_id": f"task-{i}", "status": "pending"}
                for i in range(5)
            ],
            "review_queue": [],
        }
        result = renderer.format_role_data("fleet-ops", data)
        assert "5" in result
        # Should show at most 3 items
        assert "apr-0" in result
        assert "apr-2" in result
        assert "apr-3" not in result

    def test_flagship_tier_counts_plus_top5(self):
        """Flagship tier: counts shown, max 5 items listed."""
        renderer = TierRenderer("flagship_local")
        data = {
            "unassigned_tasks": 7,
            "unassigned_details": [
                {"id": f"task-u{i}", "title": f"Task {i}", "priority": "medium"}
                for i in range(7)
            ],
            "blocked_tasks": 0,
            "progress": "0/7",
            "inbox_count": 7,
        }
        result = renderer.format_role_data("project-manager", data)
        assert "7" in result
        assert "task-u0" in result
        assert "task-u4" in result
        assert "task-u5" not in result


# ─── TestActionDirectiveEdge ─────────────────────────────────────────────────


class TestActionDirectiveEdge:
    def test_one_line_with_contributions_missing(self):
        """Lightweight tier: BLOCKED with missing contributions returns short line."""
        renderer = TierRenderer("lightweight")
        result = renderer.format_action_directive(
            "work", 0, 1, contributions_missing=["design_input", "qa_test_definition"],
        )
        assert "BLOCKED" in result
        assert "design_input" in result
        assert len(result) < 120


# ─── TestSourceStringIntegrity ───────────────────────────────────────────────


class TestSourceStringIntegrity:
    def test_contribution_replacement_strings_exist_in_config(self):
        """Verify the 4 strings used in is_contribution replacements exist in methodology.yaml."""
        from fleet.core.stage_context import get_stage_instructions
        # These strings are replaced by format_stage_protocol when is_contribution=True
        # If methodology.yaml changes, these replacements silently stop matching
        targets = [
            ("analysis", "Present findings to the PO via task comments"),
            ("reasoning", "Present the plan to the PO for confirmation"),
            ("analysis", "PO reviewed the findings"),
            ("reasoning", "PO confirmed the plan"),
        ]
        for stage, expected_string in targets:
            protocol = get_stage_instructions(stage)
            assert expected_string in protocol, (
                f"String '{expected_string}' not found in {stage} protocol. "
                f"Contribution replacements in tier_renderer.py will silently fail."
            )
