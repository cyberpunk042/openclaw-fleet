# System 01: Methodology — Stage-Gated Task Progression

**Type:** Fleet System
**ID:** S01
**Files:** methodology.py (476 lines), stage_context.py (214 lines), phases.py (187 lines)
**Config:** config/phases.yaml (110 lines)
**Total:** 877 lines of code + 110 lines config
**Tests:** 55+

## What This System Does

Enforces a 5-stage progression that prevents agents from coding before understanding requirements. Every task moves through stages — each with boolean gate checks that ALL must pass before advancement. Work stage (where code is produced) requires PO-confirmed readiness of 99%.

Before this system existed, agents received a task and immediately started coding. The result: code that didn't match requirements, solutions without research, plans that didn't reference the PO's words, implementations that deviated from what was asked.

## The 5 Stages

```
CONVERSATION (readiness 10) → ask PO, get verbatim requirement
  Checks: has_verbatim_requirement, has_po_response, no_open_questions
  Produces: questions, draft proposals (NO code, NO commits)

ANALYSIS (readiness 30) → read codebase, examine what exists
  Checks: has_analysis_document, po_reviewed
  Produces: analysis documents with file references (NO solutions)

INVESTIGATION (readiness 50) → research multiple options
  Checks: has_research_document, multiple_options_explored, po_reviewed
  Produces: option comparisons with tradeoffs (NO decisions)

REASONING (readiness 80) → plan the approach
  Checks: has_plan, plan_references_verbatim, plan_specifies_files, po_confirmed_plan
  Produces: implementation plan referencing verbatim (NO code)

WORK (readiness 99) → execute the confirmed plan
  Checks: readiness >= 99, has_commits, has_pr, acceptance_criteria_met, required_tools_called
  Produces: code, tests, PRs via fleet_commit + fleet_task_complete
```

ALL checks must pass for `can_advance = True`. No partial advancement.

## Task Types Skip Stages

Not every task needs all 5 stages:

| Type | Stages | Why |
|------|--------|-----|
| epic | all 5 | Complex — needs full process |
| story | conversation → reasoning → work | Clear scope — skip analysis/investigation |
| task | reasoning → work | Well-defined — just plan and execute |
| subtask | reasoning → work | Even simpler |
| bug | analysis → reasoning → work | Analyze what's broken, plan fix, fix |
| spike | conversation → investigation → reasoning | Research only — NO work stage |
| concern | conversation → analysis → investigation | Analysis only — NO work stage |

Configured in `DEFAULT_REQUIRED_STAGES` (methodology.py:44-91).

## Readiness Values

NOT continuous 0-100. Specific valid values that map to Plane labels:

```
Valid: 0, 5, 10, 20, 30, 50, 70, 80, 90, 95, 99, 100
snap_readiness() rounds to nearest valid value.

Strategic checkpoints:
  50  → direction review (PO gate — fleet_gate_request)
  90  → final review (PO gate — plan ready for confirmation)
  99  → work authorized (PO said "go" — dispatch eligible)
  100 → task complete
```

Suggested readiness per stage: conversation=10, analysis=30, investigation=50, reasoning=80, work=99. These are SUGGESTIONS — PO sets actual readiness.

## Stage Instructions — What Agents See

Each stage has MUST do / MUST NOT do / CAN produce / How to advance instructions from stage_context.py. Injected into agent's task-context.md Layer 7 via preembed.py. Every non-work stage says "Do NOT call fleet_commit or fleet_task_complete."

Work stage specifies the required tool sequence:
```
1. fleet_read_context (load task + methodology state)
2. fleet_task_accept (confirm plan)
3. fleet_commit (one or more — conventional format)
4. fleet_task_complete (push, PR, review)
```

## MCP Enforcement

WORK_ONLY_TOOLS in tools.py: fleet_task_complete blocked outside work stage. fleet_commit allowed in stages 2-5 (agents produce artifacts in analysis+). Calling a blocked tool returns error + emits fleet.methodology.protocol_violation event → doctor detects → teaching lesson injected.

## Delivery Phases (Distinct from Stages)

Stages = how you WORK on a task. Phases = PO's declaration of deliverable maturity.

Phases are FREE TEXT — the PO declares the phase ("poc", "mvp", "potato") and provides requirements per case. No predefined progressions. No config-driven enforcement. Each deliverable is different — PO decides what each phase means for THAT specific deliverable.

A deliverable in "mvp" phase has multiple tasks, each going through their own stages independently.

## Relationships

- ENFORCED BY: MCP tools.py _check_stage_allowed (stage-gated tools)
- ENFORCED BY: PreToolUse hook (structural prevention — broader than MCP check)
- DETECTED BY: doctor.py detect_protocol_violation (immune system catches violations)
- TREATED BY: teaching.py (protocol_violation lesson injected)
- CONSUMED BY: orchestrator.py Step 5 (dispatch gate — readiness >= 99)
- CONSUMED BY: preembed.py (stage instructions injected into agent context)
- CONSUMED BY: context_assembly.py (methodology section in task context)
- CONSUMED BY: artifact_tracker.py (completeness → suggested readiness)
- CONSUMED BY: plan_quality.py (plan assessment at fleet_task_accept)
- CONSUMED BY: fleet_gate_request tool (readiness gates at 50% and 90%)
- CONNECTS TO: S02 immune system (protocol violations → disease detection)
- CONNECTS TO: S03 teaching (lessons for methodology violations)
- CONNECTS TO: S07 orchestrator (enforces stages, gates dispatch)
- CONNECTS TO: S08 MCP tools (stage gating on tools)
- CONNECTS TO: S09 standards (artifact standards per type/phase)
- CONNECTS TO: S10 transpose (artifacts rendered to Plane per type)
- CONNECTS TO: S17 Plane (methodology labels: stage:X, readiness:N)
- CONNECTS TO: S22 agent intelligence (autocomplete chain uses stage instructions)
- NOT YET IMPLEMENTED: contribution flow at reasoning stage (brain creating subtasks), phase gate enforcement in orchestrator, automated stage check evaluation

## For LightRAG Entity Extraction

Key entities: Stage (CONVERSATION, ANALYSIS, INVESTIGATION, REASONING, WORK), MethodologyTracker, StageCheckResult, readiness (integer 0-100), task_type (epic, story, task, subtask, bug, spike, concern), delivery_phase (free text), requirement_verbatim (sacrosanct anchor).

Key relationships: Stage GATES tools. Readiness GATES dispatch. Task type DETERMINES required stages. PO CONFIRMS readiness. Doctor DETECTS violations. Teaching CORRECTS violations. Preembed INJECTS stage instructions. Artifact completeness SUGGESTS readiness.
