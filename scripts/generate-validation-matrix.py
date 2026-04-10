#!/usr/bin/env python3
"""Generate validation matrix — every state combination rendered for inspection.

Each scenario produces a separate file in validation-matrix/ that shows
EXACTLY what the agent sees. Line by line. No summarization.

Two primary modes:
  HEARTBEAT — agent wakes on CRON, processes queue
  TASK — agent dispatched to work on specific task

Each mode has multiple state axes:
  Stage: conversation, analysis, investigation, reasoning, work
  Contributions: none received, partial, all received
  Plane: connected, not connected
  Iteration: first attempt, rejection rework
  Injection: full, none
"""

import os, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from fleet.core.models import Task, TaskStatus, TaskCustomFields
from fleet.core.preembed import build_task_preembed, build_heartbeat_preembed
from fleet.core.tier_renderer import TierRenderer

EXPERT_RENDERER = TierRenderer("expert")

OUT_DIR = Path("validation-matrix")
if OUT_DIR.exists():
    shutil.rmtree(OUT_DIR)
OUT_DIR.mkdir()


def write_scenario(filename, title, content):
    path = OUT_DIR / filename
    with open(path, "w") as f:
        f.write(f"# {title}\n\n")
        f.write(content)
    print(f"  {filename} ({len(content)} chars)")


def read_runtime(agent, filename):
    p = Path(f"agents/{agent}/{filename}")
    if p.exists():
        return p.read_text()
    p2 = Path(f"agents/_template/heartbeats/{agent}.md")
    if filename == "HEARTBEAT.md" and p2.exists():
        return p2.read_text()
    return f"[{filename} not found for {agent}]"


def make_task(**kwargs):
    defaults = dict(
        id="task-a1b2c3d4", board_id="b1",
        title="Add fleet health dashboard", status=TaskStatus.IN_PROGRESS,
        priority="high", description="Dashboard with agent grid, task pipeline, storm, budget",
        custom_fields=TaskCustomFields(
            agent_name="software-engineer", task_type="story", story_points=5,
            project="fleet",
        ),
    )
    defaults.update(kwargs)
    return Task(**defaults)


# Simulated contributions
ARCH_CONTRIB = """## CONTRIBUTION: design_input (from architect)

**Approach:** DashboardHealth component in fleet/ui/components/ using React.
- AgentGrid: 10 cards, color-coded by status
- TaskPipeline: horizontal bar chart (inbox/progress/review/done)
- StormIndicator: circular gauge with severity colors
- BudgetGauge: arc gauge with 5h and 7d usage

**Target files:** fleet/ui/components/DashboardHealth.tsx, fleet/ui/hooks/useFleetStatus.ts
**Patterns:** Observer (real-time), Adapter (API → component)
**Constraints:** Existing MC build pipeline. No new deps.

---"""

QA_CONTRIB = """## CONTRIBUTION: qa_test_definition (from qa-engineer)

TC-001: AgentGrid shows 10 agent cards | unit | required
TC-002: Agent card color matches status | unit | required
TC-003: TaskPipeline segments sum to total | unit | required
TC-004: StormIndicator correct severity color | unit | required
TC-005: BudgetGauge shows API percentage | integration | required
TC-006: Dashboard refreshes on status change | integration | recommended
TC-007: Keyboard navigation works | e2e | required

---"""

NAV_WORK = """## Stage: WORK — Resources Available

### Skills:
- /fleet-engineer-workflow — contribution consumption, TDD, conventional commits
- /fleet-completion-checklist — 8-point pre-completion check
- /test-driven-development (superpowers) — RED-GREEN-REFACTOR cycle
- /verification-before-completion (superpowers) — run tests before claiming done

### Sub-agents:
- **test-runner** (sonnet) — run pytest in isolated context
- **code-explorer** (sonnet) — trace execution paths

### MCP: fleet · filesystem · github · playwright
### Plugins: claude-mem · safety-net · context7 · superpowers · pyright-lsp
"""

