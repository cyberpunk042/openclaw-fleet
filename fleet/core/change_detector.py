"""Change detection — track what changed between orchestrator cycles.

Instead of the orchestrator re-scanning all tasks every 30 seconds,
the change detector identifies WHAT changed since the last check.
This enables targeted reactions instead of blind polling.

Uses MC activity events as the change source when available,
falls back to task list diff when not.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from fleet.core.models import Task, TaskStatus


@dataclass
class Change:
    """A detected change in the fleet state."""

    change_type: str       # task_status_changed, task_created, task_assigned, agent_offline
    task_id: str = ""
    agent_name: str = ""
    old_value: str = ""
    new_value: str = ""
    timestamp: Optional[datetime] = None
    details: str = ""


@dataclass
class ChangeSet:
    """All changes detected in one cycle."""

    changes: list[Change] = field(default_factory=list)
    new_tasks_in_review: list[str] = field(default_factory=list)
    new_tasks_done: list[str] = field(default_factory=list)
    new_tasks_in_inbox: list[str] = field(default_factory=list)
    tasks_unblocked: list[str] = field(default_factory=list)
    agents_went_offline: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)

    @property
    def needs_review_wake(self) -> bool:
        """Should fleet-ops be woken for review work?"""
        return bool(self.new_tasks_in_review)

    @property
    def needs_dispatch(self) -> bool:
        """Are there newly unblocked or inbox tasks to dispatch?"""
        return bool(self.new_tasks_in_inbox) or bool(self.tasks_unblocked)


class ChangeDetector:
    """Detects changes between orchestrator cycles by diffing task states.

    Tracks: task status changes, newly unblocked tasks, new tasks,
    agent status changes.
    """

    def __init__(self) -> None:
        self._previous_states: dict[str, str] = {}  # task_id → status
        self._previous_blocked: set[str] = set()     # task_ids that were blocked

    def detect(self, tasks: list[Task], now: Optional[datetime] = None) -> ChangeSet:
        """Compare current tasks against previous state. Return changes."""
        now = now or datetime.now()
        changes = ChangeSet()
        current_states: dict[str, str] = {}
        current_blocked: set[str] = set()

        for task in tasks:
            current_states[task.id] = task.status.value
            if task.is_blocked:
                current_blocked.add(task.id)

            prev_status = self._previous_states.get(task.id)

            if prev_status is None:
                # New task
                if task.status == TaskStatus.INBOX:
                    changes.new_tasks_in_inbox.append(task.id)
                changes.changes.append(Change(
                    change_type="task_created",
                    task_id=task.id,
                    new_value=task.status.value,
                    timestamp=now,
                    details=task.title[:60],
                ))
            elif prev_status != task.status.value:
                # Status changed
                changes.changes.append(Change(
                    change_type="task_status_changed",
                    task_id=task.id,
                    old_value=prev_status,
                    new_value=task.status.value,
                    timestamp=now,
                    details=task.title[:60],
                ))
                if task.status == TaskStatus.REVIEW:
                    changes.new_tasks_in_review.append(task.id)
                elif task.status == TaskStatus.DONE:
                    changes.new_tasks_done.append(task.id)

            # Check unblocked
            if task.id in self._previous_blocked and task.id not in current_blocked:
                changes.tasks_unblocked.append(task.id)
                changes.changes.append(Change(
                    change_type="task_unblocked",
                    task_id=task.id,
                    timestamp=now,
                    details=task.title[:60],
                ))

        # Update state for next cycle
        self._previous_states = current_states
        self._previous_blocked = current_blocked

        return changes