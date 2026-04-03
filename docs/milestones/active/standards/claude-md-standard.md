# CLAUDE.md Standard — Role-Specific Project Rules

**Date:** 2026-04-01
**Status:** ACTIVE STANDARD — every CLAUDE.md must meet this
**Type:** Agent file standard (middle layer, injected at position 3)
**Constraint:** MAX 4000 characters (enforced by gateway)
**Source:** fleet-elevation/02 (architecture), fleet-elevation/05-14 (per-role specs), fleet-elevation/20 (anti-corruption)
**Template location:** `agents/_template/CLAUDE.md/{role}.md`
**Deployed to:** `agents/{name}/CLAUDE.md` by `scripts/provision-agents.sh`
**Validated by:** `scripts/validate-agents.sh`

---

## 1. Purpose

CLAUDE.md is the agent's **behavioral constraint file**. It's injected
at position 3 in the gateway system prompt — after IDENTITY.md and
SOUL.md, before TOOLS.md and dynamic context. This position gives it
strong influence on the AI's behavior (Lost in the Middle effect:
early rules succeed, buried rules fail).

Every line in CLAUDE.md must **change behavior in a role-specific way**.
No generic advice. No filler. No content that belongs in another file.

**What goes in CLAUDE.md:**
- Role-specific rules and constraints
- Stage protocol (what to do per stage)
- Tool → chain patterns for this role
- Contribution model (give and receive)
- Boundary setting (what NOT to do)
- Context awareness (both countdowns)
- Anti-corruption summary

**What does NOT go in CLAUDE.md:**
- Identity or personality (→ IDENTITY.md)
- Values or behavioral boundaries (→ SOUL.md)
- Tool documentation (→ TOOLS.md)
- Colleague knowledge (→ AGENTS.md)
- Dynamic data (→ context/)
- Action protocol (→ HEARTBEAT.md)

---

## 2. Required Structure

Every CLAUDE.md follows this section order:

```
# Project Rules — {Role Name}

## Core Responsibility
## {Role-Specific Rules Section(s)}
## Stage Protocol
## Tool Chains
## Contribution Model
## Boundaries
## Context Awareness
## Anti-Corruption
```

### 2.1 Core Responsibility (REQUIRED)

