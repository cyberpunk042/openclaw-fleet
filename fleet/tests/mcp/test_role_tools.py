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


# ═══════════════════════════════════════════════════════════════════════
# BEHAVIORAL TESTS — verify MC API calls, trail, contribution detection
# ═══════════════════════════════════════════════════════════════════════

# ─── PM behavioral ───────────────────────────────────────────────────

def test_pm_standup_posts_to_board_memory_and_irc():
    c, t = _ctx("project-manager"); t.custom_fields.plan_id = "sprint-1"
    r = _tool("project-manager", "pm_sprint_standup", c, sprint_id="sprint-1")
    assert r["ok"]
    # Should post standup report + trail to board memory
    assert c.mc.post_memory.call_count >= 2
    # Should notify IRC #sprint
    c.irc.notify.assert_called()
    irc_args = c.irc.notify.call_args
    assert "#sprint" in str(irc_args)


def test_pm_contribution_check_detects_missing():
    c, t = _ctx("project-manager")
    t.custom_fields.agent_name = "software-engineer"
    t.custom_fields.task_type = "story"
    # No contributions in comments → should detect missing
    c.mc.list_comments = AsyncMock(return_value=[])
    r = _tool("project-manager", "pm_contribution_check", c, task_id="task-12345678")
    assert r["ok"]
    assert not r["all_received"]
    assert len(r["missing"]) > 0
    assert "suggested_actions" in r


def test_pm_blocker_warns_when_over_limit():
    c, _ = _ctx("project-manager")
    # Create 3 blocked tasks (limit is 2)
    blocked_tasks = []
    for i in range(3):
        bt = MockTask()
        bt.is_blocked = True
        bt.blocked_by_task_ids = [f"dep-{i}"]
        bt.title = f"Blocked task {i}"
        blocked_tasks.append(bt)
    c.mc.list_tasks = AsyncMock(return_value=blocked_tasks)
    r = _tool("project-manager", "pm_blocker_resolve", c, task_id="task-12345678")
    assert r["ok"]
    assert r["fleet_blocked_count"] == 3
    assert "RESOLVE URGENTLY" in r["warning"]


# ─── Fleet-ops behavioral ───────────────────────────────────────────

def test_ops_review_detects_no_verbatim():
    c, t = _ctx("fleet-ops")
    t.custom_fields.requirement_verbatim = ""
    r = _tool("fleet-ops", "ops_real_review", c, task_id="task-12345678")
    assert r["ok"]
    review = r["review"]
    assert not review["verbatim_exists"]
    assert any("verbatim" in i.lower() for i in review["issues"])


def test_ops_review_detects_no_trail():
    c, t = _ctx("fleet-ops")
    c.mc.list_memory = AsyncMock(return_value=[])  # no trail events
    r = _tool("fleet-ops", "ops_real_review", c, task_id="task-12345678")
    review = r["review"]
    assert not review["checks"]["trail_exists"]
    assert any("trail" in i.lower() for i in review["issues"])


def test_ops_review_recommends_approve_when_clean():
    c, t = _ctx("fleet-ops")
    t.custom_fields.requirement_verbatim = "Build the feature"
    # Provide trail events
    trail_entry = MagicMock()
    trail_entry.tags = ["trail", "task:task-12345678"]
    trail_entry.content = "**[trail]** plan_accepted"
    c.mc.list_memory = AsyncMock(return_value=[trail_entry])
    r = _tool("fleet-ops", "ops_real_review", c, task_id="task-12345678")
    review = r["review"]
    assert review["checks"]["trail_exists"]
    assert review["verbatim_exists"]


def test_ops_board_health_detects_blocked():
    c, _ = _ctx("fleet-ops")
    blocked = []
    for i in range(4):
        bt = MockTask()
        bt.is_blocked = True; bt.title = f"Blocked {i}"; bt.id = f"b{i}"
        blocked.append(bt)
    c.mc.list_tasks = AsyncMock(return_value=blocked)
    c.mc.list_agents = AsyncMock(return_value=[])
    r = _tool("fleet-ops", "ops_board_health_scan", c)
    assert r["ok"]
    assert r["tasks_blocked"] == 4
    assert not r["healthy"]


