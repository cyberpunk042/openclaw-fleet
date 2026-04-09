#!/usr/bin/env python3
"""Validate session output — produce inspectable artifacts for every system.

Run this to generate human-readable output that the PO can manually inspect
to verify each system produces correct, complete, high-standard results.

Usage:
  python scripts/validate-session-output.py > validation-output.md
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from fleet.core.models import Task, TaskStatus, TaskCustomFields


def make_task(**kwargs):
    defaults = {
        "id": "task-a1b2c3d4e5f6",
        "board_id": "board-1",
        "title": "Add fleet health dashboard to Mission Control UI",
        "status": TaskStatus.IN_PROGRESS,
        "description": "Create a dashboard component showing agent status, task progress, storm level, and budget usage",
        "priority": "high",
        "custom_fields": TaskCustomFields(
            task_stage="work",
            task_readiness=99,
            task_progress=30,
            requirement_verbatim="Add a health dashboard to the MC frontend showing: agent grid (online/idle/sleeping/offline), task pipeline (inbox→progress→review→done counts), storm indicator with severity color, budget gauge with percentage",
            project="fleet",
            agent_name="software-engineer",
            task_type="story",
            story_points=5,
            delivery_phase="mvp",
            phase_progression="standard",
            parent_task="epic-abc123",
            labor_iteration=1,
        ),
    }
    defaults.update(kwargs)
    return Task(**defaults)


def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def subsection(title):
    print(f"\n--- {title} ---\n")


# ============================================================
section("1. AUTOCOMPLETE CHAIN — What the engineer sees in task-context.md")
# ============================================================

from fleet.core.preembed import build_task_preembed
task = make_task()
chain = build_task_preembed(task)
print(chain)
print(f"\n[SIZE: {len(chain)} chars]")

# Verify sections are in order
required_sections = [
    "YOU ARE:", "YOUR TASK:", "YOUR STAGE:", "READINESS:",
    "VERBATIM REQUIREMENT", "WHAT TO DO NOW", "WHAT HAPPENS WHEN YOU ACT",
]
positions = []
for s in required_sections:
    pos = chain.find(s)
    positions.append((s, pos))

print(f"\n[SECTION ORDER CHECK]")
prev_pos = -1
all_ordered = True
for name, pos in positions:
    ok = "✓" if pos > prev_pos else "✗ OUT OF ORDER"
    if pos < 0:
        ok = "✗ MISSING"
        all_ordered = False
    elif pos <= prev_pos:
        all_ordered = False
    print(f"  {ok} {name} at position {pos}")
    prev_pos = pos
print(f"  → {'ALL IN ORDER' if all_ordered else 'ORDER BROKEN'}")


# ============================================================
section("2. FOCUSED TOOLS.MD — What the engineer sees as tool reference")
# ============================================================

tools_md = Path("agents/software-engineer/TOOLS.md").read_text()
print(tools_md[:3000])
if len(tools_md) > 3000:
    print(f"\n... [{len(tools_md) - 3000} more chars]")
print(f"\n[SIZE: {len(tools_md)} chars — target <6000]")
print(f"[Has 'Your Tools': {'✓' if '## Your Tools' in tools_md else '✗'}]")
print(f"[Has 'Boundaries': {'✓' if '## Boundaries' in tools_md else '✗'}]")
print(f"[Has chain arrows: {'✓' if '**→**' in tools_md else '✗'}]")
print(f"[No Skills section: {'✓' if '## Skills' not in tools_md else '✗ STILL HAS SKILLS'}]")
print(f"[No Hooks section: {'✓' if '## Hooks' not in tools_md else '✗ STILL HAS HOOKS'}]")


# ============================================================
section("3. CLAUDE.MD — What the engineer sees as role rules")
# ============================================================

claude_md = Path("agents/_template/CLAUDE.md/software-engineer.md").read_text()
print(claude_md)
print(f"\n[SIZE: {len(claude_md)} chars — limit 4000]")
print(f"[Sections: {claude_md.count('## ')} — target 8]")


# ============================================================
section("4. DISEASE DETECTION — Scenario: engineer commits without reading")
# ============================================================

from fleet.core.doctor import (
    detect_code_without_reading, detect_scope_creep,
    detect_cascading_fix, detect_compression,
    DiseaseCategory,
)

print("Scenario: Agent called fleet_commit without any Read/Grep/Glob calls")
d = detect_code_without_reading(
    "software-engineer", "task-a1b2c3d4",
    tool_calls=["fleet_commit", "fleet_task_complete"],
    has_read_calls=False,
)
if d:
    print(f"  Disease: {d.disease.value}")
    print(f"  Severity: {d.severity.value}")
    print(f"  Signal: {d.signal}")
    print(f"  Evidence: {d.evidence}")
    print(f"  Action: {d.suggested_action.value}")
else:
    print("  ✗ NOT DETECTED — this is wrong")

print()
print("Scenario: Agent on fix iteration 3 (cascading fixes)")
d = detect_cascading_fix("software-engineer", "task-a1b2c3d4", fix_iteration=3)
if d:
    print(f"  Disease: {d.disease.value}")
    print(f"  Severity: {d.severity.value}")
    print(f"  Signal: {d.signal}")
    print(f"  Action: {d.suggested_action.value}")

print()
print("Scenario: Agent changed 5 files outside the planned 2")
d = detect_scope_creep(
    "software-engineer", "task-a1b2c3d4",
    files_changed=["a.py", "b.py", "x.py", "y.py", "z.py"],
    planned_files=["a.py", "b.py"],
)
if d:
    print(f"  Disease: {d.disease.value}")
    print(f"  Evidence: {d.evidence}")

print()
print("Scenario: Agent compressed 200-word requirement to 30-word plan")
d = detect_compression("software-engineer", "task-a1b2c3d4", 200, 30)
if d:
    print(f"  Disease: {d.disease.value}")
    print(f"  Evidence: {d.evidence}")


# ============================================================
section("5. TEACHING — What the lesson looks like for each disease")
# ============================================================

from fleet.core.teaching import adapt_lesson, DiseaseCategory as DC

for disease in [DC.PROTOCOL_VIOLATION, DC.CODE_WITHOUT_READING, DC.CASCADING_FIX, DC.COMPRESSION, DC.NOT_LISTENING]:
    lesson = adapt_lesson(
        disease, "software-engineer", "task-a1b2c3d4",
        context={
            "requirement_verbatim": "Add health dashboard with agent grid and budget gauge",
            "current_stage": "work",
            "agent_plan": "I'll add a dashboard component",
            "what_agent_did": "fleet_commit without reading code",
            "fix_iteration": "3",
            "scope_description": "health dashboard with 4 panels",
            "what_agent_produced": "single status line",
            "po_questions_count": "3",
            "agent_answers_count": "0",
        },
    )
    print(f"Disease: {disease.value}")
    print(f"  Lesson: {lesson.content[:150]}...")
    print(f"  Exercise: {lesson.exercise.instruction[:100]}...")
    print()


# ============================================================
section("6. EFFORT ESCALATION — Budget mode scenarios")
# ============================================================

from fleet.core.model_selection import select_model_for_task

task = make_task()
for mode in ["turbo", "standard", "economic", "minimal"]:
    config = select_model_for_task(task, "software-engineer", budget_mode=mode)
    print(f"  Budget mode '{mode}': model={config.model}, effort={config.effort}")
    print(f"    Reason: {config.reason}")

print()
print("Rate limit pressure scenarios:")
for pct in [50, 70, 85, 92, 96]:
    config = select_model_for_task(task, "software-engineer", rate_limit_pct=float(pct))
    print(f"  Rate limit {pct}%: effort={config.effort}")

print()
print("Rejection escalation:")
for rej in [0, 1, 2]:
    config = select_model_for_task(task, "software-engineer", rejection_count=rej)
    print(f"  Rejection #{rej}: effort={config.effort}")


# ============================================================
section("7. CONTEXT STRATEGY — Threshold scenarios")
# ============================================================

from fleet.core.context_strategy import ContextStrategy

strategy = ContextStrategy()
for ctx_pct, rate_pct in [(30, 20), (72, 40), (83, 60), (91, 75), (96, 88), (50, 92), (50, 96)]:
    ev = strategy.evaluate("engineer", context_pct=ctx_pct, rate_limit_pct=rate_pct)
    print(f"  Context={ctx_pct}% Rate={rate_pct}%: ctx_action={ev.context_action.value}, rate_action={ev.rate_limit_action.value}")
    if ev.message:
        for line in ev.message.split('\n'):
            print(f"    → {line}")
    print(f"    block_dispatch={ev.should_block_dispatch}, should_compact={ev.should_compact}")


# ============================================================
section("8. LABOR STAMP — Trainee flagging output")
# ============================================================

from fleet.core.labor_stamp import LaborStamp

expert = LaborStamp(agent_name="software-engineer", backend="claude-code", model="opus-4-6", effort="high", duration_seconds=340, estimated_tokens=15000, estimated_cost_usd=0.0450, lines_added=120, lines_removed=30)
trainee = LaborStamp(agent_name="software-engineer", backend="localai", model="hermes-3b", effort="medium", duration_seconds=180, estimated_tokens=8000, lines_added=80, lines_removed=10)
community = LaborStamp(agent_name="software-engineer", backend="openrouter", model="mimo-v2-pro", effort="medium")

for stamp, label in [(expert, "EXPERT"), (trainee, "TRAINEE"), (community, "COMMUNITY")]:
    subsection(f"{label} stamp")
    print(f"  is_trainee: {stamp.is_trainee}")
    print(f"  requires_challenge: {stamp.requires_challenge}")
    print(f"  short_label: {stamp.short_label}")
    print(f"  provenance_line: {stamp.provenance_line}")
    print(f"  trainee_warning: {stamp.trainee_warning or '(none)'}")
    print(f"  full_signature: {stamp.full_signature}")


# ============================================================
section("9. CONTRIBUTION FLOW — Synergy matrix check")
# ============================================================

from fleet.core.contributions import detect_contribution_opportunities, check_contribution_completeness

print("Story assigned to software-engineer — what contributions needed?")
opps = detect_contribution_opportunities("task-xyz", "software-engineer", "story")
for o in opps:
    print(f"  {o.contributor_role} → {o.contribution_type} ({o.priority}): {o.description}")

print()
print("Completeness check — none received:")
status = check_contribution_completeness("task-xyz", "software-engineer", "story", [])
print(f"  Required: {status.required}")
print(f"  Missing: {status.missing}")
print(f"  Complete: {status.all_received} ({status.completeness_pct}%)")

print()
print("Completeness check — all received:")
status = check_contribution_completeness("task-xyz", "software-engineer", "story", status.required)
print(f"  Complete: {status.all_received} ({status.completeness_pct}%)")


# ============================================================
section("10. FULL INJECTION SIMULATION — All 8 positions for engineer")
# ============================================================

total = 0
for pos, name, path in [
    (1, "IDENTITY.md", "agents/_template/IDENTITY.md/software-engineer.md"),
    (2, "SOUL.md", "agents/_template/SOUL.md/software-engineer.md"),
    (3, "CLAUDE.md", "agents/_template/CLAUDE.md/software-engineer.md"),
    (4, "TOOLS.md", "agents/software-engineer/TOOLS.md"),
    (5, "AGENTS.md", "agents/software-engineer/AGENTS.md"),
    (8, "HEARTBEAT.md", "agents/_template/heartbeats/software-engineer.md"),
]:
    p = Path(path)
    size = len(p.read_text()) if p.exists() else 0
    total += size
    print(f"  §{pos} {name:15s} {size:5d} chars")

# Context estimated
ctx_est = 9500
total += ctx_est
print(f"  §6-7 context/       ~{ctx_est:5d} chars (fleet + task + knowledge)")
print(f"  {'─'*40}")
print(f"  TOTAL:             ~{total:5d} chars")
print(f"  Gateway limit:     150,000 chars")
print(f"  Usage:              {total/150000*100:.1f}%")


# ============================================================
section("SUMMARY")
# ============================================================

print("All scenarios above should be manually inspected to verify:")
print("  1. Autocomplete chain has correct section order")
print("  2. TOOLS.md is focused (no skills/hooks/CRONs)")
print("  3. CLAUDE.md has 8 sections, role-specific content")
print("  4. Disease detection catches real misbehavior")
print("  5. Teaching lessons are specific, not generic")
print("  6. Effort adapts to budget mode and pressure")
print("  7. Context strategy produces correct actions at thresholds")
print("  8. Trainee flagging shows warnings for non-expert models")
print("  9. Contribution flow creates correct subtasks and gates")
print("  10. Total injection fits within gateway limits")
