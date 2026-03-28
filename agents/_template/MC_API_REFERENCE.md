# MC API Reference (Manual Fallback)

**This file is a reference only.** Use fleet MCP tools instead.
Only use these manual methods if fleet tools are completely unavailable.

## Task Update (manual)
```bash
curl -s -X PATCH "$BASE_URL/api/v1/agent/boards/$BOARD_ID/tasks/$TASK_ID" \
  -H "X-Agent-Token: $AUTH_TOKEN" -H "Content-Type: application/json" \
  -d '{"status": "in_progress", "comment": "Starting work."}'
```

## Post Comment (manual)
```bash
curl -s -X POST "$BASE_URL/api/v1/agent/boards/$BOARD_ID/tasks/$TASK_ID/comments" \
  -H "X-Agent-Token: $AUTH_TOKEN" -H "Content-Type: application/json" \
  -d '{"message": "Progress: ..."}'
```

## Board Memory (manual)
```bash
curl -s -X POST "$BASE_URL/api/v1/agent/boards/$BOARD_ID/memory" \
  -H "X-Agent-Token: $AUTH_TOKEN" -H "Content-Type: application/json" \
  -d '{"content": "...", "tags": ["..."], "source": "agent-name"}'
```

## Credentials
Read from TOOLS.md: AUTH_TOKEN, BASE_URL, BOARD_ID