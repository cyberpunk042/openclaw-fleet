#!/usr/bin/env bash
# generate-agents-md.sh — Generate AGENTS.md per agent from synergy matrix + identities
#
# Usage: bash scripts/generate-agents-md.sh [agent-name]
#
# Reads: config/agent-identities.yaml (names, roles)
# Produces: agents/{name}/AGENTS.md (knowledge of colleagues)

set -euo pipefail

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AGENTS_DIR="$FLEET_DIR/agents"
IDENTITIES="$FLEET_DIR/config/agent-identities.yaml"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if ! command -v yq &>/dev/null; then
    echo -e "${YELLOW}[dep]${NC} yq required. Run: bash scripts/setup-agent-tools.sh first"
    exit 1
fi

# Synergy matrix: who contributes what to whom (from fleet-elevation/15)
# Format: target_role|contributor_role|contribution_type
SYNERGY_MATRIX=(
    "software-engineer|architect|design_input"
    "software-engineer|devsecops-expert|security_requirement"
    "software-engineer|qa-engineer|qa_test_definition"
    "architect|software-engineer|feasibility_assessment"
    "architect|devsecops-expert|security_review"
    "devops|architect|infrastructure_design"
    "devops|devsecops-expert|security_requirement"
    "devops|software-engineer|application_requirements"
    "qa-engineer|software-engineer|implementation_context"
    "qa-engineer|architect|design_context"
    "technical-writer|software-engineer|technical_accuracy"
    "technical-writer|architect|architecture_context"
    "devsecops-expert|architect|architecture_context"
    "devsecops-expert|software-engineer|implementation_context"
)

generate_for_agent() {
    local agent_name="$1"
    local agent_dir="$AGENTS_DIR/$agent_name"

    if [[ ! -d "$agent_dir" ]]; then
        return
    fi

    local display_name
    display_name=$(yq -r ".agents.\"$agent_name\".display_name // \"$agent_name\"" "$IDENTITIES")

    local content="# Colleagues — $display_name

## Your Fleet

You work alongside 9 other agents in the fleet. Each is a top-tier expert.

| Agent | Role | How You Interact |
|-------|------|-----------------|"

    # List all colleagues
    for colleague in $(yq -r '.agents | keys | .[]' "$IDENTITIES"); do
        [[ "$colleague" == "$agent_name" ]] && continue
        local col_display
        col_display=$(yq -r ".agents.\"$colleague\".display_name // \"$colleague\"" "$IDENTITIES")

        # Find synergy relationships
        local interaction="Fleet colleague"

        for entry in "${SYNERGY_MATRIX[@]}"; do
            local target contrib_role contrib_type
            target="${entry%%|*}"
            local rest="${entry#*|}"
            contrib_role="${rest%%|*}"
            contrib_type="${rest#*|}"

            if [[ "$target" == "$agent_name" && "$contrib_role" == "$colleague" ]]; then
                interaction="Contributes $contrib_type to your tasks"
            elif [[ "$target" == "$colleague" && "$contrib_role" == "$agent_name" ]]; then
                interaction="You contribute to their tasks"
            fi
        done

        content="$content
| $col_display | $colleague | $interaction |"
    done

    # Add contribution sections
    local receives=""
    local provides=""

    for entry in "${SYNERGY_MATRIX[@]}"; do
        local target contrib_role contrib_type
        target="${entry%%|*}"
        local rest="${entry#*|}"
        contrib_role="${rest%%|*}"
        contrib_type="${rest#*|}"

        if [[ "$target" == "$agent_name" ]]; then
            local col_display
            col_display=$(yq -r ".agents.\"$contrib_role\".display_name // \"$contrib_role\"" "$IDENTITIES")
            receives="$receives
- **$contrib_type** from $col_display ($contrib_role)"
        elif [[ "$contrib_role" == "$agent_name" ]]; then
            local tgt_display
            tgt_display=$(yq -r ".agents.\"$target\".display_name // \"$target\"" "$IDENTITIES")
            provides="$provides
- **$contrib_type** to $tgt_display ($target)"
        fi
    done

    if [[ -n "$receives" ]]; then
        content="$content

## Contributions You Receive
$receives"
    fi

    if [[ -n "$provides" ]]; then
        content="$content

## Contributions You Provide
$provides"
    fi

    content="$content

## Communication

Use \`fleet_chat\` with @mentions to communicate with colleagues.
Contributions arrive in your context under **INPUTS FROM COLLEAGUES**."

    # Write if changed
    local agents_path="$agent_dir/AGENTS.md"
    if [[ -f "$agents_path" ]]; then
        local existing
        existing=$(cat "$agents_path")
        if [[ "$existing" == "$content" ]]; then
            echo -e "  ${YELLOW}[skip]${NC} $agent_name: AGENTS.md unchanged"
            return
        fi
        echo -e "  ${GREEN}[updated]${NC} $agent_name: AGENTS.md"
    else
        echo -e "  ${GREEN}[created]${NC} $agent_name: AGENTS.md"
    fi

    echo "$content" > "$agents_path"
}

# ─── Main ────────────────────────────────────────────────────────────

echo "═══════════════════════════════════════════════════════"
echo "  Generate AGENTS.md per agent (synergy matrix)"
echo "═══════════════════════════════════════════════════════"
echo ""

if [[ $# -gt 0 ]]; then
    generate_for_agent "$1"
else
    for agent_name in $(yq -r '.agents | keys | .[]' "$IDENTITIES"); do
        generate_for_agent "$agent_name"
    done
fi

echo ""
echo "Done."
