# Tool Call Tree Catalog — Every Tool, Every Tree

**Date:** 2026-03-30
**Status:** Design — complete tool → tree mapping
**Part of:** Fleet Elevation (document 24 — added to series)

---

## PO Requirements (Verbatim)

> "agents need to call the right things that will do the right chains
> of actions... you dont want to have to manually update everywhere"

> "chain is calling multiple tools, not just small process and
> transformation but also add a comment to the mc board for example
> and auto adding it to the task on Plane and etc.... a tree map to
> generate multiple tool call from a single one."

> "only using specific tool when necessary but also aiming for group
> calls."

---

## What This Document Covers

The complete tool call tree for EVERY MCP tool — current 25 and 5 new.
Each tree shows the actual internal function calls that fire from one
agent-facing tool call. The agent calls ONE tool; the system executes
the TREE.

---

## Current 25 Tools — Existing Trees + Elevated Trees

### fleet_read_context(task_id, project)
Agent calls this FIRST every session to load context.

```
fleet_read_context
├── mc.get_task(board_id, task_id)         # load task data
├── mc.list_memory(board_id, limit=20)     # board memory
│   ├── filter: decisions, alerts, escalations, agent mentions
│   └── categorize for agent awareness
├── ctx.resolve_board_id()                 # resolve board
├── urls.resolve(project, task_id)         # resolve links
├── store task_stage + task_readiness      # for stage enforcement
│
│ ELEVATED ADDITIONS:
├── context_assembly.assemble_task_context(task, mc, board_id)
│   ├── methodology: stage, instructions, required stages
│   ├── contributions: architect input, QA tests, DevSecOps reqs
│   ├── artifact: current artifact state + completeness
│   ├── comments: typed, with contributor attribution
│   ├── related_tasks: parent, children, dependencies
│   └── phase: current phase, standards, requirements
├── phases.get_phase_standards(delivery_phase)
└── return: full context bundle with autocomplete chain data
```

### fleet_task_accept(plan)
Agent confirms their plan for the task.

```
fleet_task_accept
├── _check_stage_allowed("fleet_task_accept", task_stage)
│   └── blocks if not in reasoning or work stage
├── mc.update_task(board_id, task_id,
│     custom_fields={plan_accepted: true})
├── mc.post_comment(board_id, task_id,
│     message="Plan accepted: {plan_summary}")
│
│ ELEVATED ADDITIONS:
├── methodology.check_plan_references_verbatim(plan, verbatim)
│   └── warn if plan doesn't reference verbatim requirement
├── plane_sync.update_issue(comment=plan_summary)
├── events.emit("fleet.task.plan_accepted")
└── mc.post_memory(trail_event: "plan_accepted")
```

### fleet_task_progress(summary, readiness_delta)
Agent reports progress on current task.

```
fleet_task_progress
├── mc.post_comment(board_id, task_id,
│     message="Progress: {summary}")
├── mc.update_task(board_id, task_id,
│     custom_fields={task_readiness: new_readiness})
│
│ ELEVATED ADDITIONS:
├── plane_sync.update_issue(
│     comment=progress_summary,
│     labels=update_readiness_label)
├── events.emit("fleet.methodology.readiness_changed")
├── mc.post_memory(trail_event: "progress_update")
├── if readiness >= 50:  # strategic checkpoint
│   └── events.emit("fleet.methodology.checkpoint_reached")
│       └── chain: notify PO
└── if readiness >= 90:  # PO gate
    └── events.emit("fleet.gate.requested",
          gate_type="readiness_90")
        └── chain: ntfy PO, IRC #gates, block advancement
```

### fleet_commit(files, message)
Agent commits code changes.

```
fleet_commit
├── _check_stage_allowed("fleet_commit", task_stage)
│   └── blocks if not in work or reasoning stage
├── git.add(files)
├── git.commit(message)  # conventional format enforced
├── mc.post_comment(board_id, task_id,
│     message="Committed: {message} ({files})")
│
│ ELEVATED ADDITIONS:
├── plane_sync.update_issue(comment=commit_summary)
├── events.emit("fleet.task.commit",
│     agent, task_id, commit_sha, message)
├── mc.post_memory(
│     tags=["trail", f"task:{task_id}"],
│     content=trail_event)
└── methodology.verify_commit_in_work_stage(task_stage)
    └── if violation: events.emit("fleet.methodology.protocol_violation")
```

