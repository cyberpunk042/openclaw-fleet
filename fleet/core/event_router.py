"""Event routing engine — matches events to agents by capability, tags, and role.

The deterministic logic layer. No AI needed — pure matching rules.

Routes events from the EventStore to agent notification feeds based on:
1. Direct recipient ("fleet-ops" → fleet-ops only)
2. Mentions (@agent-name → mentioned agent)
3. Tag subscriptions (agent subscribes to tags matching capabilities)
4. Role-based routing (PM gets unassigned, fleet-ops gets escalations)
5. Project association (agents get events from their assigned projects)

> "like the command center aggregate everything and redistribute and
> orchestrate and lets the agents do their works and their heartbeats
> and their responsive to targeted events, proper use of tagging and
> responsiveness to tagging."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from fleet.core.events import FleetEvent
from fleet.core.routing import AGENT_CAPABILITIES


# ─── Agent Subscriptions ──────────────────────────────────────────────

# What event tags each agent subscribes to (beyond direct routing)
AGENT_TAG_SUBSCRIPTIONS: dict[str, list[str]] = {
    "fleet-ops": [
        "review", "alert", "escalation", "quality", "security",
        "governance", "compliance", "impediment", "blocker",
    ],
    "project-manager": [
        "plan", "sprint", "velocity", "backlog", "plane",
        "unassigned", "impediment", "blocker", "milestone",
    ],
    "architect": [
        "architecture", "design", "system", "component",
        "dependency", "pattern", "complexity",
    ],
    "software-engineer": [
        "implement", "code", "feature", "fix", "refactor",
        "python", "module", "test",
    ],
    "qa-engineer": [
        "test", "qa", "quality", "coverage", "regression",
        "validation", "benchmark",
    ],
    "devops": [
        "docker", "ci", "cd", "pipeline", "deploy",
        "infrastructure", "monitoring", "setup", "infra",
    ],
    "devsecops-expert": [
        "security", "cve", "vulnerability", "secret",
        "audit", "compliance", "hardening",
    ],
    "technical-writer": [
        "documentation", "readme", "changelog", "docs",
        "guide", "onboarding",
    ],
    "ux-designer": [
        "ui", "ux", "interface", "accessibility",
        "design", "wireframe",
    ],
    "accountability-generator": [
        "accountability", "transparency", "evidence",
        "narrative", "report", "nnrt",
    ],
}

# Priority routing — certain event types always go to specific agents
PRIORITY_ROUTES: dict[str, dict] = {
    "fleet.escalation": {
        "recipients": ["fleet-ops"],
        "min_priority": "urgent",
    },
    "fleet.task.blocked": {
        "recipients": ["project-manager"],
        "min_priority": "important",
    },
    "fleet.alert.posted": {
        "recipients": ["fleet-ops"],
        "min_priority": "important",
    },
    "fleet.plane.issue_created": {
        "recipients": ["project-manager"],
        "min_priority": "info",
    },
    "fleet.plane.cycle_started": {
        "recipients": ["project-manager", "fleet-ops"],
        "min_priority": "important",
    },
    "fleet.github.ci_failed": {
        "recipients": [],  # Goes to assigned agent
        "min_priority": "urgent",
    },
    "fleet.agent.offline": {
        "recipients": ["fleet-ops"],
        "min_priority": "important",
    },
    "fleet.agent.stuck": {
        "recipients": ["fleet-ops", "project-manager"],
        "min_priority": "urgent",
    },
}


@dataclass
class RoutingResult:
    """Result of routing an event to agents."""

    event_id: str
    event_type: str
    recipients: list[str] = field(default_factory=list)
    reason: str = ""


def route_event(event: FleetEvent, all_agents: list[str] | None = None) -> RoutingResult:
    """Determine which agents should receive this event.

    Routing rules (in priority order):
    1. Direct recipient (event.recipient != "all")
    2. Priority routes (certain event types always go to specific agents)
    3. Mentions (@agent-name in event data)
    4. Tag subscriptions (event tags match agent subscriptions)
    5. "all" → everyone

    Returns RoutingResult with list of recipient agent names.
    """
    if all_agents is None:
        all_agents = list(AGENT_TAG_SUBSCRIPTIONS.keys())

    result = RoutingResult(event_id=event.id, event_type=event.type)
    recipients = set()

    # 1. Direct recipient
    recipient = event.recipient
    if recipient and recipient not in ("all", ""):
        if recipient in all_agents:
            recipients.add(recipient)
        elif recipient == "pm" or recipient == "unassigned":
            recipients.add("project-manager")
        elif recipient == "lead" or recipient == "ops":
            recipients.add("fleet-ops")
        result.reason = f"direct:{recipient}"

    # 2. Priority routes (type-based)
    if event.type in PRIORITY_ROUTES:
        route = PRIORITY_ROUTES[event.type]
        for r in route.get("recipients", []):
            if r in all_agents:
                recipients.add(r)
        if not result.reason:
            result.reason = f"priority_route:{event.type}"

    # 3. Mentions
    for mention in event.mentions:
        if mention in all_agents:
            recipients.add(mention)
            if not result.reason:
                result.reason = f"mention:{mention}"

    # 4. Tag subscriptions (only if no direct routing found)
    if not recipients or recipient == "all":
        event_tags = set(event.tags)
        for agent_name, subscribed_tags in AGENT_TAG_SUBSCRIPTIONS.items():
            if event_tags & set(subscribed_tags):
                recipients.add(agent_name)
                if not result.reason:
                    matching = event_tags & set(subscribed_tags)
                    result.reason = f"tag_match:{','.join(matching)}"

    # 5. "all" fallback
    if recipient == "all" and not recipients:
        recipients = set(all_agents)
        result.reason = "broadcast:all"

    result.recipients = sorted(recipients)
    return result


def build_agent_feed(
    events: list[FleetEvent],
    agent_name: str,
    limit: int = 20,
) -> list[dict]:
    """Build a notification feed for an agent from a list of events.

    Returns events formatted for the agent's heartbeat context:
    - Filtered to only events relevant to this agent
    - Sorted by priority (urgent > important > info) then time
    - Limited to most recent N items
    """
    priority_order = {"urgent": 0, "important": 1, "info": 2}

    feed = []
    for event in events:
        routing = route_event(event)
        if agent_name not in routing.recipients:
            continue

        feed.append({
            "id": event.id,
            "type": event.type,
            "time": event.time,
            "priority": event.priority,
            "data": event.data,
            "routing_reason": routing.reason,
        })

    # Sort: urgent first, then important, then info; within same priority, newest first
    feed.sort(key=lambda e: (priority_order.get(e["priority"], 9), e["time"]), reverse=False)
    # Reverse time within same priority (newest first per priority group)
    # Actually just sort by priority then reverse time
    feed.sort(key=lambda e: (priority_order.get(e["priority"], 9), ""), reverse=False)

    return feed[:limit]