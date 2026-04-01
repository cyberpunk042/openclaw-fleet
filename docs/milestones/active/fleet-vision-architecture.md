# Fleet Vision Architecture — Code-Verified System Map

**Date:** 2026-03-31
**Status:** ACTIVE — built from reading actual code, not summaries
**Verification:** Every claim in this document was verified by reading the source module. Module paths and line numbers cited.

---

## 1. What This Document Is

The single reference for understanding the entire fleet system. Built by reading 94 core modules, 25 MCP tools, 10 agent configs, 8 config files, and 45+ design documents. Only states what is verified in code or explicitly noted as "design doc only — not implemented."

---

## 2. The Orchestrator — What Actually Runs

**Source:** `fleet/cli/orchestrator.py` (1378 lines)

The orchestrator is the brain. It runs in a loop (default 30s interval) and executes 9 steps per cycle:

```
Step 0: _refresh_agent_contexts()     — pre-embed FULL data per agent role
Step 1: _security_scan()              — check tasks for suspicious content
Step 2: _run_doctor()                 — immune system detection + response
Step 3: _ensure_review_approvals()    — create approval objects for review tasks
Step 4: _wake_drivers()               — inject wake messages into PM/fleet-ops sessions
Step 5: _dispatch_ready_tasks()       — dispatch unblocked inbox tasks to agents
Step 6: _process_directives()         — parse PO directives from board memory
Step 7: _evaluate_parents()           — when all children done → parent to review
Step 8: _health_check()               — detect stuck tasks, offline agents
```

**Before the steps:** Storm monitor evaluates (CRITICAL=stop, STORM=0 dispatch, WARNING=1 dispatch). Gateway duplication check. Effort profile gate. Fleet mode gate.

**What the orchestrator uses (verified imports):**
- `FleetLifecycle` from `agent_lifecycle.py`
- `ChangeDetector` from `change_detector.py`
- `NotificationRouter` from `notification_router.py`
- `BudgetMonitor` from `budget_monitor.py`
- `StormMonitor` from `storm_monitor.py`
- `FleetControlState` from `fleet_mode.py`
- `DoctorReport`, `run_doctor_cycle` from `doctor.py`
- `parse_directives` from `directives.py`
- `check_gateway_duplication` from `gateway_guard.py`
- `adapt_lesson`, `format_lesson_for_injection` from `teaching.py`
- `get_active_profile_name`, `get_profile` from `effort_profiles.py`

### 2.1 Step 0: Context Refresh (IMPLEMENTED)

**Source:** `orchestrator.py:257-366`, `context_writer.py`, `preembed.py`, `role_providers.py`

Every cycle, the orchestrator writes `agents/{name}/context/fleet-context.md` and `task-context.md` for each agent. Data is FULL, not compressed.

Each agent gets:
- Their assigned tasks (full detail via `format_task_full()`)
- Messages mentioning them (from board memory, `mention:{agent_name}` tag)
- PO directives (from board memory, parsed by `directives.py`)
- Role-specific data (via role_providers):
  - **fleet-ops:** pending_approvals, review_queue, offline_agents
  - **project-manager:** unassigned_tasks, blocked_tasks, sprint progress
  - **architect:** tasks needing design review (verified in `role_providers.py`)
- Fleet state: work_mode, cycle_phase, backend_mode, agents online/total
- Events since last heartbeat

**How it reaches agents:** `context_writer.py` writes to disk → gateway reads files when agent heartbeats → files injected into system prompt.

### 2.2 Step 2: Doctor — Immune System (IMPLEMENTED)

**Source:** `doctor.py` (250+ lines)

Detections implemented:
- `detect_protocol_violation()` — fleet_commit called in non-work stage
- `detect_laziness()` — fast completion relative to SP, partial acceptance criteria
- `detect_stuck()` — no activity for threshold minutes
- `detect_correction_threshold()` — 3 corrections = prune

Response actions: NONE, MONITOR, FORCE_COMPACT, TRIGGER_TEACHING, PRUNE, ESCALATE_TO_PO

The orchestrator uses the DoctorReport to:
- Skip flagged agents during dispatch
- Block flagged tasks
- Inject teaching lessons via gateway `inject_content()`

