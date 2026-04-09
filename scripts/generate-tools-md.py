#!/usr/bin/env python3
"""Generate per-agent TOOLS.md — focused desk, detail on-demand.

Produces a FOCUSED tool reference card per agent. Only the tools THIS
role actually uses, with role-specific descriptions and chain awareness.
Skills, sub-agents, hooks, CRONs move to Navigator (knowledge-context.md).

Design: wiki/domains/architecture/tools-md-redesign.md
Algorithm: wiki/domains/architecture/generate-tools-md-redesign.md

Reads:
  config/tool-roles.yaml          — PRIMARY FILTER: which tools per role
  config/tool-chains.yaml         — chain docs (what fires automatically)
  fleet/mcp/roles/*.py            — role-specific group call names + docstrings
  config/agent-tooling.yaml       — MCP servers, plugins (names only)
  config/standing-orders.yaml     — autonomous authority per role
  config/agent-identities.yaml    — display names

Produces:
  agents/{name}/TOOLS.md          — focused reference card (2-4K target)

Usage:
  python scripts/generate-tools-md.py              # all agents
  python scripts/generate-tools-md.py architect     # single agent
  python scripts/generate-tools-md.py --compare     # show old vs new sizes
"""

import ast
import sys
from pathlib import Path

import yaml

FLEET_DIR = Path(__file__).resolve().parent.parent
CONFIG = FLEET_DIR / "config"
AGENTS_DIR = FLEET_DIR / "agents"
ROLES_DIR = FLEET_DIR / "fleet" / "mcp" / "roles"


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


# ── Role boundaries — from fleet-elevation specs ──────────────────────

ROLE_BOUNDARIES = {
    "project-manager": [
        "Implementation → software-engineer, devops",
        "Design decisions → architect",
        "Security decisions → devsecops-expert",
        "Work approval → fleet-ops",
        "PO gates → fleet_gate_request, don't decide",
    ],
    "fleet-ops": [
        "Task assignment → project-manager",
        "Implementation → software-engineer",
        "Design → architect",
        "PO decisions → escalate, don't decide",
    ],
    "architect": [
        "Implementation → software-engineer (transfer after design)",
        "Test predefinition → qa-engineer",
        "Security review → devsecops-expert",
        "Task assignment → project-manager",
    ],
    "devsecops-expert": [
        "Implementation → software-engineer",
        "Architecture → architect",
        "Task assignment → project-manager",
        "Work approval → fleet-ops (security_hold is separate)",
    ],
    "software-engineer": [
        "Architecture decisions → architect",
        "Test predefinition → qa-engineer",
        "Work approval → fleet-ops",
        "Security decisions → devsecops-expert",
        "Missing contributions → fleet_request_input, don't skip",
    ],
    "devops": [
        "Architecture decisions → architect",
        "Security decisions → devsecops-expert",
        "Work approval → fleet-ops",
        "Task assignment → project-manager",
    ],
    "qa-engineer": [
        "Implementation → software-engineer",
        "Architecture decisions → architect",
        "Work approval → fleet-ops",
        "Task assignment → project-manager",
    ],
    "technical-writer": [
        "Implementation → software-engineer",
        "Architecture decisions → architect",
        "Work approval → fleet-ops",
        "Technical accuracy → verify with engineer before publishing",
    ],
    "ux-designer": [
        "Implementation → software-engineer",
        "Architecture decisions → architect",
        "Work approval → fleet-ops",
        "UX at ALL levels — not just UI",
    ],
    "accountability-generator": [
        "Enforcement → feed immune system, don't enforce directly",
        "Task assignment → project-manager",
        "Work approval → fleet-ops",
        "Verify process, not quality (quality is fleet-ops)",
    ],
}


# ── Extract tool info from Python source ──────────────────────────────

def extract_role_tools(role_name: str) -> list[dict]:
    """Extract group call names and docstrings from the role-specific module."""
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
    filename = file_map.get(role_name)
    if not filename:
        return []
    path = ROLES_DIR / filename
    if not path.exists():
        return []
    with open(path) as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    tools = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            name = node.name
            if name.startswith(("pm_", "ops_", "arch_", "sec_", "eng_",
                                "devops_", "qa_", "writer_", "ux_", "acct_")):
                doc = ast.get_docstring(node) or ""
                tools.append({"name": name, "doc": doc})
    return tools


# ── Format a tool entry (focused) ────────────────────────────────────

