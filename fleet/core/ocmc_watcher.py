"""OCMC watcher — detects Mission Control state changes and emits events.

Tracks task status transitions, new approvals, agent online/offline,
and board memory changes. Each detected delta becomes a CloudEvent.

Runs alongside the existing sync daemon but focuses on EVENT EMISSION
rather than sync actions. The sync daemon handles PR↔task sync.
This watcher handles observability and agent notification.

> "no matter from where I mention, that it be internal chat or Plane,
> or if I change something manually on the platform, you must detect
> and record the event"
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from fleet.core.events import EventStore, create_event
from fleet.core.models import Task, TaskStatus, Agent

logger = logging.getLogger(__name__)


@dataclass
class OCMCWatcherState:
    """Tracks last-known OCMC state for delta detection."""

    # task_id → {status, updated_at, assigned_agent}
    known_tasks: dict[str, dict] = field(default_factory=dict)
    # agent_name → status (online/offline/provisioning)
    known_agents: dict[str, str] = field(default_factory=dict)
    # approval_id → status
    known_approvals: dict[str, str] = field(default_factory=dict)
    # Last poll timestamp
    last_poll: str = ""


class OCMCWatcher:
    """Detects OCMC state changes and emits events.

    Usage::

        watcher = OCMCWatcher(mc_client, board_id)
        events = await watcher.poll(tasks, agents, approvals)
    """

    def __init__(self, state_path: str = "") -> None:
        self._store = EventStore()
        if not state_path:
            fleet_dir = os.environ.get("FLEET_DIR", ".")
            state_path = os.path.join(fleet_dir, ".fleet-ocmc-watcher.json")
        self._state_path = Path(state_path)
        self._state = self._load_state()

    def _load_state(self) -> OCMCWatcherState:
        if self._state_path.exists():
            try:
                with open(self._state_path) as f:
                    data = json.load(f)
                return OCMCWatcherState(
                    known_tasks=data.get("known_tasks", {}),
                    known_agents=data.get("known_agents", {}),
                    known_approvals=data.get("known_approvals", {}),
                    last_poll=data.get("last_poll", ""),
                )
            except Exception:
                pass
        return OCMCWatcherState()

    def _save_state(self) -> None:
        try:
            with open(self._state_path, "w") as f:
                json.dump({
                    "known_tasks": self._state.known_tasks,
                    "known_agents": self._state.known_agents,
                    "known_approvals": self._state.known_approvals,
                    "last_poll": self._state.last_poll,
                }, f)
        except Exception:
            pass

    def poll(
        self,
        tasks: list[Task],
        agents: list[Agent],
        approvals: list | None = None,
    ) -> list[dict]:
        """Detect state changes and emit events. Returns list of events emitted."""
        events_emitted = []

        # ── Task status transitions ──
        for task in tasks:
            task_key = task.id
            known = self._state.known_tasks.get(task_key, {})
            known_status = known.get("status", "")
            current_status = task.status.value

            if known_status and current_status != known_status:
                # Status changed — emit event
                agent_name = task.custom_fields.agent_name or ""
                project = task.custom_fields.project or ""

                # Determine event type and priority
                if current_status == "done":
                    event_type = "fleet.task.completed"
                    priority = "important"
                    recipient = "fleet-ops"
                elif current_status == "review":
                    event_type = "fleet.task.completed"
                    priority = "important"
                    recipient = "fleet-ops"
                elif current_status == "in_progress" and known_status == "inbox":
                    event_type = "fleet.task.dispatched"
                    priority = "info"
                    recipient = agent_name or "all"
                elif current_status == "inbox" and known_status in ("in_progress", "review"):
                    # Task sent back to inbox — impediment or rejection
                    event_type = "fleet.task.blocked"
                    priority = "important"
                    recipient = agent_name or "pm"
                else:
                    event_type = "fleet.system.sync"
                    priority = "info"
                    recipient = "all"

                event = create_event(
                    event_type,
                    source="fleet/core/ocmc_watcher",
                    subject=task.id,
                    recipient=recipient,
                    priority=priority,
                    mentions=[agent_name] if agent_name else [],
                    tags=[f"project:{project}", "status_change", current_status],
                    surfaces=["internal", "channel"],
                    task_title=task.title[:60],
                    old_status=known_status,
                    new_status=current_status,
                    agent=agent_name,
                )
                self._store.append(event)
                events_emitted.append({
                    "type": event_type,
                    "task": task.title[:40],
                    "change": f"{known_status} → {current_status}",
                })

            # Update known state
            self._state.known_tasks[task_key] = {
                "status": current_status,
                "updated_at": str(task.updated_at) if task.updated_at else "",
                "assigned_agent": task.custom_fields.agent_name or "",
            }

        # ── Agent online/offline transitions ──
        for agent in agents:
            if "Gateway" in agent.name:
                continue
            agent_key = agent.name
            known_status = self._state.known_agents.get(agent_key, "")
            current_status = agent.status

            if known_status and current_status != known_status:
                if current_status == "online" and known_status in ("offline", "provisioning"):
                    event = create_event(
                        "fleet.agent.online",
                        source="fleet/core/ocmc_watcher",
                        subject=agent.name,
                        recipient="all",
                        priority="info",
                        tags=["agent", "online"],
                        surfaces=["internal"],
                        agent=agent.name,
                    )
                    self._store.append(event)
                    events_emitted.append({"type": "fleet.agent.online", "agent": agent.name})

                elif current_status == "offline" and known_status == "online":
                    event = create_event(
                        "fleet.agent.offline",
                        source="fleet/core/ocmc_watcher",
                        subject=agent.name,
                        recipient="fleet-ops",
                        priority="important",
                        mentions=["fleet-ops"],
                        tags=["agent", "offline", "impediment"],
                        surfaces=["internal", "channel"],
                        agent=agent.name,
                    )
                    self._store.append(event)
                    events_emitted.append({"type": "fleet.agent.offline", "agent": agent.name})

            self._state.known_agents[agent_key] = current_status

        # ── Approval changes ──
        if approvals:
            for approval in approvals:
                approval_id = approval.id if hasattr(approval, "id") else str(approval.get("id", ""))
                status = approval.status if hasattr(approval, "status") else approval.get("status", "")
                known_status = self._state.known_approvals.get(approval_id, "")

                if known_status and status != known_status:
                    if status == "approved":
                        event = create_event(
                            "fleet.task.approved",
                            source="fleet/core/ocmc_watcher",
                            subject=approval_id,
                            recipient="all",
                            priority="info",
                            tags=["approved", "review"],
                            surfaces=["internal", "channel"],
                        )
                        self._store.append(event)
                        events_emitted.append({"type": "fleet.task.approved"})
                    elif status == "rejected":
                        event = create_event(
                            "fleet.task.rejected",
                            source="fleet/core/ocmc_watcher",
                            subject=approval_id,
                            recipient="all",
                            priority="important",
                            tags=["rejected", "review"],
                            surfaces=["internal", "channel", "notify"],
                        )
                        self._store.append(event)
                        events_emitted.append({"type": "fleet.task.rejected"})

                self._state.known_approvals[approval_id] = status

        self._state.last_poll = datetime.utcnow().isoformat() + "Z"
        self._save_state()

        return events_emitted