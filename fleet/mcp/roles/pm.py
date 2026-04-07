"""Project Manager role-specific group calls.

The PM drives the board. These group calls aggregate multiple operations
into single agent-facing tools. The PM calls ONE tool, the system
executes the tree.

Source: fleet-elevation/05 (PM role spec)
        tools-system-full-capability-map.md (PM group call inventory)

Group calls:
  pm_sprint_standup — aggregate sprint state, format report, post to board memory + IRC
  pm_contribution_check — verify all required contributions received before work stage
  (pm_epic_breakdown, pm_gate_route, pm_blocker_resolve — TO BE IMPLEMENTED)
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from fleet.mcp.context import FleetMCPContext

_ctx: FleetMCPContext | None = None


def _get_ctx() -> FleetMCPContext:
    global _ctx
    if _ctx is None:
        _ctx = FleetMCPContext.from_env()
    return _ctx


def register_tools(server: FastMCP) -> None:
    """Register PM-specific group calls."""

    @server.tool()
    async def pm_sprint_standup(sprint_id: str = "") -> dict:
        """Generate sprint standup summary — tasks by status, velocity, blockers, action items.

        One call aggregates sprint state from all tasks and produces a
        formatted standup report posted to board memory and IRC #sprint.

        Tree:
        1. Load all tasks for sprint → compute velocity metrics
        2. Identify blockers with resolution suggestions
        3. Identify contribution gaps (synergy matrix check)
        4. Format standup report
        5. Post to board memory [sprint, standup]
        6. Post to IRC #sprint
        7. Record trail

        Args:
            sprint_id: Sprint/plan ID. Empty = detect from most active sprint.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "project-manager"

        try:
            from fleet.core.velocity import compute_sprint_metrics
            from fleet.core.models import TaskStatus

            all_tasks = await ctx.mc.list_tasks(board_id)

            # Resolve sprint_id if not provided — find most active sprint
            if not sprint_id:
                plan_counts: dict[str, int] = {}
                for t in all_tasks:
                    pid = t.custom_fields.plan_id or t.custom_fields.sprint or ""
                    if pid:
                        active = 1 if t.status.value in ("in_progress", "review") else 0
                        plan_counts[pid] = plan_counts.get(pid, 0) + active
                if plan_counts:
                    sprint_id = max(plan_counts, key=plan_counts.get)

            if not sprint_id:
                return {"ok": True, "message": "No active sprint found.", "sprint_id": ""}

            # Compute metrics
            metrics = compute_sprint_metrics(all_tasks, sprint_id)

            # Identify blockers
            blockers = []
            for t in all_tasks:
                pid = t.custom_fields.plan_id or t.custom_fields.sprint or ""
                if pid == sprint_id and t.is_blocked:
                    blockers.append({
                        "id": t.id[:8],
                        "title": t.title[:50],
                        "agent": t.custom_fields.agent_name or "unassigned",
                        "blocked_by": t.blocked_by_task_ids[:3],
                    })

            # Identify contribution gaps
            contrib_gaps = []
            try:
                from fleet.core.contributions import check_contribution_completeness
                for t in all_tasks:
                    pid = t.custom_fields.plan_id or t.custom_fields.sprint or ""
                    cf = t.custom_fields
                    if (pid == sprint_id
                            and cf.task_stage in ("reasoning", "work")
                            and cf.agent_name):
                        received = []
                        try:
                            comments = await ctx.mc.list_comments(board_id, t.id)
                            for c in (comments or []):
                                cmsg = c.message if hasattr(c, 'message') else c.get("message", "")
                                if "**Contribution (" in cmsg:
                                    try:
                                        ts = cmsg.index("(") + 1
                                        te = cmsg.index(")")
                                        received.append(cmsg[ts:te])
                                    except (ValueError, IndexError):
                                        pass
                        except Exception:
                            pass

                        status = check_contribution_completeness(
                            t.id, cf.agent_name, cf.task_type or "task", received,
                        )
                        if not status.all_received and status.missing:
                            contrib_gaps.append({
                                "task": t.title[:40],
                                "task_id": t.id[:8],
                                "missing": status.missing,
                            })
            except Exception:
                pass

            # Format standup report
            report_lines = [
                f"## Sprint Standup — {sprint_id}",
                "",
                f"**Progress:** {metrics.done_tasks}/{metrics.total_tasks} tasks "
                f"({metrics.completion_pct:.0f}%)",
                f"**Story Points:** {metrics.done_story_points}/{metrics.total_story_points} SP",
                f"**In Progress:** {metrics.in_progress_tasks} | "
                f"**In Review:** {metrics.review_tasks} | "
                f"**Inbox:** {metrics.inbox_tasks}",
            ]

            if metrics.blocked_tasks:
                report_lines.append(f"**Blocked:** {metrics.blocked_tasks}")

            if blockers:
                report_lines.append("")
                report_lines.append("### Blockers")
                for b in blockers[:5]:
                    report_lines.append(
                        f"- {b['title']} ({b['id']}) — {b['agent']} — "
                        f"blocked by {', '.join(str(x)[:8] for x in b['blocked_by'][:2])}"
                    )

            if contrib_gaps:
                report_lines.append("")
                report_lines.append("### Missing Contributions")
                for g in contrib_gaps[:5]:
                    report_lines.append(
                        f"- {g['task']} ({g['task_id']}): missing {', '.join(g['missing'])}"
                    )

            if metrics.is_complete:
                report_lines.append("")
                report_lines.append("### **SPRINT COMPLETE**")

            report = "\n".join(report_lines)

            # Post to board memory
            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=report,
                    tags=["sprint", "standup", f"plan:{sprint_id}"],
                    source=agent,
                )
            except Exception:
                pass

            # Post to IRC #sprint
            try:
                irc_summary = (
                    f"[sprint] {sprint_id}: {metrics.done_tasks}/{metrics.total_tasks} done "
                    f"({metrics.completion_pct:.0f}%), {metrics.done_story_points} SP"
                )
                if metrics.blocked_tasks:
                    irc_summary += f" | {metrics.blocked_tasks} blocked"
                await ctx.irc.notify("#sprint", irc_summary)
            except Exception:
                pass

            # Trail
            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=f"**[trail]** Sprint standup for {sprint_id} by {agent}",
                    tags=["trail", f"plan:{sprint_id}", "standup"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True,
                "sprint_id": sprint_id,
                "completion_pct": round(metrics.completion_pct),
                "done": metrics.done_tasks,
                "total": metrics.total_tasks,
                "story_points": f"{metrics.done_story_points}/{metrics.total_story_points}",
                "blocked": metrics.blocked_tasks,
                "contribution_gaps": len(contrib_gaps),
                "is_complete": metrics.is_complete,
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def pm_contribution_check(task_id: str) -> dict:
        """Check if a task has all required contributions before advancing to work stage.

        One call checks the synergy matrix, reads task comments for received
        contributions, identifies gaps, and suggests actions for missing ones.

        Tree:
        1. Read task type and assigned agent
        2. Load synergy matrix for required contributions
        3. Read task comments for received contributions
        4. Compute completeness
        5. List gaps with suggested fleet_task_create commands
        6. Record trail

        Args:
            task_id: Task to check contributions for.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "project-manager"

        try:
            task = await ctx.mc.get_task(board_id, task_id)
            cf = task.custom_fields
            target_agent = cf.agent_name or ""
            task_type = cf.task_type or "task"

            # Gather received contributions from comments
            received_types = []
            try:
                comments = await ctx.mc.list_comments(board_id, task_id)
                for c in (comments or []):
                    cmsg = c.message if hasattr(c, 'message') else c.get("message", "")
                    if "**Contribution (" in cmsg:
                        try:
                            ts = cmsg.index("(") + 1
                            te = cmsg.index(")")
                            received_types.append(cmsg[ts:te])
                        except (ValueError, IndexError):
                            pass
            except Exception:
                pass

            # Check completeness
            from fleet.core.contributions import (
                check_contribution_completeness,
                load_synergy_matrix,
            )
            status = check_contribution_completeness(
                task_id=task_id,
                target_agent=target_agent,
                task_type=task_type,
                received_types=received_types,
            )

            # Build suggested actions for missing contributions
            suggested_actions = []
            if status.missing:
                matrix = load_synergy_matrix()
                specs = matrix.get(target_agent, [])
                for missing_type in status.missing:
                    provider_role = ""
                    for spec in specs:
                        if spec.contribution_type == missing_type:
                            provider_role = spec.role
                            break

                    if provider_role:
                        suggested_actions.append({
                            "missing": missing_type,
                            "from_role": provider_role,
                            "action": (
                                f"fleet_task_create(title='{missing_type} for {task.title[:30]}', "
                                f"agent_name='{provider_role}', task_type='subtask', "
                                f"parent_task='{task_id[:8]}')"
                            ),
                        })

            # Trail
            try:
                gap_text = f"Missing: {', '.join(status.missing)}" if status.missing else "ALL RECEIVED"
                await ctx.mc.post_memory(
                    board_id,
                    content=(
                        f"**[trail]** Contribution check for task:{task_id[:8]} by {agent}: "
                        f"{len(status.received)}/{len(status.required)} received. {gap_text}"
                    ),
                    tags=["trail", f"task:{task_id}", "contribution_check"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True,
                "task_id": task_id,
                "task_title": task.title,
                "target_agent": target_agent,
                "required": status.required,
                "received": status.received,
                "missing": status.missing,
                "all_received": status.all_received,
                "completeness_pct": status.completeness_pct,
                "suggested_actions": suggested_actions,
                "ready_for_work": status.all_received,
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def pm_epic_breakdown(task_id: str) -> dict:
        """Analyze an epic and prepare context for breaking it into subtasks.

        Reads the epic's requirement, identifies subtask candidates with
        agent assignments, dependencies, and story points.

        Args:
            task_id: Epic to break down.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "project-manager"

        try:
            task = await ctx.mc.get_task(board_id, task_id)
            cf = task.custom_fields

            breakdown_guide = (
                f"## Epic Breakdown: {task.title}\n\n"
                f"**Verbatim:** {cf.requirement_verbatim or '(not set)'}\n"
                f"**Phase:** {cf.delivery_phase or 'unknown'}\n\n"
                "### For each subtask, set ALL fields:\n"
                "- title, agent_name, task_type, story_points, dependencies\n"
                "- task_stage (based on clarity), task_readiness, delivery_phase\n"
                "- parent_task (link to this epic)\n\n"
                "### Typical structure:\n"
                "```\n"
                f"Epic: {task.title}\n"
                "├── Design (architect) — analysis/reasoning\n"
                "├── Implement (engineer) — depends_on: [design]\n"
                "├── Tests (qa-engineer) — depends_on: [design]\n"
                "├── Security (devsecops) — parallel with design\n"
                "└── Docs (writer) — depends_on: [implement]\n"
                "```\n\n"
                "Create each via fleet_task_create. Post breakdown summary on epic."
            )

            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=f"**[trail]** Epic breakdown started for task:{task_id[:8]} by {agent}",
                    tags=["trail", f"task:{task_id}", "epic_breakdown"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True, "task_id": task_id, "task_title": task.title,
                "task_type": cf.task_type or "epic",
                "verbatim": cf.requirement_verbatim or "",
                "breakdown_guide": breakdown_guide,
                "next_step": "Identify subtasks, create each via fleet_task_create with ALL fields.",
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def pm_gate_route(task_id: str, gate_type: str = "readiness_90") -> dict:
        """Package a gate request with full context for PO decision.

        Gathers task state, contributions, readiness to produce a
        comprehensive gate request.

        Args:
            task_id: Task at gate threshold.
            gate_type: Gate type (readiness_90, phase_advance).
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "project-manager"

        try:
            task = await ctx.mc.get_task(board_id, task_id)
            cf = task.custom_fields

            # Check contributions
            received_types = []
            try:
                comments = await ctx.mc.list_comments(board_id, task_id)
                for c in (comments or []):
                    cmsg = c.message if hasattr(c, 'message') else c.get("message", "")
                    if "**Contribution (" in cmsg:
                        try:
                            received_types.append(cmsg[cmsg.index("(")+1:cmsg.index(")")])
                        except (ValueError, IndexError):
                            pass
            except Exception:
                pass

            contrib_summary = ", ".join(received_types) if received_types else "none"

            gate_summary = (
                f"Task: {task.title}\n"
                f"Agent: {cf.agent_name or 'unassigned'}\n"
                f"Readiness: {cf.task_readiness or 0}%\n"
                f"Phase: {cf.delivery_phase or 'unknown'}\n"
                f"Contributions: {contrib_summary}"
            )

            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=f"**[trail]** Gate route for task:{task_id[:8]} by {agent}. Type: {gate_type}",
                    tags=["trail", f"task:{task_id}", "gate_route"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True, "task_id": task_id, "task_title": task.title,
                "gate_type": gate_type, "gate_summary": gate_summary,
                "next_step": f"Call fleet_gate_request(task_id='{task_id}', gate_type='{gate_type}', summary='...')",
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def pm_blocker_resolve(task_id: str) -> dict:
        """Evaluate a blocked task and suggest resolution options.

        Rule: Never more than 2 active blockers at once.

        Args:
            task_id: Blocked task to resolve.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "project-manager"

        try:
            task = await ctx.mc.get_task(board_id, task_id)
            all_tasks = await ctx.mc.list_tasks(board_id)
            total_blocked = sum(1 for t in all_tasks if t.is_blocked)

            # Read blocker context
            blocker_reason = ""
            try:
                comments = await ctx.mc.list_comments(board_id, task_id)
                for c in (comments or []):
                    cmsg = c.message if hasattr(c, 'message') else c.get("message", "")
                    if "blocked" in cmsg.lower() or "blocker" in cmsg.lower():
                        blocker_reason = cmsg[:300]
                        break
            except Exception:
                pass

            options = [
                "Reassign — can another agent handle the dependency?",
                "Split — separate non-blocked and blocked parts",
                "Remove dependency — is the dep still necessary?",
                "Escalate — needs PO decision? fleet_escalate",
                "Create subtask — resolve the blocker as a new task",
            ]

            warning = ""
            if total_blocked > 2:
                warning = f"Fleet has {total_blocked} active blockers (limit: 2). RESOLVE URGENTLY."

            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=f"**[trail]** Blocker analysis for task:{task_id[:8]} by {agent}. Fleet blockers: {total_blocked}",
                    tags=["trail", f"task:{task_id}", "blocker_resolve"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True, "task_id": task_id, "task_title": task.title,
                "blocked_by": task.blocked_by_task_ids,
                "reason": blocker_reason or "(not found)",
                "fleet_blocked_count": total_blocked,
                "warning": warning,
                "resolution_options": options,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
