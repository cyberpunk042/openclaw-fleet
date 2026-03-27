#!/usr/bin/env bash
set -euo pipefail

# Clone a project and prepare it for fleet work.
#
# Usage: bash scripts/setup-project.sh <project-name>
#
# Reads config/projects.yaml for the repo URL.
# Clones to projects/<name>/ if not already present.

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_NAME="${1:?Usage: setup-project.sh <project-name>}"
PROJECTS_DIR="$FLEET_DIR/projects"
PROJECTS_YAML="$FLEET_DIR/config/projects.yaml"

# Read project config
PROJECT_INFO=$(python3 -c "
import yaml, sys
with open('$PROJECTS_YAML') as f:
    cfg = yaml.safe_load(f)
projects = cfg.get('projects', {})
p = projects.get('$PROJECT_NAME')
if not p:
    print('NOT_FOUND')
    sys.exit(0)
import json
print(json.dumps(p))
" 2>/dev/null)

if [[ "$PROJECT_INFO" == "NOT_FOUND" || -z "$PROJECT_INFO" ]]; then
    echo "ERROR: Project '$PROJECT_NAME' not found in config/projects.yaml" >&2
    echo ""
    echo "Available projects:"
    python3 -c "
import yaml
with open('$PROJECTS_YAML') as f:
    cfg = yaml.safe_load(f)
for name, info in cfg.get('projects', {}).items():
    print(f'  {name:20s} {info.get(\"description\",\"\")}')
" 2>/dev/null
    exit 1
fi

IS_LOCAL=$(echo "$PROJECT_INFO" | python3 -c "import json,sys; print(json.load(sys.stdin).get('local', False))")
REPO_URL=$(echo "$PROJECT_INFO" | python3 -c "import json,sys; print(json.load(sys.stdin).get('repo', ''))")
DESC=$(echo "$PROJECT_INFO" | python3 -c "import json,sys; print(json.load(sys.stdin).get('description', ''))")

echo "Project: $PROJECT_NAME"
echo "Description: $DESC"

if [[ "$IS_LOCAL" == "True" ]]; then
    echo "Local project (no clone needed)"
    if [[ "$PROJECT_NAME" == "openclaw-fleet" ]]; then
        echo "Path: $FLEET_DIR"
    else
        echo "Path: configured in project definition"
    fi
    exit 0
fi

if [[ -z "$REPO_URL" ]]; then
    echo "ERROR: No repo URL configured for '$PROJECT_NAME'" >&2
    exit 1
fi

PROJECT_PATH="$PROJECTS_DIR/$PROJECT_NAME"

if [[ -d "$PROJECT_PATH/.git" ]]; then
    echo "Already cloned: $PROJECT_PATH"
    echo "Fetching latest..."
    cd "$PROJECT_PATH" && git fetch --all --prune
    echo "Done"
    exit 0
fi

echo "Cloning: $REPO_URL"
mkdir -p "$PROJECTS_DIR"
git clone "$REPO_URL" "$PROJECT_PATH"
echo "Cloned to: $PROJECT_PATH"