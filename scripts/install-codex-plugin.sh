#!/usr/bin/env bash
set -euo pipefail

# Install Codex Plugin for Claude Code (M-BR06)
#
# Installs the openai/codex-plugin-cc plugin so fleet agents can use:
#   /codex:review              — standard code review
#   /codex:adversarial-review  — challenges design decisions
#   /codex:rescue              — delegate tasks to Codex
#
# Prerequisites:
#   - Node.js 18.18+
#   - Claude Code installed
#   - ChatGPT subscription OR OpenAI API key
#
# Usage:
#   bash scripts/install-codex-plugin.sh

FLEET_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_CONFIG_DIR="${FLEET_DIR}/.codex"

echo "=== Codex Plugin Setup ==="

# ─── Pre-flight ────────────────────────────────────────────────

# Check Node.js
if ! command -v node >/dev/null 2>&1; then
    echo "  ERROR: Node.js not found. Install Node.js 18.18+"
    exit 1
fi

NODE_VER=$(node -v | sed 's/v//' | cut -d. -f1)
if [[ "$NODE_VER" -lt 18 ]]; then
    echo "  ERROR: Node.js $NODE_VER found, need 18+."
    exit 1
fi
echo "  Node.js: OK ($(node -v))"

# Check Claude Code
if ! command -v claude >/dev/null 2>&1; then
    echo "  WARN: Claude Code not found. Plugin install will be deferred."
    echo "  Install Claude Code first: npm install -g @anthropic-ai/claude-code"
fi

# ─── Install Codex CLI (if not present) ────────────────────────

if ! command -v codex >/dev/null 2>&1; then
    echo "  Installing Codex CLI..."
    npm install -g @openai/codex 2>/dev/null || {
        echo "  WARN: Codex CLI install failed. Install manually: npm install -g @openai/codex"
    }
else
    echo "  Codex CLI: OK ($(codex --version 2>/dev/null || echo 'installed'))"
fi

# ─── Project-level Codex Config ────────────────────────────────

echo "  Configuring Codex..."
mkdir -p "$CODEX_CONFIG_DIR"

# Project config — adversarial review defaults
if [[ ! -f "${CODEX_CONFIG_DIR}/config.toml" ]]; then
    cat > "${CODEX_CONFIG_DIR}/config.toml" <<'TOML'
# Codex project config for fleet adversarial reviews
# Docs: https://github.com/openai/codex-plugin-cc

model = "o4-mini"
model_reasoning_effort = "high"

# Approval mode: suggest = read-only (safe for reviews)
approval_mode = "suggest"
TOML
    echo "  Created ${CODEX_CONFIG_DIR}/config.toml"
else
    echo "  Codex config exists: ${CODEX_CONFIG_DIR}/config.toml"
fi

# Instructions for adversarial reviews
if [[ ! -f "${CODEX_CONFIG_DIR}/instructions.md" ]]; then
    cat > "${CODEX_CONFIG_DIR}/instructions.md" <<'MD'
# Codex Review Instructions

You are an adversarial reviewer for the OpenClaw Fleet project.

## Review Focus
- Logic errors and edge cases
- Security vulnerabilities (OWASP top 10)
- Missing error handling at system boundaries
- Incorrect assumptions about data or state
- Test coverage gaps
- Compliance with fleet conventions (type hints, conventional commits)

## Fleet Context
- This is a 10-agent autonomous fleet managed by OpenClaw + Mission Control
- Agents produce work artifacts (PRs, comments, reviews) with labor attribution
- Every artifact carries a LaborStamp recording provenance
- Budget modes (blitz/standard/economic/frugal/survival/blackout) control cost
- Confidence tiers (expert/standard/trainee/community) determine review depth

## Output Format
Respond with structured findings:
1. Issue description
2. Severity (low/medium/high/critical)
3. File and line number
4. Recommended fix
MD
    echo "  Created ${CODEX_CONFIG_DIR}/instructions.md"
else
    echo "  Codex instructions exist: ${CODEX_CONFIG_DIR}/instructions.md"
fi

# ─── Plugin Install Note ──────────────────────────────────────

echo ""
echo "  Plugin installation requires Claude Code interactive session."
echo "  Run these commands inside Claude Code to complete setup:"
echo ""
echo "    /plugin marketplace add openai/codex-plugin-cc"
echo "    /plugin install codex@openai-codex"
echo "    /reload-plugins"
echo "    /codex:setup"
echo ""
echo "  If Codex is not authenticated:"
echo "    !codex login"
echo ""
echo "  Verify with: /codex:review (on any open file)"
echo ""
echo "=== Codex Plugin Setup Complete ==="