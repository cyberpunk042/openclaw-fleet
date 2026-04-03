# Unified Configuration Reference

**Date:** 2026-03-30
**Status:** Design — complete config/fleet.yaml after elevation
**Part of:** Fleet Elevation (document 26 — added to series)

---

## What This Document Covers

The complete configuration landscape after fleet elevation. Every
config section, what it controls, which document designed it, and
the full YAML structure. This is the implementation reference — one
place to see everything that needs to be configured.

---

## Current config/fleet.yaml (What Exists)

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

---

## Elevated config/fleet.yaml (Full Structure)

```yaml
# ═══════════════════════════════════════════════════════════════
# FLEET IDENTITY (doc 16)
# ═══════════════════════════════════════════════════════════════

fleet:
  id: alpha                    # Short identifier for this fleet
  number: 1                    # Numeric fleet identifier
  name: "Fleet Alpha"          # Display name
  version: 0.2.0

  # Shared resources
  shared_plane: true           # This Plane is shared with other fleets
  shared_github: true          # GitHub repos are shared


# ═══════════════════════════════════════════════════════════════
# INFRASTRUCTURE
# ═══════════════════════════════════════════════════════════════

gateway:
  port: 9400
  claude_model: opus
  default_mode: think
  ws_url: ws://localhost:18789   # WebSocket RPC for doctor tools
  # Injection order for system prompt (doc 02)
  injection_order:
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
  api_key_env: PLANE_API_KEY    # env var name, not the key itself

agents_dir: agents

# LocalAI peering (doc 16)
cluster:
  local:
    url: http://localhost:8090
    gpu_vram: 8192
  peers: []
  # peers:
  #   - fleet_id: bravo
  #     url: http://bravo-localai:8090
  #     priority: 1


# ═══════════════════════════════════════════════════════════════
# ORCHESTRATOR — THE BRAIN (doc 04)
# ═══════════════════════════════════════════════════════════════

orchestrator:
  cycle_interval: 30             # seconds between cycles
  max_concurrent_per_agent: 1
  max_dispatch_per_cycle: 2
  dry_run: false
  budget_mode: turbo

  driver_agents:
    - project-manager
    - fleet-ops
  driver_heartbeat_interval: 600  # seconds

  # Doctor configuration (doc 04, immune system)
  doctor:
    correction_threshold: 3       # corrections before prune signal
    stuck_threshold_minutes: 60   # minutes inactive before stuck detection
    contribution_avoidance_threshold: 0.3  # must contribute to 30% of opportunities
    trail_completeness_required: true

  # Chain cascade control (doc 04)
  chain:
    max_cascade_depth: 5          # prevent infinite event loops


# ═══════════════════════════════════════════════════════════════
# NOTIFICATIONS (doc 04)
# ═══════════════════════════════════════════════════════════════

notifications:
  ntfy:
    url: http://192.168.40.11:10222
    topics:
      progress: fleet-progress    # info — task done, sprint update
      review: fleet-review        # important — gate request, review needed
      alert: fleet-alert          # urgent — security, infrastructure
    fleet_prefix: true            # prefix messages with [fleet_id]
  windows:
    enabled: false
    only_urgent: true
  irc:
    channels:
      fleet: "#fleet"             # general activity
      alerts: "#alerts"           # security, immune, budget, infra
      reviews: "#reviews"         # tasks in review, approval decisions
      gates: "#gates"             # gate requests, PO decisions
      contributions: "#contributions"  # contribution activity
      sprint: "#sprint"           # sprint progress, milestones

  # Routing matrix — which event goes where (doc 04)
  # Loaded from config/notifications.yaml for full detail
  routing_config: config/notifications.yaml


# ═══════════════════════════════════════════════════════════════
# PHASES — PO-DEFINED (doc 03)
# ═══════════════════════════════════════════════════════════════

# Phases are in their own file because the PO owns them
# and may change them frequently
phases_config: config/phases.yaml


# ═══════════════════════════════════════════════════════════════
# METHODOLOGY (existing + doc 03, 17)
# ═══════════════════════════════════════════════════════════════

methodology:
  stages:
    - conversation
    - analysis
    - investigation
    - reasoning
    - work

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
  po_required_gates: [90]          # readiness values where ONLY PO can advance


# ═══════════════════════════════════════════════════════════════
# CONTRIBUTIONS — CROSS-AGENT SYNERGY (doc 15)
# ═══════════════════════════════════════════════════════════════

contributions:
  # When task enters this stage, these roles contribute
  reasoning:
    - role: architect
      contribution_type: design_input
      required_for: [epic, story]
      optional_for: [task]
      condition: "complexity == 'high'"
    - role: qa-engineer
      contribution_type: qa_test_definition
      required_for: [epic, story, task]
      optional_for: [bug]
    - role: ux-designer
      contribution_type: ux_spec
      required_for: [story]
      condition: "tags contains 'ui'"
    - role: devsecops-expert
      contribution_type: security_requirement
      required_for: [epic]
      condition: "tags contains 'security' OR task_type == 'epic'"
    - role: technical-writer
      contribution_type: documentation_outline
      optional_for: [epic, story]
      # condition set by PO per phase in phases.yaml

  review:
    - role: qa-engineer
      contribution_type: qa_validation
      required_for: [epic, story, task]
      condition: "qa_test_definition exists for this task"
    - role: devsecops-expert
      contribution_type: security_review
      required_for: [epic, story]
      condition: "pr_url is set"
    - role: ux-designer
      contribution_type: ux_review
      optional_for: [story]
      condition: "tags contains 'ui'"

  completion:
    - role: technical-writer
      contribution_type: documentation_update
      required_for: [epic, story]
      # condition set by PO per phase in phases.yaml
    - role: accountability-generator
      contribution_type: trail_verification
      required_for: [epic, story, task]


# ═══════════════════════════════════════════════════════════════
# AGENT LIFECYCLE — SLEEP/WAKE (doc 23)
# ═══════════════════════════════════════════════════════════════

lifecycle:
  defaults:
    idle_after_heartbeat_ok: 2   # consecutive HEARTBEAT_OK → idle
    sleeping_after_heartbeat_ok: 3  # consecutive HEARTBEAT_OK → sleeping
    offline_after_hours: 4         # hours sleeping → offline
    wake_sensitivity: medium       # low, medium, high

  overrides:
    project-manager:
      idle_after_heartbeat_ok: 4
      sleeping_after_heartbeat_ok: 6
      wake_sensitivity: high
    fleet-ops:
      idle_after_heartbeat_ok: 4
      sleeping_after_heartbeat_ok: 6
      wake_sensitivity: high
    architect:
      wake_sensitivity: medium
    qa-engineer:
      wake_sensitivity: medium
    devsecops-expert:
      wake_sensitivity: medium
    # software-engineer, devops, technical-writer,
    # ux-designer, accountability-generator use defaults


# ═══════════════════════════════════════════════════════════════
# STRATEGIC CALL DECISIONS (doc 23)
# ═══════════════════════════════════════════════════════════════

call_strategy:
  models:
    complex_task: opus
    standard_task: sonnet
    lightweight_check: sonnet
    future_local: hermes-3b      # LocalAI target

  effort:
    complex_reasoning: high
    standard_work: high
    status_check: medium
    gradual_wake: medium
    budget_conscious: medium     # when weekly > 70%

  session:
    sleeping_prompt_wake: fresh
    sleeping_gradual_wake: compact
    idle_check: compact
    active_progressive: continue
    active_new_task: fresh
    active_bloated: compact
    before_planning: compact
    after_prune: fresh

  max_turns:
    heartbeat_check: 5
    simple_contribution: 10
    standard_task: 15
    complex_task: 25
    crisis: 30


# ═══════════════════════════════════════════════════════════════
# CHAIN HANDLERS (doc 04)
# ═══════════════════════════════════════════════════════════════

# Full chain definitions in separate file for readability
chains_config: config/chains.yaml


# ═══════════════════════════════════════════════════════════════
# BOARD MEMORY (doc 04)
# ═══════════════════════════════════════════════════════════════

board_memory:
  retention:
    directives: permanent        # until superseded
    decisions: permanent
    trails: permanent            # audit requirement
    chat: current_sprint
    events: 2_sprints
    reports: 3_sprints
```

