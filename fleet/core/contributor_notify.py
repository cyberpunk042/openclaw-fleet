"""Contributor notification — notify contributors when their task enters review.

When fleet_task_complete fires, contributors who provided input
(architect design, QA tests, DevSecOps requirements, etc.) should
be notified that the task is ready for their review/validation.

QA should validate predefined tests were addressed.
DevSecOps should verify security requirements were followed.
Architect should verify design was implemented correctly.

Source: fleet-elevation/24 (fleet_task_complete tree: notify_contributors)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ContributorNotification:
    """A notification to send to a contributor."""
    role: str
    contribution_type: str
    message: str
    tags: list[str] = field(default_factory=list)


async def build_contributor_notifications(
    task_id: str,
    task_title: str,
    mc,
    board_id: str,
) -> list[ContributorNotification]:
    """Build notifications for all contributors to a task.

    Reads task comments to find typed contributions, then builds
    notifications for each contributor role.

    Args:
        task_id: Task entering review.
        task_title: Task title for notification message.
        mc: MCClient for reading comments.
        board_id: Board ID.

    Returns:
        List of notifications to send (caller posts to board memory).
    """
    notifications: list[ContributorNotification] = []

    try:
        # Read task comments to find contributions
        comments = await mc.list_comments(board_id, task_id)
        if not comments:
            return notifications

        # Find contribution comments (contain "Contribution (type)" pattern)
        contributor_roles: set[str] = set()
        for c in comments:
            content = c.message if hasattr(c, 'message') else c.get("message", "")
            if "**Contribution (" in content:
                # Extract contributor from "from {agent}:" pattern
                if "from " in content:
                    after_from = content.split("from ", 1)[1]
                    agent_name = after_from.split(":")[0].split("\n")[0].strip()
                    if agent_name:
                        contributor_roles.add(agent_name)

        # Build notification for each contributor
        for role in contributor_roles:
            notifications.append(ContributorNotification(
                role=role,
                contribution_type="review_needed",
                message=(
                    f"Task '{task_title[:40]}' ({task_id[:8]}) is now in review. "
                    f"Your contribution is part of this task — please validate "
                    f"your input was addressed in the implementation."
                ),
                tags=[
                    f"mention:{role}",
                    "review-needed",
                    f"task:{task_id}",
                ],
            ))

    except Exception as e:
        logger.debug("Failed to build contributor notifications: %s", e)

    return notifications


async def notify_contributors(
    task_id: str,
    task_title: str,
    mc,
    board_id: str,
) -> int:
    """Notify all contributors that a task is in review.

    Posts board memory entries with @mention tags so contributors
    see the notification in their heartbeat context.

    Returns:
        Number of contributors notified.
    """
    notifications = await build_contributor_notifications(
        task_id, task_title, mc, board_id,
    )

    notified = 0
    for n in notifications:
        try:
            await mc.post_memory(
                board_id,
                content=f"**[review]** @{n.role} {n.message}",
                tags=n.tags,
            )
            notified += 1
        except Exception as e:
            logger.debug("Failed to notify contributor %s: %s", n.role, e)

    return notified
