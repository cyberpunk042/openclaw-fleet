#!/usr/bin/env bash
set -euo pipefail

# Push enhanced SOUL.md and .claude/settings.json to all MC-provisioned agent workspaces.
# Combines agent role (from agents/<name>/SOUL.md) with MC workflow instructions.
# Also ensures Claude Code permissions are set for each workspace.

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AGENTS_DIR="$FLEET_DIR/agents"
WORKFLOW="$AGENTS_DIR/_template/MC_WORKFLOW.md"
TEMPLATE_SETTINGS="$AGENTS_DIR/_template/.claude/settings.json"

if [[ ! -f "$WORKFLOW" ]]; then
    echo "ERROR: $WORKFLOW not found"
    exit 1
fi

updated=0
skipped=0

for workspace in "$FLEET_DIR"/workspace-mc-*; do
    [[ -d "$workspace" ]] || continue

    # Extract agent name from TOOLS.md
    agent_name=$(grep 'AGENT_NAME=' "$workspace/TOOLS.md" 2>/dev/null | sed 's/.*`AGENT_NAME=//' | sed 's/`//' | tr -d '[:space:]')
    if [[ -z "$agent_name" ]]; then
        echo "SKIP: $workspace (no AGENT_NAME in TOOLS.md)"
        skipped=$((skipped + 1))
        continue
    fi

    # Find the agent's role SOUL.md
    role_soul="$AGENTS_DIR/$agent_name/SOUL.md"
    if [[ ! -f "$role_soul" ]]; then
        echo "SKIP: $agent_name (no role SOUL.md at $role_soul)"
        skipped=$((skipped + 1))
        continue
    fi

    # Combine: role + workflow
    {
        cat "$role_soul"
        echo ""
        cat "$WORKFLOW"
    } > "$workspace/SOUL.md"

    # Ensure Claude Code permissions
    mkdir -p "$workspace/.claude"
    if [[ -f "$TEMPLATE_SETTINGS" ]]; then
        cp "$TEMPLATE_SETTINGS" "$workspace/.claude/settings.json"
    fi

    echo "OK: $agent_name"
    updated=$((updated + 1))
done

echo ""
echo "Updated: $updated, Skipped: $skipped"