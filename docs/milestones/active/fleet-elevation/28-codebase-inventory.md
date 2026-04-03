# Codebase Inventory — What Already Exists

**Date:** 2026-03-30
**Status:** Reference — code awareness for elevation implementation
**Part of:** Fleet Elevation (document 28 — CRITICAL reference)

---

## Why This Document Exists

> "All this make me realize how its important to have code awareness.
> imagine you had try to write all these right after the compact, it
> would have been a total failure.... you needed to regather the context
> and reprocess it and reread the files grep and search the codebase
> for everything and make sure you use the right roads, right patterns
> and standards"

**READ THIS BEFORE IMPLEMENTING ANYTHING.**

The fleet codebase has 55 core modules, 7 infrastructure modules,
25 MCP tools, and established patterns. The elevation EXTENDS these —
it does NOT replace them. This document maps every module, what it
does, what the elevation changes, and how systems connect.

---

## Critical Finding: What Already Exists

### Chain Execution Engine — ALREADY BUILT

The tool call tree concept from doc 24 is ALREADY IMPLEMENTED:

- `fleet/core/event_chain.py` — EventChain, EventSurface (6 surfaces),
  Event with required/optional flag, ChainResult
- `fleet/core/chain_runner.py` — ChainRunner that executes EventChains
  across all surfaces with failure tolerance
- **Three chain builders already exist:**
  - `build_task_complete_chain()` — 12+ operations across all surfaces
  - `build_alert_chain()` — alert routing to IRC/ntfy/board memory
  - `build_sprint_complete_chain()` — sprint milestone publishing
- **Already used** in `fleet/mcp/tools.py` for fleet_task_complete
- **Already tested** in `fleet/tests/core/test_chain_runner.py` and
  `fleet/tests/core/test_event_chain.py`

**Elevation action:** ADD new chain builders for contributions, gates,
phase advances, transfers, rejections. Follow the EXISTING pattern:
```python
def build_contribution_chain(...) -> EventChain:
    chain = EventChain(operation="contribution", ...)
    chain.add(EventSurface.INTERNAL, "post_comment", {...})
    chain.add(EventSurface.PLANE, "update_issue", {...}, required=False)
    chain.add(EventSurface.CHANNEL, "notify_irc", {...}, required=False)
    return chain
```

### Pre-Embed: Two Systems — How They Relate

Two pre-embed modules exist. They are NOT duplicates — they serve
different roles:

1. `fleet/core/heartbeat_context.py` — **HeartbeatBundle** dataclass
   - Structured data: assigned_tasks, chat_messages, domain_events,
     sprint_summary, stage_instructions, fleet_mode, budget_warning,
     plane_data, mentioned_by
   - `format_message()` → compact text with emoji indicators
   - Used by: orchestrator, context_assembly, smart_chains, MCP tools
   - PO quotes in docstring about pre-computing context

2. `fleet/core/preembed.py` — **Text generators**
   - `build_heartbeat_preembed()` → full markdown text
   - `build_task_preembed()` → full task markdown with stage instructions
   - `format_task_full()` → detailed single-task format
   - Used by: orchestrator (_refresh_agent_contexts), context_writer

**Relationship:** heartbeat_context.py creates the DATA STRUCTURE.
preembed.py creates the TEXT OUTPUT. heartbeat_context.py imports
from preembed.py for the `preembed_text` field. context_writer.py
uses preembed.py to write the actual files.

**Elevation action:** Restructure preembed.py to generate the
AUTOCOMPLETE CHAIN format (identity → state → protocol → inputs →
standards → action) instead of flat data dump. heartbeat_context.py's
HeartbeatBundle gets new fields (contributions, phase, lifecycle state).

### Smart Chains — Designed but NOT Wired In

`fleet/core/smart_chains.py` has DispatchContext and the batched
operations concept. BUT: **it's imported by nothing.** The module
was designed but never integrated into the orchestrator or MCP tools.

**Elevation action:** Either wire smart_chains.py into the orchestrator
for dispatch context pre-computation, OR merge its concepts into the
existing preembed.py/context_assembly.py flow. Don't leave it unused.

### Model Selection — ALREADY Task-Aware

`fleet/core/model_selection.py` already selects opus/sonnet based on:
- Story points (>= 8 → opus, >= 5 → consider)
- Task type (epic → opus with max effort, blocker → opus)
- Agent role (DEEP_REASONING_AGENTS: architect, devsecops, PM, accountability)
- Explicit override (model custom field)

**Elevation action:** Extend with lifecycle-aware selection (doc 23).
Add budget-conscious downgrade (when weekly > 70%, force sonnet).
Add phase-aware selection (POC tasks can use lighter models).
DON'T create a new model selection module — extend this one.

### Federation — FleetIdentity ALREADY Exists

