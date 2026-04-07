"""Tests for role-specific group calls.

Verifies each role's group calls register, accept inputs, return structured results.
Uses _run_role_tool helper that patches FleetMCPContext.from_env globally.
"""

from __future__ import annotations
import asyncio, os, sys
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MockCF:
    task_stage: str = "work"; task_readiness: int = 99
    requirement_verbatim: str = "Test requirement"; project: str = "fleet"
    branch: str = ""; pr_url: str = ""; agent_name: str = "software-engineer"
    story_points: int = 3; complexity: str = ""; task_type: str = "task"
    parent_task: str = ""; worktree: str = ""; plan_id: str = "sprint-1"
    sprint: str = ""; delivery_phase: str = "mvp"; phase_progression: str = "standard"
    plane_issue_id: str = ""; plane_workspace: str = ""; plane_project_id: str = ""
    contribution_type: str = ""; gate_pending: str = ""; security_hold: str = ""


@dataclass
class MockTask:
    id: str = "task-12345678"; title: str = "Test Task"; description: str = "A test task"
    priority: str = "medium"; status: MagicMock = field(default_factory=lambda: MagicMock(value="in_progress"))
    custom_fields: MockCF = field(default_factory=MockCF)
    tags: list = field(default_factory=list); is_blocked: bool = False
    blocked_by_task_ids: list = field(default_factory=list)
    created_at: Optional[str] = None; updated_at: Optional[str] = None; assigned_agent_id: str = ""


def _run(coro):
    loop = asyncio.new_event_loop()
    try: return loop.run_until_complete(coro)
    finally: loop.close()


def _ctx(agent="project-manager"):
    c = MagicMock(); c.agent_name = agent; c.task_id = "task-12345678"
    c.project_name = "fleet"; c.worktree = ""; c.plane = None; c.plane_workspace = ""
    c.mc = AsyncMock(); t = MockTask()
    c.mc.get_task = AsyncMock(return_value=t)
    c.mc.update_task = AsyncMock(return_value=t)
    c.mc.post_comment = AsyncMock(); c.mc.post_memory = AsyncMock()
    c.mc.list_comments = AsyncMock(return_value=[])
    c.mc.list_tasks = AsyncMock(return_value=[t])
    c.mc.list_agents = AsyncMock(return_value=[])
    c.mc.list_memory = AsyncMock(return_value=[])
    c.mc.create_approval = AsyncMock()
    c.irc = AsyncMock(); c.irc.notify = AsyncMock(return_value=True)
    c.resolve_board_id = AsyncMock(return_value="board-123")
    return c, t


def _tool(agent, tool_name, ctx, **kw):
    os.environ['FLEET_AGENT'] = agent
    for k in [k for k in sys.modules if 'fleet.mcp' in k]: del sys.modules[k]
    with patch("fleet.mcp.context.FleetMCPContext.from_env", return_value=ctx):
        from fleet.mcp.server import create_server
        server = create_server()
        fn = server._tool_manager._tools[tool_name].fn
        return _run(fn(**kw))


# ─── PM ───────────────────────────────────────────────────────────────
def test_pm_sprint_standup():
    c, t = _ctx("project-manager"); t.custom_fields.plan_id = "sprint-1"
    r = _tool("project-manager", "pm_sprint_standup", c, sprint_id="sprint-1")
    assert r["ok"]; assert "sprint_id" in r

def test_pm_contribution_check():
    c, t = _ctx("project-manager")
    r = _tool("project-manager", "pm_contribution_check", c, task_id="task-12345678")
    assert r["ok"]; assert "all_received" in r

def test_pm_epic_breakdown():
    c, t = _ctx("project-manager")
    r = _tool("project-manager", "pm_epic_breakdown", c, task_id="task-12345678")
    assert r["ok"]; assert "breakdown_guide" in r

def test_pm_gate_route():
    c, t = _ctx("project-manager")
    r = _tool("project-manager", "pm_gate_route", c, task_id="task-12345678", gate_type="readiness_90")
    assert r["ok"]; assert "gate_summary" in r

def test_pm_blocker_resolve():
    c, t = _ctx("project-manager"); t.is_blocked = True; t.blocked_by_task_ids = ["dep-1"]
    r = _tool("project-manager", "pm_blocker_resolve", c, task_id="task-12345678")
    assert r["ok"]; assert "resolution_options" in r

# ─── Fleet-ops ────────────────────────────────────────────────────────
def test_ops_real_review():
    c, t = _ctx("fleet-ops")
    r = _tool("fleet-ops", "ops_real_review", c, task_id="task-12345678")
    assert r["ok"]; assert "review" in r; assert "recommendation" in r["review"]

def test_ops_board_health():
    c, t = _ctx("fleet-ops")
    r = _tool("fleet-ops", "ops_board_health_scan", c)
    assert r["ok"]; assert "healthy" in r

def test_ops_compliance():
    c, t = _ctx("fleet-ops"); t.status = MagicMock(value="done")
    r = _tool("fleet-ops", "ops_compliance_spot_check", c)
    assert r["ok"]; assert "sampled" in r

def test_ops_budget():
    c, t = _ctx("fleet-ops")
    r = _tool("fleet-ops", "ops_budget_assessment", c)
    assert r["ok"]; assert "assessment" in r

# ─── Architect ────────────────────────────────────────────────────────
def test_arch_design():
    c, t = _ctx("architect")
    r = _tool("architect", "arch_design_contribution", c, task_id="task-12345678")
    assert r["ok"]; assert "next_step" in r

