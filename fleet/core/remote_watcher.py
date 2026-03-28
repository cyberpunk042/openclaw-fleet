"""Remote change detection — react to GitHub and MC dashboard changes.

Detects changes made by humans outside the fleet:
- PR comments on GitHub (human feedback on agent PRs)
- PR merged/closed on GitHub (human acted on PR directly)
- Task comments on MC dashboard (human directives)
- Task status changes on MC (human moved tasks)

Produces a list of RemoteChanges that the orchestrator should act on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from fleet.core.models import Task, TaskStatus


@dataclass
class RemoteChange:
    """A change detected from an external source."""

    source: str         # "github_pr_comment", "github_pr_merged", "github_pr_closed",
                        # "mc_task_comment", "mc_task_status"
    task_id: str = ""
    pr_url: str = ""
    actor: str = ""     # Who made the change (human username)
    content: str = ""   # Comment text, status change description
    action_needed: str = ""  # What the fleet should do about it
    target_agent: str = ""   # Who should handle it


@dataclass
class RemoteChangeSet:
    """All remote changes detected in one check cycle."""

    changes: list[RemoteChange] = field(default_factory=list)
    checked_at: Optional[datetime] = None

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)

    @property
    def pr_comments(self) -> list[RemoteChange]:
        return [c for c in self.changes if c.source == "github_pr_comment"]

    @property
    def pr_merges(self) -> list[RemoteChange]:
        return [c for c in self.changes if c.source == "github_pr_merged"]

    @property
    def pr_closes(self) -> list[RemoteChange]:
        return [c for c in self.changes if c.source == "github_pr_closed"]

    @property
    def human_directives(self) -> list[RemoteChange]:
        return [c for c in self.changes if c.source == "mc_task_comment"]


def classify_pr_change(
    task: Task,
    pr_state: str,
    previous_state: str = "OPEN",
) -> Optional[RemoteChange]:
    """Classify a PR state change into a RemoteChange.

    Args:
        task: The task linked to this PR.
        pr_state: Current PR state (OPEN, MERGED, CLOSED).
        previous_state: Previous PR state.
    """
    if pr_state == previous_state:
        return None

    pr_url = task.custom_fields.pr_url or ""
    agent = task.custom_fields.agent_name or ""

    if pr_state == "MERGED" and previous_state == "OPEN":
        return RemoteChange(
            source="github_pr_merged",
            task_id=task.id,
            pr_url=pr_url,
            actor="human",
            content=f"PR merged: {pr_url}",
            action_needed="Move task to done. Post board memory. Notify fleet.",
            target_agent="fleet-ops",
        )

    if pr_state == "CLOSED" and previous_state == "OPEN":
        return RemoteChange(
            source="github_pr_closed",
            task_id=task.id,
            pr_url=pr_url,
            actor="human",
            content=f"PR closed without merging: {pr_url}",
            action_needed="Move task to inbox (rework) or mark abandoned. Check human intent.",
            target_agent=agent or "fleet-ops",
        )

    return None


def classify_human_comment(
    task: Task,
    comment_text: str,
    commenter: str = "human",
) -> RemoteChange:
    """Classify a human comment on a task as a directive.

    Human comments on MC or GitHub PRs are treated as directives —
    the fleet should act on them.
    """
    # Detect intent from comment
    text_lower = comment_text.lower()
    action = "Address human feedback"

    if any(w in text_lower for w in ("fix", "change", "update", "modify", "add")):
        action = "Implement changes requested by human"
    elif any(w in text_lower for w in ("looks good", "lgtm", "approve", "merge")):
        action = "Human approved — proceed with merge"
    elif any(w in text_lower for w in ("reject", "close", "abandon", "cancel")):
        action = "Human rejected — close PR and task"
    elif any(w in text_lower for w in ("question", "why", "explain", "??")):
        action = "Answer human question before proceeding"

    return RemoteChange(
        source="github_pr_comment" if "pr" in task.custom_fields.pr_url else "mc_task_comment",
        task_id=task.id,
        pr_url=task.custom_fields.pr_url or "",
        actor=commenter,
        content=comment_text[:500],
        action_needed=action,
        target_agent=task.custom_fields.agent_name or "fleet-ops",
    )