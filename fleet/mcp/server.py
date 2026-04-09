"""Fleet MCP Server — exposes fleet operations as native agent tools.

Agents call these tools naturally, like they call exec or read.
The server handles all infrastructure: MC API, IRC, GitHub, URL resolution.

Run: python -m fleet mcp-server
Or via .mcp.json in agent workspace (stdio transport).
"""

from __future__ import annotations

import os
import sys

from mcp.server.fastmcp import FastMCP

from fleet.mcp.tools import register_tools


def create_server() -> FastMCP:
    """Create and configure the Fleet MCP server.

    Two-phase tool registration:
    1. Generic fleet tools (all agents) — from tools.py
    2. Role-specific group calls (per agent) — from roles/

    The FLEET_AGENT env var determines which role-specific tools
    are registered. Each agent only sees their own role's group calls
    alongside the shared fleet tools.
    """
    server = FastMCP(
        name="fleet",
        instructions=(
            "Fleet operations tools for OpenFleet agents. "
            "Use these to interact with Mission Control, create PRs, "
            "post to IRC, and manage your task lifecycle. "
            "Your task data may be pre-embedded (injection:full). Use fleet_read_context to load additional task data when needed."
        ),
    )

    # Phase 1: Generic fleet tools (all agents)
    register_tools(server)

    # Phase 2: Role-specific group calls (per agent role)
    from fleet.mcp.roles import register_role_tools
    agent_name = os.environ.get("FLEET_AGENT", "")
    if agent_name:
        register_role_tools(server, agent_name)

    return server


def run_server() -> int:
    """Run the Fleet MCP server (stdio transport)."""
    # Debug: log startup to confirm server was spawned by OpenClaw
    debug_log = os.path.join(
        os.environ.get("FLEET_DIR", "."), ".fleet-mcp-debug.log"
    )
    # Truncate if over 1 MB to prevent unbounded growth
    try:
        if os.path.exists(debug_log) and os.path.getsize(debug_log) > 1_000_000:
            with open(debug_log, "w") as f:
                f.write("[truncated — exceeded 1 MB]\n")
    except Exception:
        pass
    try:
        with open(debug_log, "a") as f:
            from datetime import datetime
            f.write(f"[{datetime.now().isoformat()}] Fleet MCP server starting\n")
            f.write(f"  FLEET_DIR={os.environ.get('FLEET_DIR', '')}\n")
            f.write(f"  FLEET_TASK_ID={os.environ.get('FLEET_TASK_ID', '')}\n")
            f.write(f"  FLEET_AGENT={os.environ.get('FLEET_AGENT', '')}\n")
            f.write(f"  Python={sys.executable}\n")
    except Exception:
        pass

    server = create_server()

    # Log registered tools
    try:
        with open(debug_log, "a") as f:
            tools = server._tool_manager._tools
            f.write(f"  Tools registered: {len(tools)}\n")
            for name in sorted(tools.keys()):
                f.write(f"    - {name}\n")
    except Exception as e:
        try:
            with open(debug_log, "a") as f:
                f.write(f"  Tools logging error: {e}\n")
        except Exception:
            pass

    server.run(transport="stdio")
    return 0


if __name__ == "__main__":
    sys.exit(run_server())