`fleet/core/federation.py` already has:
- FleetIdentity: fleet_id, fleet_name, machine_id, instance_uuid,
  agent_prefix, created_at
- Identity generated on first setup, persists in config/fleet-identity.yaml

**Elevation action:** Extend with shared_plane flag, IRC nick prefix,
git branch naming convention. The identity FOUNDATION is built.

### Events — ALREADY CloudEvents-Based

`fleet/core/events.py` uses CloudEvents specification. NOT aspirational
— it's the current implementation.

**Elevation action:** Add ~35 new event types. The EVENT SYSTEM exists;
only new types and renderers are needed.

### Agent Routing — Capability Matching ALREADY EXISTS

`fleet/core/routing.py` has AGENT_CAPABILITIES dict and suggest_agent()
function that matches tasks to agents by content analysis.

**Elevation action:** Used by PM for assignment decisions. Brain can
use this for contribution task routing (which agent should contribute
to which task type).

### PR Authority — Per-Role ALREADY Defined

`fleet/core/agent_roles.py` has AGENT_ROLES dict with PRAuthority
per agent:
- Architect: can_reject, can_request_changes
- QA: can_reject, can_request_changes
- DevSecOps: can_reject, can_request_changes, can_close_pr, CAN_BLOCK_APPROVAL
- Fleet-ops: final authority (implied by review role)
- Engineers/DevOps/Writer: can_request_changes only

**Elevation action:** Add contribution authority (who can contribute
what). Add cowork permissions. Add phase-gate authority.

### Event Router — Tag Subscriptions ALREADY Defined

`fleet/core/event_router.py` has AGENT_TAG_SUBSCRIPTIONS:
- fleet-ops subscribes to: review, alert, escalation, quality, security
- PM subscribes to: plan, sprint, velocity, backlog, plane, unassigned
- architect subscribes to: architecture, design, system, component
- etc.

PO quote in docstring about command center aggregation.

**Elevation action:** Add contribution tags, phase tags, gate tags
to subscription lists. Extend routing for new event types.

### Other Already-Built Systems

| Module | What It Does | Used? | Elevation Impact |
|--------|-------------|-------|-----------------|
| `behavioral_security.py` | Detect suspicious agent behavior | Yes (orchestrator) | Add contribution avoidance patterns |
| `health.py` | HealthIssue, HealthReport | Yes (orchestrator) | Add contribution health |
| `self_healing.py` | Auto-resolve stale reviews, offline agents | Yes (orchestrator) | Add stale contribution resolution |
| `task_scoring.py` | Priority scoring for dispatch | Yes (orchestrator) | Add phase urgency, contribution readiness |
| `skill_enforcement.py` | Required tools per task type | Yes (MCP tools) | Add contribution tools for contributor roles |
| `plan_quality.py` | Validate plans reference verbatim | Yes (MCP tools) | Phase-aware plan quality |
| `velocity.py` | Sprint metrics | Yes (PM heartbeat) | Add contribution metrics |
| `cross_refs.py` | Link related items across surfaces | Yes (events) | Extend for contributions, phase changes |
| `outage_detector.py` | Back off when APIs fail | Yes (orchestrator) | Used by error recovery |
| `memory_structure.py` | Agent persistent memory | Yes (agents) | Trail integration |
| `driver.py` | Autonomous driver model | Yes (PM, accountability) | Contribution-aware driver behavior |
| `board_cleanup.py` | Archive noise tasks | Yes (daemon) | No change needed |
| `config_watcher.py` | Detect config changes | Yes (daemon) | Used for evolution (doc 27) |
| `pr_hygiene.py` | Stale/conflicting PR detection | Yes (fleet-ops) | No change needed |
| `task_lifecycle.py` | PRE→PROGRESS→POST stages | Yes (MCP tools) | Methodology stages layer on top |

---

## Agent Files — Current State vs Elevation

### What Exists Now

| File | Architect | PM | Fleet-Ops | Others |
|------|-----------|-----|-----------|--------|
| agent.yaml | 15 lines (basic) | 15 lines | 15 lines | ~15 lines |
| CLAUDE.md | 67 lines (GOOD content) | 95 lines (GOOD) | 95 lines (GOOD) | Varies |
| HEARTBEAT.md | 105 lines (rewritten) | 156 lines (rewritten) | 96 lines (rewritten) | Template or basic |
| IDENTITY.md | Generic OpenClaw template | Same | Same | Same |
| SOUL.md | Generic OpenClaw template | Same | Same | Same |
| TOOLS.md | Auto-generated list | Same | Same | Same |
| AGENTS.md | Basic fleet awareness | Same | Same | Same |
| context/ | NO directory | NO | NO | Only accountability-generator has one |

### What Elevation Changes

