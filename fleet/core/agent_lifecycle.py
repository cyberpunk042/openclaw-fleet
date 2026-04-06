"""Agent lifecycle — smart status management for fleet agents.

Tracks agent activity and manages transitions between states:
  ACTIVE → IDLE → SLEEPING → OFFLINE

Agents wake on: task assignment, tag reference, @mention, explicit wake.
After 1 HEARTBEAT_OK, the brain takes over evaluation (silent heartbeat).
The cron never stops — the brain intercepts and evaluates for free.

Heartbeat intervals come from the gateway config (openarms.json), not hardcoded.
Budget mode adjusts these intervals via update_cron_tempo(). MC's OFFLINE_AFTER
is derived per-agent from their CRON interval (interval * 1.5).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class AgentStatus(str, Enum):
    """Agent status — drives heartbeat behavior and cost.

    ACTIVE → IDLE → SLEEPING → OFFLINE

    After 1 HEARTBEAT_OK, agent transitions to IDLE and the brain
    takes over heartbeat evaluation. The cron still fires, but the
    brain intercepts — if nothing for this agent, silent OK ($0).
    If wake trigger found, brain fires real heartbeat with strategic config.

    The agent never stops. The brain is the filter between cron and Claude call.
    """

    ACTIVE = "active"       # Working on a task right now
    IDLE = "idle"           # 1 HEARTBEAT_OK — brain evaluates, cron still fires
    SLEEPING = "sleeping"   # Extended idle, brain evaluates
    OFFLINE = "offline"     # Very extended idle


# Transition thresholds (seconds) — time-based
SLEEPING_AFTER = 30 * 60      # 30 minutes idle → sleeping
OFFLINE_AFTER = 4 * 60 * 60   # 4 hours sleeping → offline

# Content-aware threshold — 1 HEARTBEAT_OK = brain takes over
IDLE_AFTER_HEARTBEAT_OK = 1   # 1 proper heartbeat with nothing → brain relay

# Default heartbeat interval when no CRON config is available (seconds).
# Should never be needed — agents should always have a CRON from openarms.json.
DEFAULT_HEARTBEAT_INTERVAL = 10 * 60  # 10 minutes


def parse_interval(every: str) -> int:
    """Parse an interval string like '10m' or '2h' to seconds."""
    match = re.match(r"(\d+)\s*(m|h|s)", every.strip().lower())
    if not match:
        return DEFAULT_HEARTBEAT_INTERVAL
    value = int(match.group(1))
    unit = match.group(2)
    if unit == "h":
        return value * 3600
    if unit == "m":
        return value * 60
    return value


@dataclass
class AgentState:
    """Tracked state for a single agent."""

    name: str
    cron_interval: int = DEFAULT_HEARTBEAT_INTERVAL  # From openarms.json heartbeat.every
    status: AgentStatus = AgentStatus.IDLE
    last_active_at: Optional[datetime] = None    # Last time agent had work
    last_heartbeat_at: Optional[datetime] = None  # Last MC heartbeat sent
    last_task_completed_at: Optional[datetime] = None
    current_task_id: Optional[str] = None
    # Content-aware lifecycle fields
    consecutive_heartbeat_ok: int = 0             # HEARTBEAT_OK count
    last_heartbeat_data_hash: str = ""            # Hash of pre-embed data at last heartbeat

    def update_activity(self, now: datetime, has_active_task: bool, task_id: str = "") -> None:
        """Update agent state based on current activity."""
        if has_active_task:
            self.status = AgentStatus.ACTIVE
            self.last_active_at = now
            self.current_task_id = task_id
            self.consecutive_heartbeat_ok = 0  # reset — agent is working
            return

        # No active task — transition based on idle duration
        if self.last_active_at is None:
            self.last_active_at = now

        idle_seconds = (now - self.last_active_at).total_seconds()

        if self.consecutive_heartbeat_ok >= IDLE_AFTER_HEARTBEAT_OK:
            if idle_seconds >= OFFLINE_AFTER:
                self.status = AgentStatus.OFFLINE
            elif idle_seconds >= SLEEPING_AFTER:
                self.status = AgentStatus.SLEEPING
            else:
                self.status = AgentStatus.IDLE
        else:
            self.status = AgentStatus.IDLE

        self.current_task_id = None

    def needs_heartbeat(self, now: datetime) -> bool:
        """Check if this agent's CRON interval has elapsed.

        Uses the per-agent interval from openarms.json (set by budget mode).
        Active agents don't need heartbeats — they drive their own work.
        """
        if self.status == AgentStatus.ACTIVE:
            return False

        if self.last_heartbeat_at is None:
            return True

        return (now - self.last_heartbeat_at).total_seconds() >= self.cron_interval

    def record_heartbeat_ok(self) -> None:
        """Record that the agent's heartbeat returned HEARTBEAT_OK.

        After 1 HEARTBEAT_OK, the brain takes over evaluation.
        The cron still fires, brain intercepts for free.
        """
        self.consecutive_heartbeat_ok += 1

    def record_heartbeat_work(self) -> None:
        """Record that the agent's heartbeat produced actual work.

        Resets the HEARTBEAT_OK counter — agent is active.
        """
        self.consecutive_heartbeat_ok = 0

    def mark_heartbeat_sent(self, now: datetime) -> None:
        """Record that an MC heartbeat was sent. Resets the CRON timer."""
        self.last_heartbeat_at = now

    def wake(self, now: datetime) -> None:
        """Explicitly wake this agent (task assigned, @mention, etc.).

        Resets CRON timer — the wake itself counts as a heartbeat.
        """
        self.status = AgentStatus.IDLE
        self.last_active_at = now
        self.last_heartbeat_at = now  # reset CRON — wake is a heartbeat
        self.consecutive_heartbeat_ok = 0

    def should_wake_for_task(self) -> bool:
        """Check if agent should be woken for a task assignment."""
        return self.status in (AgentStatus.IDLE, AgentStatus.SLEEPING, AgentStatus.OFFLINE)

    @property
    def brain_evaluates(self) -> bool:
        """Whether the brain should intercept this agent's heartbeat.

        After 1 HEARTBEAT_OK, the brain evaluates deterministically
        instead of making a Claude call. The cron still fires.
        """
        return self.consecutive_heartbeat_ok >= IDLE_AFTER_HEARTBEAT_OK


class FleetLifecycle:
    """Manages the lifecycle state of all fleet agents.

    Per-agent CRON intervals come from openarms.json (the gateway config).
    The orchestrator calls load_intervals() on startup and after budget mode changes.
    """

    def __init__(self) -> None:
        self._agents: dict[str, AgentState] = {}

    def get_or_create(self, name: str) -> AgentState:
        """Get or create agent state tracker."""
        if name not in self._agents:
            self._agents[name] = AgentState(name=name)
        return self._agents[name]

    def load_intervals(self, agent_intervals: dict[str, int]) -> None:
        """Update per-agent CRON intervals from gateway config.

        Args:
            agent_intervals: Map of agent_name → interval_seconds.
                             Typically parsed from openarms.json heartbeat.every.
        """
        for name, interval_sec in agent_intervals.items():
            state = self.get_or_create(name)
            state.cron_interval = interval_sec

    def update_all(
        self,
        now: datetime,
        active_agents: dict[str, str],  # agent_name → task_id
    ) -> None:
        """Update all tracked agents based on current board state."""
        for name, state in self._agents.items():
            task_id = active_agents.get(name, "")
            state.update_activity(now, bool(task_id), task_id)

    def agents_needing_heartbeat(self, now: datetime) -> list[AgentState]:
        """Return agents whose CRON interval has elapsed."""
        return [
            state for state in self._agents.values()
            if state.needs_heartbeat(now)
        ]

    def get_status_summary(self) -> dict[str, list[str]]:
        """Return agent names grouped by status."""
        summary: dict[str, list[str]] = {
            "active": [],
            "idle": [],
            "sleeping": [],
            "offline": [],
        }
        for state in self._agents.values():
            summary[state.status.value].append(state.name)
        return summary

    def is_fleet_idle(self) -> bool:
        """Check if the entire fleet has no active work."""
        return all(
            s.status != AgentStatus.ACTIVE
            for s in self._agents.values()
        )