### 2.3 Step 4: Wake Drivers (IMPLEMENTED)

**Source:** `orchestrator.py:761-830`

PM wakes when: unassigned inbox tasks exist (120s cooldown)
Fleet-ops wakes when: tasks in review status exist (120s cooldown)

Waking = `inject_content(agent.session_key, wake_message)` via gateway client. The message includes full task details for PM or review count for fleet-ops.

---

## 3. Methodology System — What Actually Exists

### 3.1 Stages (IMPLEMENTED)

**Source:** `methodology.py` (477 lines)

5 stages: `CONVERSATION → ANALYSIS → INVESTIGATION → REASONING → WORK`

**Work stage requires readiness >= 99** (line 196 for initial stage, lines 339-341 for work check).

Valid readiness values (line 368): `0, 5, 10, 20, 30, 50, 70, 80, 90, 95, 99, 100`

Readiness suggestions per stage (line 377):
- conversation: 10
- analysis: 30
- investigation: 50
- reasoning: 80
- work: 99

**Task types skip stages** (lines 44-91):
- epic: all 5 stages
- story: conversation, reasoning, work
- task/subtask: reasoning, work
- bug: analysis, reasoning, work
- spike: conversation, investigation, reasoning (NO work stage)
- concern: conversation, analysis, investigation (NO work stage)

**Stage checks** (lines 213-362) — each stage has explicit boolean checks:
- conversation: has_verbatim_requirement, has_po_response, no_open_questions
- analysis: has_analysis_document, po_reviewed
- investigation: has_research_document, multiple_options_explored, po_reviewed
- reasoning: has_plan, plan_references_verbatim, plan_specifies_files, po_confirmed_plan
- work: readiness >= 99, has_commits, has_pr, acceptance_criteria_met, required_tools_called

ALL checks must pass before `can_advance = True`.

### 3.2 Stage Instructions (IMPLEMENTED)

**Source:** `stage_context.py` (215 lines)

Each stage has full MUST do / MUST NOT do / CAN produce / How to advance instructions. Injected into agent context via `preembed.py`.

Key enforcement: Every stage explicitly says "Do NOT call fleet_commit or fleet_task_complete" except work stage.

### 3.3 Stage-Gated Tool Access (IMPLEMENTED)

**Source:** `fleet/mcp/tools.py:130-171`

`WORK_ONLY_TOOLS = {"fleet_commit", "fleet_task_complete"}` (line 130)

`_check_stage_allowed()` returns an error dict AND emits a `fleet.methodology.protocol_violation` event if work tools are called outside work stage. This IS enforcement — the tool returns an error to the agent.

### 3.4 Delivery Phases (IMPLEMENTED — Distinct from Stages)

**Source:** `phases.py` (60+ lines), `config/phases.yaml`

Stages = how you work on a task. Phases = how mature a deliverable is.

Phase progressions defined by PO in YAML:
- standard: ideal → conceptual → poc → mvp → staging → production
- release: alpha → beta → rc → release

Each phase has: standards, required_contributions, gate (bool — requires PO approval).

---

## 4. Agent File Architecture — What Actually Exists

### 4.1 File Structure (VERIFIED from git and .gitignore)

**Committed files** (IaC source of truth):
- `agent.yaml` — all agents
- `CLAUDE.md` — all agents (role-specific rules)
- `HEARTBEAT.md` — all agents (action protocol)
- `context/fleet-context.md` — overwritten by brain every cycle
- `context/task-context.md` — overwritten by brain at dispatch

**Gitignored files** (generated at runtime for workers):
- `IDENTITY.md`, `SOUL.md`, `TOOLS.md`, `USER.md`, `MEMORY.md`, `AGENTS.md`, `BOOTSTRAP.md`

**Exception — Persistent agents** (devsecops, fleet-ops, project-manager):
- Have their own `.gitignore` that only ignores `TOOLS.md` and `*.json`
- Their IDENTITY.md, SOUL.md, AGENTS.md, USER.md, BOOTSTRAP.md ARE committed

### 4.2 Gateway Injection Order (FROM DESIGN DOC fleet-elevation/02 — Not Verified in Gateway Code)

