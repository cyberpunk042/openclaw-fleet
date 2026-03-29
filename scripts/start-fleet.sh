#!/usr/bin/env bash
set -euo pipefail

# Start the OpenClaw gateway.
# Kills any existing gateway first (clean restart).
# Must run before Mission Control connects.

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Starting OpenClaw Gateway ==="

# Kill existing gateway processes (avoid duplicates)
if pgrep -f "openclaw-gateway" >/dev/null 2>&1; then
    echo "  Killing existing gateway..."
    pkill -f "openclaw-gateway" 2>/dev/null || true
    sleep 2
fi

# Also kill stale openclaw parent process
if pgrep -f "openclaw$" >/dev/null 2>&1; then
    pkill -f "openclaw$" 2>/dev/null || true
    sleep 1
fi

# Start gateway in background (detached from shell)
# Increase Node.js heap to 4GB — template sync causes rapid config patches
# that exhaust the default ~1.7GB heap during SIGUSR1 restart storms.
export NODE_OPTIONS="--max-old-space-size=4096"
nohup openclaw gateway run --port 18789 > "$FLEET_DIR/.gateway.log" 2>&1 &
disown
GATEWAY_PID=$!

# Wait for it to be ready
echo "  Waiting for gateway..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:18789/ >/dev/null 2>&1; then
        echo "  Gateway ready (PID: $GATEWAY_PID)"
        exit 0
    fi
    sleep 2
done

echo "  ERROR: Gateway failed to start within 60 seconds."
echo "  Check logs: tail -50 $FLEET_DIR/.gateway.log"
exit 1