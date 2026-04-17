# CLAUDE.md — OpenFleet (Claude Code delta)

> **This is the Claude Code delta. For cross-tool universal context see `AGENTS.md`. For detailed rules see `.claude/rules/`.**

## Operator Directives (Sacrosanct)

The PO's words are verbatim and non-negotiable. Key standing rules:

- "do what is asked. not do what you were not asked to do"
- "this is a platform project, not an AI assistant — solo on main, no feature branches, no worktrees"
- "I AM THE PO — approve major changes via me"
- "verify code against the REAL data shape that module returns"
- "understanding before action — keep reading until told to stop, don't present summaries prematurely"
- "the second brain is the master right now and we are the slave — swallow the information, integrate, contribute back, evolve"

Full history: `wiki/log/` (directives kept verbatim, sacrosanct).

## Project Identity (Goldilocks — stable fields only)

| Dimension | Value |
|-----------|-------|
| **Type** | system (platform running a fleet; also solo-developable) |
| **Domain** | mixed (Python orchestrator + TS/Node gateway + Bash IaC + Markdown wiki) |
| **Phase** | production (fleet runs daily; platform still evolves) |
| **Scale** | large (~3,815 .md files, 2,246-line orchestrator, ~50k LOC+) |
| **Second Brain** | connected (sister project at `../devops-solutions-research-wiki`) |

Execution mode, SDLC profile, methodology model, trust tier are **consumer/task properties** — declared by each consumer at connect time. Not hardcoded here.

Full profile: `wiki/ecosystem/openfleet/identity-profile.md`.

## Three Governing Principles (from second brain)

| # | Principle | Measured Evidence |
|---|-----------|-------------------|
| 1 | **Infrastructure > Instructions** | Prose = 25% compliance; hooks = 100% (OpenArms v8→v10) |
| 2 | **Structured Context > Content** | Prose = 25%; tables = 60%; infra = 100%+ |
| 3 | **Goldilocks** | Right process per identity × phase × scale |
| 4 | **Declarations Aspirational Until Verified** | Every declared claim needs a gate or is aspirational |

## Claude-Specific Hard Rules (EVERY message)

| # | Rule | Why |
|---|------|-----|
| 1 | **Read command output IN FULL.** Never default to truncation. Internal tool output is curated — read every line. State a REASON before any truncation. | PO directive 2026-04-16 "don't truncate commands output mindlessly". |
| 2 | **When told to execute, execute.** Don't explain, don't ask, don't probe `--help`. Don't propose when asked to do. | Recurring drift. |
| 3 | **Major standards/config changes go through the PO.** Propose-approve-execute. Unilateral decisions on project standards are forbidden. | 2026-04-16 "I AM THE PO... HOW COULD YOU FORGET THAT". |
| 4 | **Use dedicated tools.** Read not cat, Grep not grep, Glob not find, Edit not sed. | System rule. |
| 5 | **Verify before contributing.** Before `gateway contribute` or shaping claims about external state, verify with `ls` / `Read` / `grep`. | 2026-04-16 self-failure: contributed a correction claiming no root AGENTS.md — there was one. |

## Work Mode (summary — detail in `.claude/rules/work-mode.md`)

- **Default**: solo coding on `main` branch. No feature branches, no worktrees, no destructive git, no subagent ceremonies without PO approval.
- **Before any git op**: can I recover without `git restore`/`reset --hard`/`stash drop`? If not, don't do it.
- **When called out**: stop. Re-read. Identify what I'm missing. Don't say "you're right" and repeat the mistake.
- **Investigate means investigate**: read code, compare data shapes, present findings. Don't propose fixes.

Detail: `.claude/rules/work-mode.md`.

## Second Brain Connection

