"""Fleet sprint management — load plans and check status.

Usage:
  python -m fleet sprint load config/sprints/dspd-s1.yaml
  python -m fleet sprint status <plan-id>
"""

from __future__ import annotations

import asyncio
import sys

import yaml

from fleet.core.models import TaskStatus
from fleet.infra.config_loader import ConfigLoader
from fleet.infra.mc_client import MCClient


async def _load_sprint(plan_path: str) -> int:
    """Load a sprint plan and create tasks in MC with dependencies."""
    with open(plan_path) as f:
        plan = yaml.safe_load(f)

    sprint_info = plan.get("sprint", {})
    sprint_id = sprint_info.get("id", "")
    sprint_name = sprint_info.get("name", sprint_id)
    task_defs = plan.get("tasks", [])

    if not task_defs:
        print("ERROR: No tasks in sprint plan")
        return 1

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

    # Resolve agent name → ID mapping
    agents = await mc.list_agents()
    agent_id_map = {a.name: a.id for a in agents}

    # Create tasks in order, tracking local_id → MC task ID
    id_map: dict[str, str] = {}
    created = 0

    print(f"Loading sprint: {sprint_name} ({sprint_id})")
    print(f"  Tasks: {len(task_defs)}")
    print()

    for task_def in task_defs:
        local_id = task_def.get("id", "")
        title = task_def.get("title", "")

        # Resolve MC task IDs for dependencies
        depends_on = []
        for dep_local_id in task_def.get("depends_on", []):
            mc_id = id_map.get(dep_local_id)
            if mc_id:
                depends_on.append(mc_id)

        # Resolve parent
        parent_local = task_def.get("parent", "")
        parent_mc_id = id_map.get(parent_local, "")

        # Resolve agent
        agent_name = task_def.get("agent", "")
        agent_id = agent_id_map.get(agent_name)

        # Build custom fields
        custom_fields: dict = {
            "plan_id": sprint_id,
            "task_type": task_def.get("type", "task"),
            "sprint": sprint_id,
        }
        if parent_mc_id:
            custom_fields["parent_task"] = parent_mc_id
        if agent_name:
            custom_fields["agent_name"] = agent_name
        if task_def.get("project"):
            custom_fields["project"] = task_def["project"]
        if task_def.get("story_points"):
            custom_fields["story_points"] = task_def["story_points"]

        try:
            task = await mc.create_task(
                board_id,
                title=title,
                description=task_def.get("description", ""),
                priority=task_def.get("priority", "medium"),
                assigned_agent_id=agent_id or None,
                custom_fields=custom_fields,
                depends_on=depends_on if depends_on else None,
                auto_created=True,
                auto_reason=f"Sprint plan: {sprint_id}",
            )
            id_map[local_id] = task.id
            created += 1

            blocked = " [BLOCKED]" if depends_on else ""
            agent_str = f" → {agent_name}" if agent_name else ""
            print(f"  CREATED: {title[:50]}{agent_str}{blocked}")
            print(f"           {task.id[:8]}")
        except Exception as e:
            print(f"  ERROR: {title[:50]} — {e}")

    print(f"\nSprint {sprint_id}: {created}/{len(task_defs)} tasks created")
    await mc.close()
    return 0


async def _sprint_status(plan_id: str) -> int:
    """Show status of a sprint plan."""
    loader = ConfigLoader()
    env = loader.load_env()
    token = env.get("LOCAL_AUTH_TOKEN", "")
    if not token:
        print("ERROR: No LOCAL_AUTH_TOKEN")
        return 1

    mc = MCClient(token=token)
    board_id = await mc.get_board_id()
    if not board_id:
        await mc.close()
        return 1

    tasks = await mc.list_tasks(board_id)
    sprint_tasks = [
        t for t in tasks
        if t.custom_fields.plan_id == plan_id
        or t.custom_fields.sprint == plan_id
    ]

    if not sprint_tasks:
        print(f"No tasks found for plan: {plan_id}")
        await mc.close()
        return 1

    # Count by status
    counts: dict[str, int] = {}
    total_points = 0
    done_points = 0
    blocked = 0

    for t in sprint_tasks:
        s = t.status.value
        counts[s] = counts.get(s, 0) + 1
        sp = t.custom_fields.story_points or 0
        total_points += sp
        if t.status == TaskStatus.DONE:
            done_points += sp
        if t.is_blocked:
            blocked += 1

    print(f"Sprint: {plan_id}")
    print(f"  Tasks: {len(sprint_tasks)}")
    for status in ["inbox", "in_progress", "review", "done"]:
        c = counts.get(status, 0)
        if c:
            print(f"    {status:15s} {c}")
    if blocked:
        print(f"    {'blocked':15s} {blocked}")
    if total_points:
        pct = (done_points / total_points * 100) if total_points else 0
        print(f"  Story Points: {done_points}/{total_points} ({pct:.0f}%)")

    print()
    for t in sprint_tasks:
        status_icon = {
            "inbox": "📥", "in_progress": "🔄",
            "review": "👀", "done": "✅",
        }.get(t.status.value, "❓")
        blocked_str = " 🚫" if t.is_blocked else ""
        agent = t.custom_fields.agent_name or ""
        print(f"  {status_icon} {t.title[:50]:50s} {agent:20s}{blocked_str}")

    await mc.close()
    return 0


def run_sprint(args: list[str] | None = None) -> int:
    """Entry point for fleet sprint."""
    argv = args if args is not None else sys.argv[2:]
    if not argv or argv[0] not in ("load", "status"):
        print("Usage:")
        print("  fleet sprint load <plan.yaml>")
        print("  fleet sprint status <plan-id>")
        return 1

    if argv[0] == "load" and len(argv) > 1:
        return asyncio.run(_load_sprint(argv[1]))
    elif argv[0] == "status" and len(argv) > 1:
        return asyncio.run(_sprint_status(argv[1]))

    print("Usage:")
    print("  fleet sprint load <plan.yaml>")
    print("  fleet sprint status <plan-id>")
    return 1