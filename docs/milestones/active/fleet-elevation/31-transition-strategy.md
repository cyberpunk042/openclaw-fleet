# Transition Strategy — Elevating a Running Fleet

**Date:** 2026-03-31
**Status:** Design — how to upgrade without breaking what works
**Part of:** Fleet Elevation (document 31)

---

## The Reality

The fleet is LIVE right now:
- OpenClaw gateway running (4.4GB RAM, serving agent sessions)
- Fleet daemon running (all 5 daemons: sync, monitor, orchestrator,
  auth, plane-watcher)
- MC backend running (Docker: backend, frontend, redis, db, webhooks)
- IRC running (miniircd on port 6667)
- The Lounge running (Docker)
- Plane running (Docker: proxy, live, space)
- Effort profile: conservative (after budget drain incident)

10 agents are configured. The orchestrator cycles every 30 seconds.
The sync daemon runs every 60 seconds. Tasks exist on the board.

You cannot take this offline, replace everything, and restart. The
elevation must happen PROGRESSIVELY — each change integrates with
the running system without breaking what works.

---

## Transition Principles

### 1. We Own Everything — No False Compatibility Constraints
This is OUR code. We control every file, every module, every config.
There are no external consumers. The elevation is a REDESIGN — when
we change something, it's changed. The old version is not preserved.

New fields on TaskCustomFields get defaults so existing data parses
correctly (data migration concern, not compatibility concern). But
the code itself UPGRADES. There's no "with or without elevation"
state — the fleet IS the elevated version once we're done.

### 2. Staged Behavioral Rollout
Certain behavioral changes benefit from staged rollout — not because
the old behavior needs preserving, but because we want to VERIFY
each new behavior works before layering the next one on top:

- Contribution creation: verify the brain creates the right tasks
  before enabling fleet-wide
- Phase gate enforcement: verify gates work correctly before they
  start blocking dispatch
- Trail recording: verify trails are recorded correctly before
  accountability generator relies on them

This is TEST-THEN-COMMIT, not backward compatibility. Once verified,
the old behavior is gone.

### 3. Extend, Then Replace
When extending existing modules (event_chain.py, agent_lifecycle.py),
the existing code continues working DURING development. New code
is added alongside. Once verified, old patterns that are superseded
get CLEANED UP — not left as dead code.

### 4. Tests Gate Everything
Before any change goes live:
- All existing tests still pass (or are UPDATED to match new behavior)
- New tests for the change pass
- Live verification against running MC backend

Tests that fail because the behavior CORRECTLY changed get UPDATED
to test the new behavior. Tests aren't sacred — the design is.

### 5. One Phase at a Time
Complete Phase A, verify, THEN start Phase B. The fleet daemons
restart between phases to pick up new code. Each restart is a
clean transition point.

---

## Revised Implementation Order (Backward/Forward Validated)

### Why the Order Changed

**Original order:** A (foundation) → B (brain) → C (contributions) →
D (agent files) → E (standards) → F (governance) → G (multi-fleet)
→ I (lifecycle) → J (tool trees) → K (change management) → H (validation)

**Problem:** Phase I (lifecycle/strategic calls) is near the end, but
budget savings matter from day one. The fleet is on CONSERVATIVE
profile after a drain incident. Content-aware sleep would reduce
costs immediately for idle agents.

**Problem:** Phase J (tool trees) depends on B (brain) but also
VALIDATES A (foundation). It should come earlier to verify the
chain extensions work.

**Problem:** Phase D (agent files) can be done incrementally —
one agent at a time — and doesn't need to wait for contributions.

### Revised Order

