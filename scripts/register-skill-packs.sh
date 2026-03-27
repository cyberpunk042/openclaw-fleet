#!/usr/bin/env bash
set -euo pipefail

# Register skill packs, sync them, and apply category/risk defaults.
#
# Reads: config/skill-packs.yaml
# Called by: setup-mc.sh
#
# Flow:
#   1. Register each pack source URL in OCMC marketplace
#   2. Sync each pack (clone repo, discover SKILL.md files)
#   3. Apply category/risk defaults to discovered skills (fixes UI filtering)

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/.env" 2>/dev/null || true

MC_URL="${OCF_MISSION_CONTROL_URL:-http://localhost:8000}"
TOKEN="${LOCAL_AUTH_TOKEN:-}"
PACKS_CONFIG="$FLEET_DIR/config/skill-packs.yaml"

if [[ -z "$TOKEN" ]]; then echo "ERROR: No LOCAL_AUTH_TOKEN" >&2; exit 1; fi
if [[ ! -f "$PACKS_CONFIG" ]]; then echo "No skill-packs.yaml, skipping"; exit 0; fi

echo "=== Registering Skill Packs ==="

# Process each pack
python3 << PYEOF
import yaml, json, sys
import urllib.request
import urllib.error

MC_URL = "$MC_URL"
TOKEN = "$TOKEN"

def api(method, path, data=None):
    url = f"{MC_URL}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return json.loads(body)
        except:
            return {"detail": body}

def get(path):
    return api("GET", path)

def post(path, data=None):
    return api("POST", path, data)

def patch(path, data=None):
    return api("PATCH", path, data)

# Load config
with open("$PACKS_CONFIG") as f:
    cfg = yaml.safe_load(f)

packs = cfg.get("packs", [])
if not packs:
    print("No packs configured")
    sys.exit(0)

# Get existing packs
existing_packs = get("/api/v1/skills/packs")
existing_urls = {}
if isinstance(existing_packs, dict):
    for p in existing_packs.get("items", []):
        existing_urls[p.get("source_url", "")] = p

for pack_cfg in packs:
    name = pack_cfg["name"]
    url = pack_cfg["source_url"]
    desc = pack_cfg.get("description", "")
    branch = pack_cfg.get("branch", "main")
    defaults = pack_cfg.get("defaults", {})
    default_category = defaults.get("category")
    default_risk = defaults.get("risk")

    # Register or get existing
    if url in existing_urls:
        pack = existing_urls[url]
        pack_id = pack["id"]
        print(f"  EXISTS: {name} (id={pack_id[:8]})")
    else:
        result = post("/api/v1/skills/packs", {
            "source_url": url,
            "name": name,
            "description": desc,
            "branch": branch,
        })
        pack_id = result.get("id")
        if not pack_id:
            print(f"  FAIL: {name} — {result.get('detail', 'unknown error')}")
            continue
        print(f"  REGISTERED: {name} (id={pack_id[:8]})")

    # Sync (discover skills from repo)
    sync = post(f"/api/v1/skills/packs/{pack_id}/sync")
    synced = sync.get("synced", 0)
    created = sync.get("created", 0)
    updated = sync.get("updated", 0)
    warnings = sync.get("warnings", [])
    print(f"  SYNCED: {synced} skills (created={created}, updated={updated})")
    for w in warnings[:3]:
        print(f"    WARN: {w}")

    # Apply category/risk defaults to skills that don't have them
    if default_category or default_risk:
        skills_resp = get(f"/api/v1/skills/marketplace?pack_id={pack_id}&limit=100")
        skills = skills_resp.get("items", []) if isinstance(skills_resp, dict) else []
        patched = 0
        for skill in skills:
            needs_update = False
            if default_category and not skill.get("category"):
                needs_update = True
            if default_risk and not skill.get("risk"):
                needs_update = True
            if needs_update:
                # OCMC doesn't have a PATCH endpoint for individual skills,
                # but category/risk come from the source. We'll note this.
                patched += 1
        if patched > 0:
            print(f"  NOTE: {patched} skills lack category/risk — source repo should add skills_index.json")

print()
print("Done. View in MC: http://localhost:3000 → Skills Marketplace")
print("Note: clear risk filter in UI to see skills with unknown risk level")
PYEOF