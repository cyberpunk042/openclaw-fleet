"""Tests for event routing engine."""

import pytest

from fleet.core.events import create_event
from fleet.core.event_router import route_event, build_agent_feed, AGENT_TAG_SUBSCRIPTIONS


class TestRouteEvent:
    def test_direct_recipient(self):
        event = create_event("fleet.test", source="test", recipient="architect")
        result = route_event(event)
        assert "architect" in result.recipients
        assert "direct" in result.reason

    def test_pm_gets_unassigned(self):
        event = create_event("fleet.task.created", source="test", recipient="unassigned")
        result = route_event(event)
        assert "project-manager" in result.recipients

    def test_fleet_ops_gets_lead(self):
        event = create_event("fleet.escalation", source="test", recipient="lead")
        result = route_event(event)
        assert "fleet-ops" in result.recipients

    def test_mention_routing(self):
        event = create_event("fleet.chat.mention", source="test",
                             recipient="all", mentions=["qa-engineer"])
        result = route_event(event)
        assert "qa-engineer" in result.recipients

    def test_tag_subscription_routing(self):
        event = create_event("fleet.test", source="test",
                             recipient="all", tags=["security", "cve"])
        result = route_event(event)
        # devsecops-expert subscribes to "security" and "cve"
        assert "devsecops-expert" in result.recipients
        # fleet-ops subscribes to "security"
        assert "fleet-ops" in result.recipients

    def test_priority_route_escalation(self):
        event = create_event("fleet.escalation", source="test")
        result = route_event(event)
        assert "fleet-ops" in result.recipients

    def test_priority_route_blocked(self):
        event = create_event("fleet.task.blocked", source="test")
        result = route_event(event)
        assert "project-manager" in result.recipients

    def test_priority_route_agent_stuck(self):
        event = create_event("fleet.agent.stuck", source="test")
        result = route_event(event)
        assert "fleet-ops" in result.recipients
        assert "project-manager" in result.recipients

    def test_broadcast_all(self):
        event = create_event("fleet.system.health", source="test", recipient="all")
        result = route_event(event)
        # Should go to everyone (no tag matches → fallback to all)
        assert len(result.recipients) > 5

    def test_infra_tag_routes_to_devops(self):
        event = create_event("fleet.test", source="test",
                             recipient="all", tags=["infra", "docker"])
        result = route_event(event)
        assert "devops" in result.recipients

    def test_docs_tag_routes_to_writer(self):
        event = create_event("fleet.test", source="test",
                             recipient="all", tags=["documentation"])
        result = route_event(event)
        assert "technical-writer" in result.recipients

    def test_plane_tag_routes_to_pm(self):
        event = create_event("fleet.plane.issue_created", source="test",
                             tags=["plane"])
        result = route_event(event)
        assert "project-manager" in result.recipients

    def test_all_agents_have_subscriptions(self):
        agents = [
            "fleet-ops", "project-manager", "architect",
            "software-engineer", "qa-engineer", "devops",
            "devsecops-expert", "technical-writer",
            "ux-designer", "accountability-generator",
        ]
        for agent in agents:
            assert agent in AGENT_TAG_SUBSCRIPTIONS, f"{agent} missing subscriptions"
            assert len(AGENT_TAG_SUBSCRIPTIONS[agent]) >= 3, f"{agent} has too few subscriptions"


class TestBuildAgentFeed:
    def test_filters_to_relevant_events(self):
        events = [
            create_event("fleet.task.completed", source="test", recipient="fleet-ops"),
            create_event("fleet.chat.message", source="test", recipient="all"),
            create_event("fleet.task.completed", source="test", recipient="architect"),
        ]
        feed = build_agent_feed(events, "fleet-ops")
        # fleet-ops gets: their direct event + broadcast
        assert len(feed) >= 1

    def test_priority_ordering(self):
        events = [
            create_event("fleet.test.1", source="test", recipient="all", priority="info"),
            create_event("fleet.test.2", source="test", recipient="all", priority="urgent"),
            create_event("fleet.test.3", source="test", recipient="all", priority="important"),
        ]
        feed = build_agent_feed(events, "fleet-ops")
        priorities = [e["priority"] for e in feed]
        # Urgent should come before important, which comes before info
        assert priorities.index("urgent") < priorities.index("info")

    def test_limit(self):
        events = [create_event(f"fleet.test.{i}", source="test", recipient="all")
                  for i in range(30)]
        feed = build_agent_feed(events, "fleet-ops", limit=5)
        assert len(feed) == 5