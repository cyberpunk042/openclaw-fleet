#!/usr/bin/env bash
set -euo pipefail

# Install gateway vendor (OpenArms preferred, OpenClaw fallback).
# OpenArms: built from ../openarms if available.
# OpenClaw: npm install -g openclaw (legacy fallback).

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/scripts/lib/vendor.sh"

echo "=== Installing Gateway Vendor ==="

# Already installed?
if [[ -n "$VENDOR_CLI" ]]; then
    VERSION=$($VENDOR_CLI --version 2>/dev/null | head -1 || echo "unknown")
    echo "  $VENDOR_NAME already installed: $VERSION"
    exit 0
fi

# Try OpenArms first (local build)
OPENARMS_DIR="$FLEET_DIR/../openarms"
if [[ -d "$OPENARMS_DIR/dist" ]]; then
    echo "  Installing openarms from local build..."
    npm install -g "$OPENARMS_DIR" 2>/dev/null || {
        echo "  Trying with sudo..."
        sudo npm install -g "$OPENARMS_DIR" 2>/dev/null || {
            echo "  WARN: Could not install openarms from local build"
        }
    }
    if command -v openarms >/dev/null 2>&1; then
        echo "  OpenArms installed: $(openarms --version 2>/dev/null | head -1)"
        exit 0
    fi
fi

# Fallback: OpenClaw from npm
echo "  Installing openclaw via npm (legacy fallback)..."
npm install -g openclaw 2>/dev/null || {
    echo "  Trying with sudo..."
    sudo npm install -g openclaw 2>/dev/null || {
        echo "  ERROR: Could not install gateway vendor."
        echo "  Build openarms: cd ../openarms && pnpm build"
        echo "  Or install legacy: npm install -g openclaw"
        exit 1
    }
}
echo "  OpenClaw installed: $(openclaw --version 2>/dev/null | head -1)"
