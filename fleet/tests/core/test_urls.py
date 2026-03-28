"""Tests for fleet URL resolver."""

from fleet.core.models import Project
from fleet.core.urls import UrlResolver


def _make_resolver() -> UrlResolver:
    projects = {
        "nnrt": Project(
            name="nnrt", owner="cyberpunk042",
            repo="Narrative-to-Neutral-Report-Transformer",
        ),
    }
    templates = {
        "github": {
            "pr": "https://github.com/{owner}/{repo}/pull/{pr_number}",
            "compare": "https://github.com/{owner}/{repo}/compare/main...{branch}",
            "file": "https://github.com/{owner}/{repo}/blob/{branch}/{path}",
            "commit": "https://github.com/{owner}/{repo}/commit/{sha}",
        },
        "mc": {
            "task": "http://localhost:3000/boards/{board_id}/tasks/{task_id}",
            "board": "http://localhost:3000/boards/{board_id}",
        },
    }
    return UrlResolver(projects, templates, board_id="board-123")


def test_resolve_pr_url():
    r = _make_resolver()
    urls = r.resolve(project="nnrt", pr_number=7)
    assert urls.pr == "https://github.com/cyberpunk042/Narrative-to-Neutral-Report-Transformer/pull/7"


def test_resolve_compare_url():
    r = _make_resolver()
    urls = r.resolve(project="nnrt", branch="fleet/sw-eng/abc123")
    assert "compare/main...fleet/sw-eng/abc123" in urls.compare


def test_resolve_file_urls():
    r = _make_resolver()
    urls = r.resolve(
        project="nnrt", branch="main",
        files=["nnrt/core/engine.py", "nnrt/core/context.py"],
    )
    assert len(urls.files) == 2
    assert "engine.py" in urls.files[0]["url"]
    assert urls.files[0]["path"] == "nnrt/core/engine.py"


def test_resolve_commit_urls():
    r = _make_resolver()
    urls = r.resolve(project="nnrt", commits=["abc1234", "def5678"])
    assert len(urls.commits) == 2
    assert urls.commits[0]["short"] == "abc1234"[:7]


def test_resolve_task_url():
    r = _make_resolver()
    urls = r.resolve(project="nnrt", task_id="task-456")
    assert "boards/board-123/tasks/task-456" in urls.task


def test_task_url_shorthand():
    r = _make_resolver()
    url = r.task_url("my-task-id")
    assert "boards/board-123/tasks/my-task-id" in url


def test_file_url_shorthand():
    r = _make_resolver()
    url = r.file_url("nnrt", "main", "nnrt/core/engine.py")
    assert "blob/main/nnrt/core/engine.py" in url


def test_unknown_project_returns_empty():
    r = _make_resolver()
    urls = r.resolve(project="unknown", pr_number=1)
    assert urls.pr is None
    assert urls.compare is None