def test_arch_codebase():
    c, t = _ctx("architect")
    r = _tool("architect", "arch_codebase_assessment", c, directory="fleet/core/")
    assert r["ok"]; assert "assessment_framework" in r

def test_arch_options():
    c, t = _ctx("architect")
    r = _tool("architect", "arch_option_comparison", c, task_id="task-12345678")
    assert r["ok"]

def test_arch_complexity():
    c, t = _ctx("architect")
    r = _tool("architect", "arch_complexity_estimate", c, task_id="task-12345678")
    assert r["ok"]; assert "guide" in r

# ─── DevSecOps ────────────────────────────────────────────────────────
def test_sec_contribution():
    c, t = _ctx("devsecops-expert")
    r = _tool("devsecops-expert", "sec_contribution", c, task_id="task-12345678")
    assert r["ok"]; assert "next_step" in r

def test_sec_pr_review():
    c, t = _ctx("devsecops-expert")
    r = _tool("devsecops-expert", "sec_pr_security_review", c, task_id="task-12345678")
    assert r["ok"]; assert "checklist" in r

def test_sec_dep_audit():
    c, t = _ctx("devsecops-expert")
    r = _tool("devsecops-expert", "sec_dependency_audit", c)
    assert r["ok"]

def test_sec_code_scan():
    c, t = _ctx("devsecops-expert")
    r = _tool("devsecops-expert", "sec_code_scan", c, directory="fleet/core/")
    assert r["ok"]

def test_sec_secret_scan():
    c, t = _ctx("devsecops-expert")
    r = _tool("devsecops-expert", "sec_secret_scan", c)
    assert r["ok"]

def test_sec_infra_health():
    c, t = _ctx("devsecops-expert")
    r = _tool("devsecops-expert", "sec_infrastructure_health", c)
    assert r["ok"]

# ─── Engineer ─────────────────────────────────────────────────────────
def test_eng_contrib_check():
    c, t = _ctx("software-engineer")
    r = _tool("software-engineer", "eng_contribution_check", c)
    assert r["ok"]; assert "all_received" in r

def test_eng_fix_response():
    c, t = _ctx("software-engineer")
    r = _tool("software-engineer", "eng_fix_task_response", c)
    assert r["ok"]

# ─── DevOps ───────────────────────────────────────────────────────────
def test_devops_infra_health():
    c, t = _ctx("devops")
    r = _tool("devops", "devops_infrastructure_health", c)
    assert r["ok"]; assert "healthy" in r

def test_devops_deploy_contrib():
    c, t = _ctx("devops")
    r = _tool("devops", "devops_deployment_contribution", c, task_id="task-12345678")
    assert r["ok"]; assert "delivery_phase" in r

def test_devops_cicd():
    c, t = _ctx("devops")
    r = _tool("devops", "devops_cicd_review", c, task_id="task-12345678")
    assert r["ok"]

def test_devops_phase_infra():
    c, t = _ctx("devops")
    r = _tool("devops", "devops_phase_infrastructure", c, task_id="task-12345678")
    assert r["ok"]; assert "phase" in r

# ─── QA ───────────────────────────────────────────────────────────────
def test_qa_predefine():
    c, t = _ctx("qa-engineer")
    r = _tool("qa-engineer", "qa_test_predefinition", c, task_id="task-12345678")
    assert r["ok"]; assert "context" in r

def test_qa_validate():
    c, t = _ctx("qa-engineer")
    r = _tool("qa-engineer", "qa_test_validation", c, task_id="task-12345678")
    assert r["ok"]

def test_qa_coverage():
    c, t = _ctx("qa-engineer")
    r = _tool("qa-engineer", "qa_coverage_analysis", c)
    assert r["ok"]

def test_qa_criteria():
    c, t = _ctx("qa-engineer")
    r = _tool("qa-engineer", "qa_acceptance_criteria_review", c, task_id="task-12345678")
    assert r["ok"]

# ─── Writer ───────────────────────────────────────────────────────────
def test_writer_doc():
    c, t = _ctx("technical-writer")
    r = _tool("technical-writer", "writer_doc_contribution", c, task_id="task-12345678")
    assert r["ok"]

def test_writer_staleness():
    c, t = _ctx("technical-writer"); t.status = MagicMock(value="done"); t.custom_fields.task_type = "story"
    r = _tool("technical-writer", "writer_staleness_scan", c)
    assert r["ok"]

# ─── UX ───────────────────────────────────────────────────────────────
def test_ux_spec():
    c, t = _ctx("ux-designer")
    r = _tool("ux-designer", "ux_spec_contribution", c, task_id="task-12345678")
    assert r["ok"]

def test_ux_accessibility():
    c, t = _ctx("ux-designer")
    r = _tool("ux-designer", "ux_accessibility_audit", c)
    assert r["ok"]

# ─── Accountability ───────────────────────────────────────────────────
def test_acct_trail():
    c, t = _ctx("accountability-generator")
    r = _tool("accountability-generator", "acct_trail_reconstruction", c, task_id="task-12345678")
    assert r["ok"]; assert "trail_events_count" in r

def test_acct_compliance():
    c, t = _ctx("accountability-generator"); t.status = MagicMock(value="done")
    r = _tool("accountability-generator", "acct_sprint_compliance", c)
    assert r["ok"]

def test_acct_patterns():
    c, t = _ctx("accountability-generator"); t.status = MagicMock(value="done")
    r = _tool("accountability-generator", "acct_pattern_detection", c)
    assert r["ok"]; assert "patterns" in r
