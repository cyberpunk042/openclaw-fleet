#!/usr/bin/env bash
set -euo pipefail

# Register skill packs in OCMC marketplace and sync them.
# Called by setup-mc.sh after MC is ready.
#
# Packs are defined in config/skill-packs.yaml.

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/.env" 2>/dev/null || true

MC_URL="${OCF_MISSION_CONTROL_URL:-http://localhost:8000}"
TOKEN="${LOCAL_AUTH_TOKEN:-}"
PACKS_CONFIG="$FLEET_DIR/config/skill-packs.yaml"

if [[ -z "$TOKEN" ]]; then
    echo "ERROR: No LOCAL_AUTH_TOKEN" >&2
    exit 1
fi

if [[ ! -f "$PACKS_CONFIG" ]]; then
    echo "No skill-packs.yaml found, skipping"
    exit 0
fi

echo "=== Registering Skill Packs ==="

# Read packs from config
PACKS=$(python3 -c "
import yaml, json
with open('$PACKS_CONFIG') as f:
    cfg = yaml.safe_load(f)
for pack in cfg.get('packs', []):
    print(json.dumps(pack))
" 2>/dev/null)

if [[ -z "$PACKS" ]]; then
    echo "No packs configured"
    exit 0
fi

# Get existing packs
EXISTING=$(curl -s -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/skills/packs" | python3 -c "
import json, sys
data = json.load(sys.stdin)
items = data.get('items', data) if isinstance(data, dict) else data
for p in items:
    print(p.get('source_url', ''))
" 2>/dev/null)

registered=0
synced=0

while IFS= read -r pack_json; do
    [[ -z "$pack_json" ]] && continue

    NAME=$(echo "$pack_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['name'])")
    URL=$(echo "$pack_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['source_url'])")
    DESC=$(echo "$pack_json" | python3 -c "import json,sys; print(json.load(sys.stdin).get('description',''))")
    BRANCH=$(echo "$pack_json" | python3 -c "import json,sys; print(json.load(sys.stdin).get('branch','main'))")

    # Skip if already registered
    if echo "$EXISTING" | grep -qF "$URL"; then
        echo "  SKIP: $NAME (already registered)"
        # Still sync it
        PACK_ID=$(curl -s -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/skills/packs" | python3 -c "
import json, sys
for p in json.load(sys.stdin).get('items', []):
    if p.get('source_url', '') == '$URL':
        print(p['id'])
        break
" 2>/dev/null)
        if [[ -n "$PACK_ID" ]]; then
            SYNC=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
                "$MC_URL/api/v1/skills/packs/$PACK_ID/sync" -d '{}')
            SYNCED_COUNT=$(echo "$SYNC" | python3 -c "import json,sys; print(json.load(sys.stdin).get('synced',0))" 2>/dev/null)
            echo "  SYNC: $NAME ($SYNCED_COUNT skills)"
            synced=$((synced + 1))
        fi
        continue
    fi

    # Register
    RESULT=$(curl -s -X POST \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        "$MC_URL/api/v1/skills/packs" \
        -d "$(python3 -c "import json; print(json.dumps({'source_url': '$URL', 'name': '$NAME', 'description': '$DESC', 'branch': '$BRANCH'}))")")

    PACK_ID=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
    if [[ -n "$PACK_ID" ]]; then
        echo "  OK: $NAME (id=$PACK_ID)"
        registered=$((registered + 1))

        # Sync to discover skills
        SYNC=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
            "$MC_URL/api/v1/skills/packs/$PACK_ID/sync" -d '{}')
        SYNCED_COUNT=$(echo "$SYNC" | python3 -c "import json,sys; print(json.load(sys.stdin).get('synced',0))" 2>/dev/null)
        echo "  SYNC: $SYNCED_COUNT skills discovered"
        synced=$((synced + 1))
    else
        ERROR=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('detail','unknown error'))" 2>/dev/null)
        echo "  WARN: $NAME — $ERROR"
    fi
done <<< "$PACKS"

echo ""
echo "Registered: $registered, Synced: $synced"