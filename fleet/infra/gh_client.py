"""Fleet GitHub client.

Implements core.interfaces.GitClient.
Uses the `gh` CLI and `git` for operations.
"""

from __future__ import annotations

import asyncio
import json
from typing import Optional

from fleet.core.interfaces import GitClient
from fleet.core.models import Commit, CommitType, PullRequest


class GHClient(GitClient):
    """GitHub and git operations via subprocess."""

    async def push_branch(self, worktree: str, branch: str) -> bool:
        """Push a branch to remote."""
        ok, _ = await self._run(
            ["git", "push", "-u", "origin", branch], cwd=worktree
        )
        return ok

    async def create_pr(
        self,
        worktree: str,
        *,
        title: str,
        body: str,
    ) -> PullRequest:
        """Create a pull request via gh CLI."""
        ok, output = await self._run(
            ["gh", "pr", "create", "--title", title, "--body", body],
            cwd=worktree,
        )
        if not ok:
            raise RuntimeError(f"PR creation failed: {output}")

        # gh pr create outputs the PR URL
        pr_url = output.strip()

        # Get PR number from URL
        pr_number = 0
        if "/pull/" in pr_url:
            try:
                pr_number = int(pr_url.rstrip("/").split("/")[-1])
            except ValueError:
                pass

        # Get branch name
        _, branch_out = await self._run(
            ["git", "branch", "--show-current"], cwd=worktree
        )

        return PullRequest(
            url=pr_url,
            number=pr_number,
            title=title,
            branch=branch_out.strip(),
        )

    async def get_pr_state(self, pr_url: str) -> Optional[str]:
        """Check PR state: OPEN, CLOSED, or MERGED."""
        ok, output = await self._run(
            ["gh", "pr", "view", pr_url, "--json", "state,mergedAt"]
        )
        if not ok:
            return None
        try:
            data = json.loads(output)
            return data.get("state", "").upper()
        except (json.JSONDecodeError, KeyError):
            return None

    async def merge_pr(self, pr_url: str) -> bool:
        """Merge a PR via gh CLI."""
        ok, _ = await self._run(
            ["gh", "pr", "merge", pr_url, "--squash", "--delete-branch"]
        )
        return ok

    async def get_branch_commits(
        self, worktree: str, base: str = "origin/main"
    ) -> list[dict]:
        """Get commits on branch since base."""
        ok, output = await self._run(
            ["git", "log", f"{base}..HEAD", "--format=%H|%s"],
            cwd=worktree,
        )
        if not ok or not output.strip():
            return []

        commits = []
        for line in output.strip().split("\n"):
            if "|" in line:
                sha, msg = line.split("|", 1)
                commit = {"sha": sha.strip(), "message": msg.strip()}
                commits.append(commit)
        return commits

    async def get_diff_stat(
        self, worktree: str, base: str = "origin/main"
    ) -> list[dict]:
        """Get diff stat with line counts per file."""
        ok, output = await self._run(
            ["git", "diff", "--numstat", f"{base}..HEAD"],
            cwd=worktree,
        )
        if not ok or not output.strip():
            return []

        files = []
        for line in output.strip().split("\n"):
            parts = line.split("\t")
            if len(parts) == 3:
                added, removed, path = parts
                files.append({
                    "path": path,
                    "added": int(added) if added != "-" else 0,
                    "removed": int(removed) if removed != "-" else 0,
                })
        return files

    def parse_commit(self, sha: str, message: str) -> Commit:
        """Parse a commit message into a Commit model."""
        import re

        commit = Commit(sha=sha, message=message)

        # Parse conventional commit: type(scope): description [task:ref]
        pattern = r"^(\w+)(?:\(([^)]+)\))?: (.+?)(?:\s*\[task:(\w+)\])?$"
        match = re.match(pattern, message)
        if match:
            try:
                commit.commit_type = CommitType(match.group(1))
            except ValueError:
                pass
            commit.scope = match.group(2)
            commit.description = match.group(3)
            commit.task_ref = match.group(4)

        return commit

    # ─── Internal ───────────────────────────────────────────────────────

    @staticmethod
    async def _run(
        cmd: list[str], cwd: Optional[str] = None
    ) -> tuple[bool, str]:
        """Run a subprocess command."""
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=30
            )
            output = stdout.decode().strip()
            if proc.returncode != 0:
                output = stderr.decode().strip() or output
            return proc.returncode == 0, output
        except (asyncio.TimeoutError, FileNotFoundError, OSError) as e:
            return False, str(e)