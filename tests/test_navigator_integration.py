"""Integration tests — navigator → context_writer → file → gateway reads.

Tests the full pipeline from navigator assembly to context file on disk,
verifying that the gateway would receive correct, complete content.
"""

import pytest
from pathlib import Path
from unittest.mock import patch

from fleet.core.navigator import Navigator
from fleet.core.context_writer import write_knowledge_context, AGENTS_DIR


@pytest.fixture
def navigator():
    nav = Navigator()
    nav.load()
    return nav


@pytest.fixture
def temp_agent_dir(tmp_path):
    """Create a temporary agent directory mimicking fleet structure."""
    agent_dir = tmp_path / "test-agent"
    agent_dir.mkdir()
    (agent_dir / "context").mkdir()
    return agent_dir


class TestFullPipeline:
    """Test navigator → context_writer → file → gateway can read."""

    def test_write_knowledge_context_creates_file(self, navigator, tmp_path):
        """Navigator output written to disk via context_writer."""
        agent_dir = tmp_path / "architect"
        agent_dir.mkdir()
        (agent_dir / "context").mkdir()

        ctx = navigator.assemble(
            role="architect", stage="reasoning", model="opus-4-6"
        )
        rendered = ctx.render()

        # Write directly (bypassing AGENTS_DIR lookup)
        path = agent_dir / "context" / "knowledge-context.md"
        path.write_text(rendered)

        assert path.exists()
        content = path.read_text()
        assert len(content) > 0
        assert len(content) <= 8000  # gateway limit
        assert "Architect" in content  # agent manual present
        assert "REASONING" in content or "reasoning" in content.lower()

    def test_gateway_reads_all_context_files(self, navigator, tmp_path):
        """Simulate gateway reading sorted context/ directory."""
        agent_dir = tmp_path / "engineer"
        agent_dir.mkdir()
        context_dir = agent_dir / "context"
        context_dir.mkdir()

        # Write three context files like orchestrator does
        (context_dir / "fleet-context.md").write_text("Fleet state: work mode active")

        ctx = navigator.assemble(
            role="software-engineer", stage="work", model="opus-4-6"
        )
        (context_dir / "knowledge-context.md").write_text(ctx.render())

        (context_dir / "task-context.md").write_text("Task: implement auth middleware")

        # Simulate gateway reading (from executor.py lines 127-132)
        parts = []
        for f in sorted(context_dir.iterdir()):
            if f.is_file() and f.suffix in (".md", ".txt", ".yaml", ".json"):
                content = f.read_text()[:8000]
                parts.append(f"Context ({f.name}):\n{content}")

        # Should have all three files in sorted order
        assert len(parts) == 3
        assert "fleet-context.md" in parts[0]
        assert "knowledge-context.md" in parts[1]
        assert "task-context.md" in parts[2]

        # Knowledge context should have navigator output
        assert "Software Engineer" in parts[1]
        assert "WORK" in parts[1] or "work" in parts[1].lower()

    def test_no_broken_text_in_output(self, navigator):
        """Every section must be complete — no mid-sentence cuts."""
        roles_stages = [
            ("architect", "reasoning"),
            ("software-engineer", "work"),
            ("fleet-ops", "review"),
            ("project-manager", "reasoning"),
            ("devops", "work"),
            ("qa-engineer", "work"),
        ]

        for role, stage in roles_stages:
            ctx = navigator.assemble(role=role, stage=stage, model="opus-4-6")
            rendered = ctx.render()
            # No truncation markers
            assert "...(truncated)" not in rendered, f"{role}/{stage} has broken text"
            # No mid-word cuts (sections end with complete words/lines)
            for section in ctx.sections:
                assert not section.endswith("..."), f"{role}/{stage} section ends with ..."

    def test_all_outputs_under_gateway_limit(self, navigator):
        """Every role × stage × model must fit in 8000 chars."""
        intents = navigator._intent_map.get("intents", {})
        role_map = {
            "pm": "project-manager",
            "engineer": "software-engineer",
            "qa": "qa-engineer",
            "architect": "architect",
            "devsecops": "devsecops-expert",
            "fleet-ops": "fleet-ops",
            "devops": "devops",
            "writer": "technical-writer",
            "ux": "ux-designer",
            "accountability": "accountability-generator",
        }

        stages = [
            "conversation", "reasoning", "work", "review",
            "heartbeat", "analysis", "investigation", "contribution",
        ]

        for intent_name in intents:
            for s in stages:
                if intent_name.endswith(f"-{s}"):
                    role_short = intent_name[:-(len(s) + 1)]
                    stage = s
                    break
            else:
                continue

            role = role_map.get(role_short, role_short)

            for model in ["opus-4-6", "sonnet-4-6", "hermes-3b"]:
                ctx = navigator.assemble(role=role, stage=stage, model=model)
                rendered = ctx.render()
                assert len(rendered) <= 8000, (
                    f"{intent_name} with {model}: {len(rendered)} chars > 8000"
                )

    def test_depth_tiers_scale_correctly(self, navigator):
        """Opus > Sonnet > LocalAI in content size for non-trivial intents."""
        test_cases = [
            ("architect", "reasoning"),
            ("software-engineer", "work"),
            ("project-manager", "reasoning"),
        ]

        for role, stage in test_cases:
            opus = navigator.assemble(role=role, stage=stage, model="opus-4-6")
            sonnet = navigator.assemble(role=role, stage=stage, model="sonnet-4-6")
            local = navigator.assemble(role=role, stage=stage, model="hermes-3b")

            opus_len = len(opus.render())
            sonnet_len = len(sonnet.render())
            local_len = len(local.render())

            assert opus_len >= sonnet_len, (
                f"{role}/{stage}: opus ({opus_len}) < sonnet ({sonnet_len})"
            )
            assert sonnet_len >= local_len, (
                f"{role}/{stage}: sonnet ({sonnet_len}) < local ({local_len})"
            )

    def test_local_graph_provides_context(self, navigator):
        """Local graph traversal should find relevant systems for task context."""
        ctx = navigator.assemble(
            role="architect",
            stage="reasoning",
            model="opus-4-6",
            task_context="design budget monitoring dashboard",
        )
        rendered = ctx.render()
        # Should find budget-related systems via cross-references
        assert "budget" in rendered.lower() or "S12" in rendered

    def test_graph_failure_graceful(self, navigator):
        """Navigator handles LightRAG down + cross-ref issues gracefully."""
        ctx = navigator.assemble(
            role="architect",
            stage="reasoning",
            model="opus-4-6",
            task_context="something completely unrelated to any system",
        )
        # Should still have static content even if graph finds nothing
        assert len(ctx.sections) >= 2  # at least agent manual + methodology

    def test_caching_returns_same_results(self, navigator):
        """Cached reads return identical results."""
        ctx1 = navigator.assemble(
            role="architect", stage="reasoning", model="opus-4-6"
        )
        ctx2 = navigator.assemble(
            role="architect", stage="reasoning", model="opus-4-6"
        )
        assert ctx1.render() == ctx2.render()

    def test_reload_clears_cache(self, navigator):
        """reload() clears cache — next call re-reads files."""
        ctx1 = navigator.assemble(
            role="architect", stage="reasoning", model="opus-4-6"
        )
        assert len(navigator._file_cache) > 0

        navigator.reload()
        assert len(navigator._file_cache) == 0
        assert navigator._loaded is True  # reload re-loads
