#!/usr/bin/env bash
# vendor.sh — Resolve which gateway vendor is installed (openarms preferred over openclaw).
# Source this file from any fleet script: source "$FLEET_DIR/scripts/lib/vendor.sh"
#
# After sourcing, these variables are set:
#   VENDOR_CLI          — "openarms" or "openclaw"
#   VENDOR_NAME         — "OpenArms" or "OpenClaw"
#   VENDOR_CONFIG_DIR   — ~/.openarms or ~/.openclaw
#   VENDOR_CONFIG_FILE  — ~/.openarms/openarms.json or ~/.openclaw/openclaw.json
#   VENDOR_ENV_FILE     — ~/.openarms/.env or ~/.openclaw/.env

if command -v openarms >/dev/null 2>&1; then
    VENDOR_CLI="openarms"
    VENDOR_NAME="OpenArms"
    VENDOR_CONFIG_DIR="${HOME}/.openarms"
    VENDOR_CONFIG_FILE="${VENDOR_CONFIG_DIR}/openarms.json"
    VENDOR_ENV_FILE="${VENDOR_CONFIG_DIR}/.env"
elif command -v openclaw >/dev/null 2>&1; then
    VENDOR_CLI="openclaw"
    VENDOR_NAME="OpenClaw"
    VENDOR_CONFIG_DIR="${HOME}/.openclaw"
    VENDOR_CONFIG_FILE="${VENDOR_CONFIG_DIR}/openclaw.json"
    VENDOR_ENV_FILE="${VENDOR_CONFIG_DIR}/.env"
else
    echo "ERROR: Neither openarms nor openclaw found in PATH" >&2
    VENDOR_CLI=""
    VENDOR_NAME=""
    VENDOR_CONFIG_DIR=""
    VENDOR_CONFIG_FILE=""
    VENDOR_ENV_FILE=""
fi
