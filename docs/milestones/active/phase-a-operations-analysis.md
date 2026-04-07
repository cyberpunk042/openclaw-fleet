# Phase A Operations Analysis — Every Operation in Every Elevated Tree

**Date:** 2026-04-07
**Status:** Analysis — prerequisite to Phase A implementation
**Sources:** fleet-elevation/24 (every tree read line by line)
**PO instruction:** "no rush. we take our time. we never at any point start rushing or doing quickfix or cutting corners or short circuiting the investigations and research."

---

## What This Document Is

Before implementing Phase A, I need to know EVERY operation across ALL elevated trees. This analysis extracts every unique operation, categorizes them, identifies what exists vs what needs building, and maps the implementation order.

---

## All Unique Operations Extracted From Elevated Trees

### Category 1: MC API Operations (INTERNAL surface)

These call the Mission Control REST API:

| Operation | Used By | ChainRunner Action | Status |
|-----------|---------|-------------------|--------|
| mc.get_task(board_id, task_id) | fleet_read_context, fleet_contribute, fleet_transfer, fleet_approve, etc. | Primary action (not chain) | EXISTS in mc_client.py |
| mc.list_tasks(board_id) | fleet_agent_status, evaluate_parent | Primary action (not chain) | EXISTS |
| mc.list_memory(board_id, limit) | fleet_read_context | Primary action (not chain) | EXISTS |
| mc.list_agents() | fleet_agent_status, fleet_task_create | Primary action (not chain) | EXISTS |
| mc.list_approvals(board_id, status) | fleet_agent_status | Primary action (not chain) | EXISTS |
| mc.update_task(board_id, task_id, status) | fleet_task_accept, fleet_task_complete, fleet_approve | update_task_status | EXISTS in ChainRunner |
| mc.update_task(board_id, task_id, custom_fields) | fleet_task_accept, fleet_task_progress, fleet_alert, fleet_gate_request, fleet_approve (reject) | update_custom_fields | EXISTS in ChainRunner (added this session) |
| mc.update_task(board_id, task_id, comment) | fleet_task_accept, fleet_task_complete, fleet_approve | Combined status+comment update | Tool does directly (not chain) |
| mc.post_comment(board_id, task_id, comment) | fleet_commit, fleet_task_complete, fleet_contribute, fleet_approve, fleet_artifact_create/update | post_comment | EXISTS in ChainRunner |
| mc.post_memory(board_id, content, tags, source) | fleet_alert, fleet_chat, fleet_escalate, fleet_gate_request, ALL trail events | post_board_memory | EXISTS in ChainRunner |
| mc.create_task(board_id, ...) | fleet_task_create, fleet_approve (fix task) | Primary action (not chain) | EXISTS in mc_client.py |
| mc.create_approval(board_id, task_ids, ...) | fleet_task_complete | create_approval | EXISTS in ChainRunner |
| mc.approve_approval(board_id, approval_id, ...) | fleet_approve | Primary action (not chain) | EXISTS in mc_client.py |

### Category 2: GitHub Operations (PUBLIC surface)

| Operation | Used By | ChainRunner Action | Status |
|-----------|---------|-------------------|--------|
| git.add(files) | fleet_commit | Primary action (not chain) | EXISTS via gh_client |
| git.commit(message) | fleet_commit | Primary action (not chain) | EXISTS |
| git.push(branch) | fleet_task_complete | push_branch | EXISTS in ChainRunner |
| github.create_pr(branch, title, body) | fleet_task_complete | create_pr | EXISTS in ChainRunner |

### Category 3: IRC Operations (CHANNEL surface)

| Operation | Used By | ChainRunner Action | Status |
|-----------|---------|-------------------|--------|
| irc.send(channel, message) | fleet_chat, fleet_alert, fleet_escalate, fleet_task_create, fleet_task_complete, fleet_approve, fleet_gate_request, fleet_transfer, fleet_phase_advance, fleet_task_progress (checkpoints) | notify_irc | EXISTS in ChainRunner |

### Category 4: Notification Operations (NOTIFY surface)