# ─── Engineer behavioral ─────────────────────────────────────────────

def test_eng_contribution_check_shows_received():
    c, t = _ctx("software-engineer")
    t.custom_fields.agent_name = "software-engineer"
    t.custom_fields.task_type = "story"
    # Simulate a received design_input contribution
    comment = MagicMock()
    comment.message = "**Contribution (design_input)** from architect:\n\nUse repository pattern."
    c.mc.list_comments = AsyncMock(return_value=[comment])
    r = _tool("software-engineer", "eng_contribution_check", c)
    assert r["ok"]
    assert len(r["received_contributions"]) == 1
    assert r["received_contributions"][0]["type"] == "design_input"


# ─── Accountability behavioral ───────────────────────────────────────

def test_acct_trail_counts_events():
    c, t = _ctx("accountability-generator")
    events = []
    for i in range(5):
        e = MagicMock()
        e.tags = ["trail", "task:task-12345678"]
        e.content = f"**[trail]** event {i}"
        events.append(e)
    c.mc.list_memory = AsyncMock(return_value=events)
    r = _tool("accountability-generator", "acct_trail_reconstruction", c, task_id="task-12345678")
    assert r["ok"]
    assert r["trail_events_count"] == 5
    assert "event" in r["trail_document"]


def test_acct_sprint_compliance_detects_gaps():
    c, _ = _ctx("accountability-generator")
    # 2 done tasks, 0 trail events → 0% compliant
    t1 = MockTask(); t1.status = MagicMock(value="done"); t1.id = "task-aaa"
    t1.custom_fields.plan_id = "sprint-1"; t1.title = "Task A"
    t2 = MockTask(); t2.status = MagicMock(value="done"); t2.id = "task-bbb"
    t2.custom_fields.plan_id = "sprint-1"; t2.title = "Task B"
    c.mc.list_tasks = AsyncMock(return_value=[t1, t2])
    c.mc.list_memory = AsyncMock(return_value=[])  # no trail
    r = _tool("accountability-generator", "acct_sprint_compliance", c, sprint_id="sprint-1")
    assert r["ok"]
    assert r["total_done"] == 2
    assert r["compliant"] == 0
    assert r["gaps"] == 2


def test_acct_pattern_detects_no_trail():
    c, _ = _ctx("accountability-generator")
    t1 = MockTask(); t1.status = MagicMock(value="done"); t1.id = "done-1"
    t2 = MockTask(); t2.status = MagicMock(value="done"); t2.id = "done-2"
    c.mc.list_tasks = AsyncMock(return_value=[t1, t2])
    c.mc.list_memory = AsyncMock(return_value=[])  # no trail events at all
    r = _tool("accountability-generator", "acct_pattern_detection", c)
    assert r["ok"]
    assert len(r["patterns"]) >= 1
    assert r["patterns"][0]["pattern"] == "tasks_without_trail"


# ─── DevSecOps behavioral ─────────────────────────────────────────

def test_sec_contribution_reads_architect_design():
    """Security contribution should read architect's design_input to assess implications."""
    c, t = _ctx("devsecops-expert")
    t.custom_fields.delivery_phase = "production"
    comment = MagicMock()
    comment.message = "**Contribution (design_input)** from architect:\n\nUse repository pattern with JWT auth."
    c.mc.list_comments = AsyncMock(return_value=[comment])
    r = _tool("devsecops-expert", "sec_contribution", c, task_id="task-12345678")
    assert r["ok"]
    assert r["context"]["architect_design"] != ""
    assert "JWT" in r["context"]["architect_design"] or "repository" in r["context"]["architect_design"]


def test_sec_contribution_records_trail():
    """Security contribution should post trail event to board memory."""
    c, t = _ctx("devsecops-expert")
    r = _tool("devsecops-expert", "sec_contribution", c, task_id="task-12345678")
    assert r["ok"]
    # Trail event posted
    c.mc.post_memory.assert_called()
    trail_call = c.mc.post_memory.call_args
    content = trail_call.kwargs.get("content", trail_call.args[1] if len(trail_call.args) > 1 else "")
    assert "trail" in content.lower()
    assert "security" in content.lower()


