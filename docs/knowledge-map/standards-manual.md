# Standards Manual — Fleet Knowledge Map

**Date:** 2026-04-02
**Source:** 8 standard documents + `fleet/core/standards.py`
**Purpose:** Dense reference for every standard governing fleet agent files, brain modules, IaC, and artifact quality.

---

## agent.yaml Standard

**Governs:** Gateway configuration and fleet identity for each agent -- the ONLY file both gateway and orchestrator read.

**Required fields (14):**
`name` (fleet-role format), `display_name`, `fleet_id`, `fleet_number`, `username` (= name), `type` ("agent"), `mode` ("heartbeat"), `backend` ("claude"/"localai"), `model` ("opus"/"sonnet"), `mission` (one-line), `capabilities` (4-8 items), `roles.primary`, `roles.contributes_to`, `heartbeat_config.every`

**Key constraints:**
- Name format: `{fleet_id}-{role}` (e.g., "alpha-architect")
- Display name format: `{Role} {Fleet}` (e.g., "Architect Alpha")
- Capabilities must be role-specific, no generic items, no overlap with other roles
- `roles.primary` must match one of the 10 canonical role names
- `contributes_to` must match the synergy matrix (fleet-elevation/15)
- Model: opus for PM/fleet-ops/architect/devsecops; sonnet for workers (brain can override per dispatch)

**Roles that write it:** Provisioned by `scripts/provision-agents.sh` from `agents/_template/agent.yaml.template` + `config/agent-identities.yaml`.

**Validation:** `scripts/validate-agents.sh` -- checks all 14 fields present, identity consistency across fleet, content quality (mission specificity, capability count), gateway compatibility (valid type/mode/backend/model/interval), and cross-file integration with AGENTS.md synergy and agent-tooling.yaml skills.

---

## IDENTITY.md + SOUL.md Standard

**Governs:** Agent identity grounding (position 1) and behavioral values/anti-corruption rules (position 2) -- the constant inner layer.

### IDENTITY.md Required Sections (4):
1. **Who You Are** -- name, display_name, fleet, fleet_number, username, role + one-line definition
2. **Your Specialty** -- 3-5 sentences of deep domain expertise (must include role-specific knowledge items per table)
3. **Your Personality** -- 2-3 sentences, role-specific communication style
4. **Your Place in the Fleet** -- 3-5 sentences referencing at least 3 other agents by role, matching synergy map

### SOUL.md Required Sections (5):
1. **Values** -- 3-5 role-specific value statements (per-role content specified)
2. **Anti-Corruption Rules** -- exactly 10 rules, shared text across all agents (sacrosanct verbatim, don't summarize, don't replace words, don't add scope, don't compress, don't skip reading, no code outside work, three corrections = wrong, follow autocomplete chain, ask don't guess)
3. **What I Do** -- 3-5 scope statements
4. **What I Do NOT Do** -- 3-5 refusals with "(that's the {role})" redirects
5. **Humility** -- must contain "not infallible," "update assumption," "ask rather than guess"

**Key constraints:**
- IDENTITY.md must use "top-tier" or equivalent expertise language, never "you are an agent"
- Identity fields must match agent.yaml values exactly
- SOUL.md anti-corruption rules are exact text from fleet-elevation/20
- No concern mixing: no rules (CLAUDE.md), no tools (TOOLS.md), no dynamic data, no action protocol
- SOUL.md / CLAUDE.md boundary: values/full anti-corruption in SOUL.md; rules/summary in CLAUDE.md

**Roles that write it:** Provisioned from `agents/_template/IDENTITY.md.template` and `SOUL.md.template`.

**Validation:** `scripts/validate-agents.sh` -- fleet identity field presence, "top-tier" language, specialty specificity (min 3 items), synergy consistency, all 10 anti-corruption rules present (key phrase match), humility section presence.

---

## CLAUDE.md Standard

**Governs:** Role-specific behavioral constraints -- injected at position 3 (high influence for Lost in the Middle effect).