```
Phase A  (foundation)     — data model, config
    ↓
Phase A+ (quick wins)     — lifecycle DROWSY state, smart_chains wiring
    ↓
Phase B  (brain core)     — chain registry, logic engine
    ↓
Phase J  (tool trees)     — extend chain builders, upgrade tool trees
    ↓
Phase C  (contributions)  — contribution tasks, propagation
    ↓
Phase D  (agent files)    — one agent at a time, verify each
    ↓
Phase E  (standards)      — phase-aware quality enforcement
    ↓
Phase F  (governance)     — PO gates, readiness regression
    ↓
Phase I  (lifecycle full) — strategic calls, model selection integration
    ↓
Phase G  (multi-fleet)    — identity, attribution (if needed)
    ↓
Phase K  (change mgmt)    — requirement evolution, config versioning
    ↓
Phase H  (validation)     — end-to-end flows, live testing
```

### Phase A+ (Quick Wins) — NEW
Before the heavy brain work, grab easy wins:
- Add DROWSY state to agent_lifecycle.py (small code change,
  immediate cost reduction for idle agents)
- Wire smart_chains.py into the orchestrator (it's already written
  and tested, just never imported)
- Prepare config sections for new elevation features
- These are LOW RISK changes to existing, tested modules

---

## Per-Phase Transition Protocol

Every phase follows the doc 30 structure PLUS transition safety:

```
1. CODE AUDIT
   Read every module you're about to touch.
   Verify current behavior. Run existing tests.

2. BACKWARD DECOMPOSITION
   Define end state for this phase.
   Work backward to specific code changes.

3. FORWARD TRACE + RIPPLE ANALYSIS
   From current code, trace what each change affects.
   Count ripple: how many modules touched?
   Verify no UNINTENDED ripples.

4. TDD
   Write tests for the end state FIRST.
   Tests define what "correct" looks like.
   Run them — they fail (red). That's expected.

5. IMPLEMENT
   Extend existing modules. Follow established patterns.
   One change at a time. Run tests after each change.
   When all tests pass (green) — implementation is done.

6. VERIFY LOCALLY
   All existing tests still pass (updated where behavior changed).
   New tests pass.
   Fleet daemon restarts cleanly with new code.
   Orchestrator cycle completes without errors.

7. LIVE VERIFICATION
   Restart fleet daemon with new code.
   Against running MC backend. Real tasks, real data.
   Monitor: orchestrator logs, budget, health signals.
   If something's wrong: git revert, restart daemon.

8. COMMIT AND DOCUMENT
   Commit with conventional format.
   Update doc 28 (codebase inventory) with changes.
   Update doc 22 (milestones) marking phase complete.
   The change is permanent. Old behavior is gone.
```

---

## Agent File Transition (Phase D — Special Case)

Agent file changes are immediate — the gateway reads them on next
heartbeat. The transition for agent files:

### Strategy: One Agent at a Time

1. Start with the `_template` agent — update template files
2. Update ONE agent (suggest: architect — already has good CLAUDE.md)
3. Verify: gateway reads files correctly, agent behaves as expected
4. If good: update next agent
5. Continue one-by-one until all 10 are done

### CLAUDE.md Merge Strategy

Existing CLAUDE.md is GOOD (67-95 lines). Elevation ADDS sections:

```markdown
# Existing content stays — DO NOT DELETE
{existing role definition, capabilities, standards, collaboration}

# === ELEVATION ADDITIONS ===

## Anti-Corruption Rules
{shared section — all agents get this}

## Contribution Awareness
{role-specific — what this agent contributes and when}

## Phase Awareness
{what delivery phases mean for this agent's work}

## Planning Methodology
{backward/forward thinking for this role}
```

The merge is ADDITIVE. Existing content is preserved. New sections
are appended after a clear marker.

### IDENTITY.md and SOUL.md — Full Rewrite

These are currently generic OpenClaw templates (blank/default).
They need full rewrites — not merges. But verify the gateway reads
them correctly after rewriting.

### TOOLS.md — Full Rewrite

Currently auto-generated lists. Need chain-aware documentation.
Full rewrite is safe — the old content is just tool names.

---

## Risk Assessment Per Phase

