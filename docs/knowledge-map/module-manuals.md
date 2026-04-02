# Module Manuals — 128 Modules Mapped to 22 Systems

**Part of:** Fleet Knowledge Map → Module Manuals branch
**Purpose:** Per-module purpose, key exports, and system mapping.
**Source:** Read from actual Python module headers and docstrings.

---

## Fleet Module Manuals — Knowledge Map Branch

### Systems Index (01-22)

| # | System | Domain |
|---|--------|--------|
| 01 | Methodology | Stage progression, readiness, protocols |
| 02 | Immune System | Disease detection, behavioral security |
| 03 | Teaching System | Adapted lessons, comprehension |
| 04 | Event Bus | CloudEvents, routing, chains |
| 05 | Control Surface | Fleet modes, directives, pause |
| 06 | Agent Lifecycle | Status, sleep, heartbeat gate |
| 07 | Orchestrator | Brain, dispatch, sync, driver |
| 08 | MCP Tools | Agent-facing tools (25 tools) |
| 09 | Standards | Artifact standards, quality |
| 10 | Transpose | Object-HTML bidirectional |
| 11 | Storm | Token drain detection, response |
| 12 | Budget | Modes, monitoring, analytics |
| 13 | Labor | Attribution, stamps, analytics |
| 14 | Router | Backend routing, model selection |
| 15 | Challenge | Adversarial validation loop |
| 16 | Models | Benchmarks, configs, promotion |
| 17 | Plane | Bidirectional Plane sync |
| 18 | Notifications | ntfy, IRC, routing, display |
| 19 | Session | Context management, telemetry |
| 20 | Infrastructure | Clients, cache, config |
| 21 | Agent Tooling | Skills, enforcement |
| 22 | Agent Intelligence | Autocomplete, preembed, context |

---

### core/ (94 modules)

`agent_lifecycle.py` -- Smart agent status management (ACTIVE/IDLE/SLEEPING/OFFLINE), silent heartbeat relay to brain after 1 HEARTBEAT_OK (key exports: AgentStatus, FleetLifecycle) **[S06]**

`agent_roles.py` -- Agent roles and PR authority per domain, defines who can reject/close/block PRs (key exports: PRAuthority, AgentRole, AGENT_ROLES) **[S02]**

`artifact_tracker.py` -- Progressive work tracking, measures artifact completeness against standards per operation cycle (key exports: ArtifactCompleteness, check_artifact_completeness) **[S09]**

`auth.py` -- Claude Code OAuth token rotation, reads/refreshes token between ~/.claude and ~/.openclaw/.env (key exports: get_current_claude_token, get_stored_token, refresh_token, token_needs_refresh) **[S20]**

`autocomplete.py` -- Context arrangement in 8-layer onion order for agent system prompt injection, FORMATTER not data source (key exports: build_task_context, build_fleet_context) **[S22]**

`backend_health.py` -- Real-time backend status dashboard (up/down/degraded) for LocalAI, OpenRouter, Claude (key exports: BackendStatus, BackendHealthEntry, BackendHealthDashboard) **[S14]**

`backend_router.py` -- Multi-backend task routing, cheapest capable backend wins, fallback chain LocalAI->OpenRouter->sonnet->opus->queue (key exports: BackendRouter, RoutingDecision) **[S14]**

`behavioral_security.py` -- Scans task content, code diffs, and human directives for suspicious patterns, can set security_hold (key exports: SecurityFinding, BehavioralSecurityScanner) **[S02]**

`board_cleanup.py` -- Archive noise tasks (heartbeats, reviews, conflicts) to keep sprint work visible (key exports: CleanupResult, identify_noise_tasks) **[S07]**

`budget_analytics.py` -- Tracks cost, quality, and efficiency per budget mode over time for PO decision-making (key exports: BudgetEvent, BudgetAnalytics) **[S12]**

`budget_modes.py` -- Fleet tempo settings, orchestrator/heartbeat frequency offsets per mode (key exports: BudgetMode, BUDGET_MODES, get_mode, get_active_mode_name) **[S12]**

`budget_monitor.py` -- Reads real Claude quota via OAuth usage API, detects fast climbs, blocks dispatch when thresholds exceeded (key exports: QuotaReading, BudgetMonitor, check_quota) **[S12]**

`budget_ui.py` -- Data provider for OCMC header bar budget controls and per-order budget overrides (key exports: BudgetOverride, BudgetUIData) **[S12]**

`cache.py` -- Abstract cache contract (key-value with TTL), implemented by infra/cache_sqlite.py (key exports: Cache) **[S20]**

`chain_runner.py` -- Executes event chains across all surfaces (INTERNAL/PUBLIC/CHANNEL/NOTIFY/PLANE/META), tolerates partial failure (key exports: ChainRunner) **[S04]**

`challenge.py` -- Challenge loop data model (M-IV01), four types: automated/agent/cross-model/scenario (key exports: ChallengeType, ChallengeStatus, ChallengeRound, ChallengeRecord, ChallengeFinding) **[S15]**

`challenge_analytics.py` -- Aggregates challenge outcomes for per-agent/per-tier pass rates, common findings, teaching signals (key exports: ChallengeEvent, ChallengeAnalytics) **[S15]**

`challenge_automated.py` -- Zero-LLM-cost deterministic challenges from task metadata and code diffs (key exports: AutomatedChallenge, generate_automated_challenges) **[S15]**

`challenge_cross_model.py` -- Uses different LLM to challenge work from original model for independent verification (key exports: CrossModelChallenger) **[S15]**

`challenge_deferred.py` -- FIFO queue for deferred challenges, persists to state/deferred_challenges.json (key exports: DeferredChallengeEntry, DeferredChallengeQueue) **[S15]**

`challenge_protocol.py` -- Orchestrates challenge lifecycle: evaluate, assign challenger, build context, run, determine outcome (key exports: ChallengeContext, ChallengeProtocol) **[S15]**

`challenge_readiness.py` -- Integrates challenge status into readiness progression (70% work complete -> 80% challenge passed -> 90% review) (key exports: ReadinessCheckpoint, check_challenge_readiness) **[S15]**

`challenge_scenario.py` -- Reproduce-and-break testing for bug fixes: reproduction, boundary, concurrency, removal, interaction (key exports: ScenarioChallenge, generate_scenario_challenges) **[S15]**

`change_detector.py` -- Tracks what changed between orchestrator cycles for targeted reactions instead of blind polling (key exports: Change, ChangeDetector) **[S07]**

`cluster_peering.py` -- Machine 1 <-> Machine 2 LocalAI cluster peering config, load balancing, failover (FUTURE) (key exports: ClusterNode, ClusterPeering) **[S16]**

`codex_review.py` -- Trigger/decision layer for Codex adversarial reviews via codex-plugin-cc, based on confidence tier and budget (key exports: CodexReviewDecision, should_trigger_codex_review) **[S14]**

`config_sync.py` -- Keeps IaC YAML configs in sync with live Plane state, optionally commits to git (key exports: ConfigSync) **[S17]**

