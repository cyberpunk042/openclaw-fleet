"""Tests for fleet.core.methodology_config — config-driven methodology."""

import pytest
from fleet.core.methodology_config import (
    load_methodology_config,
    get_methodology_config,
    MethodologyConfig,
    StageDefinition,
)


class TestConfigLoading:
    def test_loads_from_default_path(self):
        cfg = get_methodology_config()
        assert isinstance(cfg, MethodologyConfig)
        assert len(cfg.stages) >= 5

    def test_stages_ordered(self):
        cfg = get_methodology_config()
        names = cfg.stage_names()
        assert names[0] == "conversation"
        assert names[-1] == "work"

    def test_readiness_ranges_no_gaps(self):
        cfg = get_methodology_config()
        # Each stage's max should equal the next stage's min
        for i in range(len(cfg.stages) - 1):
            assert cfg.stages[i].readiness_max == cfg.stages[i + 1].readiness_min, (
                f"Gap between {cfg.stages[i].name} max={cfg.stages[i].readiness_max} "
                f"and {cfg.stages[i + 1].name} min={cfg.stages[i + 1].readiness_min}"
            )

    def test_first_stage_starts_at_zero(self):
        cfg = get_methodology_config()
        assert cfg.stages[0].readiness_min == 0

    def test_all_stages_have_protocol(self):
        cfg = get_methodology_config()
        for s in cfg.stages:
            assert len(s.protocol) > 50, f"Stage {s.name} has short/empty protocol"

    def test_all_stages_have_summary(self):
        cfg = get_methodology_config()
        for s in cfg.stages:
            assert len(s.summary) > 10, f"Stage {s.name} has short/empty summary"


class TestStageByName:
    def test_existing_stage(self):
        cfg = get_methodology_config()
        s = cfg.stage_by_name("conversation")
        assert s is not None
        assert s.name == "conversation"

    def test_unknown_stage(self):
        cfg = get_methodology_config()
        assert cfg.stage_by_name("nonexistent") is None


class TestStageForReadiness:
    def test_zero_readiness(self):
        cfg = get_methodology_config()
        s = cfg.stage_for_readiness(0)
        assert s.name == "conversation"

    def test_mid_readiness(self):
        cfg = get_methodology_config()
        s = cfg.stage_for_readiness(50)
        assert s.name == "investigation"

    def test_high_readiness(self):
        cfg = get_methodology_config()
        s = cfg.stage_for_readiness(90)
        assert s.name == "reasoning"

    def test_work_readiness(self):
        cfg = get_methodology_config()
        s = cfg.stage_for_readiness(99)
        assert s.name == "work"

    def test_full_readiness(self):
        cfg = get_methodology_config()
        s = cfg.stage_for_readiness(100)
        assert s.name == "work"

    def test_boundary_20(self):
        cfg = get_methodology_config()
        # 19 → conversation, 20 → analysis
        assert cfg.stage_for_readiness(19).name == "conversation"
        assert cfg.stage_for_readiness(20).name == "analysis"

    def test_boundary_50(self):
        cfg = get_methodology_config()
        assert cfg.stage_for_readiness(49).name == "analysis"
        assert cfg.stage_for_readiness(50).name == "investigation"


class TestTaskTypes:
    def test_epic_has_all_stages(self):
        cfg = get_methodology_config()
        stages = cfg.required_stage_names("epic")
        assert len(stages) == 5
        assert stages[0] == "conversation"
        assert stages[-1] == "work"

    def test_bug_skips_conversation(self):
        cfg = get_methodology_config()
        stages = cfg.required_stage_names("bug")
        assert "conversation" not in stages
        assert stages[0] == "analysis"

    def test_spike_no_work(self):
        cfg = get_methodology_config()
        stages = cfg.required_stage_names("spike")
        assert "work" not in stages

    def test_unknown_type_uses_default(self):
        cfg = get_methodology_config()
        stages = cfg.required_stage_names("unknown_type")
        assert stages == list(cfg.no_type_stages)

    def test_required_stages_in_order(self):
        """Required stages should be returned in stage definition order."""
        cfg = get_methodology_config()
        stage_names = cfg.stage_names()
        for tt in cfg.task_types.values():
            ordered = cfg.required_stage_names(tt.name)
            indices = [stage_names.index(s) for s in ordered]
            assert indices == sorted(indices), (
                f"Task type {tt.name} stages not in order: {ordered}"
            )


class TestToolBlocking:
    def test_commit_blocked_in_conversation(self):
        cfg = get_methodology_config()
        assert cfg.is_tool_blocked("conversation", "fleet_commit")

    def test_commit_allowed_in_analysis(self):
        cfg = get_methodology_config()
        assert not cfg.is_tool_blocked("analysis", "fleet_commit")

    def test_complete_blocked_everywhere_except_work(self):
        cfg = get_methodology_config()
        for s in cfg.stages:
            if s.name == "work":
                assert not cfg.is_tool_blocked("work", "fleet_task_complete")
            else:
                assert cfg.is_tool_blocked(s.name, "fleet_task_complete"), (
                    f"fleet_task_complete should be blocked in {s.name}"
                )

    def test_read_context_allowed_everywhere(self):
        cfg = get_methodology_config()
        for s in cfg.stages:
            assert not cfg.is_tool_blocked(s.name, "fleet_read_context")

    def test_unknown_stage_allows_all(self):
        cfg = get_methodology_config()
        assert not cfg.is_tool_blocked("nonexistent", "fleet_commit")


class TestVerbatimSkip:
    def test_rules_sorted_descending(self):
        cfg = get_methodology_config()
        thresholds = [r.threshold for r in cfg.verbatim_skip]
        assert thresholds == sorted(thresholds, reverse=True)

    def test_has_rules(self):
        cfg = get_methodology_config()
        assert len(cfg.verbatim_skip) >= 2


class TestValidReadiness:
    def test_includes_zero(self):
        cfg = get_methodology_config()
        assert 0 in cfg.valid_readiness

    def test_includes_100(self):
        cfg = get_methodology_config()
        assert 100 in cfg.valid_readiness

    def test_includes_99(self):
        cfg = get_methodology_config()
        assert 99 in cfg.valid_readiness

    def test_sorted(self):
        cfg = get_methodology_config()
        assert cfg.valid_readiness == sorted(cfg.valid_readiness)