```
1. IDENTITY.md    ← grounding (most influence)
2. SOUL.md        ← boundaries
3. CLAUDE.md      ← role-specific rules (max 4000 chars)
4. TOOLS.md       ← chain-aware capabilities
5. AGENTS.md      ← synergy knowledge
6. context/fleet-context.md  ← fleet state (dynamic)
7. context/task-context.md   ← task + autocomplete chain (dynamic)
8. HEARTBEAT.md   ← action prompt (last)
```

**NOTE:** This order is specified in the design doc but I have NOT verified the actual gateway executor code reads files in this order. The gateway is OpenClaw vendor code.

### 4.3 CLAUDE.md Constraints

**From design doc fleet-elevation/02:** Max 4000 chars enforced by gateway. Content must be dense, role-specific. No generic filler. Must include anti-corruption rules.

**Current state:** Only `devsecops-expert` has a rich CLAUDE.md (139 lines). Other agents have functional but not role-specific CLAUDE.md files. None include the 10 anti-corruption rules from `fleet-elevation/20`.

---

## 5. The 25 MCP Tools — What Agents Can Actually Do

**Source:** `fleet/mcp/tools.py` (2200+ lines)

| # | Tool | Purpose |
|---|------|---------|
| 1 | `fleet_read_context` | Read full task and project context |
| 2 | `fleet_task_accept` | Accept assigned task with plan |
| 3 | `fleet_task_progress` | Report progress on task |
| 4 | `fleet_commit` | Git commit (WORK stage only) |
| 5 | `fleet_task_complete` | Complete task → push → PR → review (WORK stage only) |
| 6 | `fleet_alert` | Post alert to board memory + IRC |
| 7 | `fleet_pause` | Pause current work, report blocker |
| 8 | `fleet_escalate` | Escalate to PO via ntfy + IRC |
| 9 | `fleet_notify_human` | Direct notification to human |
| 10 | `fleet_chat` | Post to board memory with @mentions |
| 11 | `fleet_task_create` | Create task/subtask |
| 12 | `fleet_approve` | Approve or reject task |
| 13 | `fleet_agent_status` | Check agent statuses |
| 14 | `fleet_plane_status` | Check Plane project status |
| 15 | `fleet_plane_sprint` | Get current sprint data |
| 16 | `fleet_plane_sync` | Sync OCMC ↔ Plane |
| 17 | `fleet_plane_create_issue` | Create Plane issue |
| 18 | `fleet_plane_comment` | Comment on Plane issue |
| 19 | `fleet_plane_update_issue` | Update Plane issue fields |
| 20 | `fleet_plane_list_modules` | List Plane modules |
| 21 | `fleet_task_context` | Get assembled task context |
| 22 | `fleet_heartbeat_context` | Get assembled heartbeat context |
| 23 | `fleet_artifact_read` | Read structured artifact from Plane |
| 24 | `fleet_artifact_update` | Update artifact field → Plane HTML |
| 25 | `fleet_artifact_create` | Create new artifact → Plane HTML |

**NOT in the tool list (design doc specifies but not implemented):**
- `fleet_contribute` — contribution to another agent's task
- `fleet_request_input` — request missing contribution from PM
- `fleet_gate_request` — request PO gate approval

---

## 6. Immune System — What Actually Exists

### 6.1 Doctor (IMPLEMENTED)

**Source:** `doctor.py`

4 detection functions implemented:
1. `detect_protocol_violation` — work tools in non-work stage
2. `detect_laziness` — fast completion, partial acceptance criteria
3. `detect_stuck` — no activity for threshold minutes
4. `detect_correction_threshold` — 3 corrections = prune

**NOT implemented** (design doc specifies):
- `detect_deviation` — work doesn't match verbatim
- `detect_scope_creep` — unrequested additions
- `detect_compression` — large scope minimized
- `detect_abstraction` — PO's words replaced
- `detect_contribution_avoidance` — skipping contributions
- `detect_synergy_bypass` — working without design input

### 6.2 Teaching System (IMPLEMENTED)

**Source:** `teaching.py`

11 disease categories defined. Lesson templates with placeholders. Exercises with verification hints. The orchestrator calls `adapt_lesson()` and `format_lesson_for_injection()` then injects via gateway.