NAV_REASONING = """## Stage: REASONING — Resources Available

### Skills:
- /fleet-implementation-planning — map plan to files and changes
- /writing-plans (superpowers) — detailed implementation roadmap
- /brainstorming (superpowers) — explore approaches

### Sub-agents:
- **code-explorer** (sonnet) — understand codebase before planning

### MCP: fleet · filesystem · github · context7
"""

NAV_CONVERSATION = """## Stage: CONVERSATION — Resources Available

### Skills:
- /fleet-communicate — which channel for what
- /brainstorming (superpowers) — explore problem space

### Sub-agents:
- **code-explorer** (sonnet) — reference codebase in questions

### MCP: fleet · filesystem
"""


print("=" * 60)
print("  Generating Validation Matrix")
print("=" * 60)
print()


# ═══════════════════════════════════════════════════════════
# HEARTBEAT MODE SCENARIOS
# ═══════════════════════════════════════════════════════════

print("HEARTBEAT MODE:")

# HB-01: Idle, no tasks
hb = build_heartbeat_preembed(
    agent_name="software-engineer", role="software-engineer",
    assigned_tasks=[], agents_online=8, agents_total=10,
    fleet_mode="full-autonomous", fleet_phase="execution", fleet_backend="claude",
    renderer=EXPERT_RENDERER,
)
write_scenario("HB-01-idle-no-tasks.md",
    "Heartbeat: Engineer idle, no tasks assigned",
    f"**Expected behavior:** Check messages, check standing orders, HEARTBEAT_OK.\n"
    f"**fleet_read_context:** NOT needed — data pre-embedded.\n\n"
    f"## fleet-context.md\n\n```\n{hb}\n```\n\n"
    f"## HEARTBEAT.md\n\n```\n{read_runtime('software-engineer', 'HEARTBEAT.md')}\n```\n"
)

# HB-02: Has in-progress task (work stage)
task_work = make_task(custom_fields=TaskCustomFields(
    task_stage="work", task_readiness=99, task_progress=40,
    requirement_verbatim="Add health dashboard with agent grid and budget gauge",
    agent_name="software-engineer", task_type="story", story_points=5,
    delivery_phase="mvp",
))
hb2 = build_heartbeat_preembed(
    agent_name="software-engineer", role="software-engineer",
    assigned_tasks=[task_work], agents_online=9, agents_total=10,
    fleet_mode="full-autonomous", fleet_phase="execution", fleet_backend="claude",
    role_data={"my_tasks_count": 1, "contribution_tasks": [],
        "contributions_received": [
            {"type": "design_input", "from": "architect", "status": "done"},
            {"type": "qa_test_definition", "from": "qa-engineer", "status": "done"},
        ], "in_review": []},
    renderer=EXPERT_RENDERER,
)
write_scenario("HB-02-has-work-task.md",
    "Heartbeat: Engineer has in-progress task (work stage)",
    f"**Expected behavior:** See task in assigned, continue work, follow HEARTBEAT.md §2.\n"
    f"**fleet_read_context:** NOT needed — task visible in pre-embed.\n\n"
    f"## fleet-context.md\n\n```\n{hb2}\n```\n\n"
    f"## HEARTBEAT.md\n\n```\n{read_runtime('software-engineer', 'HEARTBEAT.md')}\n```\n"
)

# HB-03: Has messages (PM assigned work)
hb3 = build_heartbeat_preembed(
    agent_name="software-engineer", role="software-engineer",
    assigned_tasks=[], agents_online=9, agents_total=10,
    fleet_mode="full-autonomous", fleet_phase="execution", fleet_backend="claude",
    messages=[
        {"from": "project-manager", "content": "Assigned you task-xyz: Implement fleet controls sidebar. Story points: 3. Stage: reasoning."},
    ],
    renderer=EXPERT_RENDERER,
)
write_scenario("HB-03-has-messages.md",
    "Heartbeat: Engineer has message from PM (new assignment)",
    f"**Expected behavior:** Read message, acknowledge assignment.\n\n"
    f"## fleet-context.md\n\n```\n{hb3}\n```\n"
)