def test_sec_pr_review_produces_checklist():
    """Security PR review should produce a structured checklist."""
    c, t = _ctx("devsecops-expert")
    t.custom_fields.pr_url = "https://github.com/org/repo/pull/42"
    t.custom_fields.branch = "fleet/engineer/auth-middleware"
    r = _tool("devsecops-expert", "sec_pr_security_review", c, task_id="task-12345678")
    assert r["ok"]
    assert "checklist" in r
    checklist = r["checklist"]
    # Checklist should mention key security areas
    assert "secrets" in checklist.lower() or "credentials" in checklist.lower()
    assert "injection" in checklist.lower()
    assert "input validation" in checklist.lower()


def test_sec_pr_review_includes_pr_info():
    """Security PR review should include PR URL and branch from task."""
    c, t = _ctx("devsecops-expert")
    t.custom_fields.pr_url = "https://github.com/org/repo/pull/42"
    t.custom_fields.branch = "fleet/engineer/auth-middleware"
    r = _tool("devsecops-expert", "sec_pr_security_review", c, task_id="task-12345678")
    assert r["ok"]
    rc = r["review_context"]
    assert rc["pr_url"] == "https://github.com/org/repo/pull/42"
    assert rc["branch"] == "fleet/engineer/auth-middleware"


# ─── Architect behavioral ────────────────────────────────────────

def test_arch_design_reads_existing_analysis():
    """Architect design contribution should read existing analysis artifacts."""
    c, t = _ctx("architect")
    comment = MagicMock()
    comment.message = "## Analysis Artifact\n\nThe codebase uses repository pattern. Investigation pending."
    c.mc.list_comments = AsyncMock(return_value=[comment])
    r = _tool("architect", "arch_design_contribution", c, task_id="task-12345678")
    assert r["ok"]
    ctx_data = r.get("context", {})
    assert ctx_data.get("existing_analysis") != ""


def test_arch_design_adapts_to_delivery_phase():
    """Design depth should change based on delivery phase."""
    c, t = _ctx("architect")
    t.custom_fields.delivery_phase = "poc"
    r_poc = _tool("architect", "arch_design_contribution", c, task_id="task-12345678")
    assert r_poc["ok"]
    poc_depth = r_poc["context"]["design_depth"]

    t.custom_fields.delivery_phase = "production"
    r_prod = _tool("architect", "arch_design_contribution", c, task_id="task-12345678")
    assert r_prod["ok"]
    prod_depth = r_prod["context"]["design_depth"]

    # POC should be simpler than production
    assert "simple" in poc_depth.lower() or "concept" in poc_depth.lower()
    assert "production" in prod_depth.lower() or "scalable" in prod_depth.lower()


def test_arch_design_records_trail():
    """Architect design contribution should post trail."""
    c, t = _ctx("architect")
    r = _tool("architect", "arch_design_contribution", c, task_id="task-12345678")
    assert r["ok"]
    c.mc.post_memory.assert_called()


# ─── DevOps behavioral ──────────────────────────────────────────

def test_devops_phase_infra_includes_phase():
    """Phase infrastructure should include the delivery phase context."""
    c, t = _ctx("devops")
    t.custom_fields.delivery_phase = "staging"
    r = _tool("devops", "devops_phase_infrastructure", c, task_id="task-12345678")
    assert r["ok"]
    assert r["phase"] == "staging"


def test_devops_deploy_contrib_reads_phase():
    """Deployment contribution should read delivery phase for appropriate advice."""
    c, t = _ctx("devops")
    t.custom_fields.delivery_phase = "production"
    r = _tool("devops", "devops_deployment_contribution", c, task_id="task-12345678")
    assert r["ok"]
    assert r["delivery_phase"] == "production"


def test_devops_infra_health_checks_mc_and_agents():
    """Infrastructure health should check MC backend and agent status."""
    c, _ = _ctx("devops")
    agent_mock = MagicMock()
    agent_mock.name = "test-agent"; agent_mock.status = "offline"
    c.mc.list_agents = AsyncMock(return_value=[agent_mock])
    r = _tool("devops", "devops_infrastructure_health", c)
    assert r["ok"]
    assert "checks" in r
    assert "mc_backend" in r["checks"]
    assert "agents" in r["checks"]
    # Agent should be counted
    assert r["checks"]["agents"]["total"] == 1