| File | Action |
|------|--------|
| agent.yaml | ADD: fleet_id, fleet_number, username, roles.contributes_to |
| CLAUDE.md | ENRICH: add anti-corruption rules, contribution awareness, phase awareness. Keep existing role content. |
| HEARTBEAT.md | VERIFY: align with contribution model, phase awareness, lifecycle |
| IDENTITY.md | REWRITE: from generic template to fleet-specific with top-tier expert characterization |
| SOUL.md | REWRITE: from generic template to fleet-specific with anti-corruption values, role values |
| TOOLS.md | REWRITE: from auto-generated list to chain-aware documentation per role |
| AGENTS.md | REWRITE: from basic awareness to synergy-point-aware per doc 15 |
| context/ | CREATE: directories, brain writes fleet-context.md and task-context.md |

**CRITICAL:** CLAUDE.md already has good content for architect (67 lines),
PM (95 lines), fleet-ops (95 lines). The elevation ADDS to this — it does
NOT replace the existing role definitions. The additions are:
- Anti-corruption rules section
- Contribution model section
- Phase awareness section
- Top-tier expert characterization

---

## Test Coverage

```
fleet/tests/
├── core/
│   ├── test_agent_lifecycle.py
│   ├── test_artifact_tracker.py
│   ├── test_behavioral_security.py
│   ├── test_budget_monitor.py
│   ├── test_chain_runner.py        ← chain execution tests exist
│   ├── test_change_detector.py
│   ├── test_context_assembly.py
│   ├── test_cross_refs.py
│   ├── test_doctor.py
│   ├── test_budget_modes.py
│   ├── test_event_chain.py         ← chain builder tests exist
│   ├── test_event_display.py
│   ├── test_event_router.py
│   ├── test_events.py
│   ├── test_fleet_mode.py
│   ├── test_health.py
│   ├── test_heartbeat_context.py
│   ├── test_methodology.py
│   ├── test_model_selection.py
│   ├── test_notification_router.py
│   ├── test_plan_quality.py
│   ├── test_preembed.py
│   ├── test_role_providers.py
│   ├── test_self_healing.py
│   ├── test_skill_enforcement.py
│   ├── test_smart_chains.py        ← tests exist even though module unused
│   ├── test_stage_context.py
│   ├── test_standards.py
│   ├── test_task_scoring.py
│   ├── test_teaching.py
│   ├── test_transpose.py
│   └── test_velocity.py
├── infra/
│   ├── test_mc_client.py
│   └── test_plane_client.py
├── mcp/
│   └── test_tools.py
├── cli/
│   └── test_orchestrator.py
└── integration/
    ├── test_live_systems.py
    ├── test_milestone_matrix.py
    ├── test_fleet_modes.py
    └── test_system_flows.py
```

Existing tests: 821. Elevation adds ~460 new tests. Existing tests
MUST continue passing — if elevation changes break them, the tests
need updating (not deleting).

---

## Module Wiring Map — What's Connected Where

### Orchestrator (fleet/cli/orchestrator.py) — 21 modules wired in

Top-level imports:
- agent_lifecycle, budget_monitor, change_detector, directives,
  doctor, fleet_mode, models, notification_router, teaching

Lazy imports (inside functions):
- behavioral_security (scan_task), context_assembly (clear_context_cache),
  context_writer (write_heartbeat_context, write_task_context),
  budget_modes (get_profile), error_reporter (detect_rate_limit),
  events (create_event, EventStore), health (assess_fleet_health),
  outage_detector, preembed (build_heartbeat_preembed, build_task_preembed),
  role_providers (get_role_provider), self_healing (plan_healing_actions),
  task_scoring (rank_tasks)

### MCP Tools (fleet/mcp/tools.py) — Module usage

- chain_runner + event_chain (fleet_task_complete uses build_task_complete_chain)
- artifact_tracker (completeness checking)
- plan_quality (plan validation)
- skill_enforcement (required tools per type)
- task_lifecycle (PRE/PROGRESS/POST stages)
- agent_roles (PR authority during review)

### Dispatch CLI (fleet/cli/dispatch.py)

- model_selection (task-aware model choice for dispatch)

### Context Assembly (fleet/core/context_assembly.py)

- heartbeat_context, preembed, role_providers, methodology, stage_context,
  artifact_tracker, transpose, directives

### Unused Modules (designed but not imported by anyone)

- **smart_chains.py** — DispatchContext, batched ops. NOT IMPORTED anywhere.
  Decision needed: wire in or merge concepts into existing flow.

### Infrastructure Scripts (43 scripts)