# HB-04: Fleet-ops with pending reviews
hb4 = build_heartbeat_preembed(
    agent_name="fleet-ops", role="fleet-ops",
    assigned_tasks=[], agents_online=10, agents_total=10,
    fleet_mode="full-autonomous", fleet_phase="execution", fleet_backend="claude",
    role_data={
        "pending_approvals": 2,
        "approval_details": [
            {"id": "appr-001", "task_id": "task-abc1", "status": "pending"},
            {"id": "appr-002", "task_id": "task-def2", "status": "pending"},
        ],
        "review_queue": [
            {"id": "task-abc1", "title": "Add fleet health dashboard", "agent": "software-engineer",
             "verbatim": "Add health dashboard with agent grid, task pipeline, storm indicator, budget gauge",
             "pr": "https://github.com/org/openfleet/pull/42", "type": "story"},
            {"id": "task-def2", "title": "Fix orchestrator stage bug", "agent": "devops",
             "verbatim": "Fix stage transition when readiness changes mid-cycle",
             "pr": "https://github.com/org/openfleet/pull/43", "type": "bug"},
        ],
        "offline_agents": ["ux-designer"],
    },
    renderer=EXPERT_RENDERER,
)
write_scenario("HB-04-fleet-ops-reviews.md",
    "Heartbeat: Fleet-ops with 2 pending reviews",
    f"**Expected behavior:** Process each review using ops_real_review(). 7-step protocol.\n\n"
    f"## fleet-context.md\n\n```\n{hb4}\n```\n\n"
    f"## HEARTBEAT.md\n\n```\n{read_runtime('fleet-ops', 'HEARTBEAT.md')}\n```\n"
)

# HB-05: PM with unassigned tasks
hb5 = build_heartbeat_preembed(
    agent_name="project-manager", role="project-manager",
    assigned_tasks=[], agents_online=9, agents_total=10,
    fleet_mode="full-autonomous", fleet_phase="execution", fleet_backend="claude",
    role_data={
        "unassigned_tasks": 3,
        "unassigned_details": [
            {"id": "task-un1", "title": "Investigate memory leak in orchestrator", "priority": "high",
             "type": "bug", "stage": "unset", "readiness": 0, "description": "Orchestrator leaks memory after 48h continuous operation"},
            {"id": "task-un2", "title": "Add changelog generation to writer CRON", "priority": "medium"},
            {"id": "task-un3", "title": "Update fleet-identity config for beta", "priority": "low"},
        ],
        "blocked_tasks": 1,
        "progress": "12/25 done (48%)",
        "inbox_count": 5,
    },
    renderer=EXPERT_RENDERER,
)
write_scenario("HB-05-pm-unassigned.md",
    "Heartbeat: PM with 3 unassigned inbox tasks + 1 blocker",
    f"**Expected behavior:** Triage each task with ALL fields. Assign agents.\n\n"
    f"## fleet-context.md\n\n```\n{hb5}\n```\n\n"
    f"## HEARTBEAT.md\n\n```\n{read_runtime('project-manager', 'HEARTBEAT.md')}\n```\n"
)


print()
print("TASK MODE:")

# ═══════════════════════════════════════════════════════════
# TASK MODE SCENARIOS
# ═══════════════════════════════════════════════════════════