`config_watcher.py` -- Detects when IaC config files are modified and emits events for re-sync (key exports: ConfigWatcher) **[S05]**

`context_assembly.py` -- Shared data aggregation for MCP group calls and pre-embed, assembles task and heartbeat context bundles (key exports: assemble_task_context, assemble_heartbeat_context, clear_context_cache) **[S22]**

`context_writer.py` -- Writes pre-embed data to agent context files (fleet-context.md, task-context.md) for gateway injection (key exports: write_heartbeat_context, write_task_context) **[S22]**

`contributions.py` -- Cross-agent synergy brain module, creates parallel contribution subtasks from synergy matrix, blocks dispatch until received (key exports: ContributionManager) **[S07]**

`cross_refs.py` -- Automatic cross-referencing across surfaces (Plane<->OCMC<->IRC<->GitHub), generated from events (key exports: CrossReference, CrossRefEngine) **[S04]**

`directives.py` -- PO commands routed to agents via board memory tags, orchestrator reads and routes each cycle (key exports: Directive, DirectiveRouter) **[S05]**

`doctor.py` -- Immune system active component, observes agents, detects disease, responds with prune/compact/teaching (key exports: DoctorReport, Doctor) **[S02]**

`driver.py` -- Autonomous driver model for agents that create their own work (PM, accountability-generator), priority model for idle time (key exports: ProductRoadmap, DriverAgent, get_driver_priority) **[S07]**

`dual_gpu.py` -- Dual-GPU configuration for 19GB VRAM (8GB+11GB), no-swap routing (FUTURE) (key exports: GPUSlot, DualGPUConfig) **[S16]**

`error_reporter.py` -- File-based agent error reporting (rate limits, API failures), orchestrator reads each cycle (key exports: AgentError, record_error, read_errors) **[S07]**

`event_chain.py` -- Multi-surface event chain definitions, single operation publishes to INTERNAL/PUBLIC/CHANNEL/NOTIFY/PLANE/META (key exports: EventSurface, Event, EventChain, ChainResult) **[S04]**

`event_display.py` -- Renders events differently per channel (IRC compact, Plane rich HTML, ntfy title+body, heartbeat structured) (key exports: render_irc, render_plane, render_ntfy, render_heartbeat) **[S18]**

`event_router.py` -- Deterministic event-to-agent matching by capability, tags, role, mentions, project association (key exports: EventRouter, AGENT_TAG_SUBSCRIPTIONS) **[S04]**

`events.py` -- CloudEvents-based event store and agent feeds, persistent, filtered by recipient/mentions/tags (key exports: FleetEvent, EventStore, create_event, EVENT_TYPES) **[S04]**

`federation.py` -- Multi-machine fleet identity and collaboration, fleet ID, agent prefix namespacing (key exports: FleetIdentity) **[S20]**

`fleet_mode.py` -- Fleet control state from board's fleet_config: work mode, cycle phase, backend mode (key exports: FleetControlState, read_fleet_control, should_dispatch) **[S05]**

`gateway_guard.py` -- Detects stale/duplicate gateway processes that burn tokens in parallel (March 2026 catastrophe prevention) (key exports: GatewayProcess, GatewayGuard) **[S11]**

`health.py` -- Fleet health monitoring: stuck detection, stale tasks, offline agents, worktree cleanup, service health (key exports: HealthIssue, HealthReport, check_fleet_health) **[S07]**

`heartbeat_context.py` -- Pre-computes agent context without AI for heartbeats, saves 3-5 tool calls per heartbeat (key exports: HeartbeatBundle, build_heartbeat_bundle) **[S22]**

`heartbeat_gate.py` -- Brain evaluation for idle/sleeping agents, deterministic Python (FREE), ~70% cost reduction (key exports: HeartbeatDecision, HeartbeatGate, evaluate_heartbeat) **[S06]**

`heartbeat_stamp.py` -- Minimal labor stamps for heartbeats to track cost trends and detect expensive heartbeats (key exports: create_heartbeat_stamp) **[S13]**

`incident_report.py` -- Post-incident report generation after WARNING+ storm events, severity/duration/cost/prevention (key exports: ResponseEntry, StormEvent, IncidentReport) **[S11]**

`interfaces.py` -- Abstract contracts for infrastructure adapters: TaskClient, MemoryClient, ApprovalClient, AgentClient, GitClient, NotificationClient, ConfigLoader (key exports: TaskClient, MemoryClient, ApprovalClient, AgentClient, GitClient, NotificationClient, ConfigLoader) **[S20]**

`labor_analytics.py` -- Aggregates labor stamps for cost/quality insights per agent, model, tier, backend (key exports: AgentCostMetrics, LaborAnalytics) **[S13]**

`labor_stamp.py` -- Provenance tracking for fleet artifacts: what produced it, how, at what confidence tier (key exports: LaborStamp, derive_confidence_tier, assemble_stamp) **[S13]**

`memory_structure.py` -- Agent persistent memory organization: MEMORY.md, codebase_knowledge, project_decisions, task_history, team_context (key exports: MEMORY_FILES, initialize_agent_memory) **[S06]**

`methodology.py` -- Stage progression system (conversation/analysis/investigation/reasoning/work), readiness gate, protocol checks (key exports: Stage, MethodologyCheck, VALID_READINESS) **[S01]**

`model_benchmark.py` -- Benchmark framework for LocalAI models on fleet-representative prompts (latency, quality, structured output) (key exports: BenchmarkPrompt, BenchmarkResult, ModelBenchmark) **[S16]**

`model_configs.py` -- LocalAI model configuration templates for current and upgrade-candidate models (key exports: ModelConfig, KNOWN_MODELS) **[S16]**

`model_promotion.py` -- Default model promotion lifecycle with pre/post approval rate monitoring (key exports: PromotionRecord, ModelPromotion) **[S16]**

`model_selection.py` -- Dynamic model (opus/sonnet) and effort level selection based on task complexity, SP, and agent role (key exports: ModelSelection, select_model) **[S14]**

`model_swap.py` -- Router-initiated model swaps for LocalAI single-active-backend, skip-swap logic, swap metrics (key exports: SwapRecord, ModelSwapManager) **[S14]**

`models.py` -- Pure domain data structures: Task, TaskStatus, Agent, Approval, PullRequest, BoardMemoryEntry, Project, FleetContext, Commit (key exports: Task, TaskStatus, Agent, Approval, PullRequest, BoardMemoryEntry, Project, FleetContext, Commit, AlertSeverity, TaskCustomFields) **[S20]**

`notification_router.py` -- Classifies events as info/important/urgent and routes to ntfy/IRC/Windows toast with deduplication (key exports: NotificationLevel, NotificationRouter) **[S18]**

`ocmc_watcher.py` -- Detects Mission Control state changes (task status, approvals, agent online/offline) and emits CloudEvents (key exports: OCMCWatcher) **[S04]**

