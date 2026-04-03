# Fleet Master Diagrams — Complete Visual Architecture

**Date:** 2026-04-01
**Status:** ACTIVE — comprehensive diagrams reflecting full system design
**Supersedes:** fleet-elevation/25-diagrams.md (partial, pre-session-management)
**Reflects:** System 22 organic context model, rate limit session awareness,
13-step brain, per-type standards, IaC flow, agent anatomy

---

## 1. Master Fleet Architecture — Everything Connected

```
                              ┌─────────────────────┐
                              │     PO (Human)      │
                              │                     │
                              │  Plane  │  OCMC     │
                              │  issues │  directives│
                              │  phases │  budget    │
                              │  gates  │  overrides │
                              └────┬────┬───────────┘
                                   │    │
            ┌──────────────────────┘    └──────────────────────┐
            ↓                                                   ↓
   ┌────────────────┐                                  ┌────────────────┐
   │     Plane      │←──── sync ────→                  │  Mission Ctrl  │
   │  (DSPD proj)   │                                  │   (OCMC API)   │
   │                │                                  │                │
   │ Issues, sprints│                                  │ Tasks, agents  │
   │ Pages, labels  │                                  │ Board memory   │
   │ PM surface     │                                  │ Approvals      │
   └────────────────┘                                  └───────┬────────┘
                                                               │
                                                               │ reads/writes
                                                               ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                        BRAIN (Orchestrator)                                   │
│                        30-second cycle, 13 steps                             │
│                        Pure Python — ZERO LLM calls                          │
│                                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │  Storm   │ │  Budget  │ │  Fleet   │ │  Budget  │ │   Session        │  │
│  │  Monitor │ │  Monitor │ │  Mode    │ │  Mode    │ │   Manager        │  │
│  │          │ │          │ │          │ │ (tempo)  │ │                  │  │
│  │ 9 indica-│ │ OAuth    │ │ 3 axes:  │ │          │ │ TWO countdowns: │  │
│  │ tors, 5  │ │ quota,   │ │ work ×   │ │ speed/   │ │ • context rem.  │  │
│  │ severity │ │ 5h/7d    │ │ phase ×  │ │ frequency│ │ • rate limit %  │  │
│  │ levels   │ │ windows  │ │ backend  │ │ offset   │ │ Aggregate math  │  │
│  └─────┬────┘ └─────┬────┘ └────┬─────┘ └────┬─────┘ └────────┬────────┘  │
│        │            │           │             │                │            │
│  13 Steps: ─────────────────────────────────────────────────────            │
│   0. Context refresh + autocomplete chain                                    │
│   1. Process event queue (chain registry)                                    │
│   2. Doctor (immune system, 11 diseases)                                     │
│   3. Gate processing (PO gates at 90%)                                       │
│   4. Contribution management (synergy matrix)                                │
│   5. Dispatch (10 gates via logic engine)                                    │
│   6. Approval & transition                                                   │
│   7. Parent evaluation (children done → parent to review)                    │
│   8. Driver management (wake PM/fleet-ops)                                   │
│   9. Cross-task propagation (child→parent, contribution→target)              │
│  10. SESSION MANAGEMENT (rate limit + context eval + aggregate math)          │
│  11. Health & budget                                                         │
│  12. Directives (PO commands)                                                │
│                                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │  Chain   │ │  Logic   │ │  Doctor  │ │ Contri-  │ │  Trail   │          │
│  │ Registry │ │  Engine  │ │          │ │ butions  │ │ System   │          │
│  │          │ │          │ │ 11 dis-  │ │          │ │          │          │
│  │ event →  │ │ 10+1     │ │ eases,   │ │ matrix   │ │ stage    │          │
│  │ handlers │ │ dispatch │ │ teach,   │ │ per role │ │ transi-  │          │
│  │ cascade  │ │ gates    │ │ prune    │ │ per phase│ │ tions    │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│                                                                              │
└──────────────────────────┬───────────────────────────────────────────────────┘
                           │ writes context/ files     │ inject_content()
                           ↓                           ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│                     GATEWAY (OpenClaw)                                        │
│                     ws://localhost:18789                                      │
│                                                                              │
│  Reads: agents/{name}/ files → builds system prompt (8-file injection order) │
│  Runs:  claude --permission-mode bypassPermissions                           │
│  MCP:   python -m fleet.mcp.server (25 tools, stdio)                         │
│  Sessions: prune, compact, inject, create fresh                              │
│                                                                              │
│  Injection Order (DESIGNED — NOT YET IMPLEMENTED IN GATEWAY):                 │
│  1.IDENTITY → 2.SOUL → 3.CLAUDE → 4.TOOLS → 5.AGENTS → 6.fleet-context     │
│  → 7.task-context → 8.HEARTBEAT                                             │
│                                                                              │
│  CURRENT REALITY (executor.py + ws_server.py):                               │
│  name+mission → CLAUDE.md → context/*.md (alphabetical)                      │
│  ⚠️ B0.7: Gateway must be modified to read all 8 files                       │
│                                                                              │
└──────────────────────────┬───────────────────────────────────────────────────┘
                           │
            ┌──────────────┼──────────────────────────────────┐
            │              │                                  │
   ┌────────┴───────┐ ┌───┴────────────┐  ┌─────────────────┴──────────┐
   │   DRIVERS      │ │   WORKERS      │  │   25 MCP TOOLS             │
   │                │ │                │  │                            │
   │ PM             │ │ architect      │  │ Task: read, accept,        │
   │ fleet-ops      │ │ engineer       │  │   progress, commit,        │
   │ devsecops      │ │ devops         │  │   complete, create         │
   │ accountability │ │ qa-engineer    │  │ Comms: chat, alert,        │
   │                │ │ writer         │  │   pause, escalate, notify  │
   │ Each:          │ │ ux-designer    │  │ Review: approve            │
   │ HEARTBEAT.md   │ │                │  │ Plane: status, sprint,     │
   │ CLAUDE.md      │ │ Each:          │  │   sync, create, comment    │
   │ (role-specific)│ │ Stage-driven   │  │ Artifact: read, update,    │
   │ 4 unique       │ │ heartbeat      │  │   create                   │
   │ heartbeat types│ │ 1 template     │  │ Status: agent_status       │
   └────────────────┘ │ 6 role variants│  │                            │
                      └────────────────┘  │ Stage gate: commit +       │
                                          │ complete BLOCKED outside   │
                                          │ work stage                 │
                                          └──────────┬─────────────────┘
                                                     │ events propagate
                                                     ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│                          6 SURFACES                                          │
│                                                                              │
│  INTERNAL │ MC (tasks, memory, approvals, trail)                             │
│  PUBLIC   │ GitHub (branches, PRs, commits, CI)                              │
│  CHANNEL  │ IRC (#fleet #alerts #reviews #sprint #agents #security #builds)  │
│  NOTIFY   │ ntfy (PO mobile push, severity-based)                            │
│  PLANE    │ Plane (issues, labels, comments, pages, sprints)                 │
│  META     │ Metrics (quality checks, analytics, diagnostics)                 │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Agent Anatomy — Onion Architecture + Autocomplete Chain

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   OUTER LAYER: Dynamic Data (refreshed every 30s by brain)          │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │  context/fleet-context.md                                    │  │
│   │  § Fleet state  § PO directives  § Messages                  │  │
│   │  § Assigned tasks (FULL, NEVER compressed)                   │  │
│   │  § Role data (from role_providers)  § Events                 │  │
│   │  § Context awareness (context %, rate limit %)               │  │
│   ├──────────────────────────────────────────────────────────────┤  │
│   │  context/task-context.md (AUTOCOMPLETE CHAIN — order matters) │  │
│   │                                                              │  │
│   │  1. # YOU ARE: {name} ({role})         ← identity grounding  │  │
│   │  2. # YOUR TASK: {title}               ← task focus          │  │
│   │  3. # YOUR STAGE: {stage}              ← constrains actions  │  │
│   │  4. # READINESS: {readiness}%          ← progress            │  │
│   │  5. ## VERBATIM REQUIREMENT            ← THE ANCHOR (never   │  │
│   │     > {PO's exact words}                  summarized)         │  │
│   │  6. ## STAGE PROTOCOL (MUST/MUST NOT)  ← stage instructions  │  │
│   │  7. ## INPUTS FROM COLLEAGUES          ← contributions       │  │
│   │  8. ## DELIVERY PHASE: {phase}         ← quality bar         │  │
│   │  9. ## WHAT TO DO NOW                  ← action directive    │  │
│   │  10.## WHAT HAPPENS WHEN YOU ACT       ← chain docs          │  │
│   │                                                              │  │
│   │  By section 10, there is a NARROW BAND of correct responses. │  │
│   │  The correct action is the EASIEST thing to generate.        │  │
│   └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│   MIDDLE LAYER: Rules & Patterns (stable, changes when fleet evolves)│
│                                                                     │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │  CLAUDE.md (position 3, max 4000 chars)                      │  │
│   │  § Core Responsibility  § Role-Specific Rules                │  │
│   │  § Stage Protocol  § Tool Chains  § Contribution Model       │  │
│   │  § Boundaries  § Context Awareness  § Anti-Corruption        │  │
│   ├──────────────────────────────────────────────────────────────┤  │
│   │  HEARTBEAT.md (position 8 — LAST — the action prompt)        │  │
│   │  Priority 0: PO directives → 1: Messages → 2: Core job      │  │
│   │  → 3: Contributions → 4: Health → 5: HEARTBEAT_OK           │  │
│   ├──────────────────────────────────────────────────────────────┤  │
│   │  TOOLS.md (position 4) — chain-aware, GENERATED from code   │  │
│   │  AGENTS.md (position 5) — synergy, GENERATED from matrix    │  │
│   └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│   INNER LAYER: Identity (constant during operation)                  │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │  IDENTITY.md (position 1 — FIRST — grounds all generation)   │  │
│   │  § Who You Are  § Your Specialty (top-tier expert)           │  │
│   │  § Your Personality  § Your Place in the Fleet               │  │
│   ├──────────────────────────────────────────────────────────────┤  │
│   │  SOUL.md (position 2 — values + anti-corruption)             │  │
│   │  § Values (role-specific)  § 10 Anti-Corruption Rules        │  │
│   │  § What I Do  § What I Do NOT Do  § Humility                 │  │
│   ├──────────────────────────────────────────────────────────────┤  │
│   │  agent.yaml (gateway config + fleet identity)                │  │
│   │  14 required fields: name, fleet_id, roles, model, mission   │  │
│   └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│   Dependencies point INWARD: outer references middle and inner,     │
│   middle references inner, inner references nothing.                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Brain 13-Step Cycle — Complete Flow

```
                    ┌────────────────────────┐
                    │    CYCLE START (30s)    │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
              ┌─────│ Step 0: CONTEXT REFRESH │
              │     │ Read MC tasks + agents  │
              │     │ Detect mode changes     │
              │     │ Write context/ files    │
              │     │ Build autocomplete chain│
              │     └───────────┬────────────┘
              │                 │
              │     ┌───────────▼────────────┐
              │     │ Step 1: EVENT QUEUE     │
              │     │ Process queued events   │
              │     │ Chain registry handlers │
              │     │ Cascade (max depth 5)   │
              │     └───────────┬────────────┘
              │                 │
              │     ┌───────────▼────────────┐
              │     │ Step 2: DOCTOR          │
              │     │ Immune system detection │
              │     │ 11 diseases (4 impl)    │
              │     │ teach / compact / prune │
              │     └───────────┬────────────┘
              │                 │
              │     ┌───────────▼────────────┐
              │     │ Step 3: GATES           │
              │     │ PO gate at readiness 90 │
              │     │ Phase advancement gates │
              │     │ Route to PO if pending  │
              │     └───────────┬────────────┘
              │                 │
              │     ┌───────────▼────────────┐
              │     │ Step 4: CONTRIBUTIONS   │
              │     │ Create contribution     │
              │     │ tasks per synergy matrix│
              │     │ Track received contribs │
              │     └───────────┬────────────┘
              │                 │
  EVERY       │     ┌───────────▼────────────┐
  30 SEC      │     │ Step 5: DISPATCH        │
  CYCLE       │     │ 10+1 dispatch gates:    │
              │     │  fleet mode, agent avail│
              │     │  unblocked, online, busy│
              │     │  doctor clear, readiness│
              │     │  PO gate, contributions │
              │     │  phase prereqs          │
              │     │  SESSION MANAGEMENT ←────── DON'T dispatch 1M near rollover
              │     └───────────┬────────────┘
              │                 │
              │     ┌───────────▼────────────┐
              │     │ Step 6: APPROVALS       │
              │     │ Create approval objects │
              │     │ Transition done/reject  │
              │     │ Wake fleet-ops if needed│
              │     └───────────┬────────────┘
              │                 │
              │     ┌───────────▼────────────┐
              │     │ Step 7: PARENTS         │
              │     │ All children done?      │
              │     │ → parent to review      │
              │     │ Aggregate child summaries│
              │     └───────────┬────────────┘
              │                 │
              │     ┌───────────▼────────────┐
              │     │ Step 8: DRIVERS         │
              │     │ Wake PM (unassigned)    │
              │     │ Wake fleet-ops (reviews)│
              │     │ inject_content() via GW │
              │     └───────────┬────────────┘
              │                 │
              │     ┌───────────▼────────────┐
              │     │ Step 9: PROPAGATION     │
              │     │ Child → parent comments │
              │     │ Contribution → target   │
              │     │ Transfer → new agent    │
              │     │ Trail recording         │
              │     └───────────┬────────────┘
              │                 │
              │     ┌───────────▼─────────────────────────────────────────┐
              │     │ Step 10: SESSION MANAGEMENT                         │
              │     │                                                     │
              │     │  ┌───────────────────┐  ┌────────────────────────┐  │
              │     │  │ COUNTDOWN 1:      │  │ COUNTDOWN 2:           │  │
              │     │  │ Context Remaining │  │ Rate Limit Session     │  │
              │     │  │                   │  │                        │  │
              │     │  │ 100%→7%: flow     │  │ 0%→85%: normal         │  │
              │     │  │ 7%: prepare       │  │ 85%: prepare           │  │
              │     │  │ 5%: extract       │  │ 90%: actively manage   │  │
              │     │  │ 0%: compact+      │  │ Near rollover:         │  │
              │     │  │     regather      │  │   force compact heavy  │  │
              │     │  └───────────────────┘  └────────────────────────┘  │
              │     │                                                     │
              │     │  For each agent with context:                       │
              │     │  ├── Needs context for upcoming work?               │
              │     │  │   YES → keep, prepare organic transition         │
              │     │  │   NO  → dump to smart artifacts                  │
              │     │  ├── Over ~40-80K tokens?                           │
              │     │  │   YES + no work → dump immediately               │
              │     │  │   YES + work → synthesised re-injection later    │
              │     │  │   NO  → low cost, keep alive                     │
              │     │  ├── Near rollover?                                 │
              │     │  │   → Force compact heavy contexts (allow >90%)    │
              │     │  │   → Don't dispatch 1M quests                     │
              │     │  └── Aggregate fleet math:                          │
              │     │      5 × 200K = 1M on rollover                      │
              │     │      2 × 1M = 2M on rollover                        │
              │     │      On x5 Pro: 1M ≈ 50% of 5h window              │
              │     │                                                     │
              │     └───────────┬─────────────────────────────────────────┘
              │                 │
              │     ┌───────────▼────────────┐
              │     │ Step 11: HEALTH+BUDGET  │
              │     │ Stuck tasks > 48h       │
              │     │ Offline agents w/ work  │
              │     │ Budget check + profile  │
              │     │ Sprint progress update  │
              │     └───────────┬────────────┘
              │                 │
              │     ┌───────────▼────────────┐
              │     │ Step 12: DIRECTIVES     │
              │     │ Read PO directives      │
              │     │ Route to agent context  │
              │     │ Mark processed          │
              └─────│                         │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │    CYCLE END → WAIT    │
                    │    (30 seconds)         │
                    └────────────────────────┘
