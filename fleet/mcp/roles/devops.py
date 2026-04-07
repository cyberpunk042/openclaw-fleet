"""DevOps role-specific group calls.

DevOps owns infrastructure, CI/CD, deployment maturity.
Everything scriptable, everything reproducible.

Source: fleet-elevation/10 (devops role spec)
        tools-system-full-capability-map.md

Group calls:
  devops_infrastructure_health — check MC, gateway, LocalAI, Plane, IRC, daemons
  devops_deployment_contribution — produce deployment_manifest for a feature
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
    """Register devops-specific group calls."""

    @server.tool()
    async def devops_infrastructure_health() -> dict:
        """Check fleet infrastructure health — MC, gateway, daemons, services.

        Tree:
        1. Check MC backend (API responds)
        2. Check gateway (WebSocket responds)
        3. Check IRC (The Lounge accessible)
        4. Report health status
        5. Post findings to board memory [infrastructure, health]
        6. Alert on critical issues
        7. Record trail
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "devops"

        checks = {}

        # Check MC backend
        try:
            agents = await ctx.mc.list_agents()
            checks["mc_backend"] = {"status": "healthy", "agents": len(agents)}
        except Exception as e:
            checks["mc_backend"] = {"status": "error", "error": str(e)[:100]}

        # Check agents online
        try:
            online = sum(1 for a in agents if a.status == "online" and "Gateway" not in a.name)
            total = sum(1 for a in agents if "Gateway" not in a.name)
            checks["agents"] = {"online": online, "total": total}
        except Exception:
            checks["agents"] = {"online": 0, "total": 0}

        # Overall health
        healthy = all(
            c.get("status") == "healthy"
            for c in checks.values()
            if isinstance(c, dict) and "status" in c
        )

        # Format report
        report_lines = ["## Infrastructure Health Check"]
        for name, check in checks.items():
            if isinstance(check, dict):
                status = check.get("status", "unknown")
                icon = "✅" if status == "healthy" else "❌"
                report_lines.append(f"- {icon} **{name}**: {check}")
            else:
                report_lines.append(f"- **{name}**: {check}")

        report = "\n".join(report_lines)

        # Post to board memory
        try:
            await ctx.mc.post_memory(
                board_id, content=report,
                tags=["infrastructure", "health"],
                source=agent,
            )
        except Exception:
            pass

        # Alert on issues
        if not healthy:
            try:
                await ctx.irc.notify(
                    "#fleet",
                    f"[{agent}] Infrastructure issues detected — check board memory",
                )
            except Exception:
                pass

        # Trail
        try:
            await ctx.mc.post_memory(
                board_id,
                content=f"**[trail]** Infrastructure health check by {agent}: {'healthy' if healthy else 'issues detected'}",
                tags=["trail", "infrastructure_health"],
                source=agent,
            )
        except Exception:
            pass

        return {"ok": True, "healthy": healthy, "checks": checks}

    @server.tool()
    async def devops_deployment_contribution(task_id: str) -> dict:
        """Prepare context for producing a deployment_manifest contribution.

        Reads the target task and delivery phase to produce infrastructure
        requirements for deployment.

        Tree:
        1. Read target task and delivery phase
        2. Prepare deployment manifest template per phase
        3. Record trail

        Args:
            task_id: Target task to contribute deployment manifest for.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        agent = ctx.agent_name or "devops"

        try:
            task = await ctx.mc.get_task(board_id, task_id)
            cf = task.custom_fields
            phase = cf.delivery_phase or "mvp"

            phase_infra = {
                "poc": "Basic local/test deployment. Docker compose. Manual steps documented.",
                "mvp": "Automated CI (lint, test, build). Docker images tagged. Env vars for config.",
                "staging": "Full CI/CD. Staging mirrors production. Health checks. Basic monitoring. Secrets managed.",
                "production": "Production pipeline. Blue-green/canary. Full monitoring. Auto-scaling. Runbook.",
            }

            template = (
                f"## Deployment Manifest for: {task.title}\n\n"
                f"**Phase:** {phase}\n"
                f"**Infrastructure Level:** {phase_infra.get(phase, phase_infra['mvp'])}\n\n"
                "### Manifest Contents:\n"
                "1. **Environment** — services, ports, resources needed\n"
                "2. **Configuration** — env vars, secrets, feature flags\n"
                "3. **Deployment strategy** — rolling/blue-green/canary\n"
                "4. **Monitoring** — what to monitor, alert thresholds\n"
                "5. **Rollback** — how to roll back safely\n\n"
                "After producing manifest, call:\n"
                "fleet_contribute(task_id, 'deployment_manifest', your_manifest)"
            )

            # Trail
            try:
                await ctx.mc.post_memory(
                    board_id,
                    content=f"**[trail]** Deployment contribution started for task:{task_id[:8]} by {agent}. Phase: {phase}",
                    tags=["trail", f"task:{task_id}", "deployment_contribution"],
                    source=agent,
                )
            except Exception:
                pass

            return {
                "ok": True,
                "task_id": task_id,
                "task_title": task.title,
                "delivery_phase": phase,
                "infrastructure_level": phase_infra.get(phase, ""),
                "template": template,
                "next_step": "Produce deployment manifest and call fleet_contribute.",
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def devops_cicd_review(task_id: str) -> dict:
        """Review CI/CD pipeline changes for correctness and security.

        Args:
            task_id: Task with CI/CD changes to review.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        try:
            task = await ctx.mc.get_task(board_id, task_id)
            checklist = (
                f"## CI/CD Review: {task.title}\n\n"
                "- Pipeline correct? (steps in right order)\n"
                "- Secrets handled properly? (not in plaintext)\n"
                "- Tests run before deploy?\n"
                "- Deploy requires CI pass?\n"
                "- Efficient? (not wastefully slow)\n"
            )
            try:
                await ctx.mc.post_memory(board_id,
                    content=f"**[trail]** CI/CD review for task:{task_id[:8]}",
                    tags=["trail", f"task:{task_id}", "cicd_review"],
                    source=ctx.agent_name or "devops")
            except Exception: pass
            return {"ok": True, "task_id": task_id, "checklist": checklist}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @server.tool()
    async def devops_phase_infrastructure(task_id: str) -> dict:
        """Assess infrastructure maturity gap for delivery phase.

        Args:
            task_id: Task to assess infrastructure for.
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()
        try:
            task = await ctx.mc.get_task(board_id, task_id)
            phase = task.custom_fields.delivery_phase or "mvp"
            requirements = {
                "poc": "Docker compose, manual steps documented",
                "mvp": "Automated CI, Docker images tagged, env vars",
                "staging": "Full CI/CD, staging env, health checks, monitoring, secrets managed",
                "production": "Production pipeline, blue-green, full monitoring, auto-scaling, runbook",
            }
            try:
                await ctx.mc.post_memory(board_id,
                    content=f"**[trail]** Phase infrastructure assessment for task:{task_id[:8]}. Phase: {phase}",
                    tags=["trail", f"task:{task_id}", "phase_infrastructure"],
                    source=ctx.agent_name or "devops")
            except Exception: pass
            return {"ok": True, "task_id": task_id, "phase": phase,
                    "requirements": requirements.get(phase, ""), "all_requirements": requirements}
        except Exception as e:
            return {"ok": False, "error": str(e)}
