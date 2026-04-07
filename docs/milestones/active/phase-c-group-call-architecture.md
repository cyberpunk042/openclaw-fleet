# Phase C: Role-Specific Group Call Architecture

**Date:** 2026-04-07
**Status:** Architecture design — before implementation
**Part of:** [tools-system-session-index.md](tools-system-session-index.md) — Phase C
**PO instruction:** "no rush. we take our time. we never at any point start rushing or doing quickfix or cutting corners or short circuiting the investigations and research."

---

## The Architecture Decision

### Problem

~35-40 role-specific group calls need to be built. Each is a new MCP tool with a tree of operations. They can't all go in tools.py (already ~3800 lines). They need to be organized by role and only visible to the relevant agent.

### Decision: Role-Aware Registration on Same Server

The fleet MCP server (single server per agent session) registers tools in two phases:

1. **Generic tools** — all 30 shared fleet tools (fleet_commit, fleet_chat, etc.) — registered for ALL agents
2. **Role-specific tools** — registered based on `FLEET_AGENT` env var → role lookup

Each agent's server instance only registers the tools for their role. The architect's server has fleet tools + architect group calls. The QA engineer's server has fleet tools + QA group calls. No agent sees another role's group calls.

### Why This Approach

- **Single MCP server** — deployment simplicity (one server process per agent, as today)
- **Role filtering at registration** — agent only sees their tools (clean context, less confusion)
- **Separate files per role** — maintainable code (fleet/mcp/roles/{role}.py)
- **Same infrastructure** — same ChainRunner, same context, same clients

### Code Structure

```
fleet/mcp/
├── server.py              # Creates server, calls register_tools()
├── tools.py               # Generic fleet tools (30) — register_generic_tools()
├── context.py             # Shared context (FleetMCPContext)
└── roles/                 # NEW — per-role group calls
    ├── __init__.py        # register_role_tools(server, agent_name)
    ├── pm.py              # PM group calls (~5 tools)
    ├── fleet_ops.py       # Fleet-ops group calls (~4 tools)
    ├── architect.py       # Architect group calls (~4 tools)
    ├── devsecops.py       # DevSecOps group calls (~6 tools)
    ├── engineer.py        # Engineer group calls (~3 tools)
    ├── devops.py          # DevOps group calls (~4 tools)
    ├── qa.py              # QA group calls (~4 tools)
    ├── writer.py          # Writer group calls (~3 tools)
    ├── ux.py              # UX group calls (~2 tools)
    └── accountability.py  # Accountability group calls (~3 tools)
```

### Registration Flow

```python
# server.py
def create_server() -> FastMCP:
    server = FastMCP(name="fleet", instructions="...")
    
    # Phase 1: Generic fleet tools (all agents)
    from fleet.mcp.tools import register_generic_tools
    register_generic_tools(server)
    
    # Phase 2: Role-specific group calls (per agent)
    from fleet.mcp.roles import register_role_tools
    agent_name = os.environ.get("FLEET_AGENT", "")
    register_role_tools(server, agent_name)
    
    return server
```

```python
# fleet/mcp/roles/__init__.py
from __future__ import annotations

import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Role → module mapping
ROLE_MODULES = {
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


def register_role_tools(server: FastMCP, agent_name: str) -> None:
    """Register role-specific group calls based on agent name."""
    module_path = ROLE_MODULES.get(agent_name)
    if not module_path:
        logger.debug("No role-specific tools for agent: %s", agent_name)
        return
    
    try:
        import importlib
        module = importlib.import_module(module_path)
        if hasattr(module, "register_tools"):
            module.register_tools(server)
            logger.debug("Registered role tools for %s from %s", agent_name, module_path)
    except Exception as e:
        logger.error("Failed to register role tools for %s: %s", agent_name, e)
```

### Per-Role Module Pattern

Each role module follows the same pattern:

```python
# fleet/mcp/roles/qa.py
"""QA Engineer role-specific group calls.

These tools aggregate multiple operations into single agent-facing calls.
The QA engineer calls ONE tool, the system executes the tree.

Source: fleet-elevation/11 (QA role spec), tools-system-full-capability-map.md
"""

from __future__ import annotations
from mcp.server.fastmcp import FastMCP
from fleet.mcp.context import FleetMCPContext

_ctx: FleetMCPContext | None = None

def _get_ctx() -> FleetMCPContext:
    global _ctx
    if _ctx is None:
        _ctx = FleetMCPContext.from_env()
    return _ctx


def register_tools(server: FastMCP) -> None:
    """Register QA-specific group calls."""

    @server.tool()
    async def qa_test_predefinition(task_id: str) -> dict:
        """Predefine test criteria for a task entering reasoning stage.
        
        Reads the target task's verbatim requirement and acceptance criteria,
        then produces structured test criteria (TC-001 format) and delivers
        them via fleet_contribute.
        
        This is a GROUP CALL that:
        1. Reads target task details
        2. Reads architect design input (if available)
        3. Produces structured qa_test_definition
        4. Calls fleet_contribute to deliver
        5. Records trail
        
        Args:
            task_id: Target task to predefine tests for.
        """
        # ... full implementation using building blocks ...
```

