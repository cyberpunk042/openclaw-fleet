"""Role providers — per-role data functions for heartbeat context.

Each agent role gets different data in their heartbeat. Fleet-ops gets
pending approvals. PM gets unassigned tasks. Architect gets design
reviews. Each provider returns a dict of role-relevant data.

Providers are async functions with signature:
    async def provider(agent_name, tasks, agents, mc, board_id) -> dict
"""

from __future__ import annotations

from fleet.core.models import Task, TaskStatus


async def fleet_ops_provider(
    agent_name: str,
    tasks: list[Task],
    agents: list,
    mc,
    board_id: str,
) -> dict:
    """Fleet-ops: approvals, review queue, health."""
    review_tasks = [t for t in tasks if t.status == TaskStatus.REVIEW]
    pending_approvals = []
    try:
        approvals = await mc.list_approvals(board_id)
        pending_approvals = [
            {"id": a.id, "task_id": a.task_ids[0] if a.task_ids else "", "status": a.status}
            for a in (approvals or [])
            if a.status == "pending"
        ]
    except Exception:
        pass

    return {
        "pending_approvals": len(pending_approvals),
        "approval_details": pending_approvals[:5],
        "review_queue": [
            {"id": t.id[:8], "title": t.title[:40], "agent": t.custom_fields.agent_name or ""}
            for t in review_tasks[:10]
        ],
        "offline_agents": [
            a.name for a in agents
            if a.status != "online" and "Gateway" not in a.name
        ],
    }


async def project_manager_provider(
    agent_name: str,
    tasks: list[Task],
    agents: list,
    mc,
    board_id: str,
) -> dict:
    """PM: unassigned tasks, sprint progress, blocked tasks."""
    inbox = [t for t in tasks if t.status == TaskStatus.INBOX]
    unassigned = [t for t in inbox if not t.custom_fields.agent_name]
    blocked = [t for t in tasks if t.is_blocked]
    done = [t for t in tasks if t.status == TaskStatus.DONE]
    total = len(tasks)

    return {
        "unassigned_tasks": len(unassigned),
        "unassigned_details": [
            {"id": t.id[:8], "title": t.title[:40], "priority": t.priority}
            for t in unassigned[:10]
        ],
        "blocked_tasks": len(blocked),
        "progress": f"{len(done)}/{total} done ({len(done)*100//total if total else 0}%)",
        "inbox_count": len(inbox),
    }


async def architect_provider(
    agent_name: str,
    tasks: list[Task],
    agents: list,
    mc,
    board_id: str,
) -> dict:
    """Architect: tasks needing design, complexity flags."""
    design_tasks = [
        t for t in tasks
        if t.custom_fields.task_type in ("epic", "story")
        and t.custom_fields.task_stage in ("analysis", "investigation", "reasoning")
    ]
    high_complexity = [
        t for t in tasks
        if t.custom_fields.complexity == "high"
        and t.status in (TaskStatus.INBOX, TaskStatus.IN_PROGRESS)
    ]

    return {
        "design_tasks": [
            {"id": t.id[:8], "title": t.title[:40], "stage": t.custom_fields.task_stage}
            for t in design_tasks[:5]
        ],
        "high_complexity": [
            {"id": t.id[:8], "title": t.title[:40]}
            for t in high_complexity[:5]
        ],
    }


async def devsecops_provider(
    agent_name: str,
    tasks: list[Task],
    agents: list,
    mc,
    board_id: str,
) -> dict:
    """DevSecOps: security tasks, PR reviews needed."""
    security_tasks = [
        t for t in tasks
        if "security" in (t.tags or [])
        and t.status in (TaskStatus.INBOX, TaskStatus.IN_PROGRESS)
    ]
    review_prs = [
        t for t in tasks
        if t.status == TaskStatus.REVIEW and t.custom_fields.pr_url
    ]

    return {
        "security_tasks": [
            {"id": t.id[:8], "title": t.title[:40]}
            for t in security_tasks[:5]
        ],
        "prs_needing_security_review": [
            {"id": t.id[:8], "title": t.title[:40], "pr": t.custom_fields.pr_url}
            for t in review_prs[:5]
        ],
    }


async def worker_provider(
    agent_name: str,
    tasks: list[Task],
    agents: list,
    mc,
    board_id: str,
) -> dict:
    """Generic worker: assigned tasks, contributions, PR feedback."""
    my_tasks = [
        t for t in tasks
        if t.custom_fields.agent_name == agent_name
    ]
    in_progress = [t for t in my_tasks if t.status == TaskStatus.IN_PROGRESS]
    in_review = [t for t in my_tasks if t.status == TaskStatus.REVIEW]

    # Contribution tasks assigned to this agent (from synergy matrix)
    contribution_tasks = [
        t for t in tasks
        if t.custom_fields.agent_name == agent_name
        and t.custom_fields.contribution_type
        and t.status == TaskStatus.INBOX
    ]

    # Contributions received for my in-progress tasks
    contributions_received = {}
    for t in in_progress:
        received = [
            {
                "type": child.custom_fields.contribution_type,
                "from": child.custom_fields.agent_name or "unknown",
                "status": child.status.value,
            }
            for child in tasks
            if child.custom_fields.contribution_target == t.id
            and child.custom_fields.contribution_type
        ]
        if received:
            contributions_received[t.id[:8]] = received

    return {
        "my_tasks_count": len(my_tasks),
        "contribution_tasks": [
            {"id": t.id[:8], "title": t.title[:40], "type": t.custom_fields.contribution_type}
            for t in contribution_tasks[:5]
        ],
        "contributions_received": contributions_received,
        "in_review": [
            {"id": t.id[:8], "title": t.title[:40], "pr": t.custom_fields.pr_url or ""}
            for t in in_review[:5]
        ],
    }


# ─── Registry ───────────────────────────────────────────────────────────

ROLE_PROVIDERS: dict[str, callable] = {
    "fleet-ops": fleet_ops_provider,
    "project-manager": project_manager_provider,
    "architect": architect_provider,
    "devsecops-expert": devsecops_provider,
    # Worker roles — generic provider with contribution awareness
    "software-engineer": worker_provider,
    "devops": worker_provider,
    "qa-engineer": worker_provider,
    "technical-writer": worker_provider,
    "ux-designer": worker_provider,
    "accountability-generator": worker_provider,
}


def get_role_provider(role: str):
    """Get the data provider for an agent role."""
    return ROLE_PROVIDERS.get(role, worker_provider)