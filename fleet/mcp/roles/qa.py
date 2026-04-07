"""QA Engineer role-specific group calls.

QA predefines tests BEFORE implementation and validates DURING review.
These group calls aggregate the test predefinition and validation
workflows into single agent-facing tools.

Source: fleet-elevation/11 (QA role spec)
        tools-system-full-capability-map.md

Group calls:
  qa_test_predefinition — read target task, produce structured TC-XXX criteria, contribute
  qa_test_validation — read implementation, check each predefined TC-XXX, produce validation report
  (qa_coverage_analysis, qa_acceptance_criteria_review — TO BE IMPLEMENTED)
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
    """Register QA-specific group calls."""

    @server.tool()
    async def qa_test_predefinition(task_id: str) -> dict:
        """Predefine test criteria for a task entering reasoning stage.

        Reads the target task's verbatim requirement, acceptance criteria,
        and architect design input, then produces structured test criteria
        in TC-XXX format and delivers them via fleet_contribute.

        Tree:
        1. Read target task verbatim + acceptance criteria
        2. Read architect design input (if available in comments)
        3. Read delivery phase for phase-appropriate rigor
        4. Produce structured qa_test_definition with TC-XXX criteria
        5. Call fleet_contribute to deliver to target task
        6. Record trail

        The agent still needs to THINK about what tests to define — this
        tool structures the OUTPUT, not the THINKING. The agent reads the
        requirement, identifies test scenarios, then uses this tool to
        format and deliver them.

        Args:
            task_id: Target task to predefine tests for.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "qa-engineer"

        try:
            task = await ctx.mc.get_task(board_id, task_id)
            cf = task.custom_fields

            # Gather context for the QA agent
            context = {
                "task_title": task.title,
                "task_type": cf.task_type or "task",
                "verbatim": cf.requirement_verbatim or "(not set)",
                "description": task.description[:500] if task.description else "(none)",
                "delivery_phase": cf.delivery_phase or "unknown",
                "architect_input": "",
            }

            # Read architect design input from comments
            try:
                comments = await ctx.mc.list_comments(board_id, task_id)
                for c in (comments or []):
                    cmsg = c.message if hasattr(c, 'message') else c.get("message", "")
                    if "**Contribution (design_input)" in cmsg:
                        context["architect_input"] = cmsg[:500]
                        break
            except Exception:
                pass

            # Determine phase-appropriate test rigor
            phase = cf.delivery_phase or "mvp"
            rigor_guide = {
                "poc": "Happy path only. Manual testing acceptable.",
                "mvp": "Main flows + critical edge cases. Automated unit tests.",
                "staging": "Comprehensive: unit, integration, load. CI-enforced.",
                "production": "Complete: all paths, performance, resilience.",
            }
            context["test_rigor"] = rigor_guide.get(phase, rigor_guide["mvp"])

            # Post a structured prompt as comment — the QA agent will use this
            # context to produce test criteria. This tool PROVIDES the structure,
            # the agent PROVIDES the intelligence.
            predefinition_context = (
                f"## Test Predefinition Context for: {task.title}\n\n"
                f"**Verbatim Requirement:** {context['verbatim']}\n\n"
                f"**Delivery Phase:** {context['delivery_phase']}\n"
                f"**Test Rigor:** {context['test_rigor']}\n\n"
            )
            if context["architect_input"]:
                predefinition_context += f"**Architect Design Input:**\n{context['architect_input'][:300]}\n\n"

            predefinition_context += (
                "**Expected Output Format:**\n"
                "```\n"
                "TC-001: [description] | type: unit/integration/e2e | priority: required/recommended\n"
                "TC-002: ...\n"
                "```\n\n"
                "After defining criteria, call fleet_contribute(task_id, 'qa_test_definition', content)."
            )

            # Post context as comment on the contribution task (not the target)
            if ctx.task_id and ctx.task_id != task_id:
                try:
                    await ctx.mc.post_comment(
                        board_id, ctx.task_id,
                        predefinition_context,
                    )
                except Exception:
                    pass

            # Trail
            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=(
                        f"**[trail]** QA test predefinition started for task:{task_id[:8]} "
                        f"by {agent}. Phase: {phase}. Rigor: {context['test_rigor'][:40]}"
                    ),
                    tags=["trail", f"task:{task_id}", "qa_test_predefinition"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True,
                "task_id": task_id,
                "task_title": task.title,
                "context": context,
                "next_step": (
                    "Review the context above. Define test criteria in TC-XXX format. "
                    "Then call fleet_contribute(task_id, 'qa_test_definition', your_criteria)."
                ),
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def qa_test_validation(task_id: str) -> dict:
        """Validate a completed task against predefined test criteria.

        Reads the predefined qa_test_definition from task comments,
        reads the implementation (completion summary, PR), and produces
        a structured validation report.

        Tree:
        1. Read predefined test criteria from task comments
        2. Read completion summary + PR info
        3. For each TC-XXX: check if addressed in implementation
        4. Produce validation report (TC-XXX: met/not met with evidence)
        5. Post validation as typed comment
        6. Flag gaps to fleet-ops
        7. Record trail

        Args:
            task_id: Task to validate (should be in review status).
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "qa-engineer"

        try:
            task = await ctx.mc.get_task(board_id, task_id)
            cf = task.custom_fields

            # Read predefined test criteria
            predefined_criteria = ""
            completion_summary = ""
            try:
                comments = await ctx.mc.list_comments(board_id, task_id)
                for c in (comments or []):
                    cmsg = c.message if hasattr(c, 'message') else c.get("message", "")
                    if "**Contribution (qa_test_definition)" in cmsg:
                        predefined_criteria = cmsg
                    if "Completed" in cmsg or "completed" in cmsg or "✅" in cmsg:
                        completion_summary = cmsg
            except Exception:
                pass

            validation_context = {
                "task_title": task.title,
                "task_id": task_id[:8],
                "has_predefined_criteria": bool(predefined_criteria),
                "has_completion_summary": bool(completion_summary),
                "pr_url": cf.pr_url or "",
                "predefined_criteria_preview": predefined_criteria[:500] if predefined_criteria else "(none found)",
                "completion_preview": completion_summary[:500] if completion_summary else "(none found)",
            }

            if not predefined_criteria:
                validation_context["warning"] = (
                    "No predefined test criteria found in task comments. "
                    "QA test predefinition may not have been done for this task."
                )

            # The QA agent reads this context and produces the validation report.
            # The tool provides structure; the agent provides judgment.

            # Post validation context as comment on QA's own task
            if ctx.task_id and ctx.task_id != task_id:
                try:
                    validation_prompt = (
                        f"## Test Validation Context for: {task.title}\n\n"
                        f"**PR:** {cf.pr_url or '(no PR)'}\n\n"
                        f"**Predefined Criteria:**\n{predefined_criteria[:400] if predefined_criteria else '(none)'}\n\n"
                        f"**Completion Summary:**\n{completion_summary[:400] if completion_summary else '(none)'}\n\n"
                        "**Expected Output:** For each TC-XXX, state: MET or NOT MET with evidence.\n"
                        "Then post your validation as a comment on the target task."
                    )
                    await ctx.mc.post_comment(board_id, ctx.task_id, validation_prompt)
                except Exception:
                    pass

            # Trail
            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=(
                        f"**[trail]** QA validation started for task:{task_id[:8]} by {agent}. "
                        f"Criteria: {'found' if predefined_criteria else 'NOT FOUND'}"
                    ),
                    tags=["trail", f"task:{task_id}", "qa_validation"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True,
                "validation_context": validation_context,
                "next_step": (
                    "Review the predefined criteria against the implementation. "
                    "For each TC-XXX: verify MET or NOT MET with evidence. "
                    "Post your validation as a comment on the target task."
                ),
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def qa_coverage_analysis(project: str = "") -> dict:
        """Analyze test coverage for a project.

        Prepares context for running coverage tools and analyzing gaps.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        guide = (
            "## Coverage Analysis\n\n"
            f"**Project:** {project or 'fleet'}\n\n"
            "### Steps:\n"
            "1. Run: python -m pytest --cov=fleet --cov-report=term-missing\n"
            "2. Identify modules with < 50% coverage\n"
            "3. Identify critical paths with 0% coverage\n"
            "4. Recommend priority test additions\n"
            "5. Post coverage report to board memory [quality, coverage]\n"
        )
        try:
            await ctx.mc.post_memory(board_id,
                content=f"**[trail]** Coverage analysis started. Project: {project or 'fleet'}",
                tags=["trail", "qa", "coverage_analysis"],
                source=ctx.agent_name or "qa-engineer")
        except Exception: pass
        return {"ok": True, "project": project or "fleet", "guide": guide}

    @server.tool()
    async def qa_acceptance_criteria_review(task_id: str) -> dict:
        """Review task acceptance criteria for testability.

        Checks if criteria are specific, checkable, and not vague.

        Args:
            task_id: Task to review criteria for.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        try:
            task = await ctx.mc.get_task(board_id, task_id)
            guide = (
                f"## Acceptance Criteria Review: {task.title}\n\n"
                f"**Description:** {task.description[:300] if task.description else '(none)'}\n\n"
                "### Check each criterion:\n"
                "- Is it SPECIFIC? (not 'it works correctly')\n"
                "- Is it CHECKABLE? (can you write a test for it?)\n"
                "- Is it MEASURABLE? (pass/fail, not 'good enough')\n\n"
                "If vague → post comment to PM with improvement suggestions.\n"
                "Example: 'it works correctly' → 'Returns 200 for valid input, "
                "400 for missing required fields, 401 for unauthenticated requests'"
            )
            try:
                await ctx.mc.post_memory(board_id,
                    content=f"**[trail]** Acceptance criteria review for task:{task_id[:8]}",
                    tags=["trail", f"task:{task_id}", "criteria_review"],
                    source=ctx.agent_name or "qa-engineer")
            except Exception: pass
            return {"ok": True, "task_id": task_id, "task_title": task.title, "guide": guide}
        except Exception as e:
            return {"ok": False, "error": str(e)}
