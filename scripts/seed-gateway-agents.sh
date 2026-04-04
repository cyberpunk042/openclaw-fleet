#!/usr/bin/env bash
set -euo pipefail

# Pre-seed gateway config with MC agent entries.
#
# Reads agent list from MC API and writes entries into openclaw.json
# so the gateway knows all agents on startup. This avoids the SIGUSR1
# restart storm that happens when MC creates agents one-by-one via
# template sync (each agents.create → config.patch → restart).
#
# Must run AFTER:
#   - MC is up (agents exist in MC database)
#   - gateway.setup has registered agents in MC
# Must run BEFORE:
#   - Gateway starts (so agents exist from first boot)

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/scripts/lib/vendor.sh"

set -a
source "$FLEET_DIR/.env" 2>/dev/null || true
set +a

echo "=== Seeding Gateway with MC Agents ==="

if [[ -z "${LOCAL_AUTH_TOKEN:-}" ]]; then
    echo "  ERROR: LOCAL_AUTH_TOKEN not set"
    exit 1
fi

MC_URL="http://localhost:${BACKEND_PORT:-8000}"

# Fetch agents from MC
MC_AGENTS=$(curl -sf -m 10 -H "Authorization: Bearer $LOCAL_AUTH_TOKEN" \
    "$MC_URL/api/v1/agents" 2>/dev/null || echo "")

if [[ -z "$MC_AGENTS" ]]; then
    echo "  ERROR: Could not fetch agents from MC"
    exit 1
fi

# Read agent identities for heartbeat intervals
IDENTITIES="$FLEET_DIR/config/agent-identities.yaml"

# Inject agent entries into openclaw.json
python3 << PYEOF
import json, os, sys

try:
    import yaml
    with open("$IDENTITIES") as f:
        identities = yaml.safe_load(f) or {}
    identity_map = identities.get("agents", {})
except Exception:
    identity_map = {}

# Default heartbeat intervals per agent (from agent-identities.yaml)
heartbeat_defaults = {
    "fleet-ops": "30m",
    "project-manager": "35m",
    "devsecops-expert": "55m",
    "architect": "60m",
    "software-engineer": "65m",
    "qa-engineer": "70m",
    "devops": "75m",
    "technical-writer": "80m",
    "ux-designer": "85m",
    "accountability-generator": "90m",
}

mc_data = json.loads('''$MC_AGENTS''')
items = mc_data.get("items", mc_data) if isinstance(mc_data, dict) else mc_data

# Read current gateway config
config_path = "$VENDOR_CONFIG_FILE"
with open(config_path) as f:
    cfg = json.load(f)

existing = cfg.setdefault("agents", {}).setdefault("list", [])
existing_ids = {a.get("id", "") for a in existing}

fleet_dir = "$FLEET_DIR"
seeded = 0
skipped = 0

for agent in items:
    name = agent.get("name", "")
    mc_id = agent.get("id", "")
    gw_agent_id = f"mc-{mc_id}"

    # Skip gateway agents
    if "Gateway" in name or "gateway" in agent.get("identity_profile", {}).get("role", ""):
        continue

    # Skip if already in config
    if gw_agent_id in existing_ids:
        skipped += 1
        continue

    # Get heartbeat interval from identities or MC config
    mc_hb = agent.get("heartbeat_config", {})
    hb_every = mc_hb.get("every", heartbeat_defaults.get(name, "60m"))

    entry = {
        "id": gw_agent_id,
        "name": name,
        "workspace": os.path.join(fleet_dir, f"workspace-{gw_agent_id}"),
        "agentDir": os.path.join("$VENDOR_CONFIG_DIR", "agents", gw_agent_id, "agent"),
        "heartbeat": {
            "every": hb_every,
            "target": "last",
            "includeReasoning": False,
        },
    }
    existing.append(entry)
    existing_ids.add(gw_agent_id)

    # Ensure workspace and agent dirs exist
    os.makedirs(entry["workspace"], exist_ok=True)
    os.makedirs(entry["agentDir"], exist_ok=True)

    seeded += 1

# Write updated config
with open(config_path, "w") as f:
    json.dump(cfg, f, indent=2)

# Reset config health checkpoint so gateway accepts the larger file
health_path = os.path.join("$VENDOR_CONFIG_DIR", "logs", "config-health.json")
if os.path.exists(health_path):
    os.remove(health_path)

print(f"  Seeded {seeded} agents, skipped {skipped} (already in config)")
PYEOF