### 6.3 What the Doctor Runs On

The orchestrator runs `_run_doctor()` at Step 2 every cycle. It produces a `DoctorReport` with:
- `detections` — what was found
- `interventions` — what actions to take
- `agents_to_skip` — don't dispatch to these agents
- `tasks_to_block` — don't dispatch these tasks
- `health_profiles` — per-agent health history

---

## 7. Control Surface — 3 Axes (IMPLEMENTED)

**Source:** `fleet_mode.py`

### Work Mode (5 options)
- `full-autonomous` — all agents active, Plane pulling
- `project-management-work` — PM drives work, no Plane pulling
- `local-work-only` — OCMC tasks only, no Plane
- `finish-current-work` — no new dispatch, finish what's in progress
- `work-paused` — nothing runs

### Cycle Phase (6 options)
- `execution` — all agents
- `planning` — project-manager + architect only
- `analysis` — architect + project-manager only
- `investigation` — any assigned agent
- `review` — fleet-ops only
- `crisis-management` — fleet-ops + devsecops only

### Backend Mode (3 options)
- `claude` — Claude Code backend
- `localai` — LocalAI backend
- `hybrid` — both

**Read from board's fleet_config JSON field every cycle.**

---

## 8. Effort Profiles (IMPLEMENTED)

**Source:** `effort_profiles.py`

| Profile | Dispatch | Driver HB | Worker HB | Opus | Active Agents |
|---------|----------|-----------|-----------|------|---------------|
| full | 2/cycle | 30min | 60min | Yes | all |
| conservative | 1/cycle | 60min | 120min | No | PM, fleet-ops, devsecops |
| minimal | 0/cycle | 120min | disabled | No | fleet-ops only |
| paused | 0/cycle | disabled | disabled | No | none |

---

## 9. Agent Lifecycle (IMPLEMENTED)

**Source:** `agent_lifecycle.py`

States: `ACTIVE → IDLE → DROWSY → SLEEPING → OFFLINE`

Content-aware transitions (from code):
- DROWSY after 2 consecutive HEARTBEAT_OK
- SLEEPING after 3 consecutive HEARTBEAT_OK
- `consecutive_heartbeat_ok` and `last_heartbeat_data_hash` fields on AgentState

Time-based fallbacks:
- IDLE after 10min without work
- SLEEPING after 30min idle
- OFFLINE after 4h sleeping

Heartbeat intervals:
- ACTIVE: 0 (agent drives own work)
- IDLE: 30min
- DROWSY: 60min
- SLEEPING: 2h
- OFFLINE: 2h

**NOT implemented:** Brain-evaluated heartbeats (the design doc specifies that DROWSY/SLEEPING agents get deterministic evaluation instead of Claude calls — the data structures exist but the evaluation logic is not in the orchestrator).

---

## 10. Event System (IMPLEMENTED)

**Source:** `event_chain.py`, `events.py`, `event_router.py`

6 event surfaces: INTERNAL, PUBLIC, CHANNEL, NOTIFY, PLANE, META

EventChain pattern: one operation produces multiple events across surfaces. Tolerates partial failure.

Events emitted by: orchestrator (mode changes, dispatch), MCP tools (commits, completions, alerts), doctor (protocol violations), methodology (stage changes).

---

## 11. Storm Prevention (IMPLEMENTED)

**Source:** `storm_monitor.py`, `storm_integration.py`

Orchestrator checks storm every cycle:
- CRITICAL → return immediately (full stop)
- STORM → dispatch = 0
- WARNING → dispatch ≤ 1, diagnostic snapshot captured
- WATCH → monitoring note

Gateway duplication check (the root cause of the March catastrophe) runs every cycle.

9 storm indicators tracked. Circuit breakers per agent and per backend. Diagnostic snapshots persisted to disk.

---

## 12. Budget System (IMPLEMENTED)

**Source:** `budget_monitor.py`, `budget_modes.py`

6 modes: blitz ($50), standard ($20), economic ($10), frugal ($5), survival ($1), blackout ($0)

Auto-transitions based on quota pressure (implemented in `budget_modes.py:evaluate_auto_transition()`).

