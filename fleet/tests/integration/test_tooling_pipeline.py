"""Integration tests for the tooling configuration and generation pipeline.

Verifies:
  - All configs parse and are internally consistent
  - Sub-agent frontmatter is valid
  - Skill directories have SKILL.md
  - Generation pipeline produces expected output structure
  - Cross-config references are valid (sub-agents, skills, roles)
  - Tool-roles.yaml tools exist in tools.py
  - Hooks reference real tools
"""

import ast
import json
from pathlib import Path

import pytest
import yaml

FLEET_DIR = Path(__file__).resolve().parent.parent.parent.parent
CONFIG = FLEET_DIR / "config"
SKILLS_DIR = FLEET_DIR / ".claude" / "skills"
AGENTS_DIR = FLEET_DIR / ".claude" / "agents"
ROLES_DIR = FLEET_DIR / "fleet" / "mcp" / "roles"


def load_yaml(path: Path) -> dict:
    if not path.exists():
        pytest.skip(f"{path.name} not found")
    with open(path) as f:
        return yaml.safe_load(f) or {}


def get_tool_names() -> set[str]:
    """Extract all fleet_* tool names from tools.py."""
    tools_py = FLEET_DIR / "fleet" / "mcp" / "tools.py"
    with open(tools_py) as f:
        tree = ast.parse(f.read())
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef))
        and node.name.startswith("fleet_")
    }


AGENT_ROSTER = [
    "architect", "software-engineer", "qa-engineer", "devops",
    "devsecops-expert", "fleet-ops", "project-manager",
    "technical-writer", "ux-designer", "accountability-generator",
]


# ── Config Parsing ──────────────────────────────────────────────────

class TestConfigsParse:
    """All tooling configs parse as valid YAML."""

    @pytest.mark.parametrize("config_file", [
        "agent-tooling.yaml",
        "agent-crons.yaml",
        "agent-hooks.yaml",
        "standing-orders.yaml",
        "skill-stage-mapping.yaml",
        "tool-chains.yaml",
        "tool-roles.yaml",
        "agent-identities.yaml",
    ])
    def test_config_parses(self, config_file):
        path = CONFIG / config_file
        if not path.exists():
            pytest.skip(f"{config_file} not found")
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data is not None, f"{config_file} is empty"
        assert isinstance(data, dict), f"{config_file} is not a dict"


# ── Sub-Agent Validation ────────────────────────────────────────────

class TestSubAgents:
    """Sub-agent .md files have valid frontmatter and structure."""

    def _get_subagent_files(self):
        if not AGENTS_DIR.exists():
            pytest.skip(".claude/agents/ not found")
        return sorted(AGENTS_DIR.glob("*.md"))

    def test_subagents_exist(self):
        files = self._get_subagent_files()
        assert len(files) >= 4, f"Expected at least 4 sub-agents, found {len(files)}"

    @pytest.mark.parametrize("required_field", ["name", "description", "model", "tools"])
    def test_subagent_frontmatter_has_required_fields(self, required_field):
        for path in self._get_subagent_files():
            content = path.read_text()
            assert content.startswith("---"), f"{path.name}: missing frontmatter"
            parts = content.split("---", 2)
            meta = yaml.safe_load(parts[1])
            assert required_field in meta, f"{path.name}: missing '{required_field}'"

    def test_subagent_models_valid(self):
        valid_models = {"opus", "sonnet", "haiku"}
        for path in self._get_subagent_files():
            content = path.read_text()
            parts = content.split("---", 2)
            meta = yaml.safe_load(parts[1])
            assert meta.get("model") in valid_models, \
                f"{path.name}: model '{meta.get('model')}' not in {valid_models}"

    def test_subagent_tools_deny_exists(self):
        for path in self._get_subagent_files():
            content = path.read_text()
            parts = content.split("---", 2)
            meta = yaml.safe_load(parts[1])
            assert "tools_deny" in meta, f"{path.name}: missing tools_deny"
            assert "Edit" in meta["tools_deny"], f"{path.name}: Edit not in tools_deny"
            assert "Write" in meta["tools_deny"], f"{path.name}: Write not in tools_deny"


# ── Skill Validation ───────────────────────────────────────────────

class TestSkills:
    """Skill directories have SKILL.md with valid frontmatter."""

    def _get_skill_dirs(self):
        if not SKILLS_DIR.exists():
            pytest.skip(".claude/skills/ not found")
        return sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir())

    def test_skills_exist(self):
        dirs = self._get_skill_dirs()
        assert len(dirs) >= 20, f"Expected at least 20 skills, found {len(dirs)}"

    def test_each_skill_has_skill_md(self):
        for d in self._get_skill_dirs():
            skill_md = d / "SKILL.md"
            assert skill_md.exists(), f"{d.name}: missing SKILL.md"

    def test_skill_frontmatter_valid(self):
        for d in self._get_skill_dirs():
            skill_md = d / "SKILL.md"
            if not skill_md.exists():
                continue
            content = skill_md.read_text()
            assert content.startswith("---"), f"{d.name}: SKILL.md missing frontmatter"
            parts = content.split("---", 2)
            meta = yaml.safe_load(parts[1])
            assert "name" in meta, f"{d.name}: missing 'name' in frontmatter"
            assert "description" in meta, f"{d.name}: missing 'description' in frontmatter"


# ── Cross-Config References ────────────────────────────────────────

class TestCrossConfigRefs:
    """References between configs are valid."""

    def test_tooling_subagent_refs_have_files(self):
        tooling = load_yaml(CONFIG / "agent-tooling.yaml")
        all_refs = set()
        for sa in tooling.get("defaults", {}).get("sub_agents", []):
            all_refs.add(sa)
        for agent, cfg in tooling.get("agents", {}).items():
            for sa in cfg.get("sub_agents", []):
                all_refs.add(sa)
        for sa in all_refs:
            assert (AGENTS_DIR / f"{sa}.md").exists(), \
                f"Sub-agent '{sa}' in agent-tooling.yaml but file missing"

    def test_skill_mapping_refs_have_dirs(self):
        mapping = load_yaml(CONFIG / "skill-stage-mapping.yaml")
        for role, stages in mapping.get("roles", {}).items():
            for stage, entries in stages.items():
                if not isinstance(entries, list):
                    continue
                for entry in entries:
                    if entry.get("source") == "workspace":
                        skill = entry["skill"]
                        assert (SKILLS_DIR / skill / "SKILL.md").exists(), \
                            f"Skill '{skill}' ({role}/{stage}) in mapping but missing on disk"

    def test_tool_roles_reference_real_tools(self):
        tool_roles = load_yaml(CONFIG / "tool-roles.yaml")
        actual_tools = get_tool_names()
        for role in AGENT_ROSTER:
            role_data = tool_roles.get(role, {})
            if not isinstance(role_data, dict):
                continue
            for tool_name in role_data.get("tools", {}):
                assert tool_name in actual_tools, \
                    f"tool-roles.yaml {role}: '{tool_name}' not in tools.py"

    def test_hook_matchers_reference_real_tools(self):
        hooks = load_yaml(CONFIG / "agent-hooks.yaml")
        actual_tools = get_tool_names()
        for section in [hooks.get("defaults", {})] + list(hooks.get("roles", {}).values()):
            if not isinstance(section, dict):
                continue
            for event_type, hook_list in section.items():
                if not isinstance(hook_list, list):
                    continue
                for hook in hook_list:
                    matcher = hook.get("matcher", "")
                    for m in matcher.split("|"):
                        m = m.strip()
                        if m and m.startswith("fleet_"):
                            assert m in actual_tools, \
                                f"Hook matcher '{m}' not in tools.py"

    def test_standing_order_roles_in_roster(self):
        orders = load_yaml(CONFIG / "standing-orders.yaml")
        for role in orders:
            if role == "defaults":
                continue
            assert role in AGENT_ROSTER, \
                f"Standing order role '{role}' not in agent roster"

    def test_cron_roles_in_roster(self):
        crons = load_yaml(CONFIG / "agent-crons.yaml")
        for role in crons:
            if role == "fleet_state_guard":
                continue
            if not isinstance(crons[role], list):
                continue
            assert role in AGENT_ROSTER, \
                f"CRON role '{role}' not in agent roster"

    def test_hook_roles_in_roster(self):
        hooks = load_yaml(CONFIG / "agent-hooks.yaml")
        for role in hooks.get("roles", {}):
            assert role in AGENT_ROSTER, \
                f"Hook role '{role}' not in agent roster"


# ── TOOLS.md Generation Output ─────────────────────────────────────

class TestToolsMdOutput:
    """Generated TOOLS.md files have expected structure."""

    @pytest.mark.parametrize("agent", AGENT_ROSTER)
    def test_tools_md_exists(self, agent):
        path = FLEET_DIR / "agents" / agent / "TOOLS.md"
        assert path.exists(), f"agents/{agent}/TOOLS.md not found"

    @pytest.mark.parametrize("agent", AGENT_ROSTER)
    def test_tools_md_has_header(self, agent):
        path = FLEET_DIR / "agents" / agent / "TOOLS.md"
        if not path.exists():
            pytest.skip("TOOLS.md not generated")
        content = path.read_text()
        assert content.startswith("# Tools —"), \
            f"{agent}: TOOLS.md doesn't start with expected header"
        assert f"AGENT_NAME={agent}" in content, \
            f"{agent}: TOOLS.md missing AGENT_NAME"

    @pytest.mark.parametrize("section", [
        "Fleet MCP Tools",
        "MCP Servers",
        "Skills",
        "Hooks (Structural Enforcement)",
    ])
    def test_tools_md_has_required_sections(self, section):
        """Every agent's TOOLS.md has these sections."""
        for agent in AGENT_ROSTER:
            path = FLEET_DIR / "agents" / agent / "TOOLS.md"
            if not path.exists():
                continue
            content = path.read_text()
            assert f"## {section}" in content, \
                f"{agent}: TOOLS.md missing '## {section}'"

    def test_tools_md_minimum_length(self):
        """TOOLS.md should be substantial, not stubs."""
        for agent in AGENT_ROSTER:
            path = FLEET_DIR / "agents" / agent / "TOOLS.md"
            if not path.exists():
                continue
            lines = len(path.read_text().splitlines())
            assert lines >= 200, \
                f"{agent}: TOOLS.md only {lines} lines (expected 200+)"


# ── Agent Tooling Internal Consistency ─────────────────────────────

class TestAgentToolingConsistency:
    """agent-tooling.yaml is internally consistent."""

    def test_no_duplicate_mcp_servers(self):
        tooling = load_yaml(CONFIG / "agent-tooling.yaml")
        for agent, cfg in tooling.get("agents", {}).items():
            names = [s.get("name") for s in cfg.get("mcp_servers", [])]
            dupes = [n for n in set(names) if names.count(n) > 1]
            assert not dupes, f"{agent}: duplicate MCP servers {dupes}"

    def test_all_agents_have_config(self):
        tooling = load_yaml(CONFIG / "agent-tooling.yaml")
        for agent in AGENT_ROSTER:
            assert agent in tooling.get("agents", {}), \
                f"{agent} missing from agent-tooling.yaml"