| Operation | Used By | ChainRunner Action | Status |
|-----------|---------|-------------------|--------|
| ntfy.send(topic, title, message, priority, tags) | fleet_alert (critical/high), fleet_chat (@po), fleet_escalate, fleet_gate_request, fleet_phase_advance, fleet_task_complete | ntfy_publish | EXISTS in ChainRunner |
| notification_router.classify_and_route(event_type, severity) | fleet_alert | NOT a chain action | EXISTS in notification_router.py but NOT wired into tools |

### Category 5: Plane Operations (PLANE surface)

| Operation | Used By | ChainRunner Action | Status |
|-----------|---------|-------------------|--------|
| plane_sync.update_issue(status, labels, comment) | fleet_task_accept, fleet_task_progress, fleet_commit, fleet_task_complete, fleet_approve, fleet_transfer | update_issue_state (status), update_labels (labels), post_comment (comment) | PARTIAL — update_issue_state + post_comment + update_labels exist in ChainRunner (update_labels added this session) |
| plane_sync.create_issue(workspace, project, title, description, labels, parent_issue) | fleet_task_create | create_issue | EXISTS in ChainRunner (added this session). Missing: parent_issue linking, labels at creation |
| plane_sync.update_issue(description_html) | fleet_artifact_create, fleet_artifact_update | NOT a chain action — done by tool directly via transpose | EXISTS in tool code (direct Plane API call) |

### Category 6: Event Operations (META surface)

| Operation | Used By | ChainRunner Action | Status |
|-----------|---------|-------------------|--------|
| events.emit(event_type, ...) | EVERY state-modifying tool | _emit_event() function in tools.py | EXISTS — but called independently, not through ChainRunner. ChainRunner emits its own chain-level event. |

### Category 7: Methodology Operations (LOGIC — not a surface)

These are LOGIC operations that happen WITHIN the tool, not through ChainRunner:

| Operation | Used By | What It Does | Status |
|-----------|---------|-------------|--------|
| methodology.check_plan_references_verbatim(plan, verbatim) | fleet_task_accept | Warn if plan doesn't reference verbatim requirement | DOES NOT EXIST — need to build |
| methodology.verify_commit_in_work_stage(task_stage) | fleet_commit | Verify commit is happening during work stage (defense-in-depth) | PARTIALLY EXISTS — _check_stage_allowed does this, but the elevated tree suggests a post-commit verification too |
| artifact_tracker.check_completeness(type, object, phase) | fleet_artifact_create/update | Check artifact completeness against phase standards | EXISTS in artifact_tracker.py — but phase parameter not connected |
| phases.check_phase_standards(task, phase) | fleet_phase_advance | Check if current phase standards are met | DOES NOT EXIST — phase_system module not built |

### Category 8: Context Operations (LOGIC — not a surface)

| Operation | Used By | What It Does | Status |
|-----------|---------|-------------|--------|
| context_assembly.assemble_task_context(task, mc, board_id) | fleet_read_context, fleet_task_context | Aggregate all task data into bundle | EXISTS |
| context.update_target_task(target_task_id, contributions) | fleet_contribute | Embed contribution into target agent's context | DOES NOT EXIST — need to build. Currently contributions are only comments, not embedded in target context. |
| context_writer.write_task_context(to_agent, task_id, include_transfer_package) | fleet_transfer | Write transfer context with packaged contributions/artifacts | PARTIALLY EXISTS — write_task_context exists but transfer_package parameter doesn't |

### Category 9: Complex Operations (Multi-Step Logic)

| Operation | Used By | What It Does | Status |
|-----------|---------|-------------|--------|
| notify_contributors(task_id, roles) | fleet_task_complete | For each contributor with predefined input → mention them that task is in review | DOES NOT EXIST as a function — need to build |
| evaluate_parent(parent_task_id) | fleet_task_complete, fleet_approve (approve) | Check if all children done → parent to review | PARTIALLY EXISTS in orchestrator (_evaluate_parents). Not available as callable from tools. |
| update_sprint_progress() | fleet_approve (approve) | Update sprint metrics after task completion | DOES NOT EXIST as callable from tools |
| check_contribution_completeness(target_task_id) | fleet_contribute | Check if all required contributions received for phase → notify PM if complete | DOES NOT EXIST — needs synergy matrix + phase config |
| doctor.signal_rejection(agent_name, task_id) | fleet_approve (reject) | Signal immune system about repeated rejections | DOES NOT EXIST as callable |
| package_context for transfer | fleet_transfer | Package architect inputs, QA tests, security reqs, artifacts, trail | DOES NOT EXIST |

