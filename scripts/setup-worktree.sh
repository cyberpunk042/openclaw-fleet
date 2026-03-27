#!/usr/bin/env bash
set -euo pipefail

# Create a git worktree for an agent to work on a project.
#
# Usage: bash scripts/setup-worktree.sh <project-name> <agent-name> [task-id]
#
# Creates: projects/<project>/worktrees/<agent>-<task-short>/
# Branch:  fleet/<agent>/<task-short> (from origin/main)
#
# If the worktree already exists for this agent, resets it to latest main.
# Returns the worktree path on stdout (last line).

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_NAME="${1:?Usage: setup-worktree.sh <project-name> <agent-name> [task-id]}"
AGENT_NAME="${2:?Usage: setup-worktree.sh <project-name> <agent-name> [task-id]}"
TASK_ID="${3:-$(date +%s)}"
TASK_SHORT="${TASK_ID:0:8}"

PROJECTS_DIR="$FLEET_DIR/projects"
PROJECT_PATH="$PROJECTS_DIR/$PROJECT_NAME"

# Handle local projects
if [[ "$PROJECT_NAME" == "openclaw-fleet" ]]; then
    PROJECT_PATH="$FLEET_DIR"
fi

if [[ ! -d "$PROJECT_PATH/.git" ]]; then
    echo "ERROR: Project not cloned. Run: bash scripts/setup-project.sh $PROJECT_NAME" >&2
    exit 1
fi

WORKTREE_DIR="$PROJECT_PATH/worktrees/${AGENT_NAME}-${TASK_SHORT}"
BRANCH_NAME="fleet/${AGENT_NAME}/${TASK_SHORT}"

# Get default branch
cd "$PROJECT_PATH"
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' || echo "main")

if [[ -d "$WORKTREE_DIR" ]]; then
    echo "Worktree exists, updating: $WORKTREE_DIR" >&2
    cd "$WORKTREE_DIR"
    git fetch origin "$DEFAULT_BRANCH" 2>/dev/null || true
    git reset --hard "origin/$DEFAULT_BRANCH" 2>/dev/null || git reset --hard "$DEFAULT_BRANCH"
else
    echo "Creating worktree: $WORKTREE_DIR" >&2
    cd "$PROJECT_PATH"
    git fetch origin "$DEFAULT_BRANCH" 2>/dev/null || true

    # Create branch and worktree
    git worktree add -b "$BRANCH_NAME" "$WORKTREE_DIR" "origin/$DEFAULT_BRANCH" 2>/dev/null || \
    git worktree add -b "$BRANCH_NAME" "$WORKTREE_DIR" "$DEFAULT_BRANCH" 2>/dev/null || \
    git worktree add -b "$BRANCH_NAME" "$WORKTREE_DIR" HEAD
fi

echo "Branch: $BRANCH_NAME" >&2
echo "Based on: $DEFAULT_BRANCH" >&2

# Output the path (for scripts to capture)
echo "$WORKTREE_DIR"