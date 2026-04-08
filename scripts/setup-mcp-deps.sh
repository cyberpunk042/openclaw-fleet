#!/usr/bin/env bash
# setup-mcp-deps.sh — Install pip/system dependencies for MCP servers
#
# Some MCP servers are pip packages (not npx). This script installs them
# into the fleet venv so they're available for agent sessions.
#
# Usage:
#   ./scripts/setup-mcp-deps.sh
#
# Idempotent — skips already-installed packages.

set -euo pipefail

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV="${FLEET_DIR}/.venv"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "═══════════════════════════════════════════════════════"
echo "  Fleet MCP Dependencies"
echo "═══════════════════════════════════════════════════════"
echo ""

# Activate venv
if [ -d "$VENV" ]; then
    source "$VENV/bin/activate"
    echo -e "  ${GREEN}[✓]${NC} venv activated"
else
    echo -e "  ${RED}[✗]${NC} venv not found at $VENV"
    exit 1
fi

# ── Pip-based MCP servers ──────────────────────────────────────────

pip_install_if_missing() {
    local pkg="$1"
    local desc="$2"

    if uv pip show "$pkg" &>/dev/null 2>&1; then
        echo -e "  ${YELLOW}[skip]${NC} $pkg ($desc) — already installed"
    else
        echo -e "  ${GREEN}[install]${NC} $pkg ($desc)"
        uv pip install "$pkg" 2>&1 | tail -1
    fi
}

echo ""
echo "MCP server pip packages:"

# daniel-lightrag-mcp is not on PyPI — install from GitHub
if uv pip show daniel-lightrag-mcp &>/dev/null 2>&1; then
    echo -e "  ${YELLOW}[skip]${NC} daniel-lightrag-mcp (LightRAG MCP) — already installed"
else
    echo -e "  ${GREEN}[install]${NC} daniel-lightrag-mcp (LightRAG MCP — from GitHub)"
    uv pip install --no-deps "git+https://github.com/desimpkins/daniel-lightrag-mcp.git" 2>&1 | tail -1
fi

# pytest-mcp: only the mcp_eval test framework (NOT an MCP server).
# Already in pyproject.toml dev deps. Disabled in pytest via addopts.
# No working pytest MCP server package exists on PyPI.

pip_install_if_missing "anthropic"    "Anthropic SDK — required by daniel-lightrag-mcp transitive dep"
pip_install_if_missing "openai"       "OpenAI SDK — required by daniel-lightrag-mcp transitive dep"

# ── Semgrep (DevSecOps MCP server) ────────────────────────────────
# semgrep provides `semgrep --mcp` for security scanning.
# Install into venv so devsecops agent can use it.

echo ""
echo "Security tools:"

pip_install_if_missing "semgrep"      "security scanning — devsecops MCP server (semgrep --mcp)"

# ── System packages (check only, don't install) ───────────────────

echo ""
echo "System tools:"

check_system() {
    local cmd="$1"
    local desc="$2"
    if command -v "$cmd" &>/dev/null; then
        echo -e "  ${GREEN}[✓]${NC} $cmd ($desc)"
    else
        echo -e "  ${YELLOW}[missing]${NC} $cmd ($desc) — install separately"
    fi
}

check_system "npx"      "npx for MCP servers (Node.js)"
check_system "node"     "Node.js runtime"

echo ""
echo "Done."
