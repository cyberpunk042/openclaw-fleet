"""Fleet board management — board config, task cleanup, tag/field listing.

Usage:
  python -m fleet board info          # show board config
  python -m fleet board tasks         # list all tasks with status
  python -m fleet board cleanup       # close stale tasks, remove orphans
  python -m fleet board tags          # list all tags
  python -m fleet board fields        # list custom fields
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timezone

from fleet.infra.config_loader import ConfigLoader
from fleet.infra.mc_client import MCClient

BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
DIM = "\033[2m"
NC = "\033[0m"


async def _board_info(mc: MCClient, board_id: str) -> int:
    """Show board configuration."""
    import urllib.request
    import json

    env = ConfigLoader().load_env()
    token = env.get("LOCAL_AUTH_TOKEN", "")
    req = urllib.request.Request(f"http://localhost:8000/api/v1/boards/{board_id}")
    req.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(req, timeout=5) as resp:
        board = json.loads(resp.read())

    print(f"{BOLD}Board: {board.get('name')}{NC}")
    print(f"  ID: {board_id}")
    print()

    policies = [
        ("require_approval_for_done", "Approval required for done"),
        ("require_review_before_done", "Review required before done"),
        ("comment_required_for_review", "Comment required for review"),
        ("block_status_changes_with_pending_approval", "Block changes with pending approval"),
        ("only_lead_can_change_status", "Only lead can change status"),
    ]
    print(f"{BOLD}Policies{NC}")
    for key, label in policies:
        val = board.get(key, False)
        color = GREEN if val else DIM
        print(f"  {color}{'✓' if val else '✗'}{NC} {label}")

    return 0


async def _board_tasks(mc: MCClient, board_id: str) -> int:
    """List all tasks with details."""
    tasks = await mc.list_tasks(board_id)
    colors = {"inbox": YELLOW, "in_progress": CYAN, "review": MAGENTA, "done": GREEN}

    counts: dict[str, int] = {}
    for t in tasks:
        s = t.status.value
        counts[s] = counts.get(s, 0) + 1
        color = colors.get(s, NC)
        pr = f" PR:{DIM}{t.custom_fields.pr_url}{NC}" if t.custom_fields.pr_url else ""
        proj = f" [{t.custom_fields.project}]" if t.custom_fields.project else ""
        agent = f" @{t.custom_fields.agent_name}" if t.custom_fields.agent_name else ""
        print(f"  {color}{s:12s}{NC} {t.title[:45]}{proj}{agent}{pr}")

    print()
    summary = ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
    print(f"  {DIM}{summary} ({len(tasks)} total){NC}")
    return 0


async def _board_cleanup(mc: MCClient, board_id: str) -> int:
    """Clean up stale tasks."""
    tasks = await mc.list_tasks(board_id)
    now = datetime.now(timezone.utc)
    actions = 0

    print(f"{BOLD}Board Cleanup{NC}")

    # Find tasks that are stale
    for t in tasks:
        hours = 0
        if t.updated_at:
            hours = (now - t.updated_at).total_seconds() / 3600

        # Old inbox tasks (> 48h)
        if t.status.value == "inbox" and hours > 48:
            print(f"  {YELLOW}STALE INBOX{NC}: {t.title[:50]} ({int(hours)}h)")
            actions += 1

        # Review tasks without PR (> 24h) — likely completed without PR
        if t.status.value == "review" and not t.custom_fields.pr_url and hours > 24:
            print(f"  {YELLOW}REVIEW NO PR{NC}: {t.title[:50]} ({int(hours)}h)")
            actions += 1

    if actions == 0:
        print(f"  {GREEN}Board is clean{NC}")
    else:
        print(f"\n  {actions} items need attention")
        print(f"  {DIM}Use MC dashboard to resolve these manually{NC}")

    return 0


async def _board_tags(mc: MCClient, board_id: str) -> int:
    """List all tags."""
    import urllib.request
    import json

    env = ConfigLoader().load_env()
    token = env.get("LOCAL_AUTH_TOKEN", "")
    req = urllib.request.Request("http://localhost:8000/api/v1/tags")
    req.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read())

    items = data.get("items", data) if isinstance(data, dict) else data
    print(f"{BOLD}Tags ({len(items)}){NC}")
    for tag in items:
        name = tag.get("name", "?")
        color = tag.get("color", "")
        count = tag.get("task_count", 0)
        print(f"  {name:30s} tasks={count} color=#{color}")

    return 0


async def _board_fields(mc: MCClient, board_id: str) -> int:
    """List custom fields."""
    import urllib.request
    import json

    env = ConfigLoader().load_env()
    token = env.get("LOCAL_AUTH_TOKEN", "")
    req = urllib.request.Request("http://localhost:8000/api/v1/organizations/me/custom-fields")
    req.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read())

    items = data.get("items", data) if isinstance(data, dict) else data
    print(f"{BOLD}Custom Fields ({len(items)}){NC}")
    for field in items:
        key = field.get("field_key", "?")
        ftype = field.get("field_type", "?")
        vis = field.get("ui_visibility", "?")
        print(f"  {key:20s} type={ftype:8s} visibility={vis}")

    return 0


async def _run_board(action: str) -> int:
    loader = ConfigLoader()
    env = loader.load_env()
    token = env.get("LOCAL_AUTH_TOKEN", "")

    if not token:
        print("ERROR: No LOCAL_AUTH_TOKEN")
        return 1

    mc = MCClient(token=token)
    board_id = await mc.get_board_id()
    if not board_id:
        print("ERROR: No board found")
        await mc.close()
        return 1

    actions = {
        "info": _board_info,
        "tasks": _board_tasks,
        "cleanup": _board_cleanup,
        "tags": _board_tags,
        "fields": _board_fields,
    }

    handler = actions.get(action)
    if not handler:
        print(f"Unknown action: {action}")
        print(f"Available: {', '.join(sorted(actions))}")
        await mc.close()
        return 1

    result = await handler(mc, board_id)
    await mc.close()
    return result


def run_board(args: list[str] | None = None) -> int:
    """Entry point for fleet board."""
    argv = args if args is not None else sys.argv[2:]
    action = argv[0] if argv else "info"
    return asyncio.run(_run_board(action))