"""Board cleanup tool — archive noise tasks, keep real work visible.

NOT a manual operation. A tool that fleet-ops or the human uses when
the board gets cluttered. Archives done heartbeat, review process,
and conflict resolution tasks while keeping sprint work visible.

Archives are tracked — nothing is deleted without a record.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from fleet.core.models import Task, TaskStatus


@dataclass
class CleanupResult:
    """Result of a board cleanup operation."""

    archived: int = 0
    kept: int = 0
    categories: dict[str, int] = field(default_factory=dict)
    archived_ids: list[str] = field(default_factory=list)


def identify_noise_tasks(
    tasks: list[Task],
    keep_recent_days: int = 7,
    now: Optional[datetime] = None,
) -> tuple[list[Task], list[Task]]:
    """Separate noise tasks from real work.

    Noise tasks (done, can be archived):
    - [heartbeat] tasks
    - [review] Process N pending approvals
    - Resolve conflict tasks (done)

    Real work (keep visible):
    - Sprint tasks (have plan_id or sprint)
    - Tasks with PR URLs
    - Tasks in inbox/in_progress/review (active)
    - Recent tasks (within keep_recent_days)

    Returns:
        (noise_tasks, keep_tasks)
    """
    now = now or datetime.now()
    cutoff = now - timedelta(days=keep_recent_days)

    noise: list[Task] = []
    keep: list[Task] = []

    for task in tasks:
        # Active tasks always kept
        if task.status in (TaskStatus.INBOX, TaskStatus.IN_PROGRESS, TaskStatus.REVIEW):
            keep.append(task)
            continue

        # Recent tasks kept
        if task.updated_at and task.updated_at > cutoff:
            keep.append(task)
            continue

        # Sprint tasks kept
        if task.custom_fields.plan_id or task.custom_fields.sprint:
            keep.append(task)
            continue

        # Tasks with PRs kept
        if task.custom_fields.pr_url:
            keep.append(task)
            continue

        # Noise patterns
        title = task.title
        if (
            "[heartbeat]" in title
            or "[review] Process" in title
            or "Resolve conflict" in title
        ):
            noise.append(task)
            continue

        # Default: keep
        keep.append(task)

    return noise, keep


def plan_cleanup(
    tasks: list[Task],
    keep_recent_days: int = 7,
) -> CleanupResult:
    """Plan what would be cleaned up without executing.

    Returns a CleanupResult showing what would be archived.
    """
    noise, keep = identify_noise_tasks(tasks, keep_recent_days)

    result = CleanupResult(
        archived=len(noise),
        kept=len(keep),
        archived_ids=[t.id for t in noise],
    )

    # Categorize noise
    for t in noise:
        if "[heartbeat]" in t.title:
            result.categories["heartbeat"] = result.categories.get("heartbeat", 0) + 1
        elif "[review] Process" in t.title:
            result.categories["review_process"] = result.categories.get("review_process", 0) + 1
        elif "Resolve conflict" in t.title:
            result.categories["resolve_conflict"] = result.categories.get("resolve_conflict", 0) + 1
        else:
            result.categories["other"] = result.categories.get("other", 0) + 1

    return result