def format_focused_tool(name: str, role_desc: dict, chain_info: dict | None) -> str:
    """Format a tool for the focused TOOLS.md.

    Uses role-specific usage/when from tool-roles.yaml.
    Adds chain summary from tool-chains.yaml.
    Adds critical notes (BLOCKED, special behavior).
    """
    lines = [f"### {name}"]

    # Role-specific description
    usage = role_desc.get("usage", "")
    if usage:
        lines.append(usage)

    when = role_desc.get("when", "")
    if when:
        lines.append(f"**When:** {when}")

    # Chain awareness — one line
    if chain_info:
        chain = chain_info.get("chain", "")
        if chain:
            lines.append(f"**→** {chain}")
        elif chain_info.get("chain_approve"):
            lines.append(f"**→ approve:** {chain_info['chain_approve']}")
            lines.append(f"**→ reject:** {chain_info.get('chain_reject', '')}")

    # Critical notes
    note = role_desc.get("note", "")
    if note:
        lines.append(f"_{note}_")

    # Blocked indicator
    if chain_info and chain_info.get("blocked"):
        lines.append(f"**{chain_info['blocked']}**")

    lines.append("")
    return "\n".join(lines)


def format_group_call(name: str, doc: str, chain_info: dict | None) -> str:
    """Format a role group call from its docstring."""
    lines = [f"### {name}"]

    if doc:
        doc_lines = doc.strip().split("\n")
        # First line = description
        lines.append(doc_lines[0].strip())

        # Extract Tree: section as chain
        tree_parts = []
        in_tree = False
        for dl in doc_lines[1:]:
            stripped = dl.strip()
            if stripped.startswith("Tree:"):
                in_tree = True
                continue
            if in_tree:
                if stripped and (stripped[0].isdigit() or stripped.startswith("-")):
                    tree_parts.append(stripped)
                elif not stripped:
                    continue
                else:
                    in_tree = False
        if tree_parts:
            lines.append(f"**→** {' → '.join(t.split('. ', 1)[-1].strip() for t in tree_parts[:4])}")
    elif chain_info:
        if chain_info.get("what"):
            lines.append(chain_info["what"])
        if chain_info.get("chain"):
            lines.append(f"**→** {chain_info['chain']}")
    else:
        lines.append("*(documentation pending)*")

    lines.append("")
    return "\n".join(lines)


# ── Main generator ────────────────────────────────────────────────────

