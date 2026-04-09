"""End-to-end pipeline test — traces a task through every system.

Verifies that when a task is assigned to an agent:
  - Model selection gives stage-aware effort
  - Contribution completeness checks against synergy matrix
  - Skill recommendations return real skills for the agent's stage
  - Standing orders exist for the agent
  - TOOLS.md exists with expected sections
  - Heartbeat template exists
  - All recommended skills are real directories with SKILL.md

This is THE integration test that proves the full pipeline is coherent.
"""

from pathlib import Path

import pytest

from fleet.core.contributions import check_contribution_completeness
from fleet.core.model_selection import select_model_for_task, _EFFORT_ORDER
from fleet.core.skill_recommendations import get_skill_recommendations
from fleet.core.standing_orders import get_standing_orders

from .conftest import make_task

FLEET_DIR = Path(__file__).resolve().parent.parent.parent.parent
AGENTS_DIR = FLEET_DIR / "agents"
SKILLS_DIR = FLEET_DIR / ".claude" / "skills"
HEARTBEAT_DIR = FLEET_DIR / "agents" / "_template" / "heartbeats"

AGENT_ROSTER = [
    "architect", "software-engineer", "qa-engineer", "devops",
    "devsecops-expert", "fleet-ops", "project-manager",
    "technical-writer", "ux-designer", "accountability-generator",
]


class TestEndToEndTaskPipeline:
    """Trace a story task through the complete pipeline for each agent."""

    @pytest.mark.parametrize("agent", AGENT_ROSTER)
    def test_model_selection_stage_aware(self, agent):
        """Model selection should produce stage-aware effort for reasoning stage."""
        task = make_task(story_points=3, task_type="story", task_stage="reasoning")
        config = select_model_for_task(task, agent)
        # Reasoning stage floor is 'high' — should be at least high
        assert _EFFORT_ORDER[config.effort] >= _EFFORT_ORDER["high"], \
            f"{agent}: reasoning stage should get >= high effort, got {config.effort}"

    @pytest.mark.parametrize("agent", AGENT_ROSTER)
    def test_skill_recommendations_return_real_skills(self, agent):
        """Every workspace-sourced skill recommended by the pipeline should exist."""
        # Gateway skills (fleet-urls, fleet-gap, fleet-report, fleet-comment, fleet-memory,
        # fleet-alert, fleet-commit, fleet-pr, fleet-task-create, fleet-task-update)
        # are provided by the gateway, not as workspace SKILL.md files.
        gateway_skills = {
            "fleet-urls", "fleet-gap", "fleet-report", "fleet-comment",
            "fleet-memory", "fleet-alert", "fleet-commit", "fleet-pr",
            "fleet-task-create", "fleet-task-update",
        }
        for stage in ["conversation", "analysis", "investigation", "reasoning", "work"]:
            recs = get_skill_recommendations(agent, stage)
            for entry in recs.get("always", []) + recs.get("stage", []):
                skill_name = entry["skill"] if isinstance(entry, dict) else entry
                # Only check workspace fleet- skills (not gateway or plugin skills)
                if skill_name.startswith("fleet-") and skill_name not in gateway_skills:
                    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
                    assert skill_path.exists(), \
                        f"{agent} at {stage}: recommended skill '{skill_name}' has no SKILL.md"

    @pytest.mark.parametrize("agent", AGENT_ROSTER)
    def test_tools_md_has_focused_sections(self, agent):
        """TOOLS.md should have focused sections: Your Tools, Available, Boundaries."""
        tools_md = AGENTS_DIR / agent / "TOOLS.md"
        assert tools_md.exists(), f"{agent}/TOOLS.md not found"
        content = tools_md.read_text()
        assert "## Your Tools" in content, f"{agent}: missing Your Tools section"
        assert "## Available" in content, f"{agent}: missing Available section"
        assert "## Boundaries" in content, f"{agent}: missing Boundaries section"

    @pytest.mark.parametrize("agent", AGENT_ROSTER)
    def test_heartbeat_template_exists(self, agent):
        """Every agent should have a role-specific heartbeat template."""
        hb = HEARTBEAT_DIR / f"{agent}.md"
        assert hb.exists(), f"No heartbeat template for {agent}"

    @pytest.mark.parametrize("agent", AGENT_ROSTER)
    def test_standing_orders_have_structure(self, agent):
        """Standing orders should have authority_level and escalation_threshold."""
        orders = get_standing_orders(agent)
        assert "authority_level" in orders
        assert "escalation_threshold" in orders
        assert orders["escalation_threshold"] > 0

    def test_contribution_flow_for_engineer_story(self):
        """An engineer story should require contributions from architect and QA."""
        status = check_contribution_completeness(
            task_id="T-END2END",
            target_agent="software-engineer",
            task_type="story",
            received_types=[],
        )
        assert not status.all_received, "Story should need contributions"
        assert "design_input" in status.required, "Engineer story needs design_input"
        assert "qa_test_definition" in status.required, "Engineer story needs qa_test_definition"

    def test_contribution_flow_complete_when_all_received(self):
        """When all required contributions are received, status should be complete."""
        # Get required types
        status_empty = check_contribution_completeness(
            task_id="T-END2END",
            target_agent="software-engineer",
            task_type="story",
            received_types=[],
        )
        # Provide all required
        status_full = check_contribution_completeness(
            task_id="T-END2END",
            target_agent="software-engineer",
            task_type="story",
            received_types=status_empty.required,
        )
        assert status_full.all_received
        assert status_full.completeness_pct == 100.0

    def test_work_stage_lower_effort_than_reasoning(self):
        """Work stage should not inflate effort above reasoning."""
        task_work = make_task(story_points=1, task_type="subtask", task_stage="work")
        task_reasoning = make_task(story_points=1, task_type="subtask", task_stage="reasoning")
        config_work = select_model_for_task(task_work, "software-engineer")
        config_reasoning = select_model_for_task(task_reasoning, "software-engineer")
        assert _EFFORT_ORDER[config_work.effort] <= _EFFORT_ORDER[config_reasoning.effort]

    def test_total_skill_count_matches_filesystem(self):
        """The number of fleet-* skill directories should match what we expect."""
        skill_dirs = list(SKILLS_DIR.glob("fleet-*/SKILL.md"))
        assert len(skill_dirs) >= 78, f"Expected >= 78 skills, found {len(skill_dirs)}"


