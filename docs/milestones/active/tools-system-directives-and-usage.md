# Tools System — Directives, Usage Guidance, and Strategic Decisions

**Date:** 2026-04-07
**Status:** Analysis — how agents know when to use what, how, why
**Part of:** [tools-system-session-index.md](tools-system-session-index.md)
**Complements:** tools-system-full-capability-map.md (WHAT exists per role), this doc covers HOW agents are directed to use it

---

## What This Document Covers

Having capabilities is not enough. A top-tier expert knows WHEN to use WHICH capability, with WHAT input, expecting WHAT output, and UNDERSTANDING the impact. This document maps the directive system — how agents receive guidance on capability usage.

---

## The Directive Layers

Agents receive capability usage guidance from 7 sources, injected at different points in the autocomplete chain:

```
INJECTION ORDER (gateway reads these into system prompt):

Position 1: IDENTITY.md     → "I am the architect, design authority"
                                (establishes WHO — shapes which capabilities feel natural)

Position 2: SOUL.md         → "I value design before implementation"
             + STANDARDS.md     (establishes VALUES — shapes WHY certain tools matter)
             + MC_WORKFLOW.md   (establishes WORKFLOW — the tool usage sequence)

Position 3: CLAUDE.md       → "Stage Protocol: at analysis, use these tools"
                                "Tool Chains: fleet_contribute → propagates everywhere"
                                "Boundaries: do NOT implement, that's the engineer"
                                (establishes RULES — hard constraints on capability usage)

Position 4: TOOLS.md        → "fleet_commit: What/When/Chain/Input/You do NOT need to"
                                "Skills: at REASONING stage → /writing-plans"
                                "Sub-agents: code-explorer for codebase navigation"
                                (establishes CAPABILITIES — what's available and how it works)

Position 5: AGENTS.md       → "Architect contributes design_input to Engineer"
                                "When to @mention: design input unclear"
                                (establishes RELATIONSHIPS — how capabilities connect to colleagues)

Position 6: context/        → "Current stage: analysis. Readiness: 35%."
                                "Assigned task: Design auth middleware"
                                "Contributions received: QA tests ✓, UX spec pending"
                                (establishes SITUATION — which capabilities are appropriate NOW)

Position 7: HEARTBEAT.md    → "Priority 0: PO directives → execute immediately"
                                "Priority 2: Core Job → contribute design input"
                                "If nothing: HEARTBEAT_OK"
                                (establishes ACTION — what to do RIGHT NOW with available capabilities)
```

The autocomplete chain works because by position 7, the agent knows:
- WHO they are (identity) → shapes natural capability selection
- WHY tools matter (values) → shapes motivation to use them correctly
- WHAT the rules are (CLAUDE.md) → hard constraints on what's allowed
- WHAT they can do (TOOLS.md) → complete capability reference
- WHO they work with (AGENTS.md) → when to involve others
- WHAT's happening (context) → current situation
- WHAT to do NOW (HEARTBEAT.md) → specific action

The CORRECT action is the natural continuation of all 7 layers.

---

## Directive Types

### Type 1: Stage-Methodology Directives

These tell agents WHAT CAPABILITIES are appropriate at each methodology stage. Source: config/methodology.yaml protocol text + config/skill-stage-mapping.yaml + CLAUDE.md stage protocol section.

**Pattern:** "At {stage} stage, you SHOULD use {capabilities}. You MUST NOT use {blocked capabilities}."

Example for architect at ANALYSIS stage:
```
## Current Stage: ANALYSIS

### Recommended capabilities:
- filesystem MCP: examine codebase structure, read relevant files
- /systematic-debugging: if investigating existing behavior
- fleet_artifact_create("analysis_document"): start building findings
- code-explorer sub-agent: delegate deep codebase navigation

### What you MUST do:
- Reference SPECIFIC files and line numbers, not vague descriptions
- Produce analysis_document artifact progressively
- Present findings to PO via task comments

### What you MUST NOT do:
- Do NOT produce solutions (reasoning stage)
- Do NOT write implementation code
- Do NOT call fleet_task_complete
- Do NOT call fleet_commit (analysis produces documents, not code)
  Exception: committing the analysis document itself IS allowed
```

### Type 2: Contribution Directives

These tell agents WHEN and HOW to contribute to other agents' tasks. Source: config/synergy-matrix.yaml + AGENTS.md + CLAUDE.md contribution model.

**Pattern:** "When assigned a contribution task of type {type}, use {capabilities} to produce {output} and call fleet_contribute with {specific content}."

