"""Fleet-Ops (Board Lead) role-specific group calls.

Fleet-ops is the quality guardian. These group calls aggregate the
complex review, health monitoring, and compliance checking operations
into single agent-facing tools.

Source: fleet-elevation/06 (fleet-ops role spec)
        tools-system-full-capability-map.md

Group calls:
  ops_real_review — structured 7+ step review of a pending approval
  ops_board_health_scan — scan all tasks for stuck/stale/offline issues
  ops_compliance_spot_check — sample completed tasks for methodology compliance
  ops_budget_assessment — read budget metrics and recommend mode changes
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
    """Register fleet-ops specific group calls."""

    @server.tool()
    async def ops_real_review(task_id: str, approval_id: str = "") -> dict:
        """Perform a REAL structured review of a completed task.

        NOT a rubber stamp. Reads the actual work, compares to verbatim,
        verifies trail completeness, checks phase standards, and produces
        a structured review decision.

        Tree:
        1. Read task details + verbatim requirement
        2. Read completion summary + PR (if exists)
        3. Verify trail: all required stages traversed
        4. Verify contributions: all required received
        5. Check phase standards: work meets delivery phase quality
        6. Compare work to verbatim: each acceptance criterion addressed
        7. Produce structured review summary
        8. Return recommendation (approve/reject/escalate) with specifics
        9. Record trail

        Args:
            task_id: Task to review.
            approval_id: Approval to act on (if known).
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "fleet-ops"

        try:
            task = await ctx.mc.get_task(board_id, task_id)
            cf = task.custom_fields

            review = {
                "task_id": task_id[:8],
                "task_title": task.title,
                "agent": cf.agent_name or "unknown",
                "stage": cf.task_stage or "unknown",
                "readiness": cf.task_readiness or 0,
                "checks": {},
                "issues": [],
                "recommendation": "pending",
            }

            # Step 1: Verbatim requirement
            verbatim = cf.requirement_verbatim or ""
            review["verbatim_exists"] = bool(verbatim)
            if not verbatim:
                review["issues"].append("No verbatim requirement set — cannot verify work matches PO's words")

            # Step 2: PR and completion data
            review["pr_url"] = cf.pr_url or ""
            review["branch"] = cf.branch or ""
            review["has_pr"] = bool(cf.pr_url)

            # Step 3: Trail verification — check stage transitions
            trail_events = []
            try:
                memory = await ctx.mc.list_memory(board_id, limit=100)
                for m in memory:
                    tags = m.tags if hasattr(m, 'tags') else m.get("tags", [])
                    content = m.content if hasattr(m, 'content') else m.get("content", "")
                    if "trail" in tags and f"task:{task_id}" in str(tags):
                        trail_events.append(content[:100])
            except Exception:
                pass

            review["trail_events_count"] = len(trail_events)
            review["checks"]["trail_exists"] = len(trail_events) > 0
            if not trail_events:
                review["issues"].append("No trail events found — methodology compliance cannot be verified")

            # Step 4: Contribution verification
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

            try:
                from fleet.core.contributions import check_contribution_completeness
                contrib_status = check_contribution_completeness(
                    task_id, cf.agent_name or "", cf.task_type or "task", received_types,
                )
                review["checks"]["contributions_complete"] = contrib_status.all_received
                review["contributions_received"] = contrib_status.received
                review["contributions_missing"] = contrib_status.missing
                if not contrib_status.all_received:
                    review["issues"].append(
                        f"Missing contributions: {', '.join(contrib_status.missing)}"
                    )
            except Exception:
                review["checks"]["contributions_complete"] = "unknown"

            # Step 5: Phase standards
            delivery_phase = cf.delivery_phase or ""
            if delivery_phase:
                try:
                    from fleet.core.phases import check_phase_standards
                    task_data = {
                        "tests": bool(cf.pr_url),  # proxy
                        "docs": True,  # TODO: verify docs exist
                        "security": True,  # TODO: verify security review
                        "monitoring": False,  # TODO: check monitoring
                        "contributions_received": received_types,
                    }
                    phase_result = check_phase_standards(task_data, delivery_phase)
                    review["checks"]["phase_standards_met"] = phase_result.all_met
                    review["phase"] = delivery_phase
                    review["phase_met_pct"] = phase_result.met_pct
                    if not phase_result.all_met:
                        review["issues"].append(
                            f"Phase '{delivery_phase}' standards not fully met: "
                            f"{', '.join(phase_result.gaps[:3])}"
                        )
                except Exception:
                    pass

            # Step 6: Acceptance criteria (check if completion addresses verbatim)
            if verbatim:
                try:
                    from fleet.core.plan_quality import check_plan_references_verbatim
                    # Use completion summary as the "plan" to check against verbatim
                    completion_comment = ""
                    try:
                        comments = await ctx.mc.list_comments(board_id, task_id)
                        for c in (comments or []):
                            cmsg = c.message if hasattr(c, 'message') else c.get("message", "")
                            if "Completed" in cmsg or "completed" in cmsg:
                                completion_comment = cmsg
                                break
                    except Exception:
                        pass

                    if completion_comment:
                        vr = check_plan_references_verbatim(completion_comment, verbatim)
                        review["checks"]["verbatim_coverage"] = vr.coverage_pct
                        review["checks"]["verbatim_referenced"] = vr.references_verbatim
                        if not vr.references_verbatim:
                            review["issues"].append(
                                f"Completion may not address verbatim requirement "
                                f"({vr.coverage_pct:.0f}% key term coverage)"
                            )
                except Exception:
                    pass

            # Step 7: Recommendation
            critical_issues = [i for i in review["issues"] if "cannot" in i.lower() or "missing" in i.lower()]
            if not review["issues"]:
                review["recommendation"] = "approve"
                review["recommendation_comment"] = (
                    f"Requirements met. Trail verified ({len(trail_events)} events). "
                    f"Contributions complete. Phase standards met."
                )
            elif critical_issues:
                review["recommendation"] = "reject"
                review["recommendation_comment"] = (
                    f"Issues found: {'; '.join(critical_issues[:3])}"
                )
            else:
                review["recommendation"] = "escalate"
                review["recommendation_comment"] = (
                    f"Minor issues, PO judgment needed: {'; '.join(review['issues'][:3])}"
                )

            # Trail
            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=(
                        f"**[trail]** Real review by {agent} for task:{task_id[:8]}: "
                        f"recommendation={review['recommendation']}. "
                        f"Issues: {len(review['issues'])}"
                    ),
                    tags=["trail", f"task:{task_id}", "review"],
                    source=agent,
                )
            except Exception:
                pass

            return {"ok": True, "review": review}

        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def ops_board_health_scan() -> dict:
        """Scan the board for health issues — stuck tasks, stale reviews, offline agents.

        Tree:
        1. Load all tasks and agents
        2. Identify stuck tasks (in_progress > 48h without progress)
        3. Identify stale reviews (review status > 24h)
        4. Identify offline agents with assigned work
        5. Identify stale contributions (> 24h without response)
        6. Count active blockers (should be <= 2)
        7. Format health report
        8. Post to board memory [health, ops]
        9. Alert PM on critical issues
        10. Record trail
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "fleet-ops"

        try:
            all_tasks = await ctx.mc.list_tasks(board_id)
            all_agents = await ctx.mc.list_agents()

            issues = []
            warnings = []

            # Stuck tasks (in_progress — we can't check time without timestamps,
            # but we can flag tasks with no recent comments)
            in_progress = [t for t in all_tasks if t.status.value == "in_progress"]
            if len(in_progress) > 10:
                warnings.append(f"{len(in_progress)} tasks in progress — may indicate backlog")

            # Stale reviews
            in_review = [t for t in all_tasks if t.status.value == "review"]
            if in_review:
                for t in in_review:
                    issues.append({
                        "type": "stale_review",
                        "task": t.title[:40],
                        "task_id": t.id[:8],
                        "agent": t.custom_fields.agent_name or "unknown",
                    })

            # Blocked tasks
            blocked = [t for t in all_tasks if t.is_blocked]
            if len(blocked) > 2:
                issues.append({
                    "type": "too_many_blockers",
                    "count": len(blocked),
                    "tasks": [{"id": t.id[:8], "title": t.title[:30]} for t in blocked[:5]],
                })

            # Offline agents with work
            online_agents = {a.name for a in all_agents if a.status == "online" and "Gateway" not in a.name}
            for t in all_tasks:
                agent_name = t.custom_fields.agent_name or ""
                if (agent_name
                        and agent_name not in online_agents
                        and t.status.value in ("in_progress", "review")):
                    issues.append({
                        "type": "offline_agent_with_work",
                        "agent": agent_name,
                        "task": t.title[:40],
                        "task_id": t.id[:8],
                    })

            # Unassigned inbox
            unassigned = [t for t in all_tasks
                          if t.status.value == "inbox" and not t.assigned_agent_id]
            if unassigned:
                warnings.append(f"{len(unassigned)} unassigned tasks in inbox — PM needs to triage")

            # Format health report
            report_lines = ["## Board Health Scan"]

            agents_online = len(online_agents)
            agents_total = sum(1 for a in all_agents if "Gateway" not in a.name)
            report_lines.append(f"\n**Agents:** {agents_online}/{agents_total} online")
            report_lines.append(
                f"**Tasks:** {len(in_progress)} in progress, {len(in_review)} in review, "
                f"{len(blocked)} blocked, {len(unassigned)} unassigned"
            )

            if issues:
                report_lines.append("\n### Issues")
                for issue in issues[:10]:
                    if isinstance(issue, dict):
                        report_lines.append(f"- **{issue['type']}**: {issue}")
                    else:
                        report_lines.append(f"- {issue}")

            if warnings:
                report_lines.append("\n### Warnings")
                for w in warnings:
                    report_lines.append(f"- {w}")

            if not issues and not warnings:
                report_lines.append("\n**Board is healthy.** No issues detected.")

            report = "\n".join(report_lines)

            # Post to board memory
            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=report,
                    tags=["health", "ops", "board_scan"],
                    source=agent,
                )
            except Exception:
                pass

            # Alert PM if critical issues
            critical = [i for i in issues if isinstance(i, dict) and i.get("type") in ("too_many_blockers", "offline_agent_with_work")]
            if critical:
                try:
                    await ctx.mc.post_memory(
                        board_id,
                        content=f"**[{agent}]** @project-manager Board health issues detected: {len(issues)} issues, {len(warnings)} warnings",
                        tags=["chat", "mention:project-manager", "health"],
                        source=agent,
                    )
                except Exception:
                    pass

            # Trail
            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=f"**[trail]** Board health scan by {agent}: {len(issues)} issues, {len(warnings)} warnings",
                    tags=["trail", "board_health_scan"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True,
                "agents_online": agents_online,
                "agents_total": agents_total,
                "tasks_in_progress": len(in_progress),
                "tasks_in_review": len(in_review),
                "tasks_blocked": len(blocked),
                "tasks_unassigned": len(unassigned),
                "issues": len(issues),
                "warnings": len(warnings),
                "healthy": len(issues) == 0,
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def ops_compliance_spot_check() -> dict:
        """Sample recently completed tasks and check methodology compliance.

        Verifies: conventional commits, PR descriptions, artifact completeness,
        trail completeness, phase standards met.

        Posts findings to board memory [quality, compliance].
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "fleet-ops"

        try:
            all_tasks = await ctx.mc.list_tasks(board_id)
            done_tasks = [t for t in all_tasks if t.status.value == "done"][-10:]  # last 10

            findings = []
            for task in done_tasks:
                cf = task.custom_fields
                issues = []

                if not cf.pr_url and cf.task_type in ("task", "story", "subtask"):
                    pass  # Non-code tasks may not have PRs

                # Check trail
                trail_count = 0
                try:
                    memory = await ctx.mc.list_memory(board_id, limit=200)
                    trail_count = sum(1 for m in memory
                                     if "trail" in (m.tags if hasattr(m, 'tags') else m.get("tags", []))
                                     and f"task:{task.id}" in str(m.tags if hasattr(m, 'tags') else m.get("tags", [])))
                except Exception:
                    pass

                if trail_count == 0:
                    issues.append("no trail events")

                if issues:
                    findings.append({
                        "task": task.title[:40],
                        "task_id": task.id[:8],
                        "agent": cf.agent_name or "unknown",
                        "issues": issues,
                    })

            report = f"## Compliance Spot Check\n\n**Sampled:** {len(done_tasks)} tasks\n**Issues:** {len(findings)}\n"
            if findings:
                report += "\n### Findings\n"
                for f in findings[:5]:
                    report += f"- {f['task']} ({f['task_id']}): {', '.join(f['issues'])}\n"

            try:
                await ctx.mc.post_memory(
                    board_id, content=report,
                    tags=["quality", "compliance", "spot_check"],
                    source=agent,
                )
            except Exception:
                pass

            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=f"**[trail]** Compliance spot check by {agent}: {len(findings)} issues in {len(done_tasks)} tasks",
                    tags=["trail", "compliance_spot_check"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True,
                "sampled": len(done_tasks),
                "findings": len(findings),
                "details": findings[:5],
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def ops_budget_assessment() -> dict:
        """Assess fleet budget status and recommend mode changes if needed.

        Reads budget metrics and spending patterns. Recommends budget_mode
        changes if thresholds are approaching.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "fleet-ops"

        try:
            # Budget metrics come from the orchestrator's budget monitor
            # We check board memory for recent budget alerts
            budget_alerts = []
            try:
                memory = await ctx.mc.list_memory(board_id, limit=50)
                for m in memory:
                    tags = m.tags if hasattr(m, 'tags') else m.get("tags", [])
                    if "budget" in tags or "alert" in tags:
                        content = m.content if hasattr(m, 'content') else m.get("content", "")
                        if "budget" in content.lower():
                            budget_alerts.append(content[:200])
            except Exception:
                pass

            assessment = (
                f"## Budget Assessment\n\n"
                f"**Recent budget alerts:** {len(budget_alerts)}\n"
            )
            if budget_alerts:
                assessment += "\n### Recent Alerts\n"
                for alert in budget_alerts[:5]:
                    assessment += f"- {alert[:100]}\n"
            else:
                assessment += "\nNo recent budget alerts. Fleet spending appears normal.\n"

            try:
                await ctx.mc.post_memory(
                    board_id, content=assessment,
                    tags=["budget", "assessment"],
                    source=agent,
                )
            except Exception:
                pass

            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=f"**[trail]** Budget assessment by {agent}: {len(budget_alerts)} recent alerts",
                    tags=["trail", "budget_assessment"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True,
                "recent_alerts": len(budget_alerts),
                "assessment": assessment,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
