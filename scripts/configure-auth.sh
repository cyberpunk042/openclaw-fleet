#!/usr/bin/env bash
set -euo pipefail

# Configure Anthropic auth for OpenClaw
# Automatically bridges Claude Code subscription — no manual steps
echo "=== Configuring Auth ==="

OPENCLAW_ENV="${HOME}/.openclaw/.env"

# Always check for fresh Claude Code token (tokens rotate)
# Even if auth looks configured, the token may have expired

# Extract token from Claude Code credentials
CLAUDE_CREDS="${HOME}/.claude/.credentials.json"
if [[ -f "$CLAUDE_CREDS" ]]; then
    TOKEN=$(python3 -c "
import json, sys
with open('$CLAUDE_CREDS') as f:
    creds = json.load(f)
token = creds.get('claudeAiOauth', {}).get('accessToken', '')
if token:
    print(token)
else:
    sys.exit(1)
" 2>/dev/null) || TOKEN=""

    if [[ -n "$TOKEN" ]]; then
        echo "Found Claude Code OAuth token"

        # Write to OpenClaw env (simplest, works for all agents)
        mkdir -p "${HOME}/.openclaw"
        # Remove old entry if exists
        if [[ -f "$OPENCLAW_ENV" ]]; then
            grep -v "ANTHROPIC_API_KEY" "$OPENCLAW_ENV" > "${OPENCLAW_ENV}.tmp" || true
            mv "${OPENCLAW_ENV}.tmp" "$OPENCLAW_ENV"
        fi
        echo "ANTHROPIC_API_KEY=${TOKEN}" >> "$OPENCLAW_ENV"
        echo "Token written to ~/.openclaw/.env"
        echo "Auth configured for all agents via environment"
        exit 0
    fi
fi

# Fallback: check existing env var
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    echo "ANTHROPIC_API_KEY found in environment"
    mkdir -p "${HOME}/.openclaw"
    if ! grep -q "ANTHROPIC_API_KEY" "$OPENCLAW_ENV" 2>/dev/null; then
        echo "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}" >> "$OPENCLAW_ENV"
        echo "Written to ~/.openclaw/.env"
    fi
    exit 0
fi

echo ""
echo "ERROR: No auth source found."
echo "  - No Claude Code credentials at ~/.claude/.credentials.json"
echo "  - No ANTHROPIC_API_KEY in environment"
echo ""
echo "Fix: run 'claude auth login' first, then re-run setup."
exit 1