Example for QA contributing test predefinition:
```
## Contribution: qa_test_definition

### When:
Brain creates contribution task targeting your role.
Target task is entering REASONING stage.

### How:
1. Read target task verbatim requirement
2. Read acceptance criteria
3. Read architect design input (if available)
4. Use /test-predefinition skill

### What to produce:
Structured test criteria in TC-XXX format:
- TC-001: description, type (unit/integration/e2e), priority, verification method
- TC-002: ...
Phase-appropriate: POC = happy path, production = comprehensive

### Input to fleet_contribute:
fleet_contribute(
  task_id=TARGET_TASK_ID,
  contribution_type="qa_test_definition",
  content=structured_test_criteria
)

### Impact:
- Content posted as typed comment on target task
- Target agent sees criteria in their context during work stage
- Each TC-XXX becomes a REQUIREMENT for the implementation
- During review, QA validates each TC-XXX: met or not met
```

### Type 3: Tool Usage Directives

These tell agents HOW to use specific tools — input expectations, output understanding, chain impact. Source: config/tool-chains.yaml + TOOLS.md.

**Pattern:** "fleet_{tool}: call with {input}. It will do {primary action} and automatically {chain operations}. You do NOT need to {what the chain handles}."

Example:
```
### fleet_task_complete

**What:** Complete task — triggers full review chain
**When:** Work stage ONLY. All acceptance criteria met. Tests pass.
**Input:** summary (what you did and why — 2-3 sentences)

**What happens when you call it (tree):**
1. Push branch to remote
2. Create PR with changelog, diff table, labor stamp
3. Update task status → review
4. Create approval for fleet-ops
5. Post completion comment on task
6. Notify IRC #fleet and #reviews
7. Send ntfy notification to PO
8. Update linked Plane issue state
9. Record trail event
10. Evaluate parent task (if children all done → parent to review)

**You do NOT need to:**
- Push code (automatic)
- Create PR (automatic — uses pr template with URLs, changelog, diff)
- Notify reviewers (automatic — IRC + ntfy + fleet-ops heartbeat wake)
- Update Plane (automatic — state + labels + comment)
- Record trail (automatic)

**Impact:**
- Task moves to review
- Fleet-ops sees it on next heartbeat
- PO gets notification
- Plane issue reflects "In Review" state
- Trail records completion event
```

### Type 4: Strategic Feature Directives

These tell agents WHEN to use expensive/advanced features. Source: fleet-elevation/23 (strategic calls) + CLAUDE.md + skill instructions.

**Pattern:** "Use {feature} WHEN {conditions}. It costs {impact}. The benefit is {value}."

```
## When to Use Extended Thinking (High Effort)

USE HIGH EFFORT WHEN:
- Analyzing complex codebase (many files, deep dependency chains)
- Exploring multiple design approaches (investigation stage)
- Producing implementation plans for L/XL tasks
- Security analysis requiring thoroughness
- Debugging subtle issues with systematic-debugging skill

USE MEDIUM EFFORT WHEN:
- Executing a confirmed plan (work stage — plan already made)
- Writing code following existing patterns
- Routine commits and comments
- Standard heartbeat processing

USE LOW EFFORT WHEN:
- Heartbeat with no assigned work (status check)
- Simple CRON operations (daily summary)
- Acknowledging messages (HEARTBEAT_OK)

## When to Spawn Sub-Agents

SPAWN SUB-AGENT WHEN:
- Codebase exploration would bloat your main context (use code-explorer)
- You need parallel research on independent topics (use dispatching-parallel-agents skill)
- Pre-completion review (use subagent-driven-development skill for 2-stage check)
- Multiple independent tests need running (delegate to test-runner)

DO NOT SPAWN WHEN:
- Task is simple and sequential (overhead not worth it)
- You need the sub-agent's output before your next step AND can't continue in parallel
- Context sharing is critical (sub-agents have isolated context)

## When to Use Adversarial Spec Review

USE ADVERSARIAL-SPEC WHEN:
- Major architecture decision with multiple valid approaches
- Spec could have blind spots — need external perspectives
- Investigation stage for complex features
- PO requested thorough option exploration

DO NOT USE WHEN:
- Decision is straightforward (one clearly best option)
- Time pressure — adversarial review is expensive (multiple LLM calls)
- Task is a subtask or small change

## When to Use Plan Mode vs Direct Execution

USE /writing-plans SKILL WHEN:
- Task has 3+ files to modify
- Task has story points >= 5
- Task type is story or epic
- Implementation approach isn't obvious from the requirement
- Required contributions (architect design, QA tests) need referencing

EXECUTE DIRECTLY WHEN:
- Task is a subtask with clear scope
- Story points 1-2
- Single file change
- Fix task with specific feedback to address
```