### Category 10: Conditional Logic Within Trees

| Condition | Tool | What Happens | Status |
|-----------|------|-------------|--------|
| if readiness >= 50 | fleet_task_progress | Emit checkpoint event → notify PO | NOT IMPLEMENTED in tool |
| if readiness >= 90 | fleet_task_progress | Emit gate request → ntfy PO, IRC #gates | NOT IMPLEMENTED in tool |
| if severity in ("critical", "high") | fleet_alert | Send ntfy with urgent priority | PARTIALLY — chain builder has this but ntfy client not always initialized |
| if category == "security" | fleet_alert | Set security_hold custom field on task | NOT IMPLEMENTED |
| if mention == "human"/"po" | fleet_chat | Send ntfy to PO | In stub chain builder but not fully wired |
| if mention is specific agent | fleet_chat | Post board memory with mention tag | Tool already does this |
| if parent_task exists | fleet_task_create | Comment on parent + Plane create linked issue | Stub chain has parent comment. Plane parent linking NOT IMPLEMENTED |
| if contribution_type set | fleet_task_create | Emit contribution opportunity event | NOT IMPLEMENTED |
| if all children done | evaluate_parent | Move parent to review | In orchestrator but not callable from tools |
| if plan doesn't reference verbatim | fleet_task_accept | Warn agent | NOT IMPLEMENTED |
| if contribution task exists for role | fleet_request_input | Reference it; else suggest PM creates one | NOT IMPLEMENTED |

---

## Gap Summary

### Operations That EXIST and Work:
- All MC API operations (mc_client.py)
- All GitHub operations (gh_client.py)
- IRC notification (irc_client.py)
- ntfy publish (ntfy_client.py)
- Plane post_comment, update_issue_state, create_issue, update_labels (ChainRunner)
- Event emission (_emit_event in tools.py + ChainRunner chain-level event)
- Context assembly (context_assembly.py)
- Artifact completeness check (artifact_tracker.py)
- Stage enforcement (_check_stage_allowed in tools.py)

### Operations That DON'T EXIST and Need Building:

