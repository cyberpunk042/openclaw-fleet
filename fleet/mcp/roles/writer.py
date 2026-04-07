"""Technical Writer role-specific group calls.

Documentation as a LIVING SYSTEM. Complements architect, UX, and engineer.

Source: fleet-elevation/12 (writer role spec)

Group calls:
  writer_doc_contribution — produce documentation_outline for a task
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
    async def writer_doc_contribution(task_id: str) -> dict:
        """Prepare context for producing a documentation_outline contribution.

        Args:
            task_id: Target task to contribute documentation outline for.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "technical-writer"

        try:
            task = await ctx.mc.get_task(board_id, task_id)
            cf = task.custom_fields

            template = (
                f"## Documentation Outline for: {task.title}\n\n"
                f"**Phase:** {cf.delivery_phase or 'unknown'}\n\n"
                "### Expected Documentation:\n"
                "1. **What** — what does this feature/change do?\n"
                "2. **Setup** — how to install/configure\n"
                "3. **Usage** — how to use it (with examples)\n"
                "4. **API** — endpoint/function documentation (if applicable)\n"
                "5. **Troubleshooting** — common issues and solutions\n\n"
                "After producing outline, call:\n"
                "fleet_contribute(task_id, 'documentation_outline', your_outline)"
            )

            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=f"**[trail]** Doc contribution started for task:{task_id[:8]} by {agent}",
                    tags=["trail", f"task:{task_id}", "doc_contribution"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True, "task_id": task_id, "task_title": task.title,
                "template": template,
                "next_step": "Produce documentation outline and call fleet_contribute.",
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def writer_staleness_scan() -> dict:
        """Scan for stale documentation — recently completed features without docs.

        Compares completed tasks to documentation state.
        For fully autonomous mode with Plane connected.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "technical-writer"
        try:
            all_tasks = await ctx.mc.list_tasks(board_id)
            done_tasks = [t for t in all_tasks if t.status.value == "done"][-20:]
            # Identify tasks that may need documentation
            needs_docs = [
                {"task": t.title[:40], "task_id": t.id[:8], "agent": t.custom_fields.agent_name or "unknown"}
                for t in done_tasks
                if t.custom_fields.task_type in ("story", "epic", "task")
            ]
            try:
                await ctx.mc.post_memory(board_id,
                    content=f"**[trail]** Staleness scan by {agent}: {len(needs_docs)} tasks to check",
                    tags=["trail", "documentation", "staleness_scan"], source=agent)
            except Exception: pass
            return {"ok": True, "tasks_to_check": len(needs_docs), "tasks": needs_docs[:10]}
        except Exception as e:
            return {"ok": False, "error": str(e)}
