# Fleet Control Surface Evolution — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the fleet control bar a real, operational control surface — every dropdown reflects actual state, changes take effect, bidirectional sync works, OCMC pause is integrated, and agents stay online after setup.

**Architecture:** Add `MCClient.update_board_fleet_config()` for backend→UI writes. Fix the FleetControlBar to auto-resolve board ID and use correct enum values. Wire the orchestrator to write state back each cycle. Integrate OCMC board-level pause into orchestrator dispatch. Fix cron job handling so agents don't go offline.

**Tech Stack:** Python 3.11+ (fleet), TypeScript/React (MC frontend patches), httpx (MC API client)

**Spec:** `docs/superpowers/specs/2026-04-04-fleet-control-surface-evolution.md`

---

## File Structure

**Create:**
- `fleet/infra/fleet_sync.py` — bidirectional sync logic (write fleet state to MC, read board pause state)

**Modify:**
- `fleet/infra/mc_client.py` — add `update_board_fleet_config()` and `is_board_paused()` methods
- `fleet/cli/orchestrator.py` — write state back, check board pause, use cycle phase for agent filtering
- `fleet/cli/pause.py` — update MC fleet_config on pause/resume
- `fleet/core/model_selection.py` — respect backend_mode from fleet state
- `fleet/core/fleet_mode.py` — add `work_mode_before_pause` field
- `patches/0005-FleetControlBar.tsx` — auto-resolve board ID, fix budget enum, handle pause state
- `patches/0005-fleet-control-bar-shell.patch` — remove pathname-based boardId
- `scripts/lib/vendor.sh` — fix cron handling in `_vendor_stop_legacy`
- `fleet/infra/gateway_client.py` — fix `disable_gateway_cron_jobs` scope during pause

---

### Task 1: Add MCClient.update_board_fleet_config()

This is the foundation — everything else depends on it.

**Files:**
- Modify: `fleet/infra/mc_client.py`

- [ ] **Step 1: Add update_board_fleet_config method**

After the `get_board_id()` method (line 427), add:

```python
    async def update_board_fleet_config(self, board_id: str, updates: dict) -> bool:
        """Update fleet_config fields on a board. Merges with existing config.

        Args:
            board_id: The board UUID.
            updates: Dict of fleet_config fields to update (merged, not replaced).

        Returns:
            True if update succeeded.
        """
        try:
            # Read current config to merge
            board = await self.get_board(board_id)
            current = board.get("fleet_config") or {}
            merged = {**current, **updates}
            resp = await self._client.patch(
                f"/api/v1/boards/{board_id}",
                json={"fleet_config": merged},
            )
            return resp.status_code == 200
        except Exception:
            return False

    async def is_board_paused(self, board_id: str) -> bool:
        """Check if a board is paused via OCMC pause button.

        Queries board memory for the latest /pause or /resume command.
        Returns True if the latest command is /pause.
        """
        try:
            resp = await self._client.get(
                f"/api/v1/boards/{board_id}/memory",
                params={"limit": 50, "offset": 0},
            )
            if resp.status_code != 200:
                return False
            data = resp.json()
            items = data.get("items", [])
            # Find the latest /pause or /resume in board memory
            for entry in items:
                content = (entry.get("content") or "").strip().lower()
                if content == "/pause":
                    return True
                if content == "/resume":
                    return False
            return False
        except Exception:
            return False
```

- [ ] **Step 2: Commit**

```bash
git add fleet/infra/mc_client.py
git commit -m "feat: add MCClient.update_board_fleet_config() and is_board_paused()"
```

---

### Task 2: Add work_mode_before_pause to FleetControlState

**Files:**
- Modify: `fleet/core/fleet_mode.py`

- [ ] **Step 1: Add field to dataclass**

In `FleetControlState` (line 48), add `work_mode_before_pause`:

```python
@dataclass
class FleetControlState:
    """Current fleet control state from the board's fleet_config."""
    work_mode: str = "work-paused"
    cycle_phase: str = "execution"
    backend_mode: str = "claude"
    budget_mode: str = "standard"
    work_mode_before_pause: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
```

- [ ] **Step 2: Read it in read_fleet_control**

In `read_fleet_control()` (line 59), add parsing:

