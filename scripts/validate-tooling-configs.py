#!/usr/bin/env python3
"""Cross-validate all tooling configs for internal consistency.

Checks:
  1. Agent names match across all configs
  2. Sub-agent references → .claude/agents/ files exist
  3. Skill references → .claude/skills/ directories exist
  4. Group call references in CRONs → fleet/mcp/roles/ functions exist
  5. Tool references in hooks → fleet/mcp/tools.py functions exist
  6. Standing order roles match agent roster
  7. CRON roles match agent roster
  8. Hook roles match agent roster
  9. Skill-stage-mapping workspace refs → skill dirs exist
  10. Plugin assignments are consistent
  11. Generated TOOLS.md exists for all agents
  12. Workspace deployment state

Usage:
  python scripts/validate-tooling-configs.py          # full validation
  python scripts/validate-tooling-configs.py --fix     # suggest fixes (no auto-fix)
"""

import ast
import os
import re
import sys
from pathlib import Path

import yaml

FLEET_DIR = Path(__file__).resolve().parent.parent
CONFIG = FLEET_DIR / "config"

# ── Config loading ──────────────────────────────────────────────────

def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


# ── Extract function names from Python source ──────────────────────

def extract_function_names(path: Path, prefix: str = "") -> set[str]:
    if not path.exists():
        return set()
    with open(path) as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            if not prefix or node.name.startswith(prefix):
                names.add(node.name)
    return names


# ── Validation checks ──────────────────────────────────────────────