```

---

## 4. Session Management — Two Parallel Countdowns

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│              TWO PARALLEL COUNTDOWNS — BOTH ALWAYS RUNNING           │
│                                                                      │
│  COUNTDOWN 1: CONTEXT REMAINING (per agent)                          │
│  ════════════════════════════════════════════                         │
│                                                                      │
│  100%                    30%        7%    5%  0%                      │
│  ├─────────────────────────┼──────────┼─────┼──┤                     │
│  │     Normal work         │Mindful   │Prep │Ex│                     │
│  │     Let it flow         │Organic   │Save │tr│                     │
│  │     No restrictions     │efficiency│Artif│ac│                     │
│  │                         │Don't     │Keep │Me│                     │
│  │                         │force     │Work │mo│                     │
│  │                         │          │     │ry│                     │
│  │                         │          │     │  │→ compact + regather │
│  │                         │          │     │  │  from memory        │
│  │                         │          │     │  │  (200-500 tokens    │
│  │                         │          │     │  │   not 50K re-reads) │
│  │  "We do not compact for no reason, we let it flow"                │
│  │  "a lot can play itself in the last 7% of context"                │
│  │                                                                   │
│  COUNTDOWN 2: RATE LIMIT USAGE (fleet-wide, 5h/7d windows)          │
│  ════════════════════════════════════════════════════════             │
│                                                                      │
│  0%                              85%       90%        ROLLOVER       │
│  ├────────────────────────────────┼──────────┼───────────┤           │
│  │     Normal dispatch            │Prepare   │Active     │           │
│  │     All context sizes OK       │No 1M     │manage     │→ Fresh   │
│  │     Normal tempo                │quests    │Force      │  window  │
│  │                                │Progress- │compact    │  Put     │
│  │                                │ive aware-│heavy      │  agents  │
│  │                                │ness      │contexts   │  back on │
│  │                                │          │Allow >90% │  track   │
│  │                                │          │for compact│          │
│  │                                │          │cost       │          │
│  │                                                                   │
│  HOW THEY INTERACT:                                                  │
│  ═══════════════════                                                 │
│                                                                      │
│  Agent at 60% context + 70% rate limit = NORMAL                      │
│  Agent at 60% context + 88% rate limit = DON'T START 1M QUEST       │
│  Agent at 93% context + 50% rate limit = ORGANIC PREPARATION         │
│  Agent at 80% context + 92% rate limit = FORCE COMPACT IF NO WORK   │
│  5 agents × 200K      + near rollover  = 1M SPIKE RISK              │
│  2 agents × 1M        + near rollover  = 2M SPIKE = 50%+ OF WINDOW  │
│                                                                      │
│  BRAIN DECISION TREE (Step 10):                                      │
│  ═══════════════════════════════                                     │
│                                                                      │
│  For each agent:                                                     │
│  │                                                                   │
│  ├── Does agent need context for upcoming work?                      │
│  │   ├── NO  → dump to smart artifacts, fresh session later          │
│  │   └── YES → keep, prepare organic transition                      │
│  │                                                                   │
│  ├── Is context > ~40-80K tokens?                                    │
│  │   ├── YES + no predicted work → dump immediately                  │
│  │   ├── YES + related work coming → synthesised re-injection        │
│  │   └── NO  → low cost, keep alive                                  │
│  │                                                                   │
│  ├── Is next task related to current context?                        │
│  │   ├── YES → re-inject synthesised context after compact           │
│  │   └── NO  → fresh session, no re-injection needed                 │
│  │                                                                   │
│  └── Aggregate: sum(all contexts) vs remaining quota                 │
│      └── If aggregate > 50% of remaining → STORM RISK               │
│                                                                      │
│  "Only smart things. the brain is smart. it goes without saying."    │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 5. IaC Flow — Config to Gateway

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOURCE OF TRUTH (in git)                       │
│                                                                   │
│  config/                          agents/_template/               │
│  ├── agent-identities.yaml        ├── agent.yaml.template        │
│  ├── agent-tooling.yaml           ├── IDENTITY.md.template       │
│  ├── agent-autonomy.yaml          ├── SOUL.md.template           │
│  ├── fleet.yaml                   ├── CLAUDE.md/                 │
│  ├── phases.yaml                  │   ├── project-manager.md     │
│  ├── projects.yaml                │   ├── fleet-ops.md           │
│  └── (new: chains.yaml,          │   ├── architect.md           │
│       brain.yaml)                 │   ├── devsecops.md           │
│                                   │   ├── software-engineer.md   │
│  fleet/mcp/tools.py               │   ├── devops.md              │
│  (tool definitions)               │   ├── qa-engineer.md         │
│                                   │   ├── technical-writer.md    │
│  fleet-elevation/15               │   ├── ux-designer.md         │
│  (synergy matrix)                 │   └── accountability.md      │
│                                   ├── heartbeats/                │
│  fleet-elevation/24               │   ├── pm.md                  │
│  (tool call trees)                │   ├── fleet-ops.md           │
│                                   │   ├── architect.md           │
│                                   │   ├── devsecops.md           │
│                                   │   └── worker.md              │
│                                   └── context/                   │
│                                       └── (empty — brain fills)  │
└───────────────┬───────────────────────────────┬──────────────────┘
                │                               │
                ↓                               ↓
┌───────────────────────────┐   ┌────────────────────────────────┐
│ scripts/generate-*.sh     │   │ scripts/provision-agents.sh    │
│                           │   │                                │
│ generate-tools-md.sh      │   │ For each agent:                │
│   tools.py + call trees   │   │  1. Create agents/{name}/      │
│   + tooling.yaml          │   │  2. Fill templates from config │
│   → TOOLS.md per role     │   │  3. Copy role CLAUDE.md        │
│                           │   │  4. Copy role HEARTBEAT.md     │
│ generate-agents-md.sh     │   │  5. Place GENERATED files      │
│   synergy matrix          │   │     (TOOLS.md, AGENTS.md)      │
│   + identities.yaml       │   │  6. Generate mcp.json from     │
│   → AGENTS.md per role    │   │     agent-tooling.yaml         │
│                           │   │  7. Report changes             │
└───────────┬───────────────┘   └───────────────┬────────────────┘
            │                                   │
            └──────────────┬────────────────────┘
                           │
                           ↓
              ┌────────────────────────┐
              │ scripts/validate-      │
              │ agents.sh              │
              │                        │
              │ Per agent:             │
              │ • CLAUDE.md ≤ 4000ch   │
              │ • 8 required sections  │
              │ • SOUL.md 10 rules     │
              │ • IDENTITY.md fields   │
              │ • agent.yaml 14 fields │
              │ • mcp.json matches     │
              │   tooling config       │
              │ • No concern mixing    │
              │ • Contribution match   │
              │ • Tool refs valid      │
              │                        │
              │ Output: PASS/WARN/FAIL │
              └────────────┬───────────┘
                           │
                           ↓
              ┌────────────────────────┐
              │ agents/{name}/         │
              │ (gitignored — runtime) │
              │                        │
              │ ├── agent.yaml         │
              │ ├── IDENTITY.md        │
              │ ├── SOUL.md            │
              │ ├── CLAUDE.md          │
              │ ├── HEARTBEAT.md       │
              │ ├── TOOLS.md           │
              │ ├── AGENTS.md          │
              │ ├── mcp.json           │
              │ └── context/           │
              │     ├── fleet-context  │
              │     └── task-context   │
              └────────────┬───────────┘
                           │
                           ↓
              ┌────────────────────────┐
              │ GATEWAY reads on       │
              │ heartbeat              │
              │                        │
              │ Injects in order:      │
              │ 1→2→3→4→5→6→7→8       │
              │                        │
              │ Builds system prompt   │
              │ → Claude Code session  │
              │ → Agent acts           │
              └────────────────────────┘

Makefile:
  make provision     → provision-agents.sh
  make setup-tools   → setup-agent-tools.sh
  make generate      → generate-tools-md.sh + generate-agents-md.sh
  make validate      → validate-agents.sh
  make setup         → ALL OF THE ABOVE (zero to running)
```

