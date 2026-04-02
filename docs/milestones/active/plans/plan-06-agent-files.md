# Plan 06 — Agent Files

**Phase:** 6 (depends on ALL above — agent files reference real capabilities)
**Source:** Synthesis implementation order, all analyses
**Milestone IDs:** I-047 to I-066, B1, B2, B4

---

## What This Plan Delivers

The actual agent files (70+) written from REAL, verified, documented
capabilities. Not from imagination — from the knowledge map, the
installed plugins, the deployed skills, the configured MCP servers,
the implemented hooks.

**This is LAST because every line in an agent file references
something that must exist first.**

---

## Why Last

| CLAUDE.md references | Must exist first |
|---------------------|-----------------|
| Skills (/feature-implement, /TDD) | Plan 02 (skills deployed) |
| Commands (/debug, /plan, /compact) | Analysis 04 (commands mapped) |
| MCP tools (fleet_contribute, Trivy) | Plan 03 (MCP deployed) |
| Tool chains (fleet_task_complete → 12 ops) | Knowledge map tool manuals |
| Anti-corruption rules | Plan 01 (safety-net), Plan 04 (hooks) |
| Stage protocol | Methodology manual |
| Contribution matrix | Knowledge map agent manuals |

Writing CLAUDE.md before these exist = referencing things that don't work.
Writing CLAUDE.md after = referencing verified, tested capabilities.

---

## Build Order

### Step 1: agent.yaml × 10 (B4, 2-4h)

**Standard:** agent-yaml-standard.md (14 required fields)
**Source:** agent-manuals.md (mission, capabilities per role)
**IaC:** scripts/provision-agent-files.sh from agent-identities.yaml

Per agent: name, display_name, fleet_id, fleet_number, username,
type, mode, backend, model, mission, capabilities, roles.primary,
roles.contributes_to, heartbeat_config.every

### Step 2: IDENTITY.md × 10 (3-5h)

**Standard:** identity-soul-standard.md (4 required sections)
**Source:** agent-manuals.md (mission, specialty, personality, place in fleet)
**IaC:** scripts/provision-agent-files.sh from template + identity config

### Step 3: SOUL.md × 10 (3-5h)

**Standard:** identity-soul-standard.md (5 required sections)
**Source:** fleet-elevation/20 (10 anti-corruption rules — EXACT TEXT)
**IaC:** scripts/provision-agent-files.sh

### Step 4: CLAUDE.md × 10 (20-40h — HEAVIEST)

**Standard:** claude-md-standard.md (8 sections, 4000 chars max)
**Source:** agent-manuals.md + methodology-manual.md + analysis 01-05
**Per role:** fleet-elevation/05-14

Each CLAUDE.md must include:
1. Core Responsibility (1 sentence from agent manual)
2. Role-Specific Rules (from fleet-elevation role spec)
3. Stage Protocol (from methodology-manual.md)
4. Tool Chains (from tool call trees, verified in Plan 03)
5. Contribution Model (from cross-references.yaml)
6. Boundaries (from agent manual key rules)
7. Context Awareness (from analysis 04 — commands per stage)
8. Anti-Corruption (summary from SOUL.md — exact text)

### Step 5: HEARTBEAT.md × 5 types (5-10h)

**Standard:** heartbeat-md-standard.md
**Source:** agent-manuals.md (wake triggers, stage behavior, tool chains)
**5 types:** PM, fleet-ops, architect, devsecops, worker (6 variants)

### Step 6: TOOLS.md × 10 (generated)

**Via:** scripts/generate-tools-md.sh
**Content:** Chain-aware tool reference per role (from tool call trees)
**Enhanced:** includes per-stage tool recommendations from methodology-manual.md

### Step 7: AGENTS.md × 10 (generated)

**Via:** scripts/generate-agents-md.sh
**Content:** Synergy matrix per role (from cross-references.yaml)

---

## Quality Gate

Every agent file validated by `scripts/validate-agents.sh` before commit:
- Char limits (CLAUDE.md ≤ 4000)
- Required sections present
- No concern mixing (identity not in CLAUDE.md, rules not in HEARTBEAT.md)
- References match reality (tool names exist, skills deployed, contributions match matrix)
- Fleet identity consistent across files

---

## Validation Checklist

- [ ] agent.yaml × 10 with all 14 fields
- [ ] IDENTITY.md × 10 with 4 sections + top-tier language
- [ ] SOUL.md × 10 with exact 10 anti-corruption rules + per-role values
- [ ] CLAUDE.md × 10 with 8 sections under 4000 chars
- [ ] HEARTBEAT.md × 5 types covering all 10 agents
- [ ] TOOLS.md × 10 generated with chain-aware content
- [ ] AGENTS.md × 10 generated with synergy matrix
- [ ] validate-agents.sh passes for all 10 agents (0 FAIL)
- [ ] Every tool/skill/command referenced in CLAUDE.md actually exists and is deployed
