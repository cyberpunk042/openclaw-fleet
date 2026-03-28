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

    # Pass 1: Create all tasks without dependencies
    print("\n  Creating tasks...")
    for task_def in task_defs:
        local_id = task_def.get("id", "")
        title = task_def.get("title", "")
        agent_name = task_def.get("agent", "")
        agent_id = agent_id_map.get(agent_name)

        parent_local = task_def.get("parent", "")
        parent_mc_id = id_map.get(parent_local, "")

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
            )
            id_map[local_id] = task.id
            created += 1
            agent_str = f" → {agent_name}" if agent_name else ""
            print(f"    {local_id:15s} {title[:45]}{agent_str}")
        except Exception as e:
            print(f"    ERROR {local_id}: {e}")

    # Pass 2: Wire dependencies via update_task
    deps_defs = [td for td in task_defs if td.get("depends_on")]
    if deps_defs:
        print(f"\n  Wiring {len(deps_defs)} dependencies...")
        for task_def in deps_defs:
            local_id = task_def.get("id", "")
            mc_id = id_map.get(local_id)
            if not mc_id:
                continue

            dep_mc_ids = [
                id_map[d] for d in task_def["depends_on"] if d in id_map
            ]
            if not dep_mc_ids:
                continue

            try:
                await mc.update_task(board_id, mc_id, depends_on=dep_mc_ids)
                dep_labels = task_def["depends_on"]
                print(f"    {local_id} ← {dep_labels}")
            except Exception as e:
                print(f"    ERROR {local_id}: {e}")

    print(f"\nSprint {sprint_id}: {created} tasks created")
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

    # Use velocity module for comprehensive metrics
    from fleet.core.velocity import (
        compute_agent_metrics,
        compute_sprint_metrics,
        format_agent_report,
        format_sprint_report,
    )

    metrics = compute_sprint_metrics(tasks, plan_id)
    print(format_sprint_report(metrics))

    # Task list
    print()
    for t in sprint_tasks:
        status_icon = {
            "inbox": "\U0001f4e5", "in_progress": "\U0001f504",
            "review": "\U0001f440", "done": "\u2705",
        }.get(t.status.value, "\u2753")
        blocked_str = " \U0001f6ab" if t.is_blocked else ""
        agent = t.custom_fields.agent_name or ""
        sp = f"({t.custom_fields.story_points}sp)" if t.custom_fields.story_points else ""
        print(f"  {status_icon} {t.title[:45]:45s} {agent:18s} {sp}{blocked_str}")

    # Agent performance for this sprint
    sprint_agent_tasks = [t for t in tasks if t.custom_fields.plan_id == plan_id or t.custom_fields.sprint == plan_id]
    agent_metrics = compute_agent_metrics(sprint_agent_tasks)
    if agent_metrics:
        print()
        print(format_agent_report(agent_metrics))

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