"""Tests for fleet template formatters."""

from fleet.core.models import Commit, CommitType
from fleet.core.urls import ResolvedUrls
from fleet.templates.comment import (
    format_accept,
    format_blocker,
    format_complete,
    format_progress,
)
from fleet.templates.irc import (
    format_alert,
    format_event,
    format_pr_ready,
    route_channel,
)
from fleet.templates.memory import alert_tags, format_pr_notice, pr_tags
from fleet.templates.pr import format_pr_body, format_pr_title


def test_pr_title():
    assert format_pr_title("sw-eng", "Fix auth") == "fleet(sw-eng): Fix auth"


def test_pr_body_has_sections():
    body = format_pr_body(
        summary="Fixed auth bug",
        commits=[Commit(sha="abc1234", message="fix(auth): handle rotation", commit_type=CommitType.FIX)],
        diff_stat=[{"path": "auth.py", "added": 5, "removed": 2}],
        urls=ResolvedUrls(),
        task_id="task-123",
        task_title="Fix auth",
        agent_name="sw-eng",
    )
    assert "## 📋 Summary" in body
    assert "## 📝 Changelog" in body
    assert "## 📊 Changes" in body
    assert "## 🔗 References" in body
    assert "sw-eng" in body
    assert "task-12" in body


def test_comment_accept():
    text = format_accept("Will fix the auth module", "architect")
    assert "▶️ Accepted" in text
    assert "Will fix the auth module" in text
    assert "architect" in text


def test_comment_progress():
    text = format_progress("Fixed 3 functions", "Testing", "none", "sw-eng")
    assert "🔄 Progress" in text
    assert "Fixed 3 functions" in text


def test_comment_complete():
    text = format_complete(
        summary="Added type hints",
        pr_url="https://github.com/test/pull/1",
        branch="fleet/sw/abc",
        commit_count=2,
        files=["a.py", "b.py"],
        agent_name="sw-eng",
    )
    assert "✅ Completed" in text
    assert "https://github.com/test/pull/1" in text
    assert "fleet/sw/abc" in text


def test_comment_blocker():
    text = format_blocker("Can't find module", "Need architect input", "sw-eng")
    assert "🚫 Blocked" in text
    assert "Can't find module" in text


def test_irc_event():
    msg = format_event("sw-eng", "✅ PR READY", "Fix auth", "https://pr/1")
    assert "[sw-eng] ✅ PR READY: Fix auth — https://pr/1" == msg


def test_irc_pr_ready():
    msg = format_pr_ready("sw-eng", "Fix auth", "https://pr/1")
    assert "[sw-eng]" in msg
    assert "https://pr/1" in msg


def test_irc_alert():
    msg = format_alert("sw-eng", "critical", "CVE found")
    assert "🔴" in msg
    assert "CRITICAL" in msg


def test_irc_route_channel():
    assert route_channel(severity="critical") == "#alerts"
    assert route_channel(severity="high") == "#alerts"
    assert route_channel(severity="medium") == "#fleet"
    assert route_channel(event_type="pr_ready") == "#reviews"
    assert route_channel() == "#fleet"


def test_memory_alert_tags():
    tags = alert_tags("high", "security", "nnrt")
    assert "alert" in tags
    assert "high" in tags
    assert "security" in tags
    assert "project:nnrt" in tags


def test_memory_pr_tags():
    tags = pr_tags("nnrt")
    assert "pr" in tags
    assert "review" in tags
    assert "project:nnrt" in tags


def test_memory_pr_notice():
    text = format_pr_notice(
        task_title="Fix tests", pr_url="https://pr/1",
        agent_name="sw-eng", branch="fleet/sw/abc",
    )
    assert "🔀 PR Ready" in text
    assert "https://pr/1" in text