```python
def read_fleet_control(board_data: dict) -> FleetControlState:
    config = board_data.get("fleet_config") or {}
    return FleetControlState(
        work_mode=config.get("work_mode", "full-autonomous"),
        cycle_phase=config.get("cycle_phase", "execution"),
        backend_mode=config.get("backend_mode", "claude"),
        budget_mode=config.get("budget_mode", "standard"),
        work_mode_before_pause=config.get("work_mode_before_pause"),
        updated_at=config.get("updated_at"),
        updated_by=config.get("updated_by"),
    )
```

- [ ] **Step 3: Commit**

```bash
git add fleet/core/fleet_mode.py
git commit -m "feat: add work_mode_before_pause to FleetControlState"
```

---

### Task 3: Fleet Pause/Resume Updates MC

**Files:**
- Modify: `fleet/cli/pause.py`

- [ ] **Step 1: Update _pause() to write fleet_config**

After the pause marker write (line 98), add MC update:

```python
    # 6b. Update fleet_config in MC (so UI shows paused)
    try:
        import asyncio as _aio
        from fleet.infra.mc_client import MCClient
        mc = MCClient()
        board_id = await mc.get_board_id()
        if board_id:
            board = await mc.get_board(board_id)
            current_config = board.get("fleet_config") or {}
            current_work_mode = current_config.get("work_mode", "full-autonomous")
            # Save current mode so resume can restore it
            await mc.update_board_fleet_config(board_id, {
                "work_mode": "work-paused",
                "work_mode_before_pause": current_work_mode if current_work_mode != "work-paused" else current_config.get("work_mode_before_pause", "full-autonomous"),
                "updated_at": datetime.now().isoformat(),
                "updated_by": "cli",
            })
            print("   Fleet config updated in MC (work-paused)")
        await mc.close()
    except Exception as e:
        print(f"   WARN: Could not update MC fleet_config: {e}")
```

- [ ] **Step 2: Update _resume() to restore fleet_config**

After removing the pause marker (line 129), add MC update:

```python
    # Restore work_mode from work_mode_before_pause
    try:
        from fleet.infra.mc_client import MCClient
        mc = MCClient()
        board_id = await mc.get_board_id()
        if board_id:
            board = await mc.get_board(board_id)
            current_config = board.get("fleet_config") or {}
            restore_mode = current_config.get("work_mode_before_pause", "full-autonomous")
            await mc.update_board_fleet_config(board_id, {
                "work_mode": restore_mode,
                "work_mode_before_pause": None,
                "updated_at": datetime.now().isoformat(),
                "updated_by": "cli",
            })
            print(f"Fleet config updated in MC (restored to {restore_mode})")
        await mc.close()
    except Exception as e:
        print(f"WARN: Could not update MC fleet_config: {e}")
```

- [ ] **Step 3: Commit**

```bash
git add fleet/cli/pause.py
git commit -m "feat: fleet pause/resume updates MC fleet_config with work_mode"
```

---

### Task 4: Orchestrator Writes State Back + Board Pause Check

**Files:**
- Modify: `fleet/cli/orchestrator.py`

- [ ] **Step 1: Add board pause check after fleet state read**

After line 200 (`_previous_fleet_state = fleet_state`), add:

```python
    # Check OCMC board-level pause (separate from fleet work_mode)
    board_paused = False
    try:
        board_paused = await mc.is_board_paused(board_id)
    except Exception:
        pass
    if board_paused:
        state.notes.append("Board paused via OCMC pause button — dispatch blocked")
        return state
```

- [ ] **Step 2: Add fleet state write-back after mode change detection**

After the mode change detection block (after line 199), add:

```python
    # Write fleet state back to MC (bidirectional sync)
    # Throttled: only writes if something changed or every 10 cycles
    _sync_counter = getattr(_run_cycle, '_sync_counter', 0) + 1
    _run_cycle._sync_counter = _sync_counter
    should_sync = bool(changes_detected) or (_sync_counter % 10 == 0)
    if should_sync:
        try:
            sync_updates = {
                "updated_at": now.isoformat(),
                "updated_by": "orchestrator",
            }
            # Write cost data from budget monitor
            if hasattr(_run_cycle, '_budget_monitor') and _run_cycle._budget_monitor:
                reading = _run_cycle._budget_monitor._last_reading
                if reading:
                    sync_updates["cost_used_pct"] = round(reading.weekly_all_pct, 1)
            await mc.update_board_fleet_config(board_id, sync_updates)
        except Exception:
            pass  # Sync must not break orchestrator
```