class TestToolsMdContentAccuracy:
    """Verify TOOLS.md contains role-appropriate tools and group calls."""

    # Each role's group call prefixes that MUST appear in their TOOLS.md
    ROLE_GROUP_CALL_PREFIXES = {
        "project-manager": ["pm_"],
        "fleet-ops": ["ops_"],
        "architect": ["arch_"],
        "devsecops-expert": ["sec_"],
        "software-engineer": ["eng_"],
        "devops": ["devops_"],
        "qa-engineer": ["qa_"],
        "technical-writer": ["writer_"],
        "ux-designer": ["ux_"],
        "accountability-generator": ["acct_"],
    }

    @pytest.mark.parametrize("agent", AGENT_ROSTER)
    def test_tools_md_contains_role_group_calls(self, agent):
        """TOOLS.md should contain the agent's role-specific group calls."""
        tools_md = AGENTS_DIR / agent / "TOOLS.md"
        assert tools_md.exists()
        content = tools_md.read_text()
        prefixes = self.ROLE_GROUP_CALL_PREFIXES.get(agent, [])
        for prefix in prefixes:
            assert prefix in content, \
                f"{agent}/TOOLS.md missing group calls with prefix '{prefix}'"

    @pytest.mark.parametrize("agent", AGENT_ROSTER)
    def test_tools_md_has_chain_awareness(self, agent):
        """TOOLS.md tools should show chain awareness (→ arrow notation)."""
        tools_md = AGENTS_DIR / agent / "TOOLS.md"
        assert tools_md.exists()
        content = tools_md.read_text()
        # At least some tools should have chain indicators
        assert "**→**" in content, \
            f"{agent}/TOOLS.md missing chain awareness (no **→** entries)"

    @pytest.mark.parametrize("agent", AGENT_ROSTER)
    def test_tools_md_no_bloat(self, agent):
        """TOOLS.md should be focused — no skills catalog, no hooks, no CRONs."""
        tools_md = AGENTS_DIR / agent / "TOOLS.md"
        assert tools_md.exists()
        content = tools_md.read_text()
        # These sections were intentionally removed in the redesign
        assert "## Skills" not in content, \
            f"{agent}/TOOLS.md still has Skills section (should be in Navigator)"
        assert "## Hooks" not in content, \
            f"{agent}/TOOLS.md still has Hooks section (removed — hooks self-teach)"
        assert "## Scheduled Operations" not in content, \
            f"{agent}/TOOLS.md still has CRONs section (removed — CRONs run in isolated sessions)"
