"""Trail recorder — complete audit trail per task.

Every action, transition, contribution, gate decision, approval,
rejection — recorded with WHO (agent + model), WHAT (action),
WHEN (timestamp), and WHY (context).

Trails are stored as board memory entries tagged:
  trail + task:{id} + {event_type}

The accountability generator reconstructs the full chronological
trail at any time. Fleet-ops reads trail during 7-step review
(Step 4: check trail).

Source: fleet-vision-architecture §38, fleet-elevation/24
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


# ─── Trail Event Types (30+) ────────────────────────────────────────


class TrailEventType(str, Enum):
    """All trail event types — complete lifecycle coverage."""

    # Task lifecycle
    TASK_CREATED = "trail.task.created"
    TASK_ASSIGNED = "trail.task.assigned"
    TASK_DISPATCHED = "trail.task.dispatched"
    TASK_STAGE_CHANGED = "trail.task.stage_changed"
    TASK_READINESS_CHANGED = "trail.task.readiness_changed"
    TASK_PROGRESS_CHANGED = "trail.task.progress_changed"
    TASK_CHECKPOINT = "trail.task.checkpoint"
    TASK_COMPLETED = "trail.task.completed"
    TASK_TRANSFERRED = "trail.task.transferred"
    TASK_DONE = "trail.task.done"
    TASK_REGRESSED = "trail.task.regressed"

    # Contributions
    CONTRIBUTION_REQUESTED = "trail.contribution.requested"
    CONTRIBUTION_POSTED = "trail.contribution.posted"
    CONTRIBUTION_ALL_RECEIVED = "trail.contribution.all_received"

    # Reviews
    REVIEW_STARTED = "trail.review.started"
    REVIEW_QA_VALIDATED = "trail.review.qa_validated"
    REVIEW_SECURITY = "trail.review.security"
    REVIEW_APPROVED = "trail.review.approved"
    REVIEW_REJECTED = "trail.review.rejected"

    # Gates
    GATE_REQUESTED = "trail.gate.requested"
    GATE_DECIDED = "trail.gate.decided"
    PHASE_ADVANCED = "trail.phase.advanced"

    # Immune system
    DISEASE_DETECTED = "trail.disease.detected"
    DISEASE_TREATED = "trail.disease.treated"
    CORRECTION_APPLIED = "trail.correction.applied"

    # Commits & PRs
    COMMIT_CREATED = "trail.commit.created"
    PR_CREATED = "trail.pr.created"

    # Input requests
    INPUT_REQUESTED = "trail.input.requested"
    INPUT_RECEIVED = "trail.input.received"

    # System
    PLAN_ACCEPTED = "trail.plan.accepted"
    CHALLENGE_STARTED = "trail.challenge.started"
    CHALLENGE_PASSED = "trail.challenge.passed"
    CHALLENGE_FAILED = "trail.challenge.failed"


# ─── Trail Event ────────────────────────────────────────────────────


@dataclass
class TrailEvent:
    """A single trail event — atomic record of what happened."""

    event_type: TrailEventType
    task_id: str
    agent: str
    timestamp: str = ""
    details: dict = field(default_factory=dict)
    # Mini-signature (§44)
    model: str = ""
    context_pct: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()

    @property
    def tags(self) -> list[str]:
        """Board memory tags for this trail event."""
        tags = [
            "trail",
            f"task:{self.task_id}",
            self.event_type.value,
            f"agent:{self.agent}",
        ]
        # Add detail-specific tags
        if "contribution_type" in self.details:
            tags.append(self.details["contribution_type"])
        if "gate_type" in self.details:
            tags.append(self.details["gate_type"])
        return tags

    @property
    def content(self) -> str:
        """Formatted board memory content."""
        detail_str = ""
        if self.details:
            detail_parts = [f"{k}={v}" for k, v in self.details.items()
                            if v is not None and v != ""]
            if detail_parts:
                detail_str = f" ({', '.join(detail_parts)})"

        sig = ""
        if self.model:
            sig = f" [{self.model}"
            if self.context_pct:
                sig += f", {self.context_pct:.0f}%"
            sig += "]"

        return (
            f"**[trail]** {self.event_type.value}: "
            f"{self.agent}{sig}{detail_str}"
        )


# ─── Trail Recorder ─────────────────────────────────────────────────


class TrailRecorder:
    """Records trail events to board memory.

    Usage:
        recorder = TrailRecorder(mc_client, board_id)
        await recorder.record(TrailEvent(
            event_type=TrailEventType.TASK_CREATED,
            task_id="abc123",
            agent="project-manager",
            details={"task_type": "task", "parent": "epic-xyz"},
        ))
    """

    def __init__(self, mc_client, board_id: str):
        self._mc = mc_client
        self._board_id = board_id

    async def record(self, event: TrailEvent) -> bool:
        """Record a trail event to board memory. Returns True if successful."""
        try:
            await self._mc.post_memory(
                self._board_id,
                content=event.content,
                tags=event.tags,
                source=event.agent,
            )
            logger.debug("Trail recorded: %s for task %s",
                         event.event_type.value, event.task_id[:8])
            return True
        except Exception as e:
            logger.warning("Trail recording failed: %s — %s",
                           event.event_type.value, e)
            return False

    async def get_trail(self, task_id: str) -> list[dict]:
        """Get full chronological trail for a task.

        Returns list of board memory entries tagged with trail + task:{id},
        sorted by timestamp (oldest first).
        """
        try:
            entries = await self._mc.list_memory(
                self._board_id,
                tags=["trail", f"task:{task_id}"],
                limit=100,
            )
            # Sort by created_at ascending (oldest first)
            return sorted(entries, key=lambda e: e.get("created_at", ""))
        except Exception as e:
            logger.warning("Trail retrieval failed for %s: %s", task_id[:8], e)
            return []


# ─── Trail Completeness ─────────────────────────────────────────────


# Required trail events per task type for a task to be "complete"
REQUIRED_TRAIL: dict[str, list[TrailEventType]] = {
    "task": [
        TrailEventType.TASK_CREATED,
        TrailEventType.TASK_ASSIGNED,
        TrailEventType.TASK_DISPATCHED,
        TrailEventType.PLAN_ACCEPTED,
        TrailEventType.COMMIT_CREATED,
        TrailEventType.TASK_COMPLETED,
        TrailEventType.REVIEW_APPROVED,
        TrailEventType.TASK_DONE,
    ],
    "subtask": [
        TrailEventType.TASK_CREATED,
        TrailEventType.TASK_ASSIGNED,
        TrailEventType.PLAN_ACCEPTED,
        TrailEventType.TASK_COMPLETED,
        TrailEventType.TASK_DONE,
    ],
    "epic": [
        TrailEventType.TASK_CREATED,
        TrailEventType.TASK_ASSIGNED,
    ],
    "contribution": [
        TrailEventType.TASK_CREATED,
        TrailEventType.CONTRIBUTION_POSTED,
        TrailEventType.TASK_DONE,
    ],
}


@dataclass
class TrailCompleteness:
    """Result of checking trail completeness for a task."""

    task_id: str
    task_type: str
    required: list[str]
    present: list[str]
    missing: list[str]
    completeness_pct: float

    @property
    def is_complete(self) -> bool:
        return len(self.missing) == 0


def check_trail_completeness(
    trail_entries: list[dict],
    task_id: str,
    task_type: str = "task",
) -> TrailCompleteness:
    """Check if a task's trail has all required events.

    Args:
        trail_entries: Board memory entries from get_trail()
        task_id: Task ID
        task_type: Task type (task, subtask, epic, contribution)

    Used by fleet-ops during review (Step 4: check trail).
    """
    required = REQUIRED_TRAIL.get(task_type, REQUIRED_TRAIL["task"])
    required_types = [e.value for e in required]

    # Extract event types from trail entries
    present_types = set()
    for entry in trail_entries:
        content = entry.get("content", "")
        tags = entry.get("tags", [])
        for tag in tags:
            if tag.startswith("trail."):
                present_types.add(tag)
        # Also check content for event type references
        for rt in required_types:
            if rt in content:
                present_types.add(rt)

    present = [t for t in required_types if t in present_types]
    missing = [t for t in required_types if t not in present_types]
    total = len(required_types)
    pct = (len(present) / total * 100) if total > 0 else 100.0

    return TrailCompleteness(
        task_id=task_id,
        task_type=task_type,
        required=required_types,
        present=present,
        missing=missing,
        completeness_pct=pct,
    )
