#!/usr/bin/env bash
set -euo pipefail

# Check for running fleet processes — detect stale/rogue processes.
# Run before starting the fleet to ensure clean state.

echo "=== Fleet Process Check ==="
echo ""

found=0

# Check gateway
GW=$(pgrep -a -f "openclaw-gateway" 2>/dev/null || true)
if [[ -n "$GW" ]]; then
  echo "⚠️  GATEWAY RUNNING:"
  echo "$GW" | while read line; do echo "   $line"; done
  found=$((found + 1))
fi

# Check openclaw main
OC=$(pgrep -a -f "openclaw$" 2>/dev/null | grep -v grep || true)
if [[ -n "$OC" ]]; then
  echo "⚠️  OPENCLAW MAIN:"
  echo "$OC" | while read line; do echo "   $line"; done
  found=$((found + 1))
fi

# Check fleet daemons
FD=$(pgrep -a -f "fleet daemon" 2>/dev/null || true)
if [[ -n "$FD" ]]; then
  echo "⚠️  FLEET DAEMONS:"
  echo "$FD" | while read line; do echo "   $line"; done
  found=$((found + 1))
fi

# Check MCP servers
MCP=$(pgrep -a -f "fleet.mcp.server" 2>/dev/null || true)
if [[ -n "$MCP" ]]; then
  echo "⚠️  MCP SERVERS:"
  echo "$MCP" | while read line; do echo "   $line"; done
  found=$((found + 1))
fi

# Check Python gateway
PGW=$(pgrep -a -f "python.*gateway" 2>/dev/null || true)
if [[ -n "$PGW" ]]; then
  echo "⚠️  PYTHON GATEWAY:"
  echo "$PGW" | while read line; do echo "   $line"; done
  found=$((found + 1))
fi

echo ""
if [[ $found -eq 0 ]]; then
  echo "✅ No fleet processes running. Clean state."
else
  echo "❌ $found fleet process group(s) detected."
  echo ""
  echo "To kill all: pkill -f openclaw; pkill -f 'fleet daemon'; pkill -f 'fleet.mcp'"
  echo "Then verify: bash scripts/check-fleet-processes.sh"
fi