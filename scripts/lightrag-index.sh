#!/usr/bin/env bash
# lightrag-index.sh — Index fleet content into LightRAG via text insertion
#
# This script handles TEXT INSERTION (LLM-based extraction for prose/code).
# KB entries are handled by kb_sync.py (direct graph API, no LLM needed).
#
# Content sources indexed here:
#   --manuals     Manuals (prose chunks for naive/mix queries)
#   --systems     Full system docs (deep system knowledge)
#   --research    Research docs (decision rationale)
#   --code        Critical source code files (actual relationships)
#   --config      Config YAMLs (agent-tooling, synergy-matrix, etc.)
#   --design      Design docs + fleet-elevation (architecture decisions)
#   --crossrefs   cross-references.yaml (role-system mappings)
#   --agents      Agent template CLAUDE.md files (what agents are told)
#   --all         Everything above
#
# Usage:
#   ./scripts/lightrag-index.sh --manuals        # index manuals only
#   ./scripts/lightrag-index.sh --code            # index source code only
#   ./scripts/lightrag-index.sh --all             # index everything
#   ./scripts/lightrag-index.sh --health          # check LightRAG health
#
# Note: KB entries use scripts/setup-lightrag.sh --sync (kb_sync.py)
#       This script is for ADDITIONAL content that needs text/prose indexing.

set -u

LIGHTRAG_URL="${LIGHTRAG_URL:-http://localhost:9621}"
FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

TOTAL=0
OK=0
FAIL=0

# ── Functions ──────────────────────────────────────────────────────

health_check() {
    echo "Checking LightRAG health..."
    if curl -s -o /dev/null "${LIGHTRAG_URL}/health"; then
        echo -e "  ${GREEN}[ok]${NC} LightRAG healthy at ${LIGHTRAG_URL}"
        return 0
    else
        echo -e "  ${RED}[fail]${NC} LightRAG not reachable"
        return 1
    fi
}

insert_text() {
    local file_path="$1"
    local file_name
    file_name=$(basename "$file_path")

    local content
    content=$(cat "$file_path")

    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "${LIGHTRAG_URL}/documents/text" \
        -H "Content-Type: application/json" \
        -d "$(python3 -c "import json,sys; print(json.dumps({'text': sys.stdin.read(), 'description': '$file_name'}))" <<< "$content")" \
        ) || true

    TOTAL=$((TOTAL + 1))
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        OK=$((OK + 1))
        echo -e "  ${GREEN}✓${NC} ${file_name}"
    else
        FAIL=$((FAIL + 1))
        echo -e "  ${RED}✗${NC} ${file_name} (HTTP ${http_code})"
    fi
}

insert_dir() {
    local dir="$1"
    local pattern="${2:-*.md}"
    local label="$3"

    if [ ! -d "$dir" ]; then
        echo -e "  ${YELLOW}[skip]${NC} $label: directory not found"
        return
    fi

    local count
    count=$(find "$dir" -maxdepth 1 -name "$pattern" | wc -l)
    echo ""
    echo "Indexing $label ($count files):"

    for file in "$dir"/$pattern; do
        [ -f "$file" ] || continue
        insert_text "$file"
    done
}

insert_files() {
    local label="$1"
    shift
    local files=("$@")

    echo ""
    echo "Indexing $label (${#files[@]} files):"

    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            insert_text "$file"
        else
            echo -e "  ${YELLOW}[skip]${NC} $(basename "$file") (not found)"
        fi
    done
}

# ── Content sources ────────────────────────────────────────────────

index_manuals() {
    insert_dir "${FLEET_DIR}/docs/knowledge-map" "*.md" "Manuals"
}

index_systems() {
    insert_dir "${FLEET_DIR}/docs/systems" "*.md" "System docs (full)"
}

index_research() {
    insert_dir "${FLEET_DIR}/docs/milestones/active/research" "*.md" "Research docs"
}

index_crossrefs() {
    echo ""
    echo "Indexing cross-references:"
    insert_text "${FLEET_DIR}/docs/knowledge-map/cross-references.yaml"
}