| Phase | Risk | Mitigation |
|-------|------|-----------|
| A (foundation) | New fields break _parse_task | Default values on new fields, test parse roundtrip |
| A+ (quick wins) | DROWSY state transitions wrong | Test all transition paths before deploying |
| B (brain core) | Chain registry breaks orchestrator cycle | Test cycle completes with registry wired in |
| J (tool trees) | Extended chains break MCP tools | Test each tool individually before deploying |
| C (contributions) | Contribution tasks flood the board | Config: max contributions per cycle, test with limits |
| D (agent files) | Changed files confuse gateway | One agent at a time, verify gateway reads correctly |
| E (standards) | Phase-aware standards reject valid work | Test with real task data before deploying |
| F (governance) | Gates block dispatch unexpectedly | Test gate logic with real board state |
| I (lifecycle full) | Strategic calls misconfigure sessions | Test model/effort/session decisions with real agents |
| G (multi-fleet) | Naming changes break existing agent sessions | Test with new fleet instance, not existing one |
| K (change mgmt) | Requirement change detection false positives | Conservative detection thresholds, PM review |
| H (validation) | End-to-end tests find integration bugs | Fix bugs, this is EXPECTED — that's what validation is for |

---

## Recovery Plan

If a phase introduces bugs after deployment:

1. **Git revert** — revert the commit(s) that introduced the bug
2. **Daemon restart** — fleet daemon picks up reverted code
3. **Daemon restart** — fleet daemon picks up reverted code
4. **Agent prune** — if agent sessions have corrupted context,
   prune via gateway (sessions.delete) — they regrow clean
5. **Board cleanup** — if bad data was written to MC board,
   use board cleanup tool (board_cleanup.py already exists)

The fleet has self-healing (self_healing.py). Combined with rollback,
recovery from a failed phase should be quick.

---

## Monitoring During Transition

Watch these signals during each phase rollout:

- **Budget:** Is token spend increasing? (budget_monitor.py)
- **Errors:** Are orchestrator cycle errors increasing? (error_reporter.py)
- **Health:** Are agents getting stuck? (health.py)
- **Outages:** Are APIs failing? (outage_detector.py)
- **Cycle time:** Is the orchestrator cycle taking longer? (OrchestratorState.total_actions)

If any signal degrades after deploying a phase → git revert, restart
daemon, investigate, fix, redeploy.

---

## The Conservative Profile

The fleet is currently on CONSERVATIVE profile:
```yaml
effort_profile: conservative
# Budget-conscious — drivers only, sonnet only, less frequent
# max_dispatch_per_cycle: 1
# allow_opus: false
# active_agents: [project-manager, fleet-ops, devsecops-expert]
```

This means during elevation implementation:
- Only 3 agents are active (PM, fleet-ops, DevSecOps)
- Only sonnet model allowed (no opus)
- Max 1 dispatch per cycle
- Heartbeats less frequent

The elevation should be implemented and tested under this profile
first. Then when ready, profile can be changed to "full" to activate
all agents with new elevation features.

---

## Connection to AICP (LocalAI Independence)

The elevation's lifecycle system (doc 23) is the bridge to AICP:

**Current:** Claude for everything. Conservative profile to save budget.
**Elevation:** Sleep/wake lifecycle. Brain evaluates sleeping agents
for free. Claude called strategically.
**AICP Future:** LocalAI handles lightweight wake evaluations. Claude
only for complex cognition. Progressive offload.

The lifecycle implementation creates the infrastructure:
- Content-aware sleep/wake is the fleet's default behavior once
  implemented
- LocalAI light wake is a FUTURE addition — when AICP Stage 2
  makes LocalAI reliable, the lifecycle code adds LocalAI as a
  model option for lightweight evaluations
- Same infrastructure, different model. The code doesn't change —
  the config adds a model option.

---

## Open Questions

- How long should each phase rollout be? (1 day? 1 sprint? Depends
  on phase complexity?)
- Should there be a "canary agent" that gets elevation features first
  before fleet-wide rollout?
- How do we handle the Plane space container being unhealthy?
  (Currently unhealthy — should be fixed before elevation touches Plane sync)
- Should the elevation be tracked as its own sprint in the fleet's
  task management? (Meta: fleet building itself)