"""Stage-aware context — protocol instructions per methodology stage.

When an agent is dispatched, it receives instructions appropriate to
the current methodology stage of its task. An agent in "conversation"
stage gets different instructions than one in "work" stage.

Protocol text and stage summaries are loaded from config/methodology.yaml.
PO can modify protocols by editing the config file.
"""

from __future__ import annotations

from fleet.core.methodology_config import get_methodology_config


def get_stage_instructions(stage: str) -> str:
    """Get the protocol instructions for a methodology stage.

    Args:
        stage: The stage value (conversation, analysis, etc.)

    Returns:
        Instruction text for the agent. Empty string if stage unknown.
    """
    try:
        cfg = get_methodology_config()
        s = cfg.stage_by_name(stage)
        if s:
            return s.protocol
    except Exception:
        pass
    return ""


def get_stage_summary(stage: str) -> str:
    """Get a one-line summary of what the agent should be doing.

    Used in compact displays (e.g., heartbeat summary, event stream).
    """
    try:
        cfg = get_methodology_config()
        s = cfg.stage_by_name(stage)
        if s:
            return s.summary
    except Exception:
        pass
    return f"Stage: {stage}"
