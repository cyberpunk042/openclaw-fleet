# Agent Keepalive & Control Sync — Requirements Understanding

## PO Requirements (Verbatim)

> "lets be methodical and investigate why the agents become offline"
> "I dont think its the restart but maybe the restart agent on ocmc restart is broken?"
> "then there is the CRON, what is the health of all that and the sync with the orchestrator and the pauses and update of CRONs with the budget and the update of brain frequency like it says it does?"
> "you have to think of the sync with openclaw and openarms"
> "you have to keep in mind what I said about budget and its influence"

## Existing Architecture (What We Already Built)

The fleet has a **complete multi-layered heartbeat system**. The problem is not that it doesn't exist — it's that pieces are broken or disconnected after the OpenArms migration.

### Layer 1: Gateway CRON Jobs
- **Where:** `~/.openarms/cron/jobs.json` (or `~/.openclaw/cron/jobs.json`)
- **Created by:** MC provisioning via `cron.add` RPC during template sync
- **Fires:** Every 30-90 minutes per agent (staggered intervals in `clean-gateway-config.sh`)
- **What it does:** Sends heartbeat prompt to Claude via the agent's session
- **Controlled by:** `enable_gateway_cron_jobs()`, `disable_gateway_cron_jobs()`, `update_cron_tempo()`
- **Gateway picks up changes:** Within 60s (forceReload on every timer tick)

### Layer 2: Agent Lifecycle State Machine (`agent_lifecycle.py`)
- **States:** ACTIVE → IDLE → SLEEPING → OFFLINE
- **Transitions:** Based on consecutive HEARTBEAT_OK responses and time
- **Key logic:** `needs_heartbeat(now)` returns different intervals per state:
  - ACTIVE: 0 (no cron, agent is working)
  - IDLE: 10 min
  - SLEEPING: 30 min
  - OFFLINE: 60 min
- **Brain evaluator:** After 1 consecutive HEARTBEAT_OK, `brain_evaluates = True` → Python intercepts heartbeat (FREE, no Claude call) and decides: WAKE, SILENT, or STRATEGIC

### Layer 3: Heartbeat Context Bundling (`heartbeat_context.py`)
- **Pre-computes** all data an agent needs: assigned tasks, chat messages, mentions, domain events, sprint summary, fleet state, Plane data, budget warnings
- **Written to:** `{workspace}/HEARTBEAT.md` before cron fires
- **Format:** Full uncompressed text via `build_heartbeat_preembed()`
- **Role-specific:** Different data for PM, fleet-ops, workers

### Layer 4: Heartbeat Gate (`heartbeat_gate.py`)
- **Purpose:** Decide if heartbeat should wake Claude ($$) or stay silent ($0)
- **Triggers for WAKE:** Direct mention, new task assigned, PO directive, role-specific events
- **Result:** SILENT (no cost), WAKE (normal), STRATEGIC (opus with high effort for urgent)

### Layer 5: Heartbeat Cost Tracking (`heartbeat_stamp.py`)
- Tracks cost per heartbeat, detects anomalies (avg > $0.10, > 20/hour, high void rate)

### Layer 6: MC last_seen_at Updates
- `POST /api/v1/agents/{id}/heartbeat` — explicit heartbeat call, updates `last_seen_at`
- `_touch_agent_presence()` — any agent-authenticated API call, throttled to 30s
- `mark_provision_complete()` — after successful provisioning
- **OFFLINE_AFTER = 10 minutes** — computed dynamically on every API read

## What's Broken

### B1: Stale CRON Jobs
**Problem:** `~/.openarms/cron/jobs.json` has 3 jobs with OLD agent IDs from legacy openclaw. MC creates CRON jobs during provisioning via `cron.add` RPC, but provisioning failed during the restart cascade. Jobs were never recreated for current agent IDs.

**Evidence:** Job agentIds don't match current MC agent UUIDs.

**Fix:** Template sync must recreate CRON jobs for all current agents. The `POST /api/v1/gateways/{id}/templates/sync` endpoint does this — but it wasn't called after the final gateway restart.

### B2: HeartbeatRunner vs MC last_seen_at Disconnect
**Problem:** The gateway's HeartbeatRunner fires heartbeats locally (LLM inference + delivery) but never calls MC's `/api/v1/agents/{id}/heartbeat` to update `last_seen_at`. MC's 10-minute timeout expires because nothing touches `last_seen_at` continuously.

**Evidence:** Agents show online immediately after setup (manual heartbeat API calls), then go offline after 10 minutes (no subsequent calls).

**What should happen:** When a gateway heartbeat fires for an agent, MC should know about it. Either:
- The gateway should call MC's heartbeat endpoint after each heartbeat run
- Or the orchestrator should periodically touch `last_seen_at` for agents it knows are alive

### B3: Orchestrator Doesn't Drive Heartbeat Context Writes
**Problem:** The orchestrator has `build_heartbeat_context()` and `write_heartbeat_context()` but these may not be running because the fleet starts paused and the orchestrator exits early on `work_mode == "work-paused"`.

**Evidence:** Orchestrator line 203-205: `if not fleet_should_dispatch(fleet_state): return state` — when paused, it returns before reaching any heartbeat context logic.

**Fix:** Heartbeat context writing should happen even when dispatch is paused. Agents still need fresh context for when they wake up.

### B4: Budget Mode Doesn't Affect Orchestrator Cycle
**Problem:** Budget mode changes CRON intervals via `update_cron_tempo()` but doesn't change the orchestrator's own cycle speed (hardcoded 30s).

**What should happen:** In "turbo" mode, orchestrator could run faster. In "economic" mode, slower. But the keepalive (touching `last_seen_at`) must always stay within 10min regardless.

### B5: Setup Doesn't Trigger Template Sync After Final Restart
**Problem:** Setup.sh restarts the gateway after seeding and cleaning config. This destroys agent sessions. Then the "Final Agent Sync" tries to call the heartbeat API to touch `last_seen_at`. But the CRON jobs are stale, so no ongoing heartbeats fire after that.

**Fix:** After the final gateway restart, setup should trigger `POST /api/v1/gateways/{id}/templates/sync` which recreates CRON jobs for all agents.

### B6: Vendor Compatibility
**Problem:** `_resolve_cron_path()` finds the first existing cron file (checks openarms first, then openclaw). The stale jobs from openclaw were copied to openarms during vendor cutover. They have wrong agent IDs.

**Fix:** CRON jobs must be vendor-independent — MC creates them via RPC, gateway stores them in the active vendor's cron dir. The fleet code just needs to point to the right path (already handled by `_resolve_cron_path()`).

## Required Changes

### C1: Fix CRON Job Recreation (Setup IaC)
After the final gateway restart in setup.sh, trigger template sync to recreate CRON jobs:
```bash
# After final gateway restart:
curl -X POST http://localhost:8000/api/v1/gateways/${GW_ID}/templates/sync -d '{}'
```
This makes MC call `cron.add` for each agent → valid CRON jobs in `~/.openarms/cron/jobs.json`.

### C2: Orchestrator Keepalive (Touch last_seen_at)
Add a lightweight keepalive step in the orchestrator cycle that runs EVEN when paused:
- Before the dispatch gate (`should_dispatch()` check)
- Calls `mc.batch_heartbeat(agent_ids)` or individual heartbeat calls
- Runs every cycle (30s) — well within 10min timeout
- Costs nothing (just HTTP POST to MC, no Claude calls)

### C3: Heartbeat Context Writes During Pause
Move the heartbeat context write step BEFORE the dispatch gate so agents get fresh context even when paused. When they wake up (resume), their HEARTBEAT.md is already current.

### C4: Budget Mode Orchestra Cycle Adjustment
When budget mode changes, adjust the orchestrator daemon interval:
- turbo: 5s cycle
- aggressive: 15s
- standard: 30s
- economic: 60s
But keepalive (touching `last_seen_at`) still happens every cycle regardless — no cycle can exceed 10min.

### C5: Template Sync After Gateway Restart
Any gateway restart should trigger template sync to ensure CRON jobs are valid. This can be done in `start-fleet.sh` after the gateway health check passes.

## Vendor Compatibility

All changes work with both openclaw and openarms:
- `_resolve_cron_path()` handles both vendor dirs ✓
- MC client uses `resolve_vendor_config()` ✓
- Gateway client uses `resolve_vendor_client_id()` ✓
- Template sync is a MC API call (vendor-independent) ✓
- CRON jobs are created by MC via gateway RPC (works with both vendors) ✓

## Verification

1. `./setup.sh` → agents online → wait 15 min → agents STILL online
2. Change budget to "turbo" → CRON intervals shrink, orchestrator runs faster
3. Change budget to "economic" → CRON intervals grow, orchestrator runs slower
4. UI pause (work_mode=work-paused) → agents stay online, no dispatch
5. OCMC board pause → agents stay online, no dispatch for that board
6. CLI `fleet pause` → kills everything, agents go offline (correct)
7. CLI `fleet resume` → agents come back, work_mode restored
8. Gateway restart → agents stay online (template sync recreates CRON, orchestrator keepalive covers gap)
9. Works with openclaw vendor AND openarms vendor