**Required sections (8, in order):**
1. **Core Responsibility** -- ONE sentence, what the role DOES (not what they are)
2. **Role-Specific Rules** -- largest section, unique per role (PM: task assignment/PO routing/sprint; fleet-ops: 7-step review/approval; architect: patterns/investigation; etc.)
3. **Stage Protocol** -- behavior per methodology stage (conversation/analysis/investigation/reasoning/work)
4. **Tool Chains** -- 4-8 tools with chain patterns, format: `fleet_{name}() -> {chain} (stage: {when})`
5. **Contribution Model** -- what this agent gives/receives per synergy matrix
6. **Boundaries** -- min 3 explicit refusals with "(that's the {role})" redirects
7. **Context Awareness** -- both countdowns (context remaining 7%/5%, rate limit session), shared text ~200 chars
8. **Anti-Corruption** -- brief summary ~150 chars, reinforcement of SOUL.md rules

**Key constraints:**
- MAX 4000 characters (gateway-enforced)
- Budget: ~2000 chars role-specific rules, ~400 stage, ~500 tools, ~350 contribution, ~250 boundaries, ~200 context, ~150 anti-corruption, ~100 title
- Every line must be role-specific -- no generic advice applicable to all agents
- No concern mixing: no personality (IDENTITY.md), no values (SOUL.md), no tool docs with params (TOOLS.md), no colleague descriptions (AGENTS.md), no dynamic data (context/), no action protocol (HEARTBEAT.md)
- PM and fleet-ops have stage protocol variations (PM manages others' stages, fleet-ops reviews)

**Roles that write it:** Provisioned from `agents/_template/CLAUDE.md/{role}.md`, content sourced from fleet-elevation/05-14.

**Validation:** `scripts/validate-agents.sh` -- char count <= 4000, all 8 sections in order, core responsibility is one sentence, no section empty or > 2500 chars, tool names match fleet/mcp/tools.py, boundaries min 3 with redirects, both countdowns mentioned, no concern mixing, contribution model matches synergy matrix.

---

## HEARTBEAT.md Standard

**Governs:** The action protocol -- injected LAST (position 8), tells the agent "what to do NOW" after absorbing all context.

**Universal priority order (all agents):**
0. PO Directives (highest -- execute immediately)
1. Messages (@mentions -- respond to all)
2. Core Job (role-specific)
3. Proactive Contributions (role-specific)
4. Health/Monitoring (role-specific)
5. HEARTBEAT_OK (ONLY if nothing above needs attention -- always last)

**Five heartbeat types (not 10):**
1. **PM** -- drives board: task assignment (ALL fields), contribution check, gate routing (50%/90%), stage progression, sprint management, epic breakdown
2. **Fleet-Ops** -- processes approvals: 4-step real review (read work, verify trail, check quality, decide), board health monitoring, methodology compliance
3. **Architect** -- stage-driven work + design contributions + architecture health monitoring, investigation always min 2 options
4. **DevSecOps** -- security contributions (SPECIFIC requirements), PR security review, security_hold mechanism, crisis response (1 of 2 agents active during crisis)
5. **Worker** (engineer/devops/QA/writer/UX/accountability) -- shared template with stage-driven work + per-role variations in work stage and contribution protocol

**Key constraints:**
- HEARTBEAT_OK is ALWAYS last -- never skip priorities 0-4
- Stage awareness mandatory: conversation/analysis/investigation/reasoning/work
- No code/commits outside work stage (stated explicitly)
- Work stage requires readiness >= 99
- No concern mixing: no identity, no rules, no tool docs, no colleague descriptions, no dynamic data

**Roles that write it:** Provisioned from `agents/_template/heartbeats/{pm,fleet-ops,architect,devsecops,worker}.md`.

**Validation:** `scripts/validate-agents.sh` -- priority order preserved, HEARTBEAT_OK last, core job role-specific, stage awareness present, no code outside work stage mentioned, readiness >= 99 prerequisite stated, tools referenced exist in fleet/mcp/tools.py, contribution types match synergy matrix.

---

## TOOLS.md + AGENTS.md Standard

**Governs:** Chain-aware tool reference (position 4) and fleet awareness/synergy knowledge (position 5).

### TOOLS.md Required Format Per Tool (5 fields):
- **What:** primary action (one line)
- **When:** stage/conditions for use
- **Chain:** automatic downstream effects
- **Input:** key parameters
- **You do NOT need to:** what the chain handles (prevents manual duplication)

Key tools documented: `fleet_task_create` (PM), `fleet_approve` (fleet-ops), `fleet_commit` (workers, work stage ONLY), `fleet_task_complete` (triggers 12+ operations), `fleet_artifact_create/update`, `fleet_contribute`, `fleet_chat`, `fleet_gate_request`, `fleet_escalate`, `fleet_read_context`, `fleet_task_accept`, `fleet_alert`.

### AGENTS.md Required Format Per Colleague (3 fields):
- **Contributes to me:** what they provide + when
- **I contribute to them:** what I provide + when
- **When to @mention:** specific conditions (not "when needed")

**Key constraints:**
- Both files are GENERATED (not hand-written) -- TOOLS.md from `fleet/mcp/tools.py` + fleet-elevation/24 call trees + agent-tooling.yaml; AGENTS.md from fleet-elevation/15 synergy matrix + agent-identities.yaml
- AGENTS.md: all 9 other agents listed, bidirectional consistency enforced
- TOOLS.md: only tools the role actually uses, no extra tools
- `fleet_commit` and `fleet_task_complete` blocked outside work stage (returns error + protocol_violation event)
- No concern mixing in either file

**Validation:** `scripts/validate-agents.sh` -- all 5 fields per tool, tool names match code, chain descriptions match call trees, stage restrictions documented, 9 colleagues listed, bidirectional contribution consistency, display names match agent.yaml.

---

## context/ Files Standard

**Governs:** Dynamic data layer -- `fleet-context.md` (position 6) and `task-context.md` (position 7) -- refreshed every 30s by the orchestrator.

### fleet-context.md Required Sections (7, in order):
1. Fleet State (work_mode, cycle_phase, backend_mode, agents online)
2. PO Directives (active directives for this agent or "all")
3. Messages (@mentions since last heartbeat, full content)
4. Assigned Tasks (FULL task details: verbatim, stage, readiness, artifacts, comments)
5. Role Data (PM: unassigned tasks/sprint metrics; fleet-ops: pending approvals/review queue; architect: design-needed tasks; devsecops: PRs for security review; workers: artifact state/completeness %)
6. Events (relevant events since last heartbeat)
7. Context Awareness (context usage %, rate limit usage %)

### task-context.md Autocomplete Chain (10 sections, ORDER IS CRITICAL):
1. `YOU ARE: {name} ({role})` -- identity grounding
2. `YOUR TASK: {title}` -- task focus
3. `YOUR STAGE: {stage}` -- stage awareness
4. `READINESS: {readiness}%` -- progress
5. `VERBATIM REQUIREMENT` -- PO's exact words, NEVER summarized (the anchor)
6. `STAGE PROTOCOL` -- MUST/MUST NOT/CAN from stage_context.py
7. `INPUTS FROM COLLEAGUES` -- contributions received
8. `DELIVERY PHASE: {phase}` -- phase quality bar
9. `WHAT TO DO NOW` -- action directive
10. `WHAT HAPPENS WHEN YOU ACT` -- chain documentation

**Key constraints:**
- NEVER compressed or summarized -- full data always (PO requirement)
- Files are GENERATED by orchestrator code (preembed.py, context_assembly.py), not hand-written
- Section order in task-context.md IS the autocomplete chain -- fixed, not configurable
- Verbatim requirement NEVER modified
- Dependencies point INWARD (context/ references CLAUDE.md/IDENTITY.md, not reverse)
- Standard enforced in CODE + unit tests, not in templates

**Validation:** Unit tests in brain code -- all sections present in order, verbatim unmodified, stage protocol matches stage_context.py, contributions included when received, action directive stage/role-appropriate.

---

## Brain Modules Standard

**Governs:** Orchestrator and all brain modules -- deterministic Python logic, no AI/LLM calls.

**Existing modules (15):** orchestrator.py (9-step cycle, target 13), preembed.py, context_assembly.py, stage_context.py, role_providers.py, agent_lifecycle.py, budget_modes.py, fleet_mode.py, smart_chains.py, doctor.py (4/11 diseases), teaching.py, storm_monitor.py, budget_monitor.py, session_telemetry.py, change_detector.py

**New modules to create (9):**
1. **chain_registry.py** -- event-to-handler mapping, max cascade depth 5, partial failure tolerant
2. **chain_handlers.py** -- 11 standard handlers (contribution opportunities, stage change notify, checkpoint, gate enforcement, create PR, move to review, create approval, evaluate parent, propagate contribution, transition to done, regress task)
3. **logic_engine.py** -- 11 dispatch gates (fleet mode, cycle phase, task unblocked, agent online, not busy, doctor clear, readiness appropriate, PO gate passed, contributions received, phase prerequisites, rate limit position safe)
4. **autocomplete.py** -- builds engineered autocomplete chain (7 sections in fixed order: identity, verbatim, stage protocol, contributions, phase standards, action directive, chain documentation)
5. **session_manager.py** -- rate limit session management, context evaluation (dump threshold ~50K tokens, rollover awareness, aggregate math: 5x200K = 1M)
6. **heartbeat_gate.py** -- silent heartbeat interception (cron never stops, gate filters Claude calls vs silent OK, < 10ms evaluation)
7. **trail.py** -- trail recording to board memory with tags, 5 event types
8. **propagation.py** -- cross-task data propagation (child-to-parent, contribution-to-target, transfer-to-agent)
9. **contributions.py** -- contribution opportunity management from matrix config, phase-aware

**Module code standards (all modules):** SRP, type hints on all public functions, docstrings, unit tests mirroring path, no circular imports (deps point inward), config from YAML, conventional commits, structured logging, no hardcoded values.

**Validation:** Unit tests per module, orchestrator integration tests, existing tests must pass during evolution.

---

## IaC + MCP Standard

**Governs:** All provisioning, tool deployment, and validation scripts -- everything reproducible from `make setup`.

**Principles (non-negotiable):** Idempotent, config-driven (YAML, no hardcoded values), zero manual steps, validate before write, report what changed, handle dependencies, source of truth in git (templates committed, runtime output gitignored).

**Required scripts (6):**
1. `provision-agents.sh` -- master provisioning from templates + config, hash-compare for idempotency
2. `setup-agent-tools.sh` -- deploys per-agent `mcp.json` from agent-tooling.yaml, resolves placeholders (`{{WORKSPACE}}`, `{{FLEET_DIR}}`, etc.)
3. `install-plugins.sh` -- `claude plugin install` per agent from agent-tooling.yaml plugins section
4. `generate-tools-md.sh` -- generates chain-aware TOOLS.md per role from tools.py + call trees + tooling config
5. `generate-agents-md.sh` -- generates AGENTS.md per role from synergy matrix + identities
6. `validate-agents.sh` -- validates all agent files against all standards (structure, size, content quality, cross-file consistency)

**Config files (3):** `config/agent-identities.yaml` (fleet roster), `config/agent-tooling.yaml` (per-role MCP servers/plugins/skills), `config/agent-autonomy.yaml` (per-role lifecycle thresholds/wake triggers)

**Makefile targets:** `make setup` = provision + setup-tools + install-plugins + validate-agents. `make generate` = generate-tools + generate-agents.

**Validation:** Run script twice = identical result (idempotency), grep for hardcoded agent names = none, fresh clone + `make setup` = all agents ready, validation output shows PASS/WARN/FAIL per agent per file.

---

## Artifact Type Standards (standards.py)

**Governs:** Quality definitions for every artifact type agents produce -- enforced by methodology checks and the teaching system.

### Data Model
- `RequiredField(name, description, required=True)` -- field that must be present (required=False = recommended but non-blocking)
- `Standard(artifact_type, description, required_fields, quality_criteria, positive_example, negative_example)`
- `ComplianceResult(artifact_type, missing_fields, failed_criteria)` -- `.compliant` (bool), `.score` (0-100)

### Compliance Score Calculation
`score = max(0, 100 - (total_issues * 15))` where `total_issues = len(missing_fields) + len(failed_criteria)`. Each missing required field or failed criterion deducts 15 points. 100 = fully compliant. Only `required=True` fields count as missing.

### Registered Artifact Types (7)

| Type | Required Fields | Optional Fields | Quality Criteria |
|------|----------------|-----------------|------------------|
| **task** | title, requirement_verbatim, description, acceptance_criteria, task_type, task_stage, task_readiness, priority, project | agent_name, story_points | Title is action not goal; verbatim populated; description refs design docs; criteria checkable; deps linked |
| **bug** | title, steps_to_reproduce, expected_behavior, actual_behavior, environment, impact | evidence | Title names specific error; steps numbered; expected vs actual separated; errors verbatim; impact states who blocked |
| **analysis_document** | title, scope, current_state, findings, implications | open_questions | Refs specific files/lines; findings are observations not opinions; scope states inclusions/exclusions; implications connect to task |
| **investigation_document** | title, scope, findings | options, recommendations, open_questions | Multiple options explored; sources cited; findings organized by topic; tradeoffs stated |
| **plan** | title, requirement_reference, approach, target_files, steps, acceptance_criteria_mapping | risks | Refs verbatim requirement; target files are specific paths; steps ordered and actionable; criteria mapped to steps |
| **pull_request** | title, description, changes, testing, task_reference | commits | Title conventional commit format; description explains why not what; test results included; task ID referenced |
| **completion_claim** | pr_url, summary, acceptance_criteria_check, files_changed | (none) | Every criterion addressed with evidence; PR URL valid; summary matches verbatim; no criteria marked done without evidence |

### Public API
- `get_standard(artifact_type) -> Optional[Standard]`
- `list_standards() -> list[Standard]`
- `check_standard(artifact_type, present_fields: dict[str, bool]) -> ComplianceResult`

`check_standard` takes a dict of `{field_name: is_present}` and returns missing required fields. Quality criteria are defined but not yet auto-evaluated by `check_standard` (only field presence is checked programmatically).

---

## Cross-Standard Relationships

| File | Position | Layer | Written By | Content Type |
|------|----------|-------|-----------|--------------|
| IDENTITY.md | 1 | Inner (constant) | IaC provision | Identity grounding |
| SOUL.md | 2 | Inner (constant) | IaC provision | Values + anti-corruption |
| CLAUDE.md | 3 | Middle (constant) | IaC provision | Role rules + constraints |
| TOOLS.md | 4 | Middle (constant) | IaC generate | Tool chain reference |
| AGENTS.md | 5 | Middle (constant) | IaC generate | Colleague synergy |
| fleet-context.md | 6 | Outer (dynamic) | Brain every 30s | Fleet state + task data |
| task-context.md | 7 | Outer (dynamic) | Brain every 30s | Autocomplete chain |
| HEARTBEAT.md | 8 | Middle (constant) | IaC provision | Action protocol (LAST) |
| agent.yaml | -- | Config | IaC provision | Gateway + orchestrator config |

**Separation principle:** Each file owns exactly one concern. No file duplicates content from another. Dependencies point inward (outer references inner, never reverse). Dynamic data never leaks into constant files.

---