### Type 5: Group Call Usage Directives (Role-Specific)

These tell agents WHEN and HOW to use their role-specific group calls. Source: TOOLS.md + CLAUDE.md.

**Pattern per role-specific group call:**

```
## pm_sprint_standup (PM role-specific)

**When:** Every heartbeat cycle with active sprint
**What it needs:** Sprint ID, task list, agent status
**What it does:**
1. Aggregate sprint state (tasks by status, velocity, blockers)
2. Format standup report per template
3. Post to board memory [sprint]
4. Notify IRC #sprint
5. Comment on Plane cycle (if connected)
6. Record trail

**Output:** Formatted sprint summary visible to PO and all agents
**Impact:** PO sees sprint progress without asking. Agents see fleet state.
**When NOT to use:** When fleet is paused, when no active sprint
```

### Type 6: CRON Directives (Via Standing Orders)

CRONs reference standing orders for their procedures. The standing order IS the directive.

**Pattern:**

```
## Standing Order: Nightly Dependency Scan (DevSecOps)

**Scope:** Scan all project dependencies for known vulnerabilities
**Trigger:** CRON fires at 01:00 daily (isolated session, opus, high thinking)
**Procedure:**
1. For each project in config/projects.yaml:
   a. Read dependency files (requirements.txt, package.json, etc.)
   b. Check against CVE databases (via semgrep MCP or pip audit/npm audit)
   c. Classify findings: critical / high / medium / low
2. Produce vulnerability_report artifact
3. For critical findings:
   a. fleet_alert(category="security", severity="critical", ...)
   b. Set security_hold on affected tasks (if any)
   c. Escalate to PO via ntfy
4. For non-critical:
   a. Post summary to board memory [security, audit]
5. Record trail

**Approval gates:** Critical findings escalate to PO. Non-critical are autonomous.
**Escalation:** If scan fails (dependency service unavailable), alert fleet-ops.
**What NOT to do:** Do NOT fix vulnerabilities in this CRON. Create fix tasks.
**Budget awareness:** If fleet over budget threshold, skip scan and log "skipped: budget".
```

### Type 7: Hook Directives (Structural Enforcement)

Hooks enforce directives structurally — not by telling the agent, but by blocking or warning on violations.

**Pattern:**

```
## PreToolUse Hook: Commit Format Validation (Engineer)

**Fires on:** fleet_commit
**Checks:** Does the commit message match conventional format?
  - Pattern: type(scope): description [task:XXXXXXXX]
  - Valid types: feat, fix, docs, refactor, test, chore, ci, style, perf
**If violation:**
  - Exit code 2 → blocks the commit
  - Error message: "Commit message doesn't match conventional format.
    Expected: type(scope): description [task:XXXXXXXX]"
**Impact:** Agent cannot commit with wrong format — structural enforcement
```

---

## How Directives Are Delivered — The Full Picture

```
STATIC DIRECTIVES (baked into agent files, don't change per task):
  CLAUDE.md → stage protocol, tool chains, contribution model, boundaries
  HEARTBEAT.md → priority protocol, core job, when to HEARTBEAT_OK
  TOOLS.md → capability reference with When/How/Input/Impact per tool
  AGENTS.md → colleague relationships, when to @mention

DYNAMIC DIRECTIVES (change per task/cycle, from context system):
  context/task-context.md → current stage, readiness, verbatim, contributions received
  context/fleet-context.md → fleet state, messages, role-specific data, events
  Methodology protocol text → stage-specific instructions (from methodology.yaml)
  Standing orders → autonomous authority programs (from AGENTS.md or dedicated file)

STRUCTURAL DIRECTIVES (enforced by system, not by text):
  Stage gating → fleet_commit BLOCKED outside work stage (MCP layer)
  Hooks → commit format validation, security patterns (PreToolUse)
  Contribution gates → brain blocks dispatch without required contributions
  Phase standards → completion blocked if standards not met
  Budget gates → expensive operations blocked when over budget
  Tool restrictions → CRONs can restrict available tools (--tools flag)

SKILL DIRECTIVES (loaded when skill is invoked):
  /brainstorming → "Explore the problem space with Socratic questioning"
  /test-driven-development → "Write the failing test FIRST, then implement"
  /writing-plans → "Break into bite-sized tasks with dependencies"
  /verification-before-completion → "Run verification commands BEFORE claiming done"
```

---

## The Input/Output Clarity Principle

Every capability an agent can use should have clear:

1. **WHEN** — what conditions make this the right choice
2. **HOW** — what input it expects, what format
3. **WHAT** — what it does (the tree of operations)
4. **IMPACT** — what changes in the fleet when it runs
5. **OUTPUT** — what the agent gets back

This applies to:
- Fleet MCP tools (documented in tool-chains.yaml → TOOLS.md)
- Role-specific group calls (documented in TOOLS.md role-specific section)
- Skills (documented in SKILL.md instructions)
- Sub-agents (documented in sub-agent description + TOOLS.md)
- CRONs (documented in standing orders)
- Hooks (documented in settings.json config — but impact should be in TOOLS.md)

The TOOLS.md generation pipeline (Chunk 8) must produce this clarity for EVERY capability. Not a flat list — a structured reference where the agent can find: "I need to do X → use capability Y → give it input Z → it will do W → I get back V."

---

## What's Missing That Needs Building

### Missing Directive Infrastructure

| What | Where It Goes | Status |
|------|-------------|--------|
| Stage-methodology directives per role | config/methodology.yaml protocol text + CLAUDE.md stage protocol | Protocol text EXISTS in methodology.yaml. Role-specific adaptations DON'T EXIST. |
| Contribution directives per role | CLAUDE.md contribution model + skill instructions | CLAUDE.md templates EXIST with basic contribution model. Detailed contribution skills DON'T EXIST. |
| Tool usage directives with impact | config/tool-chains.yaml + TOOLS.md | tool-chains.yaml EXISTS but ASPIRATIONAL. TOOLS.md generation doesn't include impact. |
| Strategic feature directives | CLAUDE.md + skill instructions | NOT DEFINED anywhere. When to use extended thinking, sub-agents, adversarial review. |
| Group call directives per role | TOOLS.md role-specific section | Group calls DON'T EXIST yet. Directives can't exist without the capabilities. |
| CRON directives (standing orders) | AGENTS.md or dedicated file | NONE EXIST. |
| Hook directive documentation | TOOLS.md hooks section | NOT IN TOOLS.md. Agents don't know what hooks enforce. |
| Input/output clarity per capability | TOOLS.md comprehensive format | Current TOOLS.md lacks impact/output documentation. |

### The Directive Creation Order

Directives can't exist without the capabilities they direct. The order:

1. Build the capability (tool, group call, skill, CRON, sub-agent, hook)
2. Define the directive (when, how, input, impact, output)
3. Place the directive in the right injection point (CLAUDE.md, TOOLS.md, skill, standing order)
4. Generate TOOLS.md that surfaces the directive to the agent

This means: directive creation is PART OF each capability creation, not a separate step. When building a role-specific group call like sec_dependency_audit, the directive (when to use it, what input, what impact) is designed AS PART of the group call, then documented in TOOLS.md.

---

## Connection to Autocomplete Chain Engineering

The autocomplete chain is the structural prevention mechanism (anti-corruption Line 1). It works because the agent's context is arranged so the CORRECT action is the natural continuation.

Directives are HOW the autocomplete chain communicates capability usage:
- Identity establishes WHO → naturally selects role-appropriate capabilities
- Values establish WHY → naturally motivates correct usage
- Rules establish CONSTRAINTS → structurally prevents wrong usage
- TOOLS.md establishes WHAT → provides the reference for correct capability selection
- Context establishes SITUATION → narrows to what's appropriate NOW
- HEARTBEAT.md establishes ACTION → points to the specific capability to use

Without clear directives, the autocomplete chain is weak — the agent has capabilities but doesn't know when to use them. With clear directives at every level, the correct action IS the natural continuation.

---

## Connection to Immune System

The immune system (doctor + teaching) DETECTS when directives are violated:

| Directive Violation | Detection | Response |
|-------------------|-----------|----------|
| Used fleet_commit outside work stage | MCP stage gate → protocol_violation event | Tool returns error. Doctor detects, may teach. |
| Skipped contribution consumption | Brain checks contributions before dispatch | Dispatch blocked until contributions received |
| Used wrong tool for stage | Doctor behavioral analysis | Teaching lesson: "You're in analysis stage, the protocol allows..." |
| Didn't follow skill workflow | Standards check on artifact completeness | Readiness doesn't advance, flags to PM |
| Violated standing order scope | (Not yet implemented) | Would need hook-based enforcement |
| Overrode colleague's input | Trail shows contribution ignored | Fleet-ops catches during review |

Structural enforcement (hooks, gates) catches violations BEFORE they happen.
Detection (doctor) catches violations AFTER they happen.
Teaching corrects the agent's behavior for future sessions.
