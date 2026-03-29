"""Effort profiles — control fleet intensity based on budget and circumstances.

Profiles:
  full         — All agents active, normal heartbeats, opus for complex tasks
  conservative — Only drivers active, longer heartbeats, sonnet only
  minimal      — Only fleet-ops monitoring, no dispatching, emergency only
  paused       — Nothing runs, gateway heartbeats disabled

Set via: fleet effort <profile> or config/fleet.yaml
The orchestrator reads the active profile and adjusts behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class EffortProfile:
    """Configuration for fleet operating intensity."""

    name: str
    description: str
    max_dispatch_per_cycle: int
    heartbeat_drivers_min: int      # Minutes between driver heartbeats
    heartbeat_workers_min: int      # Minutes between worker heartbeats
    allow_opus: bool                # Allow opus model for complex tasks
    allow_dispatch: bool            # Allow dispatching new tasks
    allow_heartbeats: bool          # Allow gateway heartbeats
    active_agents: list[str]        # Which agents can be active ("all" or specific names)


PROFILES: dict[str, EffortProfile] = {
    "full": EffortProfile(
        name="full",
        description="Full fleet operation — all agents, all models",
        max_dispatch_per_cycle=2,
        heartbeat_drivers_min=30,
        heartbeat_workers_min=60,
        allow_opus=True,
        allow_dispatch=True,
        allow_heartbeats=True,
        active_agents=["all"],
    ),
    "conservative": EffortProfile(
        name="conservative",
        description="Budget-conscious — drivers only, sonnet only, less frequent",
        max_dispatch_per_cycle=1,
        heartbeat_drivers_min=60,
        heartbeat_workers_min=120,
        allow_opus=False,
        allow_dispatch=True,
        allow_heartbeats=True,
        active_agents=["project-manager", "fleet-ops", "devsecops-expert"],
    ),
    "minimal": EffortProfile(
        name="minimal",
        description="Emergency mode — fleet-ops monitoring only, no dispatch",
        max_dispatch_per_cycle=0,
        heartbeat_drivers_min=120,
        heartbeat_workers_min=0,  # 0 = disabled
        allow_opus=False,
        allow_dispatch=False,
        allow_heartbeats=True,
        active_agents=["fleet-ops"],
    ),
    "paused": EffortProfile(
        name="paused",
        description="Fleet stopped — nothing runs",
        max_dispatch_per_cycle=0,
        heartbeat_drivers_min=0,
        heartbeat_workers_min=0,
        allow_opus=False,
        allow_dispatch=False,
        allow_heartbeats=False,
        active_agents=[],
    ),
}


def get_profile(name: str) -> Optional[EffortProfile]:
    """Get an effort profile by name."""
    return PROFILES.get(name)


def get_active_profile_name(fleet_dir: str = "") -> str:
    """Read the active effort profile from config."""
    import os
    import yaml

    if fleet_dir:
        config_path = os.path.join(fleet_dir, "config", "fleet.yaml")
    else:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "config", "fleet.yaml",
        )

    try:
        with open(config_path) as f:
            cfg = yaml.safe_load(f) or {}
        return cfg.get("orchestrator", {}).get("effort_profile", "full")
    except Exception:
        return "full"


def should_dispatch(profile: EffortProfile) -> bool:
    """Check if dispatching is allowed under the current profile."""
    return profile.allow_dispatch and profile.max_dispatch_per_cycle > 0


def is_agent_active(profile: EffortProfile, agent_name: str) -> bool:
    """Check if an agent is allowed to be active under the current profile."""
    if "all" in profile.active_agents:
        return True
    return agent_name in profile.active_agents