#!/usr/bin/env bash
set -euo pipefail

# Teardown — stop everything cleanly for a fresh setup.
# Usage: bash scripts/teardown.sh

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Fleet Teardown ==="

echo "1. Stopping fleet daemons..."
pkill -f "fleet daemon" 2>/dev/null && echo "   Killed" || echo "   None running"

echo "2. Stopping MCP servers..."
pkill -f "fleet.mcp.server" 2>/dev/null && echo "   Killed" || echo "   None running"

echo "3. Stopping gateway..."
systemctl --user stop fleet-gateway 2>/dev/null && echo "   Stopped" || echo "   Not running"
systemctl --user disable fleet-gateway 2>/dev/null || true

echo "4. Stopping Docker containers..."
cd "$FLEET_DIR"
docker compose down 2>/dev/null && echo "   Down" || echo "   None running"

echo "5. Stopping IRC..."
pkill -f "miniircd" 2>/dev/null && echo "   Killed" || echo "   None running"

echo "6. Stopping stale LightRAG syncs..."
pkill -f "setup-lightrag" 2>/dev/null && echo "   Killed" || echo "   None running"

echo "7. Killing any remaining openarms/openclaw processes..."
pkill -f "openarms-gateway" 2>/dev/null || true
pkill -f "openclaw-gateway" 2>/dev/null || true
pkill -f "openarms$" 2>/dev/null || true
pkill -f "openclaw$" 2>/dev/null || true

echo ""
echo "=== Teardown Complete ==="
echo "Everything stopped. Run ./setup.sh for a fresh start."