def render_task_scenario(filename, title, task, injection="full",
                         contribs="", nav="", notes="",
                         renderer=None, rejection_feedback="", target_task=None,
                         confirmed_plan="", received_contribution_types=None):
    r = renderer or EXPERT_RENDERER
    base = build_task_preembed(task, injection_level=injection,
                                renderer=r, rejection_feedback=rejection_feedback,
                                target_task=target_task, confirmed_plan=confirmed_plan,
                                received_contribution_types=received_contribution_types)
    if contribs:
        # Insert contribution content at the marker and update checklist
        insert_marker = "<!-- CONTRIBUTIONS_ABOVE -->"
        if insert_marker in base:
            base = base.replace(insert_marker, f"\n{contribs}\n", 1)
        # Mark delivered types as received in checklist
        import re
        for ctype_match in re.findall(r'## CONTRIBUTION:\s*(\S+)', contribs):
            base = base.replace(
                f"**{ctype_match}** from",
                f"**{ctype_match}** ✓ from",
            )
            # Only replace awaiting on the specific line
            lines_list = base.split("\n")
            for i, line in enumerate(lines_list):
                if f"**{ctype_match}**" in line and "awaiting delivery" in line:
                    lines_list[i] = line.replace("— *awaiting delivery*", "— *received*")
            base = "\n".join(lines_list)
    parts = [
        f"**Expected:** {notes}\n",
        f"## task-context.md\n\n```\n{base}\n```\n",
    ]
    if nav:
        parts.append(f"## knowledge-context.md\n\n```\n{nav}\n```\n")
    write_scenario(filename, title, "\n".join(parts))


# TK-01: Work stage, full injection, all contributions received
render_task_scenario("TK-01-work-full-contrib.md",
    "Task: Work stage, full injection, contributions received",
    make_task(custom_fields=TaskCustomFields(
        task_stage="work", task_readiness=99, task_progress=40,
        requirement_verbatim="Add health dashboard with agent grid, task pipeline, storm indicator, budget gauge",
        agent_name="software-engineer", task_type="story", story_points=5,
        delivery_phase="mvp", parent_task="epic-fleet-ui-001",
    )),
    contribs=ARCH_CONTRIB + "\n" + QA_CONTRIB,
    received_contribution_types=["design_input", "qa_test_definition"],
    nav=NAV_WORK,
    notes="Engineer has everything. Follow plan, commit, complete. fleet_read_context NOT needed.",
    confirmed_plan="1. Create DashboardHealth.tsx component\n2. Implement AgentGrid (10 cards, color-coded)\n3. Implement TaskPipeline (horizontal bar chart)\n4. Implement StormIndicator (circular gauge)\n5. Implement BudgetGauge (arc gauge)\n6. Wire useFleetStatus.ts hook\n7. Tests for TC-001 through TC-007",
)

# TK-02: Work stage, full injection, NO contributions (missing)
render_task_scenario("TK-02-work-no-contrib.md",
    "Task: Work stage, full injection, contributions MISSING",
    make_task(custom_fields=TaskCustomFields(
        task_stage="work", task_readiness=99, task_progress=0,
        requirement_verbatim="Add health dashboard with agent grid",
        agent_name="software-engineer", task_type="story", story_points=5,
        delivery_phase="mvp",
    )),
    nav=NAV_WORK,
    notes="Contributions required but NOT received. Should see 'fleet_request_input()' directive. Should NOT proceed.",
)

# TK-03: Reasoning stage
render_task_scenario("TK-03-reasoning.md",
    "Task: Reasoning stage — produce plan, NOT implement",
    make_task(custom_fields=TaskCustomFields(
        task_stage="reasoning", task_readiness=85, task_progress=0,
        requirement_verbatim="Add health dashboard with agent grid, task pipeline, storm indicator, budget gauge",
        agent_name="software-engineer", task_type="story", story_points=5,
    )),
    nav=NAV_REASONING,
    notes="PLAN only. NO code. NO commits. Reference verbatim. fleet_commit should NOT appear in recommended actions.",
)

# TK-04: Conversation stage
render_task_scenario("TK-04-conversation.md",
    "Task: Conversation stage — clarify requirements, NO code",
    make_task(custom_fields=TaskCustomFields(
        task_stage="conversation", task_readiness=10, task_progress=0,
        requirement_verbatim="We need a dashboard but details unclear",
        agent_name="software-engineer", task_type="story",
    )),
    nav=NAV_CONVERSATION,
    notes="CLARIFY only. NO code, NO solutions, NO designs. Ask questions.",
)