- [ ] **Step 3: Integrate cycle phase agent filtering**

In the dispatch section (around the `_dispatch_ready_tasks` call), add phase-based filtering:

```python
    # Filter agents by cycle phase
    from fleet.core.fleet_mode import get_active_agents_for_phase
    phase_agents = get_active_agents_for_phase(fleet_state)
    if phase_agents is not None:
        agent_map = {aid: a for aid, a in agent_map.items() if a.name in phase_agents}
        state.notes.append(f"Phase {fleet_state.cycle_phase}: active agents = {phase_agents}")
```

- [ ] **Step 4: Commit**

```bash
git add fleet/cli/orchestrator.py
git commit -m "feat: orchestrator writes state back to MC, checks board pause, filters by phase"
```

---

### Task 5: Fix Budget Mode Enum in UI

**Files:**
- Modify: `patches/0005-FleetControlBar.tsx`

- [ ] **Step 1: Replace BUDGET_MODES array**

Replace lines 47-54:

```typescript
const BUDGET_MODES = [
  { value: "turbo", label: "Turbo", desc: "5s cycle" },
  { value: "aggressive", label: "Aggressive", desc: "15s cycle" },
  { value: "standard", label: "Standard", desc: "30s cycle" },
  { value: "economic", label: "Economic", desc: "60s cycle" },
];
```

- [ ] **Step 2: Commit**

```bash
git add patches/0005-FleetControlBar.tsx
git commit -m "fix: budget mode enum matches backend (turbo/aggressive/standard/economic)"
```

---

### Task 6: FleetControlBar Auto-Resolves Board ID

**Files:**
- Modify: `patches/0005-FleetControlBar.tsx`
- Modify: `patches/0005-fleet-control-bar-shell.patch`

- [ ] **Step 1: Add board auto-resolution to FleetControlBar**

Replace the `useEffect` at line 70 and the early return at line 150. The component should fetch the board list when no boardId is provided:

After the state declarations (line 67), add:

```typescript
  const [resolvedBoardId, setResolvedBoardId] = useState<string | undefined>(boardId);

  // Auto-resolve board ID if not provided
  useEffect(() => {
    if (boardId) {
      setResolvedBoardId(boardId);
      return;
    }
    if (!isSignedIn) return;

    const resolveBoard = async () => {
      try {
        const resp = await fetch("/api/v1/boards?limit=10&offset=0");
        if (resp.ok) {
          const data = await resp.json();
          const boards = data.items || [];
          // Find the fleet board by name, or use the first one
          const fleet = boards.find((b: any) => b.name === "Fleet Operations") || boards[0];
          if (fleet) {
            setResolvedBoardId(fleet.id);
          }
        }
      } catch {
        // Silent fail
      }
    };

    resolveBoard();
  }, [isSignedIn, boardId]);
```

Then replace all `boardId` references in the component with `resolvedBoardId`, and change the early return:

```typescript
  if (!resolvedBoardId) return null;
```

- [ ] **Step 2: Update fleet_config fetch to use resolvedBoardId**

The existing `useEffect` for fetching config (line 70) should use `resolvedBoardId`:

```typescript
  useEffect(() => {
    if (!isSignedIn || !resolvedBoardId) return;

    const fetchConfig = async () => {
      try {
        const resp = await fetch(`/api/v1/boards/${resolvedBoardId}`);
        // ... rest unchanged
      }
    };

    fetchConfig();
  }, [isSignedIn, resolvedBoardId]);
```

And `updateConfig` should use `resolvedBoardId`:

```typescript
    async (updates: Record<string, string>) => {
      if (!resolvedBoardId || loading) return;
      // ... rest uses resolvedBoardId instead of boardId
```

- [ ] **Step 3: Simplify DashboardShell patch**

Update `patches/0005-fleet-control-bar-shell.patch` — the DashboardShell no longer needs to extract boardId from pathname:

```tsx
<FleetControlBar />
```

