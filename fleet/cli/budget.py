"""Fleet budget — view and manage budget modes (M-BM04).

Usage:
    python -m fleet budget                    # Show current mode and quota
    python -m fleet budget set <mode>         # Set global budget mode
    python -m fleet budget report             # Cost breakdown by mode/agent/model
    python -m fleet budget modes              # List all available modes
"""

from __future__ import annotations

import asyncio
import os
import sys
from typing import Optional

from fleet.core.budget_modes import (
    BUDGET_MODES,
    MODE_ORDER,
    BudgetMode,
    evaluate_auto_transition,
    get_active_mode_name,
    get_mode,
)

BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
DIM = "\033[2m"
NC = "\033[0m"


# Mode emoji/color indicators
_MODE_STYLE: dict[str, tuple[str, str]] = {
    "blitz": ("\U0001f525", RED),       # fire
    "standard": ("\U0001f7e2", GREEN),  # green circle
    "economic": ("\U0001f535", CYAN),    # blue circle
    "frugal": ("\U0001f7e1", YELLOW),   # yellow circle
    "survival": ("\U0001f7e0", YELLOW), # orange circle
    "blackout": ("\u26ab", RED),        # black circle
}


def _mode_indicator(name: str) -> str:
    emoji, color = _MODE_STYLE.get(name, ("\u2b55", NC))
    return f"{emoji} {color}{name}{NC}"


# ─── Commands ──────────────────────────────────────────────────────


def show_current(fleet_dir: str = "") -> int:
    """Show current budget mode and quota status."""
    active = get_active_mode_name(fleet_dir)
    mode = get_mode(active)

    print(f"\n{BOLD}Budget Mode{NC}")
    print(f"  Active: {_mode_indicator(active)}")

    if mode:
        print(f"  {DIM}{mode.description}{NC}")
        print()
        print(f"  Models:    {', '.join(mode.allowed_models) or 'none (free-only)'}")
        print(f"  Backends:  {', '.join(mode.allowed_backends) or 'none (frozen)'}")
        print(f"  Max effort: {mode.max_effort}")
        print(f"  Dispatch/cycle: {mode.max_dispatch_per_cycle}")
        print(f"  Heartbeat: {mode.heartbeat_interval_min}m")
        print(f"  Opus: {'yes' if mode.allow_opus else 'no'}")
        print(f"  Challenges: {'yes' if mode.allow_challenges else 'no'}")

    # Check for auto-transition recommendation
    # (Would need quota data — show placeholder)
    print(f"\n  {DIM}Use 'fleet budget report' for cost breakdown{NC}")
    print()
    return 0


def set_mode(mode_name: str, fleet_dir: str = "") -> int:
    """Set the global budget mode."""
    if mode_name not in BUDGET_MODES:
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
    old_mode = cfg["orchestrator"].get("budget_mode", "standard")
    cfg["orchestrator"]["budget_mode"] = mode_name

    with open(config_path, "w") as f:
        yaml.safe_dump(cfg, f, default_flow_style=False)

    print(f"Budget mode: {_mode_indicator(old_mode)} \u2192 {_mode_indicator(mode_name)}")
    return 0


def list_modes() -> int:
    """List all available budget modes."""
    print(f"\n{BOLD}Budget Modes{NC}\n")
    print(f"  {'Mode':<12} {'Dispatch':<10} {'Models':<20} {'Effort':<8} {'Description'}")
    print(f"  {'─'*12} {'─'*10} {'─'*20} {'─'*8} {'─'*40}")

    for name in MODE_ORDER:
        mode = BUDGET_MODES[name]
        models = ", ".join(mode.allowed_models) if mode.allowed_models else "free-only"
        emoji, color = _MODE_STYLE.get(name, ("\u2b55", NC))
        print(
            f"  {emoji} {color}{name:<10}{NC} "
            f"{mode.max_dispatch_per_cycle:<10} "
            f"{models:<20} "
            f"{mode.max_effort:<8} "
            f"{DIM}{mode.description}{NC}"
        )

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

    # Aggregate by model, budget mode, agent
    by_model = Counter()
    by_mode = Counter()
    by_agent = Counter()
    by_backend = Counter()

    for r in records:
        by_model[r.get("model", "unknown")] += 1
        by_mode[r.get("budget_mode", "unknown")] += 1
        by_agent[r.get("agent_name", "unknown")] += 1
        by_backend[r.get("backend", "unknown")] += 1

    print(f"\n{BOLD}Budget Report{NC} ({len(records)} dispatches)\n")

    print(f"  {BOLD}By Model:{NC}")
    for model, count in by_model.most_common():
        print(f"    {model:<20} {count}")

    print(f"\n  {BOLD}By Backend:{NC}")
    for backend, count in by_backend.most_common():
        print(f"    {backend:<20} {count}")

    print(f"\n  {BOLD}By Budget Mode:{NC}")
    for mode, count in by_mode.most_common():
        print(f"    {_mode_indicator(mode):<30} {count}")

    print(f"\n  {BOLD}By Agent:{NC}")
    for agent, count in by_agent.most_common():
        print(f"    {agent:<20} {count}")

    print()
    return 0


# ─── Entry Point ───────────────────────────────────────────────────


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