"""DevSecOps (Cyberpunk-Zero) role-specific group calls.

Security at EVERY phase, not just review. These group calls aggregate
security scanning, contribution, and assessment workflows.

Source: fleet-elevation/08 (DevSecOps role spec)
        tools-system-full-capability-map.md

Group calls:
  sec_contribution — produce security_requirement for a target task
  sec_pr_security_review — structured security review of a PR
  (sec_dependency_audit, sec_code_scan, sec_secret_scan, sec_infrastructure_health — TO BE IMPLEMENTED)
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
    """Register DevSecOps-specific group calls."""

    @server.tool()
    async def sec_contribution(task_id: str) -> dict:
        """Prepare context for producing a security_requirement contribution.

        Reads the target task's requirements and plan to assess security
        implications and produce specific, actionable security requirements.

        Tree:
        1. Read target task verbatim + plan
        2. Assess security implications (auth, data, external calls, deps)
        3. Prepare security requirement context
        4. Record trail

        After this call, DevSecOps produces specific requirements and calls
        fleet_contribute(task_id, 'security_requirement', content).

        Not generic "be secure" — specific: "use JWT with RS256",
        "pin actions to SHA", "sanitize input on endpoint X".

        Args:
            task_id: Target task to provide security requirements for.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "devsecops-expert"

        try:
            task = await ctx.mc.get_task(board_id, task_id)
            cf = task.custom_fields

            context = {
                "task_title": task.title,
                "verbatim": cf.requirement_verbatim or "(not set)",
                "description": task.description[:500] if task.description else "(none)",
                "delivery_phase": cf.delivery_phase or "unknown",
                "target_agent": cf.agent_name or "unassigned",
                "architect_design": "",
            }

            # Read architect design input
            try:
                comments = await ctx.mc.list_comments(board_id, task_id)
                for c in (comments or []):
                    cmsg = c.message if hasattr(c, 'message') else c.get("message", "")
                    if "**Contribution (design_input)" in cmsg:
                        context["architect_design"] = cmsg[:400]
                        break
            except Exception:
                pass

            # Security assessment template
            assessment_template = (
                f"## Security Assessment for: {task.title}\n\n"
                f"**Verbatim:** {context['verbatim']}\n"
                f"**Phase:** {context['delivery_phase']}\n\n"
                "### Security Considerations:\n"
                "1. **Authentication** — does this involve auth? What method? (JWT, session, API key)\n"
                "2. **Input validation** — does this accept user input? Where? Sanitization needed?\n"
                "3. **Dependencies** — new dependencies added? Known CVEs? Version pinning?\n"
                "4. **Secrets** — does this handle secrets? How? (env vars, not hardcoded)\n"
                "5. **Network** — external calls? Allowlist needed? TLS required?\n"
                "6. **Permissions** — file permissions? User roles? Access control?\n\n"
                "### Expected Output:\n"
                "Specific, actionable requirements. Not 'be secure' — but:\n"
                "- 'Use JWT with RS256 signing, not HS256'\n"
                "- 'Pin GitHub Actions to SHA, not tags'\n"
                "- 'Sanitize all input on /api/search endpoint'\n"
                "- 'Store API keys in .env, not config.py'\n\n"
                "After producing requirements, call:\n"
                "fleet_contribute(task_id, 'security_requirement', your_requirements)"
            )

            # Post to own task
            if ctx.task_id and ctx.task_id != task_id:
                try:
                    await ctx.mc.post_comment(board_id, ctx.task_id, assessment_template)
                except Exception:
                    pass

            # Trail
            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=(
                        f"**[trail]** Security contribution started for task:{task_id[:8]} "
                        f"by {agent}. Phase: {context['delivery_phase']}"
                    ),
                    tags=["trail", f"task:{task_id}", "security_contribution"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True,
                "task_id": task_id,
                "context": context,
                "next_step": (
                    "Assess security implications using the framework above. "
                    "Produce SPECIFIC requirements (not generic advice). "
                    "Call fleet_contribute(task_id, 'security_requirement', your_requirements)."
                ),
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def sec_pr_security_review(task_id: str) -> dict:
        """Prepare context for a security review of a PR.

        Reads the task's PR information and prepares a structured
        security review checklist for the DevSecOps agent.

        Tree:
        1. Read task with PR URL and branch
        2. Prepare security review checklist
        3. Record trail

        The DevSecOps agent then uses filesystem MCP to read the diff
        and produces a security_review typed comment.

        Critical findings → fleet_alert(category="security") → security_hold.

        Args:
            task_id: Task with PR to review.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "devsecops-expert"

        try:
            task = await ctx.mc.get_task(board_id, task_id)
            cf = task.custom_fields

            review_context = {
                "task_title": task.title,
                "pr_url": cf.pr_url or "(no PR)",
                "branch": cf.branch or "(no branch)",
                "agent": cf.agent_name or "unknown",
                "delivery_phase": cf.delivery_phase or "unknown",
            }

            checklist = (
                f"## Security Review: {task.title}\n\n"
                f"**PR:** {cf.pr_url or '(no PR)'}\n"
                f"**Branch:** {cf.branch or '(no branch)'}\n"
                f"**Phase:** {cf.delivery_phase or 'unknown'}\n\n"
                "### Review Checklist:\n"
                "- [ ] No secrets in code (tokens, keys, passwords, connection strings)\n"
                "- [ ] No hardcoded credentials\n"
                "- [ ] Input validation at all boundaries\n"
                "- [ ] No injection patterns (SQL, command, XSS)\n"
                "- [ ] Dependencies from official sources, pinned versions\n"
                "- [ ] No world-writable permissions\n"
                "- [ ] Auth/permission changes reviewed\n"
                "- [ ] External network calls justified and secured\n\n"
                "### If Critical Finding:\n"
                "1. Call fleet_alert(category='security', severity='critical', ...)\n"
                "   This sets security_hold on the task, blocking approval.\n"
                "2. Post detailed finding as comment on the task.\n"
                "3. If severity warrants, call fleet_escalate to notify PO.\n\n"
                "### If No Findings:\n"
                "Post typed comment: 'Security review: no findings. Clear for approval.'"
            )

            # Trail
            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=(
                        f"**[trail]** Security PR review started for task:{task_id[:8]} "
                        f"by {agent}. PR: {cf.pr_url or 'none'}"
                    ),
                    tags=["trail", f"task:{task_id}", "security_review"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True,
                "task_id": task_id,
                "review_context": review_context,
                "checklist": checklist,
                "next_step": (
                    "Use filesystem MCP to read the PR diff. "
                    "Check each item in the security checklist. "
                    "Post your findings as a comment on the task. "
                    "Use fleet_alert for critical findings."
                ),
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def sec_dependency_audit(project: str = "") -> dict:
        """Audit project dependencies for known vulnerabilities.

        Uses available tools (pip audit, npm audit, semgrep) to scan.

        Args:
            project: Project to audit. Empty = fleet project.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "devsecops-expert"
        guide = (
            "## Dependency Audit\n\n"
            "### Steps:\n"
            "1. Use filesystem MCP to read requirements.txt / package.json\n"
            "2. Run pip audit / npm audit if available\n"
            "3. Check for known CVEs\n"
            "4. Classify: critical / high / medium / low\n"
            "5. For critical: fleet_alert(category='security', severity='critical')\n"
            "6. Post findings to board memory [security, audit]\n"
        )
        try:
            await ctx.mc.post_memory(board_id,
                content=f"**[trail]** Dependency audit started by {agent}. Project: {project or 'fleet'}",
                tags=["trail", "security", "dependency_audit"], source=agent)
        except Exception: pass
        return {"ok": True, "project": project or "fleet", "guide": guide}

    @server.tool()
    async def sec_code_scan(directory: str = "", pattern: str = "") -> dict:
        """Prepare context for scanning code for security patterns.

        Args:
            directory: Target directory to scan.
            pattern: Specific pattern to look for (e.g., "hardcoded secrets").
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "devsecops-expert"
        checklist = (
            "## Code Security Scan\n\n"
            f"**Target:** {directory or 'full codebase'}\n"
            f"**Pattern:** {pattern or 'general security'}\n\n"
            "### Scan for:\n"
            "- Hardcoded secrets (API keys, tokens, passwords)\n"
            "- Injection vectors (SQL, command, XSS patterns)\n"
            "- Insecure deserialization\n"
            "- Insecure file permissions\n"
            "- Deprecated/vulnerable function usage\n\n"
            "Use filesystem MCP + semgrep MCP if available."
        )
        try:
            await ctx.mc.post_memory(board_id,
                content=f"**[trail]** Code scan started by {agent}. Dir: {directory or 'full'}",
                tags=["trail", "security", "code_scan"], source=agent)
        except Exception: pass
        return {"ok": True, "directory": directory or "full", "checklist": checklist}

    @server.tool()
    async def sec_secret_scan() -> dict:
        """Scan repository for exposed credentials and secrets."""
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "devsecops-expert"
        guide = (
            "## Secret Scan\n\n"
            "### Patterns to detect:\n"
            "- API keys (AKIA..., sk-..., ghp_...)\n"
            "- Tokens (Bearer, jwt, session)\n"
            "- Passwords in config files\n"
            "- Connection strings with credentials\n"
            "- Private keys (BEGIN RSA, BEGIN EC)\n\n"
            "Use grep/filesystem MCP to scan.\n"
            "Any finding → fleet_alert(category='security', severity='critical')"
        )
        try:
            await ctx.mc.post_memory(board_id,
                content=f"**[trail]** Secret scan started by {agent}",
                tags=["trail", "security", "secret_scan"], source=agent)
        except Exception: pass
        return {"ok": True, "guide": guide}

    @server.tool()
    async def sec_infrastructure_health() -> dict:
        """Check fleet infrastructure for security issues."""
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "devsecops-expert"
        checklist = (
            "## Infrastructure Security Check\n\n"
            "- MC backend: auth tokens rotated?\n"
            "- Gateway: auth configured?\n"
            "- Secrets in .env (gitignored)?\n"
            "- Ports properly restricted?\n"
            "- TLS for external connections?\n"
            "- Docker images from trusted registries?\n"
        )
        try:
            await ctx.mc.post_memory(board_id,
                content=f"**[trail]** Infrastructure security check by {agent}",
                tags=["trail", "security", "infra_health"], source=agent)
        except Exception: pass
        return {"ok": True, "checklist": checklist}
