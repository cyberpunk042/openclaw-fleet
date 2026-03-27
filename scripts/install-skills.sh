#!/usr/bin/env bash
set -euo pipefail

# Install marketplace skills on the fleet gateway.
#
# Reads: config/skill-assignments.yaml (which skills to install)
# Requires: skill packs already registered and synced (register-skill-packs.sh)
#
# Flow:
#   1. Read skill-assignments.yaml for skills with install: true
#   2. Find each skill in OCMC marketplace by name
#   3. Call POST /marketplace/{skill_id}/install for each
#   4. Report results
#
# Usage:
#   bash scripts/install-skills.sh              # install all marked install: true
#   bash scripts/install-skills.sh --list       # just list what would be installed
#   bash scripts/install-skills.sh --skill pdf  # install a specific skill

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/.env" 2>/dev/null || true

MC_URL="${OCF_MISSION_CONTROL_URL:-http://localhost:8000}"
TOKEN="${LOCAL_AUTH_TOKEN:-}"
ASSIGNMENTS="$FLEET_DIR/config/skill-assignments.yaml"

if [[ -z "$TOKEN" ]]; then echo "ERROR: No LOCAL_AUTH_TOKEN" >&2; exit 1; fi
if [[ ! -f "$ASSIGNMENTS" ]]; then echo "ERROR: No skill-assignments.yaml" >&2; exit 1; fi

LIST_ONLY=false
SPECIFIC_SKILL=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --list) LIST_ONLY=true; shift ;;
        --skill) SPECIFIC_SKILL="$2"; shift 2 ;;
        *) shift ;;
    esac
done

python3 << PYEOF
import yaml, json, sys
import urllib.request
import urllib.error

MC_URL = "$MC_URL"
TOKEN = "$TOKEN"
LIST_ONLY = $([[ "$LIST_ONLY" == "true" ]] && echo "True" || echo "False")
SPECIFIC_SKILL = "$SPECIFIC_SKILL"

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
        try:
            return json.loads(e.read().decode())
        except:
            return {"detail": str(e)}

# Load assignments
with open("$ASSIGNMENTS") as f:
    cfg = yaml.safe_load(f)

skills_cfg = cfg.get("skills", [])

# Filter to installable skills
to_install = []
for s in skills_cfg:
    if SPECIFIC_SKILL and s["name"] != SPECIFIC_SKILL:
        continue
    if not SPECIFIC_SKILL and not s.get("install", False):
        continue
    to_install.append(s)

if not to_install:
    print("No skills to install")
    sys.exit(0)

# Get gateway ID
agents_resp = api("GET", "/api/v1/agents")
gw_id = None
for a in (agents_resp.get("items", []) if isinstance(agents_resp, dict) else []):
    if a.get("gateway_id"):
        gw_id = str(a["gateway_id"])
        break

if not gw_id:
    print("ERROR: No gateway found")
    sys.exit(1)

# Get marketplace skills (all)
marketplace = api("GET", f"/api/v1/skills/marketplace?gateway_id={gw_id}&limit=200")
available = {}
items = marketplace if isinstance(marketplace, list) else (marketplace.get("items", []) if isinstance(marketplace, dict) else [])
for s in items:
    name = s.get("name", "")
    available[name] = s

print(f"=== Fleet Skill Installation ===")
print(f"Gateway: {gw_id[:8]}")
print(f"Marketplace: {len(available)} skills available")
print(f"To install: {len(to_install)} skills")
print()

if LIST_ONLY:
    for s in to_install:
        name = s["name"]
        agents = ", ".join(s.get("agents", []))
        cat = s.get("category", "")
        in_marketplace = name in available
        installed = available.get(name, {}).get("installed", False)
        status = "installed" if installed else ("available" if in_marketplace else "NOT FOUND")
        print(f"  {name:25s} [{status:10s}] agents=[{agents}] category={cat}")
    sys.exit(0)

installed_count = 0
skipped_count = 0
failed_count = 0

for s in to_install:
    name = s["name"]
    agents = ", ".join(s.get("agents", []))

    if name not in available:
        print(f"  SKIP: {name} (not in marketplace — register and sync pack first)")
        skipped_count += 1
        continue

    skill_info = available[name]
    skill_id = skill_info["id"]

    if skill_info.get("installed"):
        print(f"  OK: {name} (already installed)")
        skipped_count += 1
        continue

    # Install
    result = api("POST", f"/api/v1/skills/marketplace/{skill_id}/install?gateway_id={gw_id}")
    if result.get("ok") or result.get("installed"):
        print(f"  INSTALLED: {name} → agents=[{agents}]")
        installed_count += 1
    else:
        detail = result.get("detail", "unknown error")
        print(f"  FAIL: {name} — {detail}")
        failed_count += 1

print()
print(f"Installed: {installed_count}, Skipped: {skipped_count}, Failed: {failed_count}")
PYEOF