---

## 6. Standards Coverage — What Gates What

```
┌──────────────────────────────────────────────────────────────────┐
│                    STANDARDS COVERAGE MAP                         │
│                                                                   │
│  Work Item          Standard Required           Validation        │
│  ═══════════        ═════════════════            ══════════        │
│                                                                   │
│  B1: CLAUDE.md ×10  claude-md-standard.md        validate-agents  │
│  │                  • 8 sections in order                         │
│  │                  • ≤ 4000 chars                                │
│  │                  • per-role content from fleet-elevation       │
│  │                  • both countdowns in context awareness        │
│  │                                                                │
│  B2: HEARTBEAT ×5   heartbeat-md-standard.md     validate-agents  │
│  │                  • 5 types (PM/ops/arch/devsec/worker)         │
│  │                  • priority order (PO directives FIRST)        │
│  │                  • per-role work variations                    │
│  │                                                                │
│  B3: IaC scripts    iac-mcp-standard.md          make setup       │
│  │                  • 6 scripts defined                           │
│  │                  • idempotent, config-driven                   │
│  │                  • Makefile targets                            │
│  │                                                                │
│  B4: agent.yaml ×10 agent-yaml-standard.md       validate-agents  │
│  │                  • 14 required fields                          │
│  │                  • fleet identity consistent                   │
│  │                  • roles.contributes_to matches synergy        │
│  │                                                                │
│  U-01: Identity     identity-soul-standard.md    validate-agents  │
│  │                  • top-tier expert language                    │
│  │                  • 10 anti-corruption rules in SOUL            │
│  │                  • per-role values and boundaries              │
│  │                                                                │
│  U-09: Self-knowl.  tools-agents-standard.md     validate-agents  │
│  │                  • chain-aware TOOLS.md (GENERATED)            │
│  │                  • synergy AGENTS.md (GENERATED)               │
│  │                  • bidirectional consistency                   │
│  │                                                                │
│  H3: Pre-embed      context-files-standard.md    unit tests       │
│  │                  • autocomplete chain (10 sections ordered)    │
│  │                  • NEVER compressed                            │
│  │                  • per-role data from role_providers            │
│  │                                                                │
│  H1,H5,U-18:       brain-modules-standard.md     unit tests       │
│  Brain modules      • 8 new modules defined                       │
│                     • 13-step orchestrator evolution               │
│                     • session_manager.py with decision tree       │
│                     • chain_registry.py with handlers             │
│                                                                   │
│  FLOW: standard → implement → validate → deploy → gateway → agent │
│                                                                   │
│  "Standards FIRST, then build. No code without meeting standard."  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 7. Agent Lifecycle — Sleep/Wake with Session Management

```
                     ┌──────────────────┐
                     │     ACTIVE       │
                     │  Working on task │
                     │  Real Claude     │
                     │  sessions        │
                     └────────┬─────────┘
                              │ task completes, no new assignment
                              │ 1 HEARTBEAT_OK → brain takes over
                              ↓
                     ┌──────────────────────────────────────────────┐
                     │     IDLE (brain takes over)                   │
                     │     Cron STILL fires — brain INTERCEPTS      │
                     │     ZERO Claude calls — brain evaluates FREE │
                     │     Silent heartbeat on each cron fire:      │
                     │                                              │
                     │     ┌─ Mention?        → WAKE (prompt)       │
                     │     ├─ Task assigned?  → WAKE (prompt)       │
                     │     ├─ Contribution?   → WAKE (prompt)       │
                     │     ├─ PO directive?   → WAKE (prompt)       │
                     │     ├─ Role trigger?   → WAKE (gradual)      │
                     │     ├─ Board activity? → WAKE (gradual)      │
                     │     └─ Nothing new     → STAY SLEEPING       │
                     │                                              │
                     │     + SESSION MANAGEMENT (brain Step 10):      │
                     │     ├─ Context > 40-80K + no work? → DUMP    │
                     │     ├─ Near rate limit rollover?   → COMPACT │
                     │     └─ Aggregate fleet math OK?    → OK      │
                     │                                              │
                     │     The cron NEVER stops. The agent is always │
                     │     on call. HeartbeatGate is the FILTER      │
                     │     between cron firing and Claude call.      │
                     │                                              │
                     └─────────┬──────────────────┬────────────────┘
                               │                  │
                     30min idle │                  │ wake trigger
                               ↓                  │ (task, mention,
                     ┌────────────────┐            │  tag, directive)
                     │   SLEEPING     │            │
                     │   (status:     │────────────┤
                     │   idle a long  │            │
                     │   time)        │            │
                     └───────┬────────┘            │
                             │ 4h                  │
                             ↓                     │
                     ┌────────────────┐            │
                     │   OFFLINE      │────────────┘
                     │   (status:     │
                     │   idle very    │
                     │   long time)   │
                     └────────────────┘

  ALL states respond the same to wake triggers.
  IDLE/SLEEPING/OFFLINE = status labels for visibility.
  Brain intercepts every cron fire regardless of state.
  
                                        ┌──────────────────┐
                          wake ────────→│     ACTIVE       │
                          trigger       │  (cycle restarts)│
                                        └──────────────────┘

  Cost flow (cron NEVER stops — brain FILTERS):
  ACTIVE:   Real Claude sessions, agent drives its own work  $$$
  IDLE:     Cron fires → brain intercepts → silent OK → $0   $0
            (after 1 HEARTBEAT_OK, brain takes over immediately)
  SLEEPING: Same as IDLE but longer cron interval             $0
  WAKING:   Brain detects trigger → fires ONE strategic call  $
  
  The cron never stops. The agent is always on call.
  The brain is the FILTER between cron firing and Claude call.
  After 1 HEARTBEAT_OK with nothing to do → brain relay → $0.
  10 agents, 7 idle/sleeping: ~70% cost reduction