---

## Separate Config Files

Some configs are in their own files for clarity and PO ownership:

### config/phases.yaml (PO-owned, doc 03)
PO defines phases, progressions, and standards. See doc 03 for
full structure. The PO changes this file directly — it's THEIR
configuration.

### config/chains.yaml (doc 04)
Chain handler definitions — event type → handler list. See doc 04
for full structure.

### config/notifications.yaml (doc 04)
Notification routing matrix — event type → channels. See doc 04
for full structure.

---

## Config File Inventory After Elevation

```
config/
├── fleet.yaml           # Main config (this document)
├── phases.yaml          # PO-defined phases + standards (doc 03)
├── chains.yaml          # Chain handler definitions (doc 04)
├── notifications.yaml   # Event → channel routing (doc 04)
└── sprints/             # Sprint definitions (existing)
    └── dspd-s1.yaml
```

---

## What Changes vs Current

| Section | Current | Elevated |
|---------|---------|----------|
| fleet | name, version | + id, number, shared_plane, shared_github |
| gateway | port, model, mode | + ws_url, injection_order |
| plane | not present | NEW: url, workspace, api_key_env |
| cluster | not present | NEW: local, peers (LocalAI peering) |
| orchestrator | basic dispatch config | + doctor, chain cascade |
| notifications | ntfy topics | + irc channels, fleet_prefix, routing_config |
| methodology | not present (in code) | NEW: stages, task_type_stages, readiness, gates |
| contributions | not present | NEW: per-stage rules (doc 15) |
| lifecycle | not present | NEW: sleep/wake thresholds per role (doc 23) |
| call_strategy | not present | NEW: model/effort/session/turns per situation (doc 23) |
| chains_config | not present | NEW: reference to chains.yaml |
| board_memory | not present | NEW: retention policies |
| phases_config | not present | NEW: reference to phases.yaml |