### fleet_task_complete(summary)
Agent declares task complete. BIGGEST tree — 12+ operations.

```
fleet_task_complete
├── _check_stage_allowed("fleet_task_complete", task_stage)
│   └── blocks if not in work stage
├── git.push(branch, remote="origin")
├── github.create_pr(
│     branch, title=conventional_title,
│     body=pr_description_with_task_ref)
├── mc.update_task(board_id, task_id,
│     status="review",
│     custom_fields={
│       pr_url: pr.url,
│       branch: branch_name,
│       task_readiness: 100,
│     })
├── mc.post_comment(board_id, task_id,
│     message=completion_summary,
│     type="completion")
├── mc.create_approval(board_id, task_id,
│     action_type="review",
│     confidence=calculated_confidence,
│     rubric_scores={...})
├── plane_sync.update_issue(
│     status="review",
│     labels=["status:review", "readiness:100"],
│     comment=completion_summary)
├── irc.send("#reviews",
│     f"[review needed] {title} by {agent}")
├── irc.send("#fleet",
│     f"[complete] {agent} finished {title}")
├── events.emit("fleet.task.completed",
│     agent, task_id, pr_url, summary)
├── mc.post_memory(
│     tags=["trail", f"task:{task_id}", "completion"],
│     content=trail_event)
├── notify_contributors(task_id,
│     roles=["qa-engineer", "devsecops-expert"])
│   ├── for each contributor with predefined input:
│   │   └── mc.post_memory(
│   │         tags=[f"mention:{role}", "review-needed"],
│   │         content="Your contribution on {task} is in review")
│   └── events.emit per contributor notified
└── evaluate_parent(parent_task_id)
    ├── mc.list_tasks(children of parent)
    ├── if ALL children done:
    │   ├── mc.update_task(parent, status="review")
    │   ├── mc.post_comment(parent, aggregate_summary)
    │   ├── mc.create_approval(parent)
    │   ├── plane_sync.update_issue(parent)
    │   └── events.emit("fleet.task.parent_evaluated")
    └── else:
        └── mc.post_comment(parent,
              f"Child completed: {child_title}. {done}/{total} done.")
```

### fleet_alert(category, severity, title, details)
Agent raises an alert.

```
fleet_alert
├── mc.post_memory(board_id,
│     content=alert_text,
│     tags=["alert", category, severity])
├── irc.send("#alerts",
│     f"[{severity}] {category}: {title}")
├── events.emit("fleet.alert.raised",
│     category, severity, agent, details)
│
│ ELEVATED ADDITIONS:
├── if severity in ("critical", "high"):
│   ├── ntfy.send(
│   │     topic="fleet-alert",
│   │     title=f"{category}: {title}",
│   │     message=details,
│   │     priority="urgent",
│   │     tags=ADMONITION_TAGS.get(category))
│   └── notification_router.classify_and_route(
│         event_type=category, severity=severity)
├── if category == "security":
│   └── mc.update_task(task_id,
│         custom_fields={security_hold: "true"})
│         # blocks approval chain
└── mc.post_memory(trail_event)
```

### fleet_chat(message, mention)
Agent communicates with fleet.

```
fleet_chat
├── mc.post_memory(board_id,
│     content=f"{agent}: {message}",
│     tags=["chat", f"mention:{mention}"])
├── irc.send("#fleet", f"<{agent}> {message}")
│
│ ELEVATED ADDITIONS:
├── events.emit("fleet.chat.message",
│     agent, message, mention)
├── if mention == "human" or mention == "po":
│   └── ntfy.send(topic="fleet-review",
│         title=f"Fleet chat from {agent}",
│         message=message)
├── if mention is specific agent:
│   └── mc.post_memory(
│         tags=[f"mention:{mention}"],
│         content=message)
│         # target sees in next heartbeat MESSAGES section
└── mc.post_memory(trail_event if task_id)
```

### fleet_task_create(title, description, agent_name, ...)
PM/agent creates a new task.