- Brain at `../devops-solutions-research-wiki` (sister project)
- First step on fresh session: `python3 -m tools.gateway orient`
- Browse: `python3 -m tools.view spine | standards | lessons | patterns | search "query"`
- Query: `python3 -m tools.gateway query --model <type> | --stage <name> | --field <name>`
- Contribute: `python3 -m tools.gateway contribute --type lesson|correction|remark --title ... --content ...`
- Compliance check: `python3 -m tools.gateway compliance` (we're Tier 4/4 structural, Tier 2+ operational)

Detail: `.claude/rules/second-brain-connection.md`.

## Methodology Pointer

- Config: `config/methodology.yaml` (7 named models, 6 stages: conversation → analysis → investigation → reasoning → work → review)
- Selection by conditions: task_type + contribution_type + labor_iteration + delivery_phase + priority + agent
- Shared framework: `../devops-solutions-research-wiki/wiki/spine/models/foundation/model-methodology.md`
- Execution standards: `../devops-solutions-research-wiki/wiki/spine/standards/model-standards/model-methodology-standards.md`

Quality tiers: **Expert / Capable / Flagship-local / Lightweight / Direct** (OpenFleet-specific tier vocabulary; maps to brain's Skyscraper/Pyramid/Mountain).

## Routing Table — Where to Find What

| Need | Go to |
|---|---|
| Cross-tool universal context (Codex, Gemini, Copilot, Cursor) | `AGENTS.md` |
| Claude Code specific overrides | this file (`CLAUDE.md`) |
| Stable project identity | `wiki/ecosystem/openfleet/identity-profile.md` |
| Detailed rules (work mode, git, etc.) | `.claude/rules/` |
| Fleet architecture diagrams + data flow | `docs/ARCHITECTURE.md` |
| Service URLs + IRC channels + current state | `docs/current-state.md` (or equivalent) |
| MCP tool inventory (13 tools) | (brief below, detail in `fleet/mcp/tools.py`) |
| Methodology config | `config/methodology.yaml` |
| Per-agent runtime brain | `agents/{name}/SOUL.md` + `agents/{name}/HEARTBEAT.md` |
| Wiki schema + templates | `wiki/config/` (seeded from brain 2026-04-16) |
| Second brain shared knowledge | `../devops-solutions-research-wiki/wiki/` |

## MCP Tools (13 fleet + forwarders to brain)

Fleet (`fleet_*`): `fleet_read_context`, `fleet_task_accept`, `fleet_task_progress`, `fleet_commit`, `fleet_task_complete`, `fleet_alert`, `fleet_pause`, `fleet_escalate`, `fleet_notify_human`, `fleet_chat`, `fleet_task_create`, `fleet_approve`, `fleet_agent_status`.

Brain forwarders (in `tools/`): `gateway`, `view`, `lint`, `evolve` — all delegate to `../devops-solutions-research-wiki/tools/*` with `--wiki-root` pointing at OpenFleet.

## Current Focus

- Foundation chain: **E001 → E002 → E003 → E007** (no bifurcations)
- Second-brain integration priority: SWALLOW → INTEGRATE → CONTRIBUTE → EVOLVE
- Operational depth: migrate existing 57 wiki pages up to brain schema over time

Key documents:

- Decision tree: `wiki/domains/architecture/context-injection-tree.md`
- Shared models integration: `wiki/domains/architecture/shared-models-integration.md`
- Session logs: `wiki/log/2026-04-10-session-context-injection-evolution.md`, `wiki/log/2026-04-16-second-brain-integration-session.md`
- Directives: `wiki/log/2026-04-09-directive-shared-models-integration.md`, `wiki/log/2026-04-09-directive-five-documentation-layers.md`, `wiki/log/2026-04-11-directive-plan-types.md`
- PO vision: `wiki/log/2026-04-08-fleet-evolution-vision.md`
- Validation issues: `wiki/domains/architecture/validation-issues-catalog.md`
- Identity profile: `wiki/ecosystem/openfleet/identity-profile.md`
- Shared models (brain): `../devops-solutions-research-wiki/wiki/spine/models/foundation/model-llm-wiki.md`, `model-methodology.md`, `models/depth/model-second-brain.md`
- Ops state: `docs/current-state.md`, `docs/ARCHITECTURE.md`