```

---

## 8. Complete Task Flow — Dispatch to Done

```
  PO creates requirement on Plane
  │
  ├──→ Plane sync → OCMC PM task created
  │
  ├──→ Brain Step 4: Wake PM (inject_content)
  │
  ├──→ PM heartbeat: assign agent, set fields, set stage
  │    fleet_task_create(subtasks) if epic
  │
  ├──→ Brain Step 4: Create contribution tasks
  │    ├── architect: design_input (required for stories/epics)
  │    ├── qa: qa_test_definition (required for stories/epics)
  │    ├── devsecops: security_requirement (if applicable)
  │    ├── ux: ux_spec (if UI task)
  │    └── writer: documentation_outline (recommended)
  │
  ├──→ Contributors work through THEIR stages:
  │    ├── Architect: analysis → investigation → reasoning
  │    │   fleet_contribute(task_id, "design_input", content)
  │    ├── QA: reasoning
  │    │   fleet_contribute(task_id, "qa_test_definition", content)
  │    └── (others similarly)
  │
  ├──→ Brain checks: all required contributions received?
  │    YES → task can advance to work stage
  │
  ├──→ Engineer heartbeat: sees task in work stage
  │    Pre-embed includes: architect design, QA tests, security reqs
  │    ├── fleet_task_accept(plan)
  │    ├── fleet_commit(files, message) × N  [conventional commits]
  │    └── fleet_task_complete(summary)
  │        Chain fires:
  │        ├── git push
  │        ├── create PR (with labor stamp, changelog)
  │        ├── MC: task → review, create approval
  │        ├── IRC: #fleet, #reviews
  │        ├── ntfy: PO notification
  │        ├── Plane: issue state → "In Review"
  │        ├── Trail: completion recorded
  │        └── Parent evaluated (if all children done)
  │
  ├──→ Brain Step 6: Wake fleet-ops (inject_content)
  │
  ├──→ Fleet-ops heartbeat: REAL review
  │    ├── Read verbatim requirement
  │    ├── Read completion summary
  │    ├── Compare: work matches requirement?
  │    ├── Check acceptance criteria (each with evidence)
  │    ├── Check PR (conventional commits, clean diff)
  │    ├── Check trail (stages, contributions, gates)
  │    ├── Check phase standards
  │    └── fleet_approve(id, "approved"/"rejected", comment)
  │
  ├── If APPROVED:
  │   ├── Task → done
  │   ├── Trail recorded
  │   ├── Sprint progress updated
  │   ├── Parent evaluated
  │   ├── Writer notified (documentation update)
  │   └── Accountability verifies trail
  │
  └── If REJECTED:
      ├── Readiness regressed
      ├── Agent notified with specific feedback
      ├── Fix task created (auto)
      ├── Trail recorded
      └── Agent corrects → re-submit → review again
