#!/usr/bin/env bash
set -euo pipefail

# Provision fleet agents through MC template sync.
# This triggers gateway restarts (one per agent) — wait for them to settle.
# Run AFTER setup-mc.sh and BEFORE clean-gateway-config.sh.

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/.env" 2>/dev/null || true

TOKEN="${LOCAL_AUTH_TOKEN:-}"
MC_URL="${OCF_MISSION_CONTROL_URL:-http://localhost:8000}"

if [[ -z "$TOKEN" ]]; then echo "ERROR: No LOCAL_AUTH_TOKEN"; exit 1; fi

# Get gateway ID
GW_ID=$(curl -sf -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/gateways" \
    | python3 -c "
import json, sys
data = json.load(sys.stdin)
items = data.get('items', data) if isinstance(data, dict) else data
for g in items:
    if 'OCF' in g.get('name', '') or 'OpenClaw' in g.get('name', ''):
        print(g['id'])
        break
" 2>/dev/null)

if [[ -z "$GW_ID" ]]; then echo "ERROR: No gateway found"; exit 1; fi

echo "=== Provisioning Fleet Agents ==="
echo "Gateway: $GW_ID"
echo ""

# Step 1: Trigger template sync (this causes gateway restart storm)
echo "1. Template sync (expect gateway restarts — this is normal)..."
RESULT=$(curl -sf -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    "$MC_URL/api/v1/gateways/${GW_ID}/templates/sync?rotate_tokens=true&force_bootstrap=true" \
    -d '{}' 2>&1 || echo '{"error":"sync failed"}')

UPDATED=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agents_updated',0))" 2>/dev/null || echo "?")
ERRORS=$(echo "$RESULT" | python3 -c "import json,sys; print(len(json.load(sys.stdin).get('errors',[])))" 2>/dev/null || echo "?")
echo "   Synced: $UPDATED agents, $ERRORS errors"

# Step 2: Wait for gateway restart storm to settle (one restart per agent)
echo "2. Waiting for gateway restarts to settle (20 seconds)..."
sleep 20

# Step 3: Verify gateway is responding
echo "3. Verifying gateway..."
for i in $(seq 1 10); do
    if curl -sf "http://localhost:${OCF_GATEWAY_PORT:-9400}/" >/dev/null 2>&1; then
        echo "   Gateway is up"
        break
    fi
    sleep 2
done

# Step 4: Check agent status
echo "4. Agent status:"
curl -sf -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/agents" | python3 -c "
import json, sys
data = json.load(sys.stdin)
online = 0
total = 0
for a in data.get('items', []):
    if 'Gateway' in a.get('name', ''): continue
    total += 1
    status = a['status']
    name = a['name']
    if status == 'online':
        online += 1
        print(f'   ✅ {name}')
    else:
        print(f'   ⏳ {name} ({status})')
print(f'\n   {online}/{total} agents online')
" 2>/dev/null

echo ""
echo "Done. Agents in 'provisioning' will go online on their next heartbeat."
echo "fleet-ops heartbeat: ~30 min, other agents: 55-90 min"