"""Fleet auth management — check and refresh tokens.

Usage:
  python -m fleet auth status    # check token state
  python -m fleet auth refresh   # refresh if rotated
"""

from __future__ import annotations

import sys

from fleet.core.auth import (
    get_current_claude_token,
    get_stored_token,
    refresh_token,
    token_needs_refresh,
)


def run_auth(args: list[str] | None = None) -> int:
    """Entry point for fleet auth."""
    argv = args if args is not None else sys.argv[2:]
    action = argv[0] if argv else "status"

    if action == "status":
        current = get_current_claude_token()
        stored = get_stored_token()
        needs = token_needs_refresh()

        print(f"Claude token: {'present' if current else 'MISSING'}")
        print(f"Stored token: {'present' if stored else 'MISSING'}")
        print(f"Needs refresh: {'YES' if needs else 'no'}")

        if current and stored:
            match = current == stored
            print(f"Tokens match: {'yes' if match else 'NO — refresh needed'}")

    elif action == "refresh":
        if refresh_token():
            print("Token refreshed. Restart gateway: make gateway-restart")
        else:
            print("Token is current (no refresh needed)")

    else:
        print(f"Unknown action: {action}")
        print("Usage: fleet auth <status|refresh>")
        return 1

    return 0