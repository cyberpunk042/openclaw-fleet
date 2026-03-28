"""Fleet MCP tool definitions — native tools for agents.

Each tool is what an agent naturally wants to do.
The tool handler does all infrastructure work internally.
Agent provides minimal semantic input. Server handles the rest.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from fleet.mcp.context import FleetMCPContext

# Shared context — initialized on first tool call
_ctx: FleetMCPContext | None = None


def _get_ctx() -> FleetMCPContext:
    """Get or create the shared context."""
    global _ctx
    if _ctx is None:
        _ctx = FleetMCPContext.from_env()
    return _ctx


def register_tools(server: FastMCP) -> None:
    """Register all fleet tools on the MCP server."""

    @server.tool()
    async def fleet_read_context(task_id: str = "", project: str = "") -> dict:
        """Read full task and project context. Call this FIRST every session.

        Args:
            task_id: The task ID from your assignment (required for task operations).
            project: Project name (e.g., "nnrt", "fleet").

        Returns task details, project info, resolved URLs, recent board memory.
        """
        ctx = _get_ctx()

        # Store task context for subsequent tool calls
        if task_id:
            ctx.task_id = task_id
        if project:
            ctx.project_name = project

        board_id = await ctx.resolve_board_id()
        result = {"board_id": board_id, "agent": ctx.agent_name, "task_id": ctx.task_id}

        if ctx.task_id:
            try:
                task = await ctx.mc.get_task(board_id, ctx.task_id)
                result["task"] = {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status.value,
                    "description": task.description[:500],
                    "priority": task.priority,
                    "project": task.custom_fields.project,
                    "tags": task.tags,
                }
                # Auto-set project from task custom fields
                if task.custom_fields.project and not ctx.project_name:
                    ctx.project_name = task.custom_fields.project
                # Auto-set worktree
                if task.custom_fields.worktree:
                    ctx.worktree = task.custom_fields.worktree
            except Exception as e:
                result["task"] = {"id": ctx.task_id, "error": str(e)}

        if ctx.project_name:
            urls = ctx.urls.resolve(project=ctx.project_name, task_id=ctx.task_id)
            result["urls"] = {"task": urls.task or "", "board": urls.board or ""}

        try:
            memory = await ctx.mc.list_memory(board_id, limit=10)
            result["recent_memory"] = [
                {"content": m.content[:200], "tags": m.tags, "source": m.source}
                for m in memory
            ]
        except Exception:
            result["recent_memory"] = []

        return result

    @server.tool()
    async def fleet_task_accept(plan: str, task_id: str = "") -> dict:
        """Accept and start working on your assigned task.

        Args:
            plan: Brief description of your approach (1-2 sentences).
            task_id: Task ID (if not already set via fleet_read_context).
        """
        ctx = _get_ctx()
        if task_id:
            ctx.task_id = task_id
        if not ctx.task_id:
            return {"ok": False, "error": "No task_id. Call fleet_read_context first."}

        board_id = await ctx.resolve_board_id()

        comment = f"## ▶️ Accepted\n\n**Plan:** {plan}\n\n---\n<sub>{ctx.agent_name or 'agent'}</sub>"

        try:
            task = await ctx.mc.update_task(
                board_id, ctx.task_id,
                status="in_progress",
                comment=comment,
                custom_fields={"agent_name": ctx.agent_name} if ctx.agent_name else None,
            )
        except Exception as e:
            return {"ok": False, "error": str(e)}

        task_url = ctx.urls.task_url(ctx.task_id) if ctx.task_id else ""
        try:
            await ctx.irc.notify_event(
                agent=ctx.agent_name or "agent",
                event="▶️ STARTED",
                title=task.title,
                url=task_url,
            )
        except Exception:
            pass

        return {"ok": True, "status": "in_progress", "task_url": task_url}

    @server.tool()
    async def fleet_task_progress(done: str, next_step: str, blockers: str = "none") -> dict:
        """Post a progress update on your current task.

        Args:
            done: What you've completed so far.
            next_step: What you're working on next.
            blockers: Any blockers (or "none").
        """
        ctx = _get_ctx()
        if not ctx.task_id:
            return {"ok": False, "error": "No task_id. Call fleet_read_context first."}
        board_id = await ctx.resolve_board_id()

        comment = (
            f"## 🔄 Progress Update\n\n"
            f"**Done:** {done}\n"
            f"**Next:** {next_step}\n"
            f"**Blockers:** {blockers}\n\n"
            f"---\n<sub>{ctx.agent_name or 'agent'}</sub>"
        )

        try:
            await ctx.mc.post_comment(board_id, ctx.task_id, comment)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        return {"ok": True}

    @server.tool()
    async def fleet_commit(files: list[str], message: str) -> dict:
        """Commit changes with conventional format and task reference.

        Args:
            files: List of file paths to stage (relative to worktree).
            message: Commit message in conventional format (e.g., "feat(core): add type hints").
                     Task reference is added automatically.
        """
        ctx = _get_ctx()
        task_ref = f" [task:{ctx.task_id[:8]}]" if ctx.task_id else ""
        full_msg = f"{message}{task_ref}"
        cwd = ctx.worktree or "."

        for f in files:
            await ctx.gh._run(["git", "add", f], cwd=cwd)

        ok, output = await ctx.gh._run(["git", "commit", "-m", full_msg], cwd=cwd)

        if ok:
            _, sha = await ctx.gh._run(["git", "rev-parse", "HEAD"], cwd=cwd)
            return {"ok": True, "sha": sha.strip()[:7], "message": full_msg}
        else:
            return {"ok": False, "error": output}

    @server.tool()
    async def fleet_task_complete(summary: str) -> dict:
        """Complete your task: push branch, create PR, update MC, notify IRC.

        One call does everything:
        1. Push branch to remote
        2. Create PR with changelog and diff table
        3. Set task custom fields (branch, pr_url)
        4. Post structured completion comment
        5. Notify IRC #fleet and #reviews
        6. Post to board memory
        7. Move task to review

        Args:
            summary: What you did and why (2-3 sentences).
        """
        ctx = _get_ctx()
        if not ctx.task_id:
            return {"ok": False, "error": "No task_id. Call fleet_read_context first."}
        board_id = await ctx.resolve_board_id()
        cwd = ctx.worktree

        # Detect worktree from filesystem if not set
        if not cwd:
            import os
            fleet_dir = os.environ.get("FLEET_DIR", ".")
            short = ctx.task_id[:8]
            for proj_dir in os.listdir(os.path.join(fleet_dir, "projects")) if os.path.isdir(os.path.join(fleet_dir, "projects")) else []:
                wt_dir = os.path.join(fleet_dir, "projects", proj_dir, "worktrees")
                if os.path.isdir(wt_dir):
                    for wt in os.listdir(wt_dir):
                        if wt.endswith(f"-{short}"):
                            cwd = os.path.join(wt_dir, wt)
                            ctx.worktree = cwd
                            break

        if not cwd:
            # No worktree — internal task, just complete
            comment = (
                f"## ✅ Completed\n\n"
                f"### Summary\n{summary}\n\n"
                f"---\n<sub>{ctx.agent_name or 'agent'}</sub>"
            )
            try:
                await ctx.mc.update_task(
                    board_id, ctx.task_id, status="review", comment=comment,
                )
            except Exception as e:
                return {"ok": False, "error": str(e)}
            return {"ok": True, "status": "review", "pr": None}

        # Get branch
        _, branch = await ctx.gh._run(["git", "branch", "--show-current"], cwd=cwd)
        branch = branch.strip()

        # Get commits and diff
        commits = await ctx.gh.get_branch_commits(cwd)
        diff_stat = await ctx.gh.get_diff_stat(cwd)

        if not commits:
            # No commits — nothing to push/PR
            comment = (
                f"## ✅ Completed (no code changes)\n\n"
                f"### Summary\n{summary}\n\n"
                f"---\n<sub>{ctx.agent_name or 'agent'}</sub>"
            )
            try:
                await ctx.mc.update_task(
                    board_id, ctx.task_id, status="review", comment=comment,
                )
            except Exception as e:
                return {"ok": False, "error": str(e)}
            return {"ok": True, "status": "review", "pr": None, "reason": "no commits"}

        # Push
        push_ok = await ctx.gh.push_branch(cwd, branch)
        if not push_ok:
            return {"ok": False, "error": "Push failed. Check git remote auth."}

        # Resolve URLs
        task_url = ctx.urls.task_url(ctx.task_id)
        urls = ctx.urls.resolve(
            project=ctx.project_name,
            task_id=ctx.task_id,
            branch=branch,
            commits=[c["sha"] for c in commits],
            files=[f["path"] for f in diff_stat],
        )

        # Build changelog
        changelog_lines = []
        for c in commits:
            parsed = ctx.gh.parse_commit(c["sha"], c["message"])
            emoji = {"feat": "✨", "fix": "🐛", "docs": "📚", "test": "🧪",
                     "refactor": "♻️", "chore": "🔧"}.get(
                parsed.commit_type.value if parsed.commit_type else "", "📝"
            )
            sha_url = ""
            for cu in (urls.commits or []):
                if cu["sha"] == c["sha"]:
                    sha_url = cu["url"]
                    break
            sha_link = f"[`{parsed.short_sha}`]({sha_url})" if sha_url else f"`{parsed.short_sha}`"
            changelog_lines.append(f"- {emoji} {parsed.message} ({sha_link})")

        # Build file table
        file_rows = []
        for f in diff_stat:
            file_url = ctx.urls.file_url(ctx.project_name, branch, f["path"])
            link = f"[`{f['path']}`]({file_url})" if file_url else f"`{f['path']}`"
            file_rows.append(f"| {link} | +{f['added']}/-{f['removed']} |")

        # Get task title
        try:
            task = await ctx.mc.get_task(board_id, ctx.task_id)
            task_title = task.title
        except Exception:
            task_title = ctx.task_id[:8]

        # Build PR body
        pr_body = (
            f"## 📋 Summary\n\n{summary}\n\n"
            f"## 📝 Changelog\n\n" + "\n".join(changelog_lines) + "\n\n"
            f"## 📊 Changes\n\n| File | Lines |\n|------|-------|\n"
            + "\n".join(file_rows) + "\n\n"
            f"## 🔗 References\n\n"
            f"| | |\n|---|---|\n"
            f"| **Task** | [{ctx.task_id[:8]}]({task_url}) |\n"
            f"| **Agent** | {ctx.agent_name or 'agent'} |\n"
            f"| **Branch** | [`{branch}`]({urls.compare or ''}) |\n\n"
            f"---\n<sub>Generated by OpenClaw Fleet</sub>"
        )

        # Create PR
        try:
            pr = await ctx.gh.create_pr(
                cwd,
                title=f"fleet({ctx.agent_name or 'agent'}): {task_title}",
                body=pr_body,
            )
        except Exception as e:
            return {"ok": False, "error": f"PR creation failed: {e}"}

        # Update MC custom fields
        try:
            await ctx.mc.update_task(
                board_id, ctx.task_id,
                custom_fields={"branch": branch, "pr_url": pr.url},
            )
        except Exception:
            pass

        # Completion comment
        files_list = ", ".join(f"`{f['path']}`" for f in diff_stat[:5])
        more = f" (+{len(diff_stat) - 5} more)" if len(diff_stat) > 5 else ""
        comment = (
            f"## ✅ Completed\n\n"
            f"**PR:** [{pr.url}]({pr.url})\n"
            f"**Branch:** [`{branch}`]({urls.compare or ''})\n"
            f"**Commits:** {len(commits)}\n"
            f"**Files:** {files_list}{more}\n\n"
            f"### Summary\n{summary}\n\n"
            f"---\n<sub>{ctx.agent_name or 'agent'}</sub>"
        )
        try:
            await ctx.mc.update_task(
                board_id, ctx.task_id, status="review", comment=comment,
            )
        except Exception:
            pass

        # IRC notifications
        try:
            await ctx.irc.notify_event(
                agent=ctx.agent_name or "agent", event="✅ PR READY",
                title=task_title, url=pr.url,
            )
            await ctx.irc.notify_event(
                agent=ctx.agent_name or "agent", event="🔀 PR",
                title=task_title, url=pr.url, channel="#reviews",
            )
        except Exception:
            pass

        # Board memory
        try:
            await ctx.mc.post_memory(
                board_id,
                content=(
                    f"## 🔀 PR Ready: {task_title}\n\n"
                    f"**PR:** [{pr.url}]({pr.url})\n"
                    f"**Agent:** {ctx.agent_name or 'agent'}\n"
                    f"**Branch:** [`{branch}`]({urls.compare or ''})\n"
                ),
                tags=["pr", "review", f"project:{ctx.project_name}"],
                source=ctx.agent_name or "agent",
            )
        except Exception:
            pass

        return {
            "ok": True,
            "pr_url": pr.url,
            "pr_number": pr.number,
            "branch": branch,
            "commits": len(commits),
            "files_changed": len(diff_stat),
            "status": "review",
        }

    @server.tool()
    async def fleet_alert(
        severity: str, title: str, details: str, category: str = "quality"
    ) -> dict:
        """Raise an alert for security, quality, or architecture concerns.

        Args:
            severity: "critical", "high", "medium", or "low"
            title: Short alert title.
            details: Detailed description with evidence.
            category: "security", "quality", "architecture", "workflow", "tooling"
        """
        ctx = _get_ctx()
        board_id = await ctx.resolve_board_id()

        content = (
            f"## ⚠️ {severity.upper()}: {title}\n\n"
            f"**Found by:** {ctx.agent_name or 'agent'}\n"
            f"**Severity:** {severity}\n"
            f"**Category:** {category}\n\n"
            f"### Details\n{details}\n"
        )

        try:
            await ctx.mc.post_memory(
                board_id, content=content,
                tags=["alert", severity, category, f"project:{ctx.project_name}"],
                source=ctx.agent_name or "agent",
            )
        except Exception as e:
            return {"ok": False, "error": str(e)}

        channel = "#alerts" if severity in ("critical", "high") else "#fleet"
        emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(severity, "⚠️")
        try:
            await ctx.irc.notify(channel, f"{emoji} [{ctx.agent_name or 'agent'}] {severity.upper()}: {title}")
        except Exception:
            pass

        return {"ok": True, "severity": severity, "channel": channel}

    @server.tool()
    async def fleet_pause(reason: str, needed: str) -> dict:
        """Pause work and escalate. Use when stuck, uncertain, or blocked.

        Args:
            reason: Why you're pausing (specific).
            needed: What would unblock you (who needs to do what).
        """
        ctx = _get_ctx()
        if not ctx.task_id:
            return {"ok": False, "error": "No task_id."}
        board_id = await ctx.resolve_board_id()

        comment = (
            f"## 🚫 Blocked\n\n"
            f"**Reason:** {reason}\n"
            f"**Needed:** {needed}\n\n"
            f"---\n<sub>{ctx.agent_name or 'agent'}</sub>"
        )
        try:
            await ctx.mc.post_comment(board_id, ctx.task_id, comment)
        except Exception as e:
            return {"ok": False, "error": str(e)}

        task_url = ctx.urls.task_url(ctx.task_id) if ctx.task_id else ""
        try:
            await ctx.irc.notify_event(
                agent=ctx.agent_name or "agent", event="🚫 BLOCKED",
                title=reason[:60], url=task_url,
            )
        except Exception:
            pass

        return {"ok": True, "action": "Wait for human input."}