```
Setup:     setup-mc.sh, configure-board.sh, provision-agents.sh,
           configure-openclaw.sh, configure-auth.sh
Runtime:   start-fleet.sh, fleet-sync-daemon.sh, fleet-monitor-daemon.sh
Agents:    register-agents.sh, push-agent-framework.sh, push-soul.sh,
           configure-agent-settings.sh, reprovision-agents.sh
IRC:       setup-irc.sh, setup-lounge.sh, notify-irc.sh, stop-irc.sh
Tasks:     create-task.sh, dispatch-task.sh, monitor-task.sh, trace-task.sh,
           integrate-task.sh
Quality:   fleet-quality-check.sh, fleet-digest.sh
Fleet:     fleet-status.sh, check-fleet-processes.sh, fleet-monitor-check.sh
Auth:      refresh-auth.sh, configure-auth.sh
Patches:   apply-patches.sh, apply-fleet-ui.sh
Other:     setup-project.sh, setup-worktree.sh, ws-monitor.sh,
           chat-agent.sh, generate-changelog.sh, clean-gateway-config.sh,
           install-openclaw.sh, install-service.sh, install-skills.sh,
           register-skill-packs.sh
```

### Makefile Targets

```
Setup:     setup, provision, board-setup
Fleet ops: status, create-task, dispatch, trace, monitor, chat, watch, integrate
Sync:      sync, sync-start, sync-stop
Daemons:   daemons-start, daemons-stop, monitor-start, monitor-stop
Agents:    agents, agents-register, agents-push, agents-config
Skills:    skills-list, skills-install, skills-sync
Infra:     mc-up, mc-down, mc-logs, irc-up, irc-down, lounge-up, lounge-down
Gateway:   gateway, gateway-stop, gateway-restart
Quality:   quality, digest
Testing:   test, clean
```

### Fleet CLI (17 commands)

```
python -m fleet <command>

  mcp-server    Start MCP server (stdio) — agent-facing tools
  status        Fleet overview (agents, tasks, activity)
  trace         Full task trace (MC + git + worktree + PR)
  sync          Sync tasks ↔ PRs (merge, close, cleanup)
  create        Create task (and optionally dispatch)
  dispatch      Dispatch task to agent via gateway
  digest        Generate daily fleet digest
  project       Manage projects (add/list/check)
  quality       Run quality compliance checks
  auth          Check and refresh auth tokens
  board         Board management (info/tasks/cleanup/tags/fields)
  cache         Manage cache (stats/cleanup/export/import)
  daemon        Run background daemons (sync/monitor/orchestrator/all)
  sprint        Sprint management (load/status)
  plane         Plane issue tracker (list/create/sync)
  pause         Pause/resume fleet (kill switch)
  notify        Send IRC notification
```

### Daemon System (5 concurrent daemons via asyncio.gather)

```
fleet daemon all
  ├── sync daemon (Plane ↔ OCMC sync, default 60s)
  ├── monitor daemon (board state monitoring, default 300s)
  ├── orchestrator daemon (the brain, default 30s)
  ├── auth refresh daemon (token refresh, 120s)
  └── plane watcher daemon (Plane change detection, 120s)
```

All daemons run concurrently. The elevation's orchestrator changes
must work alongside sync, monitor, auth, and plane-watcher without
interference. The daemon system is the fleet's HEARTBEAT — it runs
continuously and drives all automation.

### Message Templates (fleet/templates/)

Formatting modules for messages sent to surfaces:
- `irc.py` — one-line IRC messages with emoji + agent + event + URL
- `memory.py` — board memory content formatting
- `comment.py` — task comment formatting
- `pr.py` — PR description formatting

Used by chain_runner and MCP tools. Elevation may need new templates
for: contribution comments, gate request messages, phase advance
notifications, trail event formatting.

### Additional Directories

```
integrations/   — mission-control integration (currently empty)
skills/         — Claude API skill packs (claude-api, doc-coauthoring,
                  pdf, xlsx, frontend-design, mcp-builder, etc.)
patches/        — 6 vendor patches for MC (fleet-config, control bar,
                  health panel, event stream)
projects/       — project workspace configs (dspd/, nnrt/)
systemd/        — systemd service template for fleet daemon
vendor/         — vendored MC code for patches
workspace-*/    — agent worktrees (created during task execution)
```

---

## Implementation Rules

1. **BEFORE creating any new module:** check this inventory. Does
   a module already do part of what you need?
2. **BEFORE implementing any pattern:** check if it's already used
   in the codebase. Follow established patterns.
3. **BEFORE writing any chain:** check event_chain.py for existing
   builders. Follow the build_*_chain() pattern.
4. **BEFORE touching pre-embed:** understand the two-system
   relationship (heartbeat_context.py = data, preembed.py = text).
5. **BEFORE modifying agent CLAUDE.md:** read the EXISTING content
   first. ENRICH, don't replace.
6. **BEFORE proposing config changes:** read the current fleet.yaml
   and understand what each section does.
7. **Run tests after every change:** `pytest fleet/tests/ -v`