Budget modes constrain:
- Allowed models (blitz=opus+sonnet+haiku, economic=sonnet only, frugal/survival=no Claude)
- Max effort level
- Routing decisions (backend_router respects constraints)

---

## 13. What's NOT Built — Honest List

### Not in code (design docs only):

1. **Brain-evaluated heartbeats** — DROWSY state exists, evaluation logic doesn't
2. **Contribution flow** — brain creating parallel contribution subtasks
3. **`fleet_contribute` MCP tool** — not in the 25 tools
4. **`fleet_request_input` MCP tool** — not in the 25 tools
5. **Autocomplete chain engineering** — context doesn't structure the response funnel
6. **Agent CLAUDE.md per fleet-elevation specs** — only devsecops has rich CLAUDE.md
7. **Anti-corruption rules in CLAUDE.md** — not in any agent's CLAUDE.md
8. **Role-specific HEARTBEAT.md per fleet-elevation specs** — template exists, per-role rewrites not done
9. **Standards injection into agent context** — standards exist, not injected per task type
10. **Plane comment sync** — OCMC task comments don't sync to Plane comments
11. **Parent task comment propagation** — subtask done doesn't post to parent
12. **AICP RAG connected to fleet** — both exist, not connected
13. **LocalAI routing in fleet** — AICP has it, fleet doesn't use it
14. **Session telemetry feeding fleet systems** — adapter built, not wired to runtime
15. **Multi-fleet identity** — design exists, not implemented

### Partially implemented:

16. **Orchestrator wake logic** — PM and fleet-ops wake IS implemented, but wake data is minimal (not full pre-embed per AR spec)
17. **Doctor detections** — 4 of ~10 designed detections implemented
18. **Pre-embed data** — FULL data written, but NOT per-role-specific as AR-02 specifies (PM doesn't get Plane sprint data, workers don't get artifact completeness)
19. **Stage-gated tool access** — fleet_commit and fleet_task_complete blocked, but other stage-inappropriate tools not gated

---

## 14. The Path — Verified Priority Order

Based on what ACTUALLY exists vs what's needed:

### Phase 1: Make Agents Functional (Blocks Everything)

| Priority | What | Why | Depends On |
|----------|------|-----|-----------|
| 1 | Write CLAUDE.md per fleet-elevation specs (10 agents) | Agents need role-specific rules + anti-corruption | Nothing |
| 2 | Rewrite HEARTBEAT.md per role (5 drivers + worker template) | Agents need correct action protocol | CLAUDE.md |
| 3 | Enhance pre-embed per role | PM needs Plane data, workers need artifact state | Pre-embed working |
| 4 | Add `fleet_contribute` MCP tool | Contribution flow depends on this tool | MCP server |
| 5 | Brain creates contribution subtasks | PM assigns → brain creates parallel contributions | fleet_contribute tool |

### Phase 2: Test with Real Agents

| Priority | What | Why |
|----------|------|-----|
| 6 | Live test: PM assigns a task | Verify PM wakes, reads context, assigns agent |
| 7 | Live test: Worker follows stages | Verify worker reads stage instructions, produces artifacts |
| 8 | Live test: Fleet-ops reviews | Verify fleet-ops reads task, approves/rejects with reasoning |
| 9 | Live test: Full cycle | PM assigns → worker works → fleet-ops reviews → done |

### Phase 3: Connect Systems

| Priority | What | Why |
|----------|------|-----|
| 10 | Wire AICP RAG to fleet | Agents need project knowledge |
| 11 | Wire LocalAI into routing | Free backend for simple tasks |
| 12 | Wire session telemetry | Real cost data into budget/storm/labor |
| 13 | Brain-evaluated heartbeats | 70% cost reduction on idle agents |

### Phase 4: Scale

| Priority | What | Why |
|----------|------|-----|
| 14 | Add Qwen 2.5 models + benchmarks | Better local models |
| 15 | Plane auto-update + writer notification | Documentation automation |
| 16 | Multi-fleet identity | Fleet Alpha + Fleet Bravo |

---

## 15. Additional Verified Systems

### 15.1 Change Detection (IMPLEMENTED)

**Source:** `change_detector.py`

