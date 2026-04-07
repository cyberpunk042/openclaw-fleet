"""Role-specific group calls — per-role MCP tools.

Each agent gets generic fleet tools (from tools.py) PLUS group calls
specific to their role. The server registers role tools based on the
FLEET_AGENT environment variable.

Architecture:
  server.py creates the FastMCP server
    → register_generic_tools(server)     from tools.py   (all agents)
    → register_role_tools(server, agent) from here        (per role)

Each role module (pm.py, fleet_ops.py, etc.) defines tools that
aggregate multiple operations into single agent-facing calls.
The agent calls ONE tool, the system executes the tree.

Source: fleet-elevation/05-14 (per-role specs)
        tools-system-full-capability-map.md (group call inventory)
        phase-c-group-call-architecture.md (this architecture)
"""

from __future__ import annotations

import importlib
import logging

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Agent name → role module mapping
# Each module must have a register_tools(server: FastMCP) function
ROLE_MODULES: dict[str, str] = {
    "project-manager": "fleet.mcp.roles.pm",
    "fleet-ops": "fleet.mcp.roles.fleet_ops",
    "architect": "fleet.mcp.roles.architect",
    "devsecops-expert": "fleet.mcp.roles.devsecops",
    "software-engineer": "fleet.mcp.roles.engineer",
    "devops": "fleet.mcp.roles.devops",
    "qa-engineer": "fleet.mcp.roles.qa",
    "technical-writer": "fleet.mcp.roles.writer",
    "ux-designer": "fleet.mcp.roles.ux",
    "accountability-generator": "fleet.mcp.roles.accountability",
}


def register_role_tools(server: FastMCP, agent_name: str) -> int:
    """Register role-specific group calls based on agent name.

    Called by server.py after generic tools are registered.
    Dynamically imports the role module and calls its register_tools().

    Args:
        server: The FastMCP server to register tools on.
        agent_name: The agent's name (from FLEET_AGENT env var).

    Returns:
        Number of role-specific tools registered.
    """
    module_path = ROLE_MODULES.get(agent_name)
    if not module_path:
        logger.debug("No role-specific tools for agent: %s", agent_name)
        return 0

    try:
        module = importlib.import_module(module_path)
        if hasattr(module, "register_tools"):
            # Count tools before and after to know how many were added
            before = len(server._tool_manager._tools) if hasattr(server, '_tool_manager') else 0
            module.register_tools(server)
            after = len(server._tool_manager._tools) if hasattr(server, '_tool_manager') else 0
            count = after - before
            logger.debug(
                "Registered %d role tools for %s from %s",
                count, agent_name, module_path,
            )
            return count
        else:
            logger.warning("Role module %s has no register_tools function", module_path)
            return 0
    except ImportError as e:
        # Module not yet implemented — this is expected during development
        logger.debug("Role module not yet implemented for %s: %s", agent_name, e)
        return 0
    except Exception as e:
        logger.error("Failed to register role tools for %s: %s", agent_name, e)
        return 0
