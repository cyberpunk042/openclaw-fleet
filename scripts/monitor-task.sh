#!/usr/bin/env bash
# =============================================================================
# monitor-task.sh — Monitor a Mission Control task's progress in real time
#
# Usage: bash scripts/monitor-task.sh <task-id>
#
# What it does:
#   - Polls the task status every 10 seconds
#   - Displays task title, status, and last updated time
#   - Shows new task comments as they appear
#   - Shows board memory entries tagged with the task ID
#   - Exits automatically when status becomes 'done'
#
# Requires: curl, python3
# Auth: reads LOCAL_AUTH_TOKEN from .env (falls back to AUTH_TOKEN env var)
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BOARD_ID="828d80ab-6bda-4d23-9da3-a670f14ea710"
BASE_URL="${BASE_URL:-http://localhost:8000}"
POLL_INTERVAL=10

# ---------------------------------------------------------------------------
# Load credentials from .env if present
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$WORKSPACE_ROOT/.env"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck source=/dev/null
  source "$ENV_FILE"
fi

# Prefer LOCAL_AUTH_TOKEN from .env; fall back to AUTH_TOKEN env var
TOKEN="${LOCAL_AUTH_TOKEN:-${AUTH_TOKEN:-}}"

if [[ -z "$TOKEN" ]]; then
  echo "ERROR: No auth token found. Set LOCAL_AUTH_TOKEN in .env or AUTH_TOKEN in environment." >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Argument validation
# ---------------------------------------------------------------------------
if [[ $# -lt 1 ]]; then
  echo "Usage: bash scripts/monitor-task.sh <task-id>"
  exit 1
fi

TASK_ID="$1"

# ---------------------------------------------------------------------------
# Helper: authenticated GET
# ---------------------------------------------------------------------------
api_get() {
  local path="$1"
  curl -sf \
    -H "X-Agent-Token: $TOKEN" \
    -H "Accept: application/json" \
    "${BASE_URL}${path}"
}

# ---------------------------------------------------------------------------
# Helper: parse JSON field with python3 (no jq required)
# ---------------------------------------------------------------------------
json_field() {
  local json="$1"
  local field="$2"
  echo "$json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
val = data.get('$field', '')
print(val if val is not None else '')
"
}

json_array_field() {
  local json="$1"
  local field="$2"
  echo "$json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
items = data.get('$field', [])
for item in items:
    print(json.dumps(item))
"
}

# ---------------------------------------------------------------------------
# Find the task in the board task list
# ---------------------------------------------------------------------------
find_task() {
  local tasks_json
  tasks_json="$(api_get "/api/v1/agent/boards/${BOARD_ID}/tasks")"

  echo "$tasks_json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
tasks = data if isinstance(data, list) else data.get('tasks', data.get('items', []))
for t in tasks:
    if t.get('id') == '$TASK_ID':
        print(json.dumps(t))
        sys.exit(0)
print('')
"
}

# ---------------------------------------------------------------------------
# Fetch comments for the task
# ---------------------------------------------------------------------------
fetch_comments() {
  api_get "/api/v1/agent/boards/${BOARD_ID}/tasks/${TASK_ID}/comments" 2>/dev/null || echo "[]"
}

# ---------------------------------------------------------------------------
# Fetch board memory entries tagged with the task ID
# ---------------------------------------------------------------------------
fetch_tagged_memory() {
  local mem_json
  mem_json="$(api_get "/api/v1/agent/boards/${BOARD_ID}/memory" 2>/dev/null || echo "[]")"

  echo "$mem_json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
entries = data if isinstance(data, list) else data.get('entries', data.get('items', []))
for e in entries:
    tags = e.get('tags', [])
    if '$TASK_ID' in tags:
        print(json.dumps(e))
"
}

# ---------------------------------------------------------------------------
# Pretty-print a timestamp (strip microseconds for readability)
# ---------------------------------------------------------------------------
fmt_time() {
  echo "${1%%.*}" | sed 's/T/ /'
}

# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

status_color() {
  case "$1" in
    done)     echo -e "${GREEN}${BOLD}" ;;
    review)   echo -e "${CYAN}${BOLD}" ;;
    in_progress) echo -e "${YELLOW}${BOLD}" ;;
    blocked)  echo -e "${RED}${BOLD}" ;;
    *)        echo -e "${RESET}" ;;
  esac
}