# TK-05: No injection (direct CLI dispatch)
render_task_scenario("TK-05-no-injection.md",
    "Task: Work stage, NO injection (direct CLI)",
    make_task(custom_fields=TaskCustomFields(
        task_stage="work", task_readiness=99,
        requirement_verbatim="Add health dashboard",
        agent_name="software-engineer", task_type="task",
    )),
    injection="none",
    notes="NO pre-embedded data. Must call fleet_read_context() FIRST.",
)

# TK-06: Rejection rework (iteration 2)
render_task_scenario("TK-06-rejection-rework.md",
    "Task: Work stage, rejection rework (iteration 2)",
    make_task(custom_fields=TaskCustomFields(
        task_stage="work", task_readiness=99, task_progress=0,
        requirement_verbatim="Add health dashboard with agent grid",
        agent_name="software-engineer", task_type="story", story_points=5,
        delivery_phase="mvp", labor_iteration=2,
    )),
    contribs=ARCH_CONTRIB + "\n" + QA_CONTRIB,
    received_contribution_types=["design_input", "qa_test_definition"],
    nav=NAV_WORK,
    notes="Second attempt after rejection. Should show iteration 2, rejection feedback, eng_fix_task_response().",
    rejection_feedback="REJECTED by fleet-ops: Missing test for TC-003 (TaskPipeline segments). Add integration test verifying segment sum equals total count.",
)

# TK-07: Architect contribution task
TARGET_TASK = Task(id="task-a1b2c3d4", board_id="b1",
    title="Add fleet health dashboard to MC frontend",
    status=TaskStatus.IN_PROGRESS, priority="high",
    description="Dashboard with agent grid, task pipeline, storm, budget",
    custom_fields=TaskCustomFields(
        requirement_verbatim="Add a health dashboard showing: agent grid (online/idle/sleeping/offline), task pipeline (inbox/progress/review/done counts), storm indicator with severity color, budget gauge with percentage",
        delivery_phase="mvp", task_stage="work", task_readiness=99,
        agent_name="software-engineer",
    ))

render_task_scenario("TK-07-architect-contribution.md",
    "Task: Architect producing design_input contribution",
    Task(id="task-contrib99", board_id="b1",
        title="Contribute design_input for: fleet health dashboard",
        status=TaskStatus.IN_PROGRESS, priority="medium",
        custom_fields=TaskCustomFields(
            task_stage="analysis", task_readiness=50,
            requirement_verbatim="Provide design_input: approach, target files, patterns for the fleet health dashboard",
            agent_name="architect", task_type="subtask",
            contribution_type="design_input", contribution_target="task-a1b2c3d4",
        )),
    notes="Architect examining codebase for design. Should show CONTRIBUTION TASK section with target task verbatim, fleet_contribute() reference.",
    target_task=TARGET_TASK,
)

# TK-08: QA predefinition contribution
render_task_scenario("TK-08-qa-predefinition.md",
    "Task: QA predefining test criteria (TC-XXX)",
    Task(id="task-qa-predef", board_id="b1",
        title="Contribute qa_test_definition for: fleet health dashboard",
        status=TaskStatus.IN_PROGRESS, priority="medium",
        custom_fields=TaskCustomFields(
            task_stage="reasoning", task_readiness=80,
            requirement_verbatim="Define structured TC-XXX test criteria for the fleet health dashboard story",
            agent_name="qa-engineer", task_type="subtask",
            contribution_type="qa_test_definition", contribution_target="task-a1b2c3d4",
        )),
    notes="QA producing TC-XXX criteria. Phase-appropriate (MVP = main flows + critical edges).",
)

