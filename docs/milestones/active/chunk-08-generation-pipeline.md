# Chunk 8: TOOLS.md Generation Pipeline Rewrite

**Date:** 2026-04-07
**Status:** Planning
**Part of:** [tools-system-session-index.md](tools-system-session-index.md) — Chunk 8 of 9
**Depends on:** ALL previous chunks (needs accurate data from all 7 layers)
**Blocks:** Chunk 9 (validation and deployment)
**Includes:** Writing tool-chains.yaml from scratch, validating tool-roles.yaml (moved from Chunk 1 — these are generation pipeline inputs, not chain wiring outputs)

---

## What This Chunk Accomplishes

Rewrite generate-tools-md.sh to produce complete per-role TOOLS.md covering ALL 7 capability layers. The generated TOOLS.md is the agent's complete capability reference — injected at position 4 in the autocomplete chain. It must be TRUTHFUL (only documents what actually works) and COMPLETE (covers everything the agent can do).

After this chunk: running `make generate-tools` produces accurate, comprehensive, per-role TOOLS.md files.

---

## Current State of generate-tools-md.sh

The script currently reads:
1. **fleet/mcp/tools.py** — extracts tool function names (fleet_*)
2. **config/tool-chains.yaml** — chain docs per tool (what/when/chain/input/auto/blocked)
3. **config/agent-tooling.yaml** — MCP servers and skills per role

