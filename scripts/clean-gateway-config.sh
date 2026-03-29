#!/usr/bin/env bash
set -euo pipefail

# Clean gateway config — remove duplicate agents, set safe heartbeat intervals.
# The gateway config at ~/.openclaw/openclaw.json has 22 agents (duplicates).
# Only the MC-provisioned versions (id: mc-*) should remain.
# Non-MC versions (id: agent-name) are leftover from initial registration.

OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"

if [[ ! -f "$OPENCLAW_CONFIG" ]]; then
  echo "ERROR: $OPENCLAW_CONFIG not found"
  exit 1
fi

echo "=== Cleaning Gateway Configuration ==="
echo ""

python3 << 'PYEOF'
import json, sys

config_path = sys.argv[1] if len(sys.argv) > 1 else "$HOME/.openclaw/openclaw.json"

with open("$HOME/.openclaw/openclaw.json") as f:
    cfg = json.load(f)

agents = cfg.get("agents", {}).get("list", [])
print(f"Before: {len(agents)} agents")

# Keep only MC-provisioned agents (id starts with mc-) and the gateway agent
cleaned = []
removed = []
for a in agents:
    agent_id = a.get("id", "")
    name = a.get("name", "")
    # Keep: gateway agent, mc-provisioned agents, unnamed main agent
    if agent_id.startswith("mc-") or agent_id == "main" or "Gateway" in name:
        cleaned.append(a)
    else:
        removed.append(f"{name} (id: {agent_id})")

print(f"Removed {len(removed)} duplicate agents:")
for r in removed:
    print(f"  - {r}")

# Set reasonable heartbeat intervals on remaining agents
for a in cleaned:
    name = a.get("name", "")
    if "Gateway" in name:
        a["heartbeat"] = {"every": "30m", "target": "last", "includeReasoning": False}
    elif name in ("project-manager", "fleet-ops"):
        # Driver agents: 30 min heartbeat
        a["heartbeat"] = {"every": "30m", "target": "last", "includeReasoning": False}
    elif name in ("devsecops-expert",):
        # Security: 60 min heartbeat
        a["heartbeat"] = {"every": "60m", "target": "last", "includeReasoning": False}
    else:
        # Worker agents: 60 min heartbeat
        a["heartbeat"] = {"every": "60m", "target": "last", "includeReasoning": False}

cfg["agents"]["list"] = cleaned

with open("$HOME/.openclaw/openclaw.json", "w") as f:
    json.dump(cfg, f, indent=2)

print(f"\nAfter: {len(cleaned)} agents")
print("\nHeartbeat intervals set:")
for a in cleaned:
    name = a.get("name", "(unnamed)")
    every = a.get("heartbeat", {}).get("every", "?")
    print(f"  {name:40s} {every}")

print("\nGateway config cleaned.")
PYEOF

echo ""
echo "Done. Gateway config cleaned and heartbeat intervals set."
echo "Restart gateway to apply: make gateway-restart"