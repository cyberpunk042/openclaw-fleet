#!/usr/bin/env bash
# setup-claude-mem.sh — Deploy claude-mem per-agent with unique ports and data dirs
#
# Each agent gets:
#   - Unique data dir: ~/.claude-mem-{agent-name}/
#   - Unique worker port: 37771-37780
#   - SQLite-only mode (ChromaDB disabled for RAM savings on WSL2)
#   - OpenRouter free tier for compression (zero cost)
#
# Usage:
#   ./scripts/setup-claude-mem.sh              # setup all agents
#   ./scripts/setup-claude-mem.sh architect    # setup one agent
#   ./scripts/setup-claude-mem.sh --status     # check worker status
#
# Prerequisites:
#   - claude-mem plugin installed (via install-plugins.sh)

set -euo pipefail

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="$FLEET_DIR/config/agent-tooling.yaml"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ── Agent → Port mapping (deterministic) ───────────────────────────

# Port assignment: base 37770 + agent index
declare -A AGENT_PORTS=(
    [architect]=37771
    [software-engineer]=37772
    [qa-engineer]=37773
    [devops]=37774
    [devsecops-expert]=37775
    [fleet-ops]=37776
    [project-manager]=37777
    [technical-writer]=37778
    [ux-designer]=37779
    [accountability-generator]=37780
)

# ── Configure claude-mem for one agent ─────────────────────────────

configure_agent() {
    local agent_name="$1"
    local port="${AGENT_PORTS[$agent_name]:-}"

    if [ -z "$port" ]; then
        echo -e "  ${RED}[error]${NC} Unknown agent: $agent_name"
        return 1
    fi

    local data_dir="$HOME/.claude-mem-${agent_name}"
    local settings_file="$data_dir/settings.json"

    echo "  Configuring $agent_name (port $port, data: $data_dir)"

    # Create data directory
    mkdir -p "$data_dir"

    # Write settings.json
    cat > "$settings_file" << SETTINGS
{
  "CLAUDE_MEM_DATA_DIR": "${data_dir}",
  "CLAUDE_MEM_WORKER_PORT": "${port}",
  "CLAUDE_MEM_WORKER_HOST": "127.0.0.1",
  "CLAUDE_MEM_CHROMA_ENABLED": false,
  "CLAUDE_MEM_PROVIDER": "openrouter",
  "CLAUDE_MEM_OPENROUTER_MODEL": "xiaomi/mimo-v2-flash:free",
  "CLAUDE_MEM_CONTEXT_OBSERVATIONS": 50,
  "CLAUDE_MEM_CONTEXT_SESSION_COUNT": 10,
  "CLAUDE_MEM_CONTEXT_FULL_COUNT": 5,
  "CLAUDE_MEM_LOG_LEVEL": "INFO",
  "CLAUDE_MEM_MODE": "code"
}
SETTINGS

    echo -e "  ${GREEN}[✓]${NC} $agent_name: settings.json written"

    # Create agent-specific env file for hook scripts
    local env_file="${FLEET_DIR}/agents/${agent_name}/.claude-mem.env"
    if [ -d "${FLEET_DIR}/agents/${agent_name}" ]; then
        cat > "$env_file" << ENVFILE
# claude-mem settings for $agent_name
# Sourced by claude-mem hook scripts
export CLAUDE_MEM_DATA_DIR="${data_dir}"
export CLAUDE_MEM_WORKER_PORT="${port}"
export CLAUDE_MEM_WORKER_HOST="127.0.0.1"
export CLAUDE_MEM_CHROMA_ENABLED=false
export CLAUDE_MEM_PROVIDER="openrouter"
export CLAUDE_MEM_OPENROUTER_MODEL="xiaomi/mimo-v2-flash:free"
ENVFILE
        echo -e "  ${GREEN}[✓]${NC} $agent_name: .claude-mem.env written"
    fi
}

# ── Check worker status ────────────────────────────────────────────

check_status() {
    echo "Claude-mem worker status:"
    echo ""

    for agent_name in "${!AGENT_PORTS[@]}"; do
        local port="${AGENT_PORTS[$agent_name]}"
        local status

        if curl -s -o /dev/null "http://127.0.0.1:${port}/health" 2>/dev/null; then
            status="${GREEN}running${NC}"
        else
            status="${YELLOW}stopped${NC}"
        fi

        printf "  %-25s port %-5s %b\n" "$agent_name" "$port" "$status"
    done | sort
}

# ── Main ───────────────────────────────────────────────────────────

echo "═══════════════════════════════════════════════════════"
echo "  Fleet Claude-Mem Deployment"
echo "  Per-agent memory with unique ports and data dirs"
echo "═══════════════════════════════════════════════════════"
echo ""

case "${1:-}" in
    --status)
        check_status
        ;;
    ""|--all)
        if ! command -v yq &>/dev/null; then
            # Fall back to hardcoded list if yq not available
            for agent_name in "${!AGENT_PORTS[@]}"; do
                configure_agent "$agent_name"
            done
        else
            for agent_name in $(yq -r '.agents | keys | .[]' "$CONFIG" 2>/dev/null); do
                configure_agent "$agent_name"
            done
        fi
        ;;
    *)
        configure_agent "$1"
        ;;
esac

echo ""
echo "Done."
echo ""
echo "Notes:"
echo "  - Workers start automatically when claude-mem hooks fire"
echo "  - ChromaDB DISABLED (SQLite-only mode for WSL2 RAM savings)"
echo "  - Compression via OpenRouter free tier (xiaomi/mimo-v2-flash:free)"
echo "  - Set CLAUDE_MEM_OPENROUTER_API_KEY in .env for each agent"
