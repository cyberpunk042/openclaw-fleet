# HEARTBEAT — Worker Agent

Your full context is pre-embedded — assigned tasks with stages, readiness, verbatim requirements, artifact state, contributions, messages, directives. Read it FIRST. No tool calls needed for awareness.

## 0. PO Directives (HIGHEST PRIORITY)

Read your DIRECTIVES section. PO orders override everything. Execute immediately.

## 1. Messages

Read your MESSAGES section. Respond to ALL @mentions via `fleet_chat()`:
- PM assigning work → acknowledge, read the assignment
- PM asking for status → report progress on task
- Architect giving design guidance → follow in your work
- Fleet-ops giving review feedback → address specific issues
- QA flagging test gaps → add tests

## 2. Core Job — Work on Assigned Tasks

Read your ASSIGNED TASKS section. Your task context includes your current stage and protocol — follow it.

**Per stage (from your CLAUDE.md):**
- conversation: clarify requirements with PO. NO code.
- analysis: examine codebase, produce analysis_document. NO solutions.
- investigation: research approaches, explore options. NO decisions.
- reasoning: produce plan referencing verbatim. NO implementation.
- work (readiness ≥ 99): execute confirmed plan.

**Before work stage:** Check context for colleague contributions:
- Architect design_input → follow approach and file structure
- QA qa_test_definition → each TC-XXX is a REQUIREMENT
- UX ux_spec → follow for user-facing work
- DevSecOps security_requirement → follow absolutely
Missing required → `fleet_request_input()` to PM.

**Completing:** `fleet_task_complete(summary)` triggers the full chain — push, PR, approval, IRC, Plane. One call does everything.

## 3. Proactive — Contribution Tasks

When assigned a contribution task (your role contributing to another agent's work):
- Read the target task's verbatim requirement in your context
- Produce your contribution per your CLAUDE.md specialty
- `fleet_contribute(task_id, contribution_type, content)`

## 4. Progressive Work Across Cycles

If continuing from a previous cycle:
- TASK CONTEXT shows artifact state — what's done, what's missing, completeness %
- Continue from where you left off
- Update artifact with new progress
- Post progress comment on task

## 5. Communication

- Blocked → `fleet_chat("blocked: {reason}", mention="project-manager")`
- Design question → `fleet_chat("@architect {question}")`
- Progress → task comment with update
- Done → `fleet_task_complete()` handles all notifications
- Discover work outside scope → `fleet_task_create()` for the right agent

## 6. HEARTBEAT_OK

If no tasks assigned, no contribution tasks, no messages:
- Respond HEARTBEAT_OK
- Do NOT create unnecessary work
- Do NOT call tools for no reason
