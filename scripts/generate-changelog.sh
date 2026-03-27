#!/usr/bin/env bash
set -euo pipefail

# Generate CHANGELOG.md from conventional commit history.
#
# Usage:
#   bash scripts/generate-changelog.sh              # full changelog
#   bash scripts/generate-changelog.sh --since v0.1 # since tag
#   bash scripts/generate-changelog.sh --last 20    # last N commits

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$FLEET_DIR"

SINCE=""
LAST=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --since) SINCE="$2"; shift 2 ;;
        --last) LAST="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Build git log range
LOG_ARGS=(--format="%H|%s|%an|%ai")
if [[ -n "$SINCE" ]]; then
    LOG_ARGS+=("${SINCE}..HEAD")
elif [[ -n "$LAST" ]]; then
    LOG_ARGS+=("-n" "$LAST")
fi

echo "# Changelog"
echo ""
echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# Parse commits into categories
declare -A CATEGORIES
CATEGORIES=(
    [feat]="Features"
    [fix]="Bug Fixes"
    [docs]="Documentation"
    [refactor]="Refactoring"
    [test]="Tests"
    [chore]="Maintenance"
    [ci]="CI/CD"
    [style]="Style"
    [perf]="Performance"
)

# Collect commits by type
declare -A ENTRIES
for type in "${!CATEGORIES[@]}"; do
    ENTRIES[$type]=""
done
ENTRIES[other]=""

while IFS='|' read -r hash subject author date; do
    [[ -z "$hash" ]] && continue

    # Parse conventional commit
    matched=false
    for type in "${!CATEGORIES[@]}"; do
        # Match: type(scope): description
        pattern="^${type}[(]([^)]*)[)]: (.+)$"
        pattern_noscope="^${type}: (.+)$"
        if [[ "$subject" =~ $pattern ]]; then
            scope="${BASH_REMATCH[1]}"
            desc="${BASH_REMATCH[2]}"
            short="${hash:0:7}"
            ENTRIES[$type]+="- **$scope**: $desc (\`$short\`)"$'\n'
            matched=true
            break
        elif [[ "$subject" =~ $pattern_noscope ]]; then
            desc="${BASH_REMATCH[1]}"
            short="${hash:0:7}"
            ENTRIES[$type]+="- $desc (\`$short\`)"$'\n'
            matched=true
            break
        fi
    done

    if [[ "$matched" == "false" ]]; then
        short="${hash:0:7}"
        ENTRIES[other]+="- $subject (\`$short\`)"$'\n'
    fi
done < <(git log "${LOG_ARGS[@]}" 2>/dev/null)

# Output by category
has_content=false
for type in feat fix refactor perf docs test ci chore style; do
    if [[ -n "${ENTRIES[$type]:-}" ]]; then
        echo "## ${CATEGORIES[$type]}"
        echo ""
        echo "${ENTRIES[$type]}"
        has_content=true
    fi
done

if [[ -n "${ENTRIES[other]:-}" ]]; then
    echo "## Other"
    echo ""
    echo "${ENTRIES[other]}"
    has_content=true
fi

if [[ "$has_content" == "false" ]]; then
    echo "No commits found."
fi