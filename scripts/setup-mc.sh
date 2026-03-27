#!/usr/bin/env bash
set -euo pipefail

# Start Mission Control and configure it
echo "=== Setting Up Mission Control ==="

FLEET_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$FLEET_DIR"

# Check .env
if [[ ! -f .env ]]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    # Generate auth token
    TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
    sed -i "s/LOCAL_AUTH_TOKEN=.*/LOCAL_AUTH_TOKEN=${TOKEN}/" .env
    echo "Generated LOCAL_AUTH_TOKEN"
fi

# Clone vendor if needed
if [[ ! -d vendor/openclaw-mission-control ]]; then
    echo "Cloning Mission Control..."
    mkdir -p vendor
    git clone https://github.com/abhi1693/openclaw-mission-control.git vendor/openclaw-mission-control
fi

# Start Docker services
echo "Starting Mission Control services..."
docker compose up -d --build 2>&1 | tail -5

# Wait for backend
echo "Waiting for backend..."
for i in $(seq 1 20); do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "Mission Control backend ready"
        break
    fi
    echo "  waiting... ($i/20)"
    sleep 3
done

# Run fleet setup (registers gateway, board, agents in MC)
echo ""
echo "Running fleet setup..."
python3 -m gateway.setup

# Sync templates (push TOOLS.md with auth tokens to agents)
echo ""
echo "Syncing agent templates..."
source .env 2>/dev/null || true
if [[ -n "${LOCAL_AUTH_TOKEN:-}" ]]; then
    # Get gateway ID
    GW_ID=$(curl -s -H "Authorization: Bearer $LOCAL_AUTH_TOKEN" http://localhost:8000/api/v1/gateways \
        | python3 -c "
import json, sys
data = json.load(sys.stdin)
items = data.get('items', data) if isinstance(data, dict) else data
for g in items:
    if 'OpenClaw' in g.get('name', '') or 'OCF' in g.get('name', ''):
        print(g['id'])
        break
" 2>/dev/null)

    if [[ -n "$GW_ID" ]]; then
        RESULT=$(curl -s -X POST \
            -H "Authorization: Bearer $LOCAL_AUTH_TOKEN" \
            -H "Content-Type: application/json" \
            "http://localhost:8000/api/v1/gateways/${GW_ID}/templates/sync?rotate_tokens=true&force_bootstrap=true" \
            -d '{}')
        UPDATED=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agents_updated',0))" 2>/dev/null)
        ERRORS=$(echo "$RESULT" | python3 -c "import json,sys; print(len(json.load(sys.stdin).get('errors',[])))" 2>/dev/null)
        echo "Templates synced: $UPDATED agents updated, $ERRORS errors"
    else
        echo "WARN: Could not find gateway ID for template sync"
    fi
else
    echo "WARN: No LOCAL_AUTH_TOKEN, skipping template sync"
fi

# Push SOUL.md and Claude Code settings to agent workspaces
echo ""
echo "Pushing SOUL.md and workspace settings..."
bash scripts/push-soul.sh

# Register skill packs in marketplace
echo ""
bash scripts/register-skill-packs.sh