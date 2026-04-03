"""Fleet budget — view and manage budget modes.

Usage:
    python -m fleet budget                    # Show current mode
    python -m fleet budget set <mode>         # Set budget mode
    python -m fleet budget modes              # List defined modes
    python -m fleet budget report             # Cost breakdown
"""

from __future__ import annotations

import os
import sys

from fleet.core.budget_modes import (
    BUDGET_MODES,
    MODE_ORDER,
    get_active_mode_name,
    get_mode,
)

BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
DIM = "\033[2m"
NC = "\033[0m"


def show_current(fleet_dir: str = "") -> int:
    """Show current budget mode."""
    active = get_active_mode_name(fleet_dir)

    print(f"\n{BOLD}Budget Mode{NC}")
    if active:
        mode = get_mode(active)
        if mode:
            print(f"  Active: {active}")
            print(f"  {DIM}{mode.description}{NC}")
            print(f"  Tempo multiplier: {mode.tempo_multiplier}")
        else:
            print(f"  Active: {active} {RED}(not defined in BUDGET_MODES){NC}")
    else:
        print(f"  {DIM}No budget mode configured{NC}")

    print()
    return 0


def set_mode(mode_name: str, fleet_dir: str = "") -> int:
    """Set the global budget mode."""
    if BUDGET_MODES and mode_name not in BUDGET_MODES:
        print(f"{RED}Unknown mode: {mode_name}{NC}")
        print(f"Available: {', '.join(MODE_ORDER)}")
        return 1

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
    except FileNotFoundError:
        cfg = {}

    if "orchestrator" not in cfg:
        cfg["orchestrator"] = {}
    old_mode = cfg["orchestrator"].get("budget_mode", "")
    cfg["orchestrator"]["budget_mode"] = mode_name

    with open(config_path, "w") as f:
        yaml.safe_dump(cfg, f, default_flow_style=False)

    print(f"Budget mode: {old_mode or '(none)'} → {mode_name}")
    return 0


def list_modes() -> int:
    """List all defined budget modes."""
    if not BUDGET_MODES:
        print(f"\n{DIM}No budget modes defined yet (TBD — waiting for PO input){NC}\n")
        return 0

    print(f"\n{BOLD}Budget Modes{NC}\n")
    for name in MODE_ORDER:
        mode = BUDGET_MODES[name]
        print(f"  {name:<15} tempo={mode.tempo_multiplier}  {DIM}{mode.description}{NC}")
    print()
    return 0


def show_report(fleet_dir: str = "") -> int:
    """Show budget usage report from dispatch records."""
    import json
    from collections import Counter

    records_dir = os.path.join(fleet_dir or ".", "state", "dispatch_records")
    if not os.path.isdir(records_dir):
        print(f"{DIM}No dispatch records found.{NC}")
        return 0

    records = []
    for f in os.listdir(records_dir):
        if f.endswith(".json"):
            try:
                with open(os.path.join(records_dir, f)) as fh:
                    records.append(json.load(fh))
            except Exception:
                pass

    if not records:
        print(f"{DIM}No dispatch records found.{NC}")
        return 0

    by_model: dict[str, int] = Counter()
    by_agent: dict[str, int] = Counter()
    by_backend: dict[str, int] = Counter()

    for r in records:
        by_model[r.get("model", "unknown")] += 1
        by_agent[r.get("agent_name", "unknown")] += 1
        by_backend[r.get("backend", "unknown")] += 1

    print(f"\n{BOLD}Budget Report{NC} ({len(records)} dispatches)\n")
    print(f"  {BOLD}By Model:{NC}")
    for model, count in by_model.most_common():
        print(f"    {model:<20} {count}")
    print(f"\n  {BOLD}By Backend:{NC}")
    for backend, count in by_backend.most_common():
        print(f"    {backend:<20} {count}")
    print(f"\n  {BOLD}By Agent:{NC}")
    for agent, count in by_agent.most_common():
        print(f"    {agent:<20} {count}")
    print()
    return 0


def main(args: list[str] | None = None) -> int:
    """CLI entry point for fleet budget command."""
    if args is None:
        args = sys.argv[1:]

    fleet_dir = os.environ.get("FLEET_DIR", "")

    if not args:
        return show_current(fleet_dir)

    cmd = args[0]

    if cmd == "set" and len(args) >= 2:
        return set_mode(args[1], fleet_dir)
    elif cmd == "modes":
        return list_modes()
    elif cmd == "report":
        return show_report(fleet_dir)
    elif cmd == "help":
        print(__doc__)
        return 0
    else:
        print(f"{RED}Unknown budget command: {cmd}{NC}")
        print(f"Usage: fleet budget [set <mode>|modes|report|help]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