```
fleet_task_create
├── mc.create_task(board_id,
│     title, description, agent_name,
│     custom_fields={
│       task_type, task_stage, task_readiness,
│       story_points, parent_task, plan_id,
│       delivery_phase, requirement_verbatim,
│       auto_created, auto_reason,
│       contribution_type, contribution_target,
│     })
├── mc.post_comment(parent_task_id,
│     f"Subtask created: {title}")  # if parent exists
├── irc.send("#fleet",
│     f"[created] {title} → {agent_name or 'unassigned'}")
│
│ ELEVATED ADDITIONS:
├── if parent_task:
│   └── plane_sync.create_issue(
│         workspace, project,
│         title, description,
│         labels=[f"type:{task_type}", f"phase:{phase}"],
│         parent_issue=parent_plane_id)
├── events.emit("fleet.task.created",
│     task_id, creator, parent, task_type)
├── mc.post_memory(trail_event:
│     f"Task created by {agent}. Parent: {parent}")
└── if contribution_type:
    └── events.emit("fleet.contribution.opportunity_created",
          task_id, target_task=contribution_target, role=agent_name)
```

### fleet_approve(approval_id, decision, comment)
Fleet-ops approves or rejects.

```
fleet_approve
├── mc.update_approval(board_id, approval_id,
│     status=decision, comment=comment)
│
│ ELEVATED ADDITIONS:
├── if decision == "approved":
│   ├── mc.update_task(board_id, task_id,
│   │     status="done")
│   ├── mc.post_comment(board_id, task_id,
│   │     message=f"Approved by {agent}: {comment}",
│   │     type="approval")
│   ├── plane_sync.update_issue(status="done",
│   │     labels=["status:done"])
│   ├── irc.send("#reviews",
│   │     f"[approved] {task_title}")
│   ├── events.emit("fleet.approval.approved")
│   ├── mc.post_memory(trail_event: "approved")
│   ├── evaluate_parent(parent_task_id)
│   └── update_sprint_progress()
│
├── if decision == "rejected":
│   ├── mc.update_task(board_id, task_id,
│   │     status="in_progress",
│   │     custom_fields={
│   │       task_readiness: regressed_value,
│   │       task_stage: regressed_stage,
│   │     })
│   ├── mc.post_comment(board_id, task_id,
│   │     message=f"Rejected by {agent}: {comment}",
│   │     type="rejection")
│   ├── plane_sync.update_issue(status="in_progress",
│   │     labels=[f"readiness:{regressed}",
│   │             f"stage:{regressed_stage}"])
│   ├── irc.send("#reviews",
│   │     f"[rejected] {task_title}: {comment}")
│   ├── events.emit("fleet.approval.rejected")
│   ├── mc.post_memory(trail_event: "rejected")
│   └── doctor.signal_rejection(agent_name, task_id)
│       # repeated rejections → detection signal
│
└── mc.post_memory(trail_event)
```

### fleet_escalate(title, details)
Agent escalates to human.

```
fleet_escalate
├── mc.post_memory(board_id,
│     content=f"ESCALATION: {title}\n{details}",
│     tags=["escalation", "po-required"])
├── irc.send("#alerts",
│     f"[escalation] {agent}: {title}")
├── ntfy.send(topic="fleet-alert",
│     title=f"Escalation: {title}",
│     message=details,
│     priority="urgent",
│     tags=["rotating_light", "escalation"])
├── events.emit("fleet.escalation.raised")
└── mc.post_memory(trail_event if task_id)
```

### fleet_agent_status()
Returns fleet snapshot. Read-only, minimal tree.

```
fleet_agent_status
├── mc.list_agents()
├── mc.list_tasks(board_id)
├── mc.list_approvals(board_id)
└── return: agents with status, task counts, pending approvals
    (no side effects — read only)
```

### fleet_artifact_create(artifact_type, title)
Agent creates a structured artifact.

```
fleet_artifact_create
├── _check_stage_allowed("fleet_artifact_create", task_stage)
├── create artifact object with required fields for type
├── transpose.to_html(artifact_type, object)
│   └── render: markers + visual HTML + hidden data blob
├── if plane_issue_id:
│   └── plane_sync.update_issue(
│         description_html=prepend_artifact_html)
│
│ ELEVATED ADDITIONS:
├── artifact_tracker.check_completeness(type, object, phase)
│   └── returns: required_pct, overall_pct, suggested_readiness
├── events.emit("fleet.artifact.created",
│     type, task_id, completeness)
├── mc.post_comment(board_id, task_id,
│     f"Artifact created: {type} — {title}. "
│     f"Completeness: {pct}%",
│     type="artifact")
├── mc.post_memory(trail_event: "artifact_created")
└── if completeness.suggested_readiness > current_readiness:
    └── suggest readiness update (don't auto-change — PM/PO decides)
```

