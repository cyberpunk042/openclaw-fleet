#!/usr/bin/env bash
set -euo pipefail

# Apply fleet patches to vendor dependencies.
# Run after cloning vendor repos (called by setup-mc.sh).
#
# Patches are stored in patches/ as git diff files.
# Each patch targets a specific vendor directory.

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PATCHES_DIR="$FLEET_DIR/patches"

if [[ ! -d "$PATCHES_DIR" ]]; then
    echo "No patches directory, skipping"
    exit 0
fi

echo "=== Applying Vendor Patches ==="

applied=0
skipped=0
failed=0

for patch in "$PATCHES_DIR"/*.patch; do
    [[ -f "$patch" ]] || continue
    name=$(basename "$patch")

    # Read target from first line comment or default to OCMC
    target="$FLEET_DIR/vendor/openclaw-mission-control"

    # Check if already applied (git apply --check with --reverse)
    if cd "$target" && git apply --check --reverse "$patch" 2>/dev/null; then
        echo "  SKIP: $name (already applied)"
        skipped=$((skipped + 1))
        continue
    fi

    # Apply
    if cd "$target" && git apply --check "$patch" 2>/dev/null; then
        git apply "$patch"
        echo "  OK: $name"
        applied=$((applied + 1))
    else
        echo "  FAIL: $name (patch doesn't apply cleanly)"
        failed=$((failed + 1))
    fi
done

echo ""
echo "Applied: $applied, Skipped: $skipped, Failed: $failed"