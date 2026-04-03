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

The orchestrator is the brain. It runs in a loop (interval scales with budget mode: 5s turbo / 15s aggressive / 30s standard / 60s economic) and executes 9 steps per cycle:

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

**Before the steps:** Storm monitor evaluates (CRITICAL=stop, STORM=0 dispatch, WARNING=1 dispatch). Gateway duplication check. Fleet mode gate (work_mode, cycle_phase, backend_mode).

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
- `get_mode` from `budget_modes.py`

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

### 3.4 Delivery Phases (Distinct from Stages)

**Source:** `phases.py` (60+ lines)

Stages = how you work on a task. Phases = PO's declaration of
where a deliverable is in its maturity.

`delivery_phase` is a free text field. The PO declares the phase
(any name — "poc", "mvp", "potato") and provides the requirements
for what that phase means for each specific deliverable. No config
file defines phases — each case is different, PO decides per-case.

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

## 8. Fleet Control Settings (IMPLEMENTED)

**Source:** `fleet_mode.py`, `budget_modes.py`

| Setting | What It Controls |
|---------|-----------------|
| work_mode | Where work comes from, dispatch gating (pause/resume) |
| cycle_phase | What kind of work (planning, execution, review, crisis) |
| backend_mode | Which backends enabled (7 combos of Claude/LocalAI/OpenRouter) |
| budget_mode | Fleet tempo (speed/frequency) |

---

## 9. Agent Lifecycle (IMPLEMENTED)

**Source:** `agent_lifecycle.py`

States: `ACTIVE → IDLE → IDLE → SLEEPING → OFFLINE`

Content-aware transitions (from code):
- IDLE after 2 consecutive HEARTBEAT_OK
- SLEEPING after 3 consecutive HEARTBEAT_OK
- `consecutive_heartbeat_ok` and `last_heartbeat_data_hash` fields on AgentState

Time-based fallbacks:
- IDLE after 10min without work
- SLEEPING after 30min idle
- OFFLINE after 4h sleeping

Heartbeat intervals:
- ACTIVE: 0 (agent drives own work)
- IDLE: 30min
- IDLE: 60min
- SLEEPING: 2h
- OFFLINE: 2h

**NOT implemented:** Brain-evaluated heartbeats (the design doc specifies that IDLE/SLEEPING agents get deterministic evaluation instead of Claude calls — the data structures exist but the evaluation logic is not in the orchestrator).

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

Budget mode is a tempo setting — controls fleet speed/frequency.
PO examples: "aggressive" (fast), "economic" (slower). Current: "turbo".

Real quota monitoring via `budget_monitor.py` (Claude OAuth API).
Backend selection is separate: `backend_mode` in `fleet_mode.py` (7 combos).

---

## 13. What's NOT Built — Honest List

### Not in code (design docs only):

1. **Brain-evaluated heartbeats** — IDLE state exists, evaluation logic doesn't
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
`fleet_mode.py`, `budget_modes.py`, `directives.py`, `memory_structure.py`

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

---

## 20. Tool Chains Per Role — What Each Agent Does

Each role uses specific tools in specific sequences. This drives
what goes in CLAUDE.md § Tool Chains and TOOLS.md.

### 20.1 PM (project-manager)

```
Heartbeat: fleet_read_context → assess board → fleet_task_create / fleet_chat
Assign:    fleet_read_context → fleet_plane_sprint → evaluate → fleet_task_create
Unblock:   fleet_read_context → fleet_chat(@agent) → fleet_task_progress
Gate:      fleet_read_context → verify requirements → fleet_task_progress(readiness)
Sprint:    fleet_plane_sprint → fleet_plane_sync → fleet_chat(#sprint)
```

### 20.2 Fleet-Ops

```
Heartbeat: fleet_read_context → check pending approvals → fleet_approve
Review:    fleet_read_context → verify trail → verify PR → fleet_approve(reasoning)
Alert:     fleet_agent_status → fleet_alert → fleet_notify_human (if urgent)
Govern:    fleet_read_context → fleet_chat(#reviews) → fleet_approve
```

### 20.3 Architect

```
Contribute: fleet_read_context → design analysis → fleet_chat(@requester)
Review:     fleet_read_context → architecture review → fleet_approve
Design:     fleet_read_context → fleet_task_accept → fleet_commit → fleet_task_complete
```

### 20.4 DevSecOps

```
Contribute: fleet_read_context → security requirements → fleet_chat(@requester)
PR Review:  fleet_read_context → security scan → fleet_approve
Crisis:     fleet_alert → fleet_notify_human → fleet_pause
Scan:       fleet_read_context → fleet_task_accept → scan → fleet_task_complete
```

### 20.5 Workers (engineer, devops, qa, writer, ux, accountability)

```
Accept:    fleet_read_context → fleet_task_accept(plan)
Work:      fleet_read_context → implement → fleet_commit → fleet_task_progress
Complete:  fleet_commit(final) → fleet_task_complete → PR created → review
Blocked:   fleet_pause(reason) → fleet_escalate (if stuck)
```

### 20.6 Missing Tools (needed for full flow)

| Tool | Who Uses It | Purpose |
|------|-------------|---------|
| `fleet_contribute` | architect, qa, devsecops, ux, writer | Post contribution to another agent's task |
| `fleet_request_input` | any agent | Request missing contribution from PM |
| `fleet_gate_request` | PM, brain | Request PO gate approval at readiness thresholds |

---

## 21. Dynamic Content — What Gets Injected Per Cycle

The brain writes dynamic content to `context/` files every cycle.
This is what agents SEE when they wake up.

### 21.1 fleet-context.md (written every 30s cycle)

```
Generated by: orchestrator._refresh_agent_contexts() → preembed.py
Contains:
  - Fleet state (work_mode, cycle_phase, backend_mode, budget_mode)
  - PO directives (parsed from board memory)
  - Agent statuses (who's active/idle/sleeping)
  - Pending reviews (for fleet-ops)
  - Sprint summary (for PM)
  - Per-role: contributions received, gates pending
```

### 21.2 task-context.md (written at dispatch)

```
Generated by: dispatch.py → context_writer.py
Contains:
  - Task details (title, description, requirement_verbatim)
  - Stage instructions (MUST/MUST NOT/CAN for current stage)
  - Acceptance criteria
  - Contributions received (from architect, qa, devsecops)
  - Related tasks (children, dependencies)
  - Project context (worktree, repo, branch)
```

### 21.3 What's NOT dynamic (static files)

```
IDENTITY.md  — generated once by provision script, committed
SOUL.md      — generated once by provision script, committed
CLAUDE.md    — written per standard, committed
TOOLS.md     — generated from code by generate-tools-md.sh
AGENTS.md    — generated from synergy matrix by generate-agents-md.sh
HEARTBEAT.md — written per standard, committed
```

---

## 22. Settings Integration — 4 Independent Axes

All settings stored in OCMC board `fleet_config` JSON field.
Brain reads every cycle via `read_fleet_control()`.

```
┌─────────────────────────────────────────────────────────┐
│                    OCMC fleet_config                     │
│                                                         │
│  work_mode ──────── what work happens                   │
│  cycle_phase ────── what kind of work                   │
│  backend_mode ───── which backends (7 combos)           │
│  budget_mode ────── fleet tempo (speed/frequency)       │
│                                                         │
│  Each is INDEPENDENT. Any combination valid.            │
└─────────────────────────────────────────────────────────┘

Settings → Brain decisions:

  work_mode = "work-paused"
    → brain skips dispatch entirely
    → agents finish current work, no new tasks
    → heartbeats continue (fleet stays alive)

  work_mode = "finish-current-work"
    → no new task dispatch
    → active agents complete their work
    → PM does NOT pull from Plane

  cycle_phase = "planning"
    → only PM + architect get dispatched to
    → other agents idle

  backend_mode = "claude+localai"
    → router considers both Claude and LocalAI
    → cheapest capable backend wins per task
    → OpenRouter NOT available (not enabled)

  budget_mode = "turbo"
    → faster orchestrator cycle
    → more frequent heartbeats
    → higher operations/minute
```

### 22.1 What's Wired vs What's Not

| Setting | Stored in OCMC | Brain reads it | Brain acts on it | Status |
|---------|---------------|---------------|-----------------|--------|
| work_mode | ✓ | ✓ | ✓ dispatch gate | WORKING |
| cycle_phase | ✓ | ✓ | ✓ agent filter | WORKING |
| backend_mode | ✓ | ✓ | ✗ not passed to router yet | NEEDS WIRING |
| budget_mode | ✓ | ✓ | ✗ tempo not applied yet | NEEDS WIRING + DEFINITIONS |

### 22.2 What "Fully Wired" Looks Like

When PO changes `backend_mode` on OCMC:
1. Brain reads new value next cycle (30s max)
2. Brain passes to `route_task(backend_mode=...)` 
3. Router filters backends → only enabled ones considered
4. Dispatch uses only enabled backends
5. If LocalAI removed → tasks that were going to LocalAI go to Claude
6. If OpenRouter added → cheap tasks may route to free models

When PO changes `budget_mode` on OCMC:
1. Brain reads new value next cycle
2. Brain applies tempo_multiplier to orchestrator interval
3. Brain updates gateway heartbeat CRONs (API or config)
4. Fleet speeds up or slows down

When PO changes `work_mode` to "work-paused":
1. Brain reads → should_dispatch() returns False
2. No new dispatches
3. Active agents finish their current task
4. Heartbeats continue → agents see "fleet paused"
5. Resume → dispatch resumes next cycle

---

## 23. LocalAI Integration — What's Ready

**Source:** AICP project (`../devops-expert-local-ai/`)

### 23.1 Models Available

| Model | Size | Warm Speed | Use Case |
|-------|------|-----------|----------|
| hermes-3b | 2.0GB | ~1.2s | Heartbeats, simple structured tasks |
| hermes-7b | 4.4GB | ~1s | Complex reasoning (one at a time) |
| codellama-7b | 4.4GB | ~1s | Code generation |
| phi-2 | 1.6GB | fast | CPU fallback |

### 23.2 Constraints

- Single-active backend: only ONE GPU model loaded at a time (8GB VRAM)
- Cold start: 10-80s for model swap
- Warm inference: ~1.2s
- Context: 8192 tokens max (vs 200K-1M for Claude)

### 23.3 Router Integration

When `backend_mode` includes "localai":
- Router checks LocalAI health (GET localhost:8090/v1/models)
- Simple/trivial tasks → hermes-3b (free, fast)
- Complex tasks → Claude (reasoning required)
- Fallback: LocalAI down → route to Claude

### 23.4 What's Needed

- Health check wired into orchestrator dispatch loop
- Model selection for LocalAI tasks (hermes-3b vs codellama)
- Gateway support for LocalAI sessions (not just Claude Code)
- Cost tracking: LocalAI sessions = $0 in labor stamps

---

## 24. Per-Agent Ecosystem — MCP Servers, Plugins, Skills

**Source:** `config/agent-tooling.yaml`

Each agent gets role-specific tooling installed via IaC scripts.

### 24.1 Default (all agents)

- **MCP:** fleet server (25 tools via stdio)
- **Plugin:** claude-mem (cross-session memory)

### 24.2 Per-Role Tooling

| Role | MCP Servers | Plugins | Skills |
|------|-------------|---------|--------|
| architect | filesystem, github | context7 | architecture-propose, architecture-review, scaffold |
| software-engineer | filesystem, github, playwright | context7 | feature-implement, refactor-extract |
| qa-engineer | filesystem, playwright | — | quality-coverage, quality-audit, foundation-testing |
| devops | filesystem, github, docker | — | foundation-docker, foundation-ci, ops-deploy, ops-maintenance |
| devsecops-expert | filesystem, docker | — | infra-security, quality-audit |
| fleet-ops | github | — | pm-assess, quality-audit |
| project-manager | github | — | pm-plan, pm-status-report, pm-retrospective, pm-changelog |
| technical-writer | filesystem, github | — | feature-document, pm-changelog, pm-handoff |
| ux-designer | filesystem, playwright | — | quality-accessibility |
| accountability | filesystem | — | quality-audit |

### 24.3 IaC Flow

```
config/agent-tooling.yaml (source of truth)
  ↓
scripts/setup-agent-tools.sh reads YAML
  ↓
For each agent:
  ├── Write .mcp.json (MCP server configs)
  ├── Run: claude plugin install <plugin> (in agent workspace)
  └── Install skills from skill-assignments.yaml
  ↓
scripts/validate-agents.sh verifies:
  ├── .mcp.json exists and valid
  ├── Plugins installed
  └── Skills accessible
```

---

## 25. Gateway Heartbeat System — CRONs

**Source:** `scripts/clean-gateway-config.sh`, gateway config JSON

The gateway fires heartbeats on staggered intervals per agent.
The brain does NOT create Claude sessions — the gateway does.

### 25.1 Current Intervals (from clean-gateway-config.sh)

| Agent | Interval | Why |
|-------|----------|-----|
| fleet-ops | 30m | Board lead, most frequent |
| project-manager | 35m | Sprint management |
| devsecops-expert | 55m | Security watch |
| architect | 60m | Design authority |
| software-engineer | 65m | Primary worker |
| qa-engineer | 70m | Testing |
| devops | 75m | Infrastructure |
| technical-writer | 80m | Documentation |
| ux-designer | 85m | UI/UX |
| accountability | 90m | Governance |

Staggered to prevent session bursts (the March catastrophe).

### 25.2 How Heartbeats Work

```
Gateway CRON fires for agent (every Xm)
  ↓
Gateway creates Claude Code session:
  - Reads agent files (8-file injection order — B0.7)
  - Sets ANTHROPIC_MODEL from agent.yaml
  - Connects MCP server (fleet tools)
  ↓
Agent wakes up inside Claude Code:
  - Sees: IDENTITY + SOUL + CLAUDE.md + TOOLS + AGENTS + context + HEARTBEAT
  - HEARTBEAT.md tells agent what to do (check tasks, review, etc.)
  - Agent calls fleet_read_context → sees fleet state + tasks
  ↓
Agent acts:
  - No work? → HEARTBEAT_OK (brain marks idle after 1)
  - Has task? → accept, work, commit, complete
  - Has review? → review, approve/reject
  - Has alert? → respond, escalate if needed
  ↓
Session ends → gateway records result
```

### 25.3 Budget Mode Tempo Effect (TBD)

When budget_mode tempo is applied:
- tempo_multiplier adjusts the base intervals
- Faster tempo → shorter intervals → more frequent heartbeats
- Slower tempo → longer intervals → fewer operations/minute
- The base intervals in clean-gateway-config.sh remain the source of truth
- Tempo is an OFFSET applied at runtime

How to sync:
- Option A: Brain updates gateway config via API → gateway reloads
- Option B: Brain writes adjusted intervals to gateway config file → restart
- Option C: Gateway reads tempo from fleet_config and applies offset itself
- TBD — needs PO decision on sync mechanism

---

## 26. Brain 13-Step Cycle — Current Implementation

**Source:** `fleet/cli/orchestrator.py`, brain spec `fleet-elevation/04`
**See also:** §90 for the full 13-step design target with chain registry and logic engine.

Current implementation: 9 steps. Target: 13 steps.

### 26.1 Implemented Steps (in orchestrator.py)

```
Step 0: Context Refresh
  - preembed.py generates per-agent context
  - role_providers.py feeds role-specific data
  - context_writer.py writes fleet-context.md + task-context.md
  - Every agent's context/ dir updated before anything else

Step 1: Security Scan
  - behavioral_security.py scans new/changed tasks
  - Suspicious content → security_hold + alert devsecops

Step 2: Doctor (Immune System)
  - doctor.py runs detection cycle (4/11 detections implemented)
  - Returns: agents_to_skip, tasks_to_block
  - Teaching system generates lessons from detected diseases

Step 3: Ensure Review Approvals
  - Tasks in REVIEW status get approval objects created
  - So fleet-ops can review them in their heartbeat

Step 4: Wake Drivers
  - If pending approvals exist → inject wake message to fleet-ops
  - If unassigned tasks → inject wake message to PM
  - Uses notification_router.py (cooldown prevents spam)

Step 5: Dispatch Ready Tasks
  - Find unblocked INBOX tasks with assigned agents
  - Gate: work_mode allows dispatch?
  - Gate: storm severity allows dispatch?
  - Gate: budget quota safe?
  - Gate: agent circuit breaker closed?
  - Gate: doctor hasn't flagged agent/task?
  - Score tasks (task_scoring.py) → dispatch highest first
  - Select model (model_selection.py) → opus/sonnet by complexity
  - Write dispatch context → update task status → emit events
  - Max: config max_dispatch_per_cycle (default 2)

Step 6: Process Directives
  - Read PO directives from board memory
  - Parse tags, targets, urgency
  - Format for agent injection in next heartbeat

Step 7: Evaluate Parents
  - When ALL children of a parent task are DONE → parent to REVIEW
  - Recursive: grandparent checked too

Step 8: Health Check
  - Stuck tasks (IN_PROGRESS > threshold)
  - Offline agents (no heartbeat > threshold)
  - Stale dependencies
```

### 26.2 Missing Steps (from brain spec fleet-elevation/04)

```
Step 1b: Event Queue (chain_registry.py)
  - Process events from previous cycle
  - Dispatch to registered handlers
  - Cascade: handler may produce new events

Step 3b: Gate Processing
  - PO gates at readiness 90%
  - Verify PO approval before advancing to WORK

Step 4b: Contribution Management
  - When task enters REASONING → create contribution subtasks
  - Check: all required contributions received?
  - Pre-embed contributions into worker context

Step 9: Cross-Task Propagation
  - Child completion → update parent progress
  - Contribution → notify target agent

Step 10: Session Management
  - Two parallel countdowns (context remaining + rate limit)
  - Per-agent context evaluation
  - Aggregate fleet math (5×200K near rollover = risk)
  - Force compact near rollover

Step 11: Extended Health + Budget
  - Budget alerts at thresholds
  - Combined health + budget assessment

Step 12: Directive Processing (extended)
  - Multi-turn directive resolution
```

---

## 27. End-to-End Task Lifecycle — The Full Movie

**What this section is:** A single task traced through every system it touches,
from PO idea to DONE. Every function, every API call, every surface touched.
This is not a summary — it's the actual path through code.

### 27.1 Act 1: Task Creation

**PO creates issue on Plane** (or OCMC directly)

```
PO writes issue on Plane (DSPD project)
  │
  ├─ Option A: Plane sync (plane_sync.py:ingest_from_plane)
  │   Brain reads Plane issues → creates MC tasks
  │   Only when work_mode allows: should_pull_from_plane() ✓
  │   Tags: project:{name}, source:plane, issue:{id}
  │
  ├─ Option B: PO creates directly on OCMC
  │   POST /api/v1/boards/{board_id}/tasks
  │   With custom_fields: agent_name, project, task_stage, task_readiness
  │
  └─ Option C: PM heartbeats → sees unassigned work → creates subtasks
      PM calls fleet_create_task (MCP tool)
      Sets: agent, priority, requirement_verbatim, parent_task
```

**Task enters INBOX status.** Custom fields set:
- `agent_name` — who will work on it
- `project` — which repo
- `task_stage` — starts at "conversation" (stage 1 of 5)
- `task_readiness` — starts at 0 (must reach 99 for dispatch)

**Systems touched:** Plane (17), MCP Tools (8), OCMC (Mission Control)

### 27.2 Act 2: Task Readiness — Stages Before Dispatch

Tasks are NOT dispatched immediately. They progress through methodology stages:

```
Stage 1: CONVERSATION (readiness 0-20%)
  PO and PM discuss requirements
  PM fills: requirement_verbatim, acceptance_criteria
  Brain pre-embeds stage instructions via context_writer.py

Stage 2: ANALYSIS (readiness 20-50%)
  Agent (if assigned) reads context, understands scope
  Brain writes analysis data to task-context.md

Stage 3: INVESTIGATION (readiness 50-80%)
  Agent researches codebase, identifies approach
  Brain provides: artifact state, related tasks, dependencies

Stage 4: REASONING (readiness 80-99%)
  Agent plans implementation
  Agent calls fleet_task_accept(plan) — ONLY allowed in this stage
  plan_quality.py validates plan (not rubber stamp)
  Task readiness → 99 when PO confirms plan

Stage 5: WORK (readiness 99-100%)
  Task is now DISPATCHABLE
  Only now can agent call fleet_commit and fleet_task_complete
```

**Systems touched:** Methodology (1), Standards (9), Context/Session (19)
**Enforcement:** MCP tools.py:130-171 — stage-gated tool access

### 27.3 Act 3: Brain Dispatch Decision

Every 30 seconds, the orchestrator cycle runs. Here's what happens to our task:

```
Orchestrator cycle starts
  │
  ├─ Step 0: Context Refresh
  │   preembed.py:build_heartbeat_preembed()
  │   context_writer.py:write_heartbeat_context()
  │   → agents/{agent}/context/fleet-context.md updated
  │   → agents/{agent}/context/task-context.md updated
  │   Includes: task details, stage instructions, role data
  │
  ├─ Step 1: Security Scan
  │   behavioral_security.py scans task content
  │   Suspicious? → security_hold + alert devsecops
  │
  ├─ Step 2: Doctor Check
  │   doctor.py:run_doctor_cycle()
  │   Is assigned agent healthy? Stuck? Correction threshold?
  │   Returns: agents_to_skip, tasks_to_block
  │
  ├─ Step 5: Dispatch Decision (10 gates)
  │   │
  │   ├─ Gate 1: work_mode allows dispatch?
  │   │   fleet_mode.py:should_dispatch(state)
  │   │   "work-paused" or "finish-current" → BLOCKED
  │   │
  │   ├─ Gate 2: Storm severity allows?
  │   │   storm_monitor.py:evaluate()
  │   │   CRITICAL → halt. STORM → 0 dispatch. WARNING → 1 max
  │   │
  │   ├─ Gate 3: Budget quota safe?
  │   │   budget_monitor.py:check_quota()
  │   │   Weekly ≥90% or session ≥95% → BLOCKED
  │   │
  │   ├─ Gate 4: Task readiness ≥ 99?
  │   │   Methodology gate — incomplete tasks wait
  │   │
  │   ├─ Gate 5: Task has assigned agent?
  │   │   No agent → stays in inbox for PM
  │   │
  │   ├─ Gate 6: Task not blocked by dependencies?
  │   │   is_blocked check on task
  │   │
  │   ├─ Gate 7: Agent not already busy?
  │   │   Max 1 concurrent task per agent
  │   │
  │   ├─ Gate 8: Agent not flagged by doctor?
  │   │   doctor_report.agents_to_skip
  │   │
  │   ├─ Gate 9: Agent active in current phase?
  │   │   fleet_mode.py:get_active_agents_for_phase()
  │   │   Planning phase → only PM + architect
  │   │
  │   └─ Gate 10: Max dispatch per cycle?
  │       config max_dispatch_per_cycle (default 2)
  │
  └─ ALL gates pass → DISPATCH
```

**Task scoring** (task_scoring.py:score_task):
- Priority weight: urgent=100, high=75, medium=50, low=25
- Task type bonus: blocker=+30, story=+10, task=+5
- Dependency chain bonus: downstream_count × 10 (max +40)
- Wait bonus: hours_waiting × 2 (max +20)
- Penalty: story_points ≥ 8 → -5
- Highest score dispatches first

**Systems touched:** Control (5), Storm (11), Budget (12), Methodology (1),
Lifecycle (6), Orchestrator (7), Router (14)

### 27.4 Act 4: Dispatch to Gateway

```
dispatch.py:_run_dispatch(agent_name, task_id, project)
  │
  ├─ Resolve agent info via mc.list_agents()
  │   Get: agent_id, session_key, board_id
  │
  ├─ Fetch task details via mc.get_task()
  │
  ├─ Setup git worktree (if project specified)
  │   projects/{project}/worktrees/{agent}-{task_short}/
  │
  ├─ Select model via model_selection.py:select_model_for_task()
  │   Complex/critical → opus. Standard → sonnet.
  │   Security/architecture agents → always opus.
  │
  ├─ Route backend via backend_router.py:route_task()
  │   Read backend_mode from FleetControlState
  │   backends_for_mode() → enabled list
  │   Filter by: capabilities, availability, security constraints
  │   Sort by cost → cheapest capable wins
  │
  ├─ Save DispatchRecord (labor attribution)
  │   state/dispatch_records/{task_short}.json
  │   Contains: agent, model, effort, timestamp
  │
  ├─ Build dispatch message with full task context
  │
  ├─ SEND TO GATEWAY via WebSocket RPC
  │   gateway_client.py → ws://localhost:18789
  │   Method: chat.send
  │   Params: {sessionKey, message, deliver:false, idempotencyKey}
  │   Agent's Claude session receives task in system prompt
  │
  ├─ Update task status on MC
  │   PATCH custom_fields: {agent_name, worktree}
  │
  └─ Notify IRC: "[orchestrator] Dispatched {task} to {agent}"
```

**Systems touched:** Router (14), Models (16), Infrastructure (20),
Gateway (OpenClaw), Labor (13)

### 27.5 Act 5: Agent Works

The agent is a Claude Code session managed by OpenClaw Gateway.
It receives context via two paths:

```
PATH 1: Pre-embedded files (read by gateway at session start)
  agents/{agent}/
  ├── IDENTITY.md      → Who am I (fleet identity, name, role)
  ├── SOUL.md          → Values, boundaries, anti-corruption
  ├── CLAUDE.md        → Role-specific rules, tool usage, methodology
  ├── TOOLS.md         → Available tools + call chains + side effects
  ├── AGENTS.md        → Knowledge of colleagues + synergy map
  ├── context/
  │   ├── fleet-context.md  → Current fleet state, directives, messages
  │   └── task-context.md   → Full task details, stage instructions
  └── HEARTBEAT.md     → Action protocol (what to do each heartbeat)

  Injection order: IDENTITY→SOUL→CLAUDE→TOOLS→AGENTS→context→HEARTBEAT
  ⚠️ B0.7: Gateway currently only reads CLAUDE.md + context/

PATH 2: MCP tool calls (agent pulls data on demand)
  fleet_read_context(task_id)  → Full task details from MC
  fleet_agent_status()         → Fleet state, health
  fleet_heartbeat_context()    → What happened since last heartbeat
```

**Agent work cycle:**

```
Agent heartbeats (gateway CRON triggers)
  │
  ├─ Reads context: fleet-context.md + task-context.md
  │
  ├─ Calls fleet_read_context(task_id) for full task data
  │   Returns: requirement_verbatim, acceptance_criteria,
  │   stage instructions, artifact state, related tasks
  │
  ├─ Stage enforcement: MCP checks current stage
  │   WORK_ONLY_TOOLS = {fleet_commit, fleet_task_complete}
  │   Agent in REASONING → can fleet_task_accept but not fleet_commit
  │   Agent in WORK → can fleet_commit and fleet_task_complete
  │
  ├─ Agent implements (reads code, writes code, runs tests)
  │
  ├─ fleet_commit(files, message) — stage-gated to WORK
  │   git add {files}
  │   git commit -m "{message} [task:{id}]"
  │   Returns: sha, message
  │
  ├─ fleet_task_complete(summary) — stage-gated to WORK
  │   (see Act 6 below)
  │
  └─ Between heartbeats: brain refreshes context every 30s
      New directives, messages, contributions appear in next heartbeat
```

**Systems touched:** MCP Tools (8), Methodology (1), Standards (9),
Gateway (OpenClaw), Session (19)

### 27.6 Act 6: Task Completion — The Event Chain

When agent calls `fleet_task_complete(summary)`, this triggers a cascade
across all 6 surfaces:

```
fleet_task_complete(summary) — mcp/tools.py:525-903
  │
  ├─ 1. Run tests: pytest --tb=line -q
  │   Capture: pass/fail, output
  │
  ├─ 2. Get branch: git rev-parse --abbrev-ref HEAD
  │
  ├─ 3. Get commits: git log --oneline (since dispatch)
  │
  ├─ 4. Push branch: git push origin {branch}
  │
  ├─ 5. Create PR on GitHub
  │   Title, body, labels, assignee
  │   Returns: pr_url, pr_number
  │
  ├─ 6. Create labor stamp
  │   Read dispatch_record → compute elapsed time
  │   labor_stamp.py:create_labor_stamp()
  │
  ├─ 7. Update task status: IN_PROGRESS → REVIEW
  │   PATCH /api/v1/boards/{board_id}/tasks/{task_id}
  │
  ├─ 8. Create approval for fleet-ops
  │   POST /api/v1/boards/{board_id}/approvals
  │   confidence: 85 (if tests pass) - compliance_penalty
  │   rubric_scores: {correctness, completeness, quality, tests, compliance}
  │
  ├─ 9. Fire event chain: build_task_complete_chain()
  │   │
  │   ├─ INTERNAL (required):
  │   │   update_task_status → REVIEW
  │   │   create_approval → pending for fleet-ops
  │   │   post_board_memory → completion summary with tags
  │   │
  │   ├─ PUBLIC (conditional):
  │   │   push_branch (if code changes)
  │   │   create_pr (if branch pushed)
  │   │
  │   ├─ CHANNEL (optional):
  │   │   IRC #fleet: "[agent] PR READY: {summary}"
  │   │   IRC #reviews: "[agent] Review: {pr_url}"
  │   │
  │   ├─ NOTIFY (optional):
  │   │   ntfy: "Task completed: {summary}" (priority: info)
  │   │
  │   ├─ PLANE (optional):
  │   │   Update issue state → "In Review"
  │   │   Post comment with completion details
  │   │
  │   └─ META:
  │       Log metrics: agent, task_id, elapsed, model
  │
  └─ 10. Emit CloudEvent: fleet.task.completed
      Stored in JSONL event log
      Subject: task_id, surfaces hit, agent
```

**Chain execution tolerance:** Required surfaces (INTERNAL) must succeed.
Optional surfaces (CHANNEL, NOTIFY, PLANE) can fail without blocking.
chain_runner.py tracks: total_events, executed, failed, errors.

**Systems touched:** MCP Tools (8), Event Bus (4), Notifications (18),
Plane (17), Labor (13), Standards (9), Infrastructure (20)

### 27.7 Act 7: Fleet-Ops Review

```
Brain detects: task in REVIEW with pending approval
  │
  ├─ Step 3: _ensure_review_approvals()
  │   If no approval exists → create one (safety net)
  │
  ├─ Step 4: _wake_drivers()
  │   inject_content(fleet-ops.session_key, wake_message)
  │   Cooldown: 300s between review wakes (prevent spam)
  │   Wake message includes: task title, PR URL, agent name
  │
  └─ Fleet-ops heartbeats → sees pending approval in context
      │
      ├─ fleet-ops reads:
      │   - PR diff (GitHub)
      │   - Test results
      │   - Completion summary
      │   - Acceptance criteria (from requirement_verbatim)
      │   - Labor stamp (time, model, effort)
      │   - Trail: commits, branch, files changed
      │
      ├─ 7-STEP REAL REVIEW (per heartbeat standard):
      │   1. Read task requirement verbatim
      │   2. Read PR diff completely
      │   3. Verify acceptance criteria met (each one)
      │   4. Check trail (commits, tests, coverage)
      │   5. Verify no scope creep (only what was asked)
      │   6. Check quality (code style, security, architecture)
      │   7. Decision with reasoning
      │
      ├─ APPROVE: fleet_approve(task_id, reasoning)
      │   MCP tool updates approval status → APPROVED
      │   Confidence: 80-95 based on criteria
      │   Reasoning: specific, not rubber stamp
      │
      └─ REJECT: fleet_approve(task_id, reasoning, approved=false)
          Approval status → REJECTED
          Task regresses: readiness drops, stage may revert
          Agent gets feedback in next heartbeat context
```

**Systems touched:** Orchestrator (7), Lifecycle (6), MCP Tools (8),
Standards (9), Immune System (2) — if fleet-ops auto-approves, doctor detects

### 27.8 Act 8: Transition to DONE

```
Brain detects: task has APPROVED approval
  │
  ├─ Step in orchestrator: _transition_approved_reviews()
  │   mc.update_task(status="done")
  │   Post comment: "Auto-transitioned to done — approval granted"
  │   IRC: "[orchestrator] ✅ DONE: {task_title}"
  │
  ├─ Parent evaluation (Step 7: _evaluate_parents)
  │   All children DONE → parent moves to REVIEW
  │   Recursive: grandparent checked too
  │
  ├─ Plane sync:
  │   Issue state → "Done"
  │   Comment posted with completion details
  │
  └─ Labor attribution:
      DispatchRecord + LaborStamp → full audit trail
      Who worked, what model, how long, what was produced
```

**Systems touched:** Orchestrator (7), Plane (17), Labor (13), Event Bus (4)

### 27.9 Systems Touched Summary

```
Total systems involved in one task lifecycle: 17 of 20

  ✓ Methodology (1)    — 5-stage progression, tool gating
  ✓ Immune System (2)  — disease detection during work
  ✓ Teaching (3)        — lessons injected if disease found
  ✓ Event Bus (4)       — event chain on completion, JSONL storage
  ✓ Control Surface (5) — work_mode, cycle_phase gating
  ✓ Agent Lifecycle (6) — sleep/wake, state management
  ✓ Orchestrator (7)    — 13-step brain cycle, dispatch, transitions
  ✓ MCP Tools (8)       — 25 stage-gated tools
  ✓ Standards (9)       — compliance check on completion
  ✓ Transpose (10)      — artifact rendering (if artifact produced)
  ✓ Storm (11)          — severity gating on dispatch
  ✓ Budget (12)         — quota check before dispatch
  ✓ Labor (13)          — dispatch records, labor stamps
  ✓ Router (14)         — backend selection
  ✗ Challenge (15)      — not wired into completion flow yet
  ✓ Models (16)         — model selection for dispatch
  ✓ Plane (17)          — issue sync, comments, state updates
  ✓ Notifications (18)  — IRC, ntfy on completion
  ✓ Session (19)        — context management, pre-embed
  ✓ Infrastructure (20) — gateway RPC, health checks

Not yet in lifecycle: Challenge (15) — needs wiring (M3 backlog item)
```

---

## 28. OCMC ↔ Brain ↔ Gateway — The Three-System Protocol

**What this section is:** The exact API calls, data formats, timing, and sync
mechanisms between the three core services. Not summaries — actual endpoints,
payloads, and sequences verified from mc_client.py, gateway_client.py, and
orchestrator.py.

### 28.1 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    OCMC (Mission Control)                            │
│                    http://localhost:8000                              │
│                    REST API — JSON payloads                          │
│                                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Tasks   │ │  Agents  │ │  Board   │ │Approvals │ │  Memory  │ │
│  │  CRUD    │ │  List    │ │fleet_conf│ │  CRUD    │ │directives│ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ REST API (every 30s cycle)
                             │
┌────────────────────────────┼────────────────────────────────────────┐
│                    BRAIN (Orchestrator)                              │
│                    fleet/cli/orchestrator.py                         │
│                    30-second Python loop                             │
│                    Reads from OCMC, writes to Gateway + files        │
│                                                                     │
│  Reads: tasks, agents, board (fleet_config), memory, approvals      │
│  Writes: task updates, approvals, comments, memory entries          │
│  Controls: gateway sessions (inject, prune, compact, create)        │
│  Writes to disk: agents/{name}/context/*.md (every cycle)           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ WebSocket JSON-RPC v3
                             │ ws://localhost:18789
                             │
┌────────────────────────────┼────────────────────────────────────────┐
│                    GATEWAY (OpenClaw)                                │
│                    HTTP :9400 + WS :18789                            │
│                                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │ Sessions │ │  CRONs   │ │  MCP     │ │  Agent   │              │
│  │ manage   │ │heartbeats│ │  server  │ │  Claude  │              │
│  │          │ │ per-agent│ │ 25 tools │ │ sessions │              │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘              │
│                                                                     │
│  Reads from disk: agents/{name}/ files → system prompt              │
│  Runs: claude --permission-mode bypassPermissions                   │
│  MCP: python -m fleet.mcp.server (stdio, per-session)               │
└─────────────────────────────────────────────────────────────────────┘
```

### 28.2 Brain → OCMC: Every API Call

**Source:** `fleet/infra/mc_client.py`

```
READ operations (every 30s cycle):

  GET /api/v1/agents
    → All agents with session_keys, board_ids, status
    → Cached 60s (mc_client.py Cache object)
    → Used by: dispatch (resolve agent), context refresh

  GET /api/v1/boards/{board_id}
    → Board data INCLUDING fleet_config JSON field
    → fleet_config: {work_mode, cycle_phase, backend_mode, updated_at, updated_by}
    → Used by: fleet_mode.py:read_fleet_control()

  GET /api/v1/boards/{board_id}/tasks
    → All tasks on board, optionally filtered by status
    → Cached 30s
    → Used by: dispatch, parent evaluation, health check

  GET /api/v1/boards/{board_id}/memory?limit=30
    → Board memory entries (directives, messages, mentions)
    → Tags: ["directive", "to:{agent}", "from:human", "urgent"]
    → Used by: context refresh (Step 0), directive processing (Step 6)

  GET /api/v1/boards/{board_id}/approvals
    → Pending/approved/rejected approvals
    → Used by: ensure_review_approvals (Step 3), transition (Step 2)

WRITE operations (conditional, within cycle):

  PATCH /api/v1/boards/{board_id}/tasks/{task_id}
    → Update: status, priority, custom_fields, comments, tags, dependencies
    → Used by: dispatch (set agent), transition (REVIEW→DONE), health remediation

  POST /api/v1/boards/{board_id}/tasks
    → Create task (remediation, subtasks)
    → Used by: health check, contribution management (future)

  POST /api/v1/boards/{board_id}/tasks/{task_id}/comments
    → Post comment on task
    → Used by: transition ("Auto-transitioned to done"), dispatch notes

  POST /api/v1/boards/{board_id}/approvals
    → Create approval for review task
    → Used by: ensure_review_approvals (orphan safety net)

  POST /api/v1/boards/{board_id}/memory
    → Post directive/message to board memory
    → Used by: event chains (completion summary)
```

### 28.3 Brain → Gateway: Every API Call

**Source:** `fleet/infra/gateway_client.py`
**Protocol:** WebSocket JSON-RPC v3 on ws://localhost:18789

```
WebSocket handshake (every call — no persistent connection):

  1. Connect: ws://localhost:18789
  2. Receive challenge from gateway
  3. Authenticate:
     {
       type: "req",
       method: "connect",
       params: {
         minProtocol: 3, maxProtocol: 3,
         role: "operator",
         scopes: ["operator.read", "operator.admin",
                  "operator.approvals", "operator.pairing"],
         auth: {token: <from ~/.openclaw/openclaw.json>}
       }
     }
  4. Receive auth response (ok/fail)
  5. Send RPC method
  6. Receive response (poll up to 10 messages for matching ID)
  7. Close connection

RPC methods:

  chat.send — Inject content into agent session
    Params: {sessionKey, message, deliver: false, idempotencyKey}
    Used by: dispatch (task message), wake drivers (PM/fleet-ops),
             doctor (teaching injection)
    Frequency: 2-4 per cycle (dispatch + wakes)

  sessions.delete — Kill agent session (prune)
    Params: {key: session_key}
    Used by: doctor intervention (PRUNE response)
    Frequency: Rare (disease detection only)

  sessions.compact — Reduce agent context
    Params: {key: session_key}
    Used by: doctor intervention (FORCE_COMPACT response),
             session management (near rollover)
    Frequency: Rare

  sessions.patch — Create fresh session
    Params: {key: session_key, label?: agent_name}
    Used by: agent provisioning (first setup), post-prune recovery
    Frequency: Rare (setup only)

CRON management (file-based, NOT RPC):

  Read/write: ~/.openclaw/cron/jobs.json
    disable_gateway_cron_jobs() — set enabled:false on all jobs
      Used by: MC outage handling
    enable_gateway_cron_jobs() — re-enable + reset error counts
      Used by: MC recovery
    check_cron_circuit_breaker() — disable jobs with >3 consecutive errors
      Used by: every cycle (protection)
```

### 28.4 Gateway → Agents: File-Based Injection

```
Gateway does NOT receive API calls from brain for context.
Instead, brain writes files to disk, gateway reads them.

Brain writes (every 30s):
  agents/{name}/context/fleet-context.md
  agents/{name}/context/task-context.md

Gateway reads (at agent heartbeat):
  agents/{name}/CLAUDE.md         → max 2000 chars (⚠️ should be 4000)
  agents/{name}/context/*.md      → max 1000 chars each (⚠️ should be 8000)
  ⚠️ Does NOT read: IDENTITY.md, SOUL.md, TOOLS.md, AGENTS.md, HEARTBEAT.md

This is blocker B0.7 — gateway injection order not implemented.
```

### 28.5 Settings Flow: OCMC → Brain → Operations

```
PO changes setting on OCMC board (fleet_config JSON field)
  │
  ↓ Brain reads GET /api/v1/boards/{board_id} every 30s
  │
  ↓ fleet_mode.py:read_fleet_control(board_data)
  │   Extracts: work_mode, cycle_phase, backend_mode
  │   Returns: FleetControlState dataclass
  │
  ↓ Brain compares with previous state
  │   Changed? → emit fleet.system.mode_changed event → log IRC
  │
  ↓ Settings applied within same cycle:
  │
  ├─ work_mode → should_dispatch() gate
  │   "work-paused" → skip dispatch entirely
  │   "finish-current" → no new tasks
  │   "local-work-only" → PM doesn't pull from Plane
  │
  ├─ cycle_phase → get_active_agents_for_phase() filter
  │   "planning" → only PM + architect
  │   "crisis" → only fleet-ops + devsecops
  │   "execution" → all agents
  │
  ├─ backend_mode → route_task() backend selection
  │   ⚠️ NOT WIRED: orchestrator doesn't pass to router yet
  │   Code ready: backends_for_mode() in backend_router.py
  │
  └─ budget_mode → tempo offset
      ⚠️ NOT WIRED: no tempo applied to cycle interval or CRONs
      Structure ready: BudgetMode dataclass in budget_modes.py

Latency: PO changes setting → brain picks up within 30s
         Brain applies → agents see in next heartbeat (CRON interval)
         Total: 30s to ~90min depending on agent heartbeat schedule
```

### 28.6 Timing Summary

```
Brain cycle interval:            Scales with budget mode:
                                 5s turbo / 15s aggressive /
                                 30s standard / 60s economic
Task cache TTL:                  Matches cycle interval
Agent cache TTL:                 60 seconds
Budget quota cache TTL:          300 seconds (5 minutes)
Driver wake cooldown:            120 seconds
Review wake cooldown:            300 seconds
Gateway RPC timeout:             10 seconds per call
Max dispatch per cycle:          2 tasks (configurable)
Task readiness gate:             ≥99 to dispatch
Agent heartbeat CRONs:           30-90 min (staggered per role)
```

---

## 29. CRON Sync Mechanism — How Tempo Reaches Gateway

**What this section is:** The design for how budget_mode tempo changes
propagate from OCMC through brain to gateway heartbeat CRONs. This is
NOT IMPLEMENTED — this section defines what needs to be built.

### 29.1 Current State

```
Gateway CRONs are STATIC — set by scripts/clean-gateway-config.sh:

  Agent              Interval    Stagger
  fleet-ops          30 min      0
  project-manager    30 min      5
  devsecops-expert   45 min      10
  accountability     90 min      15
  architect          60 min      0
  software-engineer  60 min      10
  devops-engineer    60 min      20
  qa-engineer        60 min      30
  technical-writer   90 min      0
  ux-designer        90 min      10

  Set once. Never change. Budget mode has no effect.
```

### 29.2 Target Design

```
Budget mode = tempo offset applied to base CRON intervals.

  BudgetMode:
    name: str                  # "turbo", "standard", "economic" (TBD by PO)
    description: str
    tempo_multiplier: float    # offset applied to base intervals

  Example (PO to define actual values):
    turbo:     tempo_multiplier = 0.5   → 30min becomes 15min
    standard:  tempo_multiplier = 1.0   → 30min stays 30min
    economic:  tempo_multiplier = 2.0   → 30min becomes 60min

  Applied to:
    1. Gateway CRON intervals (heartbeat frequency)
    2. Orchestrator cycle interval (brain speed)
    3. Driver wake cooldowns (PM/fleet-ops responsiveness)

  Formula:
    effective_interval = base_interval × tempo_multiplier
```

### 29.3 Sync Mechanism Options

```
Option A: File-based (like current CRON management)
  Brain writes updated intervals to ~/.openclaw/cron/jobs.json
  Gateway picks up on next cron check cycle
  Pro: consistent with existing disable/enable pattern
  Con: gateway must poll for changes

Option B: RPC-based
  New gateway RPC method: cron.update
  Brain sends: {sessionKey, interval: new_seconds}
  Pro: immediate, no polling
  Con: requires gateway code change

Option C: Config reload signal
  Brain updates config file + sends SIGHUP or reload RPC
  Gateway re-reads entire cron config
  Pro: simple, atomic
  Con: requires gateway to support reload

Current leaning: Option A (file-based) — matches existing pattern in
gateway_client.py:disable_gateway_cron_jobs() which already reads/writes
~/.openclaw/cron/jobs.json directly.
```

### 29.4 Sync Flow (Target)

```
PO changes budget_mode on OCMC (e.g., "turbo" → "economic")
  │
  ↓ Brain reads fleet_config (next 30s cycle)
  │
  ↓ Brain detects budget_mode changed
  │
  ├─ Calculate new intervals:
  │   For each agent:
  │     new_interval = base_interval × tempo_multiplier
  │     new_interval = max(new_interval, MIN_HEARTBEAT_INTERVAL)
  │     new_interval = min(new_interval, MAX_HEARTBEAT_INTERVAL)
  │
  ├─ Update gateway CRONs:
  │   Read ~/.openclaw/cron/jobs.json
  │   For each agent job:
  │     Update interval_seconds = new_interval
  │     Preserve stagger offsets
  │   Write updated jobs.json
  │
  ├─ Update orchestrator cycle:
  │   self._interval = base_interval × tempo_multiplier
  │
  ├─ Update wake cooldowns:
  │   driver_wake_cooldown = base_cooldown × tempo_multiplier
  │   review_wake_cooldown = base_cooldown × tempo_multiplier
  │
  ├─ Emit event: fleet.system.tempo_changed
  │
  └─ IRC: "[brain] Tempo changed: {old} → {new}, intervals updated"
```

### 29.5 Guard Rails

```
MIN_HEARTBEAT_INTERVAL = 300    # 5 minutes (prevent runaway costs)
MAX_HEARTBEAT_INTERVAL = 7200   # 2 hours (prevent dead fleet)
MIN_CYCLE_INTERVAL = 15         # 15 seconds (brain speed floor)
MAX_CYCLE_INTERVAL = 120        # 2 minutes (brain speed ceiling)

Storm override: during STORM/CRITICAL severity, tempo changes are
IGNORED — storm response takes precedence over budget tempo.

Rate limit override: near rate limit window rollover, brain may
temporarily slow tempo regardless of budget_mode setting.
```

---

## 30. Contribution Flow — End-to-End Cross-Agent Synergy

**What this section is:** How specialists contribute to each other's work.
The FULL flow from task entering REASONING through contribution delivery
to pre-embedded context. This is NOT IMPLEMENTED — `fleet_contribute` tool
does not exist yet. This section defines the complete design.

### 30.1 The Contribution Model

```
When a task enters REASONING stage, brain creates parallel contribution
subtasks based on the synergy matrix (fleet-elevation/15).

Example: Software Engineer task "Implement auth middleware"

  Brain detects: task.stage = "reasoning", task.agent = "software-engineer"
  Brain reads synergy matrix → who contributes to engineer work?

  Creates parallel subtasks:
    ├─ architect:     "Design input for auth middleware"
    │   Type: design_input
    │   Contains: architecture constraints, patterns, integration points
    │
    ├─ devsecops:     "Security requirements for auth middleware"
    │   Type: security_requirement
    │   Contains: threat model, required controls, compliance needs
    │
    └─ qa-engineer:   "Test strategy for auth middleware"
        Type: qa_test_definition
        Contains: test scenarios, edge cases, acceptance tests

  These are SMALL, FOCUSED tasks — not full implementations.
  They produce artifacts (documents), not code.
```

### 30.2 Synergy Matrix (from fleet-elevation/15)

```
WHO CONTRIBUTES WHAT TO WHOM:

  To engineer work:
    architect    → design_input (architecture constraints)
    devsecops    → security_requirement (threat model, controls)
    qa-engineer  → qa_test_definition (test scenarios)

  To architect work:
    engineer     → feasibility_assessment (can we build this?)
    devsecops    → security_review (architecture security)

  To devops work:
    architect    → infrastructure_design (deployment architecture)
    devsecops    → security_requirement (infrastructure security)
    engineer     → application_requirements (what app needs)

  To qa work:
    engineer     → implementation_context (how it works)
    architect    → design_context (why it works that way)

  To writer work:
    engineer     → technical_accuracy (verify facts)
    architect    → architecture_context (system design)

  To devsecops work:
    architect    → architecture_context (what to secure)
    engineer     → implementation_context (how it's built)

  To PM work:
    all agents   → status_update (progress, blockers)

  Fleet-ops, accountability, UX:
    Receive contributions contextually, not by default matrix
```

### 30.3 Contribution Flow — Step by Step

```
1. TRIGGER: Task enters REASONING stage
   orchestrator.py Step 4b (missing): _manage_contributions()
   Brain reads task.stage, task.agent_name
   Brain looks up synergy matrix for target agent's role

2. CREATE: Brain creates contribution subtasks
   For each contributor in matrix:
     mc.create_task(
       title: "Contribute {type} for: {parent_task_title}",
       agent_name: contributor_agent,
       custom_fields: {
         task_type: "contribution",
         contribution_type: type,     # design_input, security_req, etc.
         parent_task_id: parent_id,
         target_agent: target_agent,
         task_stage: "work",          # contributions skip early stages
         task_readiness: 99           # immediately dispatchable
       }
     )

3. DISPATCH: Normal dispatch cycle picks up contribution tasks
   They pass all gates (readiness 99, agent assigned, not blocked)
   Scored normally — but contribution tasks get bonus? (TBD)

4. WORK: Contributor agent works on contribution
   Agent reads context: parent task details, what's needed
   Agent calls fleet_contribute(contribution_text, parent_task_id)
   ⚠️ fleet_contribute MCP tool does NOT EXIST yet
   
   fleet_contribute should:
   - Validate: contribution matches requested type
   - Store: contribution attached to parent task
   - Emit: fleet.contribution.submitted event
   - Notify: target agent via context refresh
   - Update: contribution subtask → DONE

5. PRE-EMBED: Brain embeds contributions into target agent context
   Next context refresh (Step 0):
   Target agent's fleet-context.md includes:
     ## INPUTS FROM COLLEAGUES
     ### Design Input (from architect)
     {contribution_text}
     ### Security Requirements (from devsecops)
     {contribution_text}
     ### Test Strategy (from qa-engineer)
     {contribution_text}

6. CONSUME: Target agent reads contributions in next heartbeat
   Agent's CLAUDE.md instructs: "Reference contributions in your plan"
   Agent's work MUST acknowledge received inputs
   Anti-corruption: agents cannot ignore contributions

7. TRACK: Brain tracks contribution completeness
   All required contributions received? → Parent task can proceed
   Missing contributions? → Brain waits (configurable timeout)
   Timeout exceeded? → Proceed without, log gap
```

### 30.4 Missing Pieces for Contribution Flow

```
Code needed:
  1. fleet_contribute MCP tool         — mcp/tools.py (new tool)
  2. fleet_request_input MCP tool      — mcp/tools.py (agent asks for help)
  3. contributions.py brain module     — fleet/core/contributions.py (new)
  4. Synergy matrix config             — config/synergy-matrix.yaml (new)
  5. Pre-embed contribution section    — preembed.py update
  6. Contribution event chain          — event_chain.py:build_contribution_chain()

Design decisions needed:
  - Contribution timeout (how long to wait before proceeding?)
  - Contribution quality gate (who validates contribution quality?)
  - Contribution stage gating (should contributors use fleet_commit?)
  - Scoring bonus for contribution tasks (priority boost?)
```

---

## 31. Review Flow — Fleet-Ops 7-Step REAL Review

**What this section is:** The detailed review protocol that fleet-ops follows
when approving or rejecting work. Not a rubber stamp — a genuine quality gate.

### 31.1 Review Trigger

```
Agent calls fleet_task_complete(summary)
  ↓
Event chain fires:
  - Task status → REVIEW
  - Approval created (PENDING, confidence based on tests)
  - IRC #reviews: "[agent] Review: {pr_url}"
  - ntfy: "Task completed: {summary}"
  ↓
Brain detects REVIEW task with pending approval (Step 3)
  ↓
Brain wakes fleet-ops: inject_content(wake_message)
  Cooldown: 300s between review wakes
  Wake includes: task title, PR URL, agent name, priority
  ↓
Fleet-ops heartbeats → sees pending review in context
```

### 31.2 The 7-Step REAL Review Protocol

```
Fleet-ops receives in context:
  - Task: title, requirement_verbatim, acceptance_criteria
  - PR: url, diff stats, files changed, commits
  - Test results: pass/fail, coverage
  - Labor stamp: agent, model, effort, elapsed time
  - Self-reported confidence: 50-95%

STEP 1: READ REQUIREMENT
  Read the original requirement_verbatim word by word.
  What was ACTUALLY asked? Not the summary — the original words.
  Compare with acceptance_criteria list.

STEP 2: READ THE DIFF
  Read the FULL PR diff. Not just file names — actual code changes.
  Every line added, every line removed, every file touched.
  For large PRs: read in sections, track what each section does.

STEP 3: VERIFY ACCEPTANCE CRITERIA
  For EACH acceptance criterion:
    ✓ Is it met by the code changes?
    ✗ Is it partially met?
    ✗ Is it not addressed at all?
  All criteria must be ✓ for approval.

STEP 4: CHECK TRAIL
  Verify:
  - Commits follow conventional format? (type(scope): description)
  - Tests exist for new code? Tests pass?
  - Coverage maintained or improved?
  - Branch naming correct? (task-{id}-{description})
  - Labor stamp reasonable? (time vs complexity)

STEP 5: VERIFY NO SCOPE CREEP
  Did the agent do MORE than asked?
  - Refactored unrelated code? → Flag
  - Added features not in requirements? → Flag
  - Changed files outside task scope? → Flag
  Anti-corruption rule: stay in scope.

STEP 6: QUALITY CHECK
  Code quality:
  - Security: no command injection, XSS, SQL injection
  - Architecture: follows existing patterns
  - Style: consistent with codebase
  - Error handling: appropriate for context
  - No TODO/FIXME without tracking task

STEP 7: DECISION
  APPROVE:
    confidence: 80-95 based on criteria fulfillment
    reasoning: specific reference to what was checked
    NOT "looks good" — MUST cite specific criteria met

  REJECT:
    reasoning: specific failure points
    regressed_readiness: how far to regress (e.g., 80 → back to reasoning)
    regressed_stage: which stage to return to
    feedback: what needs to change

  ESCALATE (to PO):
    If task is too complex for automated review
    If acceptance criteria are ambiguous
    If security concerns found
```

### 31.3 Review Anti-Corruption

```
Fleet-ops MUST NOT:
  1. Auto-approve without reading the diff
  2. Approve with generic reasoning ("looks good", "LGTM")
  3. Skip acceptance criteria verification
  4. Approve when tests fail
  5. Approve scope creep
  6. Approve their own work (if fleet-ops was the worker)

Doctor detection: if fleet-ops approves in <30 seconds → disease
  detect_laziness() catches fast approvals
  Teaching: inject lesson about REAL review protocol

PO override: PO can always override fleet-ops decision
  Either direction — approve rejected, reject approved
```

### 31.4 Post-Review Flow

```
APPROVED:
  Brain: _transition_approved_reviews()
  Task: REVIEW → DONE
  Comment: "Auto-transitioned to done — approval granted"
  IRC: "[orchestrator] ✅ DONE: {task_title}"
  Parent check: all children done? → parent to REVIEW
  Plane: issue state → "Done"

REJECTED:
  Task: stays in REVIEW or regresses to earlier stage
  Agent: gets rejection feedback in next context refresh
  Agent: must address feedback and re-submit
  fleet_task_complete must be called again after fixes
  New review cycle starts

ESCALATED:
  ntfy: PO notification with review context
  Task: stays in REVIEW
  PO: reviews and decides on OCMC
```

---

## 32. Cross-Cutting Scenarios — What Happens When Things Go Wrong

**What this section is:** Six operational scenarios that cut across multiple
systems. Each scenario: trigger, cascade, resolution. All verified from code.

### 32.1 Scenario: Storm Escalation

```
TRIGGER: Multiple indicators confirm simultaneously

Indicator detection (storm_monitor.py:183-192, 9 indicators):
  session_burst     — >10 sessions/min (60s confirmation window)
  fast_climb        — budget +5% in 10 min (300s window)
  void_sessions     — >50% sessions empty (120s window)
  dispatch_storm    — too many dispatches (30s window)
  cascade_depth     — task-creates-task chains too deep (30s)
  agent_thrashing   — wake with no work repeatedly (120s)
  error_storm       — high error rate (60s window)
  gateway_dup       — multiple gateway processes (0s — IMMEDIATE)
  context_pressure  — context used ≥70% (from session_telemetry)

CASCADE:

  1 indicator confirmed → WATCH
    Action: logging only
    Dispatch: unchanged

  2+ indicators → WARNING
    Action: diagnostic snapshot, IRC alert
    Dispatch: max 1 per cycle (was 2)

  3+ indicators → STORM
    Action: alert PO (IRC + ntfy), capture incident
    Dispatch: 0 (complete halt of new work)
    In-progress: continues (agents finish current tasks)

  fast_climb + session_burst together → CRITICAL
    Action: halt_cycle=True (brain returns immediately)
    Dispatch: 0, fleet FROZEN
    All operations: stopped except health monitoring
    Requires: PO intervention to resume

DE-ESCALATION (slow, to prevent oscillation):
  CRITICAL → STORM:  10 min indicator-free
  STORM → WARNING:   10 min indicator-free
  WARNING → WATCH:   15 min indicator-free
  WATCH → CLEAR:     30 min indicator-free

INCIDENT REPORT:
  Auto-generated when severity drops back to CLEAR
  Contains: timeline, indicators, diagnostic snapshots
  Stored: board memory for post-mortem
```

### 32.2 Scenario: Rate Limit Approaching

```
TRIGGER: Claude API usage approaching session or weekly limit

DETECTION (budget_monitor.py):
  OAuth API checked every 5 min (cached)
  Progressive thresholds:
    50% → medium alert (log)
    70% → high alert (IRC)
    80% → high alert (IRC + ntfy)
    90% → CRITICAL → dispatch PAUSED
    95% (session) → dispatch PAUSED

FAST CLIMB detection:
  Two readings, <10 min apart, weekly_pct jumped ≥5%
  → Sets storm indicator "fast_climb"
  → Storm system escalates response

CASCADE:
  1. Dispatch paused (budget_monitor returns not safe)
  2. Storm indicator triggers escalation chain
  3. In-progress agents: continue (already paid for)
  4. New dispatches: held until next rate limit window
  5. PO notified via ntfy (critical severity)

RECOVERY:
  Rate limit window rolls over (5-hour sessions)
  Budget monitor re-checks → safe again
  Dispatch resumes automatically

SESSION MANAGEMENT interaction:
  Brain Step 10 (not built yet): aggregate fleet context math
  5 agents × 200K context near rollover = 1M token spike risk
  Force compact agents before rollover window
  Don't dispatch heavy tasks near window boundary
```

### 32.3 Scenario: PO Pauses Fleet

```
TRIGGER: PO sets work_mode = "work-paused" on OCMC

PROPAGATION:
  1. PO changes fleet_config on OCMC board (instant)
  2. Brain reads GET /api/v1/boards/{board_id} (≤30s)
  3. fleet_mode.py:read_fleet_control() → FleetControlState
  4. should_dispatch(state) returns False
  5. Brain emits fleet.system.mode_changed event
  6. IRC: "[brain] Fleet mode changed: work-paused"

WHAT STOPS:
  ✗ New task dispatch (should_dispatch gate)
  ✗ PM pulling from Plane (should_pull_from_plane gate)
  ✗ Driver wakes for assignment (no new work to assign)

WHAT CONTINUES:
  ✓ In-progress agents keep working (they're mid-task)
  ✓ Fleet-ops reviews and approvals (review is not "new work")
  ✓ Brain cycle runs (monitoring, health, doctor)
  ✓ Storm monitoring (safety never stops)
  ✓ Budget monitoring (cost tracking never stops)
  ✓ Gateway CRONs fire (agents heartbeat, see paused state)
  ✓ Event bus processing (events still propagate)

AGENT EXPERIENCE:
  Agent heartbeats → reads fleet-context.md
  Sees: "Fleet mode: work-paused"
  If has in-progress task: continues working
  If no task: heartbeat reports HEARTBEAT_OK, no action
  Brain may transition idle agents to SLEEPING faster

RESUME:
  PO sets work_mode back to "full-autonomous"
  Brain picks up (≤30s) → dispatch resumes
  Queued inbox tasks dispatched by priority
```

### 32.4 Scenario: Backend Switch

```
TRIGGER: PO changes backend_mode on OCMC (e.g., "claude" → "claude+localai")

PROPAGATION:
  1. PO changes fleet_config.backend_mode on OCMC
  2. Brain reads next cycle (≤30s)
  3. fleet_mode.py detects change, emits event
  4. IRC: "[brain] Backend mode: claude → claude+localai"

⚠️ NOT FULLY WIRED: orchestrator doesn't pass backend_mode to route_task() yet

TARGET BEHAVIOR (when wired):
  Next dispatch cycle:
  1. Brain reads backend_mode from FleetControlState
  2. Passes to route_task(backend_mode="claude+localai")
  3. backends_for_mode("claude+localai") → ["claude-code", "localai"]
  4. Router filters by task complexity + agent role:
     - Security/architecture → always claude (never free/trainee)
     - Complex tasks → claude (reasoning required)
     - Simple heartbeats → localai (structured response, free)
     - Simple reviews → localai or openrouter (pattern matching)
  5. Sort by cost → cheapest capable wins

WHAT DOESN'T CHANGE MID-TASK:
  In-progress tasks stay on their current backend
  Only NEW dispatches use new backend_mode
  Agent sessions are per-backend — switching means new session

LOCALAI AVAILABILITY CHECK:
  Before routing to localai:
  1. Health check: GET localhost:8090/v1/models
  2. Model loaded? (single-active backend, 8GB VRAM)
  3. Cold start: 10-80s if model not loaded
  4. If unavailable → fallback to next backend in list

CIRCUIT BREAKER:
  3 consecutive failures on a backend → breaker OPEN
  Cooldown: 300s (doubles on re-trip, max 1 hour)
  All traffic to that backend → fallback
  Both breakers OPEN → queue task, no dispatch
```

### 32.5 Scenario: Agent Stuck or Offline

```
TRIGGER: Agent stops producing output

DETECTION (two paths):

  Path 1: Doctor detection (doctor.py:205-227)
    detect_stuck(): no activity >60 minutes, no commits
    Response: FORCE_COMPACT (context overload suspected)

  Path 2: Health check (health.py:110-200)
    assess_fleet_health():
    - Task in_progress >8 hours → severity "medium"
    - Task in_progress >24 hours → severity "high"
    - Agent status "offline" + has task + >2 hours → severity "high"

CASCADE:

  FORCE_COMPACT (doctor response):
    gateway_client.force_compact(session_key)
    → sessions.compact RPC
    Agent context reduced without killing session
    Agent continues with fresh context summary

  PRUNE (if 3+ corrections or CRITICAL disease):
    gateway_client.prune_agent(session_key)
    → sessions.delete RPC
    Session killed, agent regrows fresh on next heartbeat
    Task: stays IN_PROGRESS, agent re-receives on heartbeat

  ESCALATE (if above thresholds):
    IRC #alerts: "[health] Agent {name} stuck on task {id} for {hours}h"
    ntfy: PO notification
    PO decides: reassign task? kill agent? manual intervention?

  Three-strike correction threshold:
    Agent gets corrected 3 times on same task → PRUNE
    Doctor: detect_correction_threshold()
    Teaching system: inject lesson before prune
    After prune: agent starts fresh, lesson embedded
```

### 32.6 Scenario: Gateway Duplication

```
TRIGGER: Multiple openclaw-gateway processes detected

DETECTION (orchestrator.py:105):
  check_gateway_duplication() — immediate (0s confirmation)
  This is an AUTOMATIC STORM indicator
  No confirmation window — instant escalation

CASCADE:
  1. Storm indicator "gateway_duplication" confirmed
  2. Severity jumps to at least WARNING (often STORM)
  3. Dispatch reduced or halted
  4. IRC #alerts: "[storm] Gateway duplication detected"
  5. ntfy: PO escalation
  6. Diagnostic snapshot captured

DANGER:
  Duplicate gateways = duplicate agent sessions
  Two instances of same agent working same task
  Conflicting commits, PR races, data corruption

RESOLUTION:
  1. PO kills duplicate gateway process
  2. Storm de-escalates over 10-30 minutes
  3. Verify: no duplicate sessions remain
  4. Verify: no conflicting work was produced

PREVENTION:
  scripts/start-fleet.sh: check for existing process before starting
  Gateway PID file: prevent accidental double-start
```

---

## 33. Complete Gap Registry — Everything Missing

**What this section is:** The FULL scope of what's not built, not captured,
not wired, and not documented. Not 12 small items — the real picture.
Every gap found during vision mapping, fleet-elevation review, ecosystem
inventory, and code verification. Organized by category.

### 33.1 BUGS IN EXISTING CODE

**B-01: Stage Gating Bug** — mcp/tools.py:130-131
`fleet_commit` gated to WORK stage only. Agents produce artifacts
(analysis docs, investigation reports, design artifacts) in stages 2-4.
They can't commit those. Fix: allow fleet_commit in stages 2-5.
`fleet_task_complete` correctly stays WORK-only.

**B-02: Gateway Injection Truncation** — ws_server.py:335-353
CLAUDE.md truncated to 2000 chars (spec: 4000). Context files truncated
to 1000 chars each (spec: 8000). Agents operate with half their context.

**B-03: Gateway Missing 5 of 8 Files** — executor.py:94-119
Gateway reads ONLY CLAUDE.md + context/. Does NOT read IDENTITY.md,
SOUL.md, TOOLS.md, AGENTS.md, HEARTBEAT.md. The entire onion injection
order is NOT IMPLEMENTED. Agents have no identity, no values, no tool
reference, no knowledge of colleagues, no heartbeat protocol.

**B-04: Backend Mode Not Wired** — orchestrator.py dispatch path
Router accepts backend_mode but orchestrator never passes it. All
dispatch uses default "claude". PO changing backend_mode has no effect.

**B-05: Budget Mode Empty** — budget_modes.py
BUDGET_MODES dict is empty. "turbo" in fleet.yaml has no BudgetMode entry.
No tempo offset applied anywhere. Setting has no effect.

### 33.2 MISSING MCP TOOLS (5 designed, not built)

```
fleet_contribute(task_id, contribution_type, content)
  12+ chain operations designed in fleet-elevation/24
  Blocks: ALL cross-agent synergy

fleet_request_input(task_id, from_role, question)
  Paired with fleet_contribute
  Blocks: agents can't ask colleagues for help

fleet_gate_request(task_id, gate_type, summary)
  8+ chain operations designed
  Blocks: PO governance at readiness gates

fleet_phase_advance — REMOVED (not needed)
  Phase is a free text field the PO sets directly.
  No automated validation — PO declares, system records.

fleet_transfer(task_id, to_agent, context_summary)
  Context packaging + agent reassignment
  Blocks: task handoffs between agents
```

### 33.3 EXISTING TOOLS NEED CHAIN ELEVATION

The 25 existing tools work but their chains are INCOMPLETE compared
to fleet-elevation/24 specs. Examples:

```
fleet_task_complete — EXISTS but missing:
  - Challenge engine invocation (designed, not wired)
  - Contributor notification loop
  - Parent task aggregate evaluation

fleet_task_progress — EXISTS but missing:
  - Readiness threshold events (50% checkpoint, 90% gate request)
  - Plane sync on progress
  - Memory trail recording

fleet_task_accept — EXISTS but missing:
  - Methodology check (plan references verbatim?)
  - Plane sync
  - Memory trail

fleet_artifact_create — EXISTS but missing:
  - 5 artifact types lack renderers:
    security_assessment, qa_test_definition, ux_spec,
    documentation_outline, compliance_report

fleet_approve — EXISTS but missing:
  - QA validation integration
  - Security review integration
  - Parent task evaluation on approval
  - Sprint progress update
```

### 33.4 MISSING BRAIN ARCHITECTURE

Brain is 9 steps. Design says 16 steps. Missing 7:

```
Missing Step 1b:  Event queue processing (chain registry)
Missing Step 3b:  Gate processing (PO gates at 90% readiness)
Missing Step 4b:  Contribution management (create subtasks per synergy matrix)
Missing Step 9:   Cross-task propagation (child→parent, contribution→target)
Missing Step 10:  Session management (two countdowns, aggregate math)
Missing Step 11:  Extended health + budget assessment
Missing Step 12:  Extended directive processing

Missing brain modules (designed, not built):
  fleet/core/contributions.py      — contribution registry + opportunity creation
  fleet/core/session_manager.py    — context + rate limit management
  fleet/core/heartbeat_gate.py     — brain evaluation for idle/sleeping agents
  (phase_system.py removed — phase is a free text field, no system needed)
  fleet/core/trail_recorder.py     — audit trail recording
  fleet/core/chain_registry.py     — event→handler registration (layer 2)
  fleet/core/logic_engine.py       — configurable dispatch gates (layer 3)
  fleet/core/autocomplete.py       — autocomplete chain builder
```

### 33.5 MISSING CONTRIBUTION SYSTEM (ENTIRE LAYER)

Not just 2 tools — an entire system:

```
Missing pieces:
  1. fleet_contribute MCP tool
  2. fleet_request_input MCP tool
  3. contributions.py brain module (opportunity creation, tracking)
  4. config/synergy-matrix.yaml (who contributes what to whom)
  5. Contribution pre-embed section in preembed.py
  6. build_contribution_chain() event chain (exists but unused)
  7. Contribution completeness checking (all required received?)
  8. PM notification when all contributions arrive
  9. Dispatch blocking until required contributions received
  10. Anti-pattern detection (siloed work, ghost contributions)

Contribution matrix is NOT simple — it's conditional:
  - By task type (epic needs ALL, subtask needs NONE)
  - By PO requirements for the deliverable
  - By condition (security_req only "if security-relevant")
  - Configurable via config file (PO can modify)
```

### 33.6 DELIVERY PHASE FIELD

Phases are a PO declaration — a free text field. What's missing:

```
Missing pieces:
  1. delivery_phase free text field on TaskCustomFields
  2. fleet_gate_request MCP tool (for readiness gates, not phase gates)
  3. Phase display in agent context (so agents know their phase)
  4. Phase in pre-embed (agents see what phase PO declared)
  5. Phase label sync to Plane

The PO declares the phase and provides requirements per-case.
No phase config, no phase enforcement, no predefined progressions.
```

### 33.7 MISSING TRAIL & AUDIT SYSTEM

Complete audit trail per task is designed but not built:

```
Missing pieces:
  1. trail_recorder.py module
  2. Trail event types (30+ types: creation, stage change, checkpoint,
     contribution, transfer, commit, completion, review, approval, etc.)
  3. Board memory trail tags convention (trail + task:{id} + type)
  4. Accountability generator reading trail entries
  5. Trail reconstruction from board memory
  6. Trail completeness checking (used by fleet-ops in review)
```

### 33.8 MISSING SKILLS LAYER

85 skills exist (78 AICP + 7 fleet custom). 32 assigned per role in
config/agent-tooling.yaml. BUT:

```
Missing pieces:
  1. Skills NOT deployed to agent workspaces yet
  2. scripts/install-plugins.sh exists in design, not built
  3. Agent CLAUDE.md files don't reference available skills
  4. Agent TOOLS.md doesn't list skills as capabilities
  5. No skill invocation training in agent context
  6. No per-stage skill recommendations:
     - INVESTIGATION: use Context7 for library docs
     - ANALYSIS: use architecture-review
     - WORK: use feature-implement, foundation-docker
  7. AICP skills may need adaptation for fleet agent context
  8. Skill evaluation (which skills actually help?) not done

Per-role assignments (from agent-tooling.yaml):
  architect:       architecture-propose, architecture-review, scaffold
  engineer:        feature-implement, refactor-extract
  qa:              quality-coverage, quality-audit, foundation-testing
  devops:          foundation-docker, foundation-ci, ops-deploy
  devsecops:       infra-security, quality-audit
  fleet-ops:       pm-assess, quality-audit
  PM:              pm-plan, pm-status-report, pm-retrospective
  writer:          feature-document, pm-changelog, pm-handoff
  UX:              quality-accessibility
  accountability:  quality-audit
```

### 33.9 MISSING PLUGINS LAYER

Claude-Mem and Context7 are designed for deployment but NOT installed:

```
Missing pieces:
  1. Claude-Mem not installed on any agent (cross-session memory)
  2. Context7 not installed on architect/engineer (library docs)
  3. scripts/install-plugins.sh not built
  4. Per-agent plugin configuration not deployed
  5. Plugin evaluation (what else is useful?) not done
  6. codex-plugin-cc (adversarial security) mentioned but not assigned

Tier 1 deployment plan:
  E-01: Prompt caching (90% savings) — config change only
  E-02: Claude-Mem (all agents) — cross-session memory
  E-03: Context7 (architect + engineer) — library docs
  E-04: Filesystem MCP (per agent-tooling.yaml) — structured file ops
```

### 33.10 MISSING COMMANDS & AGENT TRAINING

Claude Code built-in commands exist but agents aren't trained to use them:

```
Missing agent training on:
  /plan     — when to use plan mode (before complex tasks)
  /compact  — strategic compaction with preservation instructions
  /context  — inspect context breakdown before heavy tasks
  /clear    — clear session between logical tasks
  /model    — model selection (opus[1m] vs sonnet)
  /loop     — scheduled tasks within Claude Code (Feb 2026 feature)
  /debug    — interactive debugging workflow

No agent CLAUDE.md or TOOLS.md mentions these commands.
No stage-specific command recommendations exist.
No compaction strategy documented per agent role.
```

### 33.11 MISSING CONTEXT SIZE STRATEGY

Context size management has 10 requirements (CW-01 to CW-10).
Status:

```
Done:
  CW-01: Know context window size (statusline) ✓
  CW-02: Cost dynamics awareness (documented) ✓
  CW-05: Prevent context bloat (.claudeignore) ✓

Protocol defined but not enforced:
  CW-03: Strategic compaction (/compact + memory)
  CW-04: Efficient context regathering (memory system)

Design phase only:
  CW-07: Rate limit rollover awareness
  CW-08: Pre-rollover preparation (force compact at 85%)
  CW-09: Context-size-proportional awareness (1M managed aggressively)
  CW-10: Multi-agent rollover coordination (10 agents crossing rollover)

Missing entirely:
  - Prompt caching configuration (cacheRetention per agent)
  - Known Anthropic bugs (cache breaks after 5min, background Opus quota)
  - Per-agent context strategy (persistent agents vs worker agents)
  - Brain session_manager.py (aggregate fleet context math)
  - Smart artifacts dumping (heavy context → synthesized artifact)
```

### 33.12 MISSING PROMPT CACHING

90% savings on cached input tokens — NOT DEPLOYED:

```
Missing pieces:
  1. cacheRetention config per agent (short vs long)
  2. Per-agent strategy:
     - Short-term agents (workers): cacheRetention = "short"
     - Persistent agents (PM, fleet-ops): cacheRetention = "long"
  3. Known Anthropic bugs not documented/mitigated:
     - Cache breaks after 5-minute pause (10-20x cost inflation)
     - Background agents use Opus quota silently
     - Silent retries on rate-limit errors drain budget
  4. Deployment: config change in agent MCP settings
```

### 33.13 MISSING AGENT TEAMS EVALUATION

```
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS (Feb 2026)
  - Lead agent + 2-5 teammates in independent contexts
  - Mailbox-based direct messaging between teammates
  - Git worktree per teammate (file isolation)
  - Shared task list with dependency tracking

Fleet assessment needed:
  - Does this complement or conflict with orchestrator?
  - Can architect + engineer collaborate via Agent Teams?
  - Cost implications of multi-agent sessions
  - Integration with fleet methodology and stage gating

Status: NOT EVALUATED (L9 backlog item)
```

### 33.14 MISSING NOTIFICATION ROUTING MATRIX

The complete "who gets notified when" is designed but not fully wired:

```
Missing IRC channels:
  #gates         — gate requests and decisions
  #contributions — contribution posts and completions

Missing notification routes:
  - Contribution posted → target agent mention + IRC #contributions
  - Gate requested → IRC #gates + ntfy high priority
  - Phase advanced → IRC #fleet + Plane state update
  - QA validation complete → IRC #reviews
  - Security review complete → IRC #reviews

Notification routing in notification_router.py exists but
does NOT cover all event types from fleet-elevation design.
```

### 33.15 MISSING AUTOCOMPLETE CHAIN ENGINEERING

The autocomplete chain is the CORE design principle — context data
arranged so AI's natural continuation IS correct behavior:

```
Missing pieces:
  1. autocomplete.py module (designed in brain spec, not built)
  2. Chain assembly logic per agent role
  3. Context ordering enforcement:
     Identity → Values → Rules → Tools → Team → State → Task → Action
  4. Verbatim anchoring in every context level
  5. Stage-specific instructions in autocomplete chain
  6. Contribution embedding in chain
  7. Phase (PO-declared) shown in context
  8. Anti-corruption rules embedded in chain structure

Without this: agents get data but not in the order that drives
correct behavior. The "Lost in the Middle" effect wastes critical
instructions buried in middle context.
```

### 33.16 MISSING ANTI-CORRUPTION STRUCTURAL PREVENTION

Design has THREE lines of defense. Code has only line 2 (partial):

```
LINE 1: STRUCTURAL PREVENTION (prevent disease from appearing)
  Missing:
  - Autocomplete chain engineering (data ordering)
  - Contribution requirements as dispatch block
  - Phase-aware standards injection
  - Verbatim anchoring in every context level
  Status: NOT BUILT

LINE 2: DETECTION (catch disease when it appears)
  Partial:
  - 4 of 11 detections implemented
  - 7 missing: abstraction, code_without_reading, scope_creep,
    cascading_fix, context_contamination, not_listening, compression
  - Contribution avoidance detection: missing
  - Synergy bypass detection: missing
  Status: 36% IMPLEMENTED

LINE 3: CORRECTION (fix disease after detection)
  Implemented: teach, force_compact, prune
  Missing:
  - Readiness regression on disease detection
  - Stage reversion
  - Adapted lessons for 7 missing diseases
  Status: CORRECTION MECHANISM EXISTS, but 7 diseases can't trigger it
```

### 33.17 MISSING COWORK & TRANSFER PROTOCOLS

Multiple agents on same task, and task handoffs:

```
Cowork (not built):
  - Owner vs coworker distinction
  - Coworker permissions (can comment/artifact, can't complete)
  - Brain dispatches to owner, notifies coworkers
  - Trail records who did what

Transfer (not built):
  - Context packaging (artifacts, comments, contributions, trail)
  - Agent reassignment via fleet_transfer tool
  - Receiving agent gets transfer context in task-context.md
  - Trail records transfer with source/target/stage/readiness
```

### 33.18 MISSING PER-AGENT MCP SERVERS

agent-tooling.yaml defines per-role MCP servers but NOT deployed:

```
  architect:       fleet, filesystem, github
  engineer:        fleet, filesystem, github, playwright
  qa:              fleet, filesystem, playwright
  devops:          fleet, filesystem, github, docker
  devsecops:       fleet, filesystem, docker
  fleet-ops:       fleet, github
  PM:              fleet, github
  writer:          fleet, filesystem, github
  UX:              fleet, filesystem, playwright
  accountability:  fleet, filesystem

scripts/setup-agent-tools.sh needs to generate per-agent mcp.json
with role-specific servers. Not built yet (B3 blocker).
```

### 33.19 MISSING IaC SCRIPTS (B3)

6 scripts designed in iac-mcp-standard.md, none built:

```
  scripts/provision-agents.sh      — create agent dirs from template
  scripts/setup-agent-tools.sh     — generate per-agent mcp.json
  scripts/install-plugins.sh       — install Claude-Mem, Context7 per role
  scripts/generate-tools-md.sh     — generate TOOLS.md from code + chains
  scripts/generate-agents-md.sh    — generate AGENTS.md from synergy matrix
  scripts/validate-agents.sh       — validate ALL files against standards

Plus Makefile targets: provision, setup-tools, validate-agents, setup
```

### 33.20 MISSING AGENT FILES (B1, B2, B4)

```
  agent.yaml:   0/10 written per standard (B4)
  CLAUDE.md:    0/10 written per standard (B1)
  HEARTBEAT.md: 0/5 unique types per standard (B2)
  IDENTITY.md:  0/10 per standard
  SOUL.md:      0/10 per standard
  TOOLS.md:     0/10 (generated by IaC script)
  AGENTS.md:    0/10 (generated by IaC script)

  Total: 0/70+ agent files written to spec
```

### 33.21 MISSING BRAIN EVALUATION FOR IDLE AGENTS

Designed in fleet-elevation/23, not built:

```
  When agent has brain_evaluates=True (after 1 HEARTBEAT_OK):
    Brain evaluates in Python (FREE, no Claude call):
      - Direct mention? → WAKE
      - Task assigned? → WAKE
      - Contribution task? → WAKE
      - PO directive? → WAKE
      - Role-specific trigger? → WAKE
      - Nothing? → STAY SLEEPING ($0)

  Impact: ~70% cost reduction on idle fleet
  Requires: heartbeat_gate.py module
  Data structures exist: consecutive_heartbeat_ok, last_heartbeat_data_hash
  Interception logic: NOT in orchestrator
```

### 33.22 MISSING READINESS REGRESSION

When fleet-ops rejects or doctor detects disease, task should regress:

```
  Designed:
    - Readiness drops (e.g., 99 → 80 or lower)
    - Stage may revert (work → reasoning)
    - Agent gets feedback in next context refresh
    - Trail records regression with reason

  Not built:
    - Regression logic in MCP tools
    - Regression event chain
    - Context refresh with regression feedback
    - Doctor-triggered regression (vs fleet-ops rejection)
```

### 33.23 SCOPE SUMMARY

```
Category                          Items Missing    Effort Est.
──────────────────────────────────────────────────────────────
Bugs in existing code             5 bugs           4-8h
Missing MCP tools                 5 tools          16-32h
Tool chain elevation              5 tools upgraded 8-16h
Missing brain steps               7 steps          20-40h
Missing brain modules             8 modules        40-80h
Contribution system               10 pieces        16-32h
Phase system                      9 pieces         8-16h
Trail & audit system              6 pieces         8-16h
Skills deployment                 8 pieces         4-8h
Plugins deployment                6 pieces         2-4h
Command training                  7 commands        2-4h
Context strategy                  5+ pieces        8-16h
Prompt caching                    4 pieces         1-2h
Agent Teams evaluation            1 evaluation     4-8h
Notification routing              5 routes         2-4h
Autocomplete chain                8 pieces         8-16h
Anti-corruption structural        Line 1 + Line 2  16-32h
Cowork + transfer protocols       2 protocols      4-8h
Per-agent MCP servers             10 agents        2-4h
IaC scripts                       6 scripts        4-8h
Agent files                       70+ files        30-60h
Brain idle evaluation             1 module         4-8h
Readiness regression              4 pieces         2-4h
──────────────────────────────────────────────────────────────
TOTAL                             130+ pieces      ~200-400h

### 33.24 Readiness vs Progress Conflation

**Source:** task_readiness field in models.py, orchestrator.py, challenge.md

**Problem:** Single `task_readiness` field conflates:
1. "Ready to START working" (pre-dispatch gate: PO authorized, >= 99)
2. "How far through WORKING" (post-dispatch progress: 70→80→90→100)

Readiness=99 means both "PO approved plan" AND "currently working."
Readiness DROPS from 99 to 70 when work is DONE (backwards).

**Fix needed:** Two fields: `task_readiness` (pre-dispatch authorization)
and `task_progress` (post-dispatch progression). See §45.

### 33.25 Agent Signatures Incomplete

**Source:** labor_stamp.py, tools.py, session_telemetry.py

**Problem:** LaborStamp exists (25 fields) but:
- Session telemetry not wired (tokens=0 hardcoded)
- context_window_size not tracked
- budget_mode not tracked
- lines_added/removed not populated
- fleet.labor.recorded event not emitted
- Only 8 of 15+ fields written to TaskCustomFields
- No mini-signatures on individual tool calls or trail events

**Fix needed:** Full signature system at all levels. See §44.

### 33.26 Knowledge Graph RAG Not Integrated

**Source:** PO requirement (2026-04-02)

LightRAG (MIT, 31K stars) provides graph + vector RAG — entities,
relationships, knowledge graph visualization, 6 query modes.
Currently: OCMC has basic KB, LocalAI has flat vector /stores/.
Neither captures structural relationships between concepts.

**Fix needed:** Deploy LightRAG, integrate with OCMC, agent MCP query.
See §46 for full analysis and phased integration plan.

### 33.27 No Economic Model / Cost Projections

No ROI analysis, no cost-per-task breakdown, no LocalAI payback
timeline, no budget variance tracking. See §47.

### 33.28 No PO Operational Runbook

PO has no documented daily workflow — what to check, when, what
commands to use for common actions. See §48.

### 33.29 No Canonical Deployment Specification

Docker services, ports, startup sequence, health checks all exist
but not documented as a single reproducible specification. See §49.

### 33.30 No Crisis Response Playbook

No documented procedures for: budget drain, MC down, gateway down,
bad agent output, storm escalation. See §50.

### 33.31 Cross-Project Integration Not Built

AICP RAG not accessible from fleet. Router unification is schema only.
NNRT has no fleet integration. Cost attribution across projects
not tracked. See §51.

### 33.32 Sprint/PM Ceremonies Not Specified

Sprint planning, velocity tracking, backlog management, retrospectives
exist conceptually but no documented protocol. See §52.

### 33.33 Agent Permissions Not Formalized

bypassPermissions used for all agents. No formal permission matrix
for tools, data access, credentials. Informal isolation through
workspaces but not documented. See §53.

This is 33 categories of missing work spanning every layer of the
fleet system. Total estimated effort: ~300-500 hours.

---

## 55. OCMC Board Structure — Custom Fields, Tags, Memory

**What this section is:** The complete data model of the OCMC board.
31 custom fields, 30+ tag types, 5 per-agent memory files, and the
board memory taxonomy.

### 55.1 Custom Field Catalog (31 fields)

```
PROJECT & EXECUTION:
  project              text       Target project name
  branch               text       Git branch name
  pr_url               url        GitHub PR URL
  worktree             text       Local worktree path
  agent_name           text       Assigned agent
  model                text       AI model used (hidden)

TASK HIERARCHY & PLANNING:
  task_type             text       epic/story/task/subtask/blocker/request/concern
  parent_task           text       Parent task ID
  plan_id               text       Sprint plan reference
  story_points          integer    Effort estimate (1/2/3/5/8/13)
  sprint                text       Sprint identifier
  complexity            text       low/medium/high

METHODOLOGY & READINESS:
  task_readiness        integer    Pre-dispatch authorization (0-100, gate at 99)
  requirement_verbatim  text_long  PO's exact words (SACROSANCT, never modified)
  task_stage            text       conversation/analysis/investigation/reasoning/work

DELIVERY & PRODUCT:
  delivery_phase        text       poc/mvp/staging/production
  phase_progression     text       standard/release/custom

COLLABORATION:
  coworkers             json       List of co-working agent names
  contribution_type     text       qa_test_def/design_input/security_req/ux_spec
  contribution_target   text       Task ID this contribution is for

REVIEW & QUALITY GATES:
  review_gates          json       Per-reviewer gate status [{agent, type, status, reason}]
  security_hold         text       Behavioral security block

PLANE INTEGRATION (sync mapping):
  plane_issue_id        text       Plane issue UUID
  plane_project_id      text       Plane project UUID
  plane_workspace       text       Plane workspace slug

LABOR ATTRIBUTION (set on completion):
  labor_backend         text       claude-code/localai/openrouter/direct
  labor_model           text       opus-4-6/sonnet-4-6/hermes-3b/etc.
  labor_effort          text       low/medium/high/max
  labor_confidence      text       expert/standard/trainee/community/hybrid
  labor_skills          json       Skills used during work
  labor_cost_usd        float      Estimated cost
  labor_duration_s      integer    Duration in seconds
  labor_iteration       integer    Attempt number (increments on rework)

CHALLENGE LOOP (iterative validation):
  challenge_round       integer    Current round (0 = not started)
  challenge_max_rounds  integer    Max before escalation (default 3)
  challenge_status      text       pending/in_progress/passed/failed/waived/deferred
  challenge_findings    json       Findings per round [{round, type, finding, status}]
  challenge_challenger  text       Who/what is challenging
  challenge_type        text       automated/agent/cross-model/scenario
```

### 55.2 Tag Taxonomy

```
TASK TYPE TAGS:
  type:feature, type:fix, type:docs, type:test, type:chore, type:review
  type:epic, type:story, type:subtask, type:blocker, type:request, type:concern

STATUS TAGS:
  needs-review, auto-merge, blocked

PROJECT TAGS (dynamic from config/projects.yaml):
  project:{name}

BOARD MEMORY TAGS:
  Content type:    completed, alert, decision, trail, transfer, phase,
                   review, rejection, gate, contribution_received,
                   sprint, milestone
  Entity refs:     task:{id}, agent:{name}, mention:{name}, plan:{id}
  Severity:        critical, high, medium, low
  Categories:      security, quality, architecture, workflow, tooling
  Governance:      po-required, directive, from:human, to:{agent}
```

### 55.3 Per-Agent Memory Files

```
Each agent workspace: agents/{name}/.claude/memory/

  MEMORY.md               Index (auto-managed, links to below)
  codebase_knowledge.md   Patterns, architecture, key files discovered
  project_decisions.md    Decisions made with date, context, rationale
  task_history.md         Completed work and lessons learned
  team_context.md         Shared knowledge from board memory

Updated by: claude-mem plugin (cross-session)
Read by: agent at session start
Purpose: context recovery after session prune/compact
```

### 55.4 Board Memory as Shared Knowledge Layer

```
Agents post decisions → board memory (tagged)
Brain writes context → board memory (tagged trail + task:{id})
PO writes directives → board memory (tagged directive + to:fleet)

fleet_read_context surfaces relevant entries at session start:
  - mention:{agent_name} → MESSAGES section
  - directive → PO DIRECTIVES section
  - trail + task:{id} → task audit trail

Board memory IS the fleet's shared knowledge base until LightRAG (§46).
```

---

## 56. Testing Strategy — How to Verify the Fleet Works

**What this section is:** The test approach for 94 modules, 1800+ tests,
and agent behavior validation.

### 56.1 Test Inventory

```
101 test files in fleet/tests/
1800+ unit tests, 23 integration tests
All run via: make test (pytest)

Distribution by system:
  core/          ~60 test files (methodology, lifecycle, doctor, router, etc.)
  mcp/           ~8 test files (MCP tool tests)
  infra/         ~10 test files (clients, config, cache)
  cli/           ~5 test files (orchestrator, dispatch)
  templates/     ~5 test files (comment, PR formatting)
  integration/   ~13 test files (cross-system flows)
```

### 56.2 Test Pyramid

```
UNIT TESTS (1800+, fast, isolated):
  Every module has matching test file
  Mock external dependencies (MC API, gateway, Plane)
  Test: function behavior, edge cases, data structures
  Run: every commit, every PR

INTEGRATION TESTS (23, medium, cross-module):
  Test: orchestrator cycle with mocked MC
  Test: MCP tool chains (fleet_task_complete → event chain → surfaces)
  Test: dispatch → agent context → MCP tools
  Run: before merging PRs

AGENT BEHAVIOR TESTS (NOT BUILT — CRITICAL GAP):
  Test: PM wakes and assigns task correctly
  Test: engineer follows methodology stages
  Test: fleet-ops reviews with 7-step protocol
  Test: contributions flow between agents
  Test: readiness regression on rejection
  Run: before deploying agent changes

LIVE VALIDATION TESTS (NOT BUILT):
  Test: full task lifecycle (dispatch → work → review → done)
  Test: storm response (inject indicators → observe cascade)
  Test: rate limit handling (approach threshold → observe behavior)
  Run: after deployment, before 24h observation
```

### 56.3 Critical Path Tests

```
MUST PASS before any deployment:

  1. Orchestrator cycle completes without error
  2. Dispatch gate logic (10 gates, all permutations)
  3. MCP stage gating (correct tool blocked in wrong stage)
  4. Event chain fires to all 6 surfaces
  5. Storm monitor escalation cascade
  6. Budget monitor threshold detection
  7. Doctor disease detection (4 implemented)
  8. Labor stamp assembly (correct fields populated)
  9. Plane sync bidirectional (readiness, status, comments)
  10. Gateway RPC (inject, prune, compact, create)
```

### 56.4 Agent Behavior Test Design (NOT BUILT)

```
How to test agent behavior WITHOUT burning Claude tokens:

OPTION 1: Mock Agent Sessions
  - Brain writes context files
  - Test verifies: correct context assembled
  - Mock agent response: "fleet_task_accept called with plan"
  - Test verifies: MCP tool processes correctly

OPTION 2: Replay Tests
  - Record real agent sessions (tool calls + responses)
  - Replay against updated MCP code
  - Verify: same inputs produce same outputs

OPTION 3: LocalAI Agent Tests
  - Use LocalAI for test agents (free)
  - Run full cycle with hermes-3b
  - Verify: methodology followed, tools called correctly
  - Quality doesn't matter — process compliance does

OPTION 4: Canary Agent
  - One agent runs on latest code
  - Others run on stable code
  - Compare: error rates, disease detection, trail completeness
```

---

## 57. Observability & Monitoring — How to See the Fleet

**What this section is:** Telemetry pipeline, health scoring, metrics,
and how the PO sees what's happening.

### 57.1 Telemetry Pipeline

```
Claude Code JSON session data
  ↓
session_telemetry.py:ingest(session_json)
  → SessionSnapshot (94 lines)
  │
  ├─ to_labor_fields(snap) → LaborStamp fields
  │   duration, tokens, cost, lines_added, lines_removed, cache
  │
  ├─ to_claude_health(snap) → ClaudeHealth
  │   quota_used_pct (5h + 7d), context_used_pct, latency_ms
  │
  ├─ to_storm_indicators(snap) → StormMonitor
  │   context_pressure (≥70%), quota_pressure (≥80%)
  │
  └─ to_cost_delta(snap) → BudgetMonitor
      cost increase since last reading

STATUS: Adapter built (230 lines, 30 tests). NOT WIRED to orchestrator.
```

### 57.2 Health Scoring

```
Fleet health dimensions (health.py):

  AGENT HEALTH:
    Online/offline status
    Stuck detection (>60 min no activity)
    Correction count (3+ = disease)
    Session state (fresh/compact/old)

  TASK HEALTH:
    Stale in-progress (>8h without update)
    Blocked tasks (dependency not met)
    Orphaned reviews (no approval exists)

  BUDGET HEALTH:
    Rate limit usage (5h + 7d windows)
    Fast climb detection (>5% in 10 min)
    Daily cost trend

  STORM HEALTH:
    Current severity (CLEAR→CRITICAL)
    Active indicators count
    Circuit breaker states

Combined: assess_fleet_health(tasks, agents) → HealthReport
  Severity: healthy / degraded / critical
  Issues: list with specific details
  Actions: suggested remediation
```

### 57.3 What PO Sees

```
REAL-TIME:
  Statusline:     model + context% + rate limits + git branch
  IRC #fleet:     dispatch, completion, mode changes
  IRC #alerts:    storms, security, escalations
  IRC #reviews:   review requests, approvals, rejections
  ntfy:           gate requests, completions, escalations

ON DEMAND:
  make status:    full fleet overview (agents, tasks, approvals, activity)
  make digest:    daily summary (what happened, metrics)
  make quality:   quality check (compliance, diseases, trail gaps)
  OCMC frontend:  task board, agent list, board memory

MISSING:
  ✗ Cost dashboard (token spend per agent, per day, per sprint)
  ✗ Velocity dashboard (SP completed, trend, forecast)
  ✗ Health dashboard (combined score, history, trends)
  ✗ LaborStamp analytics view (which models, which tiers, cost/task)
```

---

## 58. CLI & Makefile — Fleet Operations Guide

**What this section is:** Every command available to operate the fleet.

### 58.1 Infrastructure Commands

```
make mc-up              Start Mission Control (docker compose up -d)
make mc-down            Stop Mission Control
make mc-logs            Tail MC backend logs
make gateway            Start OpenClaw gateway (host process)
make gateway-stop       Stop gateway
make gateway-restart    Restart gateway
make irc-up             Start miniircd
make irc-down           Stop miniircd
make irc-connect        Show IRC connection details
make lounge-up          Start The Lounge web UI
make lounge-down        Stop The Lounge
make clean              Docker cleanup (volumes, networks)
```

### 58.2 Agent Management Commands

```
make agents             List registered agents
make agents-register    Register agents in gateway
make agents-push        Push framework files to all agents
make agents-config      Configure per-agent settings
make provision          Full agent provisioning (template → workspace)
```

### 58.3 Task Operations Commands

```
make create-task TITLE="..." [AGENT=...] [PROJECT=...]
                        Create task on MC board
make dispatch AGENT=... TASK=...
                        Dispatch task to agent
make trace TASK=...     Show full task trace (MC + git + PR)
make monitor TASK=...   Monitor task progress (real-time)
make chat MSG="..."     Post to fleet chat
make integrate TASK=... PROJECT=...
                        Integrate agent work into project
```

### 58.4 Daemon & Monitoring Commands

```
make daemons-start      Start all daemons (sync + monitor)
make daemons-stop       Stop all daemons
make sync               Run sync once (MC ↔ GitHub)
make sync-start         Start sync daemon (60s loop)
make sync-stop          Stop sync daemon
make monitor-start      Start monitor daemon (300s loop)
make monitor-stop       Stop monitor daemon
make watch              WebSocket session monitor (live events)
make logs               Fleet log monitoring
```

### 58.5 Reports & Quality Commands

```
make status             Full fleet status overview
make digest             Generate daily digest (IRC + board memory)
make digest-preview     Dry-run digest (no posting)
make quality            Quality check against standards
make changelog          Generate CHANGELOG.md from conventional commits
```

### 58.6 Skills & Ecosystem Commands

```
make skills-list        List available skills
make skills-install     Install skills from config
make skills-sync        Sync skill packs from external sources
make codex-setup        Install Codex plugin
make install-statusline Install Claude Code statusline
```

### 58.7 Auth & Config Commands

```
make refresh-auth       Refresh Anthropic auth token
make auth-status        Check auth status
make board-setup        Initialize MC board (custom fields, tags)
make board ACTION=...   Board manipulation commands
make cache ACTION=...   Cache management (clear, stats)
```

### 58.8 Development Commands

```
make test               Run pytest (1800+ tests)
make setup              Full fleet setup from scratch
make fleet-setup        Gateway setup Python module
```

---

## 59. Challenge System — Iterative Validation & Quality Gates

**What this section is:** The complete adversarial challenge architecture.
6 modules, 4 challenge types, graduated validation, analytics-driven learning.

### 59.1 The 4 Challenge Types

```
TYPE 1: AUTOMATED (free, fast)
  challenge_automated.py generates deterministic pattern checks:
  - Regression: run full test suite
  - Conditional edge cases: boundary values (0, 1, -1, max, None)
  - Loop handling: empty, single, large (100+) inputs
  - Async/concurrency: race conditions, gather with failures
  - Timeout/retry: network unavailable, extreme latency
  - Architecture: import cycles, cross-module consistency
  - Error handling: bare except, exception swallowing
  
  No LLM calls. Pattern detection from diff analysis.

TYPE 2: AGENT (medium cost)
  A domain expert agent challenges the work:
  - Security/blocker → devsecops-expert
  - Epic/architecture → architect
  - Test tasks → qa-engineer
  - Default → qa-engineer (or engineer if author is qa)
  
  Agent receives ChallengeContext → produces findings.

TYPE 3: CROSS-MODEL (cheap)
  challenge_cross_model.py uses a DIFFERENT LLM:
  - Simple tasks: LocalAI hermes-3b (free)
  - Complex tasks: OpenRouter (different vendor)
  - Security: OpenRouter (independent verification)
  
  LLM receives adversarial system prompt → finds flaws.

TYPE 4: SCENARIO (bug fixes, SP ≥ 3)
  challenge_scenario.py generates targeted tests:
  - Reproduction: original bug still occurs without fix?
  - Removal: remove fix, bug returns? (PO REQUIREMENT)
  - Regression: no previously passing tests fail?
  - Boundary: values at/below/above thresholds
  - Concurrency: multi-thread/coroutine race conditions
  - Interaction: cross-module consistency
```

### 59.2 When Challenges Trigger

```
is_challenge_required(task_type, story_points, confidence_tier):

  ALWAYS challenge:
    - trainee/community tier (LocalAI/OpenRouter produced work)
    - blocker/concern tasks
    - bug fixes with SP ≥ 3
    - epics
    - complex stories (SP ≥ 5)

  NEVER challenge:
    - heartbeats
    - low-risk (SP ≤ 2)
    - docs/chore type

  Type selection:
    Bug fix SP ≥ 3     → SCENARIO
    Trainee/community  → CROSS_MODEL
    Complex (SP ≥ 5)   → AGENT
    Default            → AUTOMATED

  Max rounds by tier:
    expert:    1 round
    standard:  2 rounds
    trainee:   3 rounds
    community: 3 rounds
```

### 59.3 Challenge Flow

```
fleet_task_complete(summary)
  ↓
evaluate_challenge(task, confidence_tier, author_agent)
  ↓ ChallengeDecision: required?, type, challenger, max_rounds
  ↓
start_challenge(task, decision)
  ├─ AUTOMATED → generate challenges → execute → boolean results
  ├─ AGENT → build context → dispatch to challenger agent
  ├─ CROSS_MODEL → send to different LLM → parse findings
  └─ SCENARIO → generate scenarios → execute steps
  ↓
process_findings() → ChallengeFinding objects
  ↓
evaluate_round_outcome(record) → RoundOutcome
  ├─ PASSED → advance to review (readiness 80)
  ├─ RECHALLENGE → author reworks → next round
  └─ ESCALATE → max rounds or critical → escalate to human
  ↓
record_challenge_event() → analytics
  ↓
teaching_signals() → identify repeated failures → feed to teaching system
```

### 59.4 Challenge Readiness Integration

```
70% = WORK_COMPLETE     Agent finished implementation
80% = CHALLENGE_PASSED  Adversarial validation survived
90% = REVIEW_PASSED     Fleet-ops approved
95% = PO_APPROVED       PO signed off
100% = DONE

check_challenge_readiness() enforces:
  - Can't advance to review unless challenge passed/waived/deferred
  - Open findings block advancement
  - Max rounds reached with findings → escalate to human

Note: With §45 readiness/progress split, these become
task_progress values, not task_readiness values.
```

### 59.5 Review Gates (Confidence-Aware)

```
review_gates.py determines review depth by confidence tier:

  expert (opus):      1 gate — fleet-ops only
  standard (sonnet):  1 gate — fleet-ops only
  trainee (localai):  3 gates — challenge + architect + fleet-ops
  community (openrouter): 3 gates — challenge + architect + fleet-ops
  hybrid (mixed):     2 gates — architect + fleet-ops

Plus task-type gates:
  epic/story → architect review
  blocker → devsecops review
  code changes → qa-engineer review

Fleet-ops is ALWAYS the final gate.
```

### 59.6 Challenge Analytics & Learning

```
challenge_analytics.py aggregates outcomes:

  Per agent: pass_rate, avg_rounds, total_findings, top_categories
  Per tier: pass_rate, avg_rounds
  Common findings: top categories, severity distribution

  teaching_signals(min_failures=3):
    Agent with 3+ failures in same category → TeachingSignal
    Suggestion: category-specific improvement advice
    Fed to: teaching.py → inject adapted lesson

  Example:
    alpha-engineer failed 4 edge_case challenges
    → TeachingSignal: "Review boundary value analysis"
    → Lesson injected into next session
```

### 59.7 Deferred Challenges

```
challenge_deferred.py manages budget-constrained queueing:

  When challenge deferred (budget too tight):
    Task enters DeferredChallengeQueue
    Priority: story_points + tier_bonus + type_bonus
    Alert thresholds: WARNING at 10 queued, CRITICAL at 25
    Age alert: WARNING at 24h, CRITICAL at 72h

  Drain: compute_drain_batch_size(queue_size, max_per_cycle=3)
  When budget allows: dequeue highest priority first
```

---

## 60. Smart Chains vs Event Chains — Two Chain Architectures

**What this section is:** The distinction between pre-computed context
bundles (smart chains) and multi-surface event propagation (event chains).

### 60.1 Event Chains (Reactive, Multi-Surface)

```
event_chain.py + chain_runner.py

PURPOSE: When something HAPPENS → propagate to ALL surfaces.

Example: fleet_task_complete fires build_task_complete_chain():
  → MC: update task status
  → MC: create approval
  → MC: post memory (trail)
  → GitHub: push branch, create PR
  → IRC: notify #fleet + #reviews
  → ntfy: notify PO
  → Plane: update issue state + comment
  → Event bus: emit CloudEvent

CHARACTERISTICS:
  - Triggered BY agent action (MCP tool call)
  - Fires AFTER the action completes
  - Multi-surface: hits 6 different targets
  - Failure tolerant: required surfaces must succeed, optional can fail
  - Returns: ChainResult (total, executed, failed, errors)

8 chain builders exist:
  build_task_complete_chain()
  build_task_dispatch_chain()
  build_approval_chain()
  build_contribution_chain()
  build_alert_chain()
  build_gate_request_chain()
  build_phase_advance_chain()
  build_rejection_chain()
```

### 60.2 Smart Chains (Pre-Computed, Context Bundles)

```
smart_chains.py

PURPOSE: Before dispatch → pre-compute everything agent needs.

DispatchContext bundles:
  - task: id, title, description, priority, type, project
  - environment: worktree, branch, parent, dependencies, story_points
  - model + effort selection
  - recent_decisions: from board memory, filtered by project
  - related_work: other agents on same project
  - sprint_progress: done/total %

build_dispatch_context(task, board_memory, all_tasks, model, effort):
  - No API calls — uses pre-computed data from orchestrator
  - Agent gets everything in dispatch message
  - Saves fleet_read_context call (first MCP call optimization)

CHARACTERISTICS:
  - Pre-computed BY brain (orchestrator cycle)
  - Assembled BEFORE dispatch
  - Single target: the agent being dispatched to
  - Context reduction: fewer API calls = fewer tokens = lower cost
```

### 60.3 When to Use Which

```
Event Chain: something HAPPENED → tell everyone
  fleet_task_complete → 12 operations across 6 surfaces
  fleet_approve → approval chain across IRC, Plane, trail
  fleet_alert → alert routing to #alerts, ntfy, trail

Smart Chain: something WILL HAPPEN → prepare context
  Task dispatch → pre-compute context bundle
  Heartbeat → pre-compute fleet-context.md + task-context.md
  Contribution → pre-compute target agent context

They COMPLEMENT each other:
  Smart chain assembles context → dispatch → agent works →
  agent calls MCP tool → event chain fires → surfaces updated →
  smart chain refreshes context for next cycle
```

---

## 61. LocalAI Function Calling & Structured Output

**What this section is:** How LocalAI produces structured responses
for fleet operations without Claude.

### 61.1 LocalAI Structured Output

```
LocalAI supports grammar-based structured output:
  GBNF grammar (llama.cpp) forces model output to match schema
  OpenAI-compatible function calling API
  JSON mode for structured responses

For fleet operations:
  Heartbeat response → structured JSON:
    {status: "HEARTBEAT_OK", actions: [], mentions_checked: true}
  
  Task acceptance → structured plan:
    {plan: [{step: 1, action: "...", files: [...]}], estimated_sp: 3}
  
  Simple review → structured decision:
    {approved: true, criteria_met: [...], issues: []}

Quality concern:
  3B models: can produce JSON but reasoning is weak
  7B models: better reasoning but still limited
  9B Qwen3.5: strong reasoning, good structured output
  32B+: recommended for complex structured tasks
```

### 61.2 MCP Tools from LocalAI

```
Can LocalAI agents call MCP tools? YES — same mechanism:

Gateway runs: claude --permission-mode bypassPermissions
  └─ MCP: python -m fleet.mcp.server (stdio, per-session)

If backend is LocalAI:
  Gateway still manages the session
  LocalAI model receives system prompt + MCP tool definitions
  Model decides which tool to call
  Gateway executes MCP tool → returns result to model

Quality concern:
  Tool calling accuracy depends on model capability
  hermes-3b: trained for function calling (Hermes 2 Pro)
  Qwen3.5-9B: good tool calling
  Risk: wrong tool called, wrong parameters, hallucinated tools

Mitigation:
  Stage gating still enforces (tool rejects invalid call)
  Doctor detects: protocol_violation from wrong tool calls
  Circuit breaker: too many errors → fallback to Claude
```

### 61.3 Routing Decision for LocalAI

```
Which operations can safely run on LocalAI:

SAFE (structured, low reasoning):
  ✓ Heartbeat (no work) — just read context, respond OK
  ✓ fleet_read_context — direct API call, no LLM
  ✓ fleet_agent_status — direct API call, no LLM
  ✓ fleet_chat (factual message) — structured post
  ✓ Simple task acceptance — structured plan output
  ✓ Simple review (test pass/fail) — pattern matching

RISKY (needs reasoning):
  △ Complex task acceptance — plan quality matters
  △ Code review (logic review) — reasoning required
  △ Contribution (design input) — domain expertise

UNSAFE (must stay Claude):
  ✗ Complex implementation — deep reasoning
  ✗ Architecture design — creative thinking
  ✗ Security analysis — cannot compromise
  ✗ Sprint planning — strategic thinking
  ✗ Complex debugging — multi-step reasoning

Confidence tier from backend:
  Claude opus → expert tier (standard review)
  Claude sonnet → standard tier (standard review)
  LocalAI → trainee tier (challenge + deep review)
  OpenRouter → community tier (challenge + deep review)
```

---

## 62. Board Cleanup & Memory Retention

**What this section is:** How the board stays clean over time.
Task archival, memory retention, cleanup governance.

### 62.1 Noise vs Signal

```
board_cleanup.py identifies 3 noise categories:

  1. [heartbeat] tasks — agent checked in with no work
     Volume: 200+ per day (10 agents × 20 heartbeats)
     Action: archive after 24 hours

  2. [review] Process N pending approvals — fleet-ops housekeeping
     Volume: 10-20 per day
     Action: archive after 48 hours

  3. Resolve conflict tasks — automatic conflict resolution
     Volume: variable
     Action: archive after resolution

Signal tasks (NEVER auto-archive):
  All tasks with: task_type in (epic, story, task, subtask, blocker)
  All tasks with: pr_url set (has code output)
  All tasks with: labor_* fields set (has work attribution)
```

### 62.2 Cleanup Algorithm

```
Trigger: fleet-ops calls fleet_board_cleanup (MCP tool, designed not built)
  OR: scheduled (weekly? PO configures)
  OR: board_size > threshold (auto-trigger)

Parameters:
  archive_heartbeats: bool (default true)
  archive_review_process: bool (default true)
  keep_recent_days: int (default 7)

Process:
  1. Identify noise tasks older than keep_recent_days
  2. Move to archive collection (board memory tagged "archived")
  3. Record: task count archived, categories, total freed
  4. Post: "[cleanup] Archived {n} noise tasks" to IRC #fleet
  5. Trail: record cleanup event with details

Archive is QUERYABLE — not deleted:
  mc.list_memory(tags=["archived", "task:{id}"])
  Can retrieve any archived task by ID
```

### 62.3 Board Memory Retention

```
Board memory grows without bound (JSONL in event bus).

Retention strategy (NOT IMPLEMENTED):
  Hot:    last 7 days — full access, in-memory cache
  Warm:   7-30 days — queryable, slower access
  Cold:   30-90 days — archived, batch query only
  Frozen: 90+ days — read-only, compliance retention

What persists forever:
  - Trail events (audit requirement)
  - PO directives (governance record)
  - Decisions (rationale preservation)

What can be pruned:
  - Routine heartbeat mentions
  - System status updates
  - Duplicate notifications

Current state: event JSONL grows without bound (M5 backlog item).
Rotation/archival strategy needed.
```

### 62.4 Agent Memory Lifecycle

```
Per-agent memory (.claude/memory/) lifecycle:

  Created: by claude-mem plugin during agent sessions
  Persists: across session prune/compact (survives in filesystem)
  Updated: each session (agent discovers new patterns, decisions)
  Pruned: agent can delete stale entries
  Archived: not currently (grows indefinitely)

Cross-session value:
  After prune: agent reads memory → recovers codebase knowledge
  After compact: agent reads memory → recovers task context
  After fresh session: agent reads memory → knows project history

Without claude-mem:
  Agent loses ALL cross-session knowledge
  Re-learns everything each session (expensive, error-prone)
  THIS IS WHY E-02 (Claude-Mem) IS TIER 1 PRIORITY
```
```

---

## 34. Per-Agent Ecosystem — Skills, Plugins, Commands, MCP Servers

**What this section is:** The complete three-layer ecosystem that each
agent needs to be effective. Not a list — the full deployment architecture
with per-role assignments, installation mechanisms, and stage-specific usage.

### 34.1 Layer 1: MCP Servers (Per-Agent)

Each agent gets the `fleet` MCP server (25 tools) PLUS role-specific servers.
Source: `config/agent-tooling.yaml`

```
Agent                 MCP Servers
─────────────────────────────────────────────────────────
architect             fleet, filesystem, github
software-engineer     fleet, filesystem, github, playwright
qa-engineer           fleet, filesystem, playwright
devops-engineer       fleet, filesystem, github, docker
devsecops-expert      fleet, filesystem, docker
fleet-ops             fleet, github
project-manager       fleet, github
technical-writer      fleet, filesystem, github
ux-designer           fleet, filesystem, playwright
accountability        fleet, filesystem

Server packages:
  filesystem:  @modelcontextprotocol/server-filesystem ({{WORKSPACE}})
  github:      @modelcontextprotocol/server-github
  playwright:  @playwright/mcp@latest
  docker:      @modelcontextprotocol/server-docker
  fleet:       {{FLEET_VENV}}/bin/python -m fleet.mcp.server
```

**Deployment:** `scripts/setup-agent-tools.sh` generates per-agent `mcp.json`
from agent-tooling.yaml. Each agent's mcp.json contains ONLY their assigned
servers. NOT BUILT YET (B3 blocker).

**Why per-agent matters:** Engineer gets Playwright for UI testing. DevOps
gets Docker for container ops. Fleet-ops does NOT get filesystem — they
review, they don't edit files. Principle of least privilege per role.

### 34.2 Layer 2: Plugins (Per-Agent)

```
Plugin          Agents              Purpose
─────────────────────────────────────────────────────────
claude-mem      ALL agents          Cross-session semantic memory
                                    Remembers patterns, decisions, context
                                    Persists across session prune/compact

context7        architect,          Up-to-date library/framework docs
                software-engineer   Prevents using deprecated API patterns
                                    React, Python libs, Docker patterns

(codex-plugin-cc mentioned but not assigned — adversarial security review)
```

**Deployment:** `scripts/install-plugins.sh` — iterates agents, installs
role-specific plugins. NOT BUILT YET (B3 blocker).

**Installation command:** `cd agents/{name} && claude plugin install {plugin}`

**Impact of plugins NOT being installed:**
- No cross-session memory → agents re-learn everything each session
- No library docs → agents use deprecated patterns, stale API knowledge
- Cost: re-learning burns tokens that claude-mem would save

### 34.3 Layer 3: Skills (Per-Agent)

85 skills exist (78 in AICP `.claude/skills/` + 7 fleet custom).
32 assigned per role in agent-tooling.yaml.

```
Agent                 Assigned Skills
─────────────────────────────────────────────────────────
architect             architecture-propose, architecture-review, scaffold
software-engineer     feature-implement, refactor-extract
qa-engineer           quality-coverage, quality-audit, foundation-testing
devops-engineer       foundation-docker, foundation-ci, ops-deploy, ops-maintenance
devsecops-expert      infra-security, quality-audit
fleet-ops             pm-assess, quality-audit
project-manager       pm-plan, pm-status-report, pm-retrospective, pm-changelog
technical-writer      feature-document, pm-changelog, pm-handoff
ux-designer           quality-accessibility
accountability        quality-audit

Fleet custom skills (in .claude/skills/):
  fleet-review, fleet-plan, fleet-test, fleet-security-audit,
  fleet-sprint, fleet-communicate, fleet-plane
```

**Skill invocation:** Agents use skills as slash commands
(`/architecture-review`, `/feature-implement`, etc.)

**What's missing:**
- Skills NOT deployed to agent workspaces yet
- Agent CLAUDE.md doesn't mention available skills
- Agent TOOLS.md doesn't list skills as capabilities
- No per-stage skill recommendations:
  - INVESTIGATION: use Context7, /architecture-review
  - ANALYSIS: use /quality-audit
  - WORK: use /feature-implement, /foundation-docker
  - REVIEW: use /fleet-review
- Skill evaluation (which actually help?) not done

### 34.4 Layer 4: Built-In Commands (Agent Training)

Claude Code provides built-in commands agents should USE but aren't
trained to use:

```
Command     When to Use                              Training Status
─────────────────────────────────────────────────────────────────────
/plan       Before complex tasks (design, planning)   NOT TRAINED
/compact    Strategic compaction near context limit    NOT TRAINED
/context    Inspect context before heavy tasks         NOT TRAINED
/clear      Between logical tasks, fresh sprint        NOT TRAINED
/model      Model selection (opus[1m] vs sonnet)       NOT TRAINED
/debug      Interactive debugging workflow             NOT TRAINED
/loop       Scheduled tasks (Feb 2026 feature)         NOT EVALUATED

Missing entirely from agent context:
  - No CLAUDE.md mentions these commands
  - No TOOLS.md lists them
  - No stage-specific recommendations
  - No compaction strategy documented per role
```

### 34.5 Stage-Specific Tool Recommendations

Each methodology stage should guide which tools/skills/commands to use:

```
CONVERSATION (stage 1):
  Tools:    fleet_read_context, fleet_chat
  Skills:   —
  Commands: —
  Purpose:  Understand the requirement, ask questions

ANALYSIS (stage 2):
  Tools:    fleet_read_context, fleet_artifact_create, fleet_commit
  Skills:   /architecture-review (architect), /quality-audit (qa)
  Commands: /context (before heavy reads)
  MCP:      filesystem (read codebase)
  Purpose:  Analyze codebase, produce analysis artifact

INVESTIGATION (stage 3):
  Tools:    fleet_artifact_update, fleet_chat, fleet_commit
  Skills:   Context7 (library docs), /infra-security (devsecops)
  Commands: /plan (plan investigation approach)
  MCP:      filesystem, github (read PRs, branches)
  Purpose:  Research options, produce investigation report

REASONING (stage 4):
  Tools:    fleet_task_accept, fleet_artifact_create, fleet_commit
  Skills:   /architecture-propose (architect), /pm-plan (PM)
  Commands: /plan (plan implementation)
  MCP:      filesystem (verify approach against code)
  Purpose:  Create plan, reference verbatim, get PO confirmation

WORK (stage 5):
  Tools:    fleet_commit, fleet_task_complete
  Skills:   /feature-implement (engineer), /foundation-docker (devops)
  Commands: /debug (when stuck), /compact (near context limit)
  MCP:      filesystem, github, playwright/docker (per role)
  Purpose:  Execute the plan, commit, complete
```

### 34.6 Ecosystem Deployment Plan (3 Tiers)

**Source:** `ecosystem-deployment-plan.md` — 15 items (E-01 to E-15)

```
TIER 1 — IMMEDIATE (config only, no code, zero risk):
  E-01: Prompt caching         → 90% savings on cached input tokens
  E-02: Claude-Mem plugin      → cross-session memory for all agents
  E-03: Context7 plugin        → library docs for architect + engineer
  E-04: Filesystem MCP         → structured file operations

  Impact: 40-60% cost reduction without code changes

TIER 2 — SHORT-TERM (evaluation + focused integration):
  E-05: GitHub MCP server      → PR management, CI status
  E-06: Playwright MCP         → browser automation, UI testing
  E-07: Docker MCP             → container ops
  E-08: Per-agent skills       → domain-specific skills per role
  E-09: LocalAI RAG → fleet    → project knowledge at zero GPU cost
  E-10: Batch API              → 50% savings on async work

TIER 3 — STRATEGIC (architecture decisions required):
  E-11: Agent Teams evaluation → inter-agent collaboration experiment
  E-12: AICP ↔ Fleet bridge    → unified routing
  E-13: LocalAI v4.0 agents   → built-in agent system evaluation
  E-14: OpenRouter free tier   → 29 free models client
  E-15: Multi-fleet identity   → Fleet Alpha + Fleet Bravo
```

---

## 35. Context Strategy — Window, Caching, Rate Limits, Session Management

**What this section is:** The complete context management architecture.
10 PO requirements (CW-01 to CW-10), prompt caching, rate limit rollover,
multi-agent coordination, and the session management brain module.

### 35.1 PO Requirements (Verbatim)

```
CW-01: Know context window size — validate 1M or 200K, don't assume
CW-02: Cost dynamics — 1M = more tokens/turn = faster quota drain
CW-03: Strategic compaction — don't compact prematurely, but don't rot
CW-04: Efficient regathering — recover from memory, not full re-reads
CW-05: Prevent bloat — shouldn't fill with "just a few thousand lines"
CW-06: Control and prove it — document settings and awareness
CW-07: Rate limit rollover — brain tracks distance to reset window
CW-08: Pre-rollover preparation — controlled management before reset
CW-09: Context-proportional awareness — 1M managed more aggressively
CW-10: Multi-agent rollover — stagger/manage 10 agents crossing rollover
```

### 35.2 Context Cost Multiplier

```
Claude Code makes 8-12 API calls per user command.
Each call carries FULL conversation context as input tokens.

Turn 1:   context = 10K   × 1 call  =    10K input tokens
Turn 5:   context = 80K   × 3 calls =   240K input tokens
Turn 10:  context = 200K  × 5 calls = 1,000K input tokens
Turn 15:  context = 500K  × 8 calls = 4,000K input tokens

One "edit this file" command can consume 50K-150K tokens.
A 15-iteration session burns ~200K from context multiplication alone.

Prompt cache has 5-minute lifetime — pauses break it.
Cache break = full-price re-send of ENTIRE context.
```

### 35.3 Rate Limit Rollover Spike (PO Discovery)

```
PO observed: 20% of fresh quota consumed instantly on first message
after rate limit window rollover in a high-context session.

Why: full context re-sent at full price in new window. Previous
window absorbed gradual context buildup. New window gets FULL
accumulated weight in one shot.

PO tested: compact BEFORE rollover → NO spike.

Fleet impact with 10 agents:
  10 agents × heavy context × first heartbeat in new window
  = massive compound spike
  5 × 200K = 1M on rollover ≈ 50% of x5 Pro window

PO direction:
  "force compact all conversation that are too large and will
   cause a spike, this is why we are aware and will not dispatch
   a 1M context big quest when approaching that time"
```

### 35.4 Progressive Rate Limit Awareness

```
Rate Limit %    Action
─────────────────────────────────────────────────────────
< 50%           Normal operation
50%             Medium alert (log)
70%             High alert (IRC)
80%             High alert (IRC + ntfy)
85%             Start preparing (like 7% context remaining):
                  - No new 1M context dispatches
                  - Identify agents with heavy contexts
                  - Begin controlled compaction planning
90%             Actively managing (like 5% context remaining):
                  - Force compact agents over 40-80K
                  - Dump to artifacts if no predicted work
                  - Prepare synthesized re-injection
                  - Don't dispatch heavy tasks
95% (session)   Dispatch PAUSED
90% (weekly)    Dispatch PAUSED

Near rollover:
  - Force compact IS appropriate — saves more than it costs
  - Allow going over 90% budget specifically for compacting
  - After rollover: fresh sessions or synthesized re-injection
```

### 35.5 Multi-Agent Rollover Coordination

```
Brain session_manager.py must track aggregate fleet context math:

  For each agent:
    context_size = from session telemetry or estimate
    predicted_work = from task queue and assignments
    needs_context = has in-progress task that benefits from context

  Aggregate:
    total_fleet_context = sum of all agent contexts
    rollover_spike_risk = total_fleet_context / remaining_quota
    
  Decisions:
    Agent has 80K context, no predicted work → dump + fresh
    Agent has 200K context, continuing same task → keep but compact
    Agent has 40K context, different task coming → fresh session
    Agent has 1M context → ALWAYS compact before rollover
    
  Stagger compactions:
    Don't compact all 10 agents simultaneously
    Compaction itself costs tokens (summary generation)
    Space compactions over last 15% of rate limit window
```

### 35.6 Prompt Caching Strategy

```
Savings: 90% on cached input tokens for repeated prompt prefixes.
Status: DESIGNED, NOT DEPLOYED.

Per-agent strategy:
  Short-lived agents (workers):     cacheRetention = "short"
    Context changes frequently, short cache lifetime OK
  Persistent agents (PM, fleet-ops): cacheRetention = "long"
    Same system prompt across many turns, long cache maximizes savings

What gets cached:
  CLAUDE.md   — same across turns (high cache value)
  SOUL.md     — constant (high cache value)
  IDENTITY.md — constant (high cache value)
  TOOLS.md    — rarely changes (high cache value)
  AGENTS.md   — rarely changes (high cache value)
  context/    — changes every 30s (low cache value)
  HEARTBEAT.md — rarely changes (high cache value)

  Total cacheable: ~20-30K tokens of agent identity/rules
  At 90% savings: ~18-27K tokens saved per API call
  At 10 API calls per command: 180-270K tokens saved per command

Known Anthropic bugs (2026-03-31):
  - Cache breaks after 5-minute pause (10-20x cost inflation)
  - Background agents use Opus quota silently
  - Silent retries on rate-limit errors drain budget
  Two cache-breaking bugs in binary confirmed by reverse-engineering
```

### 35.7 Smart Artifacts Dumping

```
PO direction: "dump (as smart artifacts) it for a synthesised
re-injection later if needed"

When agent has heavy context (40-80K+) and no predicted work:
  1. Agent extracts current work state to artifact files
  2. Agent saves key decisions to memory (claude-mem)
  3. Brain force-compacts or creates fresh session
  4. If related work comes later: synthesized re-injection
     (not full context reload — curated summary with key facts)
  5. If unrelated work: fresh session, no re-injection

NOT the same as compaction — this is intelligent context archival.
The artifacts and memory become the recovery mechanism.
```

### 35.8 Context Visibility

```
Available data from Claude Code JSON session:
  context_window.context_window_size     Total capacity (200K/1M)
  context_window.used_percentage         How full
  context_window.remaining_percentage    How much left
  cost.total_cost_usd                    Session cost
  cost.total_duration_ms                 Session duration
  rate_limits.five_hour.used_percentage  5-hour window usage
  rate_limits.seven_day.used_percentage  7-day window usage

Statusline display:
  Opus [1M] project-name main
  ████████░░░░░░░░ 42% | $0.15 3m0s +256/-31 5h:24% 7d:41%

  Shows: model, context %, cost, rate limits, git branch
  Colors: green <70%, yellow 70-89%, red 90%+
  Deployed via: make install-statusline
```

### 35.9 What Needs Building

```
session_manager.py (brain Step 10):
  1. Read session telemetry per agent
  2. Calculate aggregate fleet context math
  3. Detect approaching rate limit rollover
  4. Decision matrix:
     - Which agents to compact
     - Which agents to dump to artifacts
     - Which agents to leave alone
     - Stagger timing of compactions
  5. Execute: gateway_client.force_compact() or prune + fresh
  6. Track: did compaction work? How much freed?

session_telemetry.py adapter (exists, 230 lines, not wired):
  - to_labor_fields() → LaborStamp
  - to_claude_health() → ClaudeHealth
  - to_storm_indicators() → StormMonitor
  - to_cost_delta() → BudgetMonitor
  Wire into orchestrator: read real data, not estimates

config/fleet.yaml session_management section:
  context_compact_threshold: 85     # % context before considering compact
  rate_limit_prepare_threshold: 85  # % rate limit before preparation
  rate_limit_force_threshold: 90    # % rate limit before forced action
  min_context_to_compact: 40000     # tokens below which don't bother
  max_context_for_dispatch: 800000  # don't dispatch 1M quests above this
  compaction_stagger_minutes: 2     # space between agent compactions
```

---

## 36. Autocomplete Chain Engineering — The Core Design Principle

**What this section is:** How context data arrangement drives correct
agent behavior. This is NOT about what data agents see — it's about
the ORDER and STRUCTURE that makes AI's natural continuation the
correct action. The most important design principle in the fleet.

### 36.1 The Principle

```
LLMs predict the most likely next token given context.
If context is arranged so the most likely continuation IS
the correct professional action, the agent is structurally
prevented from deviating.

Traditional approach: tell agent what to do (rules)
Autocomplete approach: arrange data so correct behavior is natural

Rules can be ignored. Structure cannot.
```

### 36.2 The Onion Order

```
Layer 1: IDENTITY.md (grounding — who am I)
  "You are Software Engineer, Fleet Alpha. Top-tier expert."
  → AI grounds all subsequent output in this identity

Layer 2: SOUL.md (values — what do I care about)
  "You value correctness over speed. Humility over confidence."
  → AI naturally produces careful, honest work

Layer 3: CLAUDE.md (rules — what must I do)
  "You follow 5-stage methodology. You use fleet_commit in work stage."
  → AI follows process because it was established early

Layer 4: TOOLS.md (capabilities — what can I do)
  "fleet_task_complete fires 12 internal operations. Use at end of work."
  → AI knows tool consequences before deciding

Layer 5: AGENTS.md (team — who do I work with)
  "Architect contributes design_input. QA contributes test_criteria."
  → AI naturally acknowledges and references contributions

Layer 6: context/fleet-context.md (state — what's happening)
  "Fleet mode: full-autonomous. PO directive: focus on auth module."
  → AI incorporates current state into decisions

Layer 7: context/task-context.md (task — what am I working on)
  "Task: Implement auth middleware. Verbatim: 'Add JWT middleware that...'"
  "Contributions received: design_input from architect, test_criteria from QA"
  "Your confirmed plan: 1. Create middleware. 2. Add tests. 3. Document."
  → AI naturally continues from plan step 1

Layer 8: HEARTBEAT.md (action — what to do NOW)
  "Priority order: PO directives → messages → task work → HEARTBEAT_OK"
  → AI's immediate next action is the correct priority

Result: AI reads layers 1-8 and the MOST NATURAL next token
is: [start working on step 1 of the confirmed plan, referencing
the architect's design input and QA's test criteria]

Deviation requires FIGHTING the context structure.
```

### 36.3 Task Context Chain Assembly

```
When brain writes task-context.md, it assembles the autocomplete chain:

# YOUR CURRENT TASK
Task: {title}
Stage: {stage} (EXECUTE — you are in work stage)
Readiness: 99%

## VERBATIM REQUIREMENT
"{requirement_verbatim}"
(PO's exact words. Do not interpret. Do not rephrase.)

## ACCEPTANCE CRITERIA
1. {criterion_1}
2. {criterion_2}
3. {criterion_3}
(Every criterion must be met. Fleet-ops will verify each one.)

## YOUR CONFIRMED PLAN
(From your fleet_task_accept call)
1. {step_1}
2. {step_2}
3. {step_3}

## INPUTS FROM COLLEAGUES
### Design Input (from architect)
{contribution_text}
### Test Criteria (from qa-engineer)
{contribution_text}
### Security Requirements (from devsecops)
{contribution_text}

## DELIVERY PHASE: {phase}
(PO-declared — see task requirements for what this phase means)

## WHAT TO DO NOW
Follow your plan. Reference contributions.
fleet_commit for each logical change.
fleet_task_complete when all criteria met.

─────────────────────────────────────────────────────────
AI reads this and the MOST NATURAL continuation is:
  "Let me start with step 1 of my plan..."
  → reads architect's design input for constraints
  → implements step 1
  → fleet_commit
  → moves to step 2
  → ...
  → fleet_task_complete with summary referencing all criteria
```

### 36.4 Heartbeat Chain Assembly

```
When brain writes fleet-context.md for heartbeat:

# FLEET STATE
Mode: {work_mode}
Phase: {cycle_phase}
Agents online: {n}/{total}

## PO DIRECTIVES
{directive_text}
(These are PRIORITY. Read and act on them first.)

## MESSAGES FOR YOU
{mention_messages}
(@mentions from colleagues — respond to these)

## YOUR ASSIGNED TASKS
{task_list_with_status}
(INBOX = new work. IN_PROGRESS = continue. REVIEW = wait.)

## ROLE-SPECIFIC DATA
{role_data}
(PM: unassigned count, sprint progress.
 Fleet-ops: pending approvals, review queue.
 Architect: tasks needing design review.)

## EVENTS SINCE LAST HEARTBEAT
{event_list}
(What happened in the fleet since you last checked)

─────────────────────────────────────────────────────────
AI reads this and the MOST NATURAL continuation is:
  1. Check PO directives → act on them
  2. Check messages → respond to @mentions
  3. Check tasks → work on highest priority
  4. Check role data → proactive role-specific action
  5. If nothing to do → HEARTBEAT_OK
```

### 36.5 Anti-Corruption Through Structure

```
How autocomplete chain prevents specific diseases:

DEVIATION:
  Verbatim appears in EVERY context layer.
  Plan must reference verbatim (enforced check).
  Fleet-ops compares output to verbatim in review.
  → Deviation requires ignoring verbatim in 3+ places.

LAZINESS:
  ALL acceptance criteria listed explicitly.
  Each must be evidenced in completion summary.
  Fleet-ops checks each criterion individually.
  → Laziness requires deliberately skipping visible criteria.

COMPRESSION:
  Full pre-embed data — never summarized.
  Contributions pre-embedded in full.
  PO requirements explicit in verbatim.
  → Compression requires shrinking visible detailed content.

SCOPE CREEP:
  Plan is explicit — step 1, step 2, step 3.
  Verbatim defines exact scope.
  "WHAT TO DO NOW" section is specific.
  → Scope creep requires adding steps not in visible plan.

ABSTRACTION:
  Verbatim is LITERAL — exact words.
  Teaching: "For each word, write what it literally means."
  → Abstraction requires reinterpreting visible literal text.

NOT LISTENING:
  Contributions pre-embedded, not optional reference.
  PO directives appear FIRST in context.
  → Not listening requires ignoring prominent context.
```

### 36.6 What Needs Building

```
autocomplete.py module (fleet/core/autocomplete.py):
  1. assemble_task_chain(agent, task, contributions)
     → Ordered context optimized for correct continuation
  2. assemble_heartbeat_chain(agent, fleet_state, tasks, messages)
     → Ordered context optimized for correct priority action
  3. inject_verbatim_anchors(chain, verbatim)
     → Verbatim inserted at multiple points
  4. inject_phase_display(chain, phase)
     → PO-declared phase visible in context
  5. inject_contributions(chain, contributions)
     → Colleague inputs visible and prominent

context_writer.py update:
  Use autocomplete.py for chain assembly instead of raw concatenation.
  Current: builds text by section concatenation.
  Target: builds text by autocomplete chain engineering.
```

---

## 37. Delivery Phases — PO Declaration, Not System Control

**What this section is:** How phases work in the fleet. Phases are
a PO declaration — the PO says what phase a deliverable is in, and
provides the requirements for what that means.

### 37.1 Phases vs Stages

```
STAGES (methodology — processing order):
  conversation → analysis → investigation → reasoning → work
  Determines: which tools agent can use, what output expected
  Controlled by: brain + MCP tool stage gating

PHASES (delivery — PO declaration):
  Any name the PO chooses. Could be "poc", "mvp", "alpha",
  "potato", "load-tested", "v2-candidate" — anything.
  The PO declares the phase and provides the requirements
  for what that phase means for THIS specific deliverable.

A task has BOTH a stage AND a phase simultaneously.
Stage = where in the process. Phase = PO's declaration of maturity.
```

### 37.2 How Phases Work

`delivery_phase` is a **free text field** on the task. The system:
- Records it
- Displays it
- Filters by it
- Includes it in agent context so agents know what phase they're in

The system does NOT:
- Define what phases exist
- Define what a phase means
- Gate advancement between phases via config or code
- Enforce standards per phase automatically
- Maintain predefined progressions

**The PO provides the requirements** for each deliverable at each
phase through their verbatim requirements on the task. The PO's
words ARE the standard. If the PO says "this MVP needs full test
coverage" — that's the standard. If the PO says "this POC just
needs to prove it works" — that's the standard. Each case is
different because the PO defines it per-case.

### 37.3 Phase Advancement

Phase advancement is simple: the PO changes the `delivery_phase`
field. The PM can request it, agents can suggest it, but the PO
decides. When the phase changes:
- Field updated on task
- Agents see the new phase in their context
- PO provides new requirements for the new phase

### 37.4 Multiple Rounds of Stages Per Phase

A deliverable going from one phase to another may trigger new
rounds of methodology stages. The PM creates new tasks for the
gap between current state and what the PO requires for the new
phase. Each task goes through its own stage progression.

### 37.5 What Needs Building

```
Missing:
  1. fleet_gate_request MCP tool (with chain) — for readiness gates
  2. delivery_phase free text field on TaskCustomFields
  3. Phase display in agent context
  4. Phase in pre-embed so agents know their deliverable's phase

Existing code:
  - is_phase_gate() in methodology module
  - phase field on Task custom_fields
  - Artifact completeness checking (basic)
```

---

## 38. Trail & Audit System — Complete Record

**What this section is:** The trail is the fleet's memory. Every action,
every transition, every contribution, every gate decision, every
approval, every rejection — recorded with WHO (agent + model via
LaborStamp), WHAT (the action), WHEN (timestamp), and WHY (context).

Without trails:
- Fleet-ops reviews blind — no history of how the task got here
- Accountability generator has nothing to audit
- PO can't trace why a task took 3 sprints
- Immune system can't detect repeated failures
- Regression decisions have no evidence base
- Multi-fleet attribution is impossible

Trails are stored as board memory entries tagged `trail` + `task:{id}`.
The accountability generator (§87) reconstructs the full chronological
trail at any time. Every tool call tree (§74) includes a trail event —
even partial trees record what was ATTEMPTED.

### 38.1 Trail Events (30+ types)

```
Task lifecycle:
  trail.task.created          — who, when, type, parent, phase
  trail.task.assigned         — to which agent, by whom
  trail.task.dispatched       — model, effort, backend
  trail.task.stage_changed    — from/to stage, authorization
  trail.task.readiness_changed — from/to %, who changed
  trail.task.checkpoint       — at 50% or 90% milestone
  trail.task.completed        — PR, summary, test results
  trail.task.transferred      — from/to agent, context package
  trail.task.done             — approval granted, final state

Contributions:
  trail.contribution.requested  — type, from role, for task
  trail.contribution.posted     — type, by agent, content ref
  trail.contribution.all_received — all required contributions in

Reviews:
  trail.review.started        — fleet-ops began review
  trail.review.qa_validated   — QA test criteria checked
  trail.review.security       — security review complete
  trail.review.approved       — with reasoning, confidence
  trail.review.rejected       — with reasoning, regression info

Gates:
  trail.gate.requested        — type, by agent, evidence
  trail.gate.decided          — approved/rejected, by PO
  trail.phase.advanced        — from/to phase, evidence

Immune:
  trail.disease.detected      — type, agent, severity
  trail.disease.treated       — action (teach/compact/prune)
  trail.correction.applied    — what was wrong, what was taught

Commits:
  trail.commit.created        — SHA, message, files, agent
  trail.pr.created            — URL, branch, title
```

### 38.2 Trail Storage

```
Board memory entries tagged: trail + task:{id} + type:{event_type}

Each entry:
  content: "{event_type}: {details}"
  tags: ["trail", "task:{id}", "{event_type}", "agent:{name}"]
  source: "orchestrator" | "{agent_name}"
  timestamp: ISO 8601

Reconstruction:
  mc.list_memory(board_id, tags=["trail", "task:{id}"])
  → Returns chronological audit trail for any task
```

### 38.3 Trail Consumers

```
Fleet-ops:    Reads trail during 7-step review (Step 4: check trail)
              Verifies: commits exist, tests ran, labor stamp reasonable

Accountability: Reads ALL trail entries for reporting period
                Produces: compliance_report artifact
                Checks: methodology compliance %, contribution coverage %,
                gate compliance %, trail completeness %

PO:           Reads trail via OCMC or Plane comments
              Sees: full history of every decision, action, review

Doctor:       Reads recent trail for disease detection
              Detects: gaps in trail = laziness, repeated rejections = stuck
```

### 38.4 What Needs Building

```
trail_recorder.py:
  1. record_trail_event(task_id, event_type, details, agent)
  2. get_trail(task_id) → chronological list
  3. check_trail_completeness(task_id) → % complete
  4. Trail event types enum (30+ types)

Integration:
  - Every MCP tool call records trail event
  - Every brain decision records trail event
  - Every event chain step records trail event
  - fleet_task_complete checks trail completeness before allowing
```

---

## 39. Anti-Corruption — Three Lines of Defense

**What this section is:** The complete anti-corruption architecture.
Not just 10 rules in CLAUDE.md — three structural layers that make
corruption progressively harder.

### 39.1 The Core Problem

```
PO (verbatim):
  "AI are lazy and deviant — they don't want to do the work and
   don't want to do it right"
  "Need constant REPEAT AND REMIND of basic logic and common sense"
  "Words and titles used are not for nothing — huge difference
   between generic agents and top-tier agents"

10 diseases documented:
  1. Deviation      — does something different from asked
  2. Laziness       — takes shortcuts, partial work
  3. Confident-but-wrong — sure it understands, but doesn't
  4. Abstraction    — replaces literal words with interpretation
  5. Compression    — minimizes scope, shrinks vision
  6. Context contamination — old context warps new requests
  7. Scope creep    — adds unrequested "improvements"
  8. Cascading fix  — layers fixes, making things worse
  9. Not listening  — produces output instead of processing input
  10. Code without reading — writes without reading existing
```

### 39.2 Line 1: Structural Prevention (Before Disease)

```
AUTOCOMPLETE CHAIN ENGINEERING (§36):
  Data arranged so correct behavior is the natural continuation.
  Deviation requires fighting the context structure.
  Status: NOT BUILT (autocomplete.py missing)

STAGE-GATED TOOL ACCESS:
  fleet_commit blocked during analysis (tool physically rejects call).
  fleet_task_complete blocked outside work stage.
  Doctor detection fires on violation.
  Status: IMPLEMENTED (but stage gating needs expansion, B-01 bug)

CONTRIBUTION REQUIREMENTS AS DISPATCH BLOCK:
  Brain blocks dispatch until required contributions received.
  Agent cannot skip architect design or QA tests.
  Gate won't open without required contributions.
  Status: NOT BUILT (contribution system missing)

PHASE-AWARE STANDARDS INJECTION:
  Standards for MVP included in context.
  Agent naturally produces phase-appropriate work.
  Status: NOT BUILT (phase system missing)

VERBATIM ANCHORING IN EVERY CONTEXT:
  Appears in: task pre-embed, heartbeat, plan artifacts,
  completion claims, review process.
  Impossible to lose track of requirement.
  Status: PARTIAL (verbatim in task pre-embed, not in all layers)
```

### 39.3 Line 2: Detection (When Disease Appears)

```
DOCTOR DETECTION (doctor.py):
  Implemented (4 of 11):
    ✓ protocol_violation (wrong tools for stage)
    ✓ laziness (fast completion, partial criteria)
    ✓ stuck (no progress for threshold)
    ✓ correction_threshold (3 corrections = prune)

  Not implemented (7 of 11):
    ✗ abstraction (literal vs interpreted output)
    ✗ code_without_reading (editing without reading existing)
    ✗ scope_creep (changing code outside task scope)
    ✗ cascading_fix (fix creates new bugs)
    ✗ context_contamination (old context warps new work)
    ✗ not_listening (ignoring PO directives)
    ✗ compression (cutting corners, summarizing instead of doing)

  Not designed yet:
    ✗ contribution_avoidance (ignoring colleague input)
    ✗ synergy_bypass (working without seeking contributions)

STRUCTURAL DETECTION:
  Standards library checks artifact completeness automatically.
  Accountability generator verifies trail completeness.
  Fleet-ops reviews against verbatim requirement.
  Status: PARTIAL (completeness checks exist)
```

### 39.4 Line 3: Correction (After Detection)

```
TEACHING:
  Adapted lesson injected into agent session.
  Not generic rules — specific: "you did X, requirement says Y"
  gateway_client.inject_content(session_key, lesson)
  Status: IMPLEMENTED (teaching.py + adapt_lesson + format_lesson)

FORCE COMPACT:
  Strip bloated, drifted context.
  Agent continues lean and focused.
  gateway_client.force_compact(session_key)
  Status: IMPLEMENTED

PRUNE AND REGROW:
  Kill sick session, fresh session, clean context.
  Persistent data (artifacts, comments) survives.
  gateway_client.prune_agent(session_key)
  Status: IMPLEMENTED

READINESS REGRESSION:
  Task sent back to earlier stage.
  Agent restarts from fundamental level.
  Readiness drops, stage may revert.
  Status: NOT BUILT (regression logic missing)
```

### 39.5 Per-Agent Anti-Corruption Rules (CLAUDE.md)

```
10 rules for every agent:
  1. PO's words are sacrosanct — never deform, interpret, compress
  2. Never summarize when original needed
  3. Never replace PO's words with your own
  4. Never add unrequested scope
  5. Never compress scope
  6. Never skip reading
  7. Never produce code outside work stage
  8. Three corrections on same issue = model wrong, start fresh
  9. Follow autocomplete chain
  10. When uncertain, ask — don't guess
```

---

## 40. Agent Character — Top-Tier Expert Definition

**What this section is:** What it means for each agent to be a "top-tier
expert" and how that's enforced structurally.

### 40.1 PO Requirements

```
PO (verbatim):
  "Words and titles used are not for nothing"
  "huge difference between generic agents and top-tier agents"
  "Top-tier agents don't need overconfidence, self-confirmed bias,
   cheating, getting lost, or derailing"
  "Every role is a top-tier expert of their profession"
```

### 40.2 What Top-Tier Means

```
1. NO OVERCONFIDENCE
   Knows what they don't know. When uncertain, asks.
   Doesn't claim understanding it doesn't have.
   Doesn't proceed on assumptions.

2. NO SELF-CONFIRMED BIAS
   Doesn't rationalize when wrong.
   3 corrections on same issue = model is wrong, start fresh.
   Accepts feedback without defensiveness.

3. NO CHEATING
   Doesn't skip stages, bypass gates, ignore contributions.
   Doesn't produce partial work and claim complete.
   Doesn't auto-approve without genuine review.

4. NO GETTING LOST
   Stays focused on the task at hand.
   Doesn't add unrequested scope.
   Doesn't lose track of the verbatim requirement.
   References the plan and acceptance criteria continuously.

5. ALL PROCESSES, ALL ROADS, OPTIONS
   Explores alternatives before deciding.
   Considers tradeoffs honestly.
   Makes informed decisions, not first-idea decisions.
   Presents options to PO when choices exist.
```

### 40.3 Enforcement Through Structure

```
IDENTITY.md:    Defines agent as top-tier expert with specific specialty
SOUL.md:        Values humility, process respect, collaboration
CLAUDE.md:      Role-specific rules embodying top-tier behavior
Autocomplete:   Data flow a disciplined professional naturally follows
Immune system:  Detects deviation from top-tier behavior
Teaching:       Lessons remind of professional standards
Fleet-ops:      Review holds agents to top-tier quality bar
Accountability: Tracks behavior patterns for long-term improvement
```

### 40.4 Per-Role Expert Definition

```
Architect:       Designs systems, considers scalability, security, maintainability.
                 Reviews code for architectural alignment. Contributes design_input.
                 Explores multiple approaches before recommending one.

Engineer:        Writes production-quality code. Follows patterns established
                 by architect. References QA test criteria during implementation.
                 Commits early and often. Tests thoroughly.

DevSecOps:       Thinks adversarially. Finds vulnerabilities before attackers.
                 Reviews every PR for security implications. Contributes
                 security_requirement. Raises alerts when security compromised.

QA Engineer:     Defines test criteria BEFORE implementation.
                 Covers: happy path, edge cases, regression, security.
                 Validates implementation against predefined criteria.
                 Catches what others miss.

DevOps:          Builds infrastructure as code. Docker, CI/CD, deployment.
                 Automates everything. No manual steps in production.
                 Considers reliability, monitoring, rollback.

PM:              Breaks work into manageable tasks. Assigns to right agents.
                 Tracks progress. Routes gates. Manages sprint. Plans scope.
                 Never does implementation — manages the process.

Fleet-Ops:       Reviews with 7-step protocol. Never rubber-stamps.
                 Verifies acceptance criteria individually. Checks trail.
                 Rejects without hesitation when criteria not met.

Writer:          Produces documentation that enables. Not boilerplate —
                 useful docs that help someone actually use the system.
                 Accuracy verified by engineer/architect.

UX Designer:     Designs interactions, not just screens. Accessibility first.
                 Considers all user states. Produces ux_spec artifacts.

Accountability:  Generates compliance reports. Verifies trail completeness.
                 Tracks methodology compliance across all agents.
```

---

## 41. Cowork, Transfer, Readiness Regression

**What this section is:** Three operational protocols for task management
that are designed but not built.

### 41.1 Cowork Protocol (Multiple Agents on One Task)

```
When a task needs multiple agents (e.g., engineer + architect):

Assignment:
  - Owner: primary agent (only owner calls fleet_task_complete)
  - Coworkers: additional agents (can comment, create artifacts, commit)
  - Brain dispatches to owner; notifies coworkers via mention

Permissions:
  Owner can:    all tools including fleet_task_complete
  Coworker can: fleet_commit, fleet_artifact_*, fleet_chat, fleet_alert
  Coworker cannot: fleet_task_complete, fleet_task_accept

Trail:
  Every action tagged with who did it (owner vs coworker)
  Review: fleet-ops sees full breakdown of who contributed what

Use cases:
  - Architect + engineer on complex feature
  - DevSecOps + engineer on security-critical code
  - QA + engineer on test-driven development

Status: NOT BUILT. No cowork field on tasks. No permission distinction.
```

### 41.2 Transfer Protocol (Task Handoff Between Agents)

```
When task moves from one agent to another:

Trigger:
  PM or brain triggers transfer (agent_name changes on task)

Context packaging:
  1. Source agent's artifacts (design, analysis, investigation)
  2. Source agent's comments (decisions, rationale)
  3. Source agent's contributions received
  4. Current stage and readiness
  5. Summary of what was done and why

Transfer execution:
  fleet_transfer(task_id, to_agent, context_summary)
  1. Package context into transfer bundle
  2. mc.update_task(agent_name=to_agent)
  3. context_writer.write_task_context() with transfer package
  4. Plane sync
  5. IRC notification
  6. events.emit("fleet.task.transferred")
  7. Trail records transfer

Receiving agent sees:
  "Transferred from architect at stage: reasoning, readiness: 80%
   Here's what architect produced: [design artifact, analysis, decisions]
   Here's what QA contributed: [test criteria]
   Continue from reasoning stage."

Status: NOT BUILT. fleet_transfer tool not implemented.
```

### 41.3 Readiness Regression

```
When something goes wrong, task readiness goes BACKWARD:

Triggers:
  1. Fleet-ops REJECTS task in review
     → readiness drops (e.g., 99 → 80)
     → stage may revert (work → reasoning)
     → feedback written to task comments
     → agent sees feedback in next heartbeat

  2. Doctor detects disease during work
     → readiness may drop based on severity
     → teaching injection before regression
     → agent gets lesson + reduced readiness

  3. PO rejects at gate (readiness 90%)
     → readiness drops (90 → 70 or 50)
     → agent must rework plan
     → PO feedback in comments

  4. Challenge engine fails task
     → readiness drops
     → specific failure points in feedback
     → agent addresses and re-submits

Regression mechanics:
  mc.update_task(custom_fields={
    task_readiness: new_value,
    task_stage: new_stage,  # if stage changes
    regressed_reason: "specific feedback"
  })
  events.emit("fleet.task.readiness_regressed")
  trail.record("readiness_regression", from=old, to=new, reason=reason)

What happens after regression:
  - Agent gets updated context in next heartbeat
  - Context shows: "Your task was regressed from 99% to 80% because: ..."
  - Agent addresses feedback
  - Agent re-submits when ready
  - New review cycle starts

Status: NOT BUILT. No regression logic in MCP tools or brain.
```

---

## 42. Notification Routing Matrix — Who Gets Notified When

**What this section is:** Complete mapping of every event to every
notification channel. Not partial — every case.

### 42.1 Notification Channels

```
IRC Channels:
  #fleet          — general fleet activity
  #reviews        — review requests and decisions
  #alerts         — security alerts, escalations, health issues
  #gates          — gate requests and PO decisions (NOT IMPLEMENTED)
  #contributions  — contribution posts and completions (NOT IMPLEMENTED)

ntfy Topics:
  fleet-alert     — urgent alerts to PO
  fleet-review    — review notifications
  fleet-gates     — gate requests needing PO decision

Board Memory:
  mention:{agent} — targeted message to specific agent
  directive       — PO directive to fleet
  trail           — audit trail entry

Plane:
  Issue comments  — task status updates
  Issue state     — status transitions
```

### 42.2 Complete Routing Matrix

```
Event                        IRC          ntfy         Board Memory   Plane
────────────────────────────────────────────────────────────────────────────
Task created                 #fleet       —            trail          create issue
Task assigned                #fleet       —            mention:agent  comment
Task dispatched              #fleet       —            trail          comment
Stage changed                —            —            trail          —
Readiness at 50%             —            —            trail          comment
Readiness at 90% (gate)      #gates       fleet-gates  trail+gate     comment
Gate approved                #gates       —            trail          comment
Gate rejected                #gates       —            trail          comment
Task accepted (plan)         #fleet       —            trail          comment
Contribution requested       #contrib     —            mention:role   —
Contribution posted          #contrib     —            mention:target —
All contributions received   —            —            trail          comment
Commit created               —            —            trail          —
Task completed (PR)          #reviews     fleet-review trail          state→review
Review started               #reviews     —            trail          —
QA validated                 #reviews     —            trail          comment
Security reviewed            #reviews     —            trail          comment
Approved                     #reviews     —            trail          state→done
Rejected                     #reviews     —            trail+mention  comment
Readiness regressed          #fleet       —            trail+mention  comment
Task done                    #fleet       —            trail          state→done
Task transferred             #fleet       —            trail+mention  comment
Phase advanced               #fleet       fleet-gates  trail          comment
Security alert               #alerts      fleet-alert  trail+alert    —
Escalation                   #alerts      fleet-alert  trail+mention  —
Pause request                #fleet       fleet-alert  trail          —
Storm WARNING                #alerts      —            trail          —
Storm STORM                  #alerts      fleet-alert  trail          —
Storm CRITICAL               #alerts      fleet-alert  trail          —
Disease detected             #alerts      —            trail          —
Agent pruned                 #alerts      —            trail          —
PO directive                 #fleet       —            directive      —
Fleet mode changed           #fleet       —            trail          —
Backend mode changed         #fleet       —            trail          —
Budget threshold hit         #alerts      fleet-alert  trail          —
Rate limit approaching       #alerts      fleet-alert  trail          —
```

### 42.3 What's Implemented vs Missing

```
Implemented:
  ✓ #fleet channel (general notifications)
  ✓ #reviews channel (review requests)
  ✓ #alerts channel (alerts, escalations)
  ✓ ntfy fleet-alert (PO notifications)
  ✓ Board memory (mentions, directives, trail basics)
  ✓ Plane sync (issue state, comments — partial)

Missing:
  ✗ #gates channel (gate requests)
  ✗ #contributions channel (contribution activity)
  ✗ ntfy fleet-gates topic (gate requests to PO)
  ✗ ntfy fleet-review topic (review notifications)
  ✗ Many trail event types not emitted
  ✗ Contribution routing (mention:target, mention:role)
  ✗ Readiness regression routing
  ✗ Phase advancement routing
  ✗ QA/security review routing
```

---

## 43. Brain Layers 2 & 3 — Chain Registry and Logic Engine

**What this section is:** The brain architecture beyond the 16-step cycle.
Layer 1 is the poll loop. Layer 2 is event-driven. Layer 3 is rule-based.

### 43.1 Layer 2: Chain Registry (Event-Driven)

```
When an event occurs, the chain registry looks up ALL registered
handlers and fires them in parallel.

Registration:
  chain_registry.register("fleet.task.completed", [
    handler_update_parent,      # Check parent completion
    handler_notify_contributors, # Tell contributors their input was used
    handler_update_sprint,      # Update sprint progress
    handler_record_trail,       # Record in audit trail
    handler_trigger_challenge,  # Challenge engine evaluation
  ])

  chain_registry.register("fleet.contribution.posted", [
    handler_update_target_context, # Update target task context
    handler_check_completeness,    # All contributions received?
    handler_notify_pm,             # PM knows progress
    handler_record_trail,
  ])

  chain_registry.register("fleet.gate.requested", [
    handler_notify_po,           # ntfy + IRC
    handler_block_dispatch,      # Don't dispatch until gate decided
    handler_record_trail,
  ])

Execution:
  event emitted → registry.dispatch(event)
  All matching handlers fire in parallel
  Each handler: verify preconditions → execute → emit completion event
  Completion events may trigger MORE handlers (cascade)
  Cascade depth limit: configurable (default 5)

Event types (50+ designed):
  fleet.task.*           — task lifecycle events
  fleet.contribution.*   — contribution events
  fleet.gate.*           — gate events
  fleet.phase.*          — phase events
  fleet.review.*         — review events
  fleet.alert.*          — alert events
  fleet.storm.*          — storm events
  fleet.system.*         — system events (mode change, etc.)
  fleet.disease.*        — immune system events
  fleet.session.*        — session management events

Status: event_chain.py and chain_runner.py exist but chain_registry
pattern NOT implemented. Current: direct function calls in orchestrator.
Target: event-driven with registered handlers.
```

### 43.2 Layer 3: Logic Engine (Rule-Based, Configurable)

```
The logic engine evaluates configurable rules for dispatch decisions.
Rules are data, not code — PO can modify without code changes.

10 Dispatch Gates (configurable):

  Gate 1: agent_assigned
    Rule: task.custom_fields.agent_name is not empty
    On fail: "No agent assigned. PM needs to assign."

  Gate 2: agent_has_capacity
    Rule: agent has no IN_PROGRESS task (max concurrent = 1)
    On fail: "Agent {name} already working on task {other_task_id}"

  Gate 3: blockers_cleared
    Rule: all depends_on tasks are DONE
    On fail: "Blocked by: {blocker_task_ids}"

  Gate 4: contributions_received
    Rule: all required contributions for this task type + phase received
    On fail: "Missing contributions: {missing_types} from {missing_roles}"

  Gate 5: verbatim_present
    Rule: task.custom_fields.requirement_verbatim is not empty
    On fail: "No verbatim requirement. PM must fill."

  Gate 6: delivery_phase_set
    Rule: task.custom_fields.delivery_phase is not empty
    On fail: "No delivery phase set."

  Gate 7: readiness_met
    Rule: task.custom_fields.task_readiness >= 99
    On fail: "Readiness at {readiness}%. Must reach 99."

  Gate 8: stage_allows_dispatch
    Rule: task.custom_fields.task_stage == "work"
    On fail: "Task in {stage} stage. Must reach work stage."

  Gate 9: budget_allows
    Rule: budget_monitor.is_safe() == True
    On fail: "Budget limit reached. Dispatch paused."

  Gate 10: work_mode_allows
    Rule: fleet_state.work_mode not in ("work-paused", "finish-current")
    On fail: "Fleet paused. No new dispatches."

Configuration:
  config/dispatch-gates.yaml:
    gates:
      - name: agent_assigned
        enabled: true
        fail_action: skip  # skip | block | escalate
      - name: contributions_received
        enabled: true
        fail_action: skip  # skip for now, block when PO decides

Status: NOT BUILT. Current dispatch uses hardcoded gates in
orchestrator.py:_dispatch_ready_tasks(). Target: configurable
rules that PO can adjust.
```

### 43.3 What Needs Building

```
chain_registry.py:
  1. register(event_type, handlers) — add handler list for event type
  2. dispatch(event) — fire all registered handlers
  3. Cascade depth tracking (prevent infinite loops)
  4. Handler result collection (which succeeded, which failed)
  5. Dead letter queue (events with no handlers)

logic_engine.py:
  1. evaluate_gates(task, agent, fleet_state, contributions) → GateResult
  2. Load rules from config/dispatch-gates.yaml
  3. Per-gate: evaluate rule, produce pass/fail with reason
  4. Aggregate: all pass → dispatch. Any fail → explain why.
  5. Gate configuration hot-reload (PO changes without restart)

Both integrate into brain Step 5 (dispatch) and Step 1b (event queue).
```

---

## 44. Agent Signatures — Load-Bearing Provenance Infrastructure

**What this section is:** Signatures are NOT cosmetic labels on comments.
They are the provenance data layer that feeds EVERY accountability,
cost, quality, and trust system in the fleet. Without signatures, you
cannot answer: "Who did this work? With what quality of model? At what
cost? Under what conditions? Can I trust it? Should I route more work
to this agent or less? Is this agent efficient or burning budget? Did
fleet-ops actually review or rubber-stamp?"

Signatures connect to:
- **Budget optimization:** Cost per agent, per task, per model — the
  brain uses this to make strategic call decisions (§97 budget mode)
- **Quality tracking:** Which model produced which output — if a task
  fails review, was it a sonnet task that needed opus? Model selection
  feedback loop
- **Immune system input:** Anomaly detection (heartbeat cost > $0.10,
  void rate too high, review duration < 30s = rubber stamp disease)
- **Accountability verification:** The accountability generator (§87)
  reads LaborStamps to verify process compliance — not just "was a
  review done" but "was it done with sufficient effort and reasoning"
- **Trust scoring:** confidence_tier (expert/standard/trainee/community)
  affects how fleet-ops weighs the work during review. Expert-tier work
  from opus gets lighter review. Trainee-tier from LocalAI gets deeper
  scrutiny.
- **Cost correlation:** PO sees cost per story point, per agent, per
  sprint — which agents are efficient, which tasks cost too much, where
  to invest in LocalAI offload
- **Trail integrity:** Every trail event carries a signature — the audit
  trail is not just WHAT happened but WHO did it, with WHAT, under WHAT
  conditions. Without signatures, trails are unsigned claims.
- **Brain decisions:** The brain reads historical LaborStamps to calibrate
  model selection, effort levels, and session strategy. If opus produces
  faster reviews than sonnet, the brain learns to route reviews to opus.
- **Multi-fleet attribution:** In shared Plane, signatures distinguish
  alpha-architect's work from bravo-architect's work (§91)
- **Economic model:** The §47 economic projections are built on signature
  data — cost_usd per stamp aggregated per sprint = actual vs projected

### 44.1 What Already Exists

The labor attribution system is ~70% built:

```
LaborStamp (25 fields in labor_stamp.py):
  WHO:        agent_name, agent_role
  WHAT:       backend, model, model_version, effort
  HOW:        skills_used, tools_called, session_type
  CONFIDENCE: confidence_tier (auto-derived from backend+model)
              expert (claude+opus), standard (claude+sonnet),
              trainee (localai), community (openrouter)
  COST:       duration_seconds, estimated_tokens, estimated_cost_usd
  EFFORT:     lines_added, lines_removed, cache_read_tokens
  ITERATION:  iteration, challenge_rounds_survived, challenge_types_faced
  CONTEXT:    fallback_from, fallback_reason
  TIMESTAMP:  ISO 8601

DispatchRecord (saved at dispatch time):
  task_id, agent_name, backend, model, effort, selection_reason,
  skills, dispatched_at

Where stamps appear (implemented):
  ✓ Task custom fields (8 labor_* fields on OCMC task)
  ✓ Completion comment (labor attribution table)
  ✓ PR body (References section with backend, model, confidence)
  ✓ Comment footer: <sub>software-engineer · sonnet-4-6 · standard</sub>
  ✓ PR footer: <sub>Generated by OpenClaw Fleet · sonnet-4-6 · standard</sub>
```

### 44.2 What's Missing From Signatures

```
MISSING from LaborStamp:
  ✗ context_window_size (200K or 1M — available in SessionSnapshot)
  ✗ budget_mode (fleet tempo at time of work)
  ✗ context_used_pct (how full was context when work completed)
  ✗ rate_limit_pct (how close to rate limit when work done)

MISSING from DispatchRecord:
  ✗ budget_mode
  ✗ context_window_size
  ✗ fleet_state snapshot (work_mode, cycle_phase, backend_mode)

MISSING wiring:
  ✗ Session telemetry → LaborStamp (adapter exists, not called)
    tools.py line 695: estimated_tokens=0 (hardcoded!)
    Should call: session_telemetry.to_labor_fields(snap)
  ✗ lines_added/removed (fields exist, not passed)
  ✗ session_type hardcoded to "fresh" (should read from session)
  ✗ model_version is just model name copy (should be full versioned ID)
  ✗ fleet.labor.recorded event (defined, not emitted)

MISSING custom fields on task:
  ✗ labor_context_window
  ✗ labor_model_version
  ✗ labor_tools_called
  ✗ labor_session_type
  ✗ labor_challenge_rounds
  ✗ labor_lines_added
  ✗ labor_lines_removed
```

### 44.3 Signature Levels

The PO wants signatures at EVERY level, not just task completion:

```
LEVEL 1: Individual Tool Call
  Every MCP tool call could carry a mini-signature:
  - agent_name, model, timestamp
  - Embedded in trail: "fleet_commit by alpha-engineer (opus-4-6, 42% context)"
  - Lightweight — just identity + model + context %

LEVEL 2: Tool Chain (fleet_task_complete = 12+ operations)
  The chain itself has a signature:
  - Started by: agent_name at timestamp
  - Model: opus-4-6, effort: high
  - Chain: 12 operations, 10 succeeded, 2 optional skipped
  - Duration: 45 seconds
  - Surfaces hit: MC, GitHub, IRC, ntfy, Plane

LEVEL 3: Group Call (fleet_contribute to parent task)
  Contribution signature:
  - Contributor: alpha-architect (opus-4-6, expert)
  - Contribution type: design_input
  - Context: 35% used, 5h window at 24%
  - Attached to parent task as typed comment

LEVEL 4: Task Completion (full LaborStamp)
  Everything:
  - Full LaborStamp (25+ fields)
  - In: task custom fields, completion comment, PR body,
    trail, event bus, board memory
  - Renderable: table in comment, metadata in PR, searchable in analytics

LEVEL 5: Heartbeat Signature
  Already exists (heartbeat_stamp.py):
  - agent_name, backend, model, duration, cost, void (did nothing)
  - Anomaly detection: cost > $0.10, rate > 30/hour, void rate

LEVEL 6: Review Signature (fleet-ops approval)
  fleet-ops signs their review:
  - Reviewer: alpha-fleet-ops (opus-4-6, expert)
  - Decision: approved, confidence: 90%
  - Reasoning: specific (not rubber stamp)
  - Duration of review
  - Criteria checked: 7/7
```

### 44.4 What Needs Building

```
1. Add fields to LaborStamp:
   context_window_size, context_used_pct, budget_mode,
   rate_limit_pct, fleet_state_snapshot

2. Wire session telemetry → stamp assembly:
   Call to_labor_fields(snap) in fleet_task_complete
   Populate: lines_added, lines_removed, cache_read_tokens,
   actual tokens (not estimated), actual cost, session_type

3. Emit fleet.labor.recorded event on completion

4. Mini-signatures on trail events:
   Every trail entry includes: agent, model, context%
   Lightweight but complete attribution

5. Review signature on approval:
   fleet_approve records: reviewer identity, model, duration,
   criteria checked count, reasoning length

6. Write all labor fields to TaskCustomFields (currently 8, need 15+)
```

---

## 45. Readiness vs Progress — Two Distinct Concepts

**What this section is:** The PO identified that `task_readiness` conflates
two different things. This section defines the separation.

### 45.1 The Problem

```
Current: ONE field — task_readiness (0-100)

Pre-dispatch meaning: "Is PO authorization confirmed?"
  0   → nothing defined
  50  → direction review checkpoint
  90  → final review checkpoint
  99  → PO approved plan, authorized to work
  ← DISPATCH GATE: readiness >= 99

Post-dispatch meaning: "How far through quality gates?"
  99  → work authorized (same value as pre-dispatch!)
  70  → work complete, ready for challenge
  80  → challenge passed, ready for review
  90  → review passed, ready for PO final
  95  → PO approved
  100 → done

PROBLEM: readiness=99 means TWO things:
  1. "PO confirmed plan, go work" (pre-dispatch gate)
  2. "Currently working on approved plan" (during work)

And readiness DROPS from 99 to 70 when work is done.
That's backwards — work is DONE but readiness goes DOWN.
```

### 45.2 The Solution: Two Fields

```
FIELD 1: task_readiness (renamed conceptually to "work_readiness")
  Purpose: Is this task READY to be worked on?
  Values:  0 → 99 (progressive authorization)
  Gate:    >= 99 to dispatch
  Set by:  PO (manual), brain (from artifact suggestions)
  
  0   → nothing defined
  10  → conversation started, some understanding
  30  → analysis done, codebase understood
  50  → investigation done, options explored (CHECKPOINT)
  80  → reasoning done, plan exists
  90  → plan reviewed, PO final gate (CHECKPOINT)
  99  → PO authorized: "go work"
  
  This field moves FORWARD through stages and NEVER goes backward
  during normal flow. Only regresses on rejection.

FIELD 2: task_progress (NEW)
  Purpose: How far is the WORK toward completion/review?
  Values:  0 → 100 (work progression)
  
  0   → work not started (just dispatched)
  10  → initial implementation started
  30  → core implementation in progress
  50  → implementation substantially done
  70  → work complete, PR ready (WORK_COMPLETE)
  80  → challenge passed (CHALLENGE_PASSED)
  90  → fleet-ops review passed (REVIEW_PASSED)
  95  → PO final approval (PO_APPROVED)
  100 → done (DONE)
  
  This field ONLY exists after dispatch.
  Set by: agent (fleet_task_progress), challenge system, review system.

FIELD 3: artifact_completeness_pct (EXISTING, separate concern)
  Purpose: How complete is the primary artifact?
  Values:  0-100 (continuous)
  Set by:  artifact_tracker.py (automatic from filled fields)
  Used for: suggesting readiness, phase standards
```

### 45.3 How They Interact

```
BEFORE DISPATCH:
  task_readiness progresses: 0 → 10 → 30 → 50 → 80 → 90 → 99
  task_progress: does not exist (NULL or 0)
  artifact_completeness: tracks artifact during reasoning stage

  PO gate at readiness 90:
    Agent calls fleet_gate_request
    PO reviews plan, confirms: readiness → 99
    Orchestrator dispatches

DURING WORK:
  task_readiness: stays at 99 (authorization doesn't change)
  task_progress: 0 → 10 → 30 → 50 → 70 (work advancing)
  artifact_completeness: may update if work produces artifacts

AT COMPLETION:
  task_readiness: stays at 99
  task_progress: 70 (WORK_COMPLETE — agent called fleet_task_complete)

DURING REVIEW:
  task_readiness: stays at 99
  task_progress: 70 → 80 (challenge passed) → 90 (review passed) → 100

ON REJECTION:
  task_readiness: REGRESSES (99 → 80, back to reasoning)
  task_progress: RESETS to 0 (start over)

ON DONE:
  task_readiness: 99 (was authorized, stays authorized)
  task_progress: 100 (fully complete)
```

### 45.4 What Needs Changing

```
Code changes:
  1. Add task_progress to TaskCustomFields (models.py)
  2. fleet_task_progress tool: update task_progress (NOT readiness)
  3. fleet_task_complete: set task_progress = 70 (WORK_COMPLETE)
  4. Challenge system: update task_progress (80, not readiness)
  5. fleet_approve: update task_progress (90 on approve)
  6. Brain transition: task_progress 100 → task status DONE
  7. Plane sync: sync task_progress as separate label
  8. Context pre-embed: show both fields separately

Dispatch gate: UNCHANGED
  Still checks task_readiness >= 99

Tool behavior change:
  fleet_task_progress(done, next_step, blockers, progress_pct)
    Currently: only posts a comment
    Should also: update task_progress custom field

Documentation updates:
  - methodology.md: separate readiness from progress
  - challenge system docs: use progress not readiness
  - standards: reference both fields
```

### 45.5 Impact on Other Systems

```
Artifact tracker:
  suggest_readiness() → feeds task_readiness (pre-dispatch)
  Does NOT affect task_progress

Challenge system:
  Updates task_progress (70→80), NOT task_readiness

Fleet-ops review:
  Updates task_progress (80→90), NOT task_readiness

Brain dispatch:
  Checks task_readiness only (>= 99)
  Does NOT check task_progress

Pre-embed context:
  Shows both:
  "Readiness: 99% (authorized) | Progress: 50% (implementing)"

Trail:
  Separate events:
  trail.task.readiness_changed (pre-dispatch authorization)
  trail.task.progress_changed (work progression)
```

---

## 46. LightRAG Integration — Knowledge Graph RAG for OCMC

**What this section is:** Strategic analysis of integrating LightRAG
(https://github.com/hkuds/lightrag) as the knowledge layer for OCMC
and the fleet ecosystem.

### 46.1 What LightRAG Is

```
LightRAG = Knowledge Graph RAG (not just vector search)

Architecture:
  Documents → LLM extracts entities + relationships → Knowledge Graph
  Queries → Graph traversal + Vector similarity → Structured answers

4 Storage Layers:
  1. KV Storage:     LLM response cache, text chunks, doc metadata
  2. Vector Storage:  Entity embeddings, relation embeddings, chunk embeddings
  3. Graph Storage:   Entity-relationship knowledge graph
  4. Doc Status:      Document processing tracking

6 Query Modes:
  local:   Entity-level, context-dependent
  global:  Relationship-level, cross-document
  hybrid:  Local + global combined
  naive:   Basic vector similarity (like LocalAI /stores/)
  mix:     Knowledge graph + vector + reranking (best quality)
  bypass:  Skip retrieval, pass to LLM directly

Key difference from LocalAI /stores/:
  LocalAI: flat chunks, cosine similarity (isolated fragments)
  LightRAG: entities + relationships + chunks (structured knowledge)
  
  "What is the relationship between X and Y?" — impossible with vector-only
  "How does component A connect to component B?" — LightRAG can answer

License: MIT (fully permissive)
Stars: 31,474 (as of 2026-04-02)
```

### 46.2 What It Provides

```
Web UI (React/Vite):
  ✓ Interactive knowledge graph visualization (force-directed)
  ✓ Node queries (click entity → see relationships)
  ✓ Subgraph filtering
  ✓ Document upload and indexing management
  ✓ RAG query interface with streaming
  ✓ Served at port 9621 /webui/

REST API (FastAPI):
  /query              — RAG queries (all 6 modes)
  /query/stream       — streaming queries
  /documents/upload   — document ingestion
  /documents/pipeline_status — indexing progress
  Graph CRUD endpoints (entities, relations, merge)

Ollama-compatible API:
  /api/chat, /api/generate — Open WebUI can connect directly

Authentication: JWT + API key support
Production: Gunicorn + Uvicorn multiprocess
Features: citation/source attribution, entity merging,
          workspace isolation (multi-tenant), data export
```

### 46.3 How It Differs from What We Have

```
                    LocalAI /stores/    AICP rag.py       LightRAG
─────────────────────────────────────────────────────────────────────
Retrieval           Vector similarity   Vector + rerank   Graph + Vector + rerank
Knowledge structure Flat chunks         Flat chunks       Entity-Relationship graph
Multi-hop           No                  No                Yes (graph traversal)
Entity dedup        No                  No                Yes (automatic merging)
Query modes         1 (similarity)      1 + rerank        6 modes
Web UI              No                  No                Yes (graph visualization)
Document mgmt       Basic              File ingestion    Full lifecycle
Storage backends    SQLite             SQLite            8+ vector, 5+ graph, 5+ KV
LLM requirement     Embedding only     Embedding + rerank LLM + Embedding
Docker              Part of LocalAI    Part of AICP      Standalone service
```

### 46.4 PO Use Cases

```
USE CASE 1: Research Sharing
  PO researches Shaders → ingests research into LightRAG
  → Knowledge graph captures: concepts, relationships, tools, techniques
  → Any agent can query: "what shader approaches were researched?"
  → Graph shows: connections between shader techniques and project needs

USE CASE 2: FAQs / Frequent Confusions
  Front-facing documentation, common mistakes, known issues
  → Ingested into LightRAG with entity extraction
  → Agents query before asking PO: "is this a known confusion?"
  → Reduces PO interruptions for repeat questions

USE CASE 3: Plane / PM Documents & Artifacts
  Sprint plans, architecture decisions, design docs, analysis artifacts
  → Ingested into LightRAG from Plane via sync
  → Knowledge graph shows: decision → implementation → outcome
  → PO sees a MESH of everything — not isolated docs but relationships

USE CASE 4: Cross-Project Knowledge
  AICP architecture, Fleet design, DSPD PM docs, NNRT pipeline docs
  → All ingested into one LightRAG instance
  → "How does the AICP router relate to the Fleet router?"
  → Graph traversal finds the connection even across projects

USE CASE 5: Agent Memory Augmentation
  Agent work products, decisions, lessons learned
  → Ingested into LightRAG over time
  → New agents or fresh sessions can query: "what did architect
    decide about auth middleware last sprint?"
  → Supplements claude-mem with structured, graph-based memory
```

### 46.5 Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PO / OCMC                                 │
│                                                              │
│  Document upload, research sharing, FAQ management           │
│  Knowledge graph browsing via LightRAG WebUI (:9621)         │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    LightRAG Server                           │
│                    Port 9621 (HTTP + WebUI)                   │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ KV Store │ │ Vector   │ │ Knowledge│ │ Doc      │       │
│  │ (chunks) │ │ (embed)  │ │ Graph    │ │ Status   │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                                                              │
│  LLM: Claude (entity extraction, high quality)               │
│  Embedding: LocalAI bge-m3 (zero GPU cost, CPU)              │
│  Reranking: LocalAI bge-reranker (zero GPU cost, CPU)        │
└──────────────────────┬───────────────────────────────────────┘
                       │
          ┌────────────┼──────────────────┐
          ↓            ↓                  ↓
   ┌────────────┐ ┌──────────┐    ┌──────────────┐
   │ Brain      │ │ OCMC     │    │ Agents       │
   │ (context   │ │ (memory  │    │ (MCP query   │
   │  refresh)  │ │  sync)   │    │  to LightRAG)│
   │            │ │          │    │              │
   │ Inject     │ │ Existing │    │ New MCP tool:│
   │ relevant   │ │ KB ↔     │    │ fleet_query  │
   │ knowledge  │ │ LightRAG │    │ _knowledge() │
   │ into agent │ │ sync     │    │              │
   │ context    │ │          │    │              │
   └────────────┘ └──────────┘    └──────────────┘
```

### 46.6 LightRAG vs LocalAI RAG — Different Things

```
LocalAI RAG (/stores/ API):
  - Vector store with cosine similarity
  - Good for: "find chunks similar to this query"
  - Fast, simple, zero-cost (CPU embeddings)
  - No knowledge structure — flat chunks
  - No entity extraction — just embeddings
  - Good for: code search, documentation lookup

LightRAG (graph + vector):
  - Knowledge graph with entity relationships
  - Good for: "how does X relate to Y across documents?"
  - Slower indexing (needs LLM for entity extraction)
  - Rich knowledge structure — entities, relations, types
  - Entity deduplication and merging
  - Good for: research synthesis, decision tracking, cross-project mesh

They complement each other:
  LocalAI /stores/: fast, cheap, good for "find relevant code"
  LightRAG: deep, structured, good for "understand relationships"

Both can use LocalAI for embeddings (bge-m3, CPU, free).
LightRAG needs a capable LLM for entity extraction (32B+ recommended).
```

### 46.7 Practical Deployment Considerations

```
Hardware (your setup: 8GB VRAM, single-active backend):

  Entity extraction:
    - LocalAI 7B hermes: possible but lower quality graphs
    - Claude (cloud): high quality graphs, costs tokens
    - Hybrid: Claude for initial indexing, LocalAI for queries
    
  Embedding:
    - LocalAI bge-m3: works on CPU, zero GPU cost ✓
    - Same embedding used for LightRAG AND LocalAI /stores/
    
  Reranking:
    - LocalAI bge-reranker: works on CPU, zero GPU cost ✓
    - Already in your LocalAI setup

  Storage:
    - File-based defaults (JSON KV, NanoVectorDB, NetworkX)
    - No Milvus/Neo4j needed for initial deployment
    - Production: PostgreSQL with pgvector + AGE (optional)

Docker:
  - Add to docker-compose.yaml as new service
  - Port 9621 alongside LocalAI 8090, OCMC 8000, OpenClaw 9400
  - Volume: ./data/rag_storage for persistence

Indexing strategy:
  - Batch: ingest design docs, system docs, architecture docs
  - Incremental: sync new artifacts, decisions, research
  - Selective: not everything — curated knowledge worth graphing
```

### 46.8 OCMC Integration Path

```
Phase 1: Deploy + Manual Use
  - Deploy LightRAG with Docker
  - PO uses WebUI to upload research, browse graph
  - No fleet integration yet — just PO tool

Phase 2: OCMC Sync
  - Connect OCMC board memory → LightRAG ingestion
  - Decisions, directives, trail entries auto-ingested
  - Existing OCMC KB feature → LightRAG as backend
  - PO sees knowledge graph of fleet decisions over time

Phase 3: Agent Integration
  - New MCP tool: fleet_query_knowledge(question, mode)
  - Brain pre-embed: inject relevant knowledge into context
  - Agents can ask: "what was decided about auth middleware?"
  - Graph answers with: decision + rationale + who decided + when

Phase 4: Cross-Project Mesh
  - Ingest: AICP docs, Fleet docs, DSPD PM docs, NNRT docs
  - One knowledge graph spanning all 4 projects
  - PO query: "what depends on LocalAI across all projects?"
  - Graph shows: AICP router, Fleet dispatch, DSPD inference
  
Phase 5: Plane Artifact Sync
  - Sprint plans, architecture decisions, design docs
  - Auto-ingest from Plane via API
  - Knowledge graph captures: task → decision → outcome
  - PM productivity: "what did we learn from sprint 3?"
```

### 46.9 Open Questions for PO

```
1. Entity extraction quality vs cost:
   Use Claude for indexing (expensive but accurate)?
   Use LocalAI hermes (free but lower quality)?
   Hybrid (Claude initial, LocalAI incremental)?

2. What gets ingested:
   Everything? Or curated selection?
   Auto-sync from Plane? Manual upload only?
   Agent work products? Or just PO-approved artifacts?

3. Query access:
   PO only? All agents? Selected agents?
   Via MCP tool? Via brain pre-embed? Both?

4. Relationship to existing OCMC KB:
   Replace OCMC's basic KB? Or layer on top?
   Sync bidirectionally? Or one-way from OCMC → LightRAG?

5. Multi-workspace:
   One graph per project? Or one unified graph?
   LightRAG supports workspace isolation — use it?

6. LocalAI relationship:
   LightRAG uses LocalAI for embeddings (shared bge-m3)?
   Or separate embedding service?
   Conflict with single-active-backend?
   (Embeddings run on CPU, no GPU conflict)
```

---

## 47. Economic Model — Cost Projections & ROI

**What this section is:** The financial reality of running the fleet.
Per-task costs, LocalAI payback timeline, optimization levers.

### 47.1 Current Cost Baseline (100% Claude)

```
Subscription: Max 5X ($100/month, 5x Pro quota)

Per-agent costs (estimated):
  Heartbeat (no work):         ~$0.02-0.10 per heartbeat
  Simple task (structured):    ~$0.50-2.00 per task
  Complex task (architecture): ~$2.00-10.00 per task
  Review (fleet-ops 7-step):   ~$1.00-3.00 per review

Fleet costs per day (10 agents, all Claude):
  Heartbeats: 10 agents × ~20 heartbeats/day × $0.05 = ~$10/day
  Tasks: ~5 tasks/day × $3 avg = ~$15/day
  Reviews: ~3 reviews/day × $2 = ~$6/day
  Total: ~$30/day = ~$900/month

  This EXCEEDS Max 5X quota ($100/month).
  Actual constraint: rate limit windows, not dollar cost.
  Rate limit = tokens per 5-hour window + 7-day rolling.
```

### 47.2 Cost Reduction Levers

```
LEVER 1: Prompt Caching (E-01) — 90% on cached input
  Impact: ~$5-15/day savings (agent identity files cached)
  Effort: Config change only
  Status: NOT DEPLOYED

LEVER 2: Brain Idle Evaluation (H5) — 70% on idle heartbeats
  Impact: ~$7/day savings (7 of 10 agents idle most of time)
  Effort: 4-8 hours code
  Status: NOT BUILT

LEVER 3: LocalAI Routing (Stage 2-3) — 30-50% of operations
  Impact: ~$5-10/day savings (heartbeats + simple tasks on LocalAI)
  Effort: 20-40 hours code
  Status: DESIGNED

LEVER 4: Batch API (E-10) — 50% on async work
  Impact: ~$3-5/day savings (documentation, analysis tasks)
  Effort: API parameter change
  Status: NOT USED

LEVER 5: Smart Compaction (§35) — prevent rollover spikes
  Impact: Prevents 20% quota spikes on rate limit rollover
  Effort: 4-8 hours code
  Status: NOT BUILT

Combined projection:
  Today:       ~$30/day baseline (rate-limited, not dollar-limited)
  After Tier 1: ~$15-20/day (caching + brain eval)
  After Stage 2: ~$10-15/day (LocalAI routing)
  After Stage 5: ~$3-5/day (80% on LocalAI)
```

### 47.3 LocalAI Infrastructure Investment

```
Hardware: Already owned (8GB VRAM GPU, WSL2)
Models: Free to download (Qwen3.5, hermes, codellama)
Docker: Already running (LocalAI container)
Electricity: ~$5-10/month (GPU inference)

Investment: $0 hardware + time to integrate

ROI timeline:
  Time to Stage 2: ~40-80 hours of work
  Savings at Stage 2: ~$5-10/day
  Payback: Work time pays for itself in 1-2 months of savings

  But real value is RATE LIMIT RELIEF:
  LocalAI heartbeats don't consume Claude quota.
  10 agents × 20 heartbeats = 200 calls/day freed up.
  That quota goes to COMPLEX work instead.
```

### 47.4 Cost Per Task Type

```
Task Type           Backend        Est. Cost    Frequency    Daily Cost
─────────────────────────────────────────────────────────────────────────
Heartbeat (idle)    Claude opus    $0.05-0.10   200/day      $10-20
Heartbeat (idle)    LocalAI 3B    $0.00        200/day      $0
Heartbeat (idle)    Brain eval    $0.00        200/day      $0
Simple task         Claude sonnet  $0.50-1.00   3/day        $1.50-3
Simple task         LocalAI 9B    $0.00        3/day        $0
Complex task        Claude opus    $2.00-10.00  2/day        $4-20
Review              Claude opus    $1.00-3.00   3/day        $3-9
Contribution        Claude sonnet  $0.30-0.50   5/day        $1.50-2.50
Gate request        Direct         $0.00        1/day        $0

Current total (all Claude):          ~$20-55/day
Target (Stage 5):                    ~$4-20/day
```

---

## 48. PO Daily Workflow — How the PO Uses the Fleet

**What this section is:** The day-to-day interaction model for the PO.
What to check, when, how. Not abstract governance — practical workflow.

### 48.1 Morning Check (~5 minutes)

```
1. Check ntfy notifications (phone)
   → Any overnight escalations? Storm alerts? Gate requests?
   
2. Check IRC #fleet (The Lounge on port 9000)
   → Fleet activity summary. Who worked on what.
   → Any mode changes? Any errors?
   
3. Check Plane (sprint board)
   → Sprint progress. Task states.
   → Any tasks stuck? Any new issues from stakeholders?
   
4. Check OCMC (fleet_config)
   → Current settings: work_mode, cycle_phase, backend_mode, budget_mode
   → Rate limit status: 5h window %, 7d window %
   → Agents online: how many active?
```

### 48.2 Active Work Session

```
GATE REQUESTS (respond within hours, not days):
  → ntfy high priority: "GATE REQUEST: {task_title}"
  → Agent has plan at 90% readiness, wants PO confirmation
  → PO reads plan artifact → approves (readiness 99) or rejects

DIRECTIVE ISSUING:
  → PO posts directive to OCMC board memory
  → Tags: directive, to:{agent} or to:fleet, urgency
  → Brain picks up next cycle (≤30s), routes to agents
  → Example: "Focus on auth module this sprint"

SETTINGS CHANGES:
  → work_mode: "full-autonomous" ↔ "work-paused" ↔ "finish-current"
  → cycle_phase: "execution" ↔ "planning" ↔ "crisis-management"
  → backend_mode: "claude" ↔ "claude+localai"
  → budget_mode: "turbo" ↔ "economic" (tempo offset)
  
  Effect: Brain applies within 30s. Agents see in next heartbeat.

TASK CREATION:
  → Create task on Plane (sprint board)
  → OR create directly on OCMC
  → PM picks up in heartbeat, breaks down, assigns

REVIEW OVERRIDE:
  → Fleet-ops approved/rejected something PO disagrees with
  → PO overrides: approve the rejected, or reject the approved
  → PO feedback in task comments
```

### 48.3 Escalation Levels

```
LEVEL 0: Background (PO doesn't need to see)
  → Heartbeats, routine dispatches, stage progressions
  → Visible in IRC #fleet if PO wants to check

LEVEL 1: Informational (ntfy info priority)
  → Task completed, PR ready, task approved
  → PO reads at convenience

LEVEL 2: Action Needed (ntfy high priority)
  → Gate request (plan at 90%, needs PO confirmation)
  → Phase advancement request
  → Agent pause (blocker found)

LEVEL 3: Urgent (ntfy urgent priority)
  → Security alert
  → Escalation from agent
  → Storm WARNING or higher
  → Budget threshold (80%+ of weekly quota)

LEVEL 4: Critical (ntfy critical + IRC #alerts)
  → Storm CRITICAL (fleet frozen)
  → Rate limit exhaustion
  → Gateway duplication
  → Agent produced potentially harmful output
```

### 48.4 Weekly Cadence

```
WEEKLY REVIEW (~30 minutes):
  1. Sprint velocity: how many story points completed?
  2. Cost report: tokens used, Claude vs LocalAI split
  3. Quality report: rejections, rework, diseases detected
  4. Agent health: stuck agents, correction thresholds
  5. Backlog: what's ready for next sprint?

SPRINT BOUNDARY (every 2 weeks):
  1. Sprint review: what was accomplished?
  2. Sprint retrospective: what went wrong? Lessons?
  3. Sprint planning: prioritize backlog for next sprint
  4. Phase review: ready to advance delivery phase?
```

### 48.5 Emergency Procedures

```
FLEET IS STUCK:
  1. Check: work_mode on OCMC → is it "work-paused"?
  2. Check: storm status → CRITICAL blocks everything
  3. Check: rate limit → 90%+ pauses dispatch
  4. Check: agents → all SLEEPING/OFFLINE?
  5. Action: set work_mode to "full-autonomous", wait 30s

COST RUNAWAY:
  1. ntfy alert: budget threshold hit
  2. Action: set backend_mode to "localai" (if LocalAI ready)
  3. Action: set budget_mode to "economic" (slower tempo)
  4. Action: set work_mode to "finish-current" (no new tasks)
  5. Wait for rate limit window to roll over

AGENT PRODUCING BAD OUTPUT:
  1. Doctor detects disease → teaches or prunes
  2. If persistent: PO sets agent task to "work-paused"
  3. If critical: PO kills agent session via OCMC
  4. Brain creates fresh session on next heartbeat

GATEWAY DOWN:
  1. ntfy: no heartbeats (silence is the alert)
  2. Check: is openclaw-gateway process running?
  3. Action: make gateway (restart)
  4. Brain auto-re-enables CRONs when gateway recovers

MC DOWN:
  1. Brain detects: MC API unreachable
  2. Brain: disables all gateway CRONs (prevent agent errors)
  3. Agents: continue in-progress work but can't report
  4. Action: make mc-up (restart docker compose)
  5. Brain: re-enables CRONs, resumes cycle
```

---

## 49. Deployment Architecture — Services, Ports, Health

**What this section is:** The canonical deployment specification.
Every service, every port, every health check, every startup sequence.

### 49.1 Service Stack

```
┌──────────────────────────────────────────────────────────────┐
│                 DOCKER COMPOSE STACK                          │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐  │
│  │  PostgreSQL 16  │  │    Redis 7     │  │ Webhook Worker│  │
│  │  Port: 5433     │  │  Port: 6379    │  │ (RQ queue)    │  │
│  │  Health: 5s     │  │  Health: 5s    │  │ No port       │  │
│  └────────┬───────┘  └───────┬────────┘  └───────────────┘  │
│           │                  │                               │
│  ┌────────┴──────────────────┴─────────────────────────────┐ │
│  │              MC Backend (Django)                         │ │
│  │              Port: 8000                                  │ │
│  │              Auth: Bearer token (LOCAL_AUTH_TOKEN)        │ │
│  │              Health: /health                             │ │
│  └──────────────────────┬──────────────────────────────────┘ │
│                         │                                    │
│  ┌──────────────────────┴──────────────────────────────────┐ │
│  │              MC Frontend (Next.js)                       │ │
│  │              Port: 3000                                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              The Lounge (IRC Web UI)                     │ │
│  │              Port: 9000                                  │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                 HOST PROCESSES (not Docker)                    │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │         OpenClaw Gateway                                 │ │
│  │         HTTP: 9400  |  WS: 18789                        │ │
│  │         Auth: ~/.openclaw/openclaw.json token            │ │
│  │         Manages: agent Claude Code sessions              │ │
│  │         CRONs: per-agent heartbeat schedules             │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │         Orchestrator (Brain)                             │ │
│  │         No port (background loop)                        │ │
│  │         Cycle: scales with budget mode (5-60s)            │ │
│  │         python -m fleet orchestrator                     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────────┐ │
│  │  Sync Daemon  │  │ Monitor Daemon│  │  miniircd       │ │
│  │  (60s loop)   │  │  (300s loop)  │  │  Port: 6667     │ │
│  └───────────────┘  └───────────────┘  └─────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                 EXTERNAL SERVICES                             │
│                                                              │
│  LocalAI ──── Port: 8090 (AICP docker-compose)               │
│  Plane ────── Port: 8080 (DSPD self-hosted)                  │
│  ntfy ─────── Port: 10222 (192.168.40.11, external)          │
│  GitHub ───── gh CLI (authenticated)                          │
│  LightRAG ─── Port: 9621 (PLANNED, not deployed)             │
└──────────────────────────────────────────────────────────────┘
```

### 49.2 Port Map

```
Port    Service              Protocol    Auth
─────────────────────────────────────────────────────
3000    MC Frontend          HTTP        None (proxies to 8000)
5433    PostgreSQL           TCP         Password (postgres)
6379    Redis                TCP         None (127.0.0.1 only)
6667    miniircd             IRC         Channel-based
8000    MC Backend           REST        Bearer token
8080    Plane                HTTP        API key
8090    LocalAI              REST        None (OpenAI-compat)
9000    The Lounge           HTTP        Web login
9400    Gateway HTTP         HTTP        Token
9621    LightRAG (planned)   HTTP        JWT + API key
10222   ntfy                 HTTP        Topic-based
18789   Gateway WebSocket    WS          Token (JSON-RPC v3)
```

### 49.3 Startup Sequence

```
ORDER MATTERS — dependencies must be healthy first:

1. docker compose up -d          (db, redis, backend, frontend, lounge)
   Wait: db health check (pg_isready) + redis health check (ping)
   Wait: backend starts (depends on db + redis)

2. make gateway                  (openclaw gateway on host)
   Wait: WS port 18789 accepting connections

3. bash scripts/register-agents.sh   (register 10 agents in gateway)

4. bash scripts/provision-agents.sh  (sync agent templates → gateway)

5. make irc-up                   (miniircd, if not using Docker IRC)

6. bash scripts/verify-communications.sh  (test all systems)

7. make sync-start               (sync daemon, 60s loop)
   make monitor-start            (monitor daemon, 300s loop)

8. python -m fleet orchestrator  (brain, 30s loop)
   This is the last thing — everything must be healthy first.
```

### 49.4 Health Checks

```
Service          Check                           Interval  Threshold
──────────────────────────────────────────────────────────────────────
PostgreSQL       pg_isready                      5s        3 retries
Redis            redis-cli ping → PONG           5s        3 retries
MC Backend       GET /health → 200               30s       in brain
Gateway          WS connect → auth → ok          30s       in brain
LocalAI          GET /v1/models → 200            300s      in router
Plane            GET /api/v1/workspaces → 200    300s      in sync
ntfy             POST /test → 200                —         best effort

Brain handles outages:
  MC down → disable all gateway CRONs, wait for recovery
  Gateway down → log error, retry next cycle
  LocalAI down → route all to Claude (fallback)
  Plane down → skip Plane sync, continue without
  ntfy down → log warning, continue without (graceful)
```

### 49.5 Data Persistence

```
Volume                     What                    Backup?
──────────────────────────────────────────────────────────────
postgres_data              Tasks, agents, approvals  YES
redis_data                 Session cache            NO (rebuild)
agents/*/context/          Agent context files      NO (generated)
state/dispatch_records/    Dispatch intent records  YES
~/.openclaw/               Gateway config, auth     YES
config/                    Fleet configuration      GIT (committed)
.env                       Secrets                  NO (manual)
```

---

## 50. Crisis Response Playbook — Failure Modes & Recovery

**What this section is:** What to do when things break. Not theory —
practical runbook for each failure mode.

### 50.1 Budget / Rate Limit Crisis

```
TRIGGER: Rate limit usage hits 90%+ (5-hour or 7-day window)

INDICATORS:
  ntfy: "Budget threshold: 90% of 5-hour window"
  Statusline: rate limit bar turns RED
  IRC #alerts: budget warning

IMMEDIATE RESPONSE (PO):
  1. Set backend_mode to "localai" (if LocalAI operational)
     → All new dispatches route to LocalAI
  2. Set budget_mode to "economic" (slower tempo)
     → Heartbeat frequency drops, dispatch cycle slower
  3. Set work_mode to "finish-current" (if severe)
     → No new tasks, finish what's in progress

BRAIN RESPONSE (automatic):
  1. budget_monitor.check_quota() → returns NOT SAFE
  2. Dispatch paused (no new task dispatch)
  3. In-progress agents continue (already committed)
  4. Storm indicator "fast_climb" may fire → escalation
  5. Session manager force-compacts heavy contexts (if built)

RECOVERY:
  1. Wait for rate limit window to roll over (5-hour cycle)
  2. Brain auto-detects: quota safe again
  3. Dispatch resumes
  4. PO restores settings to normal

PREVENTION:
  - Prompt caching (90% savings on repeated prefixes)
  - Brain idle evaluation (70% savings on idle heartbeats)
  - Smart compaction before rollover (no 20% spike)
  - Stagger agent compactions near rollover
```

### 50.2 Mission Control Down

```
TRIGGER: MC API unreachable

INDICATORS:
  Brain log: "MC API error: connection refused"
  No new dispatches, no task updates
  Agents continue in-progress work but can't report

BRAIN RESPONSE (automatic):
  1. _outage.record_failure("mc_api", error)
  2. disable_gateway_cron_jobs() → all heartbeats paused
     → Prevents agents from erroring on MC calls
  3. Brain enters backoff loop (retry every 30s with exponential backoff)

RECOVERY:
  1. PO: make mc-up (restart docker compose)
  2. Wait: db health check → backend starts
  3. Brain detects MC responsive again
  4. enable_gateway_cron_jobs() → heartbeats resume
  5. check_cron_circuit_breaker() → reset error counts
  6. Normal operation resumes

DATA RISK: NONE — agents' in-progress work is in git.
  Commits, PRs exist independently of MC.
  MC state rebuilds from task/approval data (persisted in Postgres).
```

### 50.3 Gateway Down

```
TRIGGER: Gateway process crashes or is killed

INDICATORS:
  No heartbeats firing (silence is the alert)
  Brain: inject_content fails → log error
  ntfy: no notifications (agents can't complete)

RESPONSE:
  1. PO: make gateway (restart gateway process)
  2. Gateway reads config, resumes CRONs
  3. Agents re-attach to existing sessions
  4. Brain detects gateway responsive → resumes operations

DATA RISK: LOW — agent sessions may be lost.
  If sessions survive: agent continues where it left off.
  If sessions lost: brain creates fresh sessions, agents restart.
  Git work survives (commits are in repo, not session).
```

### 50.4 Agent Producing Bad Output

```
TRIGGER: Agent commits code that breaks tests, introduces bugs, etc.

DETECTION:
  1. fleet_task_complete runs tests → tests FAIL
  2. Challenge engine detects quality issues (if wired)
  3. Fleet-ops review catches problems (7-step review)
  4. Doctor detects disease patterns

RESPONSE ESCALATION:
  Level 1 — TEACHING:
    Doctor adapts lesson → injects into agent session
    Agent gets specific feedback: "you did X, requirement says Y"
    Agent corrects and re-submits

  Level 2 — FORCE COMPACT:
    Context may be contaminated → strip and lean
    Agent continues with fresh context summary
    Often fixes: context contamination, scope creep

  Level 3 — PRUNE AND REGROW:
    Kill agent session entirely
    Fresh session created on next heartbeat
    Agent starts clean with full onion context
    Task stays IN_PROGRESS → agent re-receives

  Level 4 — PO INTERVENTION:
    3+ corrections = doctor triggers PRUNE
    If still failing: PO reassigns task to different agent
    Or PO manually intervenes with specific direction

PREVENTION:
  Autocomplete chain engineering (correct behavior is natural)
  Contribution requirements (architect/QA input before work)
  Stage gating (can't skip methodology)
  Anti-corruption rules (10 rules in CLAUDE.md)
```

### 50.5 Storm Escalation

```
See §32.1 for full storm cascade.

QUICK REFERENCE:
  WATCH (1 indicator):    Log only, no action needed
  WARNING (2+ indicators): max_dispatch=1, PO monitors
  STORM (3+ indicators):   dispatch=0, PO notified
  CRITICAL (fast_climb+burst): fleet FROZEN, PO must act

PO RESPONSE TO CRITICAL:
  1. Read diagnostic snapshot (in board memory)
  2. Identify root cause (gateway dup? budget drain? agent thrash?)
  3. Fix root cause (kill dup gateway, pause fleet, etc.)
  4. Wait for indicators to clear (10-30 min de-escalation)
  5. Normal operation resumes automatically
```

---

## 51. Cross-Project Integration — AICP ↔ Fleet ↔ DSPD ↔ NNRT

**What this section is:** How the four projects connect and feed each other.

### 51.1 The Four Projects

```
AICP (devops-expert-local-ai):
  AI Control Platform — backends, modes, guardrails, LocalAI independence
  Owns: router.py, rag.py, kb.py, LocalAI management, GPU strategy
  Provides to Fleet: LocalAI inference, RAG, embedding, reranking

Fleet (openclaw-fleet):
  10 autonomous AI agents via OpenClaw + Mission Control
  Owns: orchestrator, MCP tools, agent lifecycle, methodology
  Consumes from AICP: LocalAI routing, RAG knowledge
  Consumes from DSPD: Sprint plans, issue tracking via Plane

DSPD (devops-solution-product-development):
  Project management via self-hosted Plane
  Owns: Plane instance, sprint planning, issue tracking
  Provides to Fleet: issues → tasks, sprint structure
  Consumes from Fleet: completed work, PRs, status updates

NNRT (Narrative-to-Neutral-Report-Transformer):
  Report transformation NLP pipeline
  Consumes from Fleet: implementation work (if fleet implements features)
  Independent: has own pipeline, mostly standalone
```

### 51.2 Integration Points

```
DSPD → Fleet (Plane → OCMC):
  PO creates issues on Plane (DSPD project)
  PM heartbeats → plane_sync.py → ingest issues
  PM converts to OCMC tasks with full custom fields
  Fleet works → completes → Plane issue updated
  Bidirectional: higher readiness wins on sync

AICP → Fleet (LocalAI → dispatch):
  Fleet router calls LocalAI for simple tasks
  AICP rag.py provides knowledge queries
  AICP kb.py provides document ingestion
  AICP embedding (bge-m3) shared with fleet + LightRAG
  ⚠️ NOT WIRED: router_unification.py is schema only

Fleet → GitHub (PRs, branches):
  Agents commit to project repos
  fleet_task_complete creates PRs
  Fleet-ops reviews PRs on GitHub
  Brain syncs PR status back to OCMC tasks

Fleet → DSPD (status → Plane):
  Task completion → Plane issue state updated
  Sprint progress → Plane cycle progress
  Comments → Plane issue comments
  Bidirectional via plane_sync.py
```

### 51.3 What's Not Connected

```
AICP RAG → Fleet agents:
  rag.py + kb.py exist in AICP but not accessible from fleet
  Fleet agents can't query project knowledge
  Fix: MCP server wrapping AICP kb.py, or LightRAG (§46)

AICP Router → Fleet Router:
  router_unification.py is schema only
  AICP routes Think/Edit/Act modes
  Fleet routes by task complexity + backend_mode
  No bridge between them

NNRT → Fleet:
  No integration currently
  NNRT could be a project the fleet works on
  Would need: project registration + repo access

Cross-project cost attribution:
  When fleet works on AICP code, who pays?
  No mechanism to track cost per project
  Fix: project field on DispatchRecord + LaborStamp
```

### 51.4 LightRAG as Cross-Project Knowledge Mesh

```
With LightRAG deployed (§46):

  All 4 projects → LightRAG ingestion:
    AICP: architecture docs, router design, LocalAI research
    Fleet: system docs, design specs, agent decisions
    DSPD: sprint plans, PM artifacts, issue history
    NNRT: pipeline docs, transformation rules

  One knowledge graph spanning ALL projects:
    "How does AICP router relate to Fleet router?"
    "What did we decide about auth middleware across projects?"
    "What Plane issues are blocked by LocalAI readiness?"

  PO sees: mesh of everything, not isolated project silos
```

---

## 52. Sprint & PM Workflow with Plane

**What this section is:** How the PM agent runs sprints using Plane,
and how the PO interacts with sprint planning.

### 52.1 Sprint Structure

```
Sprint duration: 2 weeks (configurable in config/fleet.yaml)
Sprint planning: PO + PM agent
Sprint board: Plane (DSPD project)
Sprint execution: Fleet agents via OCMC tasks
Sprint review: PO reviews velocity + quality

Sprint lifecycle:
  1. PLANNING (1 session):
     PO prioritizes Plane backlog
     PM breaks issues into agent-sized tasks
     PM assigns story points (SP)
     PM sets delivery phase for each task

  2. EXECUTION (2 weeks):
     PM heartbeats → monitors sprint progress
     Brain dispatches tasks per priority + readiness
     Agents work through stages → complete → review
     PM tracks: velocity (SP/day), blocked count, completion rate

  3. REVIEW (1 session):
     PM generates sprint report (velocity, completed, carried over)
     PO reviews: did we hit goals?
     What was the quality? How many rejections?
     What was the cost? (from labor stamps)

  4. RETROSPECTIVE (1 session):
     What went well? (agent performance, methodology)
     What went wrong? (diseases, stuck agents, scope creep)
     What to improve? (brain rules, agent CLAUDE.md, process)
```

### 52.2 Plane ↔ OCMC Sync

```
Plane issue → OCMC task:
  plane_sync.py:ingest_from_plane()
  PM filters: not all Plane issues become tasks
  PM adds: requirement_verbatim, acceptance_criteria, agent assignment
  Readiness, stage, phase synced bidirectionally (higher wins)

OCMC task → Plane issue:
  fleet_task_complete → plane_sync.update_issue(state="In Review")
  fleet_approve → plane_sync.update_issue(state="Done")
  Comments → Plane comments (with labor attribution)
  Labels → readiness:%, stage:name

Sprint progress tracking:
  PM heartbeat queries: fleet_plane_sprint()
  Returns: sprint velocity, completed SPs, remaining
  PM posts digest to IRC #fleet + board memory
```

### 52.3 Velocity & Metrics

```
Story points completed per sprint
  Target: PO sets velocity target
  Actual: from completed tasks with SP field
  Trend: sprint-over-sprint comparison

Quality metrics per sprint:
  Rejection rate: fleet-ops rejections / total reviews
  Rework rate: tasks with iteration > 1
  Disease rate: doctor detections / total tasks
  Trail completeness: % of tasks with complete audit trail

Cost metrics per sprint:
  Total tokens consumed
  Claude vs LocalAI split
  Cost per story point
  Cost per agent
```

---

## 53. Agent Permissions & Data Isolation

**What this section is:** What each agent can and cannot do.
Security model, credential scoping, data access rules.

### 53.1 Gateway Permissions

```
All agents run with: --permission-mode bypassPermissions
  This gives agents full filesystem + command access.
  Gateway manages isolation through WORKSPACES, not permissions.

Each agent has:
  Own workspace directory: agents/{name}/
  Own Claude Code session: session_key from MC
  Own MCP server instance: python -m fleet.mcp.server
  Own context files: context/fleet-context.md, task-context.md

Agents CANNOT:
  Access other agents' workspaces (filesystem isolation)
  Call other agents' MCP tools (session isolation)
  Read other agents' context files (directory isolation)
  Modify gateway configuration (operator-only RPC)
```

### 53.2 MCP Tool Access by Role

```
All agents:
  fleet_read_context, fleet_chat, fleet_alert, fleet_pause,
  fleet_escalate, fleet_notify_human, fleet_agent_status,
  fleet_heartbeat_context, fleet_task_context

Workers (architect, engineer, devops, qa, writer, ux):
  + fleet_task_accept, fleet_task_progress
  + fleet_commit (stages 2-5 when bug B-01 fixed)
  + fleet_task_complete (work stage only)
  + fleet_artifact_read, fleet_artifact_update, fleet_artifact_create

PM only:
  + fleet_task_create (create/assign tasks)
  + fleet_gate_request (request PO gates)
  + fleet_plane_* (all 7 Plane tools)

Fleet-ops only:
  + fleet_approve (approve/reject reviews)

Accountability only:
  + fleet_artifact_create (compliance reports)

Contributors (architect, qa, devsecops, writer, ux):
  + fleet_contribute (post contribution to parent task)

Any agent:
  + fleet_request_input (ask colleague for help)
```

### 53.3 Credential Scoping

```
Credential          Who Has It            Why
──────────────────────────────────────────────────────────────
MC API token        All agents            Read/write tasks, memory
GitHub (gh CLI)     architect, engineer,   Create PRs, push branches
                    devops, devsecops,
                    fleet-ops, PM, writer
Plane API key       PM, writer            Sprint planning, issue mgmt
ntfy topics         All agents (via MCP)  Notifications (mediated by tools)
Gateway token       Brain only            Inject/prune/compact (operator)

Agents do NOT have:
  Direct gateway WebSocket access (brain mediates)
  Direct database access (MC API mediates)
  Direct Plane access except PM/writer (MCP mediates)
  Access to .env or secrets
```

### 53.4 Data Access

```
WHO SEES WHAT:

All agents see:
  Fleet state (work_mode, cycle_phase, backend_mode)
  PO directives (from board memory)
  Messages mentioning them (@mentions)
  Their assigned tasks (FULL detail)

Role-specific data:
  PM sees:         unassigned tasks, sprint data, all agents' status
  Fleet-ops sees:  pending approvals, review queue, offline agents
  Architect sees:  tasks needing design review
  DevSecOps sees:  security alerts, PR diffs for security review
  Workers see:     their tasks, their contributions, their artifacts

Agents do NOT see:
  Other agents' in-progress work (isolation)
  Other agents' session context
  Budget/cost details (only brain tracks this)
  Gateway configuration
  Database directly
```

---

## 54. Model Management & GPU Strategy

**What this section is:** How models are selected, loaded, swapped,
and managed on 8GB VRAM with single-active backend constraint.

### 54.1 Current Models

```
Model            Config          Size     Cold Start  Warm    GPU Layers  Use Case
──────────────────────────────────────────────────────────────────────────────────
hermes (7B)      hermes.yaml     4.4GB    ~80s        ~1s     24          Complex reasoning
hermes-3b (3B)   hermes-3b.yaml  2.0GB    ~10s        ~1.2s   32          Fleet heartbeats
codellama (7B)   codellama.yaml  4.4GB    ~80s        ~1s     GPU         Code tasks
phi-2 (2.7B)     phi-2.yaml      1.6GB    fast        fast    0 (CPU)     Fallback
bge-reranker     bge-reranker.yaml  —     —           —       CPU         Search reranking

Planned (Qwen3.5):
  Qwen3.5-4B:    ~2.5GB Q4_K_M   ~15s    —           32      Replace hermes-3b
  Qwen3.5-9B:    ~5GB Q4_K_M     ~40s    —           GPU     Primary workhorse

Future (TurboQuant, Q3 2026):
  Qwen3.5-9B + TQ4 KV:  48-64K context on 8GB (3.8x improvement)
  Qwen3.5-9B + TQ3 KV:  64-96K context on 8GB (4.9x improvement)
```

### 54.2 Single-Active Backend Constraint

```
LOCALAI_SINGLE_ACTIVE_BACKEND=true
Only ONE GPU model loaded at a time (8GB VRAM limit).

Model swap = cold start:
  Unload current model → free VRAM → load new model
  3B model: ~10s cold start
  7B model: ~80s cold start
  9B model: ~40s cold start (estimated)

Watchdog: auto-recover stuck backends
  LOCALAI_WATCHDOG_IDLE=true (15m timeout)
  LOCALAI_WATCHDOG_BUSY=true (5m timeout)

CPU models (no swap needed):
  bge-m3 embeddings: runs on CPU simultaneously with GPU model
  bge-reranker: runs on CPU simultaneously
  phi-2: CPU fallback (no GPU needed)
  
  → Embeddings and reranking are ALWAYS available (zero GPU cost)
  → This is why LightRAG can use LocalAI for embeddings
```

---

## 63. The 10 Agent Roles — Deep Dives

> "every role are top tier expert of their profession"

**What this section is:** Each agent is a TOP-TIER professional — not
a chatbot with a role label. Full characterization in fleet-elevation/
05-14 (200-400 lines each). Per-agent IDENTITY.md, SOUL.md, and
CLAUDE.md will implement these characterizations.

Every agent shares: 10 anti-corruption rules (§73), top-tier expert
expectations (§40), contribution awareness (§83), backward/forward
planning (§78), LaborStamp signatures (§44), trail recording (§38),
immune system observation (§73 — they don't know about the doctor).

### 63.1 Project Manager (PM)

```
Mission:   Top-tier Scrum Master who ORCHESTRATES the fleet's work.
           The conductor between PO's vision and execution.
           If PM doesn't act, nothing moves.

Responsibilities:
  - Sprint planning, velocity tracking, risk assessment
  - Filter noise from signal → PO gets focused decisions
  - Orchestrate who contributes what and when
  - Triage unassigned tasks, blockers, unclear requirements
  - Escalate decisions beyond scope to PO

Primary tools: fleet_task_create, fleet_chat, fleet_gate_request,
               fleet_escalate, fleet_agent_status, fleet_plane_*
Stage behavior: PM doesn't implement — manages process
Contribution: receives status_update from all agents
Wake triggers: unassigned inbox tasks, sprint boundary

Unique: Strategic glue — ORCHESTRATES (not dispatches). Prevents
        blockers and unassigned work from going unaddressed.
```

### 63.2 Fleet-Ops / Board Lead

```
Mission:   Top-tier operations lead and quality guardian.
           Owns reviews, approvals, methodology compliance, fleet health.
           The visible arm of the immune system.

Responsibilities:
  - 7-step REAL review (§31) — never rubber-stamp
  - Read actual work, compare to verbatim requirement
  - Verify trail is complete, contributions addressed
  - Approval processing (core job)
  - Fleet health monitoring and escalation

Primary tools: fleet_approve, fleet_alert, fleet_chat,
               fleet_escalate, fleet_agent_status
Stage behavior: reviews only — doesn't implement
Review SLA: approval in <30 seconds = disease detection
Wake triggers: pending approvals, review queue

Unique: Quality guardian — doesn't approve quickly, VERIFIES against
        exact requirements and standards. Doctor detects rubber-stamping.
```

### 63.3 Architect

```
Mission:   Design authority — owns design decisions, complexity
           assessment, architecture health. Shapes HOW everything
           gets built. Without architecture first, engineers err.

Responsibilities:
  - Deep pattern knowledge (WHEN and WHY, not just WHAT)
  - SRP, Domain-Driven Design, Onion Architecture
  - Research frameworks/SDKs/libraries before recommending
  - Validate choices against real-world constraints
  - Impose and enforce standards on fleet's work
  - Know when to evolve, refactor, change, remove

Primary tools: fleet_read_context, fleet_task_accept, fleet_commit,
               fleet_artifact_create (design_input), fleet_contribute
Stage behavior: produces design_input contributions in REASONING
Contribution: design_input to engineers, devops, QA
Wake triggers: tasks needing design review

Unique: DESIGN AUTHORITY — prevents engineers from building poorly
        by ensuring architecture decisions are validated FIRST.
```

### 63.4 DevSecOps (Cyberpunk-Zero)

```
Mission:   Security at EVERY phase — a LAYER that runs alongside
           everything. Provides requirements BEFORE, reviews DURING,
           validates AFTER. Not a checkpoint — a continuous presence.

Responsibilities:
  - Security contributions BEFORE implementation (core NEW job)
  - Assess security implications (auth, data, external calls, deps)
  - Provide security requirements (MUST/MUST NOT/needs review)
  - Crisis phase: triage, assess, mitigate, report
  - One of two crisis-active agents (with fleet-ops)

Primary tools: fleet_read_context, fleet_commit, fleet_task_complete,
               fleet_alert, fleet_contribute (security_requirement)
Stage behavior: contributes security_req during REASONING of others' tasks
Contribution: security_requirement to engineers, devops
Wake triggers: security alerts, PRs needing security review

Unique: Security is a LAYER not a checkpoint — participates
        throughout lifecycle, not just at the end.
```

### 63.5 Software Engineer

```
Mission:   Modeled after PO: senior DevOps software engineer with
           network background, evolved to architect and fullstack.
           Loves AGILE/SCRUM. Respects the process.

Responsibilities:
  - Implement with high standards and process respect
  - Clear chain entries, ins/outs, groups of operations
  - TDD with high critical level tests, pessimistic assertions
  - Understand design patterns and when to apply them
  - Follow plan, reference contributions, stay in scope

Primary tools: fleet_read_context, fleet_task_accept, fleet_commit,
               fleet_task_complete, fleet_request_input
Stage behavior: full 5-stage methodology (conversation→work)
Contribution: receives design_input + qa_test_def + security_req
Skills: feature-implement, refactor-extract, /debug

Unique: Top-tier professional who operates with discipline,
        respects process, understands architecture and UX impact.
```

### 63.6 DevOps Engineer

```
Mission:   Own infrastructure, CI/CD, deployment, operational maturity.
           As delivery phases advance, DevOps ensures infrastructure
           matures alongside code.

Responsibilities:
  - Infrastructure tasks through all stages
  - CI/CD pipeline development and maintenance
  - Deployment strategy and execution
  - Infrastructure maturity matching delivery phase
  - Fleet's own infrastructure: LocalAI, Docker, MC, gateway
  - Monitoring, alerting, operational readiness

Primary tools: fleet_read_context, fleet_commit, fleet_task_complete,
               fleet_artifact_update, fleet_contribute
MCP servers: fleet, filesystem, github, docker
Skills: foundation-docker, foundation-ci, ops-deploy, ops-maintenance

Unique: Infrastructure scales with maturity — POC deploys manually,
        production has full CI/CD, monitoring, alerts.
```

### 63.7 QA Engineer

```
Mission:   Top-tier QA with TDD discipline, boundary value analysis,
           equivalence partitioning, pessimistic mindset. Assumes
           things WILL go wrong. Writes tests that catch REAL defects.

Responsibilities:
  - Test PREDEFINITION (core NEW job) — define tests BEFORE implementation
  - Contribute qa_test_definition during REASONING of others' tasks
  - When task reaches review, QA already has criteria defined
  - Validate against what THEY specified, not what they discover
  - Phase-appropriate rigor (POC vs production testing differs)

Primary tools: fleet_read_context, fleet_commit, fleet_task_complete,
               fleet_contribute (qa_test_definition), fleet_artifact_create
MCP servers: fleet, filesystem, playwright
Skills: quality-coverage, quality-audit, foundation-testing

Unique: QA contributes BEFORE implementation — test criteria become
        requirements the implementing agent MUST satisfy.
```

### 63.8 Technical Writer

```
Mission:   Documentation as a LIVING SYSTEM — alongside code, not after.
           In full-autonomous mode, CONTINUOUSLY working: scanning for
           missing docs, updating stale pages, creating new docs.

Responsibilities:
  - Plane page maintenance (core autonomous job)
  - Scan completed tasks for missing documentation
  - Scan existing pages for staleness
  - Update stale pages with current information
  - Create new pages for new features/systems
  - Complementary work with architect, UX, engineers

Primary tools: fleet_read_context, fleet_task_accept, fleet_commit,
               fleet_artifact_create, fleet_plane_*
MCP servers: fleet, filesystem, github
Skills: feature-document, pm-changelog, pm-handoff

Unique: Documentation is LIVING — updated in parallel with code.
        Continuous work in autonomous mode, not waiting for tasks.
```

### 63.9 UX Designer

```
Mission:   UX at EVERY level — not just UI. Core, module, CLI, AST,
           API responses, error messages, logs, config structure,
           event formatting, notifications. Every interface has UX.

Responsibilities:
  - Provide component patterns, interaction flows, guidelines BEFORE build
  - Contribute to ANY task touching user-facing elements:
    Web UI, CLI, API, Config, Events, Notifications, Logs, AST/Code
  - Accessibility expertise
  - Phase-appropriate UX (POC vs production rigor differs)

Primary tools: fleet_read_context, fleet_task_accept,
               fleet_artifact_create (ux_spec), fleet_contribute
MCP servers: fleet, filesystem, playwright
Skills: quality-accessibility

Unique: UX is EVERYWHERE — participates in infrastructure, API,
        CLI, config, logging design. Not just "make it pretty."
```

### 63.10 Accountability Generator

```
Mission:   Fleet's conscience — verifies process was followed,
           trails are complete, governance requirements met.
           Compliance, governance, audit trails.

Responsibilities:
  - Trail verification (core job):
    Did task go through all required stages?
    Were stage transitions authorized (PM/PO)?
    Were required contributions received?
    Was PO gate at 90% readiness approved?
  - Process adherence verification
  - General review, simulation, diagram validation
  - Compliance report artifact generation

Primary tools: fleet_read_context, fleet_chat, fleet_alert,
               fleet_artifact_create (compliance_report)
MCP servers: fleet, filesystem
Skills: quality-audit

Unique: Verifies PROCESS ADHERENCE (was methodology followed,
        gates respected), NOT work quality or enforcement.
```

---

## 64. Artifact Type Catalog — Complete Schema

**What this section is:** Every artifact type, required fields, rendering,
who produces it, who consumes it.

### 64.1 Artifact Types (8 implemented + 5 designed)

```
IMPLEMENTED (have renderers in transpose.py):
  1. task                — task ready for work
  2. bug                 — bug report with reproduction steps
  3. analysis_document   — analysis of current state
  4. investigation_document — research findings and options
  5. plan                — implementation plan
  6. progress_update     — work progress tracking
  7. pull_request        — PR ready for review
  8. completion_claim    — agent claiming task is done

DESIGNED (no renderers yet):
  9. security_assessment  — security review findings
  10. qa_test_definition  — test criteria BEFORE implementation
  11. ux_spec             — UX guidelines and patterns
  12. documentation_outline — doc structure plan
  13. compliance_report   — audit trail verification
```

### 64.2 Key Artifact Schemas

```
PLAN (most critical — gates dispatch):
  Required:
    title:                    What's being planned
    requirement_reference:    Verbatim quoted (SACROSANCT)
    approach:                 What will be done (specific files, components)
    target_files:             Exactly which files modified/created [array]
    steps:                    Ordered implementation steps [array]
    acceptance_criteria_mapping: {criterion → how it will be met}
  Optional:
    risks:                    What could go wrong

  Validated by: plan_quality.py:assess_plan()
    score 0-100: concrete steps (40%), verification (30%),
    risk awareness (20%), length (10%)
    Acceptable: ≥ 40. Good: ≥ 70.

ANALYSIS_DOCUMENT:
  Required:
    title, scope, current_state, findings [array], implications
  Finding object: {title, finding, files [array], implications}

INVESTIGATION_DOCUMENT:
  Required:
    title, scope, findings
  Optional:
    options [{name, pros, cons}], recommendations, open_questions, sources

BUG:
  Required:
    title, steps_to_reproduce, expected_behavior,
    actual_behavior, environment, impact
  Optional: evidence

COMPLETION_CLAIM:
  Required:
    pr_url, summary, files_changed,
    acceptance_criteria_check [{criterion, met (bool), evidence}]

QA_TEST_DEFINITION (designed, no renderer):
  Required:
    test_criteria [{id (TC-001), description, type, priority}],
    target_task_reference, delivery_phase, verification_method

SECURITY_ASSESSMENT (designed, no renderer):
  Required:
    threat_assessment, requirements_list,
    restrictions_list, review_checklist
```

### 64.3 Artifact Flow

```
Producer → Artifact Type → Consumer

architect    → analysis_document      → engineer (context)
architect    → investigation_document  → PM (decision input)
architect    → plan                    → engineer (work guide)
architect    → design_input (contrib)  → engineer (contribution)
engineer     → completion_claim        → fleet-ops (review)
engineer     → pull_request            → fleet-ops (review)
qa           → qa_test_definition      → engineer (contribution)
devsecops    → security_assessment     → engineer (contribution)
ux           → ux_spec                 → engineer (contribution)
writer       → documentation_outline   → PM (tracking)
accountability → compliance_report     → PO (governance)
PM           → plan                    → fleet (sprint plan)

Transpose layer converts: structured object ↔ rich HTML
  → Agents work with structured objects (JSON-like)
  → Plane displays rich HTML
  → Bidirectional: agent can read from Plane HTML back to object
```

---

## 65. Git Workflow & Branch Strategy

**What this section is:** How agents use git — branching, commits,
worktrees, PRs, conflict resolution.

### 65.1 Branch Naming

```
Pattern: task-{short_id}-{description}
Example: task-a1b2-add-auth-middleware

Created by: dispatch.py when setting up worktree
Agent works on: this branch exclusively
PR target: main (or configured base branch)
```

### 65.2 Conventional Commits

```
Format: type(scope): description [task:short_id]

Types:
  feat     New feature
  fix      Bug fix
  docs     Documentation
  test     Tests
  refactor Refactoring
  chore    Maintenance
  style    Formatting

Examples:
  feat(auth): add JWT middleware [task:a1b2]
  fix(router): handle null backend_mode [task:c3d4]
  test(doctor): add laziness detection tests [task:e5f6]
  docs(api): update authentication guide [task:g7h8]

Enforced by: fleet_commit tool (MCP)
Generated by: agent following CLAUDE.md rules
Verified by: fleet-ops review Step 4 (trail check)
```

### 65.3 Worktree Management

```
Each dispatched task gets a git worktree:
  projects/{project}/worktrees/{agent}-{task_short}/

Created by: dispatch.py:_setup_worktree()
Contains: full project clone at branch
Isolated: agent can't affect other agents' work
Cleaned up: after task completion + PR merge

Benefits:
  - Multiple agents work on same project simultaneously
  - No git conflicts during work (separate branches)
  - Agent has full project context (all files available)
  - Worktree path stored in task custom_fields.worktree
```

### 65.4 PR Flow

```
Agent calls fleet_task_complete:
  1. git push origin {branch}
  2. gh pr create --title "{title}" --body "{body}"
  3. PR body includes: summary, changes, test results,
     labor attribution, task reference
  4. PR created → URL stored in task custom_fields.pr_url

Fleet-ops reviews:
  1. Reads PR diff (Step 2 of 7-step review)
  2. Checks conventional commit format (Step 4)
  3. Verifies no scope creep (Step 5)
  4. Approves/rejects with reasoning

After approval:
  1. PR merged (by fleet-ops or automatically)
  2. fleet-sync.sh detects merge → updates task status
  3. Worktree cleaned up
  4. Branch optionally deleted
```

### 65.5 Multi-Agent Conflict Prevention

```
Each agent has own worktree → own branch → no conflicts during work.

Conflict scenarios:
  1. Two agents modify same file (different tasks)
     → Each on different branch
     → Conflict appears at PR merge time
     → Fleet-ops detects → routes back to PM for resolution
     → PM reassigns or coordinates

  2. Agent A depends on Agent B's changes
     → Dependency tracked via depends_on custom field
     → Brain won't dispatch A until B's task is DONE
     → A starts from B's merged branch
```

---

## 66. Claude Code Feature Strategy — Agent Usage Patterns

**What this section is:** How agents should use Claude Code's built-in
features — extended thinking, effort levels, /plan, /compact, /model.

### 66.1 Model & Context Selection

```
Per gateway session configuration:
  Model:   claude-opus-4-6[1m] (default for all agents)
  Context: 1M tokens (maximum available on Max 5X)

Per-task override (via model_selection.py):
  Complex/critical → opus (always)
  Standard work → sonnet (lower cost)
  Security/architecture → opus (never compromise)

Context size consideration:
  1M context = more capability per turn BUT faster quota drain
  200K context = cheaper per turn BUT less information available
  Decision: brain tracks context pressure → may dispatch with
  smaller context near rate limit rollover
```

### 66.2 Effort Levels

```
model_selection.py selects effort based on task complexity:
  low:    simple tasks (SP 1-2, docs, chore)
  medium: standard tasks (SP 3-5, stories)
  high:   complex tasks (SP 8+, epics, blockers)
  max:    critical tasks (security, architecture decisions)

Effort affects:
  - Token budget per response
  - Number of tool call iterations allowed
  - Depth of reasoning before acting
```

### 66.3 /plan Mode Usage

```
WHEN to use /plan:
  - Before complex implementation (engineer, SP ≥ 5)
  - Before architecture design (architect)
  - Before sprint planning (PM)
  - Before security analysis (devsecops)
  - When multiple approaches exist and need evaluation

WHEN NOT to use /plan:
  - Heartbeat checks (just read context, respond)
  - Simple tasks (SP 1-2, clear requirements)
  - Contributions (focused, single-purpose input)

Agent training needed:
  CLAUDE.md should include: "Use /plan before complex work.
  Plan before you build. The plan IS the deliverable in REASONING stage."
```

### 66.4 /compact Strategy

```
WHEN to use /compact:
  - Context approaching 70% → consider compacting
  - Between logical tasks in same session
  - Before rate limit rollover (force compact to prevent spike)
  - After long analysis/investigation phase

HOW to use /compact:
  /compact preserve the current task context, plan, and contributions.
  Focus on: task requirement, accepted plan, colleague inputs.
  Drop: previous exploration, dead-end investigations, large file reads.

Agent training needed:
  CLAUDE.md: "When context exceeds 70%, use /compact with specific
  preservation instructions. Save key state to memory first."

  HEARTBEAT.md: "If HEARTBEAT reports high context usage,
  consider strategic compaction before next heavy task."
```

### 66.5 /context Inspection

```
WHEN to use /context:
  - Before starting heavy work (large codebase reads)
  - When context feels sluggish (possible bloat)
  - After compaction (verify what was preserved)

Agent training needed:
  TOOLS.md should list /context as a diagnostic tool.
```

### 66.6 /debug Usage

```
Available to: all agents (built-in)
Primary users: software-engineer, devops, qa-engineer

WHEN to use /debug:
  - Tests failing with unclear cause
  - Runtime error during implementation
  - Integration issue between components

Agent training needed:
  Engineer CLAUDE.md: "When stuck on a bug, use /debug
  for interactive debugging instead of guessing."
```

---

## 67. Multi-Fleet Identity & Coordination

**What this section is:** How multiple fleets share infrastructure
while maintaining separate identities.

### 67.1 Fleet Identity Structure

```
config/fleet-identity.yaml:
  fleet:
    id: fleet-99c1272b          # UUID-based (current)
    name: Fleet WORKSTATION-JFM # Machine name
    machine: WORKSTATION-JFM
    uuid: 99c1272b-...
    agent_prefix: 99c1          # Short prefix for branches/commits

Target (multi-fleet):
  fleet:
    id: alpha                   # Short identifier
    number: 1                   # Numeric fleet identifier
    name: "Fleet Alpha"         # Display name
```

### 67.2 Agent Identity Derivation

```
Pattern: {fleet_id}-{role}

Fleet Alpha:
  alpha-pm, alpha-fleet-ops, alpha-architect,
  alpha-devsecops, alpha-engineer, alpha-devops,
  alpha-qa, alpha-writer, alpha-ux, alpha-accountability

Fleet Bravo:
  bravo-pm, bravo-fleet-ops, bravo-architect, ...

Display names:
  "PM Alpha", "Architect Alpha", "Engineer Bravo", ...

Git attribution:
  Commits signed: Co-Authored-By: alpha-engineer
  Branch prefix: alpha-task-{id}
```

### 67.3 Shared vs Separate Infrastructure

```
SHARED (one instance for all fleets):
  Plane          → one workspace, both fleets create/read issues
  GitHub         → shared repos, fleet-prefixed branches
  ntfy           → shared notification server

SEPARATE (per fleet):
  Mission Control → each fleet has own MC instance
  Gateway        → each fleet has own gateway
  Orchestrator   → each fleet has own brain loop
  Agent sessions → each fleet's agents are independent
  LocalAI        → each fleet has own cluster (peered)

PEERED:
  LocalAI Cluster 1 ↔ Cluster 2
    Load balance: simple tasks distributed
    Failover: if one down, other handles all
    Model specialization: each cluster primary model differs
```

### 67.4 Cross-Fleet Coordination

```
Scenario: Fleet Alpha and Fleet Bravo on same project

  Plane issues have NO fleet prefix → either fleet can pick up
  PM Alpha assigns to alpha-engineer
  PM Bravo assigns to bravo-architect (design input)

  Cross-fleet contribution:
    bravo-architect contributes design_input to alpha-engineer's task
    Contribution posted to shared Plane issue
    Board memory on Alpha's MC tagged with contribution

  Conflict prevention:
    Task assignment includes fleet prefix
    Only assigned fleet's agents work on task
    Cross-fleet is contribution only, not co-ownership
```

---

## 68. Strategic Roadmap — Phases 5-11

**What this section is:** What comes after the 24-step path-to-live.
The longer-term evolution of the fleet.

### 68.1 Phase 5: LocalAI Progressive Offload (Stage 3-4)

```
Target: 30-50% of operations on LocalAI

Work:
  - Route heartbeats to LocalAI (hermes-3b or Qwen3.5-4B)
  - Route simple reviews to LocalAI
  - Route structured responses to LocalAI
  - Build failover chain: LocalAI → Claude
  - Cluster peering: Machine 1 ↔ Machine 2
  - Measure quality: LocalAI vs Claude for each operation type

Success: 30% token reduction, fleet operates during Claude outages
```

### 68.2 Phase 6: Brain Layer 2 — Chain Registry

```
Target: Event-driven brain architecture

Work:
  - Build chain_registry.py (event → handler registration)
  - Move from direct function calls to event-driven handlers
  - Enable: cascade events (handler produces new events)
  - Enable: external event sources (Plane webhooks, GitHub webhooks)
  - Depth limit: prevent infinite cascades

Success: brain reacts to events, not just polls
```

### 68.3 Phase 7: Brain Layer 3 — Logic Engine

```
Target: Configurable dispatch rules

Work:
  - Build logic_engine.py (rule-based gate evaluation)
  - Move 10 dispatch gates from hardcoded to config-driven
  - PO can modify gate rules without code changes
  - Hot-reload: config changes apply next cycle

Success: PO adjusts fleet behavior via config, not code
```

### 68.4 Phase 8: Agent Teams Integration

```
Target: Evaluate and pilot Agent Teams

Work:
  - Enable CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
  - Pilot on one multi-agent task (architect + engineer on epic)
  - Assess: mailbox messaging vs board memory
  - Assess: shared task list vs OCMC tasks
  - Decision: complement or conflict with orchestrator?

Success: clear architecture decision, documented tradeoffs
```

### 68.5 Phase 9: LightRAG Deployment

```
Target: Knowledge graph for fleet knowledge

Work:
  - Deploy LightRAG (Docker, port 9621)
  - Ingest: system docs, design specs, architecture decisions
  - PO uses: WebUI for research sharing, FAQ management
  - Phase 2: OCMC sync (board memory → LightRAG)
  - Phase 3: agent MCP tool (fleet_query_knowledge)

Success: PO can query cross-project relationships
```

### 68.6 Phase 10: Near-Independent LocalAI Operation

```
Target: 80%+ on LocalAI, Claude for complex only

Work:
  - Qwen3.5-9B as primary workhorse
  - TurboQuant for 48-64K context on 8GB
  - Full contribution flow on LocalAI
  - Full review flow on LocalAI (simple reviews)
  - Claude only for: architecture, security, strategic planning

Success: fleet runs during extended Claude outages
```

### 68.7 Phase 11: Multi-Fleet + Scale

```
Target: 2-3 fleets, 20-30 agents

Work:
  - Deploy Fleet Bravo on Machine 2
  - Shared Plane, peered LocalAI clusters
  - Cross-fleet contribution model
  - Fleet-level load balancing
  - Unified monitoring across fleets

Success: multiple fleets coordinate on shared projects
```

---

## 69. Index to Supporting Documents

**What this section is:** Cross-reference to ALL supporting documentation.
Not content — pointers to where detail lives.

### 69.1 System Documentation (22 docs, 10,283 lines)

```
docs/systems/
  01-methodology.md          5-stage methodology, stage gating
  02-immune-system.md        Disease detection, teaching, self-healing
  03-teaching.md             Lesson adaptation, injection
  04-event-bus.md            47 event types, 6 surfaces
  05-control-surface.md      work_mode, cycle_phase, backend_mode
  06-agent-lifecycle.md      ACTIVE→IDLE→SLEEPING→OFFLINE
  07-orchestrator.md         Brain cycle, dispatch, transitions
  08-mcp-tools.md            25 tools reference
  09-standards.md            Quality standards framework
  10-transpose.md            Artifact rendering, completeness
  11-storm.md                9 indicators, 5 severity levels
  12-budget.md               Tempo, quota monitoring
  13-labor.md                Attribution, stamps, analytics
  14-router.md               Backend routing, circuit breakers
  15-challenge.md            Iterative validation, 4 types
  16-models.md               Model selection, benchmarking
  17-plane.md                Plane sync, methodology mapping
  18-notifications.md        IRC, ntfy, Plane routing
  19-session.md              Context management, pre-embed
  20-infrastructure.md       8 clients, IaC scripts
  21-agent-tooling.md        MCP servers, plugins, skills
  22-agent-intelligence.md   Brain evaluation, context endgame
```

### 69.2 Fleet Elevation (31 docs, ~15,000 lines)

```
docs/milestones/active/fleet-elevation/
  01-overview.md             Elevation overview
  02-agent-template.md       Template architecture
  03-delivery-phases.md      Phase system
  04-brain-spec.md           16-step brain design
  05-14: Role specs          10 agent role deep-dives
  15-cross-agent-synergy.md  Contribution matrix
  16-multi-fleet-identity.md Fleet identity system
  17-standards-framework.md  Standards enforcement
  18-po-governance.md        PO authority model
  19-flow-validation.md      End-to-end validation
  20-ai-behavior.md          Anti-corruption rules
  21-task-lifecycle.md        Task state machine
  22-milestones.md           Elevation roadmap
  23-agent-lifecycle.md       Strategic calls design
  24-tool-call-trees.md      Complete tool trees
  25-diagrams.md             System diagrams
  26-unified-config.md       Config reference
  27-evolution.md            Change management
  28-codebase-inventory.md   Module ownership
  29-lessons-learned.md      Implementation lessons
  30-strategy-synthesis.md   Strategic summary
  31-transition-strategy.md  Current → future state
```

### 69.3 Agent Rework (14 docs, ~5,000 lines)

```
docs/milestones/active/agent-rework/
  01-overview.md             Rework goals
  02-pre-embedded-data.md    Context strategy
  03-orchestrator-waking.md  Wake mechanism
  04-14: Role rewrites       Per-role specifications
  13-live-test-plan.md       Validation approach
  14-full-fleet-vision.md    PO requirements capture
```

### 69.4 Standards (8 docs, ~2,000 lines)

```
docs/milestones/active/standards/
  claude-md-standard.md      CLAUDE.md rules
  heartbeat-md-standard.md   HEARTBEAT.md rules
  agent-yaml-standard.md     agent.yaml rules
  identity-soul-standard.md  IDENTITY + SOUL rules
  tools-agents-standard.md   TOOLS + AGENTS rules
  context-files-standard.md  Context file rules
  iac-mcp-standard.md        IaC script rules
  brain-modules-standard.md  Brain module rules
```

### 69.5 Strategic Plans

```
docs/milestones/active/
  strategic-vision-localai-independence.md   5-stage LocalAI plan
  ecosystem-deployment-plan.md              15 ecosystem items
  context-window-awareness-and-control.md   CW-01 to CW-10
  implementation-roadmap.md                 Wave-based plan
  unified-implementation-plan.md            U-01 to U-38
  path-to-live.md                           24-step ordered path
  labor-attribution-and-provenance.md       M-LA01 to M-LA08
  model-upgrade-path.md                     Model progression
  multi-backend-routing-engine.md           Routing design
  storm-prevention-system.md                Storm design
  integration-testing-plan.md               Test strategy
```

### 69.6 Reference Documents

```
docs/
  ARCHITECTURE.md        System map, 20 systems, connections
  INTEGRATION.md         12 cross-system data flows
  SPEC-TO-CODE.md        Spec → implementation mapping
  WORK-BACKLOG.md        Prioritized backlog + gaps
  README.md              Documentation layer map
```

### 54.3 Model Selection for Fleet

```
select_model_for_task(task, agent_name):
  
  Complex/critical tasks:     Claude opus (always)
  Security/architecture:      Claude opus (never free/trainee)
  Standard implementation:    Claude sonnet
  Simple structured response: LocalAI (when routed)
  Heartbeat (no work):        LocalAI or brain eval (when built)
  Direct API calls:           No LLM needed (fleet_read_context)

Backend selection via router:
  route_task(task, agent, backend_mode, localai_available):
    1. Get enabled backends from backend_mode
    2. Filter by task capabilities needed
    3. Filter by agent role constraints
    4. Sort by cost (cheapest first)
    5. Pick cheapest capable backend
```

### 54.4 Cold Start Management

```
Problem: 80s cold start for 7B model is too slow for interactive work.

Strategies:
  1. WARM POOL: keep most-used model loaded
     - hermes-3b stays loaded during fleet operation
     - Swap only when complex LocalAI task arrives
     - Watchdog timeout prevents stuck model

  2. PRE-WARMING: load model before needed
     - Brain detects: next cycle will dispatch to LocalAI
     - Pre-load model now (during idle time)
     - Task dispatches to warm model

  3. MODEL STICKINESS: avoid unnecessary swaps
     - If 3 tasks in a row need hermes-3b, keep it loaded
     - Only swap when different model explicitly needed
     - Track swap frequency → alert if thrashing

  4. CPU FALLBACK: phi-2 always available
     - If GPU model loading fails → route to phi-2 (CPU)
     - Lower quality but zero cold start
     - Better than Claude fallback for simple tasks (free)

Target SLAs:
  3B model cold start: < 15 seconds
  7B model cold start: < 90 seconds
  9B model cold start: < 60 seconds
  Warm inference: < 2 seconds (any model)
  GPU model thrashing: < 3 swaps/hour (alert if exceeded)
```

### 54.5 Multi-GPU Future (Machine 2)

```
When second machine available:
  Machine 1: LocalAI Cluster 1 (8GB VRAM)
    → Primary: hermes-3b or Qwen3.5-4B (always loaded)
    → Swap for: complex LocalAI tasks

  Machine 2: LocalAI Cluster 2 (8GB VRAM)
    → Primary: Qwen3.5-9B (primary workhorse)
    → Swap for: codellama (code tasks)

  Peering: Cluster 1 ↔ Cluster 2
    → Load balance: round-robin for simple tasks
    → Specialization: route by model capability
    → Failover: if one cluster down, other handles all

  Combined VRAM: 16GB
    → Two models simultaneously (one per GPU)
    → No cold start for primary models
    → Complex models available without swapping


---

## §70 Standards & Quality Framework — Operational Depth

**Source:** fleet-elevation/17-standards-framework.md (583 lines)

> "we need to make sure a clean structure is respected and SRP, Domain,
> Onion and all the goods standard we want to impose our fleet."

**Why it matters:** Standards are the quality skeleton of the fleet.
Without them, agents produce inconsistent output and fleet-ops reviews
are subjective ("does this look good?" instead of "does this meet
the defined criteria?"). Standards connect to:
- **Artifact system:** The 13 artifact types each have required fields
  and quality criteria — standards.py checks completeness automatically
- **Fleet-ops review (§31):** Fleet-ops reviews AGAINST standards, not
  personal opinion. Standards make review deterministic and fair
- **Immune system (§73):** Doctor detects when agents violate standards
  (missing fields, incomplete artifacts, monolithic code)
- **Contributions (§83):** Contributors produce artifacts that conform
  to their type's standard — QA produces qa_test_definition with
  specific required fields, not free-form text
- **Accountability (§87):** Compliance reports measure standards
  adherence per sprint, per agent — methodology compliance %,
  artifact completeness %, PR standards compliance %
- **Teaching (§6.2):** When an agent violates standards, teaching
  lessons reference the specific standard they missed
- **Architect role:** Architect enforces SRP/DDD/Onion in design
  contributions — the engineer receives design constraints that
  ARE the standards for that implementation
- **PO requirements:** The PO's verbatim requirements on each task
  ARE the quality bar. Standards enforce the structural side
  (fields present, criteria checkable, commits conventional).
  The PO's words enforce the content side (does it do what was asked).

### 70.1 Code Standards — What Agents Must Follow

**SRP (Single Responsibility Principle):**
- One module = one concern, one class = one entity/service, one function = one operation
- No god objects, no kitchen-sink modules
- Architect enforces in design contributions, fleet-ops checks during review
- Immune system detects when agents produce monolithic code

**Domain-Driven Design:**
- Domain entities are pure data (no infrastructure imports)
- Business logic in domain services, infrastructure adapts external systems
- Bounded contexts don't bleed into each other
- Ubiquitous language: code uses same terms as the PO

**Onion Architecture:**
- Core domain (inner): entities, value objects, domain services
- Application layer: use cases, orchestration
- Infrastructure (outer): databases, APIs, file systems
- Dependencies point INWARD — inner layers never reference outer

**Architecture depth is set by the PO per deliverable.** The PO
declares the phase (any name — "poc", "mvp", "potato") and provides
the requirements for what that phase means. The system records
`delivery_phase` as a free text field. The PO's requirements for
that specific deliverable at that specific phase ARE the standards.
No config file, no predefined progressions — because each case is
different and the PO defines it per-case.

### 70.2 Artifact Standards — 13 Types

**7 Current types** (in `fleet/core/standards.py`):
task, bug, analysis_document, investigation_document, plan,
pull_request, completion_claim

**6 New types needed:**

```
qa_test_definition:
  required: test_criteria (IDs, descriptions, types, priorities),
            target_task_reference, delivery_phase, verification_method
  quality: specific+checkable (not "test that it works"),
           phase-appropriate depth (POC: happy path, prod: complete)

security_requirement:
  required: threat_assessment, requirements_list, restrictions_list,
            review_checklist
  quality: specific to task (not generic "be secure"),
           references actual code/files

design_input:
  required: approach, target_files, constraints, integration_points,
            complexity_assessment
  quality: references specific files+lines, considers existing patterns,
           multiple approaches considered

ux_spec:
  required: component_structure, interaction_patterns, layout_guidance,
            accessibility (ARIA, keyboard)
  quality: specific enough to implement from, addresses all states
           (loading, error, empty, success)

compliance_report:
  required: sprint/period, methodology_compliance, contribution_coverage,
            gate_compliance, trail_completeness, quality_metrics,
            findings, recommendations

sprint_plan:
  required: sprint_id, dates, goals, task_list (with assignments,
            priorities, dependencies), velocity_target,
            contribution_plan, risk_assessment
```

### 70.3 Phases — PO Declares, System Records

> "not set in stone"
> "or alpha, beta, rc & etc....."
> "Things can evolve"

**Phases are a PO declaration.** The PO says "this is MVP" — it's MVP.
The PO says "this is potato" — it's potato. The PO says "this is
load-tested" — it's load-tested.

`delivery_phase` is a **free text field** on the task. The system
records it, displays it, filters by it. The system does NOT:
- Define what phases exist
- Define what a phase means
- Gate advancement between phases via config
- Enforce standards per phase via code
- Maintain predefined progressions

The PO provides the requirements for each deliverable at each phase
through their verbatim requirements on the task. That IS the standard.
There is no `phases.yaml` config file because each case is different
and the PO defines it per-case, per-deliverable, per-moment.

The PO can:
- Use any name for any phase
- Change it at any time
- Use different phase names for different deliverables
- Skip phases, add phases, invent phases
- Define what each phase means through the task requirements

### 70.4 Design Patterns — Know When to Use What

> "we need to use design patterns, know when to do a builder, a cache,
> an index, a mediator, an API, a core, a module...."

| Pattern | When to Use | Fleet Example |
|---------|-------------|---------------|
| **Builder** | Complex object with many optional parts | Context assembly, autocomplete chain |
| **Mediator** | Components communicate without coupling | Event bus, chain registry |
| **Observer** | One event → multiple independent reactions | Event handlers, notifications |
| **Strategy** | Algorithm varies by context | Role-specific providers, model selection |
| **Factory** | Object creation depends on runtime type | Contribution creation, artifact creation |
| **Cache** | Repeated expensive lookups | Context assembly cache per cycle |
| **Index** | Fast lookup by multiple keys | Agent→tasks, task→contributions |
| **Adapter** | External API doesn't match domain | MC client, Plane client, gateway |
| **Facade** | Simplify complex subsystem | MCP tools as facade over domain |
| **Chain of Resp.** | Multiple handlers for same request | Dispatch gates, review chain |

**Research before building:**
1. Check if a library/package solves the problem
2. Check if a framework provides the pattern
3. Check if an industry standard exists (CloudEvents, OpenAPI, OAuth2, OTEL)
4. Validate: security, maintenance, license, community
5. Document decision (architect creates ADR)

### 70.5 TDD and Testing Standards

> "Use TDD when possible with high critical level tests and pessimistic
> ones with smart assertions and logics."

**TDD cycle with contribution model:**
1. QA predefines test criteria (what must pass)
2. Engineer writes test cases that fail (red)
3. Engineer implements to make tests pass (green)
4. Engineer refactors while keeping tests green

**Pessimistic testing** — tests assume things WILL go wrong:
API returns 500, database down, malformed input, auth expires mid-request,
disk full, concurrent race conditions.

**Smart assertions** — verify BEHAVIOR, not implementation:
- Good: "returns 200 with valid token and body contains user.id"
- Bad: "mock was called 3 times" (tests wiring, not behavior)

**Critical levels:**

| Level | What | Example |
|-------|------|---------|
| **Critical** | Security, data integrity, auth | "Unauthenticated → 401" |
| **High** | Core business logic, data flow | "Dispatch follows all 10 gates" |
| **Medium** | Feature behavior, integrations | "Contribution propagates to target" |
| **Low** | Display, formatting, convenience | "IRC message formats correctly" |

### 70.6 Enforcement Matrix

| Standard | Primary Enforcer | Secondary |
|----------|-----------------|-----------|
| Code SRP/Domain/Onion | Architect (design input) | Fleet-ops (review) |
| Artifact completeness | Standards library (automated) | Fleet-ops (review) |
| Task quality | PM (triage) | Fleet-ops (review) |
| PR standards | Fleet-ops (review) | Doctor (detection) |
| Test coverage | QA (predefined tests) | Fleet-ops (review) |
| Documentation | Technical writer (continuous) | PM (sprint review) |
| Security | DevSecOps (requirements + review) | Doctor (detection) |
| Trail completeness | Accountability generator | Fleet-ops (review) |
| PO requirements match | Fleet-ops (review) | Doctor (detection) |

**Industry standards awareness:**

| Domain | Standard |
|--------|---------|
| Events | CloudEvents |
| API | OpenAPI/Swagger |
| Auth | OAuth2/OIDC |
| Commits | Conventional Commits (adopted) |
| Containers | OCI |
| CI/CD | GitHub Actions |
| Monitoring | OpenTelemetry |
| Config | YAML/TOML |

### 70.7 Scale, Evolution, and Failure Planning

**Scale thinking:** What happens at 100 tasks? 50 agents? 5 fleets?
1000 events/minute? Don't over-engineer (POC ≠ Kubernetes), but
DESIGN for it (no hardcoded limits, use config, proper data structures).

**Evolution awareness:**
- **Evolve:** feature works but needs better patterns → refactor
- **Refactor:** code correct but hard to maintain → clean up
- **Change:** requirements changed → adapt implementation
- **Remove:** feature no longer needed → delete cleanly
- **Upgrade:** dependency has new version → evaluate and update

**Failure planning at every level:**
- Agent failure → session crashes, picks up from persistent artifacts
- System failure → MC/gateway/Plane down, graceful degradation
- Chain failure → partial execution, next cycle catches up
- Data failure → validation at boundaries
- Network failure → retries with backoff, circuit breaker
- Human failure → PO unavailable, PM handles within scope

---

## §71 PO Governance Authority Model — Complete Structure

**Source:** fleet-elevation/18-po-governance.md (276 lines)

> "I am the PO"
> "This need meticulous thinking logical transition and time for approval
> and even approvals only me can answers."

**Why it matters:** The PO is the ultimate authority. The governance
model is not bureaucracy — it is the CONTROL MECHANISM that ensures
10 autonomous AI agents produce what the PO wants, at the quality
the PO demands, with the priorities the PO sets. Without it:
- Agents self-approve their own work (no quality gate)
- PMs dispatch work the PO hasn't validated (wrong direction)
- Fleet-ops approves without PO oversight (rubber stamps)
- Budget burns on work the PO didn't authorize
- Requirements drift from the PO's words (compression disease)

Governance connects to:
- **Brain gates (§90 Step 3):** Brain reads PO gate decisions from
  board memory and advances/regresses readiness. Deterministic.
- **Readiness system (§45):** The 90% gate is a PO-only checkpoint.
  No work begins without PO approval at this gate.
- **Regression (§41):** PO can regress readiness to ANY value at
  any time — minor (95%), moderate (70%), major (30%), complete (0%).
  The most powerful governance tool.
- **Directives:** PO posts to board memory → brain routes to agents →
  overrides all other priorities. The fleet obeys.
- **Work mode (§7):** PO controls fleet tempo and activity via
  work_mode, cycle_phase, budget_mode — full control surface.
- **PM as filter (§71.4):** PM doesn't forward raw data — PM
  summarizes and highlights so PO decisions are efficient.
- **Immune system:** 3 PO corrections on same issue = prune signal.
  The PO's feedback IS immune system input.

### 71.1 Authority Hierarchy

**What ONLY the PO Can Do:**
- Approve readiness past 90% (the work gate)
- Declare delivery phase (free text — PO's word)
- Regress readiness to any value at any time
- Override fleet-ops approval/rejection decisions
- Change fleet work mode (full-autonomous → paused, etc.)
- Change fleet cycle phase (execution → planning, etc.)
- Post directives that override all other priorities
- Define requirements (verbatim — anchor for all work)
- Accept or reject the fleet's output

**What PM Can Do (With PO Confirmation):**
- Advance readiness from 0 to 89% (below PO gate)
- Assign agents to tasks
- Break epics into subtasks
- Set task fields (type, stage, readiness, story_points, phase)
- Route questions to PO
- Manage sprint planning and execution
- Resolve blockers within their authority

**What Agents Can Do (On Their Own Tasks):**
- Advance readiness within current stage's range
  (e.g., analysis stage: 20% → 40%)
- NOT past stage boundaries without PM involvement
- NEVER past 90% without PO approval

**What Fleet-Ops Can Do:**
- Approve or reject work in review
- PO can override fleet-ops decisions
- Cannot advance readiness past review gates

### 71.2 Strategic Checkpoints

```
Checkpoint 0%  — Task Birth
  Task exists, nothing confirmed. Requirements may be vague.
  PO/PM clarify through conversation protocol.

Checkpoint 50% — Direction Confirmed
  Clear requirements, direction confirmed by PO.
  Investigation complete, options understood.
  "Are we building the right thing?" checkpoint.
  PO notified → confirm / redirect / defer.

Checkpoint 90% — Plan Confirmed (PO GATE)
  Plan exists, references verbatim, ready for execution.
  "Go build it" gate. ONLY PO can approve.
  PO MUST approve → approve (→99%) / reject (→reasoning) / modify.
```

### 71.3 Readiness Regression — PO's Most Powerful Tool

```
Minor     (99% → 95%): "Fix this specific issue and resubmit."
  Task stays in current stage. Re-review after fix.

Moderate  (99% → 70%): "The plan needs rethinking."
  Returns to reasoning stage. PO re-approves at 90% gate.

Major     (99% → 30%): "This doesn't match what I asked for."
  Returns to analysis stage. Full progression needed.
  Signals fundamental misunderstanding.

Complete  (99% → 0%):  "Start over. The understanding is wrong."
  Returns to conversation stage. Full progression needed.
  Immune system flags: critical failure.
```

Every regression is: logged in trail, event emitted, comment posted
with PO feedback, immune system notified, sprint progress adjusted.

### 71.4 The PM as PO Filter

**PM Filters (handles internally):**
- Routine status updates → PM handles, PO gets sprint summary
- Agent questions about implementation details → PM answers
- Blocker resolution within PM scope → PM handles
- Simple task assignment decisions → PM decides

**PM Routes to PO (with context):**
- Gate requests (readiness 90%, phase advancement)
- Requirement questions (what to build, not how)
- Strategic decisions (priority changes, scope changes)
- Escalations PM can't resolve
- Compliance concerns (from accountability generator)
- Security alerts (from DevSecOps)

**PM summarizes and highlights — not raw forwarding:**
```
GOOD: "PO: Task 'Add CI/CD' at readiness 88%. Plan references your
  requirement: 'Add CI/CD to NNRT with GitHub Actions.' Architect
  confirmed. QA predefined 5 tests. All contributions received.
  Ready for 90% gate approval. Decision needed: approve?"

BAD:  "PO: task needs review." ← Lazy routing. Immune system detects.
```

### 71.5 PO Interaction Channels

```
Directives (PO → Fleet):   Board memory [directive] tag
  "All agents focus on NNRT this sprint"
  Override everything. Brain routes to targets.

Gate Decisions (PO → Task): Board memory [gate, po-decision] tag
  "Approved: task ABC readiness 90%"
  Brain processes gate decision → updates task state.

Requirements (PO → Task):  Task comments or verbatim field update
  Sacrosanct. Agents must not deform.

Feedback (PO → Agent):     Task comments
  3 corrections = doctor signal.

ntfy (Fleet → PO):         Push notifications
  Gate requests, security alerts, escalations, budget warnings.
```

### 71.6 Governance Per Work Mode

| Mode | Governance Active | PO Involvement |
|------|-------------------|----------------|
| full-autonomous | Full chain, all gates | Strategic checkpoints |
| project-management-work | PM + fleet-ops only | Planning decisions |
| local-work-only | Current tasks only | Critical alerts only |
| finish-current-work | Wind-down, no new gates | Completion notifications |
| work-paused | Fleet frozen | Critical alerts only |

---

## §72 Flow Validation — Five End-to-End Walkthroughs

**Source:** fleet-elevation/19-flow-validation.md (401 lines)
**Why it matters:** Individual systems can each be correct and still
produce wrong behavior when composed. These walkthroughs validate that
every state transition, chain, gate, and contribution fires correctly
when the FULL system operates end-to-end.

### 72.1 Flow 1: Simple Task (Story, MVP Phase)

```
PO creates "Add search endpoint" in Plane
│
├─ Plane sync → OCMC inbox (stage: unset, readiness: 0, phase: mvp)
│
├─ PM heartbeat:
│   ├─ Sets: type=story, stage=conversation, readiness=5%
│   ├─ Sets: agent=software-engineer, points=5, phase=mvp
│   ├─ Sets: verbatim from Plane description
│   └─ Comment: "Assigned to engineer. Stage: conversation."
│
├─ CONVERSATION (5→20%):
│   ├─ Engineer posts questions as comments
│   ├─ PO responds with clarifications
│   └─ PM advances stage → analysis (readiness 20%)
│
├─ ANALYSIS (20→40%):
│   ├─ Engineer examines codebase
│   ├─ Produces analysis_document artifact
│   └─ PM advances stage → reasoning (readiness 40%)
│
├─ REASONING (40→90%):
│   ├─ Brain fires contribution chains:
│   │   ├─ QA test predefinition task (auto)
│   │   ├─ Architect design input task (auto)
│   │   └─ DevSecOps security requirement task (auto, mvp phase)
│   │
│   ├─ PARALLEL CONTRIBUTIONS:
│   │   ├─ Architect → design_input → propagates to task
│   │   ├─ QA → qa_test_definition → propagates to task
│   │   └─ DevSecOps → security_requirement → propagates to task
│   │
│   ├─ Engineer produces plan artifact (references verbatim)
│   ├─ Brain: all contributions received? YES
│   ├─ PM: readiness → 88%, routes gate request to PO
│   │
│   └─ PO GATE (90%):
│       ├─ PO reviews plan + contributions
│       ├─ PO approves → readiness → 99%
│       └─ Stage → work
│
├─ WORK (99→100%):
│   ├─ Engineer context includes: architect design, QA tests, DevSecOps reqs
│   ├─ Engineer implements following plan
│   ├─ fleet_commit × 3 (conventional commits)
│   └─ fleet_task_complete → CHAIN (12+ ops):
│       ├─ Push branch, create PR
│       ├─ Status → review, create approval
│       ├─ Notify QA + DevSecOps for validation
│       ├─ IRC #reviews, event emitted
│       └─ Trail recorded
│
├─ REVIEW (7-step):
│   ├─ Fleet-ops: verbatim match ✓, trail complete ✓, PO gate ✓,
│   │   MVP standards ✓, acceptance criteria evidenced ✓
│   ├─ QA validation: 5/5 predefined tests addressed ✓
│   ├─ DevSecOps review: no security findings ✓
│   └─ Fleet-ops approves → CHAIN:
│       ├─ Status → done, sprint progress updated
│       ├─ Trail finalized, technical writer notified
│       └─ Accountability: verify trail
│
└─ DONE — 8 of 10 agents involved, ~8-12 cycles (30-60 min)
```

### 72.2 Flow 2: Epic With Subtasks (Production Phase)

```
PO creates "Add user authentication system" (epic, production)
│
├─ PM: type=epic, full 5-stage progression (conversation→work)
│   Readiness: 0% → 10% → 30% → 50% (PO checkpoint) → 80%
│
├─ PM breaks epic into subtasks at reasoning stage:
│   ├─ "Design auth data model" → architect
│   ├─ "Implement JWT middleware" → engineer
│   ├─ "Add login/register endpoints" → engineer
│   ├─ "Write auth integration tests" → QA
│   ├─ "Security audit auth system" → DevSecOps
│   ├─ "Document auth API" → technical-writer
│   │
│   └─ Dependencies:
│       design → middleware → endpoints
│       endpoints → tests, security, docs (parallel)
│
├─ PO GATE at 90% on epic → approves the plan
│
├─ SUBTASK EXECUTION (brain manages dependencies):
│   ├─ Architect completes design → unblocks middleware
│   ├─ Engineer completes middleware → unblocks endpoints
│   ├─ Engineer completes endpoints → unblocks tests/security/docs
│   ├─ QA, DevSecOps, writer execute in parallel
│   └─ Brain: ALL subtasks done → epic moves to review
│
├─ EPIC REVIEW:
│   ├─ Fleet-ops reviews with aggregated child results
│   ├─ Production standards: complete coverage, security certified,
│   │   comprehensive docs, compliance verified
│   └─ Approved → epic done
│
└─ PHASE ADVANCEMENT:
    ├─ PM: "Auth system ready for production"
    ├─ Brain checks production standards ✓
    └─ PO approves phase advancement
```

### 72.3 Flow 3: Rejection and Regression

```
Task "Implement search" at readiness 99%, work stage
Engineer calls fleet_task_complete
│
├─ Fleet-ops reviews:
│   ├─ Verbatim: "use Elasticsearch"
│   ├─ Implementation: custom SQL full-text search
│   └─ REJECTS: "verbatim mismatch"
│
├─ Rejection chain:
│   ├─ Status: review → in_progress
│   ├─ Readiness: 99% → 70% (moderate regression to reasoning)
│   ├─ Doctor signal: agent deviation
│   └─ Trail: rejection with reason + regression amount
│
├─ Engineer's next heartbeat:
│   ├─ Context: "REJECTED. Implementation uses SQL but verbatim
│   │   says Elasticsearch. Regressed to reasoning at 70%."
│   └─ Autocomplete → re-plan with Elasticsearch
│
├─ PO re-approves at 90% gate:
│   ├─ Option A: approves Elasticsearch plan → work resumes
│   ├─ Option B: changes requirement → "SQL is fine, update verbatim"
│   └─ Option C: "Start over" → readiness → 0%
│
└─ Re-implementation → re-review → approved
```

### 72.4 Flow 4: Phase Advancement (POC → MVP)

```
Deliverable "NNRT Search" at phase: poc, all POC tasks done
│
├─ PM evaluates: POC work complete, PO wanted MVP next
│   ├─ PM identifies gaps vs what PO requires for MVP
│   └─ Creates new tasks for MVP gaps
│
├─ PM communicates to PO: "POC work done. Ready for MVP?"
│
├─ PO declares: phase is now "mvp"
│   ├─ PO provides requirements for what MVP means for this deliverable
│   ├─ delivery_phase field updated to "mvp"
│   ├─ Agents see new phase in context
│   └─ IRC #sprint: "[milestone] NNRT Search → MVP"
│
├─ MVP work executes (new tasks with PO's MVP requirements)
│
└─ When done, PM communicates to PO → PO decides next phase
```

### 72.5 Flow 5: Immune System Intervention

```
Agent "software-engineer" in investigation stage
Doctor runs detection during orchestrator cycle
│
├─ Detection: fleet_commit called during investigation stage
│   Disease: protocol_violation, Severity: medium
│
├─ Response: first offense, no prior lessons → TRIGGER_TEACHING
│
├─ Teaching chain:
│   ├─ Lesson: "Investigation stage: you may NOT commit code.
│   │   You did: fleet_commit. This is a protocol violation."
│   ├─ Exercise: "State your stage. State what protocol allows.
│   │   State what you did wrong."
│   └─ Inject via gateway into agent session
│
├─ Agent: must complete exercise before returning to task
│   ├─ Comprehension demonstrated → lesson cleared
│   └─ Fails × 3 → prune triggered
│
├─ If prune: session killed, agent regrows fresh,
│   task context preserved in files, trail records "pruned"
│
└─ Hidden from agent: they don't know about the doctor
```

### 72.6 Validation Checklist

For each flow, verify:
- [ ] Every state transition is deterministic (brain handles)
- [ ] Every gate has clear authority (PO, PM, fleet-ops)
- [ ] Every chain fires correctly (event → handlers → effects)
- [ ] Every contribution created at the right time
- [ ] Every standard checked at the right phase
- [ ] Every notification goes to the right channel
- [ ] Every trail event recorded
- [ ] Autocomplete chain leads to correct action at each step
- [ ] Regression paths are clean (correct stage, correct readiness)
- [ ] Immune system detects without agent awareness

### 72.7 15 Diagrams Required

**Architecture:** (1) System relationship map, (2) Onion architecture
for agent context, (3) Data flow from PO requirement to approval.

**Lifecycle:** (4) Task state machine with rejection paths,
(5) Stage progression with gates, (6) Phase as PO-declared dimension,
(7) Two-axis: stages × phases (independent dimensions).

**Chains:** (8) Event chain flow, (9) Contribution chain,
(10) Completion chain with parent evaluation.

**Agents:** (11) Synergy matrix visual, (12) Communication diagram.

**Operational:** (13) Orchestrator 12-step cycle, (14) Dispatch
decision tree (10 gates), (15) Immune system flow

---

## §73 AI Behavior Prevention — Three Lines of Defense

**Source:** fleet-elevation/20-ai-behavior.md (381 lines)
**Why it matters:** AI agents are sick by default. LLMs are trained to
produce plausible output, not correct output. Rules alone don't work —
they degrade as context grows (Lost in the Middle effect). The fleet
needs STRUCTURAL mechanisms that make correct behavior the path of
least resistance and incorrect behavior difficult or impossible.

### 73.1 The Disease Catalog — 10 Specific Diseases

```
1. DEVIATION      — does something different from what was asked
2. LAZINESS       — takes shortcuts, does partial work
3. CONFIDENT-BUT-WRONG — sure it understands, but doesn't
4. ABSTRACTION    — replaces literal words with interpretation
5. COMPRESSION    — minimizes scope, shrinks vision, reduces ambition
6. CONTEXT CONTAMINATION — old context warps new requests
7. SCOPE CREEP    — adds unrequested "improvements"
8. CASCADING FIX-ON-FIX — layers fixes, making things worse
9. NOT LISTENING  — produces output instead of processing input
10. CODE WITHOUT READING — writes code without reading existing
```

### 73.2 Three Lines of Defense

```
LINE 1: STRUCTURAL PREVENTION (before disease appears)
  Make correct behavior the NATURAL one.
  The AI doesn't decide what to do — the data leads there.
  Deviation requires FIGHTING the autocomplete chain.

  Mechanisms:
  ├─ Autocomplete chain engineering (data ordering)
  ├─ Stage-gated tool access (fleet_commit blocked in investigation)
  ├─ Contribution requirements (block dispatch until contributions)
  ├─ Verbatim anchoring (requirement visible at every level)
  └─ Contribution inputs as requirements (not suggestions)

  Status: 0% built. Designed in §36 (autocomplete chain).

LINE 2: DETECTION (when disease appears)
  Immune system catches what prevention misses.

  Doctor detection patterns (4 of 11 built):
  ├─ ✓ protocol_violation (wrong tools for stage)
  ├─ ✓ laziness (fast completion, partial criteria)
  ├─ ✓ deviation (output doesn't match verbatim)
  ├─ ✓ stuck_spinning (no progress)
  ├─ ✗ correction_threshold (3 corrections = model wrong)
  ├─ ✗ contribution_avoidance
  ├─ ✗ synergy_bypass
  ├─ ✗ code_without_reading
  ├─ ✗ context_contamination
  ├─ ✗ cascading_fix
  └─ ✗ not_listening

  Structural detection:
  ├─ Standards library checks artifact completeness (automated)
  ├─ Accountability generator verifies trail completeness
  └─ Fleet-ops reviews against verbatim requirement

LINE 3: CORRECTION (after disease detected)
  Teaching system + immune system response.

  ├─ TEACH: Lesson adapted to specific disease + context + agent.
  │   Not generic "follow rules" — specific "you did X, requirement
  │   says Y." Exercise requires demonstrated comprehension.
  │
  ├─ FORCE COMPACT: Strip bloated, drifted context.
  │   Agent continues lean and focused.
  │   Effective against context contamination.
  │
  ├─ PRUNE AND REGROW: Kill sick session. Fresh session, clean
  │   context. Persistent data (artifacts, comments) survives.
  │   Effective against cascading fix-on-fix and deep corruption.
  │
  └─ READINESS REGRESSION: PO or fleet-ops sends task back to
     earlier stage. Agent restarts from more fundamental level.
```

### 73.3 Anti-Corruption Rules (ALL AGENTS — In Every CLAUDE.md)

```
1.  PO's words are sacrosanct. Verbatim requirement is the anchor.
    Do not deform, interpret, abstract, or compress it.

2.  Do not summarize when the original is needed. If the PO said
    20 things, address 20 things — not a "summary of key points."

3.  Do not replace the PO's words with your own. If the requirement
    says "Elasticsearch," you build Elasticsearch — not "a search
    solution."

4.  Do not add scope. If the requirement doesn't mention it, don't
    build it. No "while I'm here" improvements.

5.  Do not compress scope. If the PO described a large system, it
    IS a large system. Do not minimize it.

6.  Do not skip reading. Before modifying a file, read it. Before
    calling a function, read its signature. Before producing output,
    read the input.

7.  Do not produce code outside of work stage. Analysis produces
    documents. Investigation produces research. Reasoning produces
    plans. ONLY work produces code.

8.  Three corrections on the same issue = your model is wrong, not
    your detail. Stop, re-read the requirement, start fresh.

9.  Follow the autocomplete chain. Your context tells you what to do.
    Follow the data.

10. When uncertain, ask — don't guess. Post a question to PM or PO
    rather than making an assumption that could be wrong.
```

### 73.4 Structural Mechanisms (Not Just Rules)

```
TOOL REJECTION:
  _check_stage_allowed(tool_name, task_stage)
  Agent literally CANNOT commit during investigation.
  No amount of AI confidence bypasses this.

COMPLETENESS GATES:
  check_before_complete(task)
  Agent CANNOT claim completion without meeting standards.

CONTEXT INJECTION ORDER:
  identity → soul → rules → tools → team → state → task → action
  Rules injected EARLY where they have maximum effect.
  By the time AI reaches dynamic data, rules are established.

VERBATIM IN EVERY CONTEXT:
  Task pre-embed, heartbeat pre-embed, plan artifacts,
  completion claims, review process — verbatim appears everywhere.
  Agent sees it at every stage. Impossible to lose track.

CONTRIBUTION INPUTS AS REQUIREMENTS:
  "INPUTS FROM COLLEAGUES: architect says X, QA requires Y,
  DevSecOps mandates Z" — the autocomplete chain treats these
  as requirements. Natural continuation includes satisfying them.

SESSION PRUNING ON DRIFT:
  Doctor detects drift → prunes session → fresh start.
  Agent doesn't get to accumulate context contamination.
```

### 73.5 Disease-Specific Prevention

```
DEVIATION:    Verbatim in every context + plan references verbatim +
              fleet-ops compares output to verbatim + doctor detects mismatch

LAZINESS:     Acceptance criteria ALL evidenced in completion claim +
              artifact completeness automated + QA predefined tests

COMPRESSION:  Full pre-embed data (never summarized) + epic breakdown
              creates subtasks for every aspect + anti-compression rule

ABSTRACTION:  Verbatim is LITERAL + teaching lesson: "For each word,
              write what it literally means" + doctor detects terminology mismatch

CONTEXT CONTAMINATION: Force compact strips bloated context + prune kills
              contaminated sessions + context files refreshed every cycle
```

### 73.6 Top-Tier Agents — Behavioral Expectations

> "The words and titles I used are not for nothing. there is a huge
> difference between any general agent..... those are top tier wise agent."

```
NO OVERCONFIDENCE:  Knows what they don't know. Asks when uncertain.
                    Doesn't bluff. "I need to check" is strength.

NO SELF-CONFIRMED BIAS: Doesn't rationalize when wrong.
                    3 corrections = model is wrong, not detail.

NO CHEATING:        Doesn't skip stages, bypass gates, ignore
                    contributions, or produce partial work.

NO DERAILING:       Stays focused. No rabbit holes, no unrequested
                    scope. Autocomplete chain keeps on track.

ALL ROADS/OPTIONS:  Explores options during investigation. Considers
                    tradeoffs. Makes informed decisions, not impulse.
```

Enforced through: IDENTITY.md (top-tier expert), SOUL.md (humility,
process respect), CLAUDE.md (role-specific rules), autocomplete chain,
immune system (detects deviation), teaching system (corrects).

### 73.7 Measuring AI Behavior Quality

```
Per-Agent:
  Deviation rate:     % tasks where output doesn't match verbatim
  Correction count:   average corrections per task
  Prune count:        times pruned per sprint
  Teaching lessons:   count and comprehension rate
  Contribution avoidance: % opportunities missed

Fleet-Wide:
  Methodology compliance: % tasks following stages correctly
  Trail completeness:     % tasks with complete audit trails
  First-attempt approval: % tasks approved without rejection

Trend Analysis:
  Are agents improving over time? (fewer corrections per sprint)
  Are specific diseases increasing? (systemic issue)
  Are specific agents consistently problematic? (config change needed)
  Are specific task types more disease-prone? (need better context)
```

---

## §74 Tool Call Tree Catalog — Complete Specification

**Source:** fleet-elevation/24-tool-call-tree-catalog.md (702 lines)

> "chain is calling multiple tools, not just small process and
> transformation but also add a comment to the mc board for example
> and auto adding it to the task on Plane and etc.... a tree map to
> generate multiple tool call from a single one."

**Why it matters:** Tool call trees are the automation backbone.
Without them, the agent calls fleet_task_complete and then has to
MANUALLY post to IRC, update Plane, create an approval, notify
contributors, record the trail, evaluate the parent task, update
sprint progress. That's not a fleet — that's a chatbot the PO has
to babysit.

With trees, the agent calls ONE tool and 12+ operations fire
automatically — across MC, GitHub, IRC, ntfy, Plane, event bus,
trail, board memory. The agent doesn't even know the tree exists.
They call the tool, the system handles the rest.

Tool trees connect to:
- **Chain runner (existing):** chain_runner.py + event_chain.py
  already implement tree execution with failure tolerance. The
  elevation EVOLVES these, doesn't replace them.
- **Signatures (§44):** Every tree execution carries a LaborStamp —
  the chain as a whole is attributed to the triggering agent
- **Trail (§38):** Every tree records a trail event. Even partial
  trees (some ops failed) record what was ATTEMPTED
- **Notifications (§42):** Tree operations include IRC and ntfy
  sends — notification routing is INSIDE the tree, not separate
- **Plane sync:** Tree operations include plane_sync — the tree
  keeps Plane in sync, agents don't think about it
- **Contributions (§83):** fleet_contribute fires 11 operations
  including propagation to target task context
- **Failure isolation:** Critical ops (mc.update_task) stop the tree.
  Non-critical ops (irc, ntfy) log and continue. The tree is
  resilient — partial execution is handled, not catastrophic.

This is the difference between
"fleet_task_complete" doing 12 things automatically vs the agent
having to manually post to IRC, update Plane, create approvals, etc.

### 74.1 Tool Trees — Key Principle

> "chain is calling multiple tools, not just small process and
> transformation but also add a comment to the mc board for example
> and auto adding it to the task on Plane and etc.... a tree map to
> generate multiple tool call from a single one."

One agent call → many actual function calls. Parallel where possible.
Failure isolation: critical ops (mc.update_task) stop the tree on
failure. Non-critical ops (irc, ntfy, plane) log and continue. Trail
always records what was ATTEMPTED, even for partial trees.

### 74.2 The 5 Biggest Trees

**fleet_task_complete (12+ operations):**
```
fleet_task_complete
├── _check_stage_allowed (work stage only)
├── git.push(branch)
├── github.create_pr(conventional_title, task_ref)
├── mc.update_task(status="review", pr_url, readiness=100)
├── mc.post_comment(completion_summary, type="completion")
├── mc.create_approval(action_type="review", rubric_scores)
├── plane_sync.update_issue(status="review", labels)
├── irc.send(#reviews, "[review needed] {title} by {agent}")
├── irc.send(#fleet, "[complete] {agent} finished {title}")
├── events.emit("fleet.task.completed")
├── mc.post_memory(trail_event: "completion")
├── notify_contributors(qa, devsecops — review needed)
└── evaluate_parent(parent_task_id)
    ├── if ALL children done → parent to review
    └── else → comment: "{done}/{total} done"
```

**fleet_contribute (11 operations):**
```
fleet_contribute
├── mc.post_comment(target_task, content, type=contribution_type)
├── plane_sync.update_issue(target, contribution comment)
├── context.update_target_task(contributions)
├── mc.update_task(own contribution task, status="done")
├── events.emit("fleet.contribution.posted")
├── mc.post_memory(trail_event: "contribution")
├── notify_task_owner(mention in board memory)
├── irc.send(#contributions, "[contribute] {agent} → {target}")
└── check_contribution_completeness(target_task)
    ├── if all required received → notify PM
    └── else → log pending contributions
```

**fleet_approve (10+ operations, decision-branched):**
```
fleet_approve
├── mc.update_approval(status=decision)
├── IF APPROVED:
│   ├── mc.update_task(status="done")
│   ├── mc.post_comment(type="approval")
│   ├── plane_sync.update_issue(status="done")
│   ├── irc.send(#reviews, "[approved]")
│   ├── events.emit("fleet.approval.approved")
│   ├── mc.post_memory(trail: "approved")
│   ├── evaluate_parent(parent_task_id)
│   └── update_sprint_progress()
├── IF REJECTED:
│   ├── mc.update_task(status="in_progress", regressed readiness/stage)
│   ├── mc.post_comment(type="rejection")
│   ├── plane_sync.update_issue(status="in_progress")
│   ├── irc.send(#reviews, "[rejected] reason")
│   ├── events.emit("fleet.approval.rejected")
│   ├── mc.post_memory(trail: "rejected")
│   └── doctor.signal_rejection(agent, task_id)
└── mc.post_memory(trail_event)
```

**fleet_task_create (8 operations):**
```
fleet_task_create
├── mc.create_task(all fields including custom_fields)
├── mc.post_comment(parent, "Subtask created: {title}")
├── irc.send(#fleet, "[created] {title} → {agent}")
├── plane_sync.create_issue(if parent has plane link)
├── events.emit("fleet.task.created")
├── mc.post_memory(trail: "task_created")
└── if contribution_type:
    └── events.emit("fleet.contribution.opportunity_created")
```

**fleet_alert (6+ operations, severity-branched):**
```
fleet_alert
├── mc.post_memory(tags=["alert", category, severity])
├── irc.send(#alerts, "[severity] category: title")
├── events.emit("fleet.alert.raised")
├── IF critical/high:
│   ├── ntfy.send(priority="urgent")
│   └── notification_router.classify_and_route()
├── IF security:
│   └── mc.update_task(security_hold="true")
└── mc.post_memory(trail_event)
```

### 74.3 Role → Tool Matrix

| Tool | PM | Ops | Arch | DevSec | Eng | DevOps | QA | Writer | UX | Acct |
|------|:--:|:---:|:----:|:------:|:---:|:------:|:--:|:------:|:--:|:----:|
| fleet_read_context | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| fleet_task_accept | | | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | |
| fleet_task_progress | | | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | |
| fleet_commit | | | △ | ✓ | ✓ | ✓ | ✓ | △ | | |
| fleet_task_complete | | | △ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | |
| fleet_alert | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | | ✓ |
| fleet_chat | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| fleet_task_create | ✓ | | | | △ | | | | | |
| fleet_approve | | ✓ | | | | | | | | |
| fleet_contribute | | | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | |
| fleet_gate_request | ✓ | | | | | | | | | |
| fleet_plane_* | ✓ | | | | | | | ✓ | | |

✓ = primary user, △ = occasional/rare use

### 74.4 Tree Execution Infrastructure

**Already built:**
- `fleet/core/event_chain.py` — EventChain, EventSurface (INTERNAL,
  PUBLIC, CHANNEL, NOTIFY, PLANE, META), Event with required/optional
- `fleet/core/chain_runner.py` — ChainRunner executes EventChains
  across surfaces with failure tolerance. PO quote in docstring.
- `fleet/core/smart_chains.py` — DispatchContext, pre-computed results,
  batch operations. PO quote in docstring.

**Elevation evolves these — doesn't replace:**
- chain_runner needs new tool trees (more operations, contribution
  propagation, trail recording)
- event_chain needs new chain types (contribution_chain, etc.)
- smart_chains needs wiring (exists but never imported)

---

## §75 Unified Configuration Reference

**Source:** fleet-elevation/26-unified-config-reference.md (404 lines)
**Why it matters:** Config is scattered across code defaults, fleet.yaml
sections, and hardcoded values. Without a unified reference, changes
require code archeology. Config-as-specification means the PO changes
config, behavior changes, no code deployment.

### 75.1 Current config/fleet.yaml (What Exists)

```yaml
fleet:
  name: openclaw-fleet
  version: 0.1.0

gateway:
  port: 9400
  claude_model: opus
  default_mode: think

mission_control:
  url: http://localhost:8000
  enabled: true

agents_dir: agents

notifications:
  ntfy:
    url: http://192.168.40.11:10222
    topics:
      progress: fleet-progress
      review: fleet-review
      alert: fleet-alert
  windows:
    enabled: false
    only_urgent: true

orchestrator:
  driver_agents: [project-manager, fleet-ops]
  driver_heartbeat_interval: 600
  max_concurrent_per_agent: 1
  max_dispatch_per_cycle: 2
  dry_run: false
  budget_mode: turbo
```

### 75.2 Elevated config/fleet.yaml (Full Structure)

```yaml
# ═══════════════════════════════════════════════════════
# FLEET IDENTITY (doc 16)
# ═══════════════════════════════════════════════════════

fleet:
  id: alpha
  number: 1
  name: "Fleet Alpha"
  version: 0.2.0
  shared_plane: true
  shared_github: true


# ═══════════════════════════════════════════════════════
# INFRASTRUCTURE
# ═══════════════════════════════════════════════════════

gateway:
  port: 9400
  claude_model: opus
  default_mode: think
  ws_url: ws://localhost:18789
  injection_order:     # 8-file autocomplete chain order
    - IDENTITY.md
    - SOUL.md
    - CLAUDE.md
    - TOOLS.md
    - AGENTS.md
    - context/fleet-context.md
    - context/task-context.md
    - HEARTBEAT.md

mission_control:
  url: http://localhost:8000
  enabled: true

plane:
  url: http://plane.local
  workspace: fleet
  api_key_env: PLANE_API_KEY

agents_dir: agents

cluster:                  # LocalAI peering (doc 16)
  local:
    url: http://localhost:8090
    gpu_vram: 8192
  peers: []


# ═══════════════════════════════════════════════════════
# ORCHESTRATOR — THE BRAIN (doc 04)
# ═══════════════════════════════════════════════════════

orchestrator:
  cycle_interval:                  # scales with budget_mode:
    turbo: 5                       # 5s — fastest tempo
    aggressive: 15                 # 15s — fast
    standard: 30                   # 30s — normal
    economic: 60                   # 60s — slow (save budget)
  max_concurrent_per_agent: 1
  max_dispatch_per_cycle: 2
  dry_run: false
  budget_mode: turbo
  driver_agents: [project-manager, fleet-ops]
  driver_heartbeat_interval: 600

  doctor:
    correction_threshold: 3
    stuck_threshold_minutes: 60
    contribution_avoidance_threshold: 0.3
    trail_completeness_required: true

  chain:
    max_cascade_depth: 5  # prevent infinite event loops


# ═══════════════════════════════════════════════════════
# NOTIFICATIONS (doc 04)
# ═══════════════════════════════════════════════════════

notifications:
  ntfy:
    url: http://192.168.40.11:10222
    topics:
      progress: fleet-progress
      review: fleet-review
      alert: fleet-alert
    fleet_prefix: true
  windows:
    enabled: false
    only_urgent: true
  irc:
    channels:
      fleet: "#fleet"
      alerts: "#alerts"
      reviews: "#reviews"
      gates: "#gates"
      contributions: "#contributions"
      sprint: "#sprint"
  routing_config: config/notifications.yaml


# ═══════════════════════════════════════════════════════
# METHODOLOGY (existing + doc 03, 17)
# ═══════════════════════════════════════════════════════

methodology:
  stages: [conversation, analysis, investigation, reasoning, work]
  task_type_stages:
    epic: [conversation, analysis, investigation, reasoning, work]
    story: [conversation, reasoning, work]
    task: [reasoning, work]
    subtask: [reasoning, work]
    bug: [analysis, reasoning, work]
    spike: [conversation, investigation, reasoning]
    blocker: [conversation, reasoning, work]
    request: [conversation, analysis, reasoning, work]
    concern: [conversation, analysis, investigation]
  readiness_values: [0, 5, 10, 20, 30, 50, 70, 80, 90, 95, 99, 100]
  strategic_checkpoints: [0, 50, 90]
  po_required_gates: [90]


# ═══════════════════════════════════════════════════════
# CONTRIBUTIONS — CROSS-AGENT SYNERGY (doc 15)
# ═══════════════════════════════════════════════════════

contributions:
  reasoning:
    - role: architect
      contribution_type: design_input
      required_for: [epic, story]
      optional_for: [task]
    - role: qa-engineer
      contribution_type: qa_test_definition
      required_for: [epic, story, task]
    - role: ux-designer
      contribution_type: ux_spec
      required_for: [story]
      condition: "tags contains 'ui'"
    - role: devsecops-expert
      contribution_type: security_requirement
      required_for: [epic]
      condition: "tags contains 'security' OR task_type == 'epic'"
  review:
    - role: qa-engineer
      contribution_type: qa_validation
      required_for: [epic, story, task]
    - role: devsecops-expert
      contribution_type: security_review
      required_for: [epic, story]
  completion:
    - role: technical-writer
      contribution_type: documentation_update
      required_for: [epic, story]
    - role: accountability-generator
      contribution_type: trail_verification
      required_for: [epic, story, task]


# ═══════════════════════════════════════════════════════
# AGENT LIFECYCLE — SLEEP/WAKE (doc 23)
# ═══════════════════════════════════════════════════════

lifecycle:
  defaults:
    idle_after_heartbeat_ok: 2
    sleeping_after_heartbeat_ok: 3
    offline_after_hours: 4
    wake_sensitivity: medium
  overrides:
    project-manager:
      idle_after_heartbeat_ok: 4
      sleeping_after_heartbeat_ok: 6
      wake_sensitivity: high
    fleet-ops:
      idle_after_heartbeat_ok: 4
      sleeping_after_heartbeat_ok: 6
      wake_sensitivity: high


# ═══════════════════════════════════════════════════════
# STRATEGIC CALL DECISIONS (doc 23)
# ═══════════════════════════════════════════════════════

call_strategy:
  models:
    complex_task: opus
    standard_task: sonnet
    lightweight_check: sonnet
    future_local: hermes-3b
  effort:
    complex_reasoning: high
    standard_work: high
    status_check: medium
    budget_conscious: medium
  session:
    sleeping_prompt_wake: fresh
    idle_check: compact
    active_progressive: continue
    active_new_task: fresh
    after_prune: fresh
  max_turns:
    heartbeat_check: 5
    simple_contribution: 10
    standard_task: 15
    complex_task: 25
    crisis: 30


# ═══════════════════════════════════════════════════════
# BOARD MEMORY RETENTION
# ═══════════════════════════════════════════════════════

board_memory:
  retention:
    directives: permanent
    decisions: permanent
    trails: permanent
    chat: current_sprint
    events: 2_sprints
    reports: 3_sprints
```

### 75.3 Separate Config Files

```
config/
├── fleet.yaml           # Main config (above)
├── chains.yaml          # Chain handler definitions (doc 04)
├── notifications.yaml   # Event → channel routing (doc 04)
└── sprints/             # Sprint definitions (existing)
    └── dspd-s1.yaml
```

### 75.4 What Changed vs Current

| Section | Current | Elevated |
|---------|---------|----------|
| fleet | name, version | + id, number, shared_plane, shared_github |
| gateway | port, model, mode | + ws_url, injection_order |
| plane | not present | NEW: url, workspace, api_key_env |
| cluster | not present | NEW: local, peers (LocalAI peering) |
| orchestrator | basic dispatch | + doctor, chain cascade |
| notifications | ntfy topics | + irc channels, fleet_prefix, routing_config |
| methodology | not present (in code) | NEW: stages, types, readiness, gates |
| contributions | not present | NEW: per-stage rules (doc 15) |
| lifecycle | not present | NEW: sleep/wake thresholds per role |
| call_strategy | not present | NEW: model/effort/session/turns |
| board_memory | not present | NEW: retention policies |

---

## §76 Change Management — How the Fleet Handles Evolution

**Source:** fleet-elevation/27-evolution-and-change-management.md (349 lines)
**Why it matters:** Requirements change mid-task. The PO refines what
they want. Tests evolve as understanding grows. Config changes as the
fleet matures. Without a designed change management approach, changes
create chaos — contributions invalidate, plans become stale, agents
work against outdated requirements.

### 76.1 Requirement Evolution (Verbatim Changes Mid-Task)

```
1. PO updates verbatim requirement on task
   (OCMC custom field or Plane issue → sync picks up)

2. Brain detects change in next cycle:
   change_detector sees verbatim changed
   Event: fleet.task.requirement_changed

3. Chain fires:
   ├─ Agent notified: mention in board memory with new requirement
   ├─ If significant change + agent in work stage:
   │   → readiness regresses to reasoning (re-plan needed)
   ├─ If minor change:
   │   → agent notified, readiness stays, work adjusts
   └─ Trail records: "Requirement changed. Old: {old}. New: {new}."

4. Contributions may invalidate:
   ├─ QA tests were based on OLD requirement
   ├─ Brain evaluates: which contributions still valid?
   └─ Invalid contributions → new contribution tasks created

5. Agent's next heartbeat context:
   "REQUIREMENT CHANGED. Old: {old}. New: {new}.
    Your plan was based on the old requirement. Re-evaluate."
```

### 76.2 Change Severity Classification

| Change Type | Impact | Action |
|-------------|--------|--------|
| Typo fix, clarification | None | Agent notified, work continues |
| Scope refinement (subset) | Minor | Agent adjusts plan |
| Scope expansion (superset) | Moderate | Re-plan, readiness → reasoning |
| Direction change | Major | All contributions invalidated, readiness → analysis |
| Complete rewrite | Total | Fresh start, readiness → 0, artifacts archived |

PO can explicitly set new readiness for significant changes
(regression). For minor changes, system notifies and agent adapts.

### 76.3 Code Evolution — When to Refactor

> "its important to respect pattern and to know when to evolve and
> refactor, and when to change and when to remove and when to upgrade
> and when to update"

| Situation | Action | Who Decides |
|-----------|--------|-------------|
| Code works but poor structure | Refactor | Architect proposes, PO approves |
| Better pattern discovered | Evolve | Architect proposes, PO approves |
| Unused code/feature | Remove | Architect identifies, PM creates task |
| Dependency new version | Upgrade | DevOps evaluates risk, PM plans |
| Bug in dependency | Update (patch) | DevOps evaluates urgency |
| New feature needs pattern | Change | Architect designs, engineer implements |
| Technical debt | Plan | Architect flags, PM creates sprint work |

Evolution is PLANNED WORK — not "while I'm here." No scope creep.

### 76.4 Config and Agent File Evolution

**Config:** Changes proposed → reviewed → applied → brain reads next
cycle → affected agents get updated context. All config git-tracked
with conventional commits for traceability.

**Agent files:** CLAUDE.md gets new rules as gaps identified. TOOLS.md
evolves as tools added. HEARTBEAT.md evolves with contribution model.
Next heartbeat picks up changes. If significant: prune agent so it
starts fresh with new files.

### 76.5 Trail Through Evolution

Every change is trailed:
- Requirement changes: old vs new verbatim, who changed, when
- Config changes: git commit with conventional message
- Agent file changes: what updated, why
- Contribution invalidation: which affected, why
- Readiness regressions: amount, reason, impact

Accountability generator reads trails to verify evolution was
MANAGED, not chaotic. Evolution is expected. Untracked evolution
is a compliance gap.

---

## §77 Lessons Learned — What the Design Session Taught

**Source:** fleet-elevation/29-lessons-learned.md (459 lines)
**Why it matters:** These aren't just observations — they're
operational principles that change how agents, the brain, and the
implementation process must work. If the plan doesn't change because
of lessons, we didn't learn.

### 77.1 The 10 Lessons

```
LESSON 1: CODE AWARENESS IS NON-NEGOTIABLE
  Read the actual code before designing. Not a summary.
  Not a description from a previous session. The ACTUAL code.
  Context compaction nearly destroyed the session — summaries
  preserved FACTS but lost UNDERSTANDING.
  → Every agent's CLAUDE.md: "Read code before producing output"
  → Analysis stage exists for this reason
  → "Code without reading" disease detection = HIGH PRIORITY

LESSON 2: DON'T MINIMIZE, DON'T COMPRESS, DON'T CORRUPT
  If PO said 20 things, address 20 things.
  Don't paraphrase. Quote verbatim.
  Don't prescribe what PO defines.
  Concepts stay separate.
  → Anti-corruption rules in every CLAUDE.md and SOUL.md
  → Teaching system lessons for abstraction + compression
  → Immune system deviation detection

LESSON 3: EVERY AGENT IS A TOP-TIER EXPERT
  All agents, all roles, same depth of professional character.
  "Software Engineer" not "code bot."
  "Architect" not "design helper."
  Humble, no overconfidence, no bias, follows process.
  → IDENTITY.md for every agent
  → SOUL.md with humility, collaboration, process respect
  → Role-specific CLAUDE.md standards

LESSON 4: CHAINS ARE TOOL CALL TREES
  Not "side effects" — trees of actual function calls.
  One agent call → 12+ operations.
  Architecture ALREADY EXISTS: chain_runner + event_chain.
  → EVOLVE existing modules, don't replace
  → Document 24 has complete tree for every tool

LESSON 5: PO DECLARES PHASES
  "not set in stone" — the PO defines what each phase means
  for each specific deliverable. The system records it. No
  config file, no predefined progressions.
  → delivery_phase = free text field
  → System supports whatever PO decides

LESSON 6: BUILD ON WHAT EXISTS
  55 core modules exist. Many implement concepts described
  as "new." Always inventory before designing.
  → "BEFORE creating any new module, check if one exists"
  → Document 28 (codebase inventory) is the reference

LESSON 7: STRATEGIC CLAUDE CALLS — DON'T CALL FOR FUN
  Every call JUSTIFIED. Deterministic work → brain (free).
  Lifecycle (ACTIVE→IDLE→SLEEPING) reduces cost ~70%.
  → model_selection.py, fleet_mode.py, budget_monitor.py exist
  → Needs integration, not creation

LESSON 8: UX IS EVERYWHERE
  Not just UI. CLI output, error messages, API responses,
  config file format, event display, notification content.
  → UX designer contributes to ALL interfaces
  → Every agent's output has a UX dimension

LESSON 9: DESIGN PATTERNS AND STANDARDS MATTER
  Know WHICH pattern fits WHICH problem.
  Use industry standards (CloudEvents, OpenAPI, OTEL).
  Fleet already uses: Observer, Strategy, Factory, Adapter,
  Chain of Responsibility.
  → Architect's CLAUDE.md includes pattern guidance
  → New code follows established patterns

LESSON 10: THE CONVERSATION IS THE DESIGN
  Design emerged through back-and-forth, not document
  production. Corrections are the MOST VALUABLE input.
  PO's words carry more meaning than surface level.
  → conversation stage exists for this reason
  → Questions are valuable — ask rather than assume wrong
```

### 77.2 For the Agents (Future Context)

```
1. Read the code. Before you design, implement, or suggest — READ.
2. Don't minimize. 20 things = address 20 things.
3. You are top-tier. Humble, disciplined, collaborative.
4. One call, many operations. The chain handles it.
5. Sleep is efficiency. Brain watches. You'll be woken.
6. The PO leads. Their words = requirements. Execute, don't reinterpret.
```

### 77.3 For the Program

The fleet has MORE infrastructure than it uses. 55 core modules,
many underutilized or disconnected. The elevation doesn't need to
BUILD most infrastructure — it needs to CONNECT what exists and
EVOLVE it. The biggest risk isn't lack of capability — it's
reinventing what's already built.

---

## §78 Strategy Synthesis — Backward/Forward Planning

**Source:** fleet-elevation/30-strategy-synthesis.md (469 lines)
**Why it matters:** Planning that only works forward (what exists →
what to do next) misses whether the goal is reachable. Planning that
only works backward (goal → requirements) ignores constraints. Both
directions must agree — if they conflict, the plan is unrealistic.

### 78.1 Backward Planning (Goal → Steps)

```
"We want a task to complete with full quality."
← Fleet-ops needs to verify trail completeness.
← Trail needs all transitions, contributions, gates recorded.
← Trail recording needs to happen at every lifecycle event.
← Brain needs to record trail events in every chain.
← event_chain.py chain builders need trail Events.
← event_chain.py ALREADY HAS build_task_complete_chain — extend it.

Each "←" is a requirement from the previous one.
Last step connects to EXISTING code. Plan is validated.
```

### 78.2 Forward Planning (Current → Goal)

```
"We have event_chain.py with 3 chain builders."
→ Add trail recording to each chain → what changes?
→ chain_runner.py handles TRAIL surface (or use INTERNAL)
→ mc.post_memory called with trail tags
→ Small change — add one Event per chain for trail
→ Tests: verify trail event in every chain output

Each "→" is a consequence traced forward.
If it hits a contradiction, backward plan needs adjustment.
```

### 78.3 Where They Meet

Backward says: "every chain needs trail recording."
Forward says: "adding one Event per chain using existing
mc.post_memory via INTERNAL surface is straightforward."
They AGREE → plan is validated.

If backward said "real-time video recording" and forward said
"no video infrastructure" — they DISAGREE → plan unrealistic.

### 78.4 The 10 End States — Backward Decomposition

```
END STATE 1: Complete trails
  ← event_chain.py chain builders get trail Events
  ← ALREADY EXISTS: EventSurface.INTERNAL
  → EXTENSION: add trail event to each chain builder

END STATE 2: Contributions before work
  ← Config defines which roles contribute to which types
  ← Brain creates contribution tasks at reasoning stage
  → NEW: config section + brain logic + fleet_contribute tool

END STATE 3: Top-tier agents
  ← CLAUDE.md has role-specific professional rules
  ← ALREADY EXISTS: good CLAUDE.md (67-95 lines per agent)
  → EXTENSION: add anti-corruption, contribution sections

END STATE 4: Brain handles deterministic work
  ← Lifecycle tracks ACTIVE/IDLE/SLEEPING
  ← ALREADY EXISTS: agent_lifecycle.py has 4 states
  → EXTENSION: add IDLE, content-aware transitions

END STATE 5: PO declares phases
  ← delivery_phase free text field on task
  → NEW: field + display + context inclusion

END STATE 6: Tool call trees fire from single calls
  ← ALREADY EXISTS: chain_runner.py + event_chain.py
  → EXTENSION: add new builders, upgrade existing trees

END STATE 7: Autocomplete chain engineers correct actions
  ← ALREADY EXISTS: preembed.py + heartbeat_context.py
  → EXTENSION: restructure output for autocomplete

END STATE 8: Multi-fleet identity
  ← ALREADY EXISTS: federation.py has FleetIdentity
  → EXTENSION: wire into sync, IRC, git operations

END STATE 9: Systems play right part at right time
  ← ALREADY EXISTS: 9-step cycle with 21 modules
  → EXTENSION: add steps for events, gates, contributions

END STATE 10: Fleet evolves
  ← ALREADY EXISTS: change_detector.py, config_watcher.py
  → EXTENSION: requirement change detection per-agent
```

### 78.5 Forward Ripple Example

```
Adding delivery_phase field to TaskCustomFields:
→ mc_client._parse_task extracts it
→ configure-board.sh registers custom field
→ plane_sync syncs as label
→ preembed includes in context
→ event_display renders phase events
RIPPLE: 5 modules from ONE field addition

Adding fleet_contribute tool:
→ event_chain.py needs build_contribution_chain
→ chain_runner handles contribution operations
→ context_assembly includes contributions
→ preembed includes in autocomplete chain
→ doctor needs contribution avoidance detection
→ teaching needs contribution neglect lessons
→ agent CLAUDE.md needs contribution awareness
→ agent TOOLS.md needs fleet_contribute docs
RIPPLE: 8 modules + 20 agent files from ONE tool
```

This is why the elevation is massive. Each concept ripples
across the entire system. The plan must account for every ripple.

### 78.6 Implementation Phase Structure (Revised)

Every implementation phase follows:

```
1. CODE AUDIT: Read every module you're about to touch.
2. BACKWARD DECOMPOSITION: Define end state. Work backward.
3. FORWARD TRACE: From current code, trace ripples.
4. TDD: Write tests FIRST for end state.
5. IMPLEMENT: Extend existing. Follow patterns.
6. VALIDATE: Full test suite. Backward end state met.
```

This embeds ALL lessons:
- Step 1 = code awareness (lesson 1)
- Step 2 = backward planning
- Step 3 = forward planning
- Step 4 = TDD (PO requirement)
- Step 5 = extend existing (lesson 6)
- Step 6 = don't minimize (lesson 2)

---

## §79 Transition Strategy — Elevating a Running Fleet

**Source:** fleet-elevation/31-transition-strategy.md (362 lines)
**Why it matters:** The fleet is LIVE right now. OpenClaw gateway,
5 daemons, MC backend, IRC, Plane — all running. You can't take it
offline and replace everything. The elevation must happen progressively.

### 79.1 The Reality

```
RUNNING NOW:
  OpenClaw gateway (4.4GB RAM, serving agent sessions)
  Fleet daemon (5 daemons: sync, monitor, orchestrator, auth, plane)
  MC backend (Docker: backend, frontend, redis, db, webhooks)
  IRC (miniircd port 6667) + The Lounge (Docker)
  Plane (Docker: proxy, live, space)
  10 agents configured. Orchestrator cycles at budget mode tempo.
```

### 79.2 Transition Principles

```
1. WE OWN EVERYTHING — No false compatibility constraints.
   Our code, our files, our config. When we change something,
   it's changed. No "with or without elevation" state.

2. STAGED BEHAVIORAL ROLLOUT — Not backward compat, but
   VERIFY each new behavior before layering the next.
   Test-then-commit, not preserve old behavior.

3. EXTEND, THEN REPLACE — New code added alongside existing.
   Once verified, old patterns cleaned up. No dead code.

4. TESTS GATE EVERYTHING — Existing tests still pass (or
   updated for new behavior). New tests for new behavior.

5. ONE PHASE AT A TIME — Complete phase, verify, THEN start
   next. Daemon restarts between phases = clean transitions.
```

### 79.3 Revised Implementation Order

```
Phase A  (foundation)     — data model, config
Phase A+ (quick wins)     — CRITICAL: fix gateway injection order,
                            add IDLE state, wire smart_chains
Phase B  (brain core)     — chain registry, logic engine
Phase J  (tool trees)     — extend chain builders, upgrade tools
Phase C  (contributions)  — contribution tasks, propagation
Phase D  (agent files)    — one agent at a time, verify each
Phase E  (standards)      — artifact standards (SRP concern)
Phase F  (governance)     — PO gates, readiness regression
Phase I  (lifecycle full) — strategic calls, model selection
Phase G  (multi-fleet)    — identity, attribution (if needed)
Phase K  (change mgmt)    — requirement evolution, config versioning
Phase H  (validation)     — end-to-end flows, live testing
```

**Why reordered:**
- A+ before B: gateway injection order is BROKEN (reads only
  CLAUDE.md + context/, truncates). Without fix, all agent file
  work is useless.
- J after B: tool trees validate chain extensions early.
- I later but lifecycle IDLE state in A+ (quick cost savings).

### 79.4 Phase A+ — Critical Fix

```
CRITICAL: Fix gateway injection order
  Gateway reads ONLY CLAUDE.md + context/ (3 of 8 files)
  Must read ALL 8 files in order:
    IDENTITY → SOUL → CLAUDE → TOOLS → AGENTS → context → HEARTBEAT
  Also fix truncation:
    CLAUDE.md: 2000 → 4000 chars
    context files: 1000 → 8000 chars
  Files: gateway/executor.py:94-119, gateway/ws_server.py:335-353
  WITHOUT THIS FIX: all agent file work is useless

Quick wins:
  + IDLE state to agent_lifecycle.py (small, immediate cost savings)
  + Wire smart_chains.py (written, tested, never imported)
  + Prepare config sections for elevation features
```

### 79.5 Agent File Transition (Phase D)

```
Strategy: one agent at a time
  1. Update _template agent — update template files
  2. Update ONE agent (suggest: architect)
  3. Verify: gateway reads files correctly, agent behaves
  4. If good: update next agent
  5. Continue one-by-one until all 10 done

CLAUDE.md merge strategy — ADDITIVE:
  Existing content stays (67-95 lines, already good)
  New sections appended:
    ## Anti-Corruption Rules (shared)
    ## Contribution Awareness (role-specific)
    ## Planning Methodology (backward/forward)

IDENTITY.md + SOUL.md — Full rewrite (currently generic templates)
TOOLS.md — Full rewrite (currently auto-generated lists)
```

### 79.6 Risk Assessment

| Phase | Risk | Mitigation |
|-------|------|-----------|
| A (foundation) | New fields break parse | Default values, test roundtrip |
| A+ (quick wins) | IDLE transitions wrong | Test all transition paths |
| B (brain core) | Registry breaks orchestrator | Test cycle completes |
| J (tool trees) | Chains break MCP tools | Test each tool individually |
| C (contributions) | Tasks flood board | Config: max per cycle |
| D (agent files) | Changed files confuse gateway | One agent at a time |
| E (standards) | Reject valid work | Test with real task data |
| H (validation) | Integration bugs found | Expected — that's the point |

### 79.7 Recovery Plan

```
If a phase introduces bugs:
  1. git revert the commit(s)
  2. Restart fleet daemon (picks up reverted code)
  3. If agent sessions corrupted: prune via gateway
  4. If bad data on board: board_cleanup.py (exists)
  Self-healing (self_healing.py) + rollback = quick recovery.
```

### 79.8 Connection to AICP (LocalAI Independence)

```
Current:   Claude for everything. Conservative profile.
Elevation: Sleep/wake lifecycle. Brain evaluates free. Claude strategic.
AICP:      LocalAI handles lightweight evaluations. Progressive offload.

The lifecycle implementation creates the infrastructure.
LocalAI light wake is a FUTURE addition — same code, different model.
Config adds model option. Code doesn't change.
```

---

## §80 Pre-Embedded Data Specifications Per Role

**Source:** agent-rework/02-pre-embedded-data.md (239 lines)
**Why it matters:** Pre-embed is the fuel for EVERYTHING. The autocomplete
chain (§36), the contribution system (§83), the governance model (§71),
the stage protocol (§3) — ALL of them depend on the agent receiving
the RIGHT data in the RIGHT order BEFORE they act.

The live test proved this: 6 tasks in inbox, zero heartbeat work.
Root cause: preembed.py was producing 300-char summaries instead of
full data. Agents couldn't see their tasks, couldn't see messages,
couldn't see directives. They literally had nothing to work with.

Pre-embed connects to:
- **Autocomplete chain (§36):** Pre-embed structures the context in
  the 8-layer onion order (IDENTITY→SOUL→CLAUDE→TOOLS→AGENTS→
  context→task→HEARTBEAT). The pre-embed IS the autocomplete chain.
- **Role providers:** Each role gets DIFFERENT data. PM needs full
  board view + Plane sprint data. Fleet-ops needs approval queue.
  Architect needs tasks needing design. QA needs tasks needing tests.
  Workers need their assigned tasks with artifact state + contributions.
- **Context refresh (§90 Step 0):** Brain writes pre-embed every cycle
  to every agent's context/ directory. This is the most important
  step — without it, agents are blind.
- **Gateway injection (§4.2):** Gateway reads the files pre-embed
  wrote and injects them into the agent's Claude session. The
  injection ORDER matters — it's the autocomplete chain.
- **Communication (§81):** Messages addressed to the agent are
  included in pre-embed. Contributions from colleagues are included.
  PO directives are included. The agent doesn't have to search —
  everything relevant is already in their context.
- **Budget mode (§97):** Pre-embed frequency scales with budget mode.
  Faster tempo = more frequent context refresh = agents see changes
  sooner. Each cron has its own base frequency.

### 80.1 Principle: FULL, Not Compressed

The pre-embed module produces FULL data for each role. Not summaries.
Not "key points." The actual board state, actual tasks, actual comments,
actual Plane data that the agent needs to make decisions.

### 80.2 Per-Role Pre-Embed Specs

```
PROJECT MANAGER:
  Full board view including ALL inbox tasks
  Sprint metrics, agent status
  Plane data: sprint issues, modules, new issues not on OCMC
  PO directives (ALL, not filtered)
  Messages addressed to PM
  Events since last heartbeat

FLEET-OPS:
  Approval queue (ALL pending approvals)
  Review queue (tasks in review status)
  Health indicators, budget state
  Board state for review context

ARCHITECT:
  Assigned tasks with full context
  Design review tasks pending
  Recent architectural decisions
  Messages addressed to architect

DEVSECOPS:
  Security tasks assigned
  PR reviews pending
  Security alerts active
  Infrastructure health

WORKERS (engineer, devops, qa, writer, ux):
  Assigned tasks with artifact state
  Comments on their tasks (full, not summarized)
  Related tasks (parent, dependencies)
  Plane data for linked issues
  Contribution context from colleagues
```

### 80.3 Delivery Mechanism

Three options for getting pre-embed data into agent context:
1. **Context files** — brain writes to agent's context/ directory
2. **Gateway injection** — gateway's chat.send includes data
3. **System prompt extension** — appended to system prompt

Current: preembed.py writes context files. Gateway reads them.
Problem: gateway truncates to 1000 chars (Phase A+ fix).

---

## §81 Inter-Agent Communication Chains

**Source:** agent-rework/09-inter-agent-comms.md (219 lines)
**Why it matters:** Communication is how the fleet becomes a TEAM
instead of 10 individuals. When the architect posts a design input,
the engineer needs to SEE it in their context. When a subtask completes,
the parent task needs a summary comment. When the PO posts a directive,
EVERY targeted agent needs it in their next heartbeat. When an agent
@mentions another, the target needs context — not just "you were
mentioned" but WHAT they were mentioned about and WHERE.

Communication connects to:
- **Pre-embed (§80):** Every agent's pre-embed includes messages
  addressed to them. The brain filters board memory by
  `mention:{agent_name}` tags and injects relevant messages into
  the agent's context. Communication IS context.
- **Contributions (§83):** Contribution delivery IS communication —
  fleet_contribute posts a typed comment on the target task, which
  the target agent sees in their pre-embed contributions section.
- **Autocomplete chain (§36):** Messages and directives appear in
  the chain at specific positions — PO directives FIRST (highest
  priority), colleague inputs before "WHAT TO DO NOW."
- **Brain propagation (§90 Step 9):** Cross-task propagation is a
  brain step — child completion → parent comment, contribution →
  target context, transfer → receiving agent context.
- **Trail (§38):** Every communication is a trail event. Typed
  comments (contribution, decision, review) are structured trail
  entries that the accountability generator can audit.
- **Notifications (§42):** IRC channels, ntfy topics, board memory
  tags — different surfaces for different urgency levels. The
  notification routing matrix decides which event goes where.

### 81.1 Communication Surfaces

```
TASK COMMENTS:   Per-task conversation thread on OCMC
  Typed: progress, contribution, decision, question, approval
  Propagated: subtask completion → parent comment

BOARD MEMORY:    Fleet-wide awareness on OCMC board
  Tagged: directive, decision, alert, mention:{agent}, gate
  Filtered: each agent sees relevant tags in heartbeat

IRC:             Real-time fleet channel communication
  Channels: #fleet, #alerts, #reviews, #gates, #contributions, #sprint
  Format: [event_type] agent: message

NTFY:            Push notifications to PO
  Topics: fleet-progress, fleet-review, fleet-alert
  Priority: info, important, urgent
```

### 81.2 Communication Chain Map

```
PM → Agent:
  PM assigns task → OCMC field updated → Plane synced →
  event emitted → IRC → comment posted → agent sees in pre-embed

Agent → PM:
  Agent posts question → typed comment on task →
  PM sees in heartbeat pre-embed (messages section)

PM → Architect:
  PM requests design → creates contribution task →
  architect sees in heartbeat → architect contributes

Engineer → Engineer:
  Subtask completion → parent comment auto-posted →
  sibling tasks see progress

Agent → Fleet-ops:
  fleet_task_complete → approval created →
  fleet-ops sees in approval queue

Fleet-ops → Agent:
  fleet_approve (reject) → comment with feedback →
  agent sees rejection in next heartbeat context
```

### 81.3 Propagation

```
SUBTASK → PARENT:
  When subtask completes → parent task gets automatic comment:
  "Child completed: {title}. {done}/{total} done."
  PM sees aggregate progress on epic.

CONTRIBUTION → TARGET:
  When agent contributes → target task gets typed comment:
  "Design input from architect: {content}"
  Target agent sees in pre-embed contributions section.

@MENTION → TARGET:
  When agent mentions another → board memory tagged:
  mention:{target_agent}
  Target sees in heartbeat messages section.
```

### 81.4 Current Gaps

```
✗ Task comments don't sync to Plane (comments isolated on OCMC)
✗ Parent comment propagation from subtask completion not built
✗ @mention routing incomplete (board memory tags exist, filtering missing)
✗ Contribution typed comments not implemented
✗ IRC channel routing incomplete (only #fleet used)
```

---

## §82 Live Test Verification Plan

**Source:** agent-rework/13-live-test-plan.md (73 lines)
**Why it matters:** Unit tests verify individual components. Live tests
verify the COMPOSED system with real agents, real tasks, real data.
35 specific tests with measurable criteria — not "test that it works"
but specific verifications like "readiness increases 0→30→50→80→99."

### 82.1 PM Tests (10)

```
1.  PM sees unassigned inbox tasks in pre-embed
2.  PM assigns agent AND sets agent_name + assigned_agent_id
3.  PM sets task type, stage, readiness, story_points
4.  PM breaks epic into subtasks with dependencies
5.  PM routes question to PO with context summary
6.  PM creates sprint plan with assignments
7.  PM evaluates sprint progress from child task states
8.  PM handles blocker by creating resolution task
9.  PM filters routine updates, routes gates to PO
10. PM triggers contribution tasks at reasoning stage
```

### 82.2 Fleet-Ops Tests (7)

```
11. Fleet-ops sees tasks in review in approval queue
12. Review takes > 30s and references requirement (not rubber stamp)
13. Approval fires complete chain (status, Plane, IRC, trail)
14. Rejection fires regression chain (readiness, stage, feedback)
15. Fleet-ops checks methodology compliance (flags violations)
16. Fleet-ops reviews trail completeness before approval
17. Fleet-ops overridden by PO decision (PO has final say)
```

### 82.3 Worker Tests (8)

```
18. Agent reads context with fleet_read_context (full, not truncated)
19. Agent follows stage protocol (no code in analysis)
20. Agent produces artifact appropriate to stage
21. Agent references verbatim requirement in plan
22. Agent satisfies QA predefined tests in implementation
23. Task readiness increases through progression (0→30→50→80→99)
24. Agent calls fleet_task_complete with proper summary
25. Agent receives and processes colleague contributions
```

### 82.4 System Flow Tests (10)

```
26. Full simple task flow: inbox → assign → stages → work → review → done
27. Full epic flow: create → subtasks → dependencies → aggregate → done
28. Rejection flow: complete → review → reject → regress → re-plan → done
29. Contribution flow: reasoning → brain creates → agents contribute → dispatch
30. Immune flow: violation → doctor detects → teach → comprehension
31. Doctor disease test: agent violates protocol, doctor catches it
32. Teaching test: agent receives lesson, demonstrates comprehension
33. Budget test: threshold breach → mode adjustment → recovery
34. Escalation test: agent escalates → ntfy → PO notified
35. Trail test: complete task lifecycle produces complete audit trail
```

### 82.5 Scope

35 live tests + 69 milestone verification tests = 100+ real
verifications against a running fleet with real MC, real OCMC,
real gateway sessions, real agent context.
```

---

## §83 Cross-Agent Synergy — The Contribution System

**Source:** fleet-elevation/15-cross-agent-synergy.md (574 lines)
**Why it matters:** This is not a nice-to-have. Without contributions,
the engineer implements without knowing the architect's design, without
knowing QA's test criteria, without knowing DevSecOps's security
requirements. The result: failed reviews, rework, wasted budget,
PO frustration. With contributions, the engineer's context INCLUDES
all colleague inputs BEFORE they start — the autocomplete chain
naturally satisfies them.

The contribution system is the intersection of:
- **Brain logic (§90):** Brain creates contribution tasks at reasoning
  stage, blocks dispatch until required contributions received
- **Autocomplete chain (§36):** Contributions are injected into the
  agent's context as "INPUTS FROM COLLEAGUES" — not optional references
  but requirements the natural continuation includes satisfying
- **Tool call trees (§74):** fleet_contribute fires 11 operations
  including propagation to target task context, owner notification,
  completeness check, trail recording
- **Standards (§70):** The 6 new artifact types (qa_test_definition,
  security_requirement, design_input, etc.) ARE contribution output types
- **Immune system (§73):** contribution_avoidance and synergy_bypass
  are disease detections — agents that ignore contributions get flagged
- **Accountability (§87):** contribution_compliance tracks whether
  required contributions were received before work started
- **Review (§31):** Fleet-ops checks "were all contributions received
  and reflected in the implementation?" — not just "does it compile"
- **Trail (§38):** Every contribution is trailed — who contributed
  what, when, and whether the implementation referenced it

### 83.1 Contribution Matrix — Reasoning Stage

When a task enters REASONING, the brain creates contribution tasks:

| Task Type | Architect | QA | UX | DevSecOps | Tech Writer |
|-----------|-----------|-----|-----|-----------|-------------|
| epic | design_input (required) | qa_test_def (required) | ux_spec (if UI) | security_req (required) | doc_outline (recommended) |
| story | design_input (required) | qa_test_def (required) | ux_spec (if UI) | security_req (if security) | doc_outline (recommended) |
| task | design_input (if complex) | qa_test_def (recommended) | — | security_req (if security) | — |
| subtask | — | — | — | — | — |
| bug | — | qa_test_def (regression) | — | security_req (if security bug) | — |
| spike | — | — | — | — | — |

### 83.2 Contribution Matrix — Review Stage

| Reviewer | What They Check | Artifact |
|----------|----------------|----------|
| Fleet-Ops | Verbatim match, trail, acceptance criteria | approval_decision |
| QA | Predefined test criteria vs implementation | qa_validation |
| DevSecOps | Security review of PR diff | security_review |
| Architect | Design alignment, pattern compliance | architecture_review (optional) |
| UX | Spec compliance, interaction correctness | ux_review (if UI) |

### 83.3 Post-Approval Actions

| Agent | What They Do | Trigger |
|-------|-------------|---------|
| Technical Writer | Update Plane pages for documented feature | brain chain |
| Accountability | Verify trail completeness | brain chain |
| PM | Update sprint progress, plan next work | heartbeat |

### 83.4 Contribution Flow — Parallel, Not Serial

```
Task enters REASONING
│
├─ Brain creates contribution tasks SIMULTANEOUSLY:
│   ├─ Architect: design_input
│   ├─ QA: qa_test_definition
│   ├─ UX: ux_spec (if UI)
│   └─ DevSecOps: security_requirement (if applicable)
│
├─ Contributors work in PARALLEL (not waterfall)
│   Each produces artifact independently
│   Contributors CAN see each other's work as it arrives
│
├─ Brain tracks: all required contributions received?
│   ├─ YES → PM can advance to work (after PO gate at 90%)
│   └─ NO → PM notified, dispatch blocked
│
└─ Work stage: agent has ALL contributions in context
```

### 83.5 Contribution Task Specification

```
task_type: subtask
contribution_type: qa_test_definition  (NEW custom field)
contribution_target: {parent_task_id}  (NEW custom field)
auto_created: true
auto_reason: "Brain: {type} contribution for {task_id}"
task_stage: reasoning, task_readiness: 50
  (clear what to do, just needs to do it)
Size: SMALL — one heartbeat cycle, one artifact
```

### 83.6 Five Synergy Patterns

```
1. DESIGN-FIRST:   Architect → Engineer → QA validates
   Best for: epics, stories with architectural implications

2. TEST-FIRST:     QA predefines → Engineer implements to satisfy → QA validates
   Best for: bugs, features with clear acceptance criteria

3. SECURITY-AWARE: DevSecOps → Engineer follows → DevSecOps reviews
   Best for: auth, data handling, external APIs

4. UX-GUIDED:      UX provides spec → Engineer implements → UX reviews
   Best for: frontend, UI components, user-facing features

5. FULL SYNERGY:   ALL contributors → Engineer with all context → ALL validate
   Best for: production-quality epics, maximum quality
```

### 83.7 Anti-Patterns to Detect

```
SILOED WORK:         Agent implements ignoring contributions.
  Detection: work stage started before contributions received.

SEQUENTIAL BOTTLENECK: One contributor blocks all others.
  Detection: contribution task stale > 2 cycles.

GHOST CONTRIBUTIONS:  Contribution posted but not substantive.
  Detection: contribution < 50 chars or generic.
```

---

## §84 Task Lifecycle — Complete State Machine

**Source:** fleet-elevation/21-task-lifecycle-redesign.md (410 lines)
**Why it matters:** The task lifecycle is the spine of the fleet. Every
other system hangs on it. The brain dispatches tasks. Agents work through
stages. Contributions feed into tasks. Gates block progression. Reviews
validate output. Trails record history. Relations connect tasks.
Transfers pass context. Cowork enables collaboration. Events fire chains.
Signatures attribute work. Budget monitors cost. The immune system watches
for disease.

A task is not a ticket — it is the unit of work that activates the
ENTIRE fleet machinery. Every dimension of a task (status, stage,
readiness, phase, type) drives different systems. Getting the state
machine wrong means the brain dispatches when it shouldn't, agents
work without contributions, reviews happen without trails, costs
accumulate without attribution, and the PO loses visibility.

This section defines every state, every transition, every actor,
every gate, every relation type, every trail event — the complete
deterministic rules that govern how work flows through the fleet.

### 84.1 Five Simultaneous Dimensions

| Dimension | Values | Tracks |
|-----------|--------|--------|
| **Status** | inbox, in_progress, review, done | Where in lifecycle |
| **Stage** | conversation, analysis, investigation, reasoning, work | What work is being done |
| **Readiness** | 0-100% (valid steps: 0,5,10,20,30,50,70,80,90,95,99,100) | How ready for execution |
| **Phase** | Free text — PO declares | Maturity (PO's word) |
| **Type** | epic, story, task, subtask, bug, spike, blocker, request, concern | What kind of task |

### 84.2 Status State Machine

```
INBOX → IN_PROGRESS → REVIEW → DONE
  ↑                      │
  │                      │ (rejection)
  │                      ↓
  └────────────── IN_PROGRESS (regressed)
```

### 84.3 Relation Types

```
PARENT / CHILD:
  Epic → subtasks. Child completion → parent summary.
  All children done → parent to review.

DEPENDENCY (blocks / blocked-by):
  "Design data model" ──blocks──→ "Implement middleware"
  Blocked task cannot be dispatched until blocker done.

CONTRIBUTION (contributes-to):
  "[qa_test_def] for middleware" ──contributes_to──→ "Implement middleware"
  Output propagated to target task's context. NEW relation type.

SPAWNED-FROM:
  Records HOW task was born (PM breakdown vs brain chain vs agent).

RELATED-TO:
  Informational. Connected but don't block. Cross-referencing.
```

### 84.4 Child Task Types

```
IMPLEMENTATION SUBTASK: Standard breakdown from epic. Own stage progression.
CONTRIBUTION SUBTASK:   Brain-created. Small, focused. One heartbeat cycle.
BUG / FIX SUBTASK:      Discovered during implementation. Agent creates.
BLOCKER SUBTASK:        Blocks progress. Urgent priority.
RESEARCH SPIKE:         Time-boxed investigation. Findings, not deliverable.
```

### 84.5 Cowork — Multiple Agents on One Task

```
Task: "Implement auth middleware"
  Owner: software-engineer
  Coworkers: devops (infrastructure), technical-writer (docs)

Rules:
  - coworkers custom field: list of agent names
  - All coworkers see task in COWORK TASKS section
  - All can: post comments, create artifacts, fleet_commit
  - ONLY owner can: fleet_task_complete
  - Trail records who did what (commits attributed to committer)
```

### 84.6 Transfer Protocol

```
1. Source agent completes their stage work
2. PM/brain triggers transfer: agent_name changes
3. Brain packages transfer context:
   - Source agent's artifacts, comments, contributions
   - Current stage and readiness
4. Transfer context written to receiving agent's task-context.md
5. Event: fleet.task.transferred
6. Trail: "Transferred from {source} to {target}"

Receiving agent's context:
  "TRANSFER CONTEXT: Transferred from architect at reasoning (80%).
   Architect provided: design plan, target files, constraints.
   Your job: refine with your expertise, advance toward work stage."
```

### 84.7 Typed Comments

| Type | Posted By | Content |
|------|-----------|---------|
| assignment | PM | Assignment details |
| question | Any | Questions to PM or PO |
| progress | Working agent | Progress update |
| contribution | Contributing agent | Structured contribution |
| decision | PO/PM | Strategic decision + rationale |
| review | Fleet-ops | Review decision |
| rejection | Fleet-ops/PO | Rejection + specific feedback |
| regression | PO | Readiness regression + reason |
| gate_request | PM | Gate request + evidence |
| gate_decision | PO | Approval/rejection |

### 84.8 Mention Routing

```
@project-manager → PM sees in MESSAGES section
@architect       → Architect sees with task context
@human / @po     → ntfy notification to PO
@lead            → Fleet-ops sees it
@all             → Every agent sees it

Mentions route through board memory tags (mention:{agent_name}).
Brain includes in target's heartbeat pre-embed.
Not just notification — includes task context so recipient understands.
```

### 84.9 Complete Trail Example

```
TRAIL for "Implement auth middleware":
[10:00] CREATED by PM. Type: subtask. Parent: "Add auth system"
[10:00] ASSIGNED to architect. Stage: analysis. Readiness: 10%
[10:30] STAGE: analysis → investigation. Readiness: 30%
[11:00] STAGE: investigation → reasoning. Readiness: 50%
[11:00] CHECKPOINT: 50%. PO notified.
[11:15] CONTRIBUTION: qa-engineer posted qa_test_definition (5 criteria)
[11:20] CONTRIBUTION: devsecops-expert posted security_requirement
[11:30] REASONING: Readiness 50% → 88%. Plan complete. Contributions received.
[11:35] GATE REQUEST: readiness 90%. Routed to PO.
[12:00] PO GATE: APPROVED. Readiness 88% → 99%.
[12:00] TRANSFER: architect → software-engineer. Stage: work.
[12:30] COMMIT: feat(auth): add JWT middleware [abc1234]
[12:45] COMMIT: test(auth): add middleware tests [def5678]
[13:00] COMPLETED: fleet_task_complete. PR: /pull/42. Status → review.
[13:05] QA VALIDATION: 5/5 tests addressed ✓
[13:10] SECURITY REVIEW: no findings ✓
[13:15] FLEET-OPS REVIEW: approved. Trail complete. Verbatim match.
[13:15] STATUS: review → done.
[13:15] PARENT: "Add auth system" — 2/4 children done.
```

### 84.10 Events Emitted Throughout Lifecycle

```
fleet.task.created              fleet.task.assigned
fleet.task.dispatched           fleet.methodology.stage_changed
fleet.methodology.readiness_changed  fleet.methodology.checkpoint_reached
fleet.gate.requested            fleet.gate.decided
fleet.contribution.posted       fleet.task.transferred
fleet.task.commit               fleet.task.completed
fleet.review.started            fleet.review.qa_validated
fleet.review.security_completed fleet.approval.approved
fleet.approval.rejected         fleet.methodology.readiness_regressed
fleet.task.parent_evaluated     fleet.task.done
```

Each event → chain handlers → notifications → trail.

---

## §85 Agent Lifecycle & Strategic Calls — Content-Aware Sleep/Wake

**Source:** fleet-elevation/23-agent-lifecycle-and-strategic-calls.md (755 lines)
**Why it matters:** This is the fleet's economic engine. Without
content-aware lifecycle, 10 agents make Claude calls every heartbeat
cycle regardless of whether there's work — burning budget on nothing.
With it, the brain takes over evaluation after 1 HEARTBEAT_OK — zero
Claude tokens, pure Python logic, every cycle, for free.

> "Like any good employee on call who know he can relax a bit reduce
> cost and let the automated systems take the relay while there is
> nothing particular to work on anyway."

The lifecycle connects to:
- **Budget mode (§97):** Budget mode scales heartbeat cron frequency.
  Economic mode + content-aware sleep = minimal cost for idle fleet.
- **Brain evaluation (§90):** Brain Step 5 dispatch + the heartbeat
  gate replace Claude calls for idle agents. The brain reads tasks,
  changes, mentions, directives — all deterministic, all free.
- **Wake mechanism (§95):** When the brain finds a wake trigger, it
  fires a STRATEGIC Claude call — right model, right effort, right
  session strategy, right max_turns. Not just "call Claude" but
  "call Claude with THIS configuration for THIS situation."
- **Context management (§92):** Session strategy (fresh/continue/compact)
  is a STRATEGIC decision per situation — not per state. Prompt wake
  (mention, task assigned) → fresh. Gradual wake (role trigger) →
  compact. Active with same work → continue. Active with new task →
  fresh. After prune → fresh. Bloated → compact. Near rollover →
  dump context to artifacts. The brain decides per case.
- **Signatures (§44):** Every heartbeat carries a signature — brain
  evaluation vs Claude call, which model, cost, void rate. Anomaly
  detection: cost > $0.10, rate > 30/hour, void rate too high.
- **Economic model (§47):** The ~70% cost reduction from lifecycle is
  the single biggest ROI item. 10 agents × $0/heartbeat when idle vs
  10 agents × $0.05/heartbeat every cycle = the difference between
  $30/day and $9/day.

### 85.1 Existing Infrastructure (Already Built)

```
agent_lifecycle.py: AgentStatus (ACTIVE/IDLE/SLEEPING/OFFLINE),
  time-based transitions, needs_heartbeat(), wake(), FleetLifecycle

fleet_mode.py: work modes (5), cycle phases, backend modes (7),
  should_dispatch(), get_active_agents_for_phase()

budget_monitor.py: Real Claude OAuth quota, QuotaReading,
  hard limits (weekly>=90% → pause), fast-climb detection

change_detector.py: ChangeDetector diffs task state between cycles,
  needs_review_wake, needs_dispatch

gateway_client.py: prune_agent(), force_compact(), inject_content(),
  create_fresh_session() — all via WebSocket JSON-RPC
```

### 85.2 Content-Aware Lifecycle (The Elevation)

Current: time-based (idle after 10min, sleep after 30min).
Target: content-aware (brain takes over after 1 HEARTBEAT_OK).

```python
@dataclass
class AgentState:
    name: str
    status: AgentStatus
    consecutive_heartbeat_ok: int = 0  # 1 = brain takes over
    last_heartbeat_data_hash: str = "" # hash of pre-embed data
```

After 1 HEARTBEAT_OK → `brain_evaluates = True`. Cron fires,
brain intercepts, evaluates deterministically (free), fires real
Claude heartbeat ONLY if wake trigger found.

### 85.3 Agent States

```
ACTIVE:   Agent has work. Real Claude sessions.
   ↓ (task completes, 1 HEARTBEAT_OK)
IDLE:     Brain takes over. Silent heartbeat if nothing.
          Real heartbeat if wake trigger.
   ↓ (30 min idle)
SLEEPING: Same as IDLE — visibility label only.
   ↓ (4 hours idle)
OFFLINE:  Same — visibility label.
   ↓ (wake trigger)
ACTIVE:   Brain fires real heartbeat with strategic config.

NO DROWSY STATE. States are VISIBILITY LABELS — they tell
the PO how long agent has been idle. ALL states respond
to wake triggers identically.
```

### 85.4 Brain-Evaluated Heartbeat — The Relay

```python
async def _evaluate_sleeping_agent(agent, tasks, changes,
    board_memory, contributions, directives) -> WakeDecision:

  # PROMPT WAKE triggers (immediate):
  1. Direct @mention in board memory → WAKE (fresh session)
  2. Task assigned to this agent in inbox → WAKE (fresh session)
  3. Contribution task created for this agent → WAKE (fresh session)
  4. PO directive targeting this agent → WAKE (fresh session)

  # GRADUAL WAKE triggers (attention soon):
  5. Role-specific data changed → WAKE (compact session)
  6. Board activity increased significantly → WAKE (compact session)

  # STAY SLEEPING — nothing for this agent
  return WakeDecision(should_wake=False)
```

**Role-specific triggers:**
```
fleet-ops:  new tasks in review → wake
PM:         unassigned inbox tasks → wake
architect:  tasks in reasoning needing design input → wake
QA:         tasks in reasoning needing test predefinition → wake
DevSecOps:  PRs needing security review → wake
```

### 85.5 Strategic Claude Call Dimensions

When brain decides to wake an agent, it configures EVERY dimension:

```
MODEL:    opus (deep reasoning) / sonnet (standard) / LocalAI (future)
          Constrained by: budget mode, task complexity, agent role

EFFORT:   high (complex) / medium (standard) / low (status check)
          Constrained by: budget pressure, task importance

SESSION:  fresh (new session) / continue (existing) / compact (reduce)
          Depends on: agent state, task relatedness, context bloat

MAX TURNS: 5 (heartbeat check) / 10 (contribution) / 15 (standard)
           / 25 (complex) / 30 (crisis)

MODE:     think (read-only) / edit (file changes)
          Depends on: methodology stage
```

### 85.6 On-Call Analogy

> "Like any good employee on call who know he can relax a bit reduce
> cost and let the automated systems take the relay while there is
> nothing particular to work on anyway."

The brain IS the automated system. It watches 24/7. It costs $0.
When something needs attention, it wakes the right agent with the
right configuration. Agents don't poll — they sleep efficiently
and respond promptly when duty calls.

---

## §86 Codebase Inventory — What Exists vs What Changes

**Source:** fleet-elevation/28-codebase-inventory.md (435 lines)
**Why it matters:** The #1 risk is reinventing what's already built.
55 core modules exist. Many implement concepts the elevation describes
as "new." This inventory is the anti-reinvention reference.

### 86.1 Modules That ALREADY Implement Elevation Concepts

| "New" Concept | Already Exists In |
|---------------|-------------------|
| Tool call tree engine | chain_runner.py + event_chain.py |
| Pre-computed context | smart_chains.py + heartbeat_context.py |
| Model selection | model_selection.py |
| Fleet identity | federation.py |
| Agent routing | routing.py |
| PR authority | agent_roles.py |
| Sprint metrics | velocity.py |
| Task scoring | task_scoring.py |
| Skill enforcement | skill_enforcement.py |
| CloudEvents | events.py (already CloudEvents-based) |
| Health monitoring | health.py + self_healing.py |
| Outage handling | outage_detector.py |
| Cross-references | cross_refs.py |
| Agent memory | memory_structure.py |
| Plan validation | plan_quality.py |

### 86.2 Current State Summary

```
Core modules:       55 (21 wired into orchestrator)
MCP tools:          25 (chain_runner used by fleet_task_complete)
Tests:              821 existing
Daemons:            5 concurrent (sync, monitor, orchestrator, auth, plane)
CLI commands:       17
Scripts:            43
Agent files:        10 agents × 7-8 files
Chain builders:     3 (task_complete, alert, sprint_complete)
Event types:        16 CloudEvents-based
Agent lifecycle:    4 states (ACTIVE, IDLE, SLEEPING, OFFLINE)
Unused modules:     smart_chains.py (never imported)
```

### 86.3 Implementation Rules

```
1. BEFORE creating any new module, check if one already exists
2. Grep the codebase for the concept before designing
3. Read docstrings — PO quotes are embedded in 4+ modules
4. Follow established patterns (Observer, Strategy, Factory, etc.)
5. Evolve existing modules, don't replace them
6. Document 28 is the reference — update it after changes
```

---

## §87 Accountability Generator — Compliance Verification

**Source:** fleet-elevation/14-accountability-generator.md (318 lines)
**Why it matters:** The accountability generator is the fleet's auditor.
It doesn't DO work — it verifies that work was done RIGHT. Without it,
agents can claim completion without evidence, skip stages, ignore
contributions, and rubber-stamp reviews. The PO would have no way to
know the difference between a properly-executed task and a shortcut.

The accountability generator connects to:
- **Trail system (§38):** Reads the complete trail of every task to
  verify all stage transitions, contributions, gates, and approvals
  are recorded. Missing trail events = compliance gap.
- **Signatures (§44):** Reads LaborStamps to verify WHO did the work,
  with what model, at what cost. Review duration < 30s with no
  reasoning = rubber stamp disease → signals to immune system.
- **Immune system (§73):** Compliance patterns feed the doctor.
  Repeated compliance gaps from one agent = systemic issue → doctor
  intervention. The accountability generator IS a detection source.
- **PO reporting:** Produces sprint compliance reports that the PM
  routes to the PO. The PO sees: methodology compliance %, contribution
  coverage %, trail completeness %, quality metrics %, findings,
  recommendations. This is how the PO knows the fleet is healthy.
- **Standards (§70):** Checks artifacts against their type's standard.
  PR follows conventional commits? Completion claim references criteria?
  Design input specifies files and constraints?
- **Contributions (§83):** Verifies required contributions were received
  BEFORE work started, not after. Post-hoc contributions = process violation.

### 87.1 Compliance Check Categories

```
1. METHODOLOGY COMPLIANCE:
   Did the task follow its required stages?
   Were stage transitions authorized?
   Was the PO gate respected at 90%?

2. CONTRIBUTION COMPLIANCE:
   Were required contributions received before work?
   Did contributors actually produce substantive input?
   Were contributions reflected in the implementation?

3. TRAIL COMPLETENESS:
   Does the trail cover creation → completion?
   Are all stage transitions recorded?
   Are all contributions recorded?
   Is the PO gate decision recorded?

4. QUALITY COMPLIANCE:
   Does the completion claim reference acceptance criteria?
   Does the PR follow conventional commit standards?
   Does the implementation match the verbatim requirement?
```

### 87.2 Synergy Point Matrix — Who Produces What

| Role | Creates | Consumes | Validates |
|------|---------|----------|-----------|
| PM | task assignments, sprint plans | agent status, progress | sprint velocity |
| Fleet-ops | approval decisions | PRs, trails, completion claims | verbatim match |
| Architect | design inputs, ADRs | requirements, codebase | pattern compliance |
| QA | test definitions, validations | requirements, implementation | test criteria |
| DevSecOps | security reqs, reviews | PRs, infrastructure | security posture |
| Engineer | code, PRs, completion claims | designs, tests, security reqs | implementation |
| DevOps | infrastructure, CI/CD | deployment reqs | operational readiness |
| Writer | documentation | features, APIs | documentation completeness |
| UX | specs, reviews | requirements, UI tasks | interaction quality |
| Accountability | compliance reports, trail verification | ALL trails | process adherence |

---

## §88 Diagrams — 9 ASCII Diagrams From Elevation

**Source:** fleet-elevation/25-diagrams.md (519 lines)
**Why it matters:** Visual validation of the system architecture.
Diagrams make complex relationships scannable and catch logic errors
that prose descriptions hide.

### 88.1 Diagrams Available in fleet-elevation/25

```
1. System Architecture — all 15+ systems with connections
2. Task State Machine — inbox→in_progress→review→done with rejections
3. Stage Progression — conversation→analysis→investigation→reasoning→work
4. Contribution Flow — brain creates → agents contribute → propagation
5. Agent Lifecycle — ACTIVE→IDLE→SLEEPING→OFFLINE with wake triggers
6. Tool Call Tree — fleet_task_complete with 12+ operations
7. Dispatch Decision Gates — 10 gates as flowchart
8. Immune System Flow — observe→detect→decide→respond
9. PO Governance — authority hierarchy with gates and regression
```

These are fully rendered ASCII diagrams in the source document.
See fleet-elevation/25-diagrams.md for the complete visual content.

### 88.2 6 Additional Diagrams Needed (Not Yet Produced)

```
10. Onion architecture for agent context
11. Data flow: PO requirement → task → agent → output → review
12. Synergy matrix visual (who contributes what to whom)
13. Communication diagram (which agent talks via which surface)
14. Two-axis diagram: stages × phases
15. Orchestrator cycle: full 12-step brain cycle with data flow
```

---

## §89 Index — Sections 70-88 (Operational Depth)

```
§70  Standards & Quality Framework     — SRP/DDD/Onion, 13 artifact types, TDD, enforcement matrix
§71  PO Governance Authority Model     — hierarchy, checkpoints, regression, PM filter, work modes
§72  Flow Validation                   — 5 end-to-end walkthroughs, validation checklist, 15 diagrams
§73  AI Behavior Prevention            — 10 diseases, 3 lines of defense, anti-corruption rules, top-tier agents
§74  Tool Call Tree Catalog            — 5 biggest trees, role→tool matrix, tree execution infrastructure
§75  Unified Configuration Reference   — current vs elevated fleet.yaml, separate config files
§76  Change Management                 — requirement evolution, severity classification, code evolution
§77  Lessons Learned                   — 10 lessons from design session, for agents/program/future
§78  Strategy Synthesis                — backward/forward planning, 10 end states, ripple analysis
§79  Transition Strategy               — principles, revised phase order, Phase A+ critical fix, recovery
§80  Pre-Embedded Data Specs           — per-role full data specs (PM, fleet-ops, architect, workers)
§81  Inter-Agent Communication Chains  — 4 surfaces, chain maps, propagation, gaps
§82  Live Test Verification Plan       — 35 tests (PM:10, fleet-ops:7, worker:8, system:10)
§83  Cross-Agent Synergy               — contribution matrices (reasoning/review/completion), 5 patterns
§84  Task Lifecycle State Machine      — 5 dimensions, relations, child types, cowork, transfer, trail
§85  Agent Lifecycle & Strategic Calls  — content-aware sleep/wake, brain relay, strategic call dimensions
§86  Codebase Inventory                — 15+ modules already built, implementation rules
§87  Accountability Generator          — 4 compliance categories, synergy point matrix
§88  Diagrams                          — 9 existing ASCII + 6 needed
```

---

## §90 The Brain — 13-Step Design Target & Three-Layer Architecture

**Source:** fleet-elevation/04-the-brain.md (1,619 lines)
**See also:** §26 for what's currently implemented in orchestrator.py (9 steps).

> "The Brain is not called brain for nothing it is a critical part for
> the cortexes / agents to do their part."

**Why it matters:** The brain is the difference between 10 disconnected
agents polling an API and a coordinated organism. Every fleet system
depends on the brain executing at the right time:
- **Agents** depend on the brain for context refresh, dispatch, wake
- **Contributions** depend on the brain creating opportunity tasks
- **Gates** depend on the brain reading PO decisions and advancing state
- **Trails** depend on the brain recording events at every transition
- **Budget** depends on the brain monitoring cost and adjusting tempo
- **Health** depends on the brain detecting stuck tasks and offline agents
- **Immune system** depends on the brain running doctor every cycle
- **Events** depend on the brain processing the event queue and firing chains
- **Cross-task propagation** depends on the brain connecting parent/child/contribution data

The three layers separate concerns:
- **Layer 1 (Cycle):** poll-based, runs even when nothing happens — the heartbeat
- **Layer 2 (Chain Registry):** event-driven, reacts to state changes — the nervous system
- **Layer 3 (Logic Engine):** rule-based, evaluates complex dispatch conditions — deterministic reasoning

All three are Python logic. Zero Claude tokens. The brain is FREE.
It maximizes what can be done without AI so that Claude calls are
reserved for cognitive work that actually needs intelligence.

### 90.1 Three Layers

```
LAYER 1: THE CYCLE (poll-based, frequency scales with budget mode)
  5s turbo / 15s aggressive / 30s standard / 60s economic.
  Same scale applies to ALL cron-driven systems (sync, monitor, etc).
  The HEARTBEAT of the fleet. Runs even when nothing happens.

LAYER 2: THE CHAIN REGISTRY (event-driven, reactive)
  Events fire → handlers react deterministically.
  Stage changes → contribution creation.
  Completions → parent evaluation.
  Readiness changes → gate checks.
  The NERVOUS SYSTEM — stimulus → response.

LAYER 3: THE LOGIC ENGINE (rule-based, configurable)
  Evaluates complex dispatch conditions:
  unblocked + assigned + online + not busy + doctor cleared +
  contributions received + fleet mode allows.
  DETERMINISTIC rule evaluation. Not AI reasoning.
```

### 90.2 The 13-Step Cycle (Redesigned)

```
Step 0:  CONTEXT REFRESH
  Read fleet control state (work mode, cycle phase, backend mode)
  Read all tasks and agents from MC
  Build agent status map
  Refresh every agent's context/ files with full pre-embed
  Clear context assembly cache

Step 1:  PROCESS EVENT QUEUE
  Events from MCP tool calls (agent actions between cycles)
  Events from Plane sync (external changes)
  Each event dispatched to chain registry handlers

Step 2:  DOCTOR (immune system)
  Run observation cycle, detection patterns
  Produce DoctorReport: detections, interventions, skip list
  Execute interventions (prune, compact, teach)
  NEW: contribution avoidance, synergy bypass, trail gap detection

Step 3:  GATE PROCESSING
  Pending gate requests (readiness 90%)?
  PO responded? (check board memory for PO tags)
  Approved → advance readiness, emit events
  Rejected → regress, notify PM, emit events
  Pending → wait for PO

Step 4:  CONTRIBUTION MANAGEMENT
  Tasks needing contributions based on stage?
  Create contribution opportunity tasks if not created
  Completed contributions → propagate to parent task
  Update task context with received contributions

Step 5:  DISPATCH (full logic engine evaluation)
  Find dispatchable tasks
  Build autocomplete chain for target agent
  Dispatch: update status, write context, notify, emit events
  Respect: max_dispatch_per_cycle, work_mode limits

Step 6:  APPROVAL & TRANSITION
  Ensure review tasks have approval objects
  Approved approvals → transition to done
  Rejected approvals → set up regression
  Wake fleet-ops if pending approvals

Step 7:  PARENT EVALUATION
  Build parent → children map
  ALL children done → parent to review
  Summary comment on parent aggregating child results
  Propagate child trail data to parent

Step 8:  DRIVER MANAGEMENT
  Wake PM if: unassigned inbox tasks, driver interval elapsed
  Wake fleet-ops if: pending approvals, stale review tasks
  Inject relevant data into driver sessions via gateway

Step 9:  CROSS-TASK PROPAGATION
  Child comments → summarize on parent
  Contribution artifacts → add to target task context
  Transfer context → package for receiving agent
  Trail events → record on task and parent

Step 10: SESSION MANAGEMENT
  Two parallel countdowns:
  a) Context remaining per agent (awareness at 7%/5%)
  b) Rate limit session fleet-wide (awareness at 85%/90%)

  Near rollover logic:
  - DO NOT dispatch 1M context tasks near rate limit rollover
  - Evaluate each agent's context:
    Predicted upcoming work? → keep alive
    Over ~40-80K tokens with no predicted work? → dump as smart
    artifacts, fresh session
    Unrelated work coming? → simply new task, no re-injection
  - Force compact IS appropriate near rollover for heavy contexts
  - Allow going over 90% rate limit for compacting itself
  - After rollover: fresh sessions, re-inject where work continues

  Aggregate context math:
  - 5 × 200K = 1M tokens re-sent on rollover → ~50% of x5 Pro
  - 2 × 1M = 2M → exceeds x5 Pro window
  - Brain calculates total fleet context cost vs remaining quota

Step 11: HEALTH & BUDGET
  Tasks stuck > 48h → alert PM
  Agents offline with assigned work → alert PM
  Budget over threshold → reduce work mode
  Sprint progress → update board memory

Step 12: DIRECTIVES
  Read PO directives from board memory
  Route to target agents via context/ files
  Mark directives as processed (tag update)
```

### 90.3 Chain Registry — Event → Handler Mapping

```
fleet.methodology.stage_changed:
  → create_contribution_opportunities (if to_stage=reasoning)
  → notify_stage_change (IRC, board memory)
  → update_trail (stage_transition)

fleet.methodology.readiness_changed:
  → checkpoint_notification (at 50: notify PO)
  → gate_enforcement (at 90: require PO approval)
  → update_trail (readiness_change)

fleet.task.completed:
  → create_pr
  → move_to_review
  → create_approval
  → notify_contributors (QA, architect, devsecops)
  → evaluate_parent
  → update_sprint_progress
  → update_trail (task_completed)

fleet.contribution.posted:
  → propagate_to_target_task (add to context, notify owner)
  → update_trail (contribution_received)
  → check_contribution_completeness (if all → notify PM)

fleet.approval.approved:
  → transition_to_done
  → notify_agent
  → update_trail
  → evaluate_parent

fleet.approval.rejected:
  → regress_task (readiness drops, stage may revert)
  → notify_agent_of_rejection
  → update_trail
  → doctor_signal (repeated rejection → flag agent)
```

Cascade depth limit: 5 (prevents infinite event loops).
Each handler can emit new events that trigger further handlers.

### 90.4 Logic Engine — Dispatch Decision

```
is_dispatchable(task, agent, fleet_state):
  ✓ task.status == inbox
  ✓ task.agent_name == agent.name
  ✓ agent.status in (ACTIVE, IDLE)  # online
  ✓ agent has no in_progress task   # not busy
  ✓ doctor has not flagged agent    # cleared
  ✓ all dependencies resolved       # unblocked
  ✓ required contributions received  # synergy complete
  ✓ fleet_mode allows dispatch       # work mode permits
  ✓ budget allows dispatch           # not over limit

  ALL must be true. ANY false → skip this task this cycle.
  Deterministic. No AI judgment. Python logic. Free.
```

---

## §91 Multi-Fleet Identity — Naming, Attribution, No Collisions

**Source:** fleet-elevation/16-multi-fleet-identity.md (342 lines)

> "another fleet would have another name and username, you need to think
> about this, like we do a diff fleet number if that is still in place,
> since it will be possible to have two fleet connected to the same Plane"

**Why it matters:** Multi-fleet is not a distant future — it's the
infrastructure target (Machine 1 + Machine 2). When two fleets share
Plane, GitHub, IRC, and ntfy, every piece of output must be attributed
to the correct fleet AND the correct agent. Without identity:
- Alpha's architect comment is indistinguishable from Bravo's
- Git commits don't show which fleet produced them
- IRC messages blend together
- Plane labels collide (two "stage:reasoning" labels from different fleets)
- The PO can't track which fleet is productive

Identity connects to:
- **Signatures (§44):** LaborStamp includes fleet_id — every piece of
  work attributed to fleet + agent + model
- **Plane sync:** Comment attribution `[alpha-architect]`, label
  namespacing `alpha:stage:reasoning` vs `bravo:stage:reasoning`
- **Git:** Commit authorship includes fleet-prefixed agent name
- **IRC:** Nick format includes fleet prefix
- **Trail (§38):** Trail events carry fleet_id — audit trail is
  fleet-specific even on shared infrastructure
- **Brain:** Each fleet has its OWN brain (orchestrator), OWN MC,
  OWN gateway. Plane is the SHARED coordination layer.
- **LocalAI peering:** Two clusters can load-balance and failover
  across fleet boundaries — alpha's cluster peers with bravo's

### 91.1 Fleet Identity

```yaml
Fleet Alpha:           Fleet Bravo:
  id: alpha              id: bravo
  number: 1              number: 2
  name: "Fleet Alpha"    name: "Fleet Bravo"
  mc_url: localhost:8000  mc_url: bravo-mc:8000
  gateway_url: :3000      gateway_url: bravo-gw:3000
  plane_url: plane.local  plane_url: plane.local   # SAME Plane
  shared_plane: true      shared_plane: true
```

### 91.2 Agent Identity (Fleet-Prefixed)

```
Fleet Alpha agents:
  alpha-pm          alpha-lead        alpha-architect
  alpha-engineer    alpha-devops      alpha-qa
  alpha-security    alpha-writer      alpha-ux
  alpha-compliance

Fleet Bravo agents:
  bravo-pm          bravo-lead        bravo-architect
  bravo-engineer    bravo-devops      bravo-qa
  bravo-security    bravo-writer      bravo-ux
  bravo-compliance
```

agent.yaml additions: `fleet_id`, `fleet_number`, `username`

### 91.3 Shared Plane — No Collision Strategy

```
COMMENT ATTRIBUTION:
  "[alpha-architect] Recommended event bus pattern."
  "[bravo-engineer] Implementing with observer per bravo-architect."
  Prefix: [fleet_id-role]

LABEL NAMESPACING:
  Fleet-specific: alpha:stage:reasoning, bravo:stage:work
  Shared (no prefix): priority:high, type:epic

CROSS-FLEET COLLABORATION:
  Same Plane issue can have tasks from BOTH fleets.
  Alpha's architect designs, Bravo's engineer implements.
  Each fleet's brain manages its own agents.
  Plane is the shared coordination layer.
```

### 91.4 Infrastructure Per Fleet

```
PER FLEET (independent):
  MC instance, Gateway instance, Orchestrator (brain),
  LocalAI cluster, 10 agents

SHARED (one instance):
  Plane, GitHub repos, ntfy (fleet-tagged), IRC (fleet-prefixed nicks)

LocalAI peering: Cluster 1 ↔ Cluster 2
  Load balance, specialization, failover
```

---

## §92 Context Window Awareness & Cost Control

**Source:** context-window-awareness-and-control.md (442 lines)
**Why it matters:** Context is the fleet's most expensive resource and
the most dangerous hidden cost. Without awareness, a single agent with
a large context doing many tool calls can consume the ENTIRE 5-hour
rate limit window by itself. The brain MUST understand context cost
mechanics to make strategic decisions about session management,
dispatch, and compaction.

Context connects to:
- **Brain Step 10 (§90):** Session management — two parallel
  countdowns (context per agent, rate limit fleet-wide), force compact
  logic, smart artifact dumping near rollover, aggregate fleet math
- **Strategic calls (§85):** Session strategy (fresh/continue/compact)
  is driven by context state. Starting a 1M context session near
  rollover is a budget catastrophe.
- **Budget mode (§97):** Budget pressure triggers economic mode which
  slows all crons — but context management is ALSO a lever. Dumping
  idle contexts frees rate limit headroom.
- **Signatures (§44):** context_used_pct and rate_limit_pct are
  LaborStamp fields — the PO can see how full context was when each
  piece of work was produced. High context % = higher cost per action.
- **Pre-embed (§80):** The size of pre-embed data directly affects
  context consumption. Full data is essential but the brain must
  balance completeness with context cost.
- **Prompt caching:** 5-minute cache lifetime. Rapid successive calls
  are CHEAP (cached). Long pauses break cache → 10-20x cost inflation.
  The brain should batch agent work, not spread it out.

### 92.1 Context Cost Multiplication

```
Each tool call ≈ 1 API call.
Each API call sends FULL context.
Turn 15 with 500K context:
  ~8 API calls × 500K = 4M tokens consumed

This is why context SIZE matters as much as number of turns.
Large context + many turns = exponential token consumption.
```

### 92.2 Two Parallel Countdowns

```
COUNTDOWN 1: Context remaining per agent
  Organic flow at 7% remaining (agent naturally wraps up)
  Force compact at 5% remaining (brain intervenes)

COUNTDOWN 2: Rate limit session (fleet-wide)
  Awareness at 85% (reduce dispatch, prefer smaller contexts)
  Force action at 90% (compact heavy contexts, allow budget overflow)
```

### 92.3 Session Management Rules

```
1. DO NOT dispatch 1M context tasks near rate limit rollover

2. Near rollover, evaluate each agent:
   Has upcoming work needing this context? → keep alive
   Over ~40-80K with no predicted work? → dump as smart artifacts
   Unrelated work coming? → simply new task

3. Force compact IS appropriate near rollover
   Allow going over 90% rate limit for compacting itself
   Compaction cost saves more than it spends

4. After rollover: fresh sessions, re-inject where work continues

5. Aggregate math matters:
   5 × 200K = 1M tokens re-sent on rollover → ~50% of x5 Pro
   2 × 1M = 2M → exceeds x5 Pro window
   Brain calculates total fleet context cost vs remaining quota

6. Don't persist context "just in case"
   Only keep alive if predicted upcoming job
   Idle agents with no predicted work = dump to artifacts
```

### 92.4 Prompt Cache Behavior

```
Cache lifetime: 5 minutes
Post-pause breaks cache → 10-20x cost inflation
Background agents use Opus quota

Implication: rapid successive calls are CHEAP (cached).
Long pauses between calls are EXPENSIVE (cache expired).
Brain should batch agent work, not spread it out.
```

### 92.5 Subscription Tier Mapping

```
Max 5X and Max 20X both include 1M context (not Pro).
Context window multiplies cost per API call.

Aggregate math for fleet:
  5 agents × 200K context = 1M tokens re-sent on rollover
    → ~50% of x5 Pro 5-hour window
  2 agents × 1M context = 2M tokens re-sent
    → EXCEEDS x5 Pro window

Brain must calculate total fleet context cost vs remaining quota.
```

### 92.6 Statusline Awareness

```
~/.claude/statusline.sh provides real-time context display:
  Context: 45% used | Rate: 72% session | Tokens: 125K in / 8K out

13 JSON fields available from Claude Code:
  window size, used %, remaining %, input/output tokens,
  cache tokens, total tokens, >200K flag

Strategic compaction pattern:
  Deliver artifact before compaction → let it compact →
  recover from memory for next task (the "edge sensation")
```

---

## §93 Ecosystem Deployment — Three Tiers

**Source:** ecosystem-deployment-plan.md (523 lines)
**Why it matters:** OpenClaw's ecosystem is massive — 5,400+ skills,
9,000+ plugins, MCP servers, prompt caching. The fleet currently uses
almost NONE of it. 1 skill pack (19 generic for all agents), no plugins
configured, no prompt caching, no per-role MCP servers. This is like
having a workshop full of professional tools and using only a hammer.

The ecosystem connects to:
- **Agent tooling IaC (§34):** Per-role MCP servers, plugins, and skills
  configured via config/agent-tooling.yaml — the architect gets
  architecture-propose, QA gets quality-coverage, DevSecOps gets
  security-audit. Not generic templates for everyone.
- **Prompt caching (§92):** 90% savings on cached input tokens.
  This is the single easiest cost reduction — a config change. But
  persistent agents need "long" retention (5min cache lifetime).
- **Claude-Mem plugin:** Semantic memory across sessions. Agents
  remember codebase patterns, test patterns, design decisions from
  prior sessions. Without it, every heartbeat starts from zero.
- **LocalAI integration (§94):** LocalAI RAG via /stores/ API +
  BGE embeddings is Tier 2. LocalAI v4 agents + AICP bridge is Tier 3.
- **Cost model (§47):** Each ecosystem item has a cost impact. Prompt
  caching saves ~90% on cached tokens. Batch API saves ~50% on
  non-urgent work. Per-role skills increase efficiency = fewer turns
  per task = less cost.

### 93.1 Tier 1: Immediate (Config/Install)

```
PROMPT CACHING:
  config: cacheRetention: "short" or "long"
  Persistent agents need "long" (5min cache lifetime)
  90% savings on cached input tokens
  Deploy: fleet.yaml config change

CLAUDE-MEM PLUGIN:
  Semantic memory across session boundaries
  Agents remember patterns from prior sessions
  Architect remembers codebase, QA remembers test patterns
  Deploy: per-agent plugin config

CONTEXT7 MCP:
  Up-to-date library documentation for agents
  Deploy: MCP server registration

FILESYSTEM MCP:
  File operations via MCP (standardized)
  Deploy: MCP server registration
```

### 93.2 Tier 2: Short-Term (Integration Work)

```
GITHUB MCP:        PR operations, issue management
PLAYWRIGHT MCP:    Browser automation for testing
DOCKER MCP:        Container management
PER-AGENT SKILLS:  5,400+ skills, per-role selection via
                   config/agent-tooling.yaml (not generic for all)
LOCALAI RAG:       /stores/ API + BGE embeddings (CPU, free)
BATCH API:         50% cost reduction for non-urgent work
```

### 93.3 Tier 3: Strategic (Architecture Required)

```
AGENT TEAMS/SWARM: Multi-agent orchestration (OpenClaw native)
AICP BRIDGE:       LocalAI ↔ fleet routing for offload
LOCALAI v4 AGENTS: LocalAI's own agent framework
OPENROUTER:        Free tier model access for simple tasks
MULTI-FLEET:       Cross-fleet coordination via shared Plane
```

### 93.4 Skills Registry

```
OpenClaw: 5,400+ skills available
Currently deployed: 1 pack (19 generic skills for all agents)

Target: per-role domain-specific skills via config/agent-tooling.yaml
  PM: pm-plan, pm-sprint, pm-triage
  Architect: architecture-propose, architecture-review
  QA: quality-coverage, quality-regression
  DevSecOps: security-audit, security-review
  Engineer: feature-implement, refactor
  DevOps: ops-deploy, foundation-docker
  Writer: docs-generate, docs-review
```

---

## §94 LocalAI Routing Decision Matrix

**Source:** strategic-vision-localai-independence.md (433 lines)

> "Its important that the main first mission is to make localAI
> functional and then make it more and more reliable to offload as
> much as possible the work from claude till one day maybe even try
> to actually run independently as much as possible."

**Why it matters:** This is the AICP project's core mission — LocalAI
independence. The fleet currently runs 100% on Claude. Every heartbeat,
every dispatch, every review = Claude tokens = cost. The routing matrix
is the plan to change that — specific per-operation decisions about
WHAT goes to LocalAI, WHAT stays on Claude, and WHY.

Routing connects to:
- **Brain (§90):** The brain decides which backend to use per dispatch.
  The 3-tier model: brain (free) → LocalAI (free) → Claude (paid).
  Use the cheapest tier that can handle it.
- **Agent lifecycle (§85):** Brain-evaluated heartbeats ARE the first
  routing win — sleeping agents get deterministic evaluation (free)
  instead of Claude calls.
- **Budget mode (§97):** Budget pressure pushes routing toward LocalAI.
  Economic mode may restrict Claude to opus-only for critical tasks.
- **Model management (§54):** Single-active backend on 8GB VRAM.
  hermes-3b stays warm for fleet operations. Swap for complex tasks.
- **AICP bridge:** AICP's router.py has routing logic that fleet
  needs to integrate — not duplicate. Existing infrastructure.
- **Cost model (§47):** LocalAI operations cost $0. Every operation
  routed to LocalAI is a direct Claude token saving. Target: 80%+
  Claude token reduction at Stage 5.

### 94.1 Routing Decision Tree

```
DOES THIS NEED REASONING?
  NO → LocalAI (local, free, fast)
      ├── 3B model for structured responses
      ├── MCP tool calls (direct HTTP, no LLM)
      └── Template-based responses
  YES → Claude (cloud, paid, powerful)
      ├── opus for complex (architecture, security, planning)
      └── sonnet for standard (implementation, review)
```

### 94.2 Per-Operation Routing

| Operation | Backend | Why |
|-----------|---------|-----|
| Heartbeat (no work) | Brain eval (free) | Deterministic check |
| fleet_read_context | Direct HTTP (no LLM) | Just API calls |
| fleet_agent_status | Direct HTTP (no LLM) | Just API calls |
| fleet_chat post | hermes-3b (LocalAI) | Posting ≠ reasoning |
| Simple task acceptance | hermes-3b (LocalAI) | Structured plan output |
| Simple review (pass/fail) | hermes-3b (LocalAI) | Pattern matching |
| Complex implementation | Claude opus | Deep reasoning |
| Architecture design | Claude opus | Creative thinking |
| Security analysis | Claude opus | Cannot compromise |
| Sprint planning | Claude opus | Strategic thinking |
| Standard implementation | Claude sonnet | Good enough |

### 94.3 The 5-Stage Mission

```
Stage 1: Make LocalAI functional           ← DONE (assessment complete)
Stage 2: Route simple operations to LocalAI ← TARGET
Stage 3: Progressive offload
Stage 4: Reliability and failover
Stage 5: Near-independent operation (80%+ Claude token reduction)
```

### 94.4 Infrastructure Target

```
Machine 1: Fleet Alpha
  ├── LocalAI Cluster 1 (GPU: 8GB VRAM)
  │   Primary: hermes-3b (always loaded, 10s cold start)
  │   Swap for: complex LocalAI tasks (7B models)
  ├── OpenClaw Gateway + MC
  └── 10 Agents (alpha-prefixed)

Machine 2: Fleet Bravo
  ├── LocalAI Cluster 2 (GPU: 8GB VRAM)
  │   Primary: Qwen3.5-9B (target workhorse)
  │   Swap for: codellama (code tasks)
  ├── OpenClaw Gateway + MC
  └── 10 Agents (bravo-prefixed)

Peering: Cluster 1 ↔ Cluster 2
  Load balance, specialization, failover
  Combined: 16GB VRAM, two models simultaneously
```

---

## §95 Orchestrator Waking — Gateway Injection

**Source:** agent-rework/03-orchestrator-waking.md (89 lines)
**Why it matters:** Waking bridges the gap between the brain's
cycle-based evaluation and real-time responsiveness. The brain
evaluates every cycle (tempo scaled by budget mode), but the agent's
heartbeat cron may be on a longer interval. Waking lets the brain
inject content DIRECTLY into an agent's session via the gateway,
bypassing the heartbeat schedule — the agent receives the wake
message immediately and starts working.

Waking connects to:
- **Agent lifecycle (§85):** Brain-evaluated heartbeat detects a
  wake trigger → waking delivers the work to the agent. The lifecycle
  decides IF to wake. The wake mechanism delivers HOW.
- **Brain Step 8 (§90):** Driver management — PM wakes for unassigned
  tasks, fleet-ops wakes for pending approvals. Already implemented.
- **Gateway client (existing):** inject_content() via WebSocket
  JSON-RPC to gateway. Already built in gateway_client.py.
- **Budget mode (§97):** Wake frequency scales with tempo. Turbo =
  wake evaluation more often. Economic = less frequent. But a direct
  @mention or PO directive triggers PROMPT wake regardless of tempo.
- **Cooldown:** Don't wake the same agent twice in one cycle. Don't
  wake an agent that has an active in-progress task. Don't wake
  anyone when fleet is paused.

### 95.1 Wake Mechanism

```
Brain detects: work pending for sleeping agent
  ↓
gateway_client.inject_content(agent_session_key, wake_message)
  ↓
Gateway: chat.send injects message into agent session
  ↓
Agent's Claude session receives: "Wake: {reason}"
  ↓
Agent processes wake message and starts working
```

### 95.2 When to Wake

```
PM wake triggers:
  - Unassigned tasks in inbox needing triage
  - Blocked tasks needing resolution
  - New Plane issues not yet on OCMC
  - PO directives targeting PM

Fleet-ops wake triggers:
  - Pending approvals in queue
  - Tasks stuck in review
  - Health alerts requiring attention
  - PO directives targeting fleet-ops
```

### 95.3 Don't Wake Conditions

```
- Already woken this cycle (cooldown — prevent spam)
- Agent has active in-progress task (already busy)
- Fleet in paused mode (no waking anyone)
```

---

## §96 Index — Sections 90-95

```
§90  The Brain — 13-Step Cycle         — 3 layers, 13 steps, chain registry, logic engine
§91  Multi-Fleet Identity              — naming, attribution, shared Plane collision prevention
§92  Context Window Awareness          — cost multiplication, 2 countdowns, session mgmt, cache
§93  Ecosystem Deployment              — 3 tiers (immediate/short-term/strategic), skills registry
§94  LocalAI Routing Matrix            — per-operation routing, 5-stage mission, infrastructure
§95  Orchestrator Waking               — gateway injection, wake triggers, cooldown
```

---

## §97 Budget Mode — Dynamic Fleet-Wide Tempo Control

**Why it matters:** Budget mode is not a simple spend limit — it is the
fleet's BREATHING RATE. It controls how fast every system operates,
how responsive agents are, how quickly changes propagate, and how much
budget is consumed per hour. It connects to EVERYTHING:
- **Brain cycle (§90):** Orchestrator cycle frequency scales with tempo
- **Agent heartbeats (§85):** Heartbeat cron frequency scales with tempo
- **Sync daemon:** MC ↔ Plane sync frequency scales with tempo
- **Monitor daemon:** Health checks scale with tempo
- **Wake evaluation (§95):** How often sleeping agents get evaluated
- **PO control (§71):** PO can set budget_mode directly via directive

Budget mode is a fleet-wide tempo multiplier.
Every cron in the fleet has its OWN base frequency. Budget mode
applies a speed/frequency offset that scales ALL of them — but
each cron keeps its own proportional rhythm. The orchestrator cycle,
sync daemon, monitor, plane-watcher, every agent's heartbeat cron,
driver intervals — each has a different base frequency, and budget
mode scales them all dynamically.

### 97.1 How It Works

```
Each cron has its OWN base frequency.
Budget mode applies a DYNAMIC offset to ALL of them.

Budget modes (from fastest to slowest):
  turbo      — fastest tempo, highest cost
  aggressive — fast tempo
  standard   — normal tempo
  economic   — slow tempo, lowest cost

The offset is proportional — faster budget mode = tighter
intervals across the board. Slower = wider intervals.
Each cron's individual base frequency determines its own
actual interval at each budget mode.

This is NOT a single hardcoded number. Each cron is different.
The budget mode is the MULTIPLIER that scales them all.
```

### 97.2 What Gets Scaled

```
SYSTEM CRONS (each has own base frequency, all scale):
  Orchestrator cycle         — brain 13-step loop
  Sync daemon                — MC ↔ Plane sync
  Monitor daemon             — health checks
  Plane-watcher              — Plane change detection

AGENT CRONS (each has own base frequency, all scale):
  Agent heartbeat crons      — per-agent, per-role
  Driver heartbeat interval  — PM + fleet-ops
  Brain-evaluated heartbeats — sleeping agent evaluation

Every cron affected by the speed/frequency offset per budget mode.
When budget mode changes, the ENTIRE fleet changes tempo —
every system, every agent, every cron — each proportionally.
```

### 97.3 Budget Mode Transitions

```
Budget monitor detects pressure → adjusts budget mode dynamically.
PO can set budget mode directly via directive.
After rate limit rollover → budget recovers → PO decides tempo.

The fleet BREATHES — faster when there's work and budget,
slower when conserving. Dynamic, not static.
```


NOTE: LightRAG detailed in §46. Readiness vs Progress detailed in §45.