### fleet_artifact_update(artifact_type, field, value)
Agent updates a field of an existing artifact.

```
fleet_artifact_update
├── transpose.from_html(current_html)  # read current object
├── update object field (set or append)
├── transpose.to_html(type, updated_object)  # re-render
├── if plane_issue_id:
│   └── plane_sync.update_issue(
│         description_html=updated_html)
│
│ ELEVATED ADDITIONS:
├── artifact_tracker.check_completeness(type, object, phase)
├── events.emit("fleet.artifact.updated",
│     type, field, completeness)
├── mc.post_comment(board_id, task_id,
│     f"Artifact updated: {field}. Completeness: {pct}%",
│     type="progress")
└── mc.post_memory(trail_event: "artifact_updated")
```

### fleet_artifact_read(artifact_type)
Agent reads current artifact state. Read-only.

```
fleet_artifact_read
├── transpose.from_html(plane_description_html)
├── artifact_tracker.check_completeness(type, object, phase)
└── return: object + completeness + suggested_readiness
    (no side effects — read only)
```

### Plane Tools (6) — Minimal Trees (Direct API)

```
fleet_plane_status        → plane.list_issues() → return
fleet_plane_sprint        → plane.list_cycles() → return
fleet_plane_sync          → plane_sync.sync_task() → mc + plane updates
fleet_plane_create_issue  → plane.create_issue() → return
fleet_plane_comment       → plane.add_comment() → return
fleet_plane_update_issue  → plane.update_issue() → return
fleet_plane_list_modules  → plane.list_modules() → return
```

These are direct Plane API calls. They don't fire complex trees
because Plane operations are typically triggered by OTHER tools'
trees (fleet_task_complete includes plane_sync, fleet_artifact_create
includes Plane update). Direct Plane tools are for agents that need
to interact with Plane outside the normal task flow (technical writer
maintaining pages, PM checking sprint data).

### Remaining Current Tools

```
fleet_pause              → mc.post_memory("pause requested") → ntfy PO
fleet_notify_human       → ntfy.send(topic, title, message)
fleet_task_context       → context_assembly.assemble_task_context() → return
fleet_heartbeat_context  → context_assembly.assemble_heartbeat_context() → return
```

---

## 5 New Tools — Full Trees

### fleet_contribute(task_id, contribution_type, content)
Agent contributes to another agent's task.

```
fleet_contribute
├── mc.post_comment(target_task_id,
│     message=content,
│     type=contribution_type)        # typed comment
├── plane_sync.update_issue(
│     target_plane_issue_id,
│     comment=formatted_contribution)
├── context.update_target_task(
│     target_task_id,
│     contributions={type: content})  # target context gets updated
├── mc.update_task(
│     contribution_task_id,
│     status="done")                  # mark own contribution task done
├── events.emit("fleet.contribution.posted",
│     contributor=agent, target=target_task_id,
│     type=contribution_type)
├── mc.post_memory(
│     tags=["trail", f"task:{target_task_id}",
│           "contribution", contribution_type],
│     content=trail_event)
├── notify_task_owner(target_task_id)
│   └── mc.post_memory(
│         tags=[f"mention:{owner}"],
│         content=f"Contribution received: {type} from {agent}")
├── irc.send("#contributions",
│     f"[contribute] {agent} → {target_title}: {type}")
└── check_contribution_completeness(target_task_id)
    ├── get required contributions for phase
    ├── get received contributions
    ├── if all_required_received:
    │   ├── mc.post_memory(
    │   │     tags=[f"mention:project-manager"],
    │   │     content=f"All contributions received for {target_title}")
    │   └── events.emit("fleet.contribution.all_received")
    └── else: log pending contributions
```

### fleet_transfer(task_id, to_agent, context_summary)
Transfer task from one agent to another with context.