index_code() {
    insert_files "Critical source code" \
        "${FLEET_DIR}/fleet/cli/orchestrator.py" \
        "${FLEET_DIR}/fleet/cli/dispatch.py" \
        "${FLEET_DIR}/fleet/core/navigator.py" \
        "${FLEET_DIR}/fleet/core/kb_sync.py" \
        "${FLEET_DIR}/fleet/core/preembed.py" \
        "${FLEET_DIR}/fleet/core/context_writer.py" \
        "${FLEET_DIR}/fleet/core/role_providers.py" \
        "${FLEET_DIR}/fleet/core/doctor.py" \
        "${FLEET_DIR}/fleet/core/storm_monitor.py" \
        "${FLEET_DIR}/fleet/core/methodology.py" \
        "${FLEET_DIR}/fleet/core/models.py" \
        "${FLEET_DIR}/fleet/core/contributions.py" \
        "${FLEET_DIR}/fleet/core/trail_recorder.py" \
        "${FLEET_DIR}/fleet/core/heartbeat_gate.py" \
        "${FLEET_DIR}/fleet/core/session_manager.py" \
        "${FLEET_DIR}/fleet/core/backend_router.py" \
        "${FLEET_DIR}/fleet/mcp/tools.py" \
        "${FLEET_DIR}/fleet/mcp/server.py" \
        "${FLEET_DIR}/fleet/mcp/context.py" \
        "${FLEET_DIR}/gateway/executor.py" \
        "${FLEET_DIR}/gateway/ws_server.py" \
        "${FLEET_DIR}/gateway/setup.py"
}

index_config() {
    insert_files "Config files" \
        "${FLEET_DIR}/config/agent-tooling.yaml" \
        "${FLEET_DIR}/config/agent-identities.yaml" \
        "${FLEET_DIR}/config/agent-autonomy.yaml" \
        "${FLEET_DIR}/config/synergy-matrix.yaml" \
        "${FLEET_DIR}/config/phases.yaml" \
        "${FLEET_DIR}/config/fleet.yaml" \
        "${FLEET_DIR}/config/skill-assignments.yaml" \
        "${FLEET_DIR}/config/projects.yaml"
}

index_design() {
    # Key design docs (not all 162 — the essential architecture ones)
    insert_files "Design docs (key)" \
        "${FLEET_DIR}/docs/milestones/active/fleet-vision-architecture.md" \
        "${FLEET_DIR}/docs/milestones/active/complete-roadmap.md" \
        "${FLEET_DIR}/docs/milestones/active/ecosystem-deployment-plan.md" \
        "${FLEET_DIR}/docs/milestones/active/budget-mode-system.md" \
        "${FLEET_DIR}/docs/milestones/active/context-window-awareness-and-control.md" \
        "${FLEET_DIR}/docs/milestones/active/agent-rework.md"

    # Fleet-elevation design docs
    insert_dir "${FLEET_DIR}/docs/fleet-elevation" "*.md" "Fleet-elevation design"
}

index_agents() {
    insert_dir "${FLEET_DIR}/agents/_template/CLAUDE.md" "*.md" "Agent CLAUDE.md templates"
    insert_files "Agent template files" \
        "${FLEET_DIR}/agents/_template/MC_API_REFERENCE.md" \
        "${FLEET_DIR}/agents/_template/MC_WORKFLOW.md" \
        "${FLEET_DIR}/agents/_template/STANDARDS.md"
}

index_all() {
    echo "═══════════════════════════════════════════════════════"
    echo "  LightRAG Content Indexing (text insertion)"
    echo "═══════════════════════════════════════════════════════"

    health_check || exit 1

    index_manuals
    index_systems
    index_research
    index_crossrefs
    index_code
    index_config
    index_design
    index_agents

    echo ""
    echo "═══════════════════════════════════════════════════════"
    echo -e "  Total: ${TOTAL} files, ${GREEN}${OK} ok${NC}, ${RED}${FAIL} fail${NC}"
    echo "═══════════════════════════════════════════════════════"
}

# ── Main ───────────────────────────────────────────────────────────

case "${1:-}" in
    --health)     health_check ;;
    --manuals)    health_check && index_manuals ;;
    --systems)    health_check && index_systems ;;
    --research)   health_check && index_research ;;
    --crossrefs)  health_check && index_crossrefs ;;
    --code)       health_check && index_code ;;
    --config)     health_check && index_config ;;
    --design)     health_check && index_design ;;
    --agents)     health_check && index_agents ;;
    --all)        index_all ;;
    *)
        echo "Usage: $0 [--all|--manuals|--systems|--research|--crossrefs|--code|--config|--design|--agents|--health]"
        echo ""
        echo "KB entries are indexed via: bash scripts/setup-lightrag.sh --sync"
        echo "This script indexes ADDITIONAL content (manuals, code, config, design docs)"
        exit 1
        ;;
esac
