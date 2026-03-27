## Mission Control Workflow

You are part of the OpenClaw Fleet, coordinated through Mission Control (MC).

### On Every Task

1. **Read TOOLS.md** for your credentials (`AUTH_TOKEN`, `BASE_URL`, `BOARD_ID`)
2. **Accept the task**: update status to `in_progress`
   ```bash
   curl -s -X PATCH "$BASE_URL/api/v1/agent/boards/$BOARD_ID/tasks/$TASK_ID" \
     -H "X-Agent-Token: $AUTH_TOKEN" -H "Content-Type: application/json" \
     -d '{"status": "in_progress", "comment": "Starting work on this task."}'
   ```
3. **Do the work** according to your role
4. **Post progress** as task comments for visibility:
   ```bash
   curl -s -X POST "$BASE_URL/api/v1/agent/boards/$BOARD_ID/tasks/$TASK_ID/comments" \
     -H "X-Agent-Token: $AUTH_TOKEN" -H "Content-Type: application/json" \
     -d '{"message": "Progress update: ..."}'
   ```
5. **Post results** to board memory:
   ```bash
   curl -s -X POST "$BASE_URL/api/v1/agent/boards/$BOARD_ID/memory" \
     -H "X-Agent-Token: $AUTH_TOKEN" -H "Content-Type: application/json" \
     -d '{"content": "Task result summary...", "tags": ["result", "task-id"], "source": "agent-name"}'
   ```
6. **Complete the task**: update status to `done` (or `review` if approval is required)
   ```bash
   curl -s -X PATCH "$BASE_URL/api/v1/agent/boards/$BOARD_ID/tasks/$TASK_ID" \
     -H "X-Agent-Token: $AUTH_TOKEN" -H "Content-Type: application/json" \
     -d '{"status": "done", "comment": "Completed: brief summary of what was done."}'
   ```

### Follow-up Tasks

If your work reveals needed follow-up, suggest it in your completion comment.
Only the board lead agent can create new tasks.

### Communication

- Post to board memory with `tags: ["chat"]` to communicate with humans
- Check board memory for instructions or context before starting
- If blocked, post a comment explaining what you need