```

---

## 9. Document Hierarchy — 6-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: VISION                                                  │
│ ARCHITECTURE.md │ INTEGRATION.md │ MASTER-INDEX.md │ SPEC-TO-CODE│
│ What systems exist, how they connect, what's done vs designed    │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 2: SYSTEM REFERENCE                                        │
│ docs/systems/01-22 (10,000+ lines)                               │
│ Each system: purpose, modules, functions, connections, gaps      │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 3: DESIGN SPECIFICATIONS                                   │
│ fleet-elevation/ (31 docs) │ agent-rework/ (14 docs)            │
│ immune/ │ methodology/ │ context/ │ strategic (6 docs, 47 M-*) │
│ What to build, how, with PO requirements verbatim               │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 4: STANDARDS (quality gates)                               │
│ standards/ (8 per-type docs) │ agent-file-standards.md (index)  │
│ claude-md │ heartbeat │ agent.yaml │ identity-soul │ tools-agents│
│ context-files │ iac-mcp │ brain-modules                         │
│ Every file type: structure, validation, IaC, integration        │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 5: PLANS                                                   │
│ unified-implementation-plan.md (U-01 to U-38, 9 phases)        │
│ implementation-roadmap.md (Waves 1-5, 47 strategic milestones)  │
│ path-to-live.md │ ecosystem-deployment-plan.md │ WORK-BACKLOG   │
├─────────────────────────────────────────────────────────────────┤
│ LAYER 6: VERIFICATION                                            │
│ VERIFICATION-MATRIX.md (69/69 foundation verified)              │
│ (Strategic + agent = 0 live tests — the next frontier)          │
└─────────────────────────────────────────────────────────────────┘

 Reading order: 1 → 2 → 3 → 4 → 5 → 6
 Implementation order: 3 (design) → 4 (standard) → build → 6 (verify)
 
 ~110+ documents. ~60,000+ lines. 6 layers.
 Every layer references the ones above and below it.
```

---

## 10. Settings Propagation — OCMC to Fleet Operations

