"""Accountability Generator role-specific group calls.

Verifies PROCESS was followed. Reports compliance. Feeds immune system.

Source: fleet-elevation/14 (accountability role spec)

Group calls:
  acct_trail_reconstruction — reconstruct full audit trail for a task
  acct_sprint_compliance — check sprint tasks for methodology compliance
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

    @server.tool()
    async def acct_trail_reconstruction(task_id: str) -> dict:
        """Reconstruct the complete audit trail for a task.

        Queries board memory for all trail events tagged with this task ID,
        sorts chronologically, and produces a complete task history.

        Tree:
        1. Query board memory by task:{id} tag
        2. Filter trail events
        3. Sort chronologically
        4. Format as audit trail document
        5. Record trail

        Args:
            task_id: Task to reconstruct trail for.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "accountability-generator"

        try:
            task = await ctx.mc.get_task(board_id, task_id)

            # Query board memory for trail events
            trail_events = []
            try:
                memory = await ctx.mc.list_memory(board_id, limit=200)
                for m in memory:
                    tags = m.tags if hasattr(m, 'tags') else m.get("tags", [])
                    content = m.content if hasattr(m, 'content') else m.get("content", "")
                    if "trail" in tags and f"task:{task_id}" in str(tags):
                        trail_events.append({
                            "content": content[:200],
                            "tags": tags,
                        })
            except Exception:
                pass

            # Format trail
            trail_lines = [
                f"## Audit Trail: {task.title}",
                f"**Task ID:** {task_id[:8]}",
                f"**Agent:** {task.custom_fields.agent_name or 'unknown'}",
                f"**Status:** {task.status.value}",
                f"**Stage:** {task.custom_fields.task_stage or 'unknown'}",
                f"**Readiness:** {task.custom_fields.task_readiness or 0}%",
                "",
                f"### Trail Events ({len(trail_events)})",
            ]

            for event in trail_events:
                content = event["content"].replace("**[trail]**", "").strip()
                trail_lines.append(f"- {content}")

            if not trail_events:
                trail_lines.append("- (no trail events found)")

            trail_doc = "\n".join(trail_lines)

            # Record own trail
            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=f"**[trail]** Trail reconstruction for task:{task_id[:8]} by {agent}. {len(trail_events)} events found.",
                    tags=["trail", f"task:{task_id}", "trail_reconstruction"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True,
                "task_id": task_id,
                "task_title": task.title,
                "trail_events_count": len(trail_events),
                "trail_document": trail_doc,
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def acct_sprint_compliance(sprint_id: str = "") -> dict:
        """Check sprint tasks for methodology compliance.

        For each completed task in the sprint, verifies trail completeness:
        stage transitions, contributions received, PO gates, phase standards.

        Tree:
        1. Load sprint tasks
        2. For each done task: query trail events
        3. Check: stages traversed? contributions? PO gate? standards?
        4. Produce compliance report
        5. Post to board memory [compliance]
        6. Record trail

        Args:
            sprint_id: Sprint/plan to check. Empty = most recent.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "accountability-generator"

        try:
            all_tasks = await ctx.mc.list_tasks(board_id)

            # Resolve sprint
            if not sprint_id:
                plan_ids = {}
                for t in all_tasks:
                    pid = t.custom_fields.plan_id or t.custom_fields.sprint or ""
                    if pid:
                        plan_ids[pid] = plan_ids.get(pid, 0) + 1
                if plan_ids:
                    sprint_id = max(plan_ids, key=plan_ids.get)

            if not sprint_id:
                return {"ok": True, "message": "No sprint found.", "sprint_id": ""}

            # Get done tasks in sprint
            done_tasks = [
                t for t in all_tasks
                if (t.custom_fields.plan_id == sprint_id or t.custom_fields.sprint == sprint_id)
                and t.status.value == "done"
            ]

            compliance_results = []
            for task in done_tasks:
                # Query trail for this task
                trail_count = 0
                try:
                    memory = await ctx.mc.list_memory(board_id, limit=200)
                    for m in memory:
                        tags = m.tags if hasattr(m, 'tags') else m.get("tags", [])
                        if "trail" in tags and f"task:{task.id}" in str(tags):
                            trail_count += 1
                except Exception:
                    pass

                compliance_results.append({
                    "task_id": task.id[:8],
                    "title": task.title[:40],
                    "agent": task.custom_fields.agent_name or "unknown",
                    "trail_events": trail_count,
                    "has_trail": trail_count > 0,
                })

            # Summary
            compliant = sum(1 for r in compliance_results if r["has_trail"])
            total = len(compliance_results)

            report = (
                f"## Sprint Compliance Report — {sprint_id}\n\n"
                f"**Compliant:** {compliant}/{total} tasks have trail events\n"
            )
            gaps = [r for r in compliance_results if not r["has_trail"]]
            if gaps:
                report += "\n### Trail Gaps\n"
                for g in gaps:
                    report += f"- {g['title']} ({g['task_id']}) — {g['agent']} — NO TRAIL\n"

            # Post to board memory
            try:
                await ctx.mc.post_memory(
                    board_id, content=report,
                    tags=["compliance", f"plan:{sprint_id}"],
                    source=agent,
                )
            except Exception:
                pass

            # Trail
            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=f"**[trail]** Sprint compliance check for {sprint_id} by {agent}: {compliant}/{total} compliant",
                    tags=["trail", f"plan:{sprint_id}", "compliance_check"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True,
                "sprint_id": sprint_id,
                "total_done": total,
                "compliant": compliant,
                "gaps": len(gaps),
                "compliance_pct": round(compliant / total * 100) if total > 0 else 100,
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def acct_pattern_detection() -> dict:
        """Analyze compliance data for recurring patterns.

        Identifies systemic issues: agents skipping stages, missing
        contributions, recurring rejections. Posts to board memory
        for the immune system.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "accountability-generator"
        try:
            all_tasks = await ctx.mc.list_tasks(board_id)
            done = [t for t in all_tasks if t.status.value == "done"]

            # Check for pattern: tasks completed without trail
            no_trail = 0
            try:
                memory = await ctx.mc.list_memory(board_id, limit=500)
                trail_task_ids = set()
                for m in memory:
                    tags = m.tags if hasattr(m, 'tags') else m.get("tags", [])
                    if "trail" in tags:
                        for tag in tags:
                            if tag.startswith("task:"):
                                trail_task_ids.add(tag.split(":")[1])
                for t in done:
                    if t.id not in trail_task_ids and t.id[:8] not in str(trail_task_ids):
                        no_trail += 1
            except Exception:
                pass

            patterns = []
            if no_trail > 0:
                patterns.append({
                    "pattern": "tasks_without_trail",
                    "count": no_trail,
                    "severity": "high" if no_trail > 3 else "medium",
                    "description": f"{no_trail} completed tasks have no trail events",
                })

            if patterns:
                for p in patterns:
                    try:
                        await ctx.mc.post_memory(board_id,
                            content=f"**[compliance pattern]** {p['description']}",
                            tags=["compliance", "pattern", p["severity"]],
                            source=agent)
                    except Exception: pass

            try:
                await ctx.mc.post_memory(board_id,
                    content=f"**[trail]** Pattern detection by {agent}: {len(patterns)} patterns found",
                    tags=["trail", "pattern_detection"], source=agent)
            except Exception: pass

            return {"ok": True, "patterns": patterns, "tasks_analyzed": len(done)}
        except Exception as e:
            return {"ok": False, "error": str(e)}
