# Chunk 1: Complete Fleet Group Call Chain Wiring

**Date:** 2026-04-07
**Status:** Planning
**Part of:** [tools-system-session-index.md](tools-system-session-index.md) — Chunk 1 of 9
**Blocks:** tool-chains.yaml from scratch, tool-roles.yaml validation, TOOLS.md fleet tools section
**Depends on:** Nothing (chain infrastructure exists)

---

## What This Chunk Accomplishes

Every fleet MCP tool that modifies state should fire a tree of operations across surfaces via ChainRunner. Today, 1 of 16 state-modifying tools uses ChainRunner (fleet_task_complete). After this chunk, ALL state-modifying tools fire trees. Read-only tools (fleet_read_context, fleet_agent_status, fleet_artifact_read, fleet_task_context, fleet_heartbeat_context) don't need trees.

Once ALL trees fire, tool-chains.yaml can be written FROM SCRATCH with accurate chain descriptions. Until then, any chain documentation is aspirational.

---

## Current State (What's Already Done This Session)

### ChainRunner — 3 new handler actions added
- INTERNAL: update_custom_fields ✓
- PLANE: update_labels ✓
- PLANE: create_issue ✓

### event_chain.py — 8 new builders added
- build_comment_chain (fleet_chat) ✓
- build_accept_chain (fleet_task_accept) ✓
- build_commit_chain (fleet_commit) ✓
- build_task_create_chain (fleet_task_create) ✓
- build_pause_chain (fleet_pause) ✓
- build_escalation_chain (fleet_escalate) ✓
- build_progress_chain (fleet_task_progress) ✓
- build_artifact_chain (fleet_artifact_create/update) ✓

### tools.py — 9 tools wired
- fleet_alert (existing builder, now wired) ✓
- fleet_chat (new builder, wired) ✓
- fleet_commit (new builder, wired) ✓
- fleet_task_accept (new builder, wired) ✓
- fleet_task_progress (new builder, wired) ✓
- fleet_pause (new builder, wired) ✓
- fleet_escalate (new builder, wired) ✓
- fleet_task_create (new builder, wired) ✓
- fleet_artifact_create + fleet_artifact_update (new builder, wired) ✓

### Builders imported verified
All 16 builders (8 existing + 8 new) import and produce valid EventChains. ✓

---

## What Remains

### 4 existing builders need wiring into their tools

| Builder | Tool | Current State of Tool | What's Needed |
|---------|------|----------------------|---------------|
| build_contribution_chain | fleet_contribute | Does direct calls (MC comment, custom fields, own task done, event, trail, IRC, Plane, mention). Most complete non-chain tool. | Wire through ChainRunner alongside existing logic. Add completeness check. |
| build_rejection_chain | fleet_approve (reject path) | Does direct calls (MC approval, status update, comment, IRC, fix task creation, event). | Wire rejection chain alongside existing logic. |
| build_transfer_chain | fleet_transfer | Does direct calls (MC reassign, comment, trail, mention, Plane, IRC, event). | Wire through ChainRunner. |
| build_gate_request_chain | fleet_gate_request | Does direct calls (MC memory, custom field, ntfy, IRC, trail, event). | Wire through ChainRunner. |

### 1 missing tool needs building

| Tool | Builder | Status |
|------|---------|--------|
| fleet_phase_advance | build_phase_advance_chain (EXISTS) | Tool does NOT exist in tools.py. Defined in tool-roles.yaml for PM. Tree defined in fleet-elevation/24. |

### tool-chains.yaml needs writing FROM SCRATCH

The current tool-chains.yaml was written based on ASPIRATIONAL trees (what SHOULD fire). After all wiring is complete, it needs to be rewritten to document what ACTUALLY fires. This is a complete rewrite, not an update.

Format per tool (from tools-agents-standard.md):
```yaml
tools:
  fleet_tool_name:
    what: "Primary action — one line"
    when: "Stage, conditions — when appropriate"
    chain: "What fires automatically after the call"
    input: "Key parameters"
    auto: "What the agent does NOT need to do manually"
    blocked: "Stage restrictions if any"
```

Every tool needs accurate chain descriptions matching the actual wired trees.

### tool-roles.yaml needs validation