**New functions/modules (STATUS UPDATED):**
1. `check_plan_references_verbatim(plan, verbatim)` — ✅ BUILT in plan_quality.py. Key term extraction, 30% coverage threshold.
2. `check_phase_standards(task_data, phase)` — ✅ BUILT in phases.py. Evaluates task against PO-defined phase quality bars.
3. `append_contribution_to_task_context(agent, type, contributor, content)` — ✅ BUILT in context_writer.py. Appends contribution sections to target agent's task-context.md.
4. `package_transfer_context(task_id, from_agent, to_agent, ...)` — ✅ BUILT in transfer_context.py. Gathers contributions, artifacts, trail into TransferPackage.
5. `notify_contributors(task_id, title, mc, board_id)` — ✅ BUILT in contributor_notify.py. Reads task comments, posts @mention for each contributor.
6. `check_contribution_completeness(task_id, agent, type, received)` — ✅ ALREADY EXISTED in contributions.py. Reads synergy matrix, checks required vs received.
7. `signal_rejection(agent_name, task_id, reviewer, reason)` — ✅ BUILT in doctor.py. Records rejection signal for immune system detection.
8. `update_sprint_progress_for_task(task_id, mc, board_id)` — ✅ BUILT in velocity.py. Loads sprint, computes metrics, posts progress to board memory.
9. `package_transfer_context(...)` — (duplicate of #4, merged)

**Plane operations to enhance:**
10. Plane create_issue with parent_issue linking (currently creates orphaned issues)
11. Plane create_issue with labels at creation time (type:X, phase:Y)

**Conditional logic to implement in tools:**
12. fleet_task_progress: auto-checkpoint at 50%, auto-gate-request at 90%
13. fleet_alert: security_hold on security category
14. fleet_alert: notification_router.classify_and_route integration
15. fleet_task_accept: verbatim reference check
16. fleet_task_create: contribution opportunity event emission
17. fleet_request_input: contribution task existence check
18. fleet_contribute: contribution completeness check with PM notification

---

## Implementation Order for Phase A

> "no rush. we take our time."

### A1-Step 1: Build the missing functions/modules FIRST

These are the building blocks that tools and chain builders need:

1. `fleet/core/phase_system.py` — check_phase_standards(task, phase) reading config/phases.yaml
2. `fleet/core/plan_quality.py` — extend with check_plan_references_verbatim(plan, verbatim) 
3. `fleet/core/contribution_checker.py` — check_contribution_completeness(task_id) reading synergy-matrix.yaml
4. `fleet/core/transfer_context.py` — package_transfer_context(task_id) gathering all contribution data
5. `fleet/core/context_writer.py` — extend write_task_context with transfer_package support
6. `fleet/core/preembed.py` or `context_assembly.py` — update_target_task_contributions()
7. Extend orchestrator helper functions to be callable from tools: notify_contributors, update_sprint_progress

### A1-Step 2: Extend ChainRunner handlers

- PLANE create_issue: add parent_issue linking and labels at creation
- (Most other operations already covered)

### A2-Step 3: Rewrite each tool's elevated tree operations

For EACH of the 30 tools, implement the FULL elevated tree from fleet-elevation/24. Not stubs. Every operation, every conditional, every path.

Order by complexity (simplest first to establish patterns):
1. fleet_escalate (simplest elevated tree)
2. fleet_chat (moderate — conditionals on mention type)
3. fleet_commit (moderate — methodology verification)
4. fleet_task_accept (moderate — verbatim reference check)
5. fleet_alert (moderate — severity/category conditionals, security_hold)
6. fleet_pause (moderate — PM mention routing)
7. fleet_task_progress (complex — readiness checkpoints, auto-gate at 90%)
8. fleet_artifact_create/update (moderate — phase-aware completeness)
9. fleet_task_create (complex — Plane linking, contribution events)
10. fleet_request_input (moderate — contribution task check)
11. fleet_gate_request (moderate — already close)
12. fleet_phase_advance (moderate — phase standards check)
13. fleet_contribute (complex — context update, completeness check, PM notification)
14. fleet_transfer (complex — context packaging, transfer bundle)
15. fleet_approve (most complex — approve path + reject path + parent eval + sprint progress + doctor signal)
16. fleet_task_complete (already most complete — enhance with notify_contributors, parent eval)

### A3-Step 4: Phase config evolution

- Extend config/phases.yaml to support flexible predefinable groups
- Build fleet/core/phase_system.py to read and evaluate phase standards
- Connect to artifact_tracker (phase parameter)

### A4-Step 5: Context system updates

- Phase standards in task pre-embed
- Contribution status in task pre-embed
- Stage-appropriate tool/skill recommendations in pre-embed

### Tests for EVERYTHING

Each new function gets unit tests. Each tool rewrite gets integration tests with mock clients. Zero stubs. Full elevated tree verified.

---

## What This Analysis Shows

Phase A is NOT "wire chains into tools." Phase A is:

1. Build 9 new functions/modules that the elevated trees need
2. Enhance ChainRunner Plane operations
3. Rewrite 16 state-modifying tools to FULLY match fleet-elevation/24 (every operation, every conditional)
4. Build phase system module
5. Extend context system for contributions and phase standards
6. Write comprehensive tests for all of it

This is a substantial engineering effort — not a day of adding try/except blocks. Each tool rewrite touches multiple systems (MC, Plane, IRC, ntfy, events, trail, methodology, contributions, phases).

The PO said: "no rush. we take our time. we never at any point start rushing or doing quickfix or cutting corners."

This analysis ensures we know EXACTLY what needs to be built before writing a single line of implementation code.
