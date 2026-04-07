# Chunk 9: Validation & Deployment

**Date:** 2026-04-07
**Status:** Planning
**Part of:** [tools-system-session-index.md](tools-system-session-index.md) — Chunk 9 of 9
**Depends on:** ALL previous chunks (this is the final verification)
**Blocks:** Live fleet operation with proper tooling

---

## What This Chunk Accomplishes

End-to-end validation that the entire tools system works: configs are accurate, generation produces correct output, deployment reaches workspaces, agents receive their complete capability surface, and one agent can actually USE the tools as documented.

This is the bridge between "tools system built" and "tools system live."

---

## Step 1: Config Validation

Verify every config file is internally consistent and cross-referenced:

### tool-chains.yaml
- Every tool in tools.py has an entry
- Every chain description matches what the tool actually fires (cross-check with event_chain.py builders + tools.py wiring)
- No aspirational descriptions (every documented chain actually works)

### tool-roles.yaml
- Every listed tool exists in tools.py
- Per-role tool sets match fleet-elevation/24 role × tool matrix
- usage and when descriptions match actual tool behavior
- No roles missing, no roles with wrong tools

### agent-tooling.yaml
- Every MCP server package verified available (Chunk 2)
- Every plugin verified installed (Chunk 2)
- Every skill verified as existing SKILL.md (Chunk 3+4)
- No stale entries (removed plugins that can't be sourced, updated skill names)

### agent-crons.yaml
- Every CRON references a valid standing order
- Schedule expressions are valid
- Model/thinking settings are appropriate per operation
- Budget gates configured

### skill-stage-mapping.yaml
- Every listed skill exists as SKILL.md
- Every stage has appropriate skills
- Per-role overrides make sense
- No skills listed that don't exist

### methodology.yaml
- Stage names match what's used everywhere else
- tools_blocked lists are accurate
- Readiness ranges cover 0-100 without gaps

---

## Step 2: Generation Validation

Run `make generate-tools` and verify output for ALL 10 agents:

### Per-Agent TOOLS.md Checks

For each of the 10 generated TOOLS.md files:

**Format compliance (per tools-agents-standard.md):**
- [ ] Fleet MCP Tools section exists with What/When/Chain/Input/"You do NOT need to"
- [ ] MCP Servers section exists with role-specific servers
- [ ] Skills section exists organized by methodology stage
- [ ] Only tools this role uses (no fleet_approve for engineer, no fleet_plane_status for QA)
- [ ] Only skills that exist as SKILL.md files
- [ ] No concern mixing (no rules, no identity, no dynamic data)

**Accuracy checks:**
- [ ] Chain descriptions match what actually fires (spot-check 3 tools per role)
- [ ] MCP servers listed match per-agent mcp.json
- [ ] Skills listed match what's available in agent's workspace
- [ ] CRONs listed match agent-crons.yaml
- [ ] Sub-agents listed match .claude/agents/ definitions

**Size check:**
- [ ] Each TOOLS.md fits within gateway injection limits
- [ ] Total skill injection (TOOLS.md + skills from all sources) within 150 skill / 30K char limits

---

## Step 3: Deployment Validation

Verify the full deployment pipeline delivers everything to workspaces:

### Per-Agent Workspace Verification

For each agent workspace (workspace-mc-{uuid}):

**Files present:**
- [ ] .mcp.json — per-agent (not template) with role-specific MCP servers
- [ ] SOUL.md — combined (SOUL + STANDARDS + MC_WORKFLOW)
- [ ] CLAUDE.md — role-specific rules
- [ ] HEARTBEAT.md — role-specific action protocol
- [ ] TOOLS.md — generated, per-role, all 7 layers
- [ ] IDENTITY.md — if gateway reads it (verify injection)
- [ ] .claude/settings.json — permissions, effort, hooks
- [ ] .claude/skills/ — symlinked to fleet workflow skills
- [ ] .agents/skills/ — symlinked to gateway operation skills
- [ ] .claude/agents/ — sub-agent definitions (if role has custom)
- [ ] context/ — directory exists (brain writes at runtime)

**Plugins installed:**
- [ ] claude-mem (all agents)
- [ ] safety-net (all agents)
- [ ] Role-specific plugins (per agent-tooling.yaml)

**MCP servers responding:**
- [ ] fleet MCP server responds to tool list query
- [ ] Role-specific MCP servers respond (filesystem, github, etc.)

---

## Step 4: Live Smoke Test

Pick ONE agent (suggestion: software-engineer — most complete capability surface) and verify end-to-end:

### Test 1: Gateway Reads Files Correctly
- Start the agent's heartbeat
- Verify TOOLS.md content appears in the agent's system prompt
- Verify role-specific MCP servers are available to the agent
- Verify skills from plugins are available

### Test 2: Fleet Tools Work With Chains
- Agent calls fleet_commit → verify chain fires (MC comment, Plane comment, trail)
- Agent calls fleet_chat → verify chain fires (Plane propagation, trail)
- Agent calls fleet_task_progress → verify chain fires (Plane, IRC at checkpoint)

### Test 3: Skills Invocable
- Agent invokes a superpowers skill (e.g., brainstorming or writing-plans)
- Verify skill instructions appear in context
- Agent follows skill procedure

### Test 4: MCP Servers Work
- Agent uses filesystem MCP to read a file
- Agent uses github MCP to check PR status (if applicable)

### Test 5: Sub-Agents Spawn
- Agent spawns a sub-agent (e.g., code-reviewer from superpowers)
- Sub-agent completes and returns results

This is NOT a full fleet test (that's path-to-live Phase D). This is a smoke test that the tools system works for one agent.

---

## Step 5: Documentation Update

After validation:

### Update tools-system-session-index.md
- Mark all 9 chunks complete
- Document final state: what was built, what was deferred, what worked, what needs follow-up

### Update STATUS-TRACKER.md
- Update MCP Tools status
- Update Agent Tooling status
- Note what's verified vs what's designed-only

### Update MASTER-INDEX.md
- Update relevant milestones (M48-M52 skills, M81-M86 foundation, etc.)

### Update path-to-live.md
- Phase B Step 9 (Generate TOOLS.md + AGENTS.md) — status update
- Phase C steps related to chain wiring — status update

---

## Verification Criteria (Meta)

This chunk's verification criteria ARE the verification criteria for the entire tools system:

- [ ] Every config file internally consistent and cross-referenced
- [ ] 10 agents' TOOLS.md generated with all 7 layers, per-role filtered
- [ ] 10 agent workspaces have all files deployed correctly
- [ ] At least 1 agent smoke-tested end-to-end (tools, chains, skills, MCP, sub-agents)
- [ ] Documentation updated to reflect actual state
- [ ] No aspirational documentation (everything documented actually works)

---

## Outputs

| Output | Description |
|--------|-------------|
| Validation report | Per-config, per-agent, per-workspace verification results |
| Smoke test results | End-to-end test of one agent's capability surface |
| Updated session index | All chunks marked complete |
| Updated STATUS-TRACKER.md | Reflects new verified state |