After tool-chains.yaml is accurate:
- Verify each role lists only tools they actually use
- Add fleet_phase_advance to PM
- Verify usage/when descriptions match actual tool behavior
- Remove tools that should be internalized (fleet_plane_comment, fleet_plane_update_issue, fleet_plane_create_issue are being absorbed into chains — but they may still be needed for PM edge cases)

---

## Execution Plan

### Step 1: Wire remaining 4 builders into tools

For each tool:
1. Read current tool implementation
2. Identify where chain execution fits (after primary action)
3. Add ChainRunner construction and chain execution
4. Fill Plane params from task custom fields (same pattern as already-wired tools)
5. Maintain fallback if chain fails (primary action already succeeded)

Order: fleet_contribute → fleet_approve (reject) → fleet_transfer → fleet_gate_request

### Step 2: Build fleet_phase_advance tool

New tool in tools.py:
- Uses build_phase_advance_chain (already exists in event_chain.py)
- Checks phase standards before allowing advancement (phases.check_phase_standards)
- Posts gate request to board memory (tagged po-required)
- Routes to PO via ntfy
- IRC notification
- Trail recording

Parameters: task_id, from_phase, to_phase, evidence
Stage restriction: none (PM can request phase advance at any stage)

### ~~Step 3: Write tool-chains.yaml from scratch~~ → MOVED TO CHUNK 8

**Reason:** tool-chains.yaml documents the COMPLETE tool capability surface across all 7 layers. Writing it with only Layer 1 (chain wiring) done would produce aspirational content — the exact problem we're solving. It belongs in Chunk 8 (generation pipeline) after Chunks 2-7 produce the data it needs to document.

### ~~Step 4: Validate tool-roles.yaml~~ → MOVED TO CHUNK 8

**Reason:** Same — tool-roles.yaml drives the generation pipeline. It needs all layers ready before it can be validated comprehensively. fleet_phase_advance addition noted for Chunk 8.

### Step 3 (renumbered): Tests

Per the existing test patterns (test_event_chain.py, test_chain_runner.py):

**New builder tests:**
- Each of the 8 new builders produces correct events per surface
- Trail events always present
- Plane events have empty issue_id/project_id (filled by caller)
- Progress chain includes IRC at 50% and 90%
- Comment chain includes ntfy for PO mentions

**Wiring integration tests:**
- Mock MC/IRC/Plane clients
- Call each tool function
- Verify ChainRunner.run() is called
- Verify chain has expected events
- Verify primary action succeeds even if chain fails

**tool-chains.yaml validation:**
- Each tool in tools.py has an entry in tool-chains.yaml
- Each entry has all required fields (what, when, chain, input)
- chain field matches what the tool actually produces (cross-check with event_chain.py)

### Step 4 (renumbered): Update session index

Mark Chunk 1 complete in tools-system-session-index.md.

---

## Verification Criteria

- [ ] All 13 state-modifying tools fire trees via ChainRunner
- [ ] fleet_phase_advance tool exists and works
- [ ] All existing tests pass (zero regressions)
- [ ] New tests cover new builders and wiring
- [ ] Every chain records trail events (accountability-generator can reconstruct)
- [ ] Plane propagation fires when task has linked issue, skips gracefully when not
- [ ] IRC notifications reach correct channels
- [ ] ntfy fires for appropriate severity/mention conditions

**Deferred to Chunk 8:**
- [ ] tool-chains.yaml covers ALL tools with ACCURATE chain descriptions
- [ ] tool-roles.yaml validated — every role has correct tool set

---

## What This Does NOT Cover

- tool-chains.yaml and tool-roles.yaml are CONFIG for the generation pipeline. The generation pipeline itself (generate-tools-md.sh rewrite) is Chunk 8.
- Skills, CRONs, sub-agents, hooks are Layers 4-7 (Chunks 3-7).
- Plugin/MCP server verification is Chunk 2.
- Per-role TOOLS.md content is the OUTPUT of Chunk 8 after all layers are ready.

This chunk produces ACCURATE CONFIG. The configs are useless without the generation pipeline to consume them — but the generation pipeline is useless without accurate configs to read. This chunk handles the config side for Layer 1.