def generate_tools_md(agent_name: str) -> str:
    """Generate focused TOOLS.md content for an agent.

    5 sections:
    1. Header
    2. Tools this role uses (from tool-roles.yaml + cross-role)
    3. Role group calls (from fleet/mcp/roles/*.py)
    4. Available tooling (MCP servers + plugins — names only)
    5. Boundaries + standing orders
    """
    # Load configs
    tool_roles = load_yaml(CONFIG / "tool-roles.yaml")
    chains = load_yaml(CONFIG / "tool-chains.yaml")
    tooling = load_yaml(CONFIG / "agent-tooling.yaml")
    standing_orders = load_yaml(CONFIG / "standing-orders.yaml")
    identities = load_yaml(CONFIG / "agent-identities.yaml")

    display_name = (identities.get("agents", {})
                    .get(agent_name, {})
                    .get("display_name", agent_name.replace("-", " ").title()))

    defaults = tooling.get("defaults", {})
    agent_config = tooling.get("agents", {}).get(agent_name, {})
    chain_tools = chains.get("tools", {})

    # ── Resolve this agent's tool set from tool-roles.yaml ─────
    agent_tool_descs = {}

    # Primary tools from role section
    role_section = tool_roles.get(agent_name, {})
    if isinstance(role_section, dict):
        for tname, tdesc in role_section.get("tools", {}).items():
            if isinstance(tdesc, dict):
                agent_tool_descs[tname] = tdesc

    # Cross-role tools where this agent is listed
    cross_role = tool_roles.get("_cross_role_tools", {})
    if isinstance(cross_role, dict):
        for tname, tdesc in cross_role.items():
            if isinstance(tdesc, dict) and agent_name in tdesc.get("roles", []):
                if tname not in agent_tool_descs:
                    agent_tool_descs[tname] = tdesc

    sections = []

    # ── § 1. Header ────────────────────────────────────────────
    sections.append(f"# Tools — {display_name}\n")
    sections.append(f"> `AGENT_NAME={agent_name}`\n")

    # ── § 2. Tools this role uses ──────────────────────────────
    if agent_tool_descs:
        sections.append("## Your Tools\n")
        tool_entries = []
        for tname, tdesc in agent_tool_descs.items():
            chain_info = chain_tools.get(tname)
            tool_entries.append(format_focused_tool(tname, tdesc, chain_info))
        sections.append("\n".join(tool_entries))

    # ── § 3. Role group calls ──────────────────────────────────
    role_tools_list = extract_role_tools(agent_name)
    role_chain_tools = chains.get("role_tools", {})
    if role_tools_list:
        sections.append("## Your Group Calls\n")
        call_entries = []
        for tool in role_tools_list:
            role_chain = role_chain_tools.get(tool["name"])
            call_entries.append(format_group_call(tool["name"], tool["doc"], role_chain))
        sections.append("\n".join(call_entries))

    # ── § 4. Available tooling (names only) ────────────────────
    mcp_names = ["fleet"]
    for srv in agent_config.get("mcp_servers", []):
        mcp_names.append(srv.get("name", "unknown"))

    all_plugins = defaults.get("plugins", []) + agent_config.get("plugins", [])

    avail_lines = ["## Available\n"]
    avail_lines.append(f"**MCP:** {' · '.join(mcp_names)}")
    if all_plugins:
        avail_lines.append(f"**Plugins:** {' · '.join(all_plugins)}")
    sections.append("\n".join(avail_lines) + "\n")

    # ── § 5. Boundaries + standing orders ──────────────────────
    boundaries = ROLE_BOUNDARIES.get(agent_name, [])
    if boundaries:
        b_lines = ["## Boundaries\n"]
        for b in boundaries:
            b_lines.append(f"- {b}")
        sections.append("\n".join(b_lines) + "\n")

    role_orders = standing_orders.get(agent_name, {})
    so_list = role_orders.get("standing_orders", [])
    authority = role_orders.get(
        "authority_level",
        standing_orders.get("defaults", {}).get("authority_level", "conservative"),
    )
    if so_list:
        so_lines = [f"## Standing Orders ({authority})\n"]
        for order in so_list:
            name = order.get("name", "unnamed")
            desc = order.get("description", "")
            boundary = order.get("boundary", "")
            so_lines.append(f"- **{name}:** {desc}")
            if boundary:
                so_lines.append(f"  _{boundary}_")
        sections.append("\n".join(so_lines) + "\n")

    return "\n".join(sections)


# ── CLI ───────────────────────────────────────────────────────────────

def main():
    tooling = load_yaml(CONFIG / "agent-tooling.yaml")
    agents = list(tooling.get("agents", {}).keys())
    compare_mode = "--compare" in sys.argv

    if len(sys.argv) > 1 and not compare_mode:
        target = sys.argv[1]
        if target not in agents:
            print(f"Unknown agent: {target}")
            print(f"Available: {', '.join(agents)}")
            sys.exit(1)
        agents = [target]

    print("=" * 55)
    print("  Generate TOOLS.md — focused desk, detail on-demand")
    print("=" * 55)
    print()

    total_old = 0
    total_new = 0

    for agent_name in agents:
        agent_dir = AGENTS_DIR / agent_name
        if not agent_dir.exists():
            print(f"  [skip] {agent_name}: no agents/{agent_name}/ directory")
            continue

        content = generate_tools_md(agent_name)
        tools_path = agent_dir / "TOOLS.md"

        new_size = len(content)
        old_size = len(tools_path.read_text()) if tools_path.exists() else 0

        if compare_mode:
            reduction = ((old_size - new_size) / old_size * 100) if old_size > 0 else 0
            print(f"  {agent_name:30s}  {old_size:6d} → {new_size:5d} chars  ({reduction:.0f}% reduction)")
            total_old += old_size
            total_new += new_size
            continue

        # Write
        if tools_path.exists():
            existing = tools_path.read_text()
            if existing == content:
                print(f"  [skip] {agent_name}: unchanged ({new_size} chars)")
                continue
            print(f"  [updated] {agent_name}: {old_size} → {new_size} chars")
        else:
            print(f"  [created] {agent_name}: {new_size} chars")

        tools_path.write_text(content)

    if compare_mode and total_old > 0:
        print()
        reduction = ((total_old - total_new) / total_old * 100)
        print(f"  {'TOTAL':30s}  {total_old:6d} → {total_new:5d} chars  ({reduction:.0f}% reduction)")

    print()
    print("Done.")


if __name__ == "__main__":
    main()