### Naming Convention

Role-specific tools use the role prefix:
- PM: `pm_sprint_standup`, `pm_epic_breakdown`, `pm_contribution_check`, `pm_gate_route`, `pm_blocker_resolve`
- Fleet-ops: `ops_real_review`, `ops_board_health_scan`, `ops_compliance_spot_check`, `ops_budget_assessment`
- Architect: `arch_design_contribution`, `arch_codebase_assessment`, `arch_option_comparison`, `arch_complexity_estimate`
- DevSecOps: `sec_dependency_audit`, `sec_code_scan`, `sec_secret_scan`, `sec_pr_security_review`, `sec_contribution`, `sec_infrastructure_health`
- Engineer: `eng_contribution_check`, `eng_implementation_cycle`, `eng_fix_task_response`
- DevOps: `devops_infrastructure_health`, `devops_deployment_contribution`, `devops_cicd_review`, `devops_phase_infrastructure`
- QA: `qa_test_predefinition`, `qa_test_validation`, `qa_coverage_analysis`, `qa_acceptance_criteria_review`
- Writer: `writer_staleness_scan`, `writer_doc_contribution`, `writer_doc_from_completion`
- UX: `ux_spec_contribution`, `ux_accessibility_audit`
- Accountability: `acct_trail_reconstruction`, `acct_sprint_compliance`, `acct_pattern_detection`

### What Each Group Call Needs

Every role-specific group call needs:
1. **Docstring** — clear description of what it does and what tree it fires
2. **Input validation** — check required params, resolve task context
3. **Primary operations** — the core work (read data, produce output, call fleet tools)
4. **Chain propagation** — trail, Plane, IRC, events (via ChainRunner or direct)
5. **Error handling** — try/except with best-effort for non-critical operations
6. **Return value** — structured result with ok, data, and any suggestions

### Implementation Order

Start with the most critical roles (whose group calls unblock the most work):

1. **PM** — pm_sprint_standup, pm_epic_breakdown, pm_contribution_check (PM drives the board — without these, nothing moves)
2. **Fleet-ops** — ops_real_review (reviews everything — without this, nothing completes)
3. **QA** — qa_test_predefinition, qa_test_validation (tests are requirements for implementation)
4. **Architect** — arch_design_contribution (design before implementation)
5. **DevSecOps** — sec_contribution, sec_dependency_audit (security requirements)
6. **Engineer** — eng_contribution_check (verify inputs before work)
7. **DevOps** — devops_infrastructure_health
8. **Writer** — writer_doc_contribution
9. **UX** — ux_spec_contribution
10. **Accountability** — acct_trail_reconstruction

### Testing Strategy

Each role module gets its own test file:
- fleet/tests/mcp/test_role_pm.py
- fleet/tests/mcp/test_role_fleet_ops.py
- etc.

Tests mock MC/IRC/Plane clients and verify:
- Tool registered correctly
- Input validation works
- Primary operations called with correct params
- Chain propagation fires
- Trail recorded
- Error handling doesn't crash

---

## Relationship to Existing Work

- Generic fleet tools (tools.py) remain unchanged — Phase A completed
- The shared FleetMCPContext is used by both generic and role-specific tools
- ChainRunner and EventChain handle propagation for role-specific tools too
- Role-specific tools can call generic fleet tools (fleet_contribute, fleet_task_create, etc.)
- config/tool-roles.yaml will need updating to include role-specific tool names (Phase G)

---

## What This Document Does NOT Cover

- The IMPLEMENTATION of each role's group calls — each is substantial (8-15 operations per tool)
- Per-role skills (Phase D) — skills teach HOW to use group calls, group calls ARE the calls
- CRONs (Phase E) — CRONs invoke group calls on schedule
- The specific tree operations per group call — these need per-role design docs referencing fleet-elevation/05-14

Each role's group calls are a design + implementation effort comparable to what Phase A did for generic fleet tools. ~35-40 tools × average 10 operations = ~350-400 operations total.
