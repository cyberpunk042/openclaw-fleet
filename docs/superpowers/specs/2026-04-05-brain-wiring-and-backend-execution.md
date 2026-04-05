# Brain Wiring & Backend Execution

## Summary

Wire the existing heartbeat brain evaluator into the orchestrator cycle, connect the backend routing engine to actual execution, and add OpenRouter free models. The code exists — it just needs to be connected.

## Context

The fleet has a complete but disconnected architecture:
- `heartbeat_gate.py` — brain evaluator (WAKE/SILENT/STRATEGIC), never called
- `agent_lifecycle.py` — state machine with `brain_evaluates` property, updated but never queried
- `backend_router.py` — full routing engine (complexity → backend mapping), decides but doesn't execute
- `openai_client.py` — LocalAI/OpenRouter HTTP clients, exist but not called from dispatch

Design docs that specify how these connect:
- `docs/systems/06-agent-lifecycle.md` — explicitly documents the gap
- `docs/milestones/active/fleet-elevation/23-agent-lifecycle-and-strategic-calls.md` — PO requirements
- `docs/milestones/active/standards/brain-modules-standard.md` — implementation blueprint
- `docs/INTEGRATION.md` — Flow 2: Agent Heartbeat with brain gate

## Part A: Wire Brain Evaluator into Orchestrator

### What exists
- `FleetLifecycle` imported and updated every orchestrator cycle
- `agents_needing_heartbeat(now)` method exists but never called
- `evaluate_agent_heartbeat()` function exists but never called
- `brain_evaluates` property exists but never checked
- `record_heartbeat_ok()` / `record_heartbeat_work()` exist but never called in production

### What to add (new orchestrator step)

After the fleet lifecycle update and BEFORE the dispatch gate, add a brain evaluation step:

```
For each agent where needs_heartbeat(now) == True:
  If brain_evaluates:
    Run evaluate_agent_heartbeat() — free Python, $0
    If SILENT:
      - Touch MC last_seen_at via heartbeat API
      - Post board activity: "Heartbeat received from {agent}. (silent)"
      - Call record_heartbeat_ok()
      - Mark heartbeat sent
    If WAKE:
      - Write fresh HEARTBEAT.md context
      - Let gateway CRON fire real Claude heartbeat
      - Mark heartbeat sent
    If STRATEGIC:
      - Write fresh HEARTBEAT.md with model/effort overrides
      - Let gateway CRON fire with strategic config
      - Mark heartbeat sent
  Else (not brain_evaluates — agent is ACTIVE or first heartbeat):
    - Write fresh HEARTBEAT.md context (normal)
    - Let gateway CRON fire normally
```

### MC activity reporting

Silent heartbeats must be visible in the board activity log:

- SILENT: `"Heartbeat received from {agent_name}. (silent)"` — tags: `["heartbeat", "silent", agent_name]`
- WAKE: `"Heartbeat received from {agent_name}."` — tags: `["heartbeat", agent_name]`
- STRATEGIC: `"Heartbeat received from {agent_name}. (strategic: {model})"` — tags: `["heartbeat", "strategic", agent_name]`

### Files to modify
- `fleet/cli/orchestrator.py` — add brain evaluation step
- `fleet/infra/mc_client.py` — add `post_board_memory(board_id, content, tags)` method
- `fleet/core/heartbeat_context.py` — ensure context is built for brain evaluation inputs

## Part B: Wire Backend Routing to Execution

### What exists
- `backend_router.py` — `route_task()` returns `RoutingDecision` with backend, model, effort, fallback
- `openai_client.py` — `create_localai_client()`, OpenRouter integration with headers
- `fleet/cli/dispatch.py` — calls `route_task()`, records decision, but always dispatches via Claude Code CLI

### What to add

When `RoutingDecision.backend` is NOT "claude-code":
- "localai": call LocalAI at `http://localhost:8090/v1/chat/completions` via `openai_client.py`
- "openrouter-free": call OpenRouter at `https://openrouter.ai/api/v1/chat/completions`
- "direct": use local tools without LLM (structured operations)

When backend is "claude-code": continue using Claude Code CLI (current behavior).

Fallback: if primary backend fails, try `fallback_backend` from the routing decision.

### OpenRouter free models

Add Qwen3.6 Plus to the backend registry:
- Model ID: to be confirmed (check OpenRouter for exact ID)
- Type: openrouter-free
- Capabilities: reasoning, code, structured
- Cost: $0

Update `backend_router.py` backend definitions to include this model.

### Files to modify
- `fleet/cli/dispatch.py` — route to actual backends based on RoutingDecision
- `fleet/core/backend_router.py` — add Qwen3.6 Plus model
- `fleet/core/openai_client.py` — ensure LocalAI and OpenRouter clients work
- `gateway/executor.py` — support non-Claude execution paths

## Part C: Budget Mode

Budget mode controls **tempo only** — orchestrator cycle speed and CRON heartbeat intervals:
- turbo: 5s cycle, fastest heartbeats
- aggressive: 15s cycle
- standard: 30s cycle
- economic: 60s cycle

Already implemented:
- CRON intervals via `update_cron_tempo()` ✓
- Orchestrator cycle speed via tempo_multiplier sleep ✓
- Safe at all speeds (keepalive every 5 cycles, worst case 5min at economic) ✓

No additional budget mode changes needed.

## Verification

1. Agent goes IDLE after 1 HEARTBEAT_OK → brain_evaluates = True → next heartbeat is SILENT ($0)
2. Board activity shows "Heartbeat received from devops. (silent)"
3. Agent stays online in MC during silent heartbeats (last_seen_at touched)
4. @mention triggers WAKE → real Claude heartbeat fires
5. Task assignment triggers WAKE
6. Backend mode "claude+localai" routes trivial tasks to LocalAI
7. Backend mode "openrouter" routes to OpenRouter free tier
8. Qwen3.6 Plus available as a model option
