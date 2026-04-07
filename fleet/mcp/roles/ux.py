"""UX Designer role-specific group calls.

UX at EVERY level — core, module, CLI, API, not just UI.

Source: fleet-elevation/13 (UX role spec)

Group calls:
  ux_spec_contribution — produce ux_spec for a task touching user-facing elements
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
    async def ux_spec_contribution(task_id: str) -> dict:
        """Prepare context for producing a ux_spec contribution.

        UX is at EVERY level: UI, CLI, API responses, error messages,
        config structure, event display, notification content.

        Args:
            task_id: Target task with user-facing elements.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "ux-designer"

        try:
            task = await ctx.mc.get_task(board_id, task_id)
            cf = task.custom_fields

            template = (
                f"## UX Spec for: {task.title}\n\n"
                "### UX Considerations:\n"
                "1. **User-facing elements** — what does the user see/interact with?\n"
                "2. **States** — loading, empty, error, success, partial\n"
                "3. **Interactions** — click, type, navigate, keyboard shortcuts\n"
                "4. **Accessibility** — ARIA labels, keyboard nav, screen reader, color contrast\n"
                "5. **Patterns to follow** — existing components, design system alignment\n"
                "6. **Patterns to avoid** — anti-patterns for this type of interface\n\n"
                "Remember: UX is not just UI. CLI output, API responses, error messages,\n"
                "config file structure, log format — ALL have user experience.\n\n"
                "After producing spec, call:\n"
                "fleet_contribute(task_id, 'ux_spec', your_spec)"
            )

            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=f"**[trail]** UX spec contribution started for task:{task_id[:8]} by {agent}",
                    tags=["trail", f"task:{task_id}", "ux_contribution"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True, "task_id": task_id, "task_title": task.title,
                "template": template,
                "next_step": "Assess user-facing elements at ALL levels. Produce UX spec. Call fleet_contribute.",
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def ux_accessibility_audit(task_id: str = "") -> dict:
        """Prepare context for an accessibility audit.

        WCAG compliance check for user-facing elements.

        Args:
            task_id: Task with UI elements to audit. Empty = general audit.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        checklist = (
            "## Accessibility Audit\n\n"
            "### WCAG Checklist:\n"
            "- [ ] All images have alt text\n"
            "- [ ] Form inputs have labels (visible + aria-label)\n"
            "- [ ] Interactive elements keyboard-accessible\n"
            "- [ ] Color contrast meets WCAG AA (4.5:1 for text)\n"
            "- [ ] Focus indicators visible\n"
            "- [ ] Screen reader announces state changes (aria-live)\n"
            "- [ ] Heading hierarchy correct (h1→h2→h3)\n"
            "- [ ] Links have descriptive text (not 'click here')\n"
        )
        try:
            await ctx.mc.post_memory(board_id,
                content=f"**[trail]** Accessibility audit started. Task: {task_id[:8] if task_id else 'general'}",
                tags=["trail", "ux", "accessibility_audit"],
                source=ctx.agent_name or "ux-designer")
        except Exception: pass
        return {"ok": True, "task_id": task_id or "", "checklist": checklist}
