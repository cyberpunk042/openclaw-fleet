#!/usr/bin/env bash
set -euo pipefail

# Register fleet agents in OpenClaw gateway.
# Reads agent-identities.yaml and creates agents via openclaw CLI.
# Idempotent — safe to run multiple times.

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/scripts/lib/vendor.sh"
IDENTITIES="$FLEET_DIR/config/agent-identities.yaml"

echo "=== Registering Fleet Agents ==="

if [[ ! -f "$IDENTITIES" ]]; then
    echo "ERROR: $IDENTITIES not found"
    exit 1
fi

python3 << PYEOF
import yaml, subprocess, os

fleet_dir = "$FLEET_DIR"
with open("$IDENTITIES") as f:
    cfg = yaml.safe_load(f)

agents = cfg.get("agents", {})
registered = 0

# Get existing agents ONCE (not per-agent — vendor CLI is slow to start)
existing_agents = ""
try:
    result = subprocess.run(
        ["$VENDOR_CLI", "agents", "list"],
        capture_output=True, text=True, timeout=15
    )
    existing_agents = result.stdout
except Exception as e:
    print(f"  WARN: Could not list agents — {e}")

for agent_name, info in agents.items():
    display = info.get("display_name", agent_name)
    workspace = os.path.join(fleet_dir, "agents", agent_name)

    if not os.path.isdir(workspace):
        print(f"  SKIP: {agent_name} — no workspace dir")
        continue

    # Check if already registered (using cached list)
    if agent_name in existing_agents:
        print(f"  EXISTS: {agent_name}")
        continue

    # Register
    try:
        subprocess.run(
            ["$VENDOR_CLI", "agents", "add", agent_name,
             "--workspace", workspace],
            capture_output=True, text=True, timeout=60
        )
        print(f"  REGISTERED: {agent_name} ({display})")
        registered += 1
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT: {agent_name} — $VENDOR_CLI CLI hung (60s), skipping")
    except Exception as e:
        print(f"  ERROR: {agent_name} — {e}")

print(f"\n{registered} agents registered")
PYEOF