`openai_client.py` -- OpenAI-compatible HTTP client for LocalAI and OpenRouter free tier (key exports: ChatMessage, ChatResponse, OpenAIClient) **[S14]**

`outage_detector.py` -- Detects API outages and rate limits, triggers exponential backoff and pause (key exports: ServiceState, OutageDetector) **[S07]**

`phases.py` -- PO-defined delivery maturity progression, unlimited phases with any name, project-specific progressions (key exports: PhaseDefinition, PhaseProgression) **[S01]**

`plane_methodology.py` -- Read/write methodology fields (stage, readiness) on Plane issues via labels, hybrid approach for CE (key exports: PlaneMethodology, VALID_READINESS, VALID_STAGES) **[S17]**

`plane_sync.py` -- Bidirectional Plane<->OCMC sync: ingest new Plane issues as OCMC tasks, push completions back (key exports: PlaneSyncer) **[S17]**

`plane_watcher.py` -- Polls Plane API for changes (new issues, state changes, comments, cycle status) and emits CloudEvents (key exports: PlaneWatcher) **[S17]**

`plan_quality.py` -- Validates agent plans meet minimum quality standards (concrete steps, verification, risk, scope) (key exports: PlanAssessment, assess_plan) **[S09]**

`preembed.py` -- FULL context injected before agent starts, NOT compressed, complete data set per role (key exports: format_events, format_tasks, format_heartbeat_preembed, format_task_preembed) **[S22]**

`pr_hygiene.py` -- Detects stale, conflicting, duplicate, orphaned, and long-open PRs with recommended actions (key exports: PRIssue, check_pr_hygiene) **[S07]**

`remote_watcher.py` -- Detects human changes on GitHub (PR comments/merges) and MC dashboard (task comments/status) (key exports: RemoteChange, RemoteWatcher) **[S07]**

`review_gates.py` -- Confidence-aware review depth: trainee/community tier gets adversarial challenge + architect review (key exports: ReviewGate, ReviewPipeline, build_review_pipeline) **[S13]**

`role_providers.py` -- Per-role data functions for heartbeat context (fleet-ops: approvals; PM: unassigned; architect: design reviews) (key exports: fleet_ops_provider, pm_provider, architect_provider) **[S22]**

`router_unification.py` -- AICP+fleet router merge (FUTURE), shared routing engine and backend registry (key exports: UnifiedRoutingRequest, UnifiedRouter) **[S14]**

`routing.py` -- Agent-to-task matching by capability, workload, status, task type analysis (key exports: AGENT_CAPABILITIES, suggest_agent, score_agent_fit) **[S07]**

`self_healing.py` -- Auto-resolves common fleet issues (stale reviews, offline agents, unassigned tasks) before escalating (key exports: HealingAction, auto_heal) **[S07]**

`session_manager.py` -- Context + rate limit dual countdown management, force compact before rollover (key exports: SessionAction, SessionManager) **[S19]**

`session_metrics.py` -- Per-session telemetry (timing, tools, tokens, errors) feeding into LaborStamp (key exports: SessionMetrics) **[S19]**

`session_telemetry.py` -- Parses Claude Code JSON session data, distributes real values to LaborStamp/ClaudeHealth/StormMonitor (key exports: SessionSnapshot, parse_session_json) **[S19]**

`shadow_routing.py` -- Dual-routes tasks to production and candidate model for comparison, non-blocking (key exports: ShadowResult, ShadowRouter) **[S16]**

`skill_enforcement.py` -- Ensures agents use required fleet tools per task type, missing tools lower confidence score (key exports: ToolRequirement, TASK_TYPE_REQUIREMENTS, check_skill_compliance) **[S21]**

`smart_chains.py` -- Batch multiple operations into single pre-computed results, saves 5+ tool calls per operation (key exports: DispatchChain, CompletionChain, ReviewChain) **[S22]**

`stage_context.py` -- Protocol instructions per methodology stage injected into heartbeat context (MUST/MUST NOT/CAN/HOW TO ADVANCE) (key exports: STAGE_INSTRUCTIONS, get_stage_context) **[S01]**

`standards.py` -- Artifact quality standards library: required fields, quality criteria, examples per artifact type (key exports: RequiredField, Standard, get_standard, check_standard) **[S09]**

`storm_analytics.py` -- Tracks storm frequency, duration, cost impact, indicator trends over time (key exports: StormRecord, StormAnalytics) **[S11]**

`storm_integration.py` -- Orchestrator-storm bridge: evaluate severity, apply graduated response, generate incident reports (key exports: StormResponse, evaluate_storm, apply_storm_response) **[S11]**

`storm_monitor.py` -- Monitors 9 indicators for token drain storms, 5 severity levels, auto-escalation/de-escalation (key exports: StormSeverity, StormMonitor) **[S11]**

`task_lifecycle.py` -- PRE->PROGRESS->POST enforcement: context loaded, plan shared, tests run, review gates populated (key exports: LifecycleStage, TaskLifecycle) **[S07]**

`task_scoring.py` -- Task priority scoring for dispatch ordering by priority, dependency depth, deadline, type, wait time (key exports: score_task, PRIORITY_SCORES) **[S07]**

`teaching.py` -- Adapted lessons, injection into context, comprehension verification through practice (key exports: DiseaseCategory, Lesson, TeachingSystem) **[S03]**

`tier_progression.py` -- Model trust progression tracking: trainee->trainee-validated->standard->expert based on approval rates (key exports: VALID_TIERS, TierRecord, TierProgressionTracker) **[S16]**

`trail_recorder.py` -- Complete audit trail per task: WHO/WHAT/WHEN/WHY for every action, stored as tagged board memory (key exports: TrailRecorder) **[S13]**

`transpose.py` -- Bidirectional object<->rich HTML with markers for Plane, agent works with dicts, Plane shows HTML (key exports: object_to_html, html_to_object) **[S10]**

`turboquant.py` -- TurboQuant KV cache compression config for extended context (FUTURE, depends on llama.cpp support) (key exports: TurboQuantConfig, calculate_extended_context) **[S16]**

`urls.py` -- Fleet URL resolver, generates cross-reference URLs from project config (key exports: ResolvedUrls, UrlResolver) **[S20]**

`velocity.py` -- Sprint velocity and metrics: SP/sprint, cycle time, agent throughput, progress projections (key exports: SprintMetrics, VelocityTracker) **[S07]**

---

### cli/ (18 modules)

`auth.py` -- CLI for token status check and refresh (key exports: run_auth) **[S20]**

`board.py` -- Board management CLI: info, tasks, cleanup, tags, custom fields listing (key exports: run_board) **[S07]**

`budget.py` -- View and manage budget modes CLI: show/set/list/report (key exports: run_budget) **[S12]**

`cache_cmd.py` -- Cache management CLI: stats, cleanup, export, import (key exports: run_cache) **[S20]**

`create.py` -- Task creation CLI with optional dispatch (key exports: run_create) **[S07]**

`daemon.py` -- Background daemons: sync, monitor, orchestrator loops with interval control (key exports: run_daemon) **[S07]**