```
fleet_transfer
├── package_context = {
│     architect_inputs: [...],
│     qa_tests: [...],
│     security_reqs: [...],
│     current_artifacts: [...],
│     trail_summary: [...],
│   }
├── mc.update_task(board_id, task_id,
│     custom_fields={agent_name: to_agent})
├── mc.post_comment(board_id, task_id,
│     message=f"Transferred from {from_agent} to {to_agent}. "
│             f"Context: {context_summary}",
│     type="transfer")
├── context_writer.write_task_context(
│     to_agent, task_id,
│     include_transfer_package=package_context)
├── plane_sync.update_issue(
│     comment=f"Transferred to {to_agent}")
├── events.emit("fleet.task.transferred",
│     from_agent, to_agent, task_id, stage)
├── mc.post_memory(
│     tags=["trail", f"task:{task_id}", "transfer"],
│     content=trail_event)
├── irc.send("#fleet",
│     f"[transfer] {from_agent} → {to_agent}: {task_title}")
└── notify receiving agent:
    └── mc.post_memory(
          tags=[f"mention:{to_agent}"],
          content=f"Task transferred to you: {title}")
```

### fleet_request_input(task_id, from_role, question)
Request a specific role's input on a task.

```
fleet_request_input
├── mc.post_memory(board_id,
│     content=f"{agent} requesting {from_role} input: {question}",
│     tags=["chat", f"mention:{from_role}",
│           f"task:{task_id}"])
├── mc.post_comment(board_id, task_id,
│     message=f"@{from_role}: {question}",
│     type="input_request")
├── irc.send("#fleet",
│     f"[request] {agent} → @{from_role}: {question[:60]}")
├── events.emit("fleet.input.requested",
│     requester=agent, target_role=from_role, task_id=task_id)
├── check: does a contribution task already exist for this role?
│   ├── if no: suggest PM creates one
│   └── if yes: reference existing contribution task
└── mc.post_memory(trail_event)
```

### fleet_gate_request(task_id, gate_type, summary)
Request PO approval at a gate.

```
fleet_gate_request
├── mc.post_memory(board_id,
│     content=f"GATE REQUEST: {gate_type}\n"
│             f"Task: {task_title}\n"
│             f"Summary: {summary}",
│     tags=["gate", "po-required", gate_type,
│           f"task:{task_id}"])
├── irc.send("#gates",
│     f"[gate] {gate_type}: {task_title} — PO approval needed")
├── ntfy.send(topic="fleet-review",
│     title=f"Gate: {gate_type}",
│     message=f"Task: {task_title}\n{summary}",
│     priority="high")
├── mc.update_task(board_id, task_id,
│     custom_fields={gate_pending: gate_type})
├── events.emit("fleet.gate.requested",
│     gate_type, task_id, summary)
└── mc.post_memory(trail_event: "gate_requested")
```

### fleet_phase_advance(task_id, from_phase, to_phase, evidence)
Request delivery phase advancement.

```
fleet_phase_advance
├── phases.check_phase_standards(task, from_phase)
│   ├── if standards not met:
│   │   └── return error: f"Cannot advance: {gaps}"
│   └── if met: continue
├── mc.post_memory(board_id,
│     content=f"PHASE ADVANCE REQUEST: {from_phase} → {to_phase}\n"
│             f"Task: {task_title}\n"
│             f"Evidence: {evidence}",
│     tags=["gate", "phase-advance", "po-required",
│           f"task:{task_id}"])
├── irc.send("#gates",
│     f"[phase] {task_title}: {from_phase} → {to_phase}")
├── ntfy.send(topic="fleet-review",
│     title=f"Phase advance: {from_phase} → {to_phase}",
│     message=f"Task: {task_title}\n{evidence}",
│     priority="high")
├── events.emit("fleet.phase.advance_requested",
│     from_phase, to_phase, task_id, evidence)
└── mc.post_memory(trail_event: "phase_advance_requested")
    # PO decides — brain processes the decision in gate step
```

---

## Tree Execution Principles

### Parallel Where Possible
Operations in a tree that don't depend on each other run in parallel:
- mc.post_comment AND irc.send → parallel (independent)
- mc.create_approval AFTER mc.update_task → sequential (needs task in review first)
- plane_sync AFTER mc.update_task → sequential (needs new status)
- events.emit AND mc.post_memory → parallel (independent)