No `boardId` prop needed. The component resolves it itself.

- [ ] **Step 4: Handle work_mode_before_pause in UI**

Add logic so that when the user changes the work mode dropdown while paused, it updates `work_mode_before_pause` instead of `work_mode`:

```typescript
  const handleWorkModeChange = (value: string) => {
    if (workMode === "work-paused" && value !== "work-paused") {
      // User selected a mode while paused — update the "resume to" mode
      setWorkModeBeforePause(value);
      updateConfig({ work_mode_before_pause: value });
    } else {
      setWorkMode(value);
      updateConfig({ work_mode: value });
    }
  };
```

Add state for `workModeBeforePause`:

```typescript
  const [workModeBeforePause, setWorkModeBeforePause] = useState<string | null>(null);
```

And read it from config on load:

```typescript
  setWorkModeBeforePause(config.work_mode_before_pause || null);
```

- [ ] **Step 5: Commit**

```bash
git add patches/0005-FleetControlBar.tsx patches/0005-fleet-control-bar-shell.patch
git commit -m "feat: FleetControlBar auto-resolves board ID, handles pause state"
```

---

### Task 7: Backend Mode in Model Selection

**Files:**
- Modify: `fleet/core/model_selection.py`

- [ ] **Step 1: Add backend_mode parameter to select_model_for_task**

Modify the function signature (line 43):

```python
def select_model_for_task(
    task: Task,
    agent_name: str = "",
    backend_mode: str = "claude",
) -> ModelConfig:
```

Add at the start of the function, after docstring:

```python
    # Backend mode override
    if backend_mode == "localai":
        return ModelConfig(
            model="localai",
            effort="medium",
            reason=f"Backend mode: localai",
        )
```

For "hybrid" mode, add after the localai check:

```python
    if backend_mode == "hybrid":
        # Use localai for low-complexity, claude for everything else
        complexity = task.custom_fields.get("complexity", "") if task.custom_fields else ""
        story_points = task.custom_fields.get("story_points", 0) if task.custom_fields else 0
        try:
            story_points = int(story_points)
        except (TypeError, ValueError):
            story_points = 0
        if story_points <= 2 and complexity in ("", "low", "routine"):
            return ModelConfig(
                model="localai",
                effort="medium",
                reason=f"Hybrid mode: low complexity (sp={story_points})",
            )
        # Fall through to normal claude selection for complex tasks
```

- [ ] **Step 2: Pass backend_mode from orchestrator**

In `fleet/cli/orchestrator.py`, where `select_model_for_task` is called, pass the backend_mode:

Find the call site and add `backend_mode=fleet_state.backend_mode`:

```python
model_config = select_model_for_task(task, agent_name=agent.name, backend_mode=fleet_state.backend_mode)
```

- [ ] **Step 3: Commit**

```bash
git add fleet/core/model_selection.py fleet/cli/orchestrator.py
git commit -m "feat: model selection respects backend_mode from fleet control"
```

---

### Task 8: Fix Agents Going Offline After Setup

**Files:**
- Modify: `scripts/lib/vendor.sh`
- Modify: `fleet/cli/pause.py`

- [ ] **Step 1: Fix _vendor_stop_legacy to only disable LEGACY cron**

The current `_vendor_stop_legacy` in `vendor.sh` correctly targets legacy cron (line 128-129 checks `VENDOR_LEGACY_CONFIG_DIR`). Verify it doesn't touch the current vendor's cron.

Check the `start-fleet.sh` — the `_vendor_stop_legacy` call there should not disable the CURRENT vendor's cron. Read the current code and verify.

If `_vendor_stop_legacy` is also called in `start-fleet.sh` and it touches the current vendor's cron, fix it.

- [ ] **Step 2: Fleet pause should NOT disable heartbeat cron**

In `fleet/cli/pause.py`, the `_pause()` function (around line 69) calls `disable_gateway_cron_jobs()`. Heartbeats keep agents visible in OCMC — they don't trigger Claude Code work. Disabling them makes agents disappear.

Remove or comment out the `disable_gateway_cron_jobs()` call in `_pause()`. Heartbeats are cheap (they just POST to MC API, no Claude usage). The budget protection for Claude usage is in the orchestrator dispatch gate (`should_dispatch()`), not in heartbeats.

