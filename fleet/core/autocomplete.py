"""Autocomplete chain engineering — context arrangement for correct behavior.

This module ARRANGES data from existing systems into the onion order
that drives correct agent behavior. It does NOT generate data — it
reads from context_assembly, stage_context, agent-tooling config, and
contribution status, then formats in the order specified in §36.

The autocomplete chain is a FORMATTER, not a data source.

Data sources:
  - context_assembly.py → task context, methodology, artifacts, comments
  - stage_context.py → MUST/MUST NOT/CAN/HOW TO ADVANCE per stage
  - config/agent-tooling.yaml → skills, plugins, MCP servers per role
  - contributions.py → contribution status + missing
  - preembed.py → task formatting

Output: formatted text for task-context.md and fleet-context.md
that the gateway injects into agent system prompt.

8-layer onion order (fleet-elevation/02):
  1. IDENTITY.md    → grounding (who am I)
  2. SOUL.md        → values + anti-corruption
  3. CLAUDE.md      → role-specific rules
  4. TOOLS.md       → capabilities + chains
  5. AGENTS.md      → team + synergy
  6. fleet-context  → state + directives + messages
  7. task-context   → task + autocomplete chain ← THIS MODULE
  8. HEARTBEAT.md   → action prompt (what to do NOW)

Source: fleet-vision-architecture §36
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def format_task_context_chain(
    context: dict[str, Any],
    agent_tooling: dict[str, Any] | None = None,
    contribution_status: dict[str, Any] | None = None,
) -> str:
    """Format assembled task context into autocomplete chain order.

    Takes the output of context_assembly.assemble_task_context() and
    arranges it so AI's natural continuation IS correct behavior.

    Args:
        context: Output from assemble_task_context()
        agent_tooling: Per-agent tooling from config/agent-tooling.yaml
        contribution_status: From contributions.check_contribution_completeness()

    Returns:
        Formatted text for task-context.md
    """
    sections = []
    task = context.get("task", {})
    cf = context.get("custom_fields", {})
    methodology = context.get("methodology", {})

    # ── 1. Task header ──────────────────────────────────────────
    sections.append("# YOUR CURRENT TASK")
    sections.append(f"Task: {task.get('title', '')}")
    sections.append(
        f"Type: {cf.get('task_type', 'task')} | "
        f"Stage: {methodology.get('stage', 'unknown')} | "
        f"Readiness: {cf.get('readiness', 0)}%"
    )
    if cf.get("delivery_phase"):
        sections.append(f"Delivery Phase: {cf['delivery_phase']}")
    if task.get("is_blocked"):
        sections.append(f"⚠ BLOCKED by: {task.get('blocked_by', [])}")

    # ── 2. Verbatim requirement ─────────────────────────────────
    verbatim = cf.get("requirement_verbatim", "")
    if verbatim:
        sections.append("")
        sections.append("## VERBATIM REQUIREMENT")
        sections.append(f'"{verbatim}"')
        sections.append("(PO's exact words. Do not interpret. Do not rephrase.)")

    # ── 3. Stage protocol (from stage_context.py) ───────────────
    instructions = methodology.get("stage_instructions", "")
    if instructions:
        sections.append("")
        sections.append(instructions)

    # ── 4. Contributions received + missing ─────────────────────
    contributions = context.get("contributions", {})
    if contributions:
        sections.append("")
        sections.append("## INPUTS FROM COLLEAGUES")
        for contrib_type, content in contributions.items():
            display = contrib_type.replace("_", " ").title()
            sections.append(f"### {display}")
            sections.append(str(content))

    if contribution_status and not contribution_status.get("all_received", True):
        missing = contribution_status.get("missing", [])
        if missing:
            sections.append("")
            sections.append("## CONTRIBUTIONS STILL NEEDED")
            for m in missing:
                sections.append(f"- {m}")
            sections.append("(Use fleet_request_input if needed.)")

    # ── 5. Plan (if accepted) ───────────────────────────────────
    plan = context.get("plan")
    if plan:
        sections.append("")
        sections.append("## YOUR CONFIRMED PLAN")
        sections.append(str(plan))

    # ── 6. Artifact state ───────────────────────────────────────
    artifact = context.get("artifact", {})
    if artifact.get("type"):
        sections.append("")
        completeness = artifact.get("completeness", {})
        sections.append(
            f"## ARTIFACT: {artifact['type']} "
            f"({completeness.get('required_pct', 0):.0f}% complete)"
        )
        missing_fields = completeness.get("missing_required", [])
        if missing_fields:
            sections.append(f"Missing: {', '.join(missing_fields)}")

    # ── 7. Skills + plugins + commands (from config) ────────────
    if agent_tooling:
        skills = agent_tooling.get("skills", [])
        plugins = agent_tooling.get("plugins", [])
        if skills:
            sections.append("")
            sections.append("## YOUR SKILLS")
            for s in skills:
                sections.append(f"- /{s}")

        if plugins:
            sections.append("")
            sections.append("## ACTIVE PLUGINS")
            for p in plugins:
                sections.append(f"- {p}")

    # ── 8. Related tasks ────────────────────────────────────────
    related = context.get("related_tasks", [])
    if related:
        sections.append("")
        sections.append("## RELATED TASKS")
        for r in related:
            sections.append(
                f"- [{r.get('relation', '?')}] {r.get('title', '')} "
                f"({r.get('status', '')})"
            )

    # ── 9. Recent activity ──────────────────────────────────────
    activity = context.get("activity", [])
    if activity:
        sections.append("")
        sections.append("## RECENT ACTIVITY")
        for a in activity[:5]:
            sections.append(
                f"- {a.get('type', '')}: {a.get('summary', '')} "
                f"({a.get('agent', '')})"
            )

    return "\n".join(sections)


def format_heartbeat_context_chain(
    fleet_state: dict[str, Any],
    directives: list[dict],
    messages: list[dict],
    tasks: list[dict],
    role_data: str = "",
    events: list[dict] | None = None,
    agent_tooling: dict[str, Any] | None = None,
    contribution_tasks: list[dict] | None = None,
) -> str:
    """Format heartbeat context into autocomplete chain order.

    Priority order drives AI behavior:
    1. PO directives (HIGHEST — act on these first)
    2. Messages (@mentions — respond)
    3. Assigned tasks (do work)
    4. Contribution tasks (deliver specialist input)
    5. Role-specific data (proactive actions)
    6. Events (awareness)
    7. Tools/skills/plugins (capabilities)
    8. If nothing → HEARTBEAT_OK

    Args:
        fleet_state: {work_mode, cycle_phase, backend_mode, budget_mode}
        directives: PO directives for this agent
        messages: Board memory @mentions for this agent
        tasks: Agent's assigned tasks (formatted)
        role_data: Role-specific pre-embed data
        events: Events since last heartbeat
        agent_tooling: Skills, plugins from config
        contribution_tasks: Contribution tasks assigned to this agent
    """
    sections = []

    # ── Fleet state ─────────────────────────────────────────────
    sections.append("# FLEET STATE")
    sections.append(f"Mode: {fleet_state.get('work_mode', '')}")
    sections.append(f"Phase: {fleet_state.get('cycle_phase', '')}")
    if fleet_state.get("budget_mode"):
        sections.append(f"Tempo: {fleet_state['budget_mode']}")

    # ── PO directives (HIGHEST PRIORITY) ────────────────────────
    if directives:
        sections.append("")
        sections.append("## PO DIRECTIVES")
        for d in directives:
            sections.append(str(d.get("content", d)))
        sections.append("(These are PRIORITY. Read and act on them first.)")

    # ── Messages (@mentions) ────────────────────────────────────
    if messages:
        sections.append("")
        sections.append("## MESSAGES FOR YOU")
        for m in messages:
            sections.append(str(m.get("content", m)))

    # ── Assigned tasks ──────────────────────────────────────────
    if tasks:
        sections.append("")
        sections.append("## YOUR ASSIGNED TASKS")
        for t in tasks:
            sections.append(str(t))
        sections.append("(INBOX = new work. IN_PROGRESS = continue. REVIEW = wait.)")

    # ── Contribution tasks ──────────────────────────────────────
    if contribution_tasks:
        sections.append("")
        sections.append("## CONTRIBUTION TASKS")
        for c in contribution_tasks:
            sections.append(f"- {c.get('title', str(c))}")
        sections.append("(Use fleet_contribute to deliver your input.)")

    # ── Role-specific data ──────────────────────────────────────
    if role_data:
        sections.append("")
        sections.append("## ROLE-SPECIFIC DATA")
        sections.append(role_data)

    # ── Events since last heartbeat ─────────────────────────────
    if events:
        sections.append("")
        sections.append("## EVENTS SINCE LAST HEARTBEAT")
        for e in events[:10]:
            sections.append(f"- {e.get('type', '')}: {e.get('summary', str(e))}")

    # ── Tools, skills, plugins (from config, not invented) ──────
    if agent_tooling:
        skills = agent_tooling.get("skills", [])
        plugins = agent_tooling.get("plugins", [])
        if skills:
            sections.append("")
            sections.append("## YOUR SKILLS")
            for s in skills:
                sections.append(f"- /{s}")
        if plugins:
            sections.append("")
            sections.append("## ACTIVE PLUGINS")
            for p in plugins:
                sections.append(f"- {p}")

    return "\n".join(sections)


def load_agent_tooling(agent_name: str, fleet_dir: str = "") -> dict:
    """Load per-agent tooling from config/agent-tooling.yaml.

    Returns: {skills: [...], plugins: [...], mcp_servers: [...]}
    """
    import os
    import yaml

    if not fleet_dir:
        fleet_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))

    config_path = os.path.join(fleet_dir, "config", "agent-tooling.yaml")
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
    except Exception:
        return {"skills": [], "plugins": [], "mcp_servers": []}

    defaults = config.get("defaults", {})
    agent_cfg = config.get("agents", {}).get(agent_name, {})

    return {
        "skills": agent_cfg.get("skills", []),
        "plugins": defaults.get("plugins", []) + agent_cfg.get("plugins", []),
        "mcp_servers": [s.get("name", "") for s in agent_cfg.get("mcp_servers", [])],
    }
