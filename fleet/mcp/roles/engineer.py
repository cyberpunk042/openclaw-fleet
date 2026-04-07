"""Software Engineer role-specific group calls.

The engineer implements the confirmed plan, consuming contributions
from architect, QA, UX, and DevSecOps. These group calls aggregate
the contribution checking and implementation workflow.

Source: fleet-elevation/09 (engineer role spec)
        tools-system-full-capability-map.md

Group calls:
  eng_contribution_check — verify all required inputs are in context before work
  eng_fix_task_response — read rejection feedback, prepare fix context
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
    """Register engineer-specific group calls."""

    @server.tool()
    async def eng_contribution_check(task_id: str = "") -> dict:
        """Check that all required contributions are available before starting work.

        Before the engineer starts implementing, they need architect design
        input, QA test criteria, and potentially UX specs and DevSecOps
        requirements. This tool checks what's available and what's missing.

        Tree:
        1. Read task type and assigned agent
        2. Check synergy matrix for required contributions
        3. Read task comments for received contributions
        4. List what's received with summaries
        5. List what's missing with request suggestions
        6. Record trail

        Args:
            task_id: Task to check. Empty = current task.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        tid = task_id or ctx.task_id
        agent = ctx.agent_name or "software-engineer"

        if not tid:
            return {"ok": False, "error": "No task_id"}

        try:
            task = await ctx.mc.get_task(board_id, tid)
            cf = task.custom_fields

            # Gather received contributions with summaries
            received = []
            try:
                comments = await ctx.mc.list_comments(board_id, tid)
                for c in (comments or []):
                    cmsg = c.message if hasattr(c, 'message') else c.get("message", "")
                    if "**Contribution (" in cmsg:
                        try:
                            ts = cmsg.index("(") + 1
                            te = cmsg.index(")")
                            ctype = cmsg[ts:te]

                            # Extract contributor
                            contributor = ""
                            if "from " in cmsg:
                                after_from = cmsg.split("from ", 1)[1]
                                contributor = after_from.split(":")[0].split("\n")[0].strip()

                            # Extract summary (first 200 chars after header)
                            summary_start = cmsg.find("\n\n")
                            summary = cmsg[summary_start:summary_start + 200].strip() if summary_start > 0 else ""

                            received.append({
                                "type": ctype,
                                "from": contributor,
                                "summary": summary[:150],
                            })
                        except (ValueError, IndexError):
                            pass
            except Exception:
                pass

            received_types = [r["type"] for r in received]

            # Check completeness
            from fleet.core.contributions import check_contribution_completeness
            status = check_contribution_completeness(
                tid, cf.agent_name or agent, cf.task_type or "task", received_types,
            )

            # Build result
            result = {
                "ok": True,
                "task_id": tid,
                "task_title": task.title,
                "received_contributions": received,
                "required": status.required,
                "missing": status.missing,
                "all_received": status.all_received,
                "completeness_pct": status.completeness_pct,
            }

            if status.missing:
                result["action_needed"] = (
                    f"Missing contributions: {', '.join(status.missing)}. "
                    f"Call fleet_request_input to request them, or wait for contributors."
                )
            else:
                result["ready"] = "All required contributions received. Ready for work stage."

            # Trail
            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=(
                        f"**[trail]** Contribution check by {agent} for task:{tid[:8]}: "
                        f"{len(received)}/{len(status.required)} received. "
                        f"{'READY' if status.all_received else f'Missing: {status.missing}'}"
                    ),
                    tags=["trail", f"task:{tid}", "contribution_check"],
                    source=agent,
                )
            except Exception:
                pass

            return result

        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def eng_fix_task_response(task_id: str = "") -> dict:
        """Read rejection feedback and prepare fix context.

        When a task is rejected by fleet-ops, the engineer needs to
        understand what went wrong and fix it. This tool reads the
        rejection feedback and prepares structured fix context.

        Tree:
        1. Read task rejection comments
        2. Identify what was rejected and why
        3. Read original verbatim for re-grounding
        4. Prepare fix context
        5. Record trail

        Args:
            task_id: Fix task or original rejected task. Empty = current task.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        tid = task_id or ctx.task_id
        agent = ctx.agent_name or "software-engineer"

        if not tid:
            return {"ok": False, "error": "No task_id"}

        try:
            task = await ctx.mc.get_task(board_id, tid)
            cf = task.custom_fields

            # Find rejection feedback
            rejection_feedback = ""
            original_task_id = cf.parent_task or ""

            try:
                comments = await ctx.mc.list_comments(board_id, tid)
                for c in (comments or []):
                    cmsg = c.message if hasattr(c, 'message') else c.get("message", "")
                    if "Rejected" in cmsg or "rejected" in cmsg:
                        rejection_feedback = cmsg[:500]
                        break
            except Exception:
                pass

            # If this is a fix task, read parent task's rejection
            if not rejection_feedback and original_task_id:
                try:
                    parent_comments = await ctx.mc.list_comments(board_id, original_task_id)
                    for c in (parent_comments or []):
                        cmsg = c.message if hasattr(c, 'message') else c.get("message", "")
                        if "Rejected" in cmsg or "rejected" in cmsg:
                            rejection_feedback = cmsg[:500]
                            break
                except Exception:
                    pass

            # Read verbatim for re-grounding
            verbatim = cf.requirement_verbatim or ""
            if not verbatim and original_task_id:
                try:
                    parent = await ctx.mc.get_task(board_id, original_task_id)
                    verbatim = parent.custom_fields.requirement_verbatim or ""
                except Exception:
                    pass

            result = {
                "ok": True,
                "task_id": tid,
                "task_title": task.title,
                "rejection_feedback": rejection_feedback or "(no rejection feedback found)",
                "verbatim": verbatim or "(not set)",
                "original_task_id": original_task_id[:8] if original_task_id else "",
            }

            if rejection_feedback:
                result["fix_approach"] = (
                    "1. Read the rejection feedback carefully — what SPECIFICALLY failed?\n"
                    "2. Re-read the verbatim requirement — are you solving the right problem?\n"
                    "3. Fix the ROOT CAUSE, not just the symptom\n"
                    "4. Add tests that would have caught the issue\n"
                    "5. Re-submit via fleet_task_complete"
                )
            else:
                result["warning"] = "No rejection feedback found. Check task comments or parent task."

            # Trail
            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=(
                        f"**[trail]** Fix task context prepared for task:{tid[:8]} by {agent}. "
                        f"Feedback: {'found' if rejection_feedback else 'NOT FOUND'}"
                    ),
                    tags=["trail", f"task:{tid}", "fix_response"],
                    source=agent,
                )
            except Exception:
                pass

            return result

        except Exception as e:
            return {"ok": False, "error": str(e)}