# TK-09: With Plane connected (delivery phase mvp)
render_task_scenario("TK-09-with-plane-mvp.md",
    "Task: Work stage with Plane connected, MVP phase",
    make_task(custom_fields=TaskCustomFields(
        task_stage="work", task_readiness=99, task_progress=60,
        requirement_verbatim="Add health dashboard with agent grid",
        agent_name="software-engineer", task_type="story", story_points=5,
        delivery_phase="mvp", phase_progression="standard",
        plane_issue_id="issue-abc123", plane_project_id="proj-fleet",
    )),
    contribs=ARCH_CONTRIB + "\n" + QA_CONTRIB,
    received_contribution_types=["design_input", "qa_test_definition"],
    nav=NAV_WORK,
    notes="Plane connected — issue linked. MVP phase standards visible. fleet_task_complete will sync to Plane.",
)

# TK-10: Nearly complete (progress 70%)
render_task_scenario("TK-10-nearly-complete.md",
    "Task: Work stage, nearly complete (progress 70%)",
    make_task(custom_fields=TaskCustomFields(
        task_stage="work", task_readiness=99, task_progress=70,
        requirement_verbatim="Add health dashboard with agent grid",
        agent_name="software-engineer", task_type="story", story_points=5,
        delivery_phase="mvp",
    )),
    contribs=ARCH_CONTRIB + "\n" + QA_CONTRIB,
    received_contribution_types=["design_input", "qa_test_definition"],
    nav=NAV_WORK,
    notes="Progress 70% = implementation done. Should run tests, then fleet_task_complete.",
)

# TK-11: Analysis stage — should reference wiki/domains/ as output location
render_task_scenario("TK-11-analysis.md",
    "Task: Analysis stage — examine codebase, produce analysis document",
    make_task(custom_fields=TaskCustomFields(
        task_stage="analysis", task_readiness=30,
        requirement_verbatim="Add health dashboard with agent grid, task pipeline, storm indicator, budget gauge",
        agent_name="software-engineer", task_type="story", story_points=5,
    )),
    notes="Analysis stage. Output should go to wiki/domains/. NO solutions, NO code. Reference specific files and lines.",
)

# TK-12: Investigation stage — should reference wiki/domains/ as output location
render_task_scenario("TK-12-investigation.md",
    "Task: Investigation stage — research approaches",
    make_task(custom_fields=TaskCustomFields(
        task_stage="investigation", task_readiness=60,
        requirement_verbatim="Add health dashboard with agent grid, task pipeline, storm indicator, budget gauge",
        agent_name="software-engineer", task_type="story", story_points=5,
    )),
    notes="Investigation stage. Output should go to wiki/domains/. Multiple options required. NO decisions.",
)

# TK-34: Engineer role-specific reasoning
render_task_scenario("TK-34-engineer-reasoning.md",
    "Task: Engineer reasoning — role-specific protocol",
    make_task(custom_fields=TaskCustomFields(
        task_stage="reasoning", task_readiness=85,
        requirement_verbatim="Add health dashboard with agent grid, task pipeline, storm indicator, budget gauge",
        agent_name="software-engineer", task_type="story", story_points=5,
    )),
    nav=NAV_REASONING,
    notes="Engineer reasoning should say 'implementation plan'. Compare: architect would say 'design_input'.",
)


# TK-13: Blocked task
render_task_scenario("TK-13-blocked.md",
    "Task: Work stage, BLOCKED by dependency",
    make_task(
        is_blocked=True, blocked_by_task_ids=["task-blocker1"],
        custom_fields=TaskCustomFields(
            task_stage="work", task_readiness=99,
            requirement_verbatim="Add health dashboard with agent grid",
            agent_name="software-engineer", task_type="story", story_points=5,
        )),
    notes="Blocked task. Should show BLOCKED in task detail and action directive should tell agent to report via fleet_pause().",
)

