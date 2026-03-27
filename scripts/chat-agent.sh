#!/usr/bin/env bash
set -euo pipefail

# Chat with an agent via Mission Control board memory.
#
# Usage:
#   bash scripts/chat-agent.sh <message>              # broadcast to board
#   bash scripts/chat-agent.sh @architect <message>    # direct to agent
#
# Messages are posted to board memory with tags=["chat"].
# Agents with active sessions will see the message.

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/.env" 2>/dev/null || true

MC_URL="${OCF_MISSION_CONTROL_URL:-http://localhost:8000}"
TOKEN="${LOCAL_AUTH_TOKEN:-}"

if [[ -z "$TOKEN" ]]; then
    echo "ERROR: No LOCAL_AUTH_TOKEN in .env" >&2
    exit 1
fi

if [[ $# -lt 1 ]]; then
    echo "Usage: bash scripts/chat-agent.sh [@agent-name] <message>"
    echo ""
    echo "Examples:"
    echo "  bash scripts/chat-agent.sh 'What is the fleet status?'"
    echo "  bash scripts/chat-agent.sh @architect 'Review the gateway config'"
    exit 1
fi

# Resolve board ID
BOARD_ID=$(curl -s -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/agents" | python3 -c "
import json, sys
for a in json.load(sys.stdin).get('items', []):
    if a.get('board_id'):
        print(a['board_id'])
        break
" 2>/dev/null)

if [[ -z "$BOARD_ID" ]]; then
    echo "ERROR: No board found" >&2
    exit 1
fi

# Build message
MESSAGE="$*"

# Post to board memory as chat
RESULT=$(curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    "$MC_URL/api/v1/boards/${BOARD_ID}/memory" \
    -d "$(python3 -c "
import json, sys
msg = '''$MESSAGE'''
print(json.dumps({'content': msg, 'tags': ['chat'], 'source': 'human-cli'}))
")")

ENTRY_ID=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)

if [[ -n "$ENTRY_ID" ]]; then
    echo "Posted to board memory (id=$ENTRY_ID)"
    echo "Message: $MESSAGE"
else
    echo "ERROR: Failed to post message"
    echo "$RESULT" | head -3
fi