Find and comment out:

```python
    # Previously: disable_gateway_cron_jobs()
    # Heartbeats are NOT disabled on pause. They keep agents visible in OCMC.
    # Budget protection is handled by the orchestrator dispatch gate.
```

- [ ] **Step 3: Verify cron path resolves to current vendor**

In `fleet/infra/gateway_client.py`, `_resolve_cron_path()` (line 210) calls `resolve_vendor_dir()`. Verify this returns `~/.openarms` when openarms is active, not `~/.openclaw`.

- [ ] **Step 4: Commit**

```bash
git add scripts/lib/vendor.sh fleet/cli/pause.py fleet/infra/gateway_client.py
git commit -m "fix: heartbeats stay enabled on pause, cron targets correct vendor"
```

---

### Task 9: Regenerate FleetControlBar Patch

The FleetControlBar.tsx changes from Tasks 5 and 6 need to be deployed as a fresh patch file since the source of truth is `patches/0005-FleetControlBar.tsx` (copied directly, not a git diff patch).

**Files:**
- Modify: `patches/0005-FleetControlBar.tsx` (already modified in Tasks 5 and 6)
- Modify: `patches/0005-fleet-control-bar-shell.patch`

- [ ] **Step 1: Verify the complete FleetControlBar.tsx**

Read the updated `patches/0005-FleetControlBar.tsx` and verify:
- Board auto-resolution works (fetches from API, finds "Fleet Operations")
- Budget modes are: turbo, aggressive, standard, economic
- work_mode_before_pause is read on load and written on pause-state changes
- All `boardId` references replaced with `resolvedBoardId`

- [ ] **Step 2: Regenerate the DashboardShell patch**

The patch must import FleetControlBar without passing boardId:

```diff
+import { FleetControlBar } from "@/components/fleet-control/FleetControlBar";
...
+              <FleetControlBar />
```

Generate the new patch from the vendor source:

```bash
cd /home/jfortin/openclaw-fleet/vendor/openclaw-mission-control
# Apply the change to DashboardShell.tsx
# Generate diff
git diff -- frontend/src/components/templates/DashboardShell.tsx > /home/jfortin/openclaw-fleet/patches/0005-fleet-control-bar-shell.patch
git checkout -- frontend/src/components/templates/DashboardShell.tsx
```

- [ ] **Step 3: Apply patches and verify**

```bash
cd /home/jfortin/openclaw-fleet
bash scripts/apply-patches.sh
```

Verify the FleetControlBar renders on a non-board page (e.g., the agents page).

- [ ] **Step 4: Commit**

```bash
git add patches/0005-FleetControlBar.tsx patches/0005-fleet-control-bar-shell.patch
git commit -m "feat: FleetControlBar complete — auto board ID, correct enums, pause state, all pages"
```

---

## Summary

| Task | Requirement | Description | Files |
|------|------------|-------------|-------|
| 1 | R7 | MCClient.update_board_fleet_config() + is_board_paused() | mc_client.py |
| 2 | R2 | work_mode_before_pause in FleetControlState | fleet_mode.py |
| 3 | R2 | Fleet pause/resume updates MC fleet_config | pause.py |
| 4 | R7, R8, R4, R6 | Orchestrator writes back, board pause check, phase filter, cost data | orchestrator.py |
| 5 | R3 | Budget mode enum fix | FleetControlBar.tsx |
| 6 | R1, R2 | FleetControlBar auto board ID + pause state handling | FleetControlBar.tsx, shell patch |
| 7 | R5 | Backend mode in model selection | model_selection.py, orchestrator.py |
| 8 | R9 | Fix agents offline — heartbeats stay enabled | vendor.sh, pause.py, gateway_client.py |
| 9 | All | Regenerate and verify patches | patches/ |

**Requirements coverage:**
- R1 (all pages): Task 6
- R2 (work mode real state): Tasks 2, 3, 6
- R3 (budget enum): Task 5
- R4 (cycle phase): Task 4
- R5 (backend mode): Task 7
- R6 (cost bar): Task 4
- R7 (bidirectional sync): Tasks 1, 4
- R8 (OCMC pause): Tasks 1, 4
- R9 (agents offline): Task 8