It produces:
- Fleet MCP Tools section — ALL tools for ALL agents (no role filtering)
- MCP Servers section — role-specific from config
- Skills section — role-specific from config (lists names only, doesn't verify they exist)

### Problems with Current Output

1. **No role filtering** — every agent sees every fleet tool (architect sees fleet_approve, engineer sees fleet_plane_status)
2. **Chain descriptions may be aspirational** — tool-chains.yaml may describe trees that don't fire until Chunk 1 is complete
3. **Skills listed but don't exist** — config lists skill NAMES but SKILL.md files may not exist
4. **No plugins section** — plugin-bundled skills and sub-agents not documented
5. **No CRONs section** — scheduled operations not documented
6. **No sub-agents section** — available sub-agents not documented
7. **No stage-aware recommendations** — no "at this stage, use these skills"
8. **No hooks section** — what hooks are active not documented
9. **tool-chains.yaml is aspirational** — needs rewriting from scratch (Chunk 1 Step 3)

---

## What The Rewritten Script Needs to Read

| Source | What It Provides | Layer |
|--------|-----------------|-------|
| fleet/mcp/tools.py | Fleet tool function names | 1 |
| config/tool-chains.yaml | Chain docs per fleet tool (AFTER Chunk 1 rewrite) | 1 |
| config/tool-roles.yaml | Per-role fleet tool assignments with usage/when | 1 |
| config/agent-tooling.yaml | MCP servers, plugins, skills per role | 2, 3, 4 |
| config/agent-crons.yaml | Scheduled operations per role (AFTER Chunk 5) | 5 |
| config/skill-stage-mapping.yaml | Stage-to-skill mapping (AFTER Chunk 3) | 4 |
| config/methodology.yaml | Stage names for section headers | 4 |
| .claude/skills/*/SKILL.md | Verify skills exist (only list existing ones) | 4 |
| .agents/skills/*/SKILL.md | Verify gateway skills exist | 4 |
| agents/{name}/.claude/agents/*.md | Sub-agent definitions per role (AFTER Chunk 6) | 6 |

### Config Dependencies

| Config | Created/Updated By | Status |
|--------|-------------------|--------|
| tool-chains.yaml | Chunk 1 Step 3 (from scratch) | NEEDS REWRITE |
| tool-roles.yaml | Chunk 1 Step 4 (validation) | EXISTS, NEEDS VALIDATION |
| agent-tooling.yaml | Chunk 2 (verification), Chunk 3-4 (skills update) | EXISTS, NEEDS UPDATES |
| agent-crons.yaml | Chunk 5 | TO CREATE |
| skill-stage-mapping.yaml | Chunk 3 Step 5 | TO CREATE |
| methodology.yaml | Already accurate | EXISTS |

---

## Target TOOLS.md Format

Per tools-agents-standard.md plus new sections for layers 2-7:

```markdown
# Tools — {Display Name}

## Fleet MCP Tools

### fleet_read_context
**What:** Load full task and project context
**When:** FIRST call every session — before any decision or work
**Chain:** none (read-only)
**Input:** (none)

### fleet_commit
**What:** Commit files with conventional message
**When:** Work stage ONLY — each logical change gets one commit
**Chain:** git add + commit → MC comment → Plane comment → trail → methodology verify
**Input:** files (list of paths), message (conventional format)
**You do NOT need to:** Post commit summary, update Plane, record trail
**BLOCKED outside work stage**

[... only tools this role uses, per tool-roles.yaml ...]

## MCP Servers

- fleet (all fleet tools)
- filesystem — read/write project files
- github — PR management, CI status, branch operations

[... only this role's servers, per agent-tooling.yaml ...]

## Plugins

- superpowers — TDD, debugging, planning, verification, code review (14 skills)
- context7 — up-to-date library/framework documentation

[... only this role's plugins, per agent-tooling.yaml ...]

## Skills

### Methodology Skills (available at all stages)
- /brainstorming — Socratic design exploration (superpowers)
- /fleet-communicate — which surface for what communication

### At CONVERSATION Stage
- /brainstorming — explore requirements before committing to approach

### At ANALYSIS Stage
- /systematic-debugging — 4-phase root cause analysis (superpowers)
- /fleet-security-audit — structured security review (if security task)

### At INVESTIGATION Stage
- /adversarial-spec — multi-LLM debate for option comparison

### At REASONING Stage
- /writing-plans — detailed implementation roadmap (superpowers)

### At WORK Stage
- /test-driven-development — RED-GREEN-REFACTOR (superpowers)
- /verification-before-completion — verify before claiming done (superpowers)
- /fleet-commit — conventional commit workflow

[... only skills that EXIST as SKILL.md files, per agent-tooling.yaml + skill-stage-mapping.yaml ...]

## Scheduled Operations (CRONs)

- Daily standup summary (09:00 weekdays) — per standing orders
- Backlog grooming session (weekly) — per standing orders

[... only this role's CRONs, per agent-crons.yaml ...]

## Sub-Agents

- code-explorer — read-only codebase navigation (sonnet, filesystem + grep)
- code-reviewer — senior code review: plan alignment, quality (superpowers)

[... only this role's sub-agents, per .claude/agents/ + plugins ...]
```

---

## Script Architecture

### Input Processing

```bash
# 1. Read all config files
# 2. For the target agent:
#    a. Get role from config (architect, engineer, etc.)
#    b. Get fleet tools from tool-roles.yaml (only this role's tools)
#    c. Get chain docs from tool-chains.yaml
#    d. Get MCP servers from agent-tooling.yaml
#    e. Get plugins from agent-tooling.yaml
#    f. Get skills from agent-tooling.yaml (VERIFY each exists as SKILL.md)
#    g. Get CRONs from agent-crons.yaml
#    h. Get sub-agents from agents/{name}/.claude/agents/
#    i. Get stage mapping from skill-stage-mapping.yaml
#    j. Get stage names from methodology.yaml
```

### Output Generation

```bash
# For each section:
# 1. Fleet MCP Tools — filtered by role, with chain docs from tool-chains.yaml
# 2. MCP Servers — from agent-tooling.yaml
# 3. Plugins — from agent-tooling.yaml (list what each provides)
# 4. Skills — organized by stage (from skill-stage-mapping.yaml),
#             ONLY skills that exist as SKILL.md files
# 5. CRONs — from agent-crons.yaml (summary of scheduled operations)
# 6. Sub-Agents — from .claude/agents/ + plugin-provided
```

### Verification During Generation

The script should VERIFY, not assume:
- Each fleet tool name matches a function in tools.py
- Each skill name matches a SKILL.md file in one of the 5 skill sources
- Each MCP server is listed in the per-agent mcp.json
- Each CRON is listed in agent-crons.yaml
- Each sub-agent definition file exists

If something is in config but doesn't actually exist, the script should WARN (not silently include it).

---

## What tool-chains.yaml Must Contain (Post Chunk 1)

EVERY fleet tool with accurate chain descriptions:

**State-modifying tools (16) — each needs chain description:**
fleet_read_context, fleet_task_accept, fleet_task_progress, fleet_commit, fleet_task_complete, fleet_task_create, fleet_alert, fleet_pause, fleet_escalate, fleet_notify_human, fleet_chat, fleet_approve, fleet_contribute, fleet_request_input, fleet_gate_request, fleet_transfer, fleet_artifact_create, fleet_artifact_update, fleet_phase_advance

**Read-only tools (5) — chain: "none (read-only)":**
fleet_agent_status, fleet_task_context, fleet_heartbeat_context, fleet_artifact_read, fleet_plane_status

**Infrastructure tools (4) — kept for PM/writer:**
fleet_plane_sprint, fleet_plane_sync, fleet_plane_list_modules, fleet_plane_create_issue (if not fully internalized)

**Internalized tools (2-3) — documented as "handled by chains":**
fleet_plane_comment → part of comment propagation chains
fleet_plane_update_issue → part of state propagation chains

---

## What tool-roles.yaml Must Contain (Post Chunk 1)

Per role: ONLY the tools that role uses, with role-specific usage and when descriptions.

Source of truth: fleet-elevation/24 role × tool matrix.

Validation: cross-check every listed tool against tools.py. Remove tools that don't exist. Add fleet_phase_advance for PM.

---

## Verification Criteria

- [ ] generate-tools-md.sh reads all 7 layer configs
- [ ] Fleet tools filtered by role (not all tools for all agents)
- [ ] Skills section only lists skills that exist as SKILL.md files
- [ ] Skills organized by methodology stage (per skill-stage-mapping.yaml)
- [ ] CRONs section shows scheduled operations per role
- [ ] Sub-agents section shows available sub-agents per role
- [ ] Plugins section shows what each plugin provides
- [ ] Script warns on config entries that don't match reality
- [ ] Output matches tools-agents-standard.md format requirements
- [ ] Generated TOOLS.md fits within 4000 char gateway limit (or uses extended limit in OpenArms)
- [ ] Running `make generate-tools` produces all 10 agents' TOOLS.md

---

## Outputs

| Output | Description |
|--------|-------------|
| Rewritten scripts/generate-tools-md.sh | Reads all 7 layers, per-role filtering, verification |
| 10 × agents/{name}/TOOLS.md | Complete per-role capability reference |
| Validation report | Warnings for any config/reality mismatches |
