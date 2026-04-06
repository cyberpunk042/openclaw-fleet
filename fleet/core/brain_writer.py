"""Brain decision writer — evaluates agents and writes .brain-decision.json.

Called by the orchestrator EVERY cycle to keep decision files fresh.
The gateway HeartbeatRunner reads these files when its CRON fires:
  - decision=silent → skip Claude call ($0)
  - decision=wake/strategic → call Claude with adapted context

This module only writes decisions. It does NOT call MC or touch heartbeat
timers. MC liveness (heartbeat_agent) is handled by the orchestrator at
CRON intervals, separately from brain evaluation.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path

from fleet.core.agent_lifecycle import AgentStatus, FleetLifecycle
from fleet.core.heartbeat_gate import (
    HeartbeatDecision,
    HeartbeatEvaluation,
    evaluate_agent_heartbeat,
)

logger = logging.getLogger(__name__)

DECISION_FILENAME = ".brain-decision.json"


def write_brain_decisions(
    lifecycle: FleetLifecycle,
    now: datetime,
    tasks: list,
    agents: list,
    board_memory: list,
    fleet_dir: str,
) -> dict[str, HeartbeatEvaluation]:
    """Evaluate ALL non-active agents and write decision files.

    Runs every orchestrator cycle to keep .brain-decision.json fresh.
    The gateway checks file freshness (<5 min) before each heartbeat.

    Returns dict of agent_name → HeartbeatEvaluation.
    """
    results: dict[str, HeartbeatEvaluation] = {}

    # Evaluate ALL non-active agents — not gated by CRON interval.
    # Brain decisions must be fresh every cycle so the gateway always
    # has a recent file when its HeartbeatRunner CRON fires.
    for agent_state in lifecycle._agents.values():
        if agent_state.status == AgentStatus.ACTIVE:
            continue  # Active agents drive their own work

        agent_name = agent_state.name

        # Mentions: board memory entries that mention this agent
        mentions = [
            m for m in board_memory
            if f"@{agent_name}" in str(m.get("content", ""))
        ]

        # Assigned tasks for this agent
        assigned = []
        for t in tasks:
            t_agent = ""
            if hasattr(t, 'custom_fields') and t.custom_fields:
                t_agent = getattr(t.custom_fields, 'agent_name', '') or ''
            elif isinstance(t, dict):
                t_agent = t.get("agent_name", "")
            if t_agent == agent_name:
                assigned.append(t if isinstance(t, dict) else {"title": getattr(t, 'title', ''), "status": getattr(t, 'status', ''), "agent_name": t_agent})

        # Directives targeted at this agent
        directives = [
            m for m in board_memory
            if "directive" in str(m.get("tags", []))
            and agent_name in str(m.get("content", ""))
        ]

        # Contributions pending
        contributions = []
        for t in tasks:
            t_target = ""
            t_status = ""
            if hasattr(t, 'custom_fields') and t.custom_fields:
                t_target = getattr(t.custom_fields, 'contribution_target', '') or ''
                t_status = getattr(t, 'status', '')
            elif isinstance(t, dict):
                t_target = t.get("contribution_target", "")
                t_status = t.get("status", "")
            if t_target == agent_name and t_status == "inbox":
                contributions.append(t if isinstance(t, dict) else {"title": getattr(t, 'title', ''), "status": t_status})

        evaluation = evaluate_agent_heartbeat(
            agent_name=agent_name,
            agent_role=agent_name,
            mentions=mentions,
            assigned_tasks=assigned,
            directives=directives,
            contributions_pending=contributions,
            events_since_last=[],
            consecutive_heartbeat_ok=agent_state.consecutive_heartbeat_ok,
        )

        _write_decision(fleet_dir, agents, agent_name, evaluation)
        results[agent_name] = evaluation

    return results


def _write_decision(
    fleet_dir: str,
    agents: list,
    agent_name: str,
    evaluation: HeartbeatEvaluation,
) -> None:
    """Write .brain-decision.json to agent's workspace."""
    workspace = None
    for a in agents:
        name = a.name if hasattr(a, 'name') else a.get("name", "")
        if name == agent_name:
            agent_id = a.id if hasattr(a, 'id') else a.get("id", "")
            workspace = os.path.join(fleet_dir, f"workspace-mc-{agent_id}")
            break

    if not workspace or not os.path.isdir(workspace):
        logger.warning("No workspace found for %s", agent_name)
        return

    decision_path = os.path.join(workspace, DECISION_FILENAME)
    try:
        data = {
            "decision": evaluation.decision.value,
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "reasons": [
                {"trigger": r.trigger, "details": r.details, "urgency": r.urgency}
                for r in evaluation.reasons
            ],
        }
        if evaluation.model_override:
            data["model_override"] = evaluation.model_override
        if evaluation.effort_override:
            data["effort_override"] = evaluation.effort_override

        with open(decision_path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.warning("Failed to write brain decision for %s: %s", agent_name, e)