# ---------------------------------------------------------------------------
# Main monitor loop
# ---------------------------------------------------------------------------
echo -e "${BOLD}Mission Control — Task Monitor${RESET}"
echo -e "Task ID : ${CYAN}${TASK_ID}${RESET}"
echo -e "Board   : ${CYAN}${BOARD_ID}${RESET}"
echo -e "Polling every ${POLL_INTERVAL}s. Exits on status: done"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Track seen comment IDs so we only print new ones
declare -A SEEN_COMMENTS=()
# Track seen memory entry IDs
declare -A SEEN_MEMORY=()

LAST_STATUS=""

while true; do
  # -- Fetch current task state --
  TASK_JSON="$(find_task)"

  if [[ -z "$TASK_JSON" ]]; then
    echo -e "${RED}ERROR: Task ${TASK_ID} not found on board.${RESET}" >&2
    exit 1
  fi

  TITLE="$(json_field "$TASK_JSON" "title")"
  STATUS="$(json_field "$TASK_JSON" "status")"
  UPDATED="$(json_field "$TASK_JSON" "updated_at")"

  # -- Print status line if changed --
  if [[ "$STATUS" != "$LAST_STATUS" ]]; then
    COLOR="$(status_color "$STATUS")"
    echo ""
    echo -e "${BOLD}[$(date '+%H:%M:%S')]${RESET} ${BOLD}${TITLE}${RESET}"
    echo -e "  Status  : ${COLOR}${STATUS}${RESET}"
    echo -e "  Updated : $(fmt_time "$UPDATED")"
    LAST_STATUS="$STATUS"
  fi

  # -- Fetch and display new comments --
  COMMENTS_JSON="$(fetch_comments)"

  while IFS= read -r comment_line; do
    [[ -z "$comment_line" ]] && continue

    C_ID="$(echo "$comment_line" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))")"
    C_MSG="$(echo "$comment_line" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message',''))")"
    C_TIME="$(echo "$comment_line" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('created_at',''))")"
    C_AUTHOR="$(echo "$comment_line" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('author_agent_id') or d.get('author_user_id') or 'unknown')")"

    if [[ -n "$C_ID" && -z "${SEEN_COMMENTS[$C_ID]+x}" ]]; then
      SEEN_COMMENTS["$C_ID"]=1
      echo -e "  ${CYAN}💬 Comment [$(fmt_time "$C_TIME")] (${C_AUTHOR}):${RESET}"
      echo -e "     ${C_MSG}"
    fi
  done < <(echo "$COMMENTS_JSON" | python3 -c "
import sys, json
data = json.load(sys.stdin)
items = data if isinstance(data, list) else data.get('comments', data.get('items', []))
for item in items:
    print(json.dumps(item))
")

  # -- Fetch and display new tagged memory entries --
  while IFS= read -r mem_line; do
    [[ -z "$mem_line" ]] && continue

    M_ID="$(echo "$mem_line" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))")"
    M_CONTENT="$(echo "$mem_line" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('content',''))")"
    M_TIME="$(echo "$mem_line" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('created_at',''))")"
    M_SRC="$(echo "$mem_line" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('source',''))")"

    if [[ -n "$M_ID" && -z "${SEEN_MEMORY[$M_ID]+x}" ]]; then
      SEEN_MEMORY["$M_ID"]=1
      echo -e "  ${GREEN}📌 Memory [$(fmt_time "$M_TIME")] (${M_SRC}):${RESET}"
      echo -e "     ${M_CONTENT}"
    fi
  done < <(fetch_tagged_memory)

  # -- Exit conditions --
  if [[ "$STATUS" == "done" ]]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${BOLD}Task reached terminal status: ${STATUS}. Exiting.${RESET}"
    exit 0
  fi

  sleep "$POLL_INTERVAL"
done