`digest.py` -- Daily fleet activity digest generation and IRC posting (key exports: run_digest) **[S18]**

`dispatch.py` -- Task dispatch to agents via OpenClaw gateway WebSocket (key exports: run_dispatch) **[S07]**

`notify.py` -- IRC notification sending CLI (key exports: run_notify) **[S18]**

`orchestrator.py` -- The autonomous brain loop: approvals, transitions, dispatch, parent evaluation, driver wake (key exports: run_orchestrator_daemon, FleetOrchestrator) **[S07]**

`pause.py` -- Fleet kill switch: pause (kill all daemons, stop heartbeats) and resume (key exports: run_pause) **[S05]**

`plane.py` -- Plane CLI: list projects/issues/cycles/states, create issues, run bidirectional sync (key exports: run_plane) **[S17]**

`project.py` -- Project management CLI: add, list, check projects with git/remote setup (key exports: run_project) **[S20]**

`quality.py` -- Standards compliance quality check (conventional commits, PR hygiene) (key exports: run_quality) **[S09]**

`sprint.py` -- Sprint management CLI: load sprint plans from YAML, check sprint status (key exports: run_sprint) **[S07]**

`status.py` -- Comprehensive fleet status overview (agents, tasks, activity) (key exports: run_status) **[S07]**

`sync.py` -- MC tasks <-> GitHub PRs sync: merge detection, close stale, cleanup (key exports: run_sync) **[S07]**

`trace.py` -- Full task trace: MC + git + worktree + PR cross-reference (key exports: run_trace) **[S07]**

---

### mcp/ (3 modules)

`server.py` -- Fleet MCP server (FastMCP), exposes fleet operations as native agent tools via stdio transport (key exports: create_server, run_server) **[S08]**

`context.py` -- Shared state for MCP tool handlers: config, credentials, infra clients, initialized once per server (key exports: FleetMCPContext) **[S08]**

`tools.py` -- 25 MCP tool definitions: fleet_read_context, fleet_task_accept, fleet_task_progress, fleet_commit, fleet_task_complete, fleet_alert, fleet_pause, fleet_escalate, fleet_notify_human, fleet_chat, fleet_task_create, fleet_approve, fleet_agent_status, fleet_plane_status, fleet_plane_sprint, fleet_plane_sync, fleet_plane_create_issue, fleet_plane_comment, fleet_plane_update_issue, fleet_plane_list_modules, fleet_task_context, fleet_heartbeat_context, fleet_artifact_read, fleet_artifact_update, fleet_artifact_create, fleet_contribute, fleet_request_input, fleet_gate_request, fleet_transfer (key exports: register_tools) **[S08]**

---

### infra/ (8 modules)

`cache_sqlite.py` -- SQLite-backed persistent cache with TTL, implements core.cache.Cache (key exports: SQLiteCache) **[S20]**

`config_loader.py` -- YAML config and TOOLS.md credential loader, implements core.interfaces.ConfigLoader (key exports: ConfigLoader) **[S20]**

`gateway_client.py` -- OpenClaw Gateway WebSocket JSON-RPC wrapper: prune, compact, inject, fresh session (key exports: gateway_rpc, prune_session, compact_session) **[S20]**

`gh_client.py` -- GitHub client via gh CLI and git subprocess, implements core.interfaces.GitClient (key exports: GHClient) **[S20]**

`irc_client.py` -- IRC notification client via OpenClaw gateway WebSocket RPC (key exports: IRCClient) **[S20]**

`mc_client.py` -- Mission Control API client (httpx async), implements TaskClient, MemoryClient, ApprovalClient, AgentClient (key exports: MCClient) **[S20]**

`ntfy_client.py` -- Push notifications to human via ntfy.sh, priority routing to fleet-progress/fleet-review/fleet-alert topics (key exports: NtfyClient, PRIORITY_MAP, TOPIC_MAP) **[S18]**

`plane_client.py` -- Plane REST API client for issue tracking (httpx async), projects/issues/states/cycles/comments (key exports: PlaneClient, PlaneProject, PlaneState, PlaneIssue) **[S17]**

---

### templates/ (4 modules)

`comment.py` -- MC task comment formatters: accept, progress, complete, blocker with labor attribution (key exports: format_accept, format_progress, format_complete, format_blocker) **[S08]**

`irc.py` -- IRC one-line message formatters with emoji, agent name, event type, URL (key exports: format_event, format_task_started, format_task_blocked, format_merged, format_task_done, format_digest_summary) **[S18]**

`memory.py` -- Board memory entry formatters: alert, decision, suggestion, PR notification (key exports: format_alert, format_pr_notice, pr_tags) **[S08]**

`pr.py` -- Publication-quality PR body formatter with changelog, diff table, cross-refs, labor attribution (key exports: format_pr_body) **[S08]**

---

### Root

`__main__.py` -- CLI entry point and command dispatcher, 17 commands registered (key exports: main, COMMANDS) **[S07]**

---

### Summary

| Directory | Module Count | Systems Covered |
|-----------|-------------|-----------------|
| core/ | 94 | S01-S22 (all) |
| cli/ | 18 | S05, S07, S09, S12, S17, S18, S20 |
| mcp/ | 3 | S08 |
| infra/ | 8 | S17, S18, S20 |
| templates/ | 4 | S08, S18 |
| root | 1 | S07 |
| **Total** | **128** | **22 systems** |

