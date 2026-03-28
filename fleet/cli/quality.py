"""Fleet quality check — validate standards compliance.

Replaces: scripts/fleet-quality-check.sh
Usage: python -m fleet quality
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import sys

from fleet.infra.config_loader import ConfigLoader
from fleet.infra.gh_client import GHClient
from fleet.infra.mc_client import MCClient

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
NC = "\033[0m"

CONVENTIONAL_RE = re.compile(
    r"^(feat|fix|docs|refactor|test|chore|ci|style|perf)(\([^)]+\))?: .+"
)


async def _run_quality() -> int:
    """Execute quality checks."""
    loader = ConfigLoader()
    env = loader.load_env()
    token = env.get("LOCAL_AUTH_TOKEN", "")
    gh = GHClient()

    print(f"{BOLD}=== Fleet Quality Check ==={NC}\n")

    violations = 0
    passes = 0

    # 1. Check commits in worktrees
    print(f"{BOLD}📝 Commit Messages{NC}")
    fleet_dir = os.environ.get("FLEET_DIR", ".")
    projects_dir = os.path.join(fleet_dir, "projects")
    if os.path.isdir(projects_dir):
        for project in os.listdir(projects_dir):
            wt_dir = os.path.join(projects_dir, project, "worktrees")
            if not os.path.isdir(wt_dir):
                continue
            for wt in os.listdir(wt_dir):
                wt_path = os.path.join(wt_dir, wt)
                commits = await gh.get_branch_commits(wt_path)
                for c in commits:
                    if CONVENTIONAL_RE.match(c["message"]):
                        passes += 1
                    else:
                        print(f"  {RED}❌{NC} {wt}: '{c['message'][:60]}'")
                        violations += 1
    if violations == 0:
        print(f"  {GREEN}✅ All commits follow conventional format{NC}")
    print()

    # 2. Check board state
    if token:
        mc = MCClient(token=token)
        board_id = await mc.get_board_id()

        if board_id:
            print(f"{BOLD}📋 Task Custom Fields{NC}")
            tasks = await mc.list_tasks(board_id)
            missing_project = sum(1 for t in tasks if not t.custom_fields.project)
            review_no_pr = sum(
                1 for t in tasks
                if t.status.value == "review" and not t.custom_fields.pr_url
            )
            if missing_project:
                print(f"  {YELLOW}⚠️  {missing_project} tasks without project field{NC}")
            else:
                print(f"  {GREEN}✅ All tasks have project field{NC}")
            if review_no_pr:
                print(f"  {YELLOW}⚠️  {review_no_pr} review tasks without pr_url{NC}")
            else:
                review_count = sum(1 for t in tasks if t.status.value == "review")
                if review_count:
                    print(f"  {GREEN}✅ All {review_count} review tasks have pr_url{NC}")
            print()

            print(f"{BOLD}🏷️  Board Memory Tags{NC}")
            memory = await mc.list_memory(board_id, limit=20)
            untagged = sum(1 for m in memory if not m.tags)
            tagged = sum(1 for m in memory if m.tags)
            if untagged:
                print(f"  {YELLOW}⚠️  {untagged} entries without tags{NC}")
            else:
                print(f"  {GREEN}✅ All {tagged} entries tagged{NC}")
            print()

            print(f"{BOLD}✅ Approvals{NC}")
            approvals = await mc.list_approvals(board_id)
            pending = sum(1 for a in approvals if a.status == "pending")
            approved = sum(1 for a in approvals if a.status == "approved")
            print(f"  Pending: {pending}, Approved: {approved}")
            print()

        await mc.close()

    # Summary
    print(f"{BOLD}{'=' * 40}{NC}")
    print(f"Passes: {passes}")
    print(f"Violations: {violations}")

    return 0 if violations == 0 else 1


def run_quality() -> int:
    """Entry point for fleet quality."""
    return asyncio.run(_run_quality())