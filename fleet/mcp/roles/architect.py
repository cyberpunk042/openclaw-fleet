"""Architect role-specific group calls.

The architect owns design decisions, complexity assessment, and
architecture health. These group calls aggregate design contribution
and assessment workflows.

Source: fleet-elevation/07 (architect role spec)
        tools-system-full-capability-map.md

Group calls:
  arch_design_contribution — read target task, produce design_input, contribute
  arch_codebase_assessment — examine codebase structure, produce analysis with file refs
  (arch_option_comparison, arch_complexity_estimate — TO BE IMPLEMENTED)
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
    """Register architect-specific group calls."""

    @server.tool()
    async def arch_design_contribution(task_id: str) -> dict:
        """Prepare context for producing a design_input contribution.

        Reads the target task's requirements, existing analysis, and
        delivery phase to provide the architect with structured context
        for producing design input.

        Tree:
        1. Read target task verbatim + description
        2. Read existing analysis artifacts/comments
        3. Read delivery phase for phase-appropriate design depth
        4. Prepare design contribution context
        5. Record trail

        After this call, the architect produces the design input and calls
        fleet_contribute(task_id, 'design_input', content).

        Args:
            task_id: Target task to contribute design input for.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "architect"

        try:
            task = await ctx.mc.get_task(board_id, task_id)
            cf = task.custom_fields

            context = {
                "task_title": task.title,
                "task_type": cf.task_type or "task",
                "verbatim": cf.requirement_verbatim or "(not set)",
                "description": task.description[:500] if task.description else "(none)",
                "delivery_phase": cf.delivery_phase or "unknown",
                "target_agent": cf.agent_name or "unassigned",
                "existing_analysis": "",
                "existing_investigation": "",
            }

            # Read existing analysis/investigation from comments
            try:
                comments = await ctx.mc.list_comments(board_id, task_id)
                for c in (comments or []):
                    cmsg = c.message if hasattr(c, 'message') else c.get("message", "")
                    if "analysis" in cmsg.lower() and "artifact" in cmsg.lower():
                        context["existing_analysis"] = cmsg[:400]
                    if "investigation" in cmsg.lower() and "artifact" in cmsg.lower():
                        context["existing_investigation"] = cmsg[:400]
            except Exception:
                pass

            # Phase-appropriate design depth
            phase = cf.delivery_phase or "mvp"
            depth_guide = {
                "poc": "Simple working structure. Can be single-file if small. Focus on proving concept.",
                "mvp": "Proper separation of concerns. Domain vs infrastructure. Clean interfaces.",
                "staging": "Full onion layering. Testable boundaries. Integration patterns defined.",
                "production": "Production architecture. Scalable. Maintainable. Documented.",
            }
            context["design_depth"] = depth_guide.get(phase, depth_guide["mvp"])

            # Design contribution template
            contribution_template = (
                f"## Design Input for: {task.title}\n\n"
                f"**Verbatim:** {context['verbatim']}\n"
                f"**Phase:** {context['delivery_phase']} — {context['design_depth']}\n\n"
                "### Expected Design Input Contents:\n"
                "1. **Architecture pattern** — which pattern fits and WHY\n"
                "2. **File structure** — where things go, naming, modules\n"
                "3. **SRP verification** — does each module have one job?\n"
                "4. **Domain boundaries** — what's core vs infrastructure\n"
                "5. **Dependency direction** — all inward (onion compliance)\n"
                "6. **Integration constraints** — how this connects to other systems\n"
                "7. **What to AVOID** — anti-patterns for this type of work\n\n"
                "After producing design input, call:\n"
                "fleet_contribute(task_id, 'design_input', your_design)"
            )

            # Post template to architect's own task
            if ctx.task_id and ctx.task_id != task_id:
                try:
                    await ctx.mc.post_comment(board_id, ctx.task_id, contribution_template)
                except Exception:
                    pass

            # Trail
            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=(
                        f"**[trail]** Design contribution started for task:{task_id[:8]} "
                        f"by {agent}. Phase: {phase}"
                    ),
                    tags=["trail", f"task:{task_id}", "design_contribution"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True,
                "task_id": task_id,
                "context": context,
                "contribution_template": contribution_template[:500],
                "next_step": (
                    "Review the target task context above. Produce design input covering "
                    "architecture pattern, file structure, SRP, domain boundaries, "
                    "dependency direction, integration constraints, and anti-patterns. "
                    "Then call fleet_contribute(task_id, 'design_input', your_design)."
                ),
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def arch_codebase_assessment(directory: str = "", scope: str = "") -> dict:
        """Assess codebase architecture health for a specific area.

        Prepares context for the architect to examine code structure,
        identify patterns, dependencies, SRP compliance, and coupling.

        Tree:
        1. Identify target directory/scope
        2. Prepare assessment framework (what to look for)
        3. Record trail

        The architect then uses filesystem MCP to explore the codebase
        and produces an analysis_document artifact.

        Args:
            directory: Target directory to assess (e.g., "fleet/core/").
            scope: What to focus on (e.g., "dependency direction", "SRP compliance").
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "architect"

        assessment_framework = (
            f"## Codebase Assessment: {directory or 'full codebase'}\n\n"
            f"**Scope:** {scope or 'general architecture health'}\n\n"
            "### Assessment Checklist:\n"
            "1. **SRP** — does each module/file have one responsibility?\n"
            "2. **Domain boundaries** — are core and infrastructure separated?\n"
            "3. **Dependency direction** — do all deps point inward (onion)?\n"
            "4. **Pattern consistency** — similar problems use similar patterns?\n"
            "5. **Coupling** — are modules loosely coupled with clean interfaces?\n"
            "6. **Technical debt** — accumulated shortcuts or workarounds?\n"
            "7. **Naming** — clear, consistent, domain-appropriate?\n\n"
            "### How to Assess:\n"
            "Use filesystem MCP to read files. Reference SPECIFIC files and line numbers.\n"
            "Produce an analysis_document artifact via fleet_artifact_create.\n"
            "Update progressively via fleet_artifact_update as you examine more code.\n"
        )

        # Trail
        try:
            await ctx.mc.post_memory(
                board_id,
                content=(
                    f"**[trail]** Codebase assessment started by {agent}. "
                    f"Directory: {directory or 'full'}. Scope: {scope or 'general'}"
                ),
                tags=["trail", "architecture", "assessment"],
                source=agent,
            )
        except Exception:
            pass

        return {
            "ok": True,
            "directory": directory or "(full codebase)",
            "scope": scope or "general architecture health",
            "assessment_framework": assessment_framework,
            "next_step": (
                "Use filesystem MCP to examine the target directory. "
                "Produce analysis_document artifact via fleet_artifact_create. "
                "Reference specific files and line numbers in findings."
            ),
        }

    @server.tool()
    async def arch_option_comparison(task_id: str) -> dict:
        """Prepare context for comparing multiple design approaches.

        For investigation stage — explore multiple options with tradeoffs.
        NOT just the first approach found.

        Args:
            task_id: Task to explore design options for.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        try:
            task = await ctx.mc.get_task(board_id, task_id)
            template = (
                f"## Option Comparison: {task.title}\n\n"
                "### For each approach:\n"
                "| Aspect | Option A | Option B | Option C |\n"
                "|--------|----------|----------|----------|\n"
                "| Pattern | | | |\n"
                "| Pros | | | |\n"
                "| Cons | | | |\n"
                "| Complexity | | | |\n"
                "| Risk | | | |\n"
                "| Phase fit | | | |\n\n"
                "Produce investigation_document via fleet_artifact_create."
            )
            try:
                await ctx.mc.post_memory(board_id,
                    content=f"**[trail]** Option comparison started for task:{task_id[:8]}",
                    tags=["trail", f"task:{task_id}", "option_comparison"],
                    source=ctx.agent_name or "architect")
            except Exception: pass
            return {"ok": True, "task_id": task_id, "template": template}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def arch_complexity_estimate(task_id: str) -> dict:
        """Assess task complexity — story points, architectural impact, risks.

        Args:
            task_id: Task to assess complexity for.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        try:
            task = await ctx.mc.get_task(board_id, task_id)
            cf = task.custom_fields
            guide = (
                f"## Complexity Assessment: {task.title}\n\n"
                "### Factors to evaluate:\n"
                "1. **Scope** — how many files/modules touched?\n"
                "2. **Dependencies** — how many systems affected?\n"
                "3. **Unknowns** — what don't we know yet?\n"
                "4. **Risk** — what could go wrong?\n"
                "5. **Suggested SP** — 1(trivial) / 2(simple) / 3(moderate) / 5(complex) / 8(very complex) / 13(epic)\n"
            )
            try:
                await ctx.mc.post_memory(board_id,
                    content=f"**[trail]** Complexity estimate started for task:{task_id[:8]}",
                    tags=["trail", f"task:{task_id}", "complexity_estimate"],
                    source=ctx.agent_name or "architect")
            except Exception: pass
            return {"ok": True, "task_id": task_id, "current_sp": cf.story_points or 0, "guide": guide}
        except Exception as e:
            return {"ok": False, "error": str(e)}
