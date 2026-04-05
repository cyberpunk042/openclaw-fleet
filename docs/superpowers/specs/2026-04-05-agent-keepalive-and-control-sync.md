# Agent Keepalive & Control Sync — Requirements Understanding

## PO Requirements (Verbatim)

### R1: Why agents go offline
> "lets be methodical and investigate why the agents become offline"

**Finding:** Agents go offline because nothing calls MC's `/api/v1/agents/{id}/heartbeat` after setup. The gateway's HeartbeatRunner and CRON system run agent work (LLM inference) but never touch `last_seen_at` in MC. MC's `OFFLINE_AFTER = 10 minutes` expires and agents are computed as offline on every API read.

**Fix required:** A continuous keepalive mechanism that touches `last_seen_at` for all agents, independent of whether they're doing work.

### R2: OCMC restart / agent re-registration
> "I dont think its the restart but maybe the restart agent on ocmc restart is broken?"

**Finding:** After gateway restart, agent sessions are destroyed. MC still has agents in its database but the gateway has no sessions for them. MC marked them as provisioned but the gateway doesn't know about them until the HeartbeatRunner fires (30-90 min) or CRON fires. The template sync during setup re-provisions them but the restart at the end of setup wipes those sessions again.

**Fix required:** After gateway restart, agents must be re-established without waiting for the full heartbeat interval. The orchestrator should handle this — it runs every 30s and can detect when agents need re-registration.

### R3: CRON health and orchestrator sync
> "then there is the CRON, what is the health of all that and the sync with the orchestrator and the pauses and update of CRONs with the budget and the update of brain frequency like it says it does?"

**Finding — CRON health:**
- `~/.openarms/cron/jobs.json` has 3 stale jobs with OLD agent IDs from legacy openclaw
- MC creates CRON jobs via `cron.add` RPC during provisioning, but provisioning failed during restart cascade
- Jobs were never recreated for current agent IDs
- Gateway picks up jobs.json changes without restart (forceReload on every timer tick ~60s)

**Finding — Orchestrator sync with CRON:**
- Orchestrator enables/disables CRON via `enable_gateway_cron_jobs()` / `disable_gateway_cron_jobs()`
- MC reachable → enable. MC down → disable (budget protection)
- Budget mode changes → `update_cron_tempo(multiplier)` modifies `everyMs` in jobs.json

**Finding — Budget influence on frequency:**
- Budget mode "turbo" → tempo_multiplier 0.167 → CRON intervals shrink (faster heartbeats, more work)
- Budget mode "economic" → tempo_multiplier 2.0 → CRON intervals grow (slower heartbeats, less work)
- `update_cron_tempo()` modifies `schedule.everyMs` in jobs.json, preserves `baseEveryMs` for future changes
- Gateway picks up changes within 60s

**Fix required:**
- CRON jobs must be recreated for current agent IDs during setup
- The orchestrator must trigger CRON recreation when it detects stale/missing jobs
- Budget mode changes must propagate to BOTH cron intervals AND orchestrator cycle behavior

### R4: Vendor compatibility (openclaw AND openarms)
> "you have to think of the sync with openclaw and openarms"

**Finding:** The `_resolve_cron_path()` function checks vendor dir first, then falls back to `~/.openclaw/cron/jobs.json` and `~/.openarms/cron/jobs.json`. With openarms active, it correctly resolves to `~/.openarms/cron/jobs.json`. But the jobs in that file are stale copies from the legacy openclaw install.

**Fix required:**
- All keepalive and CRON management code must work with BOTH vendors
- `resolve_vendor_config()`, `resolve_vendor_dir()`, `resolve_vendor_client_id()` are already in place
- CRON path resolution via `_resolve_cron_path()` already handles both
- The gateway (openarms or openclaw) reads from the same file — the fix is in the fleet IaC, not the vendor

### R5: Budget mode influence
> "you have to keep in mind what I said about budget and its influence"

**Finding — What budget mode SHOULD control:**
1. **CRON job intervals** — how often agents heartbeat (via `update_cron_tempo()`) ✓ implemented
2. **Orchestrator cycle speed** — how often the orchestrator runs ✗ NOT implemented (hardcoded 30s)
3. **Heartbeat frequency** — how often `last_seen_at` is touched ✗ NOT implemented
4. **Agent work frequency** — how often agents do actual LLM work ✓ via CRON intervals

**Finding — What budget mode ACTUALLY controls today:**
- Only CRON job intervals (via `update_cron_tempo()`)
- The orchestrator cycle is hardcoded at 30s regardless of budget mode
- `last_seen_at` is never touched by anything continuous
- HeartbeatRunner intervals are read from gateway config, not affected by budget mode changes

**Fix required:**
- Budget mode must affect the keepalive frequency (how often we touch `last_seen_at`)
- In "turbo" mode: more frequent keepalive, faster work
- In "economic" mode: less frequent keepalive, slower work
- BUT: keepalive must never exceed the 10min offline timeout regardless of budget mode

### R6: Work mode pause behavior
> "what if I pause work? what does it do?"
> "pause does not return to full-autonomous, it returns to the value that is selected in the control"

**Finding — UI pause (work_mode dropdown → "work-paused"):**
- Writes `fleet_config.work_mode = "work-paused"` to board
- Orchestrator reads it → `should_dispatch()` returns false → no new tasks dispatched
- Heartbeats keep running (CRON not disabled)
- Agents stay online (if keepalive is working)

**Finding — CLI pause (`fleet pause`):**
- Kills all processes, disables CRON, writes `.fleet-paused` marker
- Updates MC fleet_config with `work_mode: "work-paused"` and saves `work_mode_before_pause`
- Complete stop — agents go offline after 10min

**Finding — Resume:**
- CLI: restores `work_mode` from `work_mode_before_pause` ✓ implemented
- UI: changing dropdown while paused updates `work_mode_before_pause` ✓ implemented

**Fix required:** When keepalive is implemented, UI pause should keep agents online (visible in OCMC) but not doing work. CLI pause is a hard stop — agents going offline is correct.

### R7: OCMC board pause button
> "what I want is that when I pause the native ocmc per fleet button we actually respect it and do the missing pieces and when it unpauses we do the missing pieces"
> "There is a global fleet control... the OCMC pause button is per-board"

**Finding:**
- OCMC pause button sends `/pause` to board memory, broadcasts to agents
- Orchestrator checks `is_board_paused()` → blocks dispatch ✓ implemented
- Agents receive `/pause` as chat message but don't parse it
- Resume: orchestrator detects `/resume` in board memory → unblocks dispatch
- Does NOT affect fleet control bar's work_mode — independent controls

**Fix required:** Board pause already blocks dispatch (Task 4 of the evolution plan). The keepalive mechanism must keep agents online even when board is paused — they're paused, not dead.

## Architecture: The Fix

### Layer 1: Orchestrator Keepalive (touches last_seen_at)

The orchestrator runs every 30s. Each cycle it already talks to MC. Add a lightweight keepalive step:

```python
# Every orchestrator cycle:
# 1. Read fleet state from board (already does this)
# 2. Touch last_seen_at for all agents via MC heartbeat API
# 3. Check board pause state (already does this)
# 4. If not paused: dispatch tasks (already does this)
```

The keepalive ALWAYS runs (even when paused) because agents should stay visible in OCMC. Only CLI hard-pause (kills orchestrator) makes agents go offline.

Budget mode influence: the orchestrator cycle speed itself could be adjusted by budget mode. In "economic" mode, the cycle runs less often. But keepalive must always stay within the 10min timeout.

### Layer 2: CRON Job Health (agent work frequency)

CRON jobs control when agents do actual LLM work. They need to:
- Have correct agent IDs matching current MC agents
- Be recreated during setup via template sync
- Respond to budget mode tempo changes via `update_cron_tempo()`
- Be enabled/disabled by the orchestrator based on MC health and pause state

The setup IaC must ensure CRON jobs are valid after every run. The orchestrator should detect stale CRON jobs and trigger recreation.

### Layer 3: Vendor Compatibility

All of this works with both openclaw and openarms because:
- `_resolve_cron_path()` handles both vendor dirs
- MC client uses `resolve_vendor_config()` for config paths
- Gateway client uses `resolve_vendor_client_id()` for RPC calls
- The keepalive calls MC's REST API (vendor-independent)

## Files to Modify

| File | Change |
|------|--------|
| `fleet/cli/orchestrator.py` | Add keepalive step: batch heartbeat API call for all agents each cycle |
| `fleet/infra/mc_client.py` | Add `batch_heartbeat(agent_ids)` method |
| `gateway/setup.py` | Ensure CRON jobs are valid after provisioning (trigger template sync) |
| `scripts/setup-mc.sh` | Verify CRON job health after setup |
| `fleet/core/budget_modes.py` | Add orchestrator cycle multiplier (not just CRON tempo) |

## Verification

After implementation:
1. Run `./setup.sh` → agents online → wait 15 min → agents still online
2. Change budget mode to "turbo" → CRON intervals shrink → heartbeats fire faster
3. Change budget mode to "economic" → CRON intervals grow → heartbeats fire slower
4. Pause via UI dropdown → agents stay online, no new work dispatched
5. Pause via OCMC button → agents stay online, no new work dispatched for that board
6. CLI `fleet pause` → everything stops, agents go offline (correct)
7. CLI `fleet resume` → agents come back online, work_mode restored from before_pause
8. Works identically with openclaw vendor and openarms vendor
