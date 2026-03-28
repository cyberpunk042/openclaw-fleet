"""Fleet health monitoring — stuck detection, service health, resource cleanup.

Detects unhealthy fleet conditions:
- Agents stuck on tasks too long (no progress)
- Tasks in a status too long without movement
- Agents offline who should be working
- Stale worktrees and branches
- Service connectivity issues

Used by fleet-ops during heartbeats and by the orchestrator for health checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from fleet.core.models import Agent, Task, TaskStatus


@dataclass
class HealthIssue:
    """A detected health problem in the fleet."""

    severity: str       # critical, high, medium, low
    category: str       # agent, task, service, resource
    title: str
    details: str
    agent_name: str = ""
    task_id: str = ""
    suggested_action: str = ""
    suggested_agent: str = ""  # Who should fix this


@dataclass
class HealthReport:
    """Full health assessment of the fleet."""

    timestamp: datetime
    issues: list[HealthIssue] = field(default_factory=list)
    agents_online: int = 0
    agents_offline: int = 0
    tasks_active: int = 0
    tasks_blocked: int = 0
    tasks_stale: int = 0

    @property
    def healthy(self) -> bool:
        return not any(i.severity in ("critical", "high") for i in self.issues)

    @property
    def critical_issues(self) -> list[HealthIssue]:
        return [i for i in self.issues if i.severity == "critical"]


# Thresholds (configurable)
TASK_STALE_IN_PROGRESS_HOURS = 8     # Task in_progress > 8h without progress
TASK_STALE_IN_REVIEW_HOURS = 24      # Task in review > 24h
TASK_STALE_IN_INBOX_HOURS = 2        # Task in inbox > 2h unassigned
AGENT_OFFLINE_HOURS = 2               # Agent offline > 2h with assigned work


def assess_fleet_health(
    tasks: list[Task],
    agents: list[Agent],
    now: Optional[datetime] = None,
) -> HealthReport:
    """Full fleet health assessment.

    Checks for stuck tasks, offline agents, stale work, and blockers.
    Returns a report with issues ranked by severity.
    """
    now = now or datetime.now()
    report = HealthReport(timestamp=now)

    # Count agents
    for agent in agents:
        if "Gateway" in agent.name:
            continue
        if agent.status == "online":
            report.agents_online += 1
        else:
            report.agents_offline += 1

    # Analyze tasks
    for task in tasks:
        if task.status == TaskStatus.IN_PROGRESS:
            report.tasks_active += 1
            _check_stale_in_progress(task, now, report)

        elif task.status == TaskStatus.REVIEW:
            _check_stale_review(task, now, report)

        elif task.status == TaskStatus.INBOX:
            _check_stale_inbox(task, now, report)

        if task.is_blocked:
            report.tasks_blocked += 1

    # Check agents with assigned tasks who are offline
    _check_offline_agents_with_work(tasks, agents, now, report)

    # Check for blocked tasks where blockers are done (stale dependency)
    _check_stale_dependencies(tasks, report)

    return report


def _check_stale_in_progress(task: Task, now: datetime, report: HealthReport) -> None:
    """Check if a task has been in_progress too long without progress."""
    if not task.updated_at:
        return

    hours = (now - task.updated_at).total_seconds() / 3600
    if hours > TASK_STALE_IN_PROGRESS_HOURS:
        report.tasks_stale += 1
        report.issues.append(HealthIssue(
            severity="high" if hours > 24 else "medium",
            category="task",
            title=f"Stale in_progress: {task.title[:50]}",
            details=f"In progress for {hours:.0f}h without update. Agent may be stuck.",
            agent_name=task.custom_fields.agent_name or "",
            task_id=task.id,
            suggested_action="Check on agent. Consider fleet_pause or reassignment.",
            suggested_agent="fleet-ops",
        ))


def _check_stale_review(task: Task, now: datetime, report: HealthReport) -> None:
    """Check if a task has been in review too long."""
    if not task.updated_at:
        return

    hours = (now - task.updated_at).total_seconds() / 3600
    if hours > TASK_STALE_IN_REVIEW_HOURS:
        report.tasks_stale += 1
        report.issues.append(HealthIssue(
            severity="medium",
            category="task",
            title=f"Stale review: {task.title[:50]}",
            details=f"In review for {hours:.0f}h. fleet-ops should process this.",
            task_id=task.id,
            suggested_action="fleet-ops should review and approve/reject.",
            suggested_agent="fleet-ops",
        ))


def _check_stale_inbox(task: Task, now: datetime, report: HealthReport) -> None:
    """Check if an unassigned inbox task has been waiting too long."""
    if task.assigned_agent_id:
        return  # Assigned — orchestrator will dispatch when possible
    if not task.created_at:
        return

    hours = (now - task.created_at).total_seconds() / 3600
    if hours > TASK_STALE_IN_INBOX_HOURS:
        report.issues.append(HealthIssue(
            severity="low",
            category="task",
            title=f"Unassigned inbox: {task.title[:50]}",
            details=f"In inbox for {hours:.0f}h without assignment.",
            task_id=task.id,
            suggested_action="PM should evaluate and assign.",
            suggested_agent="project-manager",
        ))


def _check_offline_agents_with_work(
    tasks: list[Task], agents: list[Agent], now: datetime, report: HealthReport
) -> None:
    """Check for agents who are offline but have in_progress tasks."""
    agent_map = {a.id: a for a in agents}

    for task in tasks:
        if task.status != TaskStatus.IN_PROGRESS:
            continue
        if not task.assigned_agent_id:
            continue

        agent = agent_map.get(task.assigned_agent_id)
        if not agent or agent.status == "online":
            continue

        # Agent is offline with an active task
        offline_hours = 0
        if agent.last_seen:
            offline_hours = (now - agent.last_seen).total_seconds() / 3600

        if offline_hours > AGENT_OFFLINE_HOURS:
            report.issues.append(HealthIssue(
                severity="high",
                category="agent",
                title=f"Agent offline with active task: {agent.name}",
                details=(
                    f"{agent.name} offline for {offline_hours:.0f}h "
                    f"but has task: {task.title[:40]}"
                ),
                agent_name=agent.name,
                task_id=task.id,
                suggested_action="Restart agent or reassign task.",
                suggested_agent="fleet-ops",
            ))


def _check_stale_dependencies(tasks: list[Task], report: HealthReport) -> None:
    """Check for blocked tasks whose blockers are actually done."""
    task_map = {t.id: t for t in tasks}

    for task in tasks:
        if not task.is_blocked:
            continue

        for blocker_id in task.blocked_by_task_ids:
            blocker = task_map.get(blocker_id)
            if blocker and blocker.status == TaskStatus.DONE:
                report.issues.append(HealthIssue(
                    severity="medium",
                    category="task",
                    title=f"Stale dependency: {task.title[:40]}",
                    details=(
                        f"Blocked by {blocker_id[:8]} which is already done. "
                        f"MC dependency may need refresh."
                    ),
                    task_id=task.id,
                    suggested_action="Check MC dependency state. May need manual unblock.",
                    suggested_agent="devops",
                ))