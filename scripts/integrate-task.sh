#!/usr/bin/env bash
set -euo pipefail

# Integrate agent work into a target project.
#
# Usage:
#   bash scripts/integrate-task.sh <task-id> <target-project-path> [--push] [--pr]
#
# For worktree-based tasks: shows branch diff, optionally pushes + creates PR.
# For MC workspace tasks: copies non-infra files to target, creates branch + commit.

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/.env" 2>/dev/null || true

MC_URL="${OCF_MISSION_CONTROL_URL:-http://localhost:8000}"
TOKEN="${LOCAL_AUTH_TOKEN:-}"

TASK_ID="${1:?Usage: integrate-task.sh <task-id> <target-path> [--push] [--pr]}"
TARGET_PATH="${2:?Usage: integrate-task.sh <task-id> <target-path> [--push] [--pr]}"
DO_PUSH=false
DO_PR=false
shift 2
while [[ $# -gt 0 ]]; do
    case "$1" in
        --push) DO_PUSH=true; shift ;;
        --pr) DO_PR=true; DO_PUSH=true; shift ;;
        *) shift ;;
    esac
done

if [[ -z "$TOKEN" ]]; then echo "ERROR: No LOCAL_AUTH_TOKEN" >&2; exit 1; fi
if [[ ! -d "$TARGET_PATH/.git" ]]; then echo "ERROR: $TARGET_PATH is not a git repo" >&2; exit 1; fi

TASK_SHORT="${TASK_ID:0:8}"

# 1. Find task info from MC
echo "=== Finding task ==="
BOARD_ID=$(curl -s -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/agents" | python3 -c "
import json, sys
for a in json.load(sys.stdin).get('items', []):
    if a.get('board_id'): print(a['board_id']); break
" 2>/dev/null)

TASK_TITLE=$(curl -s -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/boards/${BOARD_ID}/tasks" | python3 -c "
import json, sys
for t in json.load(sys.stdin).get('items', []):
    if str(t.get('id','')) == '$TASK_ID':
        print(t.get('title',''))
        break
" 2>/dev/null)

if [[ -z "$TASK_TITLE" ]]; then
    echo "ERROR: Task $TASK_ID not found" >&2
    exit 1
fi

# 2. Find workspace — check project worktrees first, fall back to MC workspace
WORKSPACE=""
AGENT_NAME=""

for wt in "$FLEET_DIR"/projects/*/worktrees/*-"$TASK_SHORT"; do
    if [[ -d "$wt" ]]; then
        WORKSPACE="$wt"
        AGENT_NAME=$(basename "$wt" | sed "s/-${TASK_SHORT}$//")
        break
    fi
done

if [[ -z "$WORKSPACE" ]]; then
    # Fall back to MC workspace via agent assignment
    AGENT_ID=$(curl -s -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/boards/${BOARD_ID}/tasks" | python3 -c "
import json, sys
for t in json.load(sys.stdin).get('items', []):
    if str(t.get('id','')) == '$TASK_ID':
        v = t.get('assigned_agent_id','')
        if v and str(v) != 'None': print(v)
        break
" 2>/dev/null)
    if [[ -n "$AGENT_ID" ]]; then
        WORKSPACE="$FLEET_DIR/workspace-mc-${AGENT_ID}"
        AGENT_NAME=$(curl -s -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/agents" | python3 -c "
import json, sys
for a in json.load(sys.stdin).get('items', []):
    if str(a.get('id','')) == '$AGENT_ID': print(a.get('name','')); break
" 2>/dev/null)
    fi
fi

if [[ -z "$WORKSPACE" || ! -d "$WORKSPACE" ]]; then
    echo "ERROR: No workspace found for task $TASK_ID" >&2
    echo "  Searched: projects/*/worktrees/*-$TASK_SHORT" >&2
    exit 1
fi

# Detect mode
IS_WORKTREE=false
if cd "$WORKSPACE" && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null || echo "")
    if [[ -n "$BRANCH" && "$BRANCH" == fleet/* ]]; then
        IS_WORKTREE=true
    fi
fi

echo "Task:      $TASK_TITLE"
echo "Agent:     $AGENT_NAME"
echo "Workspace: $WORKSPACE"
echo "Target:    $TARGET_PATH"
echo "Mode:      $(if $IS_WORKTREE; then echo "git worktree (branch: $BRANCH)"; else echo 'file copy'; fi)"

# 3. Show changes
echo ""
if $IS_WORKTREE; then
    cd "$WORKSPACE"
    DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' || echo "main")
    COMMITS=$(git log --oneline "origin/$DEFAULT_BRANCH..HEAD" 2>/dev/null || true)

    if [[ -z "$COMMITS" ]]; then
        echo "No commits on branch $BRANCH beyond $DEFAULT_BRANCH."
        echo "Nothing to integrate."
        exit 0
    fi

    echo "=== Commits ==="
    echo "$COMMITS"
    COMMIT_COUNT=$(echo "$COMMITS" | wc -l)
    FILE_COUNT=$(git diff --name-only "origin/$DEFAULT_BRANCH..HEAD" | wc -l)
    echo ""
    echo "=== Files changed ($FILE_COUNT) ==="
    git diff --stat "origin/$DEFAULT_BRANCH..HEAD"
    echo ""
    echo "=== Diff ==="
    git diff "origin/$DEFAULT_BRANCH..HEAD" | head -80
    [[ $(git diff "origin/$DEFAULT_BRANCH..HEAD" | wc -l) -gt 80 ]] && echo "... (truncated)"
else
    echo "=== Agent work files ==="
    WORK_FILES=()
    while IFS= read -r file; do
        skip=false
        for pat in AGENTS.md BOOTSTRAP.md HEARTBEAT.md IDENTITY.md MEMORY.md SOUL.md TOOLS.md USER.md; do
            [[ "$(basename "$file")" == "$pat" ]] && skip=true
        done
        for d in .openclaw .claude memory api; do
            [[ "$file" == "$d"/* ]] && skip=true
        done
        $skip || WORK_FILES+=("$file")
    done < <(cd "$WORKSPACE" && find . -type f -not -path './.git/*' | sed 's|^\./||' | sort)

    if [[ ${#WORK_FILES[@]} -eq 0 ]]; then
        echo "No work files found."
        exit 0
    fi
    for f in "${WORK_FILES[@]}"; do echo "  $f"; done
    FILE_COUNT=${#WORK_FILES[@]}
    COMMIT_COUNT=0
fi

# 4. Confirm
echo ""
read -p "Proceed with integration? [y/N] " -r REPLY
if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# 5. Integrate
echo ""
echo "=== Integrating ==="

if $IS_WORKTREE; then
    cd "$WORKSPACE"
    if [[ "$DO_PUSH" == "true" ]]; then
        echo "Pushing branch $BRANCH..."
        git push -u origin "$BRANCH"
    else
        echo "Branch $BRANCH is ready."
        echo "To push: cd $WORKSPACE && git push -u origin $BRANCH"
    fi
else
    cd "$TARGET_PATH"
    if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
        git stash push -m "pre-integration-${TASK_SHORT}"
    fi
    DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' || echo "main")
    BRANCH="fleet/${AGENT_NAME}/${TASK_SHORT}"
    git checkout -b "$BRANCH" "origin/$DEFAULT_BRANCH" 2>/dev/null || git checkout -b "$BRANCH"
    for f in "${WORK_FILES[@]}"; do
        mkdir -p "$(dirname "$TARGET_PATH/$f")"
        cp "$WORKSPACE/$f" "$TARGET_PATH/$f"
    done
    git add "${WORK_FILES[@]}"
    git commit -m "fleet($AGENT_NAME): $TASK_TITLE

Task: $TASK_ID
Agent: $AGENT_NAME"
    if [[ "$DO_PUSH" == "true" ]]; then
        git push -u origin "$BRANCH"
    fi
fi

# 6. PR
if [[ "$DO_PR" == "true" ]]; then
    PR_DIR="$WORKSPACE"
    $IS_WORKTREE || PR_DIR="$TARGET_PATH"
    if command -v gh >/dev/null 2>&1; then
        cd "$PR_DIR"
        gh pr create --title "fleet($AGENT_NAME): $TASK_TITLE" --body "Task: \`$TASK_ID\`
Agent: $AGENT_NAME
Files: $FILE_COUNT

Generated by openclaw-fleet."
    else
        echo "WARN: gh not found — branch pushed but no PR created"
    fi
fi

echo ""
echo "=== Done ==="
echo "Branch: $BRANCH"
echo "Files: $FILE_COUNT"