"""Tests for heartbeat context bundler."""

from fleet.core.heartbeat_context import build_heartbeat_context, HeartbeatBundle
from fleet.core.models import Agent, Task, TaskCustomFields, TaskStatus


def _task(title="Test", agent="devops", status="inbox", plan_id="") -> Task:
    return Task(
        id="t1234567", board_id="b1", title=title,
        status=TaskStatus(status),
        custom_fields=TaskCustomFields(agent_name=agent, plan_id=plan_id),
    )

def _agent(name="devops", status="online") -> Agent:
    return Agent(id=f"id-{name}", name=name, status=status)

def _memory(content="Test", source="agent", tags=None):
    class M:
        pass
    m = M()
    m.content = content
    m.source = source
    m.tags = tags or []
    return m


def test_bundle_with_assigned_work():
    tasks = [_task("Deploy Plane", "devops", "inbox")]
    agents = [_agent("devops")]
    bundle = build_heartbeat_context("devops", tasks, agents)
    assert bundle.has_work
    assert len(bundle.assigned_tasks) == 1
    assert "Deploy" in bundle.assigned_tasks[0]["title"]


def test_bundle_no_work():
    tasks = [_task("Deploy Plane", "architect", "inbox")]  # assigned to someone else
    agents = [_agent("devops")]
    bundle = build_heartbeat_context("devops", tasks, agents)
    assert not bundle.has_work
    assert len(bundle.assigned_tasks) == 0


def test_bundle_with_chat():
    tasks = []
    agents = [_agent("devops")]
    memory = [_memory("@devops can you check the CI?", "pm", ["chat", "mention:devops"])]
    bundle = build_heartbeat_context("devops", tasks, agents, board_memory=memory)
    assert bundle.has_chat
    assert len(bundle.chat_messages) == 1
    assert "pm" in bundle.mentioned_by


def test_bundle_fleet_ops_sees_lead_mentions():
    tasks = []
    agents = [_agent("fleet-ops")]
    memory = [_memory("@lead please review", "sw-eng", ["chat", "mention:lead"])]
    bundle = build_heartbeat_context("fleet-ops", tasks, agents, board_memory=memory)
    assert bundle.has_chat


def test_bundle_domain_events():
    tasks = []
    agents = [_agent("devsecops-expert")]
    memory = [_memory("CVE found in dependency", "scanner", ["alert", "security"])]
    bundle = build_heartbeat_context("devsecops-expert", tasks, agents, board_memory=memory)
    assert len(bundle.domain_events) == 1


def test_bundle_sprint_summary():
    tasks = [
        _task("Done task", "devops", "done", plan_id="s3"),
        _task("In prog", "sw-eng", "in_progress", plan_id="s3"),
        _task("Inbox", "qa", "inbox", plan_id="s3"),
    ]
    agents = [_agent("devops")]
    bundle = build_heartbeat_context("devops", tasks, agents, sprint_id="s3")
    assert "1/3" in bundle.sprint_summary


def test_bundle_fleet_health():
    agents = [_agent("a", "online"), _agent("b", "online"), _agent("c", "offline")]
    bundle = build_heartbeat_context("a", [], agents)
    assert bundle.agents_online == 2
    assert bundle.agents_total == 3


def test_format_message_no_work():
    bundle = HeartbeatBundle(agent_name="devops", timestamp="2026-03-29 10:00")
    msg = bundle.format_message()
    assert "HEARTBEAT_OK" in msg
    assert "Do NOT call any tools" in msg


def test_format_message_with_work():
    bundle = HeartbeatBundle(
        agent_name="devops",
        timestamp="2026-03-29 10:00",
        has_work=True,
        assigned_tasks=[{"id": "t1", "title": "Deploy", "status": "inbox", "priority": "high"}],
    )
    msg = bundle.format_message()
    assert "YOU HAVE ASSIGNED WORK" in msg
    assert "Deploy" in msg