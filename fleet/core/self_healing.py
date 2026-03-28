"""Self-healing — auto-resolve common fleet issues.

When health monitoring detects issues, self-healing tries to fix them
automatically before escalating to humans. Only resolves issues that
have clear, safe automated solutions.

Resolution types:
- Stale review tasks → create review task for fleet-ops
- Offline agents with work → create restart task or reassign
- Stale dependencies → alert devops to check MC state
- Unassigned inbox tasks → route via capability matching

Issues that can't be auto-resolved are escalated via ntfy notification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fleet.core.health import HealthIssue, HealthReport
from fleet.core.routing import suggest_agent
from fleet.core.models import Agent, Task


@dataclass
class HealingAction:
    """An action taken to resolve a health issue."""

    issue_title: str
    action: str          # What was done
    target_agent: str    # Who should handle it
    task_title: str = "" # Task to create (empty = no task needed)
    task_description: str = ""
    priority: str = "medium"
    escalate: bool = False  # True = needs human attention
    escalate_reason: str = ""


def plan_healing_actions(
    report: HealthReport,
    available_agents: list[Agent],
) -> list[HealingAction]:
    """Plan healing actions for detected health issues.

    Returns a list of actions the orchestrator should execute.
    Each action is either a task to create or an escalation.
    """
    actions: list[HealingAction] = []

    for issue in report.issues:
        action = _plan_action_for_issue(issue, available_agents)
        if action:
            actions.append(action)

    return actions


def _plan_action_for_issue(
    issue: HealthIssue,
    available_agents: list[Agent],
) -> Optional[HealingAction]:
    """Plan a healing action for a single issue."""

    if issue.category == "task" and "Stale in_progress" in issue.title:
        return HealingAction(
            issue_title=issue.title,
            action="check_stuck_agent",
            target_agent=issue.agent_name or "fleet-ops",
            task_title=f"Check stuck task: {issue.title[:40]}",
            task_description=(
                f"Task has been in_progress for too long. {issue.details}\n\n"
                f"Options:\n"
                f"1. Check if agent is still working (post progress update)\n"
                f"2. fleet_pause if stuck\n"
                f"3. Reassign to another agent\n"
            ),
            priority="high",
        )

    if issue.category == "task" and "Stale review" in issue.title:
        return HealingAction(
            issue_title=issue.title,
            action="nudge_reviewer",
            target_agent="fleet-ops",
            task_title=f"Review overdue: {issue.title[:40]}",
            task_description=f"Task in review too long. {issue.details}",
            priority="high",
        )

    if issue.category == "task" and "Unassigned inbox" in issue.title:
        return HealingAction(
            issue_title=issue.title,
            action="route_unassigned",
            target_agent="project-manager",
            task_title=f"Evaluate and assign: {issue.title[:40]}",
            task_description=f"Unassigned task in inbox. {issue.details}",
            priority="medium",
        )

    if issue.category == "agent" and "offline" in issue.title.lower():
        return HealingAction(
            issue_title=issue.title,
            action="restart_agent",
            target_agent="fleet-ops",
            task_title=f"Restart offline agent: {issue.agent_name}",
            task_description=(
                f"Agent {issue.agent_name} is offline with active work. {issue.details}\n\n"
                f"Try waking the agent. If that fails, reassign the task."
            ),
            priority="high",
        )

    if issue.category == "task" and "Stale dependency" in issue.title:
        return HealingAction(
            issue_title=issue.title,
            action="check_dependency",
            target_agent="devops",
            task_title=f"Fix stale dependency: {issue.title[:40]}",
            task_description=f"Blocked task may have stale dependency. {issue.details}",
            priority="medium",
        )

    # Can't auto-resolve — escalate
    if issue.severity in ("critical", "high"):
        return HealingAction(
            issue_title=issue.title,
            action="escalate",
            target_agent="fleet-ops",
            escalate=True,
            escalate_reason=f"{issue.title}: {issue.details}",
        )

    return None