(Count excludes `__init__.py` files which are empty package 
# Module Manuals — 128 Modules Mapped to 22 Systems

**Part of:** Fleet Knowledge Map → Module Manuals branch
**Purpose:** Per-module purpose, key exports, and system mapping.
**Source:** Read from actual Python module headers and docstrings.

---

## Fleet Module Manuals — Knowledge Map Branch

### SYSTEMS INDEX (for cross-reference)

| # | System Name |
|---|-------------|
| 01 | Methodology |
| 02 | Immune System |
| 03 | Teaching System |
| 04 | Event Bus |
| 05 | Control Surface |
| 06 | Agent Lifecycle |
| 07 | Orchestrator |
| 08 | MCP Tools |
| 09 | Standards |
| 10 | Transpose |
| 11 | Storm Prevention |
| 12 | Budget |
| 13 | Labor Attribution |
| 14 | Backend Router |
| 15 | Challenge / Iterative Validation |
| 16 | Model Upgrade |
| 17 | Plane Integration |
| 18 | Notifications |
| 19 | Session Management |
| 20 | Infrastructure |
| 21 | Agent Tooling |
| 22 | Agent Intelligence |

---

### core/ (94 modules)

`agent_lifecycle.py` -- Smart agent status management (ACTIVE/IDLE/SLEEPING/OFFLINE), silent heartbeat relay to brain after 1 HEARTBEAT_OK (key exports: AgentStatus, FleetLifecycle) **[S06]**

`agent_roles.py` -- Per-agent PR authority and quality domain definitions, rejection/approval/close permissions (key exports: PRAuthority, AgentRole, AGENT_ROLES) **[S22]**

`artifact_tracker.py` -- Progressive work tracking across operation cycles, checks artifact completeness against standards (key exports: ArtifactCompleteness, check_artifact_completeness) **[S09]**

`auth.py` -- Claude Code OAuth token refresh and validation, auto-rotation for gateway auth (key exports: get_current_claude_token, get_stored_token, refresh_token, token_needs_refresh) **[S20]**

`autocomplete.py` -- Context arrangement formatter for 8-layer onion order, arranges data from context_assembly/stage_context/config into agent system prompt sections (key exports: format_autocomplete_chain) **[S22]**

`backend_health.py` -- Real-time backend status dashboard (up/down/degraded), model loaded on LocalAI, OpenRouter availability, Claude quota status (key exports: BackendStatus, BackendHealthDashboard) **[S14]**

`backend_router.py` -- Multi-backend routing by task complexity, agent role, cost, and availability; cheapest capable backend wins; fallback chain LocalAI to OpenRouter to Claude (key exports: BackendRouter, RoutingDecision) **[S14]**

`behavioral_security.py` -- Cyberpunk-Zero behavioral analysis: scan task content for dangerous patterns, scan code diffs, flag suspicious human directives, set security_hold (key exports: SecurityFinding, BehavioralAnalyzer) **[S02]**

`board_cleanup.py` -- Archive noise tasks (done heartbeats, review process, conflict resolution), keep sprint work visible, track archives (key exports: CleanupResult, identify_noise_tasks) **[S07]**

`budget_analytics.py` -- Cost/quality/efficiency tracking per budget mode over time; compare same task type across modes; quality impact measurement (key exports: BudgetEvent, BudgetAnalytics) **[S12]**

`budget_modes.py` -- Fleet tempo settings (orchestrator cycle speed, heartbeat frequency); offset-based modes applied to base fleet.yaml config (key exports: BudgetMode, BUDGET_MODES, get_active_mode_name, get_mode) **[S12]**

`budget_monitor.py` -- Read real Claude quota via OAuth usage API; five_hour/seven_day utilization; fast climb detection; orchestrator pre-dispatch check (key exports: QuotaReading, check_quota) **[S12]**

`budget_ui.py` -- Data provider for OCMC header bar budget controls; per-order budget mode overrides (key exports: BudgetOverride, BudgetUIData) **[S12]**

`cache.py` -- Abstract cache interface (key-value with TTL), implemented by infra/cache_sqlite.py (key exports: Cache) **[S20]**

`chain_runner.py` -- Executes EventChains across all surfaces (INTERNAL/PUBLIC/CHANNEL/NOTIFY/PLANE/META), tolerant of partial failure (key exports: ChainRunner) **[S04]**

`challenge.py` -- Challenge loop data model (M-IV01): 4 challenge types (automated/agent/cross-model/scenario), challenge flow lifecycle (key exports: ChallengeType, ChallengeStatus, ChallengeRecord, ChallengeRound, ChallengeFinding) **[S15]**

`challenge_analytics.py` -- Aggregates challenge outcomes: per-agent pass rates, per-tier pass rates, average rounds to pass, common findings, teaching signals (key exports: ChallengeEvent, ChallengeAnalytics) **[S15]**

`challenge_automated.py` -- Deterministic zero-LLM-cost challenge generator from task metadata and code diffs: regression, edge cases, loops, async, timeout, architecture checks (key exports: AutomatedChallenge, generate_automated_challenges) **[S15]**

`challenge_cross_model.py` -- Uses a different LLM to challenge work produced by the original model; independent verification via LocalAI/OpenRouter/opus (key exports: CrossModelChallenger) **[S15]**

`challenge_deferred.py` -- FIFO queue for challenges deferred when conditions prevent execution; persists to state/deferred_challenges.json (key exports: DeferredChallenge, DeferredChallengeQueue) **[S15]**

`challenge_protocol.py` -- Challenge lifecycle orchestration (M-IV03): evaluate need, assign challenger, build context, run challenge, determine outcome (key exports: ChallengeContext, ChallengeProtocol) **[S15]**

`challenge_readiness.py` -- Integrates challenge status into readiness progression: 70% work complete, 80% challenge passed, 90% review passed, 95% PO approved (key exports: ReadinessCheckpoint, check_challenge_readiness) **[S15]**

`challenge_scenario.py` -- Reproduce-and-break testing for bug fixes: reproduction, boundary, concurrency, removal, interaction scenarios (key exports: ScenarioChallenge, generate_scenario_challenges) **[S15]**

`change_detector.py` -- Track what changed between orchestrator cycles; targeted reactions instead of blind polling; uses MC activity events or task list diff (key exports: Change, ChangeDetector) **[S07]**

`cluster_peering.py` -- Machine 1 to Machine 2 LocalAI cluster peering config; load balancing and failover (FUTURE) (key exports: ClusterNode, ClusterPeering) **[S16]**

`codex_review.py` -- Trigger and decision layer for adversarial reviews via codex-plugin-cc; confidence tier and budget mode driven (key exports: CodexReviewDecision) **[S14]**

`config_sync.py` -- Keep IaC YAML configs in sync with live Plane state; batch changes and commit periodically (key exports: ConfigSync) **[S17]**

`config_watcher.py` -- Detect when IaC config files are modified; emit events for fleet.yaml, agent-identities.yaml, projects.yaml, DSPD configs (key exports: ConfigWatcher) **[S04]**

`context_assembly.py` -- Shared data aggregation for MCP calls and pre-embed; single source of truth for task and heartbeat context bundles (key exports: assemble_task_context, assemble_heartbeat_context, clear_context_cache) **[S22]**

`context_writer.py` -- Writes pre-embed data to agent context files (fleet-context.md, task-context.md) that the gateway injects into system prompt (key exports: write_heartbeat_context, write_task_context) **[S22]**

`contributions.py` -- Cross-agent synergy: create contribution subtasks from synergy matrix, check completeness, block dispatch until required contributions arrive (key exports: ContributionManager) **[S22]**

`cross_refs.py` -- Automated cross-referencing across surfaces: task to Plane, PR to OCMC, Plane to IRC, sprint announcements (key exports: CrossReference, generate_cross_refs) **[S04]**

`directives.py` -- PO commands routed to agents via board memory tags; orchestrator reads and routes to target agent or fleet (key exports: Directive, parse_directives) **[S05]**

`doctor.py` -- Immune system active component: observe agents, detect disease, produce interventions (prune, force compact, trigger teaching); runs in orchestrator cycle (key exports: DoctorReport, Doctor) **[S02]**

`driver.py` -- Autonomous driver model for agents that create their own work; priority: human-assigned, dependency unblocking, own roadmap, fleet improvement (key exports: ProductRoadmap, DriverPriority) **[S06]**

`dual_gpu.py` -- Dual-GPU configuration for two simultaneous models when 19GB VRAM available (FUTURE) (key exports: GPUSlot, DualGPUConfig) **[S16]**

`error_reporter.py` -- File-based agent error reporting; agents write errors, orchestrator reads each cycle to detect outages (key exports: AgentError, write_error, read_errors) **[S07]**

`event_chain.py` -- Multi-surface event chain definitions; single fleet operation produces events across INTERNAL/PUBLIC/CHANNEL/NOTIFY/PLANE/META (key exports: EventSurface, Event, EventChain, ChainResult) **[S04]**

`event_display.py` -- Render same event differently per channel: IRC compact, Plane rich HTML, ntfy title+body, heartbeat structured, board memory tagged (key exports: render_irc, render_plane, render_ntfy) **[S04]**

`event_router.py` -- Deterministic event-to-agent matching by capability, tags, role, mentions, project association (key exports: EventRouter, AGENT_TAG_SUBSCRIPTIONS) **[S04]**

`events.py` -- CloudEvents-based event store and agent feeds; persistent, filterable, tracked per-agent seen/unseen (key exports: FleetEvent, EventStore, create_event, EVENT_TYPES) **[S04]**

`federation.py` -- Multi-machine fleet identity and collaboration; fleet ID, agent prefix namespace, identity generation and persistence (key exports: FleetIdentity) **[S20]**

`fleet_mode.py` -- Fleet control state from board: work mode, cycle phase, backend mode; three independent axes (key exports: FleetControlState, read_fleet_control, should_dispatch) **[S05]**

`gateway_guard.py` -- Detect and clean stale/duplicate gateway processes; prevent March 2026 catastrophe recurrence (key exports: GatewayProcess, GatewayGuard) **[S11]**

`health.py` -- Fleet health monitoring: stuck agents, stale tasks, offline agents, stale worktrees, service connectivity (key exports: HealthIssue, HealthReport, check_fleet_health) **[S07]**

`heartbeat_context.py` -- Pre-compute agent context bundle without AI; saves 3-5 tool calls per heartbeat; direct API calls, no tokens consumed (key exports: HeartbeatBundle, bundle_heartbeat_context) **[S22]**

`heartbeat_gate.py` -- Brain evaluation for idle/sleeping agents; deterministic Python check (FREE, no Claude call); WAKE/SILENT decision; ~70% cost reduction (key exports: HeartbeatDecision, HeartbeatGate) **[S06]**

`heartbeat_stamp.py` -- Minimal labor stamps for heartbeats to track cost trends and detect expensive heartbeats (key exports: create_heartbeat_stamp) **[S13]**

`incident_report.py` -- Post-incident report generation after WARNING+ storm events; severity, duration, cost impact, responses, prevention recommendations (key exports: ResponseEntry, StormEvent, IncidentReport) **[S11]**

`interfaces.py` -- Abstract contracts for infrastructure adapters: TaskClient, MemoryClient, ApprovalClient, AgentClient, GitClient, NotificationClient, ConfigLoader (key exports: TaskClient, MemoryClient, ApprovalClient, AgentClient, GitClient, NotificationClient, ConfigLoader) **[S20]**

`labor_analytics.py` -- Aggregate labor stamps: cost per agent, per model, per confidence tier, approval rate per tier (key exports: AgentCostMetrics, LaborAnalytics) **[S13]**

`labor_stamp.py` -- Provenance tracking for fleet-produced artifacts; confidence tiers (expert/standard/trainee/community/hybrid); populated by infrastructure (key exports: LaborStamp, derive_confidence_tier, assemble_stamp) **[S13]**

`memory_structure.py` -- Agent memory organization: MEMORY.md, codebase_knowledge.md, project_decisions.md, task_history.md, team_context.md (key exports: MEMORY_FILES, create_memory_structure) **[S22]**

`methodology.py` -- Stage progression (conversation/analysis/investigation/reasoning/work), protocol checks, readiness gate; work protocol only at 99-100% (key exports: Stage, VALID_READINESS, MethodologyCheck) **[S01]**

`model_benchmark.py` -- Benchmark LocalAI models against each other on fleet-representative prompts: heartbeat, task acceptance, simple review, structured JSON (key exports: BenchmarkPrompt, BenchmarkResult, ModelBenchmark) **[S16]**

`model_configs.py` -- LocalAI model configuration templates for current and upgrade-candidate models; YAML format compatible with LocalAI (key exports: ModelConfig) **[S16]**

`model_promotion.py` -- Default model promotion lifecycle: config switch, monitoring, pre/post promotion approval rate tracking (key exports: PromotionRecord, ModelPromotion) **[S16]**

`model_selection.py` -- Dynamic model (opus/sonnet) and effort level (low/medium/high/max) selection based on task complexity, type, story points, agent role (key exports: ModelSelection, select_model) **[S14]**

`model_swap.py` -- Router-initiated LocalAI model swaps for single-active-backend constraint; swap protocol with skip-swap logic and metrics (key exports: SwapRecord, ModelSwapManager) **[S14]**

`models.py` -- Pure domain data structures: Task, TaskStatus, Agent, AgentRole, Approval, BoardMemoryEntry, Project, PullRequest, Commit, FleetContext, TaskCustomFields, AlertSeverity (key exports: Task, TaskStatus, Agent, Approval, Project, PullRequest, Commit, FleetContext) **[S20]**

`notification_router.py` -- Classify events as info/important/urgent and route to ntfy/IRC/Windows toast; deduplication to prevent spam (key exports: NotificationLevel, NotificationRouter) **[S18]**

`ocmc_watcher.py` -- Detect Mission Control state changes (task status, approvals, agent online/offline, board memory) and emit CloudEvents (key exports: OCMCWatcher) **[S04]**

`openai_client.py` -- OpenAI-compatible HTTP client for LocalAI and OpenRouter free tier; unified chat completions interface (key exports: ChatMessage, ChatCompletion, OpenAIClient) **[S14]**

`outage_detector.py` -- Detect API outages and rate limits; exponential backoff; orchestrator checks before each cycle (key exports: ServiceState, OutageDetector) **[S07]**

`phases.py` -- PO-defined delivery maturity progression; unlimited phases, any name, any progression, any standards; loaded from config/phases.yaml (key exports: PhaseDefinition, PhaseProgression) **[S01]**

`plane_methodology.py` -- Read/write methodology fields on Plane issues via labels (stage:, readiness:) and description HTML markers (key exports: VALID_READINESS, VALID_STAGES, parse_methodology_labels) **[S17]**

`plane_sync.py` -- Plane to OCMC bidirectional sync: ingest from Plane, push completions to Plane; mapping stored in OCMC custom fields (key exports: PlaneSyncer) **[S17]**

`plane_watcher.py` -- Poll Plane API for changes (new issues, state changes, comments, cycle status), emit CloudEvents (key exports: PlaneWatcher) **[S17]**

`plan_quality.py` -- Validate agent plans meet minimum quality standards: concrete steps, verification approach, risk awareness, estimated scope (key exports: PlanAssessment, assess_plan_quality) **[S01]**

`preembed.py` -- Pre-embedded FULL context data injected before agent starts; not compressed, not summarized; complete data set per role (key exports: format_events, format_task_preembed, format_heartbeat_preembed) **[S22]**

`pr_hygiene.py` -- Detect and resolve stale, conflicting, duplicate, orphaned, and long-open PRs; produce recommended actions (key exports: PRIssue, check_pr_hygiene) **[S07]**

`remote_watcher.py` -- Detect changes made by humans outside the fleet: GitHub PR comments/merges, MC task comments/status changes (key exports: RemoteChange, RemoteWatcher) **[S04]**

`review_gates.py` -- Confidence-aware review depth: trainee/community tier gets adversarial challenge + architect review; expert/standard gets standard review (key exports: ReviewGate, ReviewRequirements) **[S13]**

`role_providers.py` -- Per-role data functions for heartbeat context: fleet-ops gets approvals, PM gets unassigned tasks, architect gets design reviews (key exports: fleet_ops_provider, pm_provider, architect_provider) **[S22]**

`router_unification.py` -- AICP router merge with fleet backend router (FUTURE, Stage 3); shared routing engine, backend registry, budget awareness (key exports: UnifiedRoutingRequest) **[S14]**

`routing.py` -- Agent routing: match tasks to agents by capability, availability, workload, status; used by PM and orchestrator for auto-assignment (key exports: AGENT_CAPABILITIES, suggest_agent) **[S07]**

`self_healing.py` -- Auto-resolve common fleet issues: stale review tasks, offline agents with work, unassigned inbox tasks; escalate if unresolvable (key exports: HealingAction, auto_heal) **[S07]**

`session_manager.py` -- Context + rate limit awareness (two parallel countdowns); 7%/5% context threshold, 85%/90% rate limit threshold; aggregate fleet math (key exports: SessionAction, SessionManager) **[S19]**

`session_metrics.py` -- Per-session telemetry: timing, tools called, token estimates, errors; feeds into LaborStamp via assemble_stamp() (key exports: SessionMetrics) **[S13]**

`session_telemetry.py` -- Parse Claude Code JSON session data and distribute real values to LaborStamp, ClaudeHealth, StormMonitor (key exports: SessionSnapshot, distribute_telemetry) **[S19]**

`shadow_routing.py` -- Dual-route tasks to production and candidate model for comparison; non-blocking, candidate response recorded for analysis only (key exports: ShadowResult, ShadowRouter) **[S16]**

`skill_enforcement.py` -- Required tool usage per task type: code tasks MUST use fleet_commit, review tasks MUST use fleet_approve; missing tools lower confidence score (key exports: ToolRequirement, TASK_TYPE_REQUIREMENTS, check_skill_compliance) **[S21]**

`smart_chains.py` -- Batch multiple operations into single pre-computed results: dispatch_chain, completion_chain, review_chain; saves token-consuming tool calls (key exports: DispatchChain, CompletionChain, ReviewChain) **[S22]**

`stage_context.py` -- Protocol instructions per methodology stage; MUST/MUST NOT/CAN/HOW TO ADVANCE templates injected into heartbeat context (key exports: STAGE_INSTRUCTIONS, get_stage_context) **[S01]**

`standards.py` -- Standards library: what "done right" looks like for every artifact type; required fields, quality criteria, examples (key exports: Standard, RequiredField, get_standard, check_standard) **[S09]**

`storm_analytics.py` -- Storm frequency, duration, cost impact, indicator trends over time; feeds into prevention improvements (key exports: StormRecord, StormAnalytics) **[S11]**

`storm_integration.py` -- Orchestrator-to-storm-monitor logic layer: evaluate severity, apply graduated response, track events, generate incident reports (key exports: StormResponse, evaluate_storm) **[S11]**

`storm_monitor.py` -- Monitor 9 indicators for storm conditions; severity levels CLEAR/WATCH/WARNING/STORM/CRITICAL; de-escalation slower than escalation (key exports: StormSeverity, StormMonitor) **[S11]**

`task_lifecycle.py` -- PRE/PROGRESS/POST enforcement: context loaded, plan shared, dependencies checked, commits, tests, review gates (key exports: LifecycleStage, TaskLifecycle) **[S07]**

`task_scoring.py` -- Intelligent dispatch ordering by priority, dependency chain depth, sprint deadline proximity, task type, time waiting (key exports: score_task, PRIORITY_SCORES) **[S07]**

`teaching.py` -- Adapted lessons, injection, comprehension verification; pattern-based learning ("forging the right path multiple times"); responds to immune system triggers (key exports: DiseaseCategory, Lesson, TeachingSystem) **[S03]**

`tier_progression.py` -- Model trust earned through observed performance; trainee to trainee-validated to standard to expert; PO decides promotion (key exports: VALID_TIERS, TierRecord, TierProgressionTracker) **[S16]**

`trail_recorder.py` -- Complete audit trail per task: WHO (agent+model), WHAT (action), WHEN (timestamp), WHY (context); stored as tagged board memory entries (key exports: TrailRecorder, record_trail) **[S13]**

`transpose.py` -- Bidirectional object-to-rich-HTML conversion; agents work with structured dicts, Plane shows rich HTML; HTML comment markers for machine-parseability (key exports: object_to_html, html_to_object) **[S10]**

`turboquant.py` -- TurboQuant KV cache compression config (FUTURE); 6x memory reduction calculations for extended context windows (key exports: TurboQuantConfig, calculate_extended_context) **[S16]**

`urls.py` -- Fleet URL resolver: generates cross-reference URLs for tasks, boards, PRs, branches, commits from config (key exports: ResolvedUrls, UrlResolver) **[S20]**

`velocity.py` -- Sprint velocity and metrics: story points per sprint, task cycle time, agent throughput, sprint progress, blocker resolution time (key exports: SprintMetrics, calculate_velocity) **[S07]**

---

### cli/ (18 modules)

`__main__.py` -- CLI entry point and command dispatcher; routes to all subcommands (key exports: main, COMMANDS) **[S20]**

`auth.py` -- CLI for token status check and refresh (key exports: run_auth) **[S20]**

`board.py` -- Board management CLI: info, tasks, cleanup, tags, custom fields (key exports: run_board) **[S05]**

`budget.py` -- Budget mode CLI: view current mode, set mode, list modes, cost report (key exports: run_budget) **[S12]**

`cache_cmd.py` -- Cache management CLI: stats, cleanup, export, import (key exports: run_cache) **[S20]**

`create.py` -- Task creation CLI: create and optionally dispatch tasks (key exports: run_create) **[S07]**

`daemon.py` -- Background daemon manager: sync, monitor, orchestrator loops with intervals (key exports: run_daemon) **[S07]**

`digest.py` -- Daily fleet digest generation and posting to IRC (key exports: run_digest) **[S18]**

`dispatch.py` -- Task dispatch CLI: send tasks to agents via OpenClaw gateway WebSocket (key exports: run_dispatch) **[S07]**

`notify.py` -- IRC notification CLI: send messages to IRC channels (key exports: run_notify) **[S18]**

`orchestrator.py` -- The autonomous brain: approval processing, task transitions, dispatch, parent evaluation, driver heartbeats; main orchestrator loop (key exports: run_orchestrator_daemon, Orchestrator) **[S07]**

`pause.py` -- Fleet kill switch: pause (kill daemons, stop heartbeats, notify) and resume (key exports: run_pause) **[S05]**

`plane.py` -- Plane CLI: list projects/issues/cycles/states, create issues, run bidirectional sync (key exports: run_plane) **[S17]**

`project.py` -- Project management CLI: add, list, check projects with git init and remote creation (key exports: run_project) **[S20]**

`quality.py` -- Quality compliance checks: conventional commits, PR standards (key exports: run_quality) **[S09]**

`sprint.py` -- Sprint management CLI: load sprint YAML plans, check sprint status (key exports: run_sprint) **[S07]**

`status.py` -- Comprehensive fleet status overview: agents, tasks, activity (key exports: run_status) **[S07]**

`sync.py` -- MC tasks to GitHub PRs bidirectional sync: merge, close, cleanup (key exports: run_sync) **[S07]**

`trace.py` -- Full task trace: MC + git + worktree + PR cross-referenced view (key exports: run_trace) **[S07]**

---

### mcp/ (3 modules)

`server.py` -- Fleet MCP server: FastMCP instance exposing fleet operations as native agent tools via stdio transport (key exports: create_server, run_server) **[S08]**

`context.py` -- MCP shared state: loads config, credentials, creates infra clients; initialized once per server instance (key exports: FleetMCPContext) **[S08]**

`tools.py` -- 25 MCP tool definitions: fleet_read_context, fleet_task_accept, fleet_task_progress, fleet_commit, fleet_task_complete, fleet_alert, fleet_pause, fleet_escalate, fleet_notify_human, fleet_chat, fleet_task_create, fleet_approve, fleet_agent_status, fleet_plane_status, fleet_plane_sprint, fleet_plane_sync, fleet_plane_create_issue, fleet_plane_comment, fleet_plane_update_issue, fleet_plane_list_modules, fleet_task_context, fleet_heartbeat_context, fleet_artifact_read, fleet_artifact_update, fleet_artifact_create, fleet_contribute, fleet_request_input, fleet_gate_request, fleet_transfer (key exports: register_tools) **[S08]**

---

### infra/ (8 modules)

`cache_sqlite.py` -- SQLite-backed persistent cache with TTL; implements core.cache.Cache; supports export for backup (key exports: SQLiteCache) **[S20]**

`config_loader.py` -- YAML config loader and TOOLS.md credential reader; implements core.interfaces.ConfigLoader (key exports: ConfigLoader) **[S20]**

`gateway_client.py` -- OpenClaw Gateway WebSocket JSON-RPC wrapper: sessions.delete (prune), sessions.compact, chat.send (inject), sessions.patch (fresh session) (key exports: gateway_rpc, prune_session, compact_session) **[S20]**

`gh_client.py` -- GitHub/git operations via subprocess (gh CLI + git); implements core.interfaces.GitClient (key exports: GHClient) **[S20]**

`irc_client.py` -- IRC notification via OpenClaw gateway WebSocket RPC; implements core.interfaces.NotificationClient (key exports: IRCClient) **[S20]**

`mc_client.py` -- Mission Control API client via httpx; implements TaskClient, MemoryClient, ApprovalClient, AgentClient (key exports: MCClient) **[S20]**

`ntfy_client.py` -- ntfy.sh push notifications with priority routing; topics fleet-progress/fleet-review/fleet-alert (key exports: NtfyClient, PRIORITY_MAP, TOPIC_MAP) **[S18]**

`plane_client.py` -- Plane REST API client via httpx; issue CRUD, cycles, states, comments (key exports: PlaneClient, PlaneProject, PlaneState, PlaneIssue) **[S17]**

---

### templates/ (4 modules)

`comment.py` -- MC task comment formatters: accept, progress, complete, blocker; completion comments include labor attribution provenance table (key exports: format_accept, format_progress, format_complete, format_blocker) **[S08]**

`irc.py` -- IRC message formatters: structured one-line messages with emoji, agent name, event type, URL (key exports: format_event, format_task_started, format_task_blocked, format_merged, format_task_done, format_digest_summary) **[S18]**

`memory.py` -- Board memory entry formatters: alert, decision, suggestion, PR notification (key exports: format_alert, format_pr_notice, pr_tags) **[S08]**

`pr.py` -- PR body formatter: publication-quality descriptions with changelog, diff table, cross-references, labor attribution provenance (key exports: format_pr_body) **[S08]**

---

### Summary

| Directory | Module Count | Primary Systems |
|-----------|-------------|-----------------|
| core/ | 94 | S01-S22 (all systems) |
| cli/ | 18 + __main__.py | S05, S07, S09, S12, S17, S18, S20 |
| mcp/ | 3 | S08 |
| infra/ | 8 | S17, S18, S20 |
| templates/ | 4 | S08, S18 |
| **Total** | **128 entries** (excluding `__init__.py` files) | |

### System Coverage Count (modules per system)

| System | # Modules | Key Modules |
|--------|-----------|-------------|
| S01 Methodology | 4 | methodology, phases, plan_quality, stage_context |
| S02 Immune System | 2 | doctor, behavioral_security |
| S03 Teaching | 1 | teaching |
| S04 Event Bus | 7 | events, event_chain, event_router, event_display, chain_runner, cross_refs, config_watcher, ocmc_watcher, remote_watcher |
| S05 Control Surface | 3 | fleet_mode, directives, board(cli), pause(cli) |
| S06 Agent Lifecycle | 3 | agent_lifecycle, heartbeat_gate, driver |
| S07 Orchestrator | 14 | orchestrator, health, self_healing, change_detector, outage_detector, task_lifecycle, task_scoring, routing, velocity, error_reporter, pr_hygiene, board_cleanup + cli |
| S08 MCP Tools | 6 | mcp/server, mcp/tools, mcp/context, templates/comment, templates/memory, templates/pr |
| S09 Standards | 2 | standards, artifact_tracker + quality(cli) |
| S10 Transpose | 1 | transpose |
| S11 Storm Prevention | 4 | storm_monitor, storm_integration, storm_analytics, incident_report, gateway_guard |
| S12 Budget | 5 | budget_modes, budget_monitor, budget_analytics, budget_ui + budget(cli) |
| S13 Labor Attribution | 6 | labor_stamp, labor_analytics, session_metrics, heartbeat_stamp, review_gates, trail_recorder |
| S14 Backend Router | 7 | backend_router, backend_health, model_selection, model_swap, openai_client, codex_review, router_unification |
| S15 Challenge | 8 | challenge, challenge_protocol, challenge_automated, challenge_cross_model, challenge_scenario, challenge_readiness, challenge_deferred, challenge_
