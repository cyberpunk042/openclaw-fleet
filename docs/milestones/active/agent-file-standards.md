# Agent File Standards — Master Index

**Date:** 2026-04-01
**Status:** ACTIVE — quality gate for all agent work (B1-B4 and beyond)

---

## PO Requirement (Verbatim)

> "we will have to establish high standards document first for each files /
> modules and templates and make sure that they all respect it and fit as
> an integration and at the right place and properly configured and with a
> strong and reliable IaC and setup"

---

## Per-Type Standards

Each file type has its own deep standard document with exact structure,
per-role content, validation criteria, IaC flow, and integration rules.

| Standard | File | Covers | Injection Position |
|----------|------|--------|-------------------|
| [CLAUDE.md Standard](standards/claude-md-standard.md) | CLAUDE.md | Role-specific rules, 4000 char limit, 8 required sections, per-role content map, annotated example | Position 3 |
| [HEARTBEAT.md Standard](standards/heartbeat-md-standard.md) | HEARTBEAT.md | 5 heartbeat types (PM, fleet-ops, architect, devsecops, worker), priority protocol, stage awareness, per-role work variations | Position 8 (LAST) |
| [agent.yaml Standard](standards/agent-yaml-standard.md) | agent.yaml | 14 required fields, fleet identity, per-role values table, model selection rationale | Gateway config |
| [IDENTITY.md + SOUL.md Standard](standards/identity-soul-standard.md) | IDENTITY.md, SOUL.md | Inner layer, top-tier expert, 10 anti-corruption rules, per-role values, humility, boundary between SOUL and CLAUDE | Positions 1, 2 |
| [TOOLS.md + AGENTS.md Standard](standards/tools-agents-standard.md) | TOOLS.md, AGENTS.md | Chain-aware tool reference (generated), synergy relationships (generated), per-role tool sets, contribution matrix | Positions 4, 5 |
| [context/ Files Standard](standards/context-files-standard.md) | fleet-context.md, task-context.md | Autocomplete chain (10 sections in order), pre-embed structure, per-role data, NEVER compressed | Positions 6, 7 |
| [IaC + MCP Standard](standards/iac-mcp-standard.md) | Scripts, mcp.json, configs | 6 required scripts, idempotent provisioning, config-driven, validate-before-write, Makefile integration | Infrastructure |
| [Brain Modules Standard](standards/brain-modules-standard.md) | fleet/core/ modules | 8 new modules, 13-step orchestrator, chain registry, session management, code standards | Runtime |

---

## How Standards Gate Work

```
Design spec (fleet-elevation)
     ↓ defines WHAT each file should contain
Per-type standard (standards/)
     ↓ defines HOW to validate, exact structure, IaC flow
Template (agents/_template/)
     ↓ implements the standard as a file template
Provisioning (scripts/provision-agents.sh)
     ↓ deploys templates to agent directories
Validation (scripts/validate-agents.sh)
     ↓ verifies all files meet their standard
Gateway injection
     ↓ injects at correct position in system prompt
Agent behavior
     ↓ shaped by the autocomplete chain
```

**No file gets committed without meeting its standard.**
**No agent gets deployed without passing validation.**

---

## Integration Verification

Cross-cutting checks that span multiple standards:

| Check | What It Verifies | Standards Involved |
|-------|-----------------|-------------------|
| No concern mixing | Each file type has its content, no other file's content | All agent file standards |
| Injection order | Files injected in positions 1-8 correctly | All agent file standards |
| Contribution consistency | CLAUDE.md model = AGENTS.md relationships = fleet-elevation/15 matrix | claude-md, tools-agents |
| Tool validity | CLAUDE.md chains + TOOLS.md docs reference real MCP tools | claude-md, tools-agents |
| Config alignment | agent.yaml fields = IDENTITY.md values = mcp.json servers = agent-tooling.yaml | agent-yaml, identity-soul, iac-mcp |
| Context awareness | CLAUDE.md has both countdowns, context/ has both %, brain Step 10 factors both | claude-md, context-files, brain-modules |
| IaC completeness | `make setup` from zero → all files deployed → all validation passes | iac-mcp |

---

## Relationship to Work Backlog

| Backlog Item | Standards Required Before Starting |
|-------------|----------------------------------|
| B1: Agent CLAUDE.md ×10 | claude-md-standard.md |
| B2: Agent HEARTBEAT.md ×5 | heartbeat-md-standard.md |
| B3: Template files deployed | iac-mcp-standard.md |
| B4: Agent.yaml updates | agent-yaml-standard.md |
| H1: Contribution flow | brain-modules-standard.md (contributions.py) |
| H3: Full pre-embed | context-files-standard.md |
| H5: Brain-evaluated heartbeats | brain-modules-standard.md |
| U-01: Agent identity | identity-soul-standard.md + claude-md-standard.md + agent-yaml-standard.md |
| U-09: Agent self-knowledge | tools-agents-standard.md |

**Standards FIRST, then build. This is the quality gate.**
