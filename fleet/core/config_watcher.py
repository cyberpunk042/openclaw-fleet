"""Config change detection — detect when IaC files are modified.

Watches config files and emits events when they change.
This enables the system to detect manual edits and trigger re-sync.

Tracked files:
  - config/fleet.yaml — orchestrator config, effort profiles
  - config/agent-identities.yaml — agent roster
  - config/projects.yaml — project registry
  - DSPD config/mission.yaml — Plane mission structure
  - DSPD config/*-board.yaml — project board content
  - agents/*/agent.yaml — agent definitions

> "if I change something manually on the platform, you must detect
> and record the event and do the appropriate chain of operations"
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from fleet.core.events import EventStore, create_event


@dataclass
class ConfigWatcherState:
    """Tracks file hashes for change detection."""
    file_hashes: dict[str, str] = field(default_factory=dict)  # path → sha256
    last_check: str = ""


class ConfigWatcher:
    """Watches config files for changes and emits events.

    Usage::

        watcher = ConfigWatcher()
        events = watcher.check()
    """

    def __init__(self, state_path: str = "") -> None:
        self._store = EventStore()
        fleet_dir = os.environ.get("FLEET_DIR", ".")
        if not state_path:
            state_path = os.path.join(fleet_dir, ".fleet-config-watcher.json")
        self._state_path = Path(state_path)
        self._fleet_dir = Path(fleet_dir)
        self._state = self._load_state()

        # Files to watch
        self._watched_files = self._discover_files()

    def _discover_files(self) -> list[Path]:
        """Discover config files to watch."""
        files = []

        # Fleet config
        for name in ["fleet.yaml", "agent-identities.yaml", "projects.yaml"]:
            p = self._fleet_dir / "config" / name
            if p.exists():
                files.append(p)

        # Agent configs
        agents_dir = self._fleet_dir / "agents"
        if agents_dir.exists():
            for d in agents_dir.iterdir():
                if d.is_dir() and not d.name.startswith("_"):
                    agent_yaml = d / "agent.yaml"
                    if agent_yaml.exists():
                        files.append(agent_yaml)
                    heartbeat = d / "HEARTBEAT.md"
                    if heartbeat.exists():
                        files.append(heartbeat)

        # DSPD configs (if adjacent repo exists)
        dspd_dir = self._fleet_dir.parent / "devops-solution-product-development"
        if dspd_dir.exists():
            mission = dspd_dir / "config" / "mission.yaml"
            if mission.exists():
                files.append(mission)
            for board_file in (dspd_dir / "config").glob("*-board.yaml"):
                files.append(board_file)
            roles_file = dspd_dir / "config" / "fleet-roles.yaml"
            if roles_file.exists():
                files.append(roles_file)
            members_file = dspd_dir / "config" / "fleet-members.yaml"
            if members_file.exists():
                files.append(members_file)

        return files

    def _load_state(self) -> ConfigWatcherState:
        if self._state_path.exists():
            try:
                with open(self._state_path) as f:
                    data = json.load(f)
                return ConfigWatcherState(
                    file_hashes=data.get("file_hashes", {}),
                    last_check=data.get("last_check", ""),
                )
            except Exception:
                pass
        return ConfigWatcherState()

    def _save_state(self) -> None:
        try:
            with open(self._state_path, "w") as f:
                json.dump({
                    "file_hashes": self._state.file_hashes,
                    "last_check": self._state.last_check,
                }, f)
        except Exception:
            pass

    def _hash_file(self, path: Path) -> str:
        """SHA256 hash of file contents."""
        try:
            return hashlib.sha256(path.read_bytes()).hexdigest()
        except Exception:
            return ""

    def check(self) -> list[dict]:
        """Check all watched files for changes. Returns events emitted."""
        events_emitted = []

        for file_path in self._watched_files:
            str_path = str(file_path)
            current_hash = self._hash_file(file_path)
            known_hash = self._state.file_hashes.get(str_path, "")

            if not current_hash:
                continue

            if known_hash and current_hash != known_hash:
                # File changed!
                rel_path = str(file_path.relative_to(self._fleet_dir)) if str(file_path).startswith(str(self._fleet_dir)) else file_path.name

                # Determine what kind of config changed
                if "mission.yaml" in str_path:
                    config_type = "mission"
                    priority = "important"
                    recipient = "project-manager"
                elif "fleet.yaml" in str_path:
                    config_type = "orchestrator"
                    priority = "important"
                    recipient = "fleet-ops"
                elif "agent-identities" in str_path or "agent.yaml" in str_path:
                    config_type = "agent"
                    priority = "info"
                    recipient = "fleet-ops"
                elif "board.yaml" in str_path:
                    config_type = "board"
                    priority = "info"
                    recipient = "project-manager"
                elif "HEARTBEAT" in str_path:
                    config_type = "heartbeat"
                    priority = "info"
                    # Extract agent name from path
                    agent_name = file_path.parent.name
                    recipient = agent_name
                elif "fleet-roles" in str_path or "fleet-members" in str_path:
                    config_type = "roles"
                    priority = "info"
                    recipient = "fleet-ops"
                else:
                    config_type = "config"
                    priority = "info"
                    recipient = "all"

                event = create_event(
                    "fleet.system.config_changed",
                    source="fleet/core/config_watcher",
                    subject=rel_path,
                    recipient=recipient,
                    priority=priority,
                    tags=["config", config_type, "sync_needed"],
                    surfaces=["internal"],
                    file_path=rel_path,
                    config_type=config_type,
                )
                self._store.append(event)
                events_emitted.append({
                    "type": "fleet.system.config_changed",
                    "file": rel_path,
                    "config_type": config_type,
                })

            # Update hash (including first-time)
            self._state.file_hashes[str_path] = current_hash

        self._state.last_check = datetime.utcnow().isoformat() + "Z"
        self._save_state()

        return events_emitted