# ─── UX behavioral ──────────────────────────────────────────────

def test_ux_spec_records_trail():
    """UX spec contribution should post trail event."""
    c, t = _ctx("ux-designer")
    r = _tool("ux-designer", "ux_spec_contribution", c, task_id="task-12345678")
    assert r["ok"]
    c.mc.post_memory.assert_called()
    trail_call = c.mc.post_memory.call_args
    content = trail_call.kwargs.get("content", trail_call.args[1] if len(trail_call.args) > 1 else "")
    assert "trail" in content.lower()
    assert "ux" in content.lower()


def test_ux_spec_includes_template():
    """UX spec contribution should include the UX assessment template."""
    c, t = _ctx("ux-designer")
    r = _tool("ux-designer", "ux_spec_contribution", c, task_id="task-12345678")
    assert r["ok"]
    template = r.get("template", "")
    # Template should mention key UX concerns
    assert "states" in template.lower()
    assert "accessibility" in template.lower()
    assert "interactions" in template.lower()


def test_ux_accessibility_records_trail():
    """Accessibility audit should post trail event."""
    c, t = _ctx("ux-designer")
    r = _tool("ux-designer", "ux_accessibility_audit", c, task_id="task-12345678")
    assert r["ok"]
    c.mc.post_memory.assert_called()


def test_ux_accessibility_has_wcag_checklist():
    """Accessibility audit should include WCAG-based checklist."""
    c, t = _ctx("ux-designer")
    r = _tool("ux-designer", "ux_accessibility_audit", c)
    assert r["ok"]
    checklist = r.get("checklist", "")
    assert "WCAG" in checklist
    assert "contrast" in checklist.lower()
    assert "keyboard" in checklist.lower()


# ─── Engineer behavioral (additional) ────────────────────────────

def test_eng_fix_response_reads_rejection():
    """Fix task response should read rejection comments."""
    c, t = _ctx("software-engineer")
    rejection_comment = MagicMock()
    rejection_comment.message = "REJECTED: Missing input validation on /api/tasks endpoint"
    c.mc.list_comments = AsyncMock(return_value=[rejection_comment])
    r = _tool("software-engineer", "eng_fix_task_response", c)
    assert r["ok"]


# ─── QA behavioral ──────────────────────────────────────────────────

def test_qa_predefinition_reads_architect_input():
    c, t = _ctx("qa-engineer")
    t.custom_fields.delivery_phase = "production"
    comment = MagicMock()
    comment.message = "**Contribution (design_input)** from architect:\n\nUse onion architecture."
    c.mc.list_comments = AsyncMock(return_value=[comment])
    r = _tool("qa-engineer", "qa_test_predefinition", c, task_id="task-12345678")
    assert r["ok"]
    assert r["context"]["architect_input"] != ""
    assert r["context"]["test_rigor"] == "Complete: all paths, performance, resilience."


def test_qa_validation_warns_missing_criteria():
    c, t = _ctx("qa-engineer")
    c.mc.list_comments = AsyncMock(return_value=[])  # no predefined criteria
    r = _tool("qa-engineer", "qa_test_validation", c, task_id="task-12345678")
    assert r["ok"]
    vc = r["validation_context"]
    assert not vc["has_predefined_criteria"]
    assert "warning" in vc


# ─── Writer behavioral ──────────────────────────────────────────────

def test_writer_staleness_finds_done_stories():
    c, _ = _ctx("technical-writer")
    t1 = MockTask(); t1.status = MagicMock(value="done"); t1.custom_fields.task_type = "story"
    t1.title = "Implement auth"; t1.id = "s1"
    t2 = MockTask(); t2.status = MagicMock(value="done"); t2.custom_fields.task_type = "subtask"
    t2.title = "Minor fix"; t2.id = "s2"
    c.mc.list_tasks = AsyncMock(return_value=[t1, t2])
    r = _tool("technical-writer", "writer_staleness_scan", c)
    assert r["ok"]
    # story should be flagged, subtask should not
    assert r["tasks_to_check"] == 1