```
PO changes setting on OCMC board (fleet_config JSON field)
  │
  ↓
┌──────────────────────────────────────────────────────────────────┐
│                   OCMC fleet_config                              │
│                                                                  │
│  work_mode:    "full-autonomous"     ← what work happens         │
│  cycle_phase:  "execution"           ← what kind of work         │
│  backend_mode: "claude+localai"      ← which backends enabled    │
│  budget_mode:  "turbo"               ← fleet tempo               │
│                                                                  │
└──────────────────────┬───────────────────────────────────────────┘
                       │ brain reads every 30s cycle
                       ↓
┌──────────────────────────────────────────────────────────────────┐
│              BRAIN (Orchestrator) — applies settings              │
│                                                                  │
│  work_mode ──────→ dispatch gate                                 │
│    "work-paused"     → skip dispatch entirely                    │
│    "finish-current"  → no NEW tasks, finish active               │
│    "local-work-only" → PM doesn't pull from Plane                │
│                                                                  │
│  cycle_phase ────→ agent filter                                  │
│    "planning"        → only PM + architect active                │
│    "crisis"          → only fleet-ops + devsecops                │
│    "execution"       → all agents                                │
│                                                                  │
│  backend_mode ───→ router (which backends to consider)           │
│    "claude"          → Claude only                               │
│    "claude+localai"  → Claude + LocalAI                          │
│    "claude+localai+openrouter" → all three                       │
│    (7 combos total)                                              │
│                                                                  │
│  budget_mode ────→ tempo (cron/heartbeat frequency offset)       │
│    "turbo"           → faster orchestrator cycle                 │
│    "economic"        → slower, fit the plan                      │
│    (mode definitions TBD)                                        │
│                                                                  │
└──────────────────────┬───────────────────────────────────────────┘
                       │
          ┌────────────┼─────────────────┐
          ↓            ↓                 ↓
   ┌────────────┐ ┌─────────┐   ┌──────────────┐
   │  Gateway   │ │ Router  │   │  Budget      │
   │  CRONs     │ │         │   │  Monitor     │
   │            │ │ backend │   │              │
   │ heartbeat  │ │ _mode → │   │ OAuth quota  │
   │ intervals  │ │ filter  │   │ check before │
   │ adjusted   │ │ backends│   │ dispatch     │
   │ by tempo   │ │         │   │              │
   └────────────┘ └─────────┘   └──────────────┘

Current status:
  work_mode     → IMPLEMENTED (FleetControlState, should_dispatch)
  cycle_phase   → IMPLEMENTED (get_active_agents_for_phase)
  backend_mode  → CODE READY (7 combos in fleet_mode.py + router)
                   NOT WIRED (orchestrator doesn't pass to router yet)
  budget_mode   → STRUCTURE READY (BudgetMode dataclass)
                   NOT WIRED (no tempo offset applied yet)
                   MODE DEFINITIONS TBD (PO to define)

What needs wiring:
  1. Orchestrator reads backend_mode from FleetControlState
     → passes to route_task() on every dispatch
  2. Budget mode tempo_multiplier applied to orchestrator interval
     and gateway heartbeat CRONs
  3. Gateway CRON sync: when brain changes tempo, update
     gateway heartbeat configs via API or config reload
  4. LocalAI models loaded and health-checked before routing
```

---

## 11. Router Decision Flow — Backend Selection

```
Task arrives for dispatch
  │
  ↓
read backend_mode from FleetControlState
  │
  ↓
backends_for_mode(backend_mode) → enabled list
  │  "claude"              → [claude-code]
  │  "claude+localai"      → [claude-code, localai]
  │  "localai"             → [localai]
  │  "openrouter"          → [openrouter-free]
  │  "claude+openrouter"   → [claude-code, openrouter-free]
  │  "localai+openrouter"  → [localai, openrouter-free]
  │  "claude+localai+openrouter" → [claude-code, localai, openrouter-free]
  │
  ↓
assess_complexity(task) → trivial / simple / medium / complex / critical
  │
  ↓
filter enabled backends by:
  ├── has required capabilities? (reasoning, code, structured)
  ├── is available? (health check)
  ├── security agent? → skip free/trainee backends
  │
  ↓
sort by cost (cheapest first)
  │
  ↓
pick cheapest capable → RoutingDecision
  │  backend, model, effort, reason, fallback
  │
  ↓
circuit breaker check (if storm_monitor provided)
  │  breaker OPEN? → execute_fallback()
  │  both OPEN? → queue task (direct backend)
  │
  ↓
health check (if health_dashboard provided)
  │  backend DOWN? → execute_fallback()
  │
  ↓
final RoutingDecision returned to orchestrator
```

---

## 12. Contribution Flow — Cross-Agent Synergy

```
Task enters REASONING stage (readiness ~80-99%)
  │
  ↓
Brain reads synergy matrix (config/synergy-matrix.yaml)
  │  Who contributes to this agent's role?
  │
  ↓
Brain creates parallel contribution subtasks
  │
  ├─ architect:   "Design input for: {task_title}"
  │   Type: design_input
  │   Readiness: 99 (immediately dispatchable)
  │   Stage: work (contributions skip early stages)
  │
  ├─ qa-engineer: "Test criteria for: {task_title}"
  │   Type: qa_test_definition
  │
  └─ devsecops:   "Security requirements for: {task_title}"
      Type: security_requirement
      Condition: if task is security-relevant
  │
  ↓ Normal dispatch cycle picks up contribution tasks
  │
  ├─ Architect heartbeats → sees contribution task
  │   Reads parent task context
  │   Produces design_input artifact
  │   Calls fleet_contribute(contribution, parent_task_id)
  │     ├─ mc.post_comment() on parent task
  │     ├─ plane_sync.update_issue()
  │     ├─ context.update_target_task()
  │     ├─ Own contribution task → DONE
  │     ├─ events.emit("fleet.contribution.posted")
  │     └─ check_contribution_completeness()
  │
  ├─ QA heartbeats → produces qa_test_definition → fleet_contribute
  │
  └─ DevSecOps heartbeats → produces security_requirement → fleet_contribute
  │
  ↓
All required contributions received
  │
  ├─ PM notified: "All contributions received for {task_title}"
  ├─ Pre-embed updated: INPUTS FROM COLLEAGUES section
  ├─ Target agent sees contributions in next heartbeat
  └─ Dispatch gate for parent task: CLEAR
  │
  ↓
Target agent works with contributions embedded in context
  │  "From architect: use middleware pattern, file auth/jwt.py"
  │  "From QA: test token validation, expiry, 401 response"
  │  "From DevSecOps: no secrets in code, env vars only"
  │
  ↓
Agent implements → plan naturally references contributions
```

Contribution requirements by phase:
```
Phase          Required Contributions
─────────────────────────────────────────────
ideal          None
conceptual     Architect only
POC            Architect
MVP            Architect + QA + DevSecOps (if applicable)
staging        Architect + QA + DevSecOps + Tech Writer
production     ALL applicable contributions
```

---

## 13. Review Flow — Fleet-Ops 7-Step REAL Review