Tracks what changed between orchestrator cycles by diffing task states. Produces a `ChangeSet` with: new_tasks_in_review, new_tasks_done, new_tasks_in_inbox, tasks_unblocked, agents_went_offline. Properties: `needs_review_wake`, `needs_dispatch`.

**Used by:** Orchestrator to determine if PM/fleet-ops need waking, if dispatch is needed.

### 15.2 Skill Enforcement (IMPLEMENTED)

**Source:** `skill_enforcement.py`

Per task-type required tools:
- **task:** fleet_read_context, fleet_task_accept, fleet_commit, fleet_task_complete (all required)
- **story:** adds fleet_task_create (stories should create subtasks), fleet_task_progress (required — stories are long)
- **epic:** fleet_read_context, fleet_agent_status (must check fleet state), fleet_task_create (MUST produce subtasks), fleet_task_accept
- **blocker:** fleet_read_context, fleet_task_accept, fleet_task_complete, fleet_alert (recommended)

Missing required tools lower confidence score during approval. Fleet-ops considers this during review.

### 15.3 Behavioral Security (IMPLEMENTED)

**Source:** `behavioral_security.py`

Cyberpunk-Zero's layer. Scans for: credential exfiltration, DB destruction, security disabling. Even human requests get flagged if suspicious. Can set `security_hold` on tasks (blocks approval). SecurityScan produces findings with severity, evidence, recommendations.

**Used by:** Orchestrator Step 1 (_security_scan).

### 15.4 Plane Sync (IMPLEMENTED — Bidirectional)

**Source:** `plane_sync.py`, `plane_methodology.py`

**Plane → OCMC:** `ingest_from_plane()` discovers new Plane issues, creates OCMC tasks with plane_issue_id, plane_project_id, plane_workspace custom fields.

**OCMC → Plane:** `push_completions_to_plane()` reflects done tasks back to Plane by updating issue state.

**Methodology on Plane:** Uses labels for stage (`stage:conversation`) and readiness (`readiness:50`). Verbatim requirement injected into Plane issue description_html via fleet-verbatim span markers.

**NOT implemented:** Task comment sync (OCMC comments → Plane comments), which is why agents' comments on tasks don't appear on Plane issues.

### 15.5 Transpose Layer (IMPLEMENTED)

**Source:** `transpose.py`

Bidirectional object ↔ rich HTML conversion. Agent works with structured dicts. Plane shows rich HTML. Uses `<span class="fleet-artifact-start" data-type="{type}">` markers for machine-parseable HTML.

Content OUTSIDE artifact markers is NEVER touched — the PO can add manual notes. Multiple artifact sections can coexist.

**Used by:** `fleet_artifact_create`, `fleet_artifact_update`, `fleet_artifact_read` MCP tools.

### 15.6 Directives (IMPLEMENTED)

**Source:** `directives.py`

PO posts to board memory with tags `["directive", "to:agent-name", "from:human"]`. Orchestrator parses directives each cycle, routes to target agent's heartbeat context. Processed directives tagged with "processed" to avoid re-processing.

### 15.7 Notification Routing (IMPLEMENTED)

**Source:** `notification_router.py`

Classifies events as INFO (ntfy progress), IMPORTANT (ntfy review), URGENT (ntfy alert + Windows toast). Handles deduplication with cooldown. Routes to ntfy with admonition tags for visual classification.

### 15.8 Velocity & Sprint Metrics (IMPLEMENTED)

**Source:** `velocity.py`

Tracks: story points per sprint, task cycle time, agent throughput, sprint progress, blocker resolution time. Used by PM for planning, fleet-ops for monitoring.

### 15.9 Cross-References (IMPLEMENTED)

**Source:** `cross_refs.py`

When events happen, automatically links related items: task completed → Plane issue gets PR link, PR merged → OCMC task comment, sprint started → IRC announcement. PO requirement: "always cross reference."

### 15.10 Memory Structure (IMPLEMENTED)

**Source:** `memory_structure.py`

Defines agent memory organization:
- `MEMORY.md` — index
- `codebase_knowledge.md` — patterns, architecture learned
- `project_decisions.md` — decisions and rationale
- `task_history.md` — what I've done, lessons learned
- `team_context.md` — what other agents are doing