### Failure Isolation
Individual operations in a tree can fail without killing the tree:
- If irc.send fails → log, continue (IRC is notification, not critical)
- If plane_sync fails → queue for retry (Plane is display, not source of truth)
- If mc.update_task fails → STOP tree (MC is source of truth, must succeed)
- If ntfy fails → log, continue (notification, not critical)

Critical operations (mc.update_task, mc.create_approval) stop the tree
on failure. Non-critical operations (irc, ntfy, plane) log and continue.

### Trail Always Records
Every tree records a trail event. Even if other operations fail, the
trail event captures what was ATTEMPTED. This ensures the accountability
generator has data even for partially-executed trees.

---

## Which Role Uses Which Tools

| Tool | PM | Ops | Arch | DevSec | Eng | DevOps | QA | Writer | UX | Acct |
|------|:--:|:---:|:----:|:------:|:---:|:------:|:--:|:------:|:--:|:----:|
| fleet_read_context | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| fleet_task_accept | | | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | |
| fleet_task_progress | | | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | |
| fleet_commit | | | △ | ✓ | ✓ | ✓ | ✓ | △ | | |
| fleet_task_complete | | | △ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | |
| fleet_alert | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | | ✓ |
| fleet_chat | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| fleet_task_create | ✓ | | | | △ | | | | | |
| fleet_approve | | ✓ | | | | | | | | |
| fleet_agent_status | ✓ | ✓ | | | | | | | | |
| fleet_escalate | ✓ | ✓ | ✓ | ✓ | | | | | | |
| fleet_artifact_create | ✓ | | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| fleet_artifact_update | | | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | |
| fleet_contribute | | | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | |
| fleet_transfer | | | ✓ | | | | | | | |
| fleet_request_input | | | | | ✓ | ✓ | | | | |
| fleet_gate_request | ✓ | | | | | | | | | |
| fleet_phase_advance | ✓ | | | | | | | | | |
| fleet_plane_* | ✓ | | | | | | | ✓ | | |

✓ = primary user, △ = occasional/rare use

---

## Testing Requirements

For each tool:
- Tree fires all operations (happy path)
- Tree handles operation failure (critical stops, non-critical continues)
- Trail event always recorded
- Stage enforcement blocks inappropriate calls
- Phase-aware completeness checked on artifacts
- Parallel operations actually run in parallel
- Events emitted with correct data
- Plane sync fires when plane_issue_id exists
- Notification routing respects config

---

## Existing Infrastructure — Already Built

**CRITICAL CODE AWARENESS:** The tree execution engine ALREADY EXISTS.
Do not create new modules — evolve existing ones:

- `fleet/core/event_chain.py` — EventChain, EventSurface (INTERNAL,
  PUBLIC, CHANNEL, NOTIFY, PLANE, META), Event with required/optional
- `fleet/core/chain_runner.py` — ChainRunner that executes EventChains
  across surfaces with failure tolerance. PO quote in docstring.
- `fleet/core/smart_chains.py` — DispatchContext, pre-computed results,
  batch operations. PO quote in docstring about chains.

The elevation EVOLVES these modules — it doesn't replace them:
- chain_runner needs to support the new tool trees (more operations,
  contribution propagation, trail recording)
- event_chain needs new EventSurface types if needed (TRAIL, CONTRIBUTION?)
  or extend existing surfaces
- smart_chains needs new chain types (contribution_chain, review_chain,
  phase_advance_chain)

Also already built:
- `fleet/core/model_selection.py` — task-aware model/effort selection
  (opus for epics/large tasks, sonnet for routine, role-based)
- `fleet/core/task_scoring.py` — priority scoring for dispatch ordering
- `fleet/core/skill_enforcement.py` — required tool usage per task type

---

## Files Affected

| File | Change |
|------|--------|
| `fleet/mcp/tools.py` | Upgrade all 25 tool trees + add 5 new tools |
| `fleet/core/event_chain.py` | EVOLVE — new chain types for contributions, trails, phases |
| `fleet/core/chain_runner.py` | EVOLVE — support new operations, contribution propagation |
| `fleet/core/smart_chains.py` | EVOLVE — new pre-computed chain types |
| `fleet/tests/mcp/test_tool_trees.py` | NEW — tree execution tests per tool |