```
Agent calls fleet_task_complete(summary)
  │
  ├─ Tests run, branch pushed, PR created
  ├─ Task status: IN_PROGRESS → REVIEW
  ├─ Approval created: PENDING (confidence based on tests)
  ├─ Trail recorded: completion event
  │
  ↓
Brain Step 3: _ensure_review_approvals()
Brain Step 4: _wake_drivers()
  │  inject_content(fleet-ops.session_key, wake_msg)
  │  Cooldown: 300s between review wakes
  │
  ↓
Fleet-ops heartbeats → sees pending review
  │
  ↓
┌──────────────────────────────────────────────────────────────┐
│                    7-STEP REAL REVIEW                         │
│                                                              │
│  STEP 1: READ REQUIREMENT                                    │
│    Read requirement_verbatim word by word                    │
│    Compare with acceptance_criteria list                      │
│                                                              │
│  STEP 2: READ THE DIFF                                       │
│    FULL PR diff — every line added, every line removed        │
│    Not just file names — actual code changes                 │
│                                                              │
│  STEP 3: VERIFY ACCEPTANCE CRITERIA                          │
│    For EACH criterion:                                       │
│      ✓ Met by code changes?                                  │
│      ✗ Partially met?                                        │
│      ✗ Not addressed?                                        │
│    ALL must be ✓ for approval                                │
│                                                              │
│  STEP 4: CHECK TRAIL                                         │
│    Commits follow conventional format?                       │
│    Tests exist and pass?                                     │
│    Coverage maintained?                                      │
│    Labor stamp reasonable (time vs complexity)?               │
│                                                              │
│  STEP 5: VERIFY NO SCOPE CREEP                               │
│    Only what was asked? No extra refactoring?                │
│    No features not in requirements?                          │
│    No files outside task scope?                              │
│                                                              │
│  STEP 6: QUALITY CHECK                                       │
│    Security: no injection, XSS, SQL injection                │
│    Architecture: follows existing patterns                   │
│    Style: consistent with codebase                           │
│    No TODO/FIXME without tracking task                       │
│                                                              │
│  STEP 7: DECISION                                            │
│    APPROVE: confidence 80-95, specific reasoning             │
│    REJECT:  specific failures, readiness regression           │
│    ESCALATE: too complex or ambiguous → PO                   │
│                                                              │
│  ANTI-RUBBER-STAMP:                                          │
│    Doctor detects approval in <30 seconds → disease           │
│    Generic reasoning ("looks good") → disease                │
│    Skipping criteria check → disease                         │
└──────────────────────────────────────────────────────────────┘
  │
  ├─ APPROVED → Brain: REVIEW → DONE → event chain → trail
  ├─ REJECTED → readiness regresses → agent gets feedback
  └─ ESCALATED → ntfy PO → PO decides
```

---

## 14. Autocomplete Chain — Context as Behavior Driver

```
┌─────────────────────────────────────────────────────────────┐
│              INJECTION ORDER (top = first, most influence)    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Layer 1: IDENTITY.md                                  │   │
│  │ "You are Software Engineer, Fleet Alpha."             │   │
│  │ → Grounds all subsequent output in this identity      │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Layer 2: SOUL.md                                      │   │
│  │ "You value correctness over speed."                   │   │
│  │ → AI naturally produces careful, honest work          │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Layer 3: CLAUDE.md                                    │   │
│  │ "Follow 5-stage methodology. Anti-corruption rules."  │   │
│  │ → AI follows process established early in context     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Layer 4: TOOLS.md                                     │   │
│  │ "fleet_task_complete fires 12 operations."            │   │
│  │ → AI knows tool consequences before deciding          │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Layer 5: AGENTS.md                                    │   │
│  │ "Architect contributes design_input."                 │   │
│  │ → AI acknowledges and references contributions        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Layer 6: context/fleet-context.md                     │   │
│  │ "Fleet mode: full-autonomous. PO: focus on auth."     │   │
│  │ → AI incorporates current state into decisions        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Layer 7: context/task-context.md                      │   │
│  │ "VERBATIM: 'Add JWT middleware that...'               │   │
│  │  PLAN: 1. Create middleware 2. Add tests 3. Document  │   │
│  │  INPUTS: architect design + QA criteria + security"   │   │
│  │ → AI continues from plan step 1 naturally             │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Layer 8: HEARTBEAT.md                                 │   │
│  │ "Priority: PO directives → messages → task → OK"     │   │
│  │ → AI's immediate action IS the correct priority       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  RESULT: Most natural next token IS correct behavior.        │
│  Deviation requires FIGHTING the structure.                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 15. Phase System — Delivery Quality Gates

```
Task has TWO dimensions simultaneously:

  STAGE (how — processing):
  ┌────────┐  ┌────────┐  ┌─────────────┐  ┌──────────┐  ┌──────┐
  │convers.│→ │analysis│→ │investigation│→ │reasoning │→ │ work │
  └────────┘  └────────┘  └─────────────┘  └──────────┘  └──────┘
  readiness:  0%           20%              50%           80-99%   99%+

  PHASE (what quality — delivery maturity):
  ┌──────┐  ┌──────────┐  ┌─────┐  ┌─────┐  ┌────────┐  ┌──────────┐
  │ideal │→ │conceptual│→ │ POC │→ │ MVP │→ │staging │→ │production│
  └──────┘  └──────────┘  └─────┘  └─────┘  └────────┘  └──────────┘
  completeness: —          —        60%      80%         90%        100%

Phase gates (PO approval required):
  ┌─────────────────────────────────────────────────────┐
  │ Agent requests phase advance                         │
  │   ↓                                                  │
  │ Brain checks phase standards                         │
  │   Met? → route to PO                                 │
  │   Not met? → BLOCK with specific gaps                │
  │   ↓                                                  │
  │ PO approves → new phase, new standards apply         │
  │ PO rejects → stay, feedback provided                 │
  └─────────────────────────────────────────────────────┘

Phase-aware contribution requirements:
  POC:        architect only
  MVP:        architect + QA + DevSecOps
  staging:    + tech writer
  production: ALL applicable
```

---

## 16. Anti-Corruption — Three Lines of Defense

```
┌──────────────────────────────────────────────────────────────┐
│                LINE 1: STRUCTURAL PREVENTION                  │
│                (before disease appears)                        │
│                                                              │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ Autocomplete   │  │ Stage-gated  │  │ Contribution    │ │
│  │ chain          │  │ tools        │  │ as dispatch     │ │
│  │ engineering    │  │              │  │ gate            │ │
│  │                │  │ fleet_commit │  │                 │ │
│  │ Data ORDER     │  │ blocked in   │  │ Can't start     │ │
│  │ drives correct │  │ wrong stage  │  │ without design  │ │
│  │ behavior       │  │              │  │ input from      │ │
│  │                │  │ Physical     │  │ architect       │ │
│  │ Deviation =    │  │ rejection    │  │                 │ │
│  │ fighting the   │  │ not just     │  │ Phase-aware:    │ │
│  │ structure      │  │ suggestion   │  │ MVP needs QA    │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌──────────────┐                       │
│  │ Phase-aware    │  │ Verbatim     │                       │
│  │ standards      │  │ anchoring    │                       │
│  │ injection      │  │              │                       │
│  │                │  │ PO's exact   │                       │
│  │ MVP standards  │  │ words in     │                       │
│  │ in context →   │  │ EVERY context│                       │
│  │ agent produces │  │ layer        │                       │
│  │ MVP-quality    │  │              │                       │
│  │ naturally      │  │ Can't lose   │                       │
│  │                │  │ track of     │                       │
│  │                │  │ requirement  │                       │
│  └────────────────┘  └──────────────┘                       │
│                                                              │
│  Status: NOT BUILT (autocomplete.py, contribution gate,      │
│          phase standards injection missing)                   │
└──────────────────────────────────────────────────────────────┘
                          │
                          ↓
