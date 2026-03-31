# Agent Architecture Review

**Date:** 2026-03-30
**Status:** Design — complete review of agent structure
**Part of:** Fleet Elevation (document 2 of 22)

---

## PO Requirements (Verbatim)

> "we need to revise everything about all agents, not just one of their
> files, the whole things and the templating and the injection and the
> structure and pattern explanation before autocomplete and so on..."

> "we need to make sure a clean structure is respected and SRP, Domain,
> Onion and all the goods standard we want to impose our fleet."

> "this is about logic and applying the roles, making the agents behave
> as they should and respecting everything about themselves, and having
> their own Identity name and username and whatnot"

> "The words and titles I used are not for nothing. there is a huge
> difference between any general agent..... those are top tier wise
> agent."

> "every role are top tier expert of their profession"

---

## What This Document Covers

The complete agent file architecture: every file, its single
responsibility, how files relate to each other, how the gateway
reads and injects them, how the onion architecture applies to agent
context, and how the template system enforces consistency across
all 10 agents.

---

## Current Agent File Structure

Each agent has:
```
agents/{name}/
├── agent.yaml       # Identity, mission, capabilities, model, mode
├── CLAUDE.md        # Project rules (max 4000 chars in gateway)
├── HEARTBEAT.md     # What to do between tasks
├── IDENTITY.md      # Display name, personality traits
├── SOUL.md          # Values, principles, behavioral boundaries
├── TOOLS.md         # Available MCP tools and usage
├── USER.md          # User-facing description
├── AGENTS.md        # Knowledge of other agents in the fleet
├── BOOTSTRAP.md     # First-time setup instructions (some agents)
├── README.md        # Agent documentation (some agents)
└── context/         # Pre-embedded data (refreshed every cycle)
    ├── fleet-context.md   # Heartbeat pre-embedded data
    └── task-context.md    # Current task pre-embedded data
```

## What Each File Does — SRP Applied

Every file has ONE responsibility. No file mixes concerns.

### agent.yaml (Gateway reads this)
**Responsibility:** gateway configuration and fleet identity.

Defines: name, display_name, fleet_id, fleet_number, username, type,
mode, backend, model, mission, capabilities, heartbeat_config,
roles (primary + contributes_to).

The gateway uses this for session creation and system prompt building.
The brain uses this for dispatch decisions and role-based logic.

```yaml
name: "alpha-architect"
display_name: "Architect Alpha"
fleet_id: "alpha"
fleet_number: 1
username: "alpha-architect"
type: "agent"
mode: "heartbeat"
backend: "claude"
model: "opus"
mission: "Design authority — architecture, patterns, complexity"
capabilities:
  - "architecture_design"
  - "complexity_assessment"
  - "design_review"
  - "pattern_selection"
roles:
  primary: "architect"
  contributes_to:
    - "software-engineer"
    - "devops"
heartbeat_config:
  every: "10m"
```

### CLAUDE.md (Gateway injects, max 4000 chars)
**Responsibility:** role-specific project rules and constraints.