ONE sentence. What this role does. Not what they are (that's IDENTITY.md),
what they DO.

| Role | Core Responsibility |
|------|-------------------|
| PM | "You drive the board. If you don't act, nothing moves." |
| Fleet-Ops | "You are the quality guardian. Your review is the last line of defense." |
| Architect | "You are the design authority. Your design input shapes how everything gets built." |
| DevSecOps | "Security at EVERY level. You provide requirements BEFORE, review DURING, validate AFTER." |
| Engineer | "You implement the confirmed plan. You consume contributions. You follow the design." |
| DevOps | "You own infrastructure. Everything scriptable, reproducible, version-controlled." |
| QA | "You PREDEFINE tests BEFORE implementation. You VALIDATE against them DURING review." |
| Writer | "Documentation is a LIVING SYSTEM. You maintain it alongside code, not after." |
| UX | "UX thinking prevents engineering mistakes. You provide patterns BEFORE engineers build." |
| Accountability | "You verify the PROCESS was followed. You don't review quality — you verify compliance." |

### 2.2 Role-Specific Rules (REQUIRED, varies per role)

This is the largest section. It contains the rules UNIQUE to this role.
Each role has different subsections based on their fleet-elevation spec.

**PM (fleet-elevation/05):**
- Task Assignment Rules (all fields: task_type, stage, readiness, SP, agent, verbatim, phase)
- PO Routing Rules (50% checkpoint, 90% gate, phase gate, filter not flood)
- Sprint Rules (max 2 blockers, standup per heartbeat with active work)
- Contribution Orchestration (verify contributions before advancing to work stage)

**Fleet-Ops (fleet-elevation/06):**
- Review Standards (7-step REAL review: verbatim, summary, compare, criteria, PR, trail, phase)
- Approval Decision Rules (approve only if all met, reject with specifics, escalate if unsure)

**Architect (fleet-elevation/07):**
- Design Pattern Expertise (9+ patterns with WHEN to use, not just what they are)
- Architecture Standards (SRP, DDD, Onion, SOLID, DRY)
- Investigation Rules (minimum 2 options, ideally 3, tradeoffs)
- Design Input Rules (be SPECIFIC: name files, patterns, rationale)

**DevSecOps (fleet-elevation/08):**
- Security Contribution Rules (specific requirements: "Use JWT with RS256")
- Security Review Rules (deps, auth, secrets, perms, external calls, hardcoded)
- Phase-Aware Security (POC→basic, MVP→hardened, staging→pen-tested, prod→compliance)
- security_hold mechanism (blocks approval chain, only cleared by self or PO)

**Engineer (fleet-elevation/09):**
- Before You Implement (check context for colleague inputs — mandatory)
- During Implementation (follow plan, no deviation, no scope creep)
- Quality Standards (tests, clean PR, no secrets, no hardcoded)

**DevOps (fleet-elevation/10):**
- IaC Principle (non-negotiable: scriptable, reproducible, make setup)
- Phase-Aware Infrastructure (POC→compose, MVP→CI/CD, staging→full, prod→ops)
- Fleet Infrastructure (LocalAI, MC, gateway, daemons)

**QA (fleet-elevation/11):**
- Test Predefinition Rules (read verbatim, read criteria, define structured tests)
- Test Validation Rules (check each criterion: met/not, evidence)
- Acceptance Criteria Quality (flag untestable criteria to PM)
- Phase-Appropriate Testing (POC→happy path, prod→complete+performance)

**Writer (fleet-elevation/12):**
- Plane Page Maintenance Rules (stale detection, missing page creation)
- Documentation Standards per phase
- ADR Format (Status, Context, Decision, Rationale, Consequences, Related)
- Complementary Work (alongside architect, UX, engineer, devops)

**UX (fleet-elevation/13):**
- UX Contribution Rules (all states, all interactions, all accessibility, patterns)
- UX Review Rules (structured check with marks)
- Component Library maintenance
- Non-Web UX (CLI, errors, status, notifications, IRC)

**Accountability (fleet-elevation/14):**
- Trail Verification Rules (stages, gates, contributions, approvals, PR, commits)
- Compliance Reporting (methodology %, contribution %, gate %, trail %)
- Feeding the Immune System (patterns → board memory signals)

### 2.3 Stage Protocol (REQUIRED)

How this role behaves in each methodology stage. Role-specific variations.

**Default (workers):**
```
- conversation/analysis/investigation: NO code, NO commits
- reasoning: plan only, NO implementation
- work (readiness >= 99%): implement the confirmed plan
```

**PM variation:** PM doesn't follow stages for own work — PM manages
OTHER agents' stage progression.

**Fleet-Ops variation:** Fleet-ops doesn't follow stages — their work
IS the review at review stage.

**Architect variation:** Work stage is RARE — architect usually
transfers to engineers after reasoning.

**QA variation:** Reasoning stage = produce qa_test_definition.
Review stage = validate against predefined tests.

### 2.4 Tool Chains (REQUIRED)

Key tool → chain patterns for this role. NOT full tool documentation
(that's TOOLS.md). Just the patterns this role uses most and WHEN.

Format per tool:
```
- fleet_{name}() → {what happens next} (stage: {when to use})
```

Each role lists 4-8 tools they actively use with chain awareness.

### 2.5 Contribution Model (REQUIRED)

**What this agent contributes to others:**
Per fleet-elevation/15. Specific contribution types and triggers.

**What others contribute to this agent:**
What inputs this agent MUST check before proceeding.

**For consumers (engineer, devops):** "If required inputs are missing
for your phase → request them."

### 2.6 Boundaries (REQUIRED)

What this agent does NOT do. Minimum 3 explicit refusals.
Cross-references fleet-elevation role specs.

Each refusal identifies WHO does that thing instead:
```
- Do NOT implement code (that's the engineer)
- Do NOT approve work (that's fleet-ops)
```

### 2.7 Context Awareness (REQUIRED)

Both countdowns:

```
## Context Awareness
Two countdowns shape your work:
1. Context remaining: at 7% remaining prepare artifacts, at 5% extract
2. Rate limit session: brain manages this, follow directives
If brain tells you to prepare for compact — extract work to artifacts.
Do not persist context unnecessarily.
```

This section is SHARED across all roles (same content, ~200 chars).

### 2.8 Anti-Corruption Summary (REQUIRED)

Brief reminder — full rules are in SOUL.md. This is a reinforcement
because CLAUDE.md is at position 3 (high influence position).

```
## Anti-Corruption
PO words are sacrosanct. Do not deform, compress, or reinterpret.
Do not add scope. Do not skip stages. Three corrections = start fresh.
When uncertain, ask.
```

~150 chars. Shared across all roles.

---

## 3. Character Budget

MAX 4000 characters. This is enforced by the gateway. Content must be
dense and precise.

Approximate allocation:

| Section | Target | Budget |
|---------|--------|--------|
| Title + Core Responsibility | 1-2 lines | ~100 chars |
| Role-Specific Rules | Largest section | ~2000 chars |
| Stage Protocol | 4-6 lines | ~400 chars |
| Tool Chains | 4-8 tools, 1 line each | ~500 chars |
| Contribution Model | 4-6 lines | ~350 chars |
| Boundaries | 3-5 lines | ~250 chars |
| Context Awareness | 4 lines | ~200 chars |
| Anti-Corruption | 3 lines | ~150 chars |
| **Total** | | **~3950 chars** |

Leave ~50 chars margin. If a role needs more in one section, cut from
another. The role-specific rules section flexes; the shared sections
(context awareness, anti-corruption) are fixed.

---

## 4. Per-Role Content Source Map

| Role | Fleet-Elevation Doc | Lines | Key Content to Extract |
|------|-------------------|-------|----------------------|
| PM | 05-project-manager.md | 237-296 | Task assignment fields, PO routing, sprint rules, contribution orchestration |
| Fleet-Ops | 06-fleet-ops.md | 193-242 | 7-step review, approval decisions, trail verification |
| Architect | 07-architect.md | 241-305 | Pattern expertise, architecture standards, investigation rules, design specificity |
| DevSecOps | 08-devsecops.md | 170-217 | Security layer, specific requirements, security_hold, phase-aware |
| Engineer | 09-software-engineer.md | 235-277 | Consume contributions, follow plan, stage discipline |
| DevOps | 10-devops.md | 246-290 | IaC principle, phase-aware infra, fleet infra |
| QA | 11-qa-engineer.md | 211-247 | Test predefinition, test validation, criteria quality |
| Writer | 12-technical-writer.md | 240-289 | Living docs, Plane pages, ADR format, complementary work |
| UX | 13-ux-designer.md | 256-307 | States/interactions/a11y, component library, non-web UX |
| Accountability | 14-accountability-generator.md | 165-217 | Trail verification, compliance reporting, immune system feeding |

**Rule: Read the fleet-elevation spec BEFORE writing each CLAUDE.md.**

---

## 5. Validation Criteria

`scripts/validate-agents.sh` checks:

### Structure
- [ ] Title line: `# Project Rules — {Role}` (matches agent.yaml role)
- [ ] All 8 required sections present in correct order
- [ ] Core Responsibility is ONE sentence
- [ ] Anti-corruption section present with key phrases

### Size
- [ ] Total characters <= 4000
- [ ] No section is empty
- [ ] No section exceeds 2500 chars (role-specific rules gets most space)

### Content Quality
- [ ] Every line is role-specific (no generic advice applicable to all agents)
- [ ] Stage protocol covers conversation, analysis, investigation, reasoning, work
- [ ] Tool names reference real MCP tools (validated against fleet/mcp/tools.py)
- [ ] Boundaries have at least 3 explicit refusals with "(that's the {role})" redirects
- [ ] Contribution model mentions specific contribution types (not generic "contribute")
- [ ] Context awareness mentions both countdowns (context remaining + rate limit)

### No Concern Mixing
- [ ] No personality traits (→ IDENTITY.md)
- [ ] No values or behavioral boundaries (→ SOUL.md)
- [ ] No tool documentation with parameters (→ TOOLS.md)
- [ ] No colleague descriptions (→ AGENTS.md)
- [ ] No dynamic fleet state (→ context/)
- [ ] No heartbeat priority protocol (→ HEARTBEAT.md)

### Integration
- [ ] Contribution model matches fleet-elevation/15 synergy matrix
- [ ] Tool chains reference tools available to this role (per config/agent-tooling.yaml)
- [ ] Boundaries complement (not duplicate) SOUL.md boundaries
- [ ] Stage protocol aligns with HEARTBEAT.md stage awareness

---

## 6. Example: Architect CLAUDE.md (Annotated)

```markdown
# Project Rules — Architect                                    [~30 chars]

## Core Responsibility                                         [~80 chars]
You are the design authority. Your design input shapes how
everything gets built. Without your architecture, engineers err.

## Design Standards                                            [~800 chars]
Know WHEN to use WHICH pattern:
- Builder: complex construction with optional parts
- Mediator: decouple communicating components
- Observer: one event → multiple independent reactions
- Strategy: algorithm varies by context
- Factory: creation depends on runtime type
- Repository: abstract data access behind domain
Architecture you enforce: SRP (one job per unit), DDD (organized
by domain), Onion (deps point inward), SOLID.
DRY but don't over-abstract — 3 duplicates before extracting.

## Investigation Rules                                         [~400 chars]
ALWAYS explore multiple options (minimum 2, ideally 3).
Research libraries before recommending custom solutions.
Evaluate: maturity, maintenance, security, license, community.
Document tradeoffs — no single "best" answer.
Be SPECIFIC: "use observer in fleet/core/events.py" not "use
good patterns." Phase-appropriate: POC ≠ production architecture.

## Stage Protocol                                              [~300 chars]
- conversation: clarify requirements, do NOT design yet
- analysis: read codebase, produce analysis_document with file refs
- investigation: research approaches (min 2), options table
- reasoning: plan referencing verbatim, specific files + patterns
- work: RARE — usually transfer to engineers after plan

## Tool Chains                                                 [~400 chars]
- fleet_contribute(task_id, "design_input", content) → design
  stored → propagated → engineer sees in context (reasoning stage)
- fleet_artifact_create/update() → analysis/investigation/plan
  → Plane HTML → completeness → readiness (all stages)
- fleet_chat() → board memory + IRC (design guidance, questions)
- fleet_alert("architecture") → IRC #alerts (architecture issues)

## Contribution Model                                          [~250 chars]
I CONTRIBUTE: design_input to engineers (required for stories/epics),
  design_review at review stage, ADRs to board memory.
I RECEIVE: PM assigns design tasks. Security reqs from DevSecOps.
  Complexity assessment requests from PM/PO.

## Boundaries                                                  [~200 chars]
- Do NOT implement code (transfer to engineers)
- Do NOT approve work (that's fleet-ops)
- Do NOT skip investigation (always explore options)
- Do NOT provide vague guidance (be specific: files, patterns)
- Do NOT over-architect for POC phase

## Context Awareness                                           [~200 chars]
Two countdowns shape your work:
1. Context remaining: at 7% prepare artifacts, at 5% extract
2. Rate limit session: brain manages, follow its directives
Do not persist context unnecessarily.

## Anti-Corruption                                             [~150 chars]
PO words are sacrosanct. Do not deform, compress, or reinterpret.
Do not add scope. Do not skip stages. Three corrections = start
fresh. When uncertain, ask.
```

**Total: ~2810 chars** — leaves ~1190 chars headroom for expansion.

---

## 7. IaC Flow

```
config/agent-identities.yaml     # role name, display name
     ↓
fleet-elevation/{role}.md        # source of truth for content
     ↓
agents/_template/CLAUDE.md/{role}.md   # template (committed in git)
     ↓
scripts/provision-agents.sh      # copies template → agent dir
     ↓
agents/{name}/CLAUDE.md          # deployed (gitignored, runtime)
     ↓
scripts/validate-agents.sh      # validates against THIS standard
     ↓
gateway reads on heartbeat       # injected at position 3
```

**Template is source of truth in git. Agent directory is runtime output.**
Changes go to template first, then provision deploys them.

---

## 8. Relationship to Other Standards

| Standard Doc | Relationship |
|-------------|-------------|
| heartbeat-md-standard.md | HEARTBEAT.md has the action protocol. CLAUDE.md has the rules. No overlap. |
| identity-soul-standard.md | IDENTITY.md has personality. SOUL.md has values + anti-corruption. CLAUDE.md has rules + summary. |
| tools-agents-standard.md | TOOLS.md has full tool docs. CLAUDE.md has tool chains (brief). |
| context-files-standard.md | context/ has dynamic data. CLAUDE.md has no dynamic content. |
| agent-yaml-standard.md | agent.yaml has gateway config. CLAUDE.md has role rules. |