Board memory = shared knowledge layer. Agents post with tags, fleet_read_context surfaces relevant entries.

### 15.11 Task Lifecycle Engine (IMPLEMENTED)

**Source:** `task_lifecycle.py`

PRE → PROGRESS → POST enforcement:
- PRE: context loaded, plan shared, dependencies checked
- PROGRESS: commits, progress updates, quality checkpoints
- POST: tests run, output validated, review gates populated

### 15.12 Config Sync (IMPLEMENTED)

**Source:** `config_sync.py`

Keeps IaC YAML configs in sync with live Plane state. When Plane watcher detects changes, updates DSPD config files. Optionally commits to git. PO requirement: "if we restart it will pick up where we left."

### 15.13 Outage Detector (IMPLEMENTED)

**Source:** `outage_detector.py`

Detects: MC API unreachable, rate limits (429), gateway unreachable, repeated failures. Orchestrator checks outage state before each cycle. Exponential backoff on rate limits. Alert human via ntfy.

---

## 16. Complete Module Inventory — 94 Core Modules

### 16.1 By System (Verified Grouping)

**Orchestrator & Brain (8):**
`orchestrator.py`, `driver.py`, `smart_chains.py`, `chain_runner.py`, `routing.py`, `context_assembly.py`, `context_writer.py`, `preembed.py`

**Methodology (5):**
`methodology.py`, `stage_context.py`, `phases.py`, `standards.py`, `plan_quality.py`

**Immune System (3):**
`doctor.py`, `behavioral_security.py`, `self_healing.py`

**Teaching System (1):**
`teaching.py`

**Agent Management (5):**
`agent_lifecycle.py`, `agent_roles.py`, `models.py`, `heartbeat_context.py`, `role_providers.py`

**Task Management (5):**
`task_lifecycle.py`, `task_scoring.py`, `skill_enforcement.py`, `review_gates.py`, `pr_hygiene.py`

**Event System (4):**
`events.py`, `event_chain.py`, `event_router.py`, `event_display.py`

**Control Surface (4):**
`fleet_mode.py`, `effort_profiles.py`, `directives.py`, `memory_structure.py`

**Plane Integration (4):**
`plane_sync.py`, `plane_watcher.py`, `plane_methodology.py`, `config_sync.py`

**Transpose Layer (2):**
`transpose.py`, `artifact_tracker.py`

**Storm Prevention (4):**
`storm_monitor.py`, `storm_integration.py`, `storm_analytics.py`, `incident_report.py`

**Budget System (4):**
`budget_monitor.py`, `budget_modes.py`, `budget_analytics.py`, `budget_ui.py`

**Labor Attribution (3):**
`labor_stamp.py`, `labor_analytics.py`, `heartbeat_stamp.py`

**Multi-Backend Routing (5):**
`backend_router.py`, `backend_health.py`, `model_swap.py`, `codex_review.py`, `router_unification.py`

**Model Management (5):**
`model_selection.py`, `model_configs.py`, `model_benchmark.py`, `model_promotion.py`, `tier_progression.py`

**Challenge Engine (8):**
`challenge.py`, `challenge_protocol.py`, `challenge_automated.py`, `challenge_cross_model.py`, `challenge_scenario.py`, `challenge_readiness.py`, `challenge_deferred.py`, `challenge_analytics.py`

**Session & Context (4):**
`session_metrics.py`, `session_telemetry.py`, `shadow_routing.py`, `change_detector.py`

**Notifications (3):**
`notification_router.py`, `cross_refs.py`, `urls.py`

**Infrastructure (8):**
`auth.py`, `cache.py`, `config_watcher.py`, `federation.py`, `gateway_guard.py`, `health.py`, `openai_client.py`, `outage_detector.py`

**Future (4):**
`dual_gpu.py`, `turboquant.py`, `cluster_peering.py`, `velocity.py`

**Other (5):**
`interfaces.py`, `__init__.py`, `ocmc_watcher.py`, `remote_watcher.py`, `board_cleanup.py`

---

## 17. The Cross-Agent Contribution Flow — What Exists vs What's Needed