# TK-25: Subtask (skip contributions)
render_task_scenario("TK-25-subtask.md",
    "Task: Subtask — skip contributions, reasoning+work only",
    Task(id="task-sub001", board_id="b1",
        title="Implement AgentGrid component",
        status=TaskStatus.IN_PROGRESS, priority="medium",
        custom_fields=TaskCustomFields(
            task_stage="work", task_readiness=99, task_progress=0,
            requirement_verbatim="Create AgentGrid showing 10 agent cards color-coded by status",
            agent_name="software-engineer", task_type="subtask",
            parent_task="task-a1b2c3d4",
        )),
    notes="Subtask. No contributions required (skip_contributions type). Parent task shown.",
)

# TK-29: No verbatim requirement
render_task_scenario("TK-29-no-verbatim.md",
    "Task: Conversation stage, NO verbatim requirement",
    make_task(custom_fields=TaskCustomFields(
        task_stage="conversation", task_readiness=5,
        requirement_verbatim="",
        agent_name="software-engineer", task_type="story",
    )),
    notes="No verbatim. Should show 'ask PO for clarification'. Must not proceed without verbatim.",
)

# TK-30: Capable tier (condensed) — golden path at qwen3-8b level
render_task_scenario("TK-30-capable-tier.md",
    "Task: Work stage, CAPABLE tier (condensed context)",
    make_task(custom_fields=TaskCustomFields(
        task_stage="work", task_readiness=99, task_progress=40,
        requirement_verbatim="Add health dashboard with agent grid, task pipeline, storm indicator, budget gauge",
        agent_name="software-engineer", task_type="story", story_points=5,
        delivery_phase="mvp", parent_task="epic-fleet-ui-001",
    )),
    contribs=ARCH_CONTRIB + "\n" + QA_CONTRIB,
    received_contribution_types=["design_input", "qa_test_definition"],
    renderer=TierRenderer("capable"),
    nav=NAV_WORK,
    notes="CAPABLE tier (qwen3-8b, 16K). Condensed context. Core fields only. Contributions as status, not full content.",
    confirmed_plan="1. Create DashboardHealth.tsx\n2. AgentGrid\n3. TaskPipeline\n4. StormIndicator\n5. BudgetGauge\n6. Tests",
)

# TK-31: Lightweight tier (minimal) — golden path at gemma4-e2b level
render_task_scenario("TK-31-lightweight-tier.md",
    "Task: Work stage, LIGHTWEIGHT tier (minimal context)",
    make_task(custom_fields=TaskCustomFields(
        task_stage="work", task_readiness=99, task_progress=40,
        requirement_verbatim="Add health dashboard with agent grid, task pipeline, storm indicator, budget gauge",
        agent_name="software-engineer", task_type="story", story_points=5,
        delivery_phase="mvp",
    )),
    renderer=TierRenderer("lightweight"),
    notes="LIGHTWEIGHT tier (gemma4-e2b, 8-16K). Minimal context. Don't overwhelm the trainee.",
)

# HB-06: Urgent PO directive
hb6 = build_heartbeat_preembed(
    agent_name="software-engineer", role="software-engineer",
    assigned_tasks=[], agents_online=9, agents_total=10,
    fleet_mode="full-autonomous", fleet_phase="execution", fleet_backend="claude",
    directives=[
        {"content": "STOP all dashboard work. Priority shift to auth fix. Start immediately.", "from": "human", "urgent": True},
    ],
    renderer=EXPERT_RENDERER,
)
write_scenario("HB-06-urgent-directive.md",
    "Heartbeat: Urgent PO directive — overrides everything",
    f"**Expected behavior:** PO directive is HIGHEST PRIORITY. Stop current work, execute directive.\n\n"
    f"## fleet-context.md\n\n```\n{hb6}\n```\n"
)

