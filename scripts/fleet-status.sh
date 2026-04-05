#!/usr/bin/env bash
set -euo pipefail

# Fleet status — comprehensive overview of the running fleet.
# Usage: bash scripts/fleet-status.sh

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/.env" 2>/dev/null || true

MC_URL="${OCF_MISSION_CONTROL_URL:-http://localhost:8000}"
TOKEN="${LOCAL_AUTH_TOKEN:-}"

# Colors
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BOLD}╔══════════════════════════════════════╗${NC}"
echo -e "${BOLD}║     OpenClaw Fleet Status            ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════╝${NC}"

# 1. Infrastructure
echo ""
echo -e "${BOLD}Infrastructure${NC}"
GW_PORT="18789"
if curl -sf "http://localhost:${GW_PORT}" > /dev/null 2>&1; then
    echo -e "  OpenClaw Gateway:  ${GREEN}UP${NC} (ws://localhost:${GW_PORT})"
else
    echo -e "  OpenClaw Gateway:  ${RED}DOWN${NC}"
fi
if curl -sf "$MC_URL/health" > /dev/null 2>&1; then
    echo -e "  MC Backend:        ${GREEN}UP${NC} ($MC_URL)"
else
    echo -e "  MC Backend:        ${RED}DOWN${NC}"
fi
if curl -sf http://localhost:3000 > /dev/null 2>&1; then
    echo -e "  MC Frontend:       ${GREEN}UP${NC} (http://localhost:3000)"
else
    echo -e "  MC Frontend:       ${RED}DOWN${NC}"
fi

if [[ -z "$TOKEN" ]]; then
    echo ""
    echo -e "  ${RED}No LOCAL_AUTH_TOKEN — cannot query MC API${NC}"
    exit 0
fi

# 2. Agents
echo ""
echo -e "${BOLD}Agents${NC}"
curl -s -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/agents" | python3 -c "
import json, sys
agents = json.load(sys.stdin).get('items', [])
for a in agents:
    name = a.get('name', '?')
    if 'Gateway' in name:
        continue
    status = a.get('status', '?')
    color = '\033[0;32m' if status == 'online' else '\033[0;31m' if status == 'offline' else '\033[0;33m'
    reset = '\033[0m'
    lead = ' (lead)' if a.get('is_board_lead') else ''
    print(f'  {name:25s} {color}{status:15s}{reset}{lead}')
print(f'  Total: {len([a for a in agents if \"Gateway\" not in a.get(\"name\",\"\")])} agents')
" 2>/dev/null

# 3. Tasks
echo ""
echo -e "${BOLD}Tasks${NC}"
curl -s -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/agents" | python3 -c "
import json, sys, urllib.request

agents = json.load(sys.stdin).get('items', [])
board_ids = set()
for a in agents:
    bid = a.get('board_id')
    if bid:
        board_ids.add(str(bid))
" 2>/dev/null

# Get board ID from first agent
BOARD_ID=$(curl -s -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/agents" | python3 -c "
import json, sys
for a in json.load(sys.stdin).get('items', []):
    if a.get('board_id'):
        print(a['board_id'])
        break
" 2>/dev/null)

if [[ -n "$BOARD_ID" ]]; then
    curl -s -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/boards/${BOARD_ID}/tasks" | python3 -c "
import json, sys
tasks = json.load(sys.stdin).get('items', [])
counts = {}
for t in tasks:
    s = t.get('status', '?')
    counts[s] = counts.get(s, 0) + 1
    assigned = t.get('assigned_agent_id', '')
    status_color = {
        'inbox': '\033[0;33m',
        'in_progress': '\033[0;36m',
        'review': '\033[0;35m',
        'done': '\033[0;32m',
    }.get(s, '\033[0m')
    reset = '\033[0m'
    print(f'  {status_color}{s:15s}{reset} {t[\"title\"][:55]}')
print()
summary = ', '.join(f'{v} {k}' for k, v in sorted(counts.items()))
print(f'  Summary: {summary} ({len(tasks)} total)')
" 2>/dev/null
fi

# 4. Recent Activity
echo ""
echo -e "${BOLD}Recent Activity${NC}"
curl -s -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/activity?limit=5" | python3 -c "
import json, sys
for e in json.load(sys.stdin).get('items', []):
    ts = e.get('created_at', '')[:19].replace('T', ' ')
    evt = e.get('event_type', '')
    msg = str(e.get('message', ''))[:80]
    print(f'  {ts}  {evt:25s} {msg}')
" 2>/dev/null