┌──────────────────────────────────────────────────────────────┐
│                LINE 2: DETECTION                              │
│                (when disease appears)                          │
│                                                              │
│  Doctor detections (4/11 implemented):                        │
│    ✓ protocol_violation  ✓ laziness                          │
│    ✓ stuck               ✓ correction_threshold              │
│    ✗ abstraction         ✗ code_without_reading              │
│    ✗ scope_creep         ✗ cascading_fix                     │
│    ✗ context_contamination  ✗ not_listening                  │
│    ✗ compression                                              │
│                                                              │
│  Structural detection:                                        │
│    Standards check artifact completeness (partial)            │
│    Accountability verifies trail completeness (not built)     │
│    Fleet-ops reviews against verbatim (designed)              │
│                                                              │
│  Status: 36% IMPLEMENTED                                     │
└──────────────────────────────────────────────────────────────┘
                          │
                          ↓
┌──────────────────────────────────────────────────────────────┐
│                LINE 3: CORRECTION                             │
│                (after detection)                              │
│                                                              │
│  ┌──────────┐ ┌──────────────┐ ┌───────────────┐            │
│  │ Teaching │ │ Force Compact│ │ Prune+Regrow  │            │
│  │          │ │              │ │               │            │
│  │ Specific │ │ Strip bloat  │ │ Kill session  │            │
│  │ lesson   │ │ agent stays  │ │ fresh start   │            │
│  │ injected │ │ but leaner   │ │ clean context │            │
│  └──────────┘ └──────────────┘ └───────────────┘            │
│                                                              │
│  ┌────────────────────────────────────────────────┐          │
│  │ Readiness Regression (NOT BUILT)               │          │
│  │ Task sent back to earlier stage                │          │
│  │ Agent restarts from fundamental level           │          │
│  └────────────────────────────────────────────────┘          │
│                                                              │
│  Status: CORRECTION MECHANISM EXISTS (teach/compact/prune),  │
│          but 7 diseases can't trigger it. Regression missing.│
└──────────────────────────────────────────────────────────────┘
```

---

## 17. Trail & Audit — Complete Task Record

```
Every task has a chronological trail of EVERYTHING:

  CREATION
  ┌─────────────────────────────────────────┐
  │ trail.task.created                       │
  │   by: PM, type: story, parent: epic-42   │
  │   phase: mvp, priority: high             │
  └──────────────────────┬──────────────────┘
                         ↓
  STAGE PROGRESSION
  ┌─────────────────────────────────────────┐
  │ trail.task.stage_changed                 │
  │   conversation → analysis (by PM)        │
  │ trail.task.stage_changed                 │
  │   analysis → investigation (by engineer) │
  │ trail.task.readiness_changed             │
  │   0% → 50% (checkpoint)                 │
  │ trail.task.stage_changed                 │
  │   investigation → reasoning              │
  └──────────────────────┬──────────────────┘
                         ↓
  CONTRIBUTIONS
  ┌─────────────────────────────────────────┐
  │ trail.contribution.requested             │
  │   type: design_input, from: architect    │
  │ trail.contribution.posted                │
  │   type: design_input, by: architect      │
  │ trail.contribution.all_received          │
  │   design_input ✓ qa_test_def ✓           │
  └──────────────────────┬──────────────────┘
                         ↓
  GATE
  ┌─────────────────────────────────────────┐
  │ trail.gate.requested                     │
  │   readiness: 90%, evidence: plan artifact│
  │ trail.gate.decided                       │
  │   approved by PO → readiness 99%         │
  └──────────────────────┬──────────────────┘
                         ↓
  WORK
  ┌─────────────────────────────────────────┐
  │ trail.commit.created × N                 │
  │   SHA, message, files, agent             │
  │ trail.pr.created                         │
  │   URL, branch, title                     │
  │ trail.task.completed                     │
  │   summary, test results, labor stamp     │
  └──────────────────────┬──────────────────┘
                         ↓
  REVIEW
  ┌─────────────────────────────────────────┐
  │ trail.review.started (by fleet-ops)      │
  │ trail.review.qa_validated               │
  │ trail.review.security_completed         │
  │ trail.review.approved                    │
  │   confidence: 90%, reasoning: specific   │
  └──────────────────────┬──────────────────┘
                         ↓
  DONE
  ┌─────────────────────────────────────────┐
  │ trail.task.done                          │
  │   approval granted, all criteria met     │
  │   Plane updated, IRC notified            │
  └─────────────────────────────────────────┘

Storage: Board memory entries tagged trail + task:{id} + type
Consumers: fleet-ops (review Step 4), accountability (compliance),
           PO (OCMC/Plane), doctor (gap detection)
```

---

## 18. Notification Routing — Who Gets Notified When

```
EVENT                    → CHANNELS
──────────────────────────────────────────────────────────────
Task created              → IRC #fleet + Plane + trail
Task assigned             → IRC #fleet + mention:agent + trail
Task dispatched           → IRC #fleet + trail
Readiness at 50%          → trail + Plane comment
Readiness at 90% (gate)   → IRC #gates + ntfy PO + trail
Gate approved/rejected    → IRC #gates + trail
Contribution requested    → IRC #contributions + mention:role
Contribution posted       → IRC #contributions + mention:target
All contributions in      → trail + Plane comment
Task completed (PR)       → IRC #reviews + ntfy PO + trail + Plane
Fleet-ops approved        → IRC #reviews + trail + Plane → DONE
Fleet-ops rejected        → IRC #reviews + mention:agent + trail
Readiness regressed       → IRC #fleet + mention:agent + trail
Security alert            → IRC #alerts + ntfy PO + trail
Escalation                → IRC #alerts + ntfy urgent + trail
Storm WARNING+            → IRC #alerts + ntfy (STORM+) + trail
Disease detected          → IRC #alerts + trail
Fleet mode changed        → IRC #fleet + trail

CHANNELS:
  IRC #fleet         General activity
  IRC #reviews       Review requests + decisions
  IRC #alerts        Security, escalation, health, storm
  IRC #gates         Gate requests + PO decisions        ← NOT IMPLEMENTED
  IRC #contributions Contribution posts + completions    ← NOT IMPLEMENTED
  ntfy fleet-alert   PO mobile notifications
  ntfy fleet-review  Review notifications                ← NOT IMPLEMENTED
  ntfy fleet-gates   Gate request notifications          ← NOT IMPLEMENTED
  Board memory       Mentions, directives, trail
  Plane              Issue state + comments
```