This is NOT generic project rules shared across all agents. Each
agent's CLAUDE.md is UNIQUE to their role. It contains:
- Their core responsibility (one sentence)
- Role-specific rules (what they must do)
- Anti-corruption rules (shared section — do not deform, minimize,
  compress the PO's words)
- Tool → chain patterns specific to their role
- What they do NOT do (boundary setting)
- Stage-specific behavior reminders

Max 4000 chars enforced by gateway. Content must be dense and precise
— every line should change the agent's behavior in a role-specific way.
No generic filler.

See documents 05-14 for each agent's CLAUDE.md content.

### HEARTBEAT.md (Agent reads during heartbeat)
**Responsibility:** between-task behavior protocol.

What the agent does when it wakes up. Ordered priority:
1. PO directives (highest priority)
2. Messages (respond to mentions)
3. Core job (role-specific: PM assigns, fleet-ops reviews, etc.)
4. Proactive contributions (role-specific)
5. Health monitoring (role-specific)
6. HEARTBEAT_OK if nothing needs attention

Heartbeat does NOT contain identity (that's IDENTITY.md), does NOT
contain rules (that's CLAUDE.md), does NOT contain tool documentation
(that's TOOLS.md). It contains the ACTION PROTOCOL.

### IDENTITY.md (Agent personality — constant)
**Responsibility:** who the agent IS.

- Name, display name, fleet ID, fleet number, username
- Role and specialty description
- Personality traits and communication style
- Place in the fleet (how they relate to other agents)
- Top-tier expert designation (not generic agent)

This file is CONSTANT during operation. It grounds the AI's identity.
It's injected FIRST in the gateway system prompt — before rules,
before data, before anything else. The AI generates all subsequent
tokens FROM this identity.

```markdown
# IDENTITY.md — Architect Alpha

## Who You Are
- Name: alpha-architect
- Display: Architect Alpha
- Fleet: Fleet Alpha (Fleet #1)
- Username: alpha-architect
- Role: Architect — Design Authority

## Your Specialty
You are a top-tier architect. You know design patterns deeply — not
just what a builder or mediator IS, but WHEN to use each and WHY.
You understand SRP, Domain-Driven Design, Onion Architecture. You
research before recommending. You validate choices against real-world
constraints.

## Your Personality
Thorough, methodical, specific. You never give vague guidance. When
you recommend a pattern, you name the exact files and the exact
rationale. You explore multiple options before deciding. You respect
the PO's authority and your colleagues' expertise.

## Your Place in the Fleet
Engineers depend on your design input. QA defines tests based on your
architecture. The PM consults you for complexity assessment. Fleet-ops
checks your design sign-off during review. Technical writer records
your decisions as ADRs. You are the design authority — your input
shapes how everything gets built.
```

### SOUL.md (Behavioral boundaries — constant)
**Responsibility:** values and what the agent will/won't do.

Contains:
- Role-specific values (architect: "design before implementation")
- Shared anti-corruption values (all agents):
  - The PO's words are sacrosanct
  - Do not deform, compress, or corrupt requirements
  - Do not skip stages or bypass gates
  - Do not produce work outside current stage
  - Three corrections = model is wrong, start fresh
- Role-specific boundaries (what this agent does / refuses)
- Humility clause (no overconfidence, no self-confirmed bias)

This file is CONSTANT. Injected after IDENTITY.md. Establishes
behavioral boundaries early in the context where they have
maximum effect.

### TOOLS.md (Chain-aware reference)
**Responsibility:** available tools with chain documentation.

NOT a list of tool names. A CHAIN-AWARE reference that tells the
agent what happens when they call each tool:
- What the tool does (primary action)
- What CHAIN it fires (automatic side effects)
- WHEN to use it (which stage, which conditions)
- What it expects as input
- What HAPPENS after the call (events, notifications, propagation)
- What the agent does NOT need to call manually

Each agent's TOOLS.md is different because different roles use
different tools in different ways. The architect rarely calls
fleet_commit but constantly calls fleet_artifact_create. QA calls
fleet_contribute to predefine tests. PM calls fleet_task_create.

See documents 05-14 for each agent's TOOLS.md content.

### AGENTS.md (Fleet awareness)
**Responsibility:** knowledge of other agents and synergy points.

Contains:
- Who the other agents are (name, role, specialty)
- How this agent's work connects to theirs
- When to reach out to whom
- What each colleague contributes and when

Updated per document 15 (cross-agent synergy map). Each agent knows
who contributes what to whom.

### context/ (Dynamic data — refreshed every cycle)
**Responsibility:** current state data, refreshed by the brain.

Two files:
- `fleet-context.md` — fleet state, messages, directives, role data,
  events. Pre-embedded for heartbeat.
- `task-context.md` — current task with engineered autocomplete chain.
  Pre-embedded for task work.

These are GENERATED by the brain every orchestrator cycle. They are
NOT written by agents or humans. They contain FULL data (never
compressed, never summarized).

The content is ENGINEERED as an autocomplete chain:
identity grounding → verbatim requirement → stage protocol →
colleague contributions → phase standards → action directive →
chain documentation.

See document 04 (the brain) for autocomplete chain builder details.

---

## Onion Architecture for Agent Context

```
┌─────────────────────────────────────────────────────┐
│                OUTER: Dynamic Data                   │
│   context/fleet-context.md (fleet state, messages)   │
│   context/task-context.md (task + autocomplete chain) │
│   Refreshed every orchestrator cycle by the brain.    │
├─────────────────────────────────────────────────────┤
│              MIDDLE: Rules & Patterns                │
│   CLAUDE.md (role-specific rules, max 4000 chars)    │
│   HEARTBEAT.md (behavior protocol)                   │
│   TOOLS.md (chain-aware tool reference)              │
│   AGENTS.md (synergy knowledge)                      │
│   Stable — changes when the fleet evolves.            │
├─────────────────────────────────────────────────────┤
│              INNER: Identity (constant)               │
│   IDENTITY.md (who you are, fleet, role)             │
│   SOUL.md (values, boundaries, anti-corruption)      │
│   agent.yaml (gateway config, fleet identity)        │
│   Never changes during operation.                     │
└─────────────────────────────────────────────────────┘
```

The agent reads from inner to outer. Identity first (grounds the AI),
then rules (constrains behavior), then dynamic data (current situation).

Dependencies point INWARD:
- Dynamic data references rules and identity
- Rules reference identity
- Identity references nothing — it IS the foundation

The gateway MUST inject files in this order (see document 04, gateway
executor section). Files injected early have more influence on AI
behavior (Lost in the Middle effect — rules at the start succeed,
rules buried in context fail).

---

## Gateway Injection Order

The gateway executor builds the system prompt from agent files in
this specific order:

```
1. IDENTITY.md    ← who I am (grounding)
2. SOUL.md        ← what I value (boundaries)
3. CLAUDE.md      ← role-specific rules (methodology, constraints)
4. TOOLS.md       ← what I can do (chain-aware capabilities)
5. AGENTS.md      ← who my colleagues are (synergy)
6. context/fleet-context.md  ← fleet state (dynamic)
7. context/task-context.md   ← my current work (autocomplete chain)
8. HEARTBEAT.md   ← what to do now (action prompt)
```

This order creates a funnel from identity → values → rules →
capabilities → team → state → task → action. Each layer narrows
the AI's response space. By the time it reaches HEARTBEAT.md,
there's a narrow band of correct responses. That's the autocomplete
chain.

---

## Template System

### Canonical Template
`agents/_template/` defines the canonical structure all agents follow:

```
agents/_template/
├── agent.yaml.template      # with {placeholders} for fleet/role
├── CLAUDE.md.template       # SRP sections, role-specific markers
├── HEARTBEAT.md.template    # common structure, role-specific content
├── IDENTITY.md.template     # fleet identity fields, role description
├── SOUL.md.template         # shared values + role-specific section
├── TOOLS.md.template        # chain documentation format
├── AGENTS.md.template       # synergy point format
└── context/
    ├── fleet-context.md     # brain-generated (template is empty)
    └── task-context.md      # brain-generated (template is empty)
```

### Template Enforcement
A validation script ensures all agents follow the template:

```bash
# scripts/validate-agents.sh
# For each agent directory:
#   1. Check all required files exist
#   2. Check file sections match template structure
#   3. Check no template placeholders remain unfilled
#   4. Check CLAUDE.md within 4000 char limit
#   5. Check no concern mixing:
#      - Identity content not in HEARTBEAT.md
#      - Tool docs not in CLAUDE.md
#      - Dynamic data not in IDENTITY.md
#   6. Check fleet identity fields are present and consistent
```

### Agent Creation From Template
When a new agent is created:
1. Copy template files to `agents/{new-name}/`
2. Fill in placeholders: fleet_id, role, display_name, etc.
3. Write role-specific content for CLAUDE.md, TOOLS.md, HEARTBEAT.md
4. Run validation script
5. Register agent in AGENTS.md for all existing agents

### Template Evolution
When the template changes (e.g., new file added, new section required):
1. Update `agents/_template/`
2. Run validation against all agents — identify gaps
3. Update each agent to match new template
4. Commit as a fleet-wide template update

---

## What Needs to Change From Current State

### Currently Divergent
- Some agents have BOOTSTRAP.md, some don't → standardize
- Some have README.md → remove (use USER.md instead)
- CLAUDE.md is generic across all agents → role-specific per 05-14
- IDENTITY.md written once, never revisited → rewrite with fleet ID
- SOUL.md written once → rewrite with anti-corruption + role values
- TOOLS.md auto-generated by MC → rewrite chain-aware per 05-14
- No template validation → add scripts/validate-agents.sh
- No injection ordering → configure gateway executor

### File Changes Needed Per Agent (10 agents)

| File | Current | Needed |
|------|---------|--------|
| agent.yaml | Basic | + fleet_id, fleet_number, username, roles |
| CLAUDE.md | Generic (same for all) | Role-specific (unique per agent, per docs 05-14) |
| HEARTBEAT.md | Rewritten for 5 agents | Verify alignment with contribution model for all 10 |
| IDENTITY.md | Basic | Full rewrite with fleet identity, top-tier expert, synergy |
| SOUL.md | Basic | Add anti-corruption rules, role-specific values, humility |
| TOOLS.md | Auto-generated list | Chain-aware documentation per role (per docs 05-14) |
| AGENTS.md | Basic | Updated with synergy points from doc 15 |
| BOOTSTRAP.md | Some agents | Standardize: all or none |
| README.md | Some agents | Remove — use USER.md |
| context/ | Exists | Verify brain writes full autocomplete chain |

### Total File Changes
- 10 agents × 7 files = 70 file updates
- Plus template files = 7 template updates
- Plus validation script = 1 new script
- Plus gateway executor = 1 modification

---

## Interaction With Other Systems

### Agent Files ↔ Brain
- Brain reads agent.yaml for dispatch decisions (role, model, fleet)
- Brain writes context/ files every cycle (autocomplete chain)
- Brain reads HEARTBEAT.md structure to understand what data to embed

### Agent Files ↔ Gateway
- Gateway reads ALL files for system prompt construction
- Gateway respects injection order (IDENTITY → SOUL → CLAUDE → ...)
- Gateway enforces CLAUDE.md 4000 char limit
- Gateway reads context/ files (8000 char limit each)

### Agent Files ↔ Immune System
- Doctor reads agent.yaml for agent identification
- Teaching lessons reference CLAUDE.md rules in lesson content
- Prune kills the session — agent files survive (persistent)

### Agent Files ↔ Multi-Fleet
- IDENTITY.md includes fleet_id, fleet_number, username
- agent.yaml includes fleet_id for brain routing
- All agents in a fleet share the fleet identity prefix

---

## Testing Requirements

- Template validation: all agents pass validation script
- Injection order: gateway injects files in correct order
- CLAUDE.md size: all under 4000 chars
- Context files: brain writes full autocomplete chain
- SRP verification: no concern mixing across files
- Fleet identity: all files include correct fleet_id
- Multi-fleet: no naming collisions between fleets

---

## Open Questions

- Should TOOLS.md be curated per role or auto-generated?
  → Answer: curated per role with chain documentation (see docs 05-14)
- Should there be a METHODOLOGY.md per agent explaining their
  stage-specific behavior?
  → Answer: no — stage behavior is in CLAUDE.md and HEARTBEAT.md
- Should CLAUDE.md be split into multiple concerns (rules.md,
  patterns.md)?
  → Answer: no — 4000 char limit keeps it focused. One file, dense.
- How does the template system handle role-specific sections vs
  common sections?
  → Answer: template has section markers. Common sections (anti-
  corruption rules) are shared. Role-specific sections are filled
  per agent.
- Should agents have a STANDARDS.md with their artifact type standards?
  → Answer: no — standards are in fleet/core/standards.py and injected
  via context. Agents don't need a static standards file.