#!/usr/bin/env bash
set -euo pipefail

# Trace a task — show everything about it: MC data, activity, worktree, commits.
#
# Usage: bash scripts/trace-task.sh <task-id>
#
# Shows:
#   - Task details from MC (title, status, agent, timestamps)
#   - All task comments (chronological)
#   - Related activity events
#   - Worktree location and git log (if exists)
#   - Board memory entries mentioning this task

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/.env" 2>/dev/null || true

MC_URL="${OCF_MISSION_CONTROL_URL:-http://localhost:8000}"
TOKEN="${LOCAL_AUTH_TOKEN:-}"
TASK_ID="${1:?Usage: trace-task.sh <task-id>}"
TASK_SHORT="${TASK_ID:0:8}"

if [[ -z "$TOKEN" ]]; then echo "ERROR: No LOCAL_AUTH_TOKEN" >&2; exit 1; fi

BOLD='\033[1m'
DIM='\033[2m'
CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
NC='\033[0m'

# Get board ID
BOARD_ID=$(curl -s -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/agents" | python3 -c "
import json, sys
for a in json.load(sys.stdin).get('items', []):
    if a.get('board_id'): print(a['board_id']); break
" 2>/dev/null)

echo -e "${BOLD}=== Task Trace: $TASK_SHORT ===${NC}"
echo ""

# 1. Task details
echo -e "${BOLD}Task${NC}"
curl -s -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/boards/${BOARD_ID}/tasks" | python3 -c "
import json, sys
for t in json.load(sys.stdin).get('items', []):
    if str(t.get('id','')) == '$TASK_ID':
        print(f'  Title:    {t[\"title\"]}')
        print(f'  Status:   {t[\"status\"]}')
        print(f'  Priority: {t.get(\"priority\",\"?\")}')
        agent_id = t.get('assigned_agent_id')
        print(f'  Agent:    {agent_id or \"(unassigned)\"}')
        print(f'  Created:  {t[\"created_at\"]}')
        print(f'  Updated:  {t[\"updated_at\"]}')
        desc = t.get('description', '')
        if desc:
            print(f'  Desc:     {desc[:200]}')
        break
else:
    print('  Task not found')
" 2>/dev/null

# 2. Activity events
echo ""
echo -e "${BOLD}Activity${NC}"
curl -s -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/activity?limit=50" | python3 -c "
import json, sys
events = json.load(sys.stdin).get('items', [])
task_events = [e for e in events if '$TASK_SHORT' in str(e.get('message','')) or '$TASK_ID' in str(e.get('task_id',''))]
if not task_events:
    # Try matching by task title keywords
    task_events = [e for e in events if any(word in str(e.get('message','')) for word in ['$TASK_SHORT'])]
for e in task_events:
    ts = e.get('created_at', '')[:19].replace('T', ' ')
    evt = e.get('event_type', '')
    msg = str(e.get('message', ''))
    # Truncate long messages but keep first 200 chars
    if len(msg) > 200:
        msg = msg[:200] + '...'
    print(f'  {ts}  {evt}')
    if msg:
        for line in msg.split(chr(10))[:5]:
            print(f'    {line}')
if not task_events:
    print('  (no activity found for this task)')
" 2>/dev/null

# 3. Worktree
echo ""
echo -e "${BOLD}Worktree${NC}"
WORKTREE=""
for wt in "$FLEET_DIR"/projects/*/worktrees/*-"$TASK_SHORT"; do
    if [[ -d "$wt" ]]; then
        WORKTREE="$wt"
        break
    fi
done

if [[ -n "$WORKTREE" ]]; then
    AGENT=$(basename "$WORKTREE" | sed "s/-${TASK_SHORT}$//")
    BRANCH=$(cd "$WORKTREE" && git branch --show-current 2>/dev/null || echo "?")
    echo "  Path:   $WORKTREE"
    echo "  Agent:  $AGENT"
    echo "  Branch: $BRANCH"
    echo ""
    echo -e "  ${BOLD}Commits${NC}"
    DEFAULT=$(cd "$WORKTREE" && git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' || echo "main")
    COMMITS=$(cd "$WORKTREE" && git log --oneline "origin/$DEFAULT..HEAD" 2>/dev/null || true)
    if [[ -n "$COMMITS" ]]; then
        echo "$COMMITS" | while read -r line; do echo "    $line"; done
    else
        echo "    (no commits beyond $DEFAULT)"
    fi
    echo ""
    echo -e "  ${BOLD}Files Changed${NC}"
    DIFF=$(cd "$WORKTREE" && git diff --stat "origin/$DEFAULT..HEAD" 2>/dev/null || true)
    if [[ -n "$DIFF" ]]; then
        echo "$DIFF" | while read -r line; do echo "    $line"; done
    else
        echo "    (no changes)"
    fi
else
    echo "  (no worktree found for task $TASK_SHORT)"
fi

# 4. Board memory
echo ""
echo -e "${BOLD}Board Memory${NC}"
curl -s -H "Authorization: Bearer $TOKEN" "$MC_URL/api/v1/boards/${BOARD_ID}/memory?limit=20" | python3 -c "
import json, sys
items = json.load(sys.stdin).get('items', [])
matches = [m for m in items if '$TASK_SHORT' in m.get('content', '') or '$TASK_ID' in m.get('content', '')]
if not matches:
    print('  (no board memory entries for this task)')
for m in matches:
    ts = m.get('created_at', '')[:19].replace('T', ' ')
    tags = m.get('tags', [])
    content = m.get('content', '')[:200]
    print(f'  {ts}  tags={tags}')
    print(f'    {content}')
" 2>/dev/null