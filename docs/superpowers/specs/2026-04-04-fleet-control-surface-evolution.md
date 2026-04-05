# Fleet Control Surface Evolution

## Summary

Make the fleet control bar a real, operational control surface. Every dropdown reflects actual fleet state, changing a value actually changes fleet behavior, the OCMC native pause button is integrated, and the bidirectional sync between UI and fleet backend is complete.

## Context

The FleetControlBar was built as a UI shell — dropdowns that write to `board.fleet_config` and an orchestrator that reads it. But the sync is incomplete: budget enum values don't match, the progress bar is always 0%, the bar only works on board pages, the fleet CLI pause doesn't update MC, and the OCMC pause button has no effect on fleet dispatch.

This spec makes it all real.

## Requirements

### R1: Control Bar on Every Page

**Current state:** FleetControlBar extracts `boardId` from URL pathname (`pathname.split("/")[2]`). Returns null on non-board pages.

**Required:** The control bar resolves the fleet board ID automatically by querying `GET /api/v1/boards` on mount and finding the fleet board. Uses the existing generated hook `useListBoardsApiV1BoardsGet()`. The `boardId` prop becomes optional — when not provided, the component self-resolves.

**Files:**
- `patches/0005-FleetControlBar.tsx` — add board auto-resolution
- `patches/0005-fleet-control-bar-shell.patch` — remove pathname-based boardId extraction from DashboardShell

### R2: Work Mode Dropdown — Real State

**Current state:** Defaults to "full-autonomous" on page load. Changing it writes to `fleet_config.work_mode`. Orchestrator reads it and gates dispatch. But `fleet pause` CLI doesn't update MC, so the UI shows "Full Autonomous" when fleet is actually paused.

**Required:**
- On page load, shows the REAL work_mode from `fleet_config`
- If fleet is paused (`.fleet-paused` exists), the orchestrator writes `work_mode: "work-paused"` to `fleet_config` via MC API
- If fleet is resumed, the orchestrator writes back the previous work_mode (stored in `fleet_config.work_mode_before_pause`)
- `fleet pause` CLI updates `fleet_config.work_mode` to `"work-paused"` and saves the current mode to `fleet_config.work_mode_before_pause`
- `fleet resume` CLI restores `fleet_config.work_mode` from `fleet_config.work_mode_before_pause`
- Changing the dropdown in UI while paused: updates `work_mode_before_pause` (the "resume to" value), work_mode stays "work-paused"
- Changing the dropdown in UI while not paused: updates `work_mode` directly

**Files:**
- `fleet/infra/mc_client.py` — add `update_board_fleet_config()` method
- `fleet/cli/pause.py` — update MC fleet_config on pause/resume
- `fleet/cli/orchestrator.py` — write fleet state back to MC each cycle
- `patches/0005-FleetControlBar.tsx` — handle `work_mode_before_pause` in UI

### R3: Budget Mode Dropdown — Enum Fix

**Current state:** UI has: blitz, standard, economic, frugal, survival, blackout. Backend has: turbo, aggressive, standard, economic. Only "standard" and "economic" match. Unknown values silently do nothing.

**Required:**
- UI uses the REAL backend enum: turbo, aggressive, standard, economic
- Labels in UI: "Turbo (5s)", "Aggressive (15s)", "Standard (30s)", "Economic (60s)"
- Changing the dropdown writes to `fleet_config.budget_mode`
- Orchestrator reads it and adjusts CRON tempo via `update_cron_tempo()`
- On page load, shows the real value

**Files:**
- `patches/0005-FleetControlBar.tsx` — replace BUDGET_MODES array
- `fleet/core/budget_modes.py` — no change needed (already correct)

### R4: Cycle Phase Dropdown — Real Effect

**Current state:** Changing it writes to `fleet_config.cycle_phase`. Orchestrator reads it. `get_active_agents_for_phase()` exists in `fleet_mode.py` but isn't consistently used during dispatch.

**Required:**
- On page load, shows the real value
- Changing it writes to `fleet_config.cycle_phase`
- Orchestrator uses `get_active_agents_for_phase()` to filter which agents receive dispatched tasks
- When phase is "planning", only project-manager and architect get work
- When phase is "review", only fleet-ops gets work
- When phase is "execution", all agents get work (no filter)
- Each phase has its own agent filter as defined in `fleet_mode.py:98-105`

**Files:**
- `fleet/cli/orchestrator.py` — integrate `get_active_agents_for_phase()` into dispatch filtering
- `patches/0005-FleetControlBar.tsx` — no change needed (already correct)

### R5: Backend Mode Dropdown — Real Effect

**Current state:** Changing it writes to `fleet_config.backend_mode`. Orchestrator reads it and passes to agent heartbeat context. But no actual backend switching happens.

**Required:**
- On page load, shows the real value
- Changing it writes to `fleet_config.backend_mode`
- UI dropdown simplified to: "Claude", "LocalAI", "Hybrid" (matches current 3 options)
- Backend mode is passed to agents in heartbeat context (already happens)
- The `model_selection.py` module uses `backend_mode` to decide which model to use for each dispatch
- When "localai": route to LocalAI endpoint
- When "claude": route to Claude API (current default)
- When "hybrid": use LocalAI for low-complexity, Claude for high-complexity (existing `model_selection.py` logic)

**Files:**
- `fleet/core/model_selection.py` — respect `backend_mode` from fleet state
- `fleet/cli/orchestrator.py` — pass `backend_mode` to model selection
- `patches/0005-FleetControlBar.tsx` — no change needed (already correct)

### R6: Cost Progress Bar — Real Data

**Current state:** UI reads `fleet_config.cost_used_pct`. Nothing writes this value. Always 0%.

**Required:**
- The orchestrator writes real cost data to `fleet_config.cost_used_pct` each cycle
- Data source: `BudgetMonitor._last_reading.weekly_all_pct` (the 7-day quota usage percentage from Claude OAuth API)
- Written via the new `MCClient.update_board_fleet_config()` method
- UI reads it on page load and shows the real percentage
- Color coding already works: green <70%, amber 70-89%, red >=90%

**Files:**
- `fleet/cli/orchestrator.py` — write `cost_used_pct` from BudgetMonitor to fleet_config
- `fleet/core/budget_monitor.py` — expose `weekly_all_pct` for the orchestrator to read (may already be accessible)
- `patches/0005-FleetControlBar.tsx` — no change needed (already reads and displays it)

### R7: Bidirectional Sync — Fleet Writes Back

**Current state:** UI writes to MC. Fleet reads from MC. Fleet never writes back. One-directional.

**Required:**
- Add `MCClient.update_board_fleet_config(board_id, updates)` — PATCH `/api/v1/boards/{board_id}` with `fleet_config` updates
- The orchestrator writes back to `fleet_config` each cycle:
  - `work_mode` — reflects actual state (paused if `.fleet-paused` exists)
  - `budget_mode` — reflects active budget mode
  - `cost_used_pct` — real quota usage
  - `updated_at` — timestamp
  - `updated_by` — "orchestrator" or "cli"
- The orchestrator does NOT overwrite values set by the user in the UI unless there's a conflict (e.g., fleet paused locally)
- Writes are throttled — at most once per orchestrator cycle (30s), not on every field read

**Files:**
- `fleet/infra/mc_client.py` — add `update_board_fleet_config()` method
- `fleet/cli/orchestrator.py` — write back logic with throttling

### R8: OCMC Native Pause Button — Fleet Integration

**Current state:** The OCMC pause button sends `/pause` to board memory, broadcasts to agents via gateway chat.send, and stores pause state in BoardMemory. The fleet orchestrator never checks this.

**Required:**
- The orchestrator checks board pause state each cycle by querying the latest `/pause` or `/resume` command from board memory
- Add `MCClient.is_board_paused(board_id)` — queries board memory for latest pause/resume command
- If the board is paused via OCMC button, the orchestrator skips dispatch for that board — same as `work_mode == "work-paused"` but at the board level
- When unpaused via OCMC button, the orchestrator resumes dispatching — the fleet control bar's work_mode is respected (whatever it was set to before the pause)
- The OCMC pause button and the fleet control bar work_mode are INDEPENDENT:
  - Fleet control bar "work-paused" = global fleet pause (all boards)
  - OCMC pause button = per-board pause (one board)
  - If fleet is "full-autonomous" but board is paused → no dispatch to that board
  - If fleet is "work-paused" → no dispatch to any board regardless of board pause state

**Files:**
- `fleet/infra/mc_client.py` — add `is_board_paused()` or `get_board_pause_state()`
- `fleet/cli/orchestrator.py` — check board pause state before dispatch
- No MC backend changes needed — the BoardMemory query pattern already exists in `provisioning_db._paused_board_ids()`

### R9: Agents Offline After Setup — Bug Fix

**Current state:** After setup completes, agents are online. 10 minutes later, all offline. Root cause: fleet starts paused → cron jobs disabled → no heartbeats → `OFFLINE_AFTER = timedelta(minutes=10)` expires.

**Required:**
- The `_vendor_stop_legacy()` function in `vendor.sh` must NOT disable cron jobs for the CURRENT vendor — only for the legacy vendor
- After setup completes with fleet paused, heartbeat cron jobs should remain ENABLED so agents stay online
- Budget protection (disabling cron when MC is down) happens in the orchestrator, not during setup
- The `.fleet-paused` marker prevents the orchestrator from DISPATCHING, but heartbeats should still fire to keep agents visible in OCMC

**Alternative:** If heartbeats must be disabled when paused (budget protection), then the UI should show agents as "paused" not "offline" — a display issue. But the simpler fix is: heartbeats fire regardless of pause state, they just don't trigger Claude Code work.

**Files:**
- `scripts/lib/vendor.sh` — fix `_vendor_stop_legacy()` to only disable LEGACY cron, not current
- `fleet/cli/pause.py` — don't disable heartbeat cron on pause (or make it configurable)
- `fleet/infra/gateway_client.py` — review `disable_gateway_cron_jobs()` scope

## Out of Scope

- FleetHealthPanel and FleetEventStream integration (separate feature, not control surface)
- Multi-board fleet control (future — current design works with one fleet board)
- Agent-side /pause handling in Claude Code sessions (the pause message is informational)
- Renaming fleet CLI commands or scripts

## Implementation Notes

- All MC frontend changes are delivered as patches in `patches/`
- The `MCClient.update_board_fleet_config()` method is the key new capability that enables bidirectional sync
- The orchestrator's write-back should be lightweight — a single PATCH call with only changed fields
- Budget mode enum alignment is a UI-only change (rename array values in TSX)
- Board ID auto-resolution in FleetControlBar uses existing generated React Query hooks