# HB-20: Lightweight heartbeat
hb_light = build_heartbeat_preembed(
    agent_name="software-engineer", role="software-engineer",
    assigned_tasks=[make_task(custom_fields=TaskCustomFields(
        task_stage="work", task_readiness=99, task_progress=40,
        requirement_verbatim="Add health dashboard with agent grid",
        agent_name="software-engineer", task_type="story", story_points=5,
    ))],
    agents_online=9, agents_total=10,
    fleet_mode="full-autonomous", fleet_phase="execution", fleet_backend="localai",
    role_data={"my_tasks_count": 1, "contribution_tasks": [], "contributions_received": {}, "in_review": []},
    renderer=TierRenderer("lightweight"),
)
write_scenario("HB-20-lightweight.md",
    "Heartbeat: Lightweight tier — minimal heartbeat context",
    f"**Expected:** Lightweight (gemma4-e2b). Minimal task detail, no standing orders, no events detail.\n\n"
    f"## fleet-context.md\n\n```\n{hb_light}\n```\n"
)


# TK-27: Spike task — research model, no work stage
render_task_scenario("TK-27-spike.md",
    "Task: Spike — research model, investigation stage",
    Task(id="task-spike01", board_id="b1",
        title="Research caching strategies for fleet context",
        status=TaskStatus.IN_PROGRESS, priority="medium",
        custom_fields=TaskCustomFields(
            task_stage="investigation", task_readiness=60,
            requirement_verbatim="Evaluate Redis vs SQLite vs file-based caching for 30-second context refresh cycle",
            agent_name="architect", task_type="spike", story_points=3,
        )),
    notes="Spike task. Research model selected. NO work stage. Must NOT produce code. Investigation → reasoning → done.",
)

# TK-42: Concern task — research model, no work stage
render_task_scenario("TK-42-concern.md",
    "Task: Concern — investigation only, no implementation",
    Task(id="task-concern01", board_id="b1",
        title="Investigate orchestrator memory growth over 48h",
        status=TaskStatus.IN_PROGRESS, priority="high",
        custom_fields=TaskCustomFields(
            task_stage="analysis", task_readiness=30,
            requirement_verbatim="The orchestrator process grows from 200MB to 1.2GB over 48 hours. Find the root cause.",
            agent_name="software-engineer", task_type="concern",
        )),
    notes="Concern task. Research model. Analysis + investigation only. NO work stage, NO code output.",
)

# FL-01: Planning cycle_phase — only PM + architect active
hb_planning = build_heartbeat_preembed(
    agent_name="software-engineer", role="software-engineer",
    assigned_tasks=[], agents_online=2, agents_total=10,
    fleet_mode="full-autonomous", fleet_phase="planning", fleet_backend="claude",
    renderer=EXPERT_RENDERER,
)
write_scenario("FL-01-planning-phase-inactive.md",
    "Fleet: Planning phase — engineer NOT ACTIVE",
    f"**Expected:** Engineer sees 'planning' phase. Should recognize it's not their turn. HEARTBEAT_OK.\n\n"
    f"## fleet-context.md\n\n```\n{hb_planning}\n```\n"
)

# FL-03: Crisis cycle_phase — only fleet-ops + devsecops active
hb_crisis_ops = build_heartbeat_preembed(
    agent_name="fleet-ops", role="fleet-ops",
    assigned_tasks=[], agents_online=2, agents_total=10,
    fleet_mode="full-autonomous", fleet_phase="crisis-management", fleet_backend="claude",
    role_data={
        "pending_approvals": 0,
        "approval_details": [],
        "review_queue": [],
        "offline_agents": ["software-engineer", "architect", "qa-engineer", "devops", "technical-writer", "ux-designer", "accountability-generator", "project-manager"],
    },
    renderer=EXPERT_RENDERER,
)
write_scenario("FL-03-crisis-fleet-ops.md",
    "Fleet: Crisis management — fleet-ops ACTIVE, 8 agents offline",
    f"**Expected:** Crisis mode. Fleet-ops is active. 8 of 10 agents offline. Focus on the crisis.\n\n"
    f"## fleet-context.md\n\n```\n{hb_crisis_ops}\n```\n"
)

print()
print("=" * 60)
total = len(list(OUT_DIR.glob("*.md")))
print(f"  Generated {total} scenario files in validation-matrix/")
print(f"  Inspect each file to verify line-by-line correctness.")
print("=" * 60)