### 17.1 What the Design Docs Specify (fleet-elevation/15)

When a task enters REASONING stage, the brain should create PARALLEL contribution subtasks:
- architect → `design_input`
- qa-engineer → `qa_test_definition`
- devsecops-expert → `security_requirement` (if applicable)
- ux-designer → `ux_spec` (if UI task)
- technical-writer → `documentation_outline` (recommended)

Contributors work independently. All contributions must arrive before WORK stage.

### 17.2 What Actually Exists in Code

**`fleet_contribute` tool:** NOT in the 25 MCP tools. NOT implemented.
**`fleet_request_input` tool:** NOT in the 25 MCP tools. NOT implemented.
**Brain creating contribution subtasks:** NOT in orchestrator code. NOT implemented.
**Contribution type tracking:** `fleet/core/models.py` has `contribution_type` field in TaskCustomFields. EXISTS.
**Review gates:** `fleet/mcp/tools.py:_build_review_gates()` creates reviewer requirements per task type (QA for code, architect for epic/story, devsecops for security). IMPLEMENTED in fleet_task_complete.

### 17.3 Gap

The contribution flow is the LARGEST missing piece. Without it:
- Architect doesn't provide design input before engineers implement
- QA doesn't predefine tests before work begins
- DevSecOps doesn't provide security requirements before implementation
- UX doesn't provide component specs before UI work
- Technical writer doesn't plan documentation

This is what the PO means by: "everyone brings their piece, their segments and artifacts."

### 17.4 What Needs Building

1. `fleet_contribute` MCP tool — agent posts contribution to another agent's task
2. Brain logic: when task enters REASONING, create contribution subtasks
3. Brain logic: check all required contributions received before allowing WORK
4. Pre-embed contributions into worker's task context

---

## 18. The 10 Anti-Corruption Rules (from fleet-elevation/20)

These must be in EVERY agent's CLAUDE.md:

```
1. PO's words are sacrosanct. Do not deform, interpret, abstract, or compress
   the verbatim requirement.
2. Do not summarize when original needed. 20 things = address 20.
3. Do not replace PO's words with your own.
4. Do not add scope not in the requirement.
5. Do not compress scope. Large system = large system.
6. Do not skip reading. Read before modifying.
7. Do not produce code outside work stage.
8. Three corrections = model is wrong. Stop, re-read, start fresh.
9. Follow the autocomplete chain. Context tells you what to do.
10. When uncertain, ask — don't guess.
```

**Current state:** ZERO agents have these rules in their CLAUDE.md.

---

## 19. Honest Milestone Assessment — What's Real

### Previously Claimed "COMPLETE" — Honest Re-Assessment

| Milestone Group | Unit Tested | Integration Tested | Live Tested | Honest Status |
|-----------------|------------|-------------------|-------------|---------------|
| Three Systems (44) | Yes (~552 tests) | Some | **No** | **Code exists, untested with real agents** |
| Control Surface (7) | Yes | — | **No** | **Code exists, untested live** |
| Event Bus (20) | Yes | — | **No** | **Code exists, untested live** |
| Fleet Autonomy (~15) | Yes | — | **Partial** | **Orchestrator runs, agents don't fully function** |
| Context System (34) | Yes | — | **No** | **Code exists, untested live** |
| Transpose Layer (7) | Yes | — | **No** | **Code exists, untested live** |
| Strategic (47) | Yes (744 tests) | Yes (23 tests) | **No** | **Decision logic tested, not connected to runtime** |

**Total: ~174 milestones with code, ~1800+ unit tests, ~23 integration tests, ~0 live tests.**

The code works in isolation. The systems connect partially. Nothing has been tested with a real agent doing a real task through the full lifecycle.

### What "Live Tested" Would Mean

A single live test: PM wakes → reads pre-embedded unassigned tasks → assigns agent → worker receives task → worker follows stage protocol → worker produces artifact → worker commits → worker completes → fleet-ops wakes → reviews → approves/rejects → done.

This has NEVER happened. Everything before this point is preparation.

---

*Document continues in fleet-vision-architecture-part2.md when more code is verified.*
*Next: gateway executor code (OpenClaw vendor), Plane integration details, AICP ↔ fleet bridge.*
