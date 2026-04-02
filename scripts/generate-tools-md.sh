#!/usr/bin/env bash
# generate-tools-md.sh — Generate TOOLS.md per agent from MCP tools + config
#
# Usage: bash scripts/generate-tools-md.sh [agent-name]
#
# Reads: fleet/mcp/tools.py (tool definitions), config/agent-tooling.yaml (per-role tools)
# Produces: agents/{name}/TOOLS.md

set -euo pipefail

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AGENTS_DIR="$FLEET_DIR/agents"
CONFIG="$FLEET_DIR/config/agent-tooling.yaml"
TOOLS_PY="$FLEET_DIR/fleet/mcp/tools.py"
VENV="$FLEET_DIR/.venv"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if ! command -v yq &>/dev/null; then
    echo -e "${YELLOW}[dep]${NC} yq required. Run: bash scripts/setup-agent-tools.sh first"
    exit 1
fi

# Extract tool names and docstrings from tools.py
extract_tools() {
    "$VENV/bin/python" -c "
import ast, sys

with open('$TOOLS_PY') as f:
    tree = ast.parse(f.read())

# Find register_tools function, then find decorated inner functions
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) or isinstance(node, ast.FunctionDef):
        if node.name.startswith('fleet_'):
            doc = ast.get_docstring(node) or ''
            first_line = doc.split(chr(10))[0] if doc else 'No description'
            print(f'{node.name}|{first_line}')
"
}

# Get tool list (cached)
TOOL_LIST=$(extract_tools)

generate_for_agent() {
    local agent_name="$1"
    local agent_dir="$AGENTS_DIR/$agent_name"

    if [[ ! -d "$agent_dir" ]]; then
        return
    fi

    local display_name
    display_name=$(yq -r ".agents.\"$agent_name\".display_name // \"$agent_name\"" \
        "$FLEET_DIR/config/agent-identities.yaml" 2>/dev/null) || display_name="$agent_name"

    # Get role-specific skills
    local skills=""
    local skill_count
    skill_count=$(yq -r ".agents.\"$agent_name\".skills | length" "$CONFIG" 2>/dev/null) || skill_count=0
    local i=0
    while (( i < skill_count )); do
        local skill
        skill=$(yq -r ".agents.\"$agent_name\".skills[$i]" "$CONFIG")
        skills="$skills- /$skill\n"
        i=$((i + 1))
    done

    # Get role-specific MCP servers
    local mcp_servers=""
    local mcp_count
    mcp_count=$(yq -r ".agents.\"$agent_name\".mcp_servers | length" "$CONFIG" 2>/dev/null) || mcp_count=0
    i=0
    while (( i < mcp_count )); do
        local srv_name
        srv_name=$(yq -r ".agents.\"$agent_name\".mcp_servers[$i].name" "$CONFIG")
        mcp_servers="$mcp_servers- $srv_name\n"
        i=$((i + 1))
    done

    # Build TOOLS.md content
    local content="# Tools — $display_name

## Fleet MCP Tools (25)

All agents share access to fleet tools via the fleet MCP server.

| Tool | Purpose |
|------|---------|"

    while IFS='|' read -r tool_name description; do
        content="$content
| \`$tool_name\` | $description |"
    done <<< "$TOOL_LIST"

    content="$content

### Stage-Gated Tools
- \`fleet_task_complete\` — WORK stage only
- \`fleet_commit\` — analysis, investigation, reasoning, work stages

## MCP Servers

- fleet (25 fleet tools)"

    if [[ -n "$mcp_servers" ]]; then
        content="$content
$(echo -e "$mcp_servers")"
    fi

    if [[ -n "$skills" ]]; then
        content="$content

## Skills (slash commands)

$(echo -e "$skills")"
    fi

    content="$content

## Built-In Commands

- \`/plan\` — plan mode for complex tasks
- \`/compact\` — strategic context compaction
- \`/context\` — inspect context breakdown
- \`/debug\` — interactive debugging"

    # Write if changed
    local tools_path="$agent_dir/TOOLS.md"
    if [[ -f "$tools_path" ]]; then
        local existing
        existing=$(cat "$tools_path")
        if [[ "$existing" == "$content" ]]; then
            echo -e "  ${YELLOW}[skip]${NC} $agent_name: TOOLS.md unchanged"
            return
        fi
        echo -e "  ${GREEN}[updated]${NC} $agent_name: TOOLS.md"
    else
        echo -e "  ${GREEN}[created]${NC} $agent_name: TOOLS.md"
    fi

    echo "$content" > "$tools_path"
}

# ─── Main ────────────────────────────────────────────────────────────

echo "═══════════════════════════════════════════════════════"
echo "  Generate TOOLS.md per agent"
echo "═══════════════════════════════════════════════════════"
echo ""

if [[ $# -gt 0 ]]; then
    generate_for_agent "$1"
else
    for agent_name in $(yq -r '.agents | keys | .[]' "$CONFIG"); do
        generate_for_agent "$agent_name"
    done
fi

echo ""
echo "Done."