class Validator:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def error(self, msg: str):
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    def ok(self, msg: str):
        self.info.append(msg)

    def check_agent_roster(self) -> set[str]:
        """Check 1: Build canonical agent roster and verify consistency."""
        identities = load_yaml(CONFIG / "agent-identities.yaml")
        tooling = load_yaml(CONFIG / "agent-tooling.yaml")

        identity_agents = set(identities.get("agents", {}).keys())
        tooling_agents = set(tooling.get("agents", {}).keys())

        # Agents in tooling but not in identities
        for a in tooling_agents - identity_agents:
            self.warn(f"agent-tooling.yaml has '{a}' but agent-identities.yaml does not")

        # Agents in identities but not in tooling
        for a in identity_agents - tooling_agents:
            self.warn(f"agent-identities.yaml has '{a}' but agent-tooling.yaml does not")

        # Canonical roster = union
        roster = identity_agents | tooling_agents
        self.ok(f"Agent roster: {len(roster)} agents")
        return roster

    def check_subagent_refs(self, roster: set[str]):
        """Check 2: All sub-agent refs in agent-tooling.yaml have files."""
        tooling = load_yaml(CONFIG / "agent-tooling.yaml")
        agents_dir = FLEET_DIR / ".claude" / "agents"

        # Collect all referenced sub-agents
        all_refs = set()
        defaults = tooling.get("defaults", {}).get("sub_agents", [])
        all_refs.update(defaults)

        for agent, cfg in tooling.get("agents", {}).items():
            for sa in cfg.get("sub_agents", []):
                all_refs.add(sa)

        # Check each ref has a file
        for sa in sorted(all_refs):
            path = agents_dir / f"{sa}.md"
            if not path.exists():
                self.error(f"Sub-agent '{sa}' referenced but {path.relative_to(FLEET_DIR)} missing")
            else:
                # Verify YAML frontmatter
                with open(path) as f:
                    content = f.read()
                if not content.startswith("---"):
                    self.error(f"Sub-agent '{sa}' has no YAML frontmatter")

        # Check for orphaned sub-agent files (exist but not referenced)
        if agents_dir.exists():
            existing = {f.stem for f in agents_dir.glob("*.md")}
            orphaned = existing - all_refs
            for o in sorted(orphaned):
                self.warn(f"Sub-agent file '{o}.md' exists but not referenced in agent-tooling.yaml")

        self.ok(f"Sub-agent references: {len(all_refs)} referenced, {len(all_refs)} checked")

    def check_skill_refs(self):
        """Check 3: All workspace skill refs in skill-stage-mapping.yaml exist."""
        mapping = load_yaml(CONFIG / "skill-stage-mapping.yaml")
        skills_dir = FLEET_DIR / ".claude" / "skills"

        # Collect all workspace skill references
        ws_refs = set()

        # Generic stages
        for stage, section in mapping.get("generic", {}).items():
            if isinstance(section, dict):
                for entry in section.get("recommended", []):
                    if entry.get("source") == "workspace":
                        ws_refs.add(entry["skill"])

        # Role stages
        for role, stages in mapping.get("roles", {}).items():
            for stage, entries in stages.items():
                if isinstance(entries, list):
                    for entry in entries:
                        if entry.get("source") == "workspace":
                            ws_refs.add(entry["skill"])

        # Check each exists
        missing = []
        for skill in sorted(ws_refs):
            skill_path = skills_dir / skill / "SKILL.md"
            if not skill_path.exists():
                self.error(f"Skill '{skill}' referenced in skill-stage-mapping.yaml but {skill_path.relative_to(FLEET_DIR)} missing")
                missing.append(skill)

        # Check for orphaned skills (exist but not in mapping)
        if skills_dir.exists():
            existing = {d.name for d in skills_dir.iterdir() if d.is_dir()}
            in_mapping = ws_refs.copy()

            # Also count skills from agent-tooling.yaml
            tooling = load_yaml(CONFIG / "agent-tooling.yaml")
            for agent, cfg in tooling.get("agents", {}).items():
                for s in cfg.get("skills", []):
                    in_mapping.add(s)
            for s in tooling.get("defaults", {}).get("skills", []):
                in_mapping.add(s)

            # Skills that exist on disk but are in neither config
            # (gateway skills like fleet-sprint won't be in mapping as workspace refs)
            # Only flag fleet-* skills that have SKILL.md
            for skill_dir in sorted(existing):
                if (skills_dir / skill_dir / "SKILL.md").exists():
                    if skill_dir not in in_mapping:
                        self.warn(f"Skill '{skill_dir}' exists but not in skill-stage-mapping.yaml or agent-tooling.yaml")

        self.ok(f"Skill refs: {len(ws_refs)} workspace refs checked, {len(missing)} missing")

    def check_group_call_refs(self, roster: set[str]):
        """Check 4: Group calls referenced in CRONs actually exist."""
        crons = load_yaml(CONFIG / "agent-crons.yaml")
        roles_dir = FLEET_DIR / "fleet" / "mcp" / "roles"

        # Map role names to their module's function names
        role_funcs = {}
        file_map = {
            "project-manager": "pm.py",
            "fleet-ops": "fleet_ops.py",
            "architect": "architect.py",
            "devsecops-expert": "devsecops.py",
            "software-engineer": "engineer.py",
            "devops": "devops.py",
            "qa-engineer": "qa.py",
            "technical-writer": "writer.py",
            "ux-designer": "ux.py",
            "accountability-generator": "accountability.py",
        }

        for role, filename in file_map.items():
            role_funcs[role] = extract_function_names(roles_dir / filename)

        # Check CRON messages for group call references
        call_pattern = re.compile(r'(\w+_\w+)\(\)')
        for role, jobs in crons.items():
            if role == "fleet_state_guard" or not isinstance(jobs, list):
                continue
            for job in jobs:
                msg = job.get("message", "")
                calls = call_pattern.findall(msg)
                for call in calls:
                    # Check if it's a fleet_ tool or a role-specific tool
                    if call.startswith("fleet_"):
                        # Generic tool — check tools.py
                        generic_funcs = extract_function_names(
                            FLEET_DIR / "fleet" / "mcp" / "tools.py", "fleet_"
                        )
                        if call not in generic_funcs:
                            self.warn(f"CRON '{job.get('name')}' for {role} references {call}() but not found in tools.py")
                    else:
                        # Role-specific — check the role module
                        funcs = role_funcs.get(role, set())
                        if call not in funcs:
                            self.warn(f"CRON '{job.get('name')}' for {role} references {call}() but not found in roles/{file_map.get(role, '?')}")

        self.ok(f"CRON group call references checked across {len(crons) - 1} roles")

    def check_hook_tool_refs(self):
        """Check 5: Hook matchers reference real tools."""
        hooks = load_yaml(CONFIG / "agent-hooks.yaml")
        generic_funcs = extract_function_names(
            FLEET_DIR / "fleet" / "mcp" / "tools.py", "fleet_"
        )

        for section in [hooks.get("defaults", {}), *hooks.get("roles", {}).values()]:
            for event_type, hook_list in section.items() if isinstance(section, dict) else []:
                if not isinstance(hook_list, list):
                    continue
                for hook in hook_list:
                    matcher = hook.get("matcher", "")
                    # Split pipe-separated matchers
                    for m in matcher.split("|"):
                        m = m.strip()
                        if m and m.startswith("fleet_") and m not in generic_funcs:
                            self.warn(f"Hook matcher '{m}' not found in tools.py")

        self.ok("Hook tool references checked")

    def check_standing_order_roles(self, roster: set[str]):
        """Check 6: Standing order roles match agent roster."""
        orders = load_yaml(CONFIG / "standing-orders.yaml")
        for key in orders:
            if key in ("defaults",):
                continue
            if key not in roster:
                self.error(f"Standing order role '{key}' not in agent roster")

        self.ok(f"Standing order roles checked")

    def check_cron_roles(self, roster: set[str]):
        """Check 7: CRON roles match agent roster."""
        crons = load_yaml(CONFIG / "agent-crons.yaml")
        for key in crons:
            if key in ("fleet_state_guard",):
                continue
            if not isinstance(crons[key], list):
                continue
            if key not in roster:
                self.error(f"CRON role '{key}' not in agent roster")

        self.ok("CRON roles checked")

    def check_hook_roles(self, roster: set[str]):
        """Check 8: Hook roles match agent roster."""
        hooks = load_yaml(CONFIG / "agent-hooks.yaml")
        for key in hooks.get("roles", {}):
            if key not in roster:
                self.error(f"Hook role '{key}' not in agent roster")

        self.ok("Hook roles checked")

    def check_tools_md(self, roster: set[str]):
        """Check 11: Generated TOOLS.md exists for all agents."""
        for agent in sorted(roster):
            tools_path = FLEET_DIR / "agents" / agent / "TOOLS.md"
            if not tools_path.exists():
                self.error(f"agents/{agent}/TOOLS.md does not exist — run generate-tools-md.py")
            else:
                # Quick content check
                content = tools_path.read_text()
                if "Fleet MCP Tools" not in content:
                    self.warn(f"agents/{agent}/TOOLS.md looks like old MC-generated version")
                lines = len(content.splitlines())
                if lines < 100:
                    self.warn(f"agents/{agent}/TOOLS.md only {lines} lines — may be incomplete")

        self.ok("TOOLS.md existence checked")

    def check_workspace_deployment(self, roster: set[str]):
        """Check 12: Workspace deployment state."""
        deployed = set()
        for mcp_file in sorted(FLEET_DIR.glob("workspace-mc-*/.mcp.json")):
            workspace = mcp_file.parent
            try:
                import json
                with open(mcp_file) as f:
                    data = json.load(f)
                agent = data["mcpServers"]["fleet"]["env"]["FLEET_AGENT"]
                deployed.add(agent)

                # Check workspace has key files
                for fname in ["TOOLS.md", "SOUL.md"]:
                    if not (workspace / fname).exists():
                        self.warn(f"Workspace {workspace.name} ({agent}): missing {fname}")

                # Check settings.json has hooks
                settings_path = workspace / ".claude" / "settings.json"
                if settings_path.exists():
                    with open(settings_path) as f:
                        settings = json.load(f)
                    if "hooks" not in settings:
                        self.warn(f"Workspace {agent}: settings.json has no hooks section")
                else:
                    self.warn(f"Workspace {agent}: no .claude/settings.json")

                # Check sub-agents deployed
                agents_path = workspace / ".claude" / "agents"
                if agents_path.exists():
                    sa_count = len(list(agents_path.glob("*.md")))
                    if sa_count == 0:
                        self.warn(f"Workspace {agent}: .claude/agents/ exists but empty")
                else:
                    self.warn(f"Workspace {agent}: no .claude/agents/ directory")

                # Check skills symlink
                skills_path = workspace / ".claude" / "skills"
                if not skills_path.exists():
                    self.warn(f"Workspace {agent}: no .claude/skills/ symlink")

            except (json.JSONDecodeError, KeyError):
                self.warn(f"Workspace {workspace.name}: cannot read agent name from .mcp.json")

        not_deployed = roster - deployed
        for a in sorted(not_deployed):
            self.warn(f"Agent '{a}' has no workspace (not deployed)")

        self.ok(f"Workspaces: {len(deployed)} deployed, {len(not_deployed)} missing")

    def check_tooling_consistency(self):
        """Check 10: agent-tooling.yaml internal consistency."""
        tooling = load_yaml(CONFIG / "agent-tooling.yaml")

        for agent, cfg in tooling.get("agents", {}).items():
            # Check MCP server names are unique per agent
            srv_names = [s.get("name") for s in cfg.get("mcp_servers", [])]
            dupes = [n for n in srv_names if srv_names.count(n) > 1]
            if dupes:
                self.error(f"agent-tooling.yaml {agent}: duplicate MCP server '{dupes[0]}'")

            # Check plugins are strings
            for p in cfg.get("plugins", []):
                if not isinstance(p, str):
                    self.error(f"agent-tooling.yaml {agent}: plugin entry is not a string: {p}")

        self.ok("agent-tooling.yaml internal consistency checked")

    def run_all(self):
        """Run all validation checks."""
        print("=" * 60)
        print("  Config Cross-Validation — all tooling configs")
        print("=" * 60)
        print()

        roster = self.check_agent_roster()
        self.check_subagent_refs(roster)
        self.check_skill_refs()
        self.check_group_call_refs(roster)
        self.check_hook_tool_refs()
        self.check_standing_order_roles(roster)
        self.check_cron_roles(roster)
        self.check_hook_roles(roster)
        self.check_tooling_consistency()
        self.check_tools_md(roster)
        self.check_workspace_deployment(roster)

        # Report
        print()
        if self.errors:
            print(f"ERRORS ({len(self.errors)}):")
            for e in self.errors:
                print(f"  [ERROR] {e}")
            print()

        if self.warnings:
            print(f"WARNINGS ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  [WARN]  {w}")
            print()

        print(f"CHECKS ({len(self.info)}):")
        for i in self.info:
            print(f"  [OK]    {i}")

        print()
        print(f"Result: {len(self.errors)} errors, {len(self.warnings)} warnings")
        if self.errors:
            print("FAIL — fix errors before deploying")
            return 1
        elif self.warnings:
            print("PASS with warnings — review before deploying")
            return 0
        else:
            print("PASS — all configs consistent")
            return 0


if __name__ == "__main__":
    v = Validator()
    sys.exit(v.run_all())
