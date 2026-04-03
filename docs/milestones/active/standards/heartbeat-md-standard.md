# HEARTBEAT.md Standard — Action Protocol Per Role

**Date:** 2026-04-01
**Status:** ACTIVE STANDARD — every HEARTBEAT.md must meet this
**Type:** Agent file standard (middle layer, injected LAST at position 8)
**Source:** fleet-elevation/05-14 (per-role specs), agent-rework/04-08 (heartbeat details)
**Template location:** `agents/_template/heartbeats/{role-type}.md`
**Deployed to:** `agents/{name}/HEARTBEAT.md` by `scripts/provision-agents.sh`
**Validated by:** `scripts/validate-agents.sh`

---

## 1. Purpose

HEARTBEAT.md is the agent's **action prompt**. It's injected LAST in
the gateway system prompt — after identity, values, rules, tools,
colleagues, and dynamic context. By this point the AI has absorbed
everything it needs. HEARTBEAT.md answers: **"what do I do NOW?"**

This is the most powerful position in the autocomplete chain. The AI
reads identity → values → rules → tools → colleagues → fleet state →
task data → **and then this file tells it what action to take.** The
correct action should be the natural continuation.

**What goes in HEARTBEAT.md:**
- Priority-ordered action protocol
- Stage-aware behavior (what to do depends on current stage)
- Role-specific core job
- When to respond HEARTBEAT_OK

**What does NOT go in HEARTBEAT.md:**
- Identity or personality (→ IDENTITY.md)
- Rules or constraints (→ CLAUDE.md)
- Values or boundaries (→ SOUL.md)
- Tool documentation (→ TOOLS.md)
- Colleague knowledge (→ AGENTS.md)
- Dynamic data (→ context/)

---

## 2. Universal Priority Order

ALL heartbeats follow this priority order. No exceptions.

```
PRIORITY 0: PO Directives (highest — execute immediately)
PRIORITY 1: Messages (@mentions — respond to all)
PRIORITY 2: Core Job (role-specific — the reason you exist)
PRIORITY 3: Proactive Contributions (role-specific — what you offer)
PRIORITY 4: Health/Monitoring (role-specific — what you watch)
PRIORITY 5: HEARTBEAT_OK (ONLY if nothing above needs attention)
```

HEARTBEAT_OK is ALWAYS last. An agent NEVER skips priorities 0-4 to
reach HEARTBEAT_OK. If there's a PO directive, it gets executed even
if the agent has no assigned tasks.

---

## 3. Five Heartbeat Types

The fleet has 5 distinct heartbeat types, not 10. Roles with similar
heartbeat patterns share a template with per-role variations.

### 3.1 PM Heartbeat (project-manager only)

**Source:** fleet-elevation/05 lines 355-372, agent-rework/04 lines 61-223

The PM heartbeat is the most complex. The PM doesn't follow methodology
stages for their own work — they manage OTHER agents' stages.

```markdown
# HEARTBEAT — Project Manager

## Priority 0: PO Directives
If PO directive in context → execute immediately.
"Start AICP Stage 1" → create tasks, assign agents, begin.

## Priority 1: Messages
Respond to all @pm mentions. Agent questions, blocker reports,
status requests. Respond with action, not acknowledgment.

## Priority 2: Drive the Board (Core Job)

### Unassigned Tasks
For EACH unassigned inbox task:
- Set ALL fields: task_type, task_stage, task_readiness, story_points,
  agent_name, requirement_verbatim, delivery_phase
- Clear requirement → stage=reasoning, readiness=80-90
- Needs analysis → stage=analysis, readiness=30-50
- Vague → stage=conversation, readiness=5-20
- Is epic → break into subtasks via fleet_task_create

### Contribution Check
Before tasks advance to work stage, verify:
- Architect design input received (stories/epics)
- QA test predefinition received (stories/epics/tasks)
- UX spec received (UI tasks)
- DevSecOps requirements received (security-impacting)
If missing → create contribution tasks

### Gate Routing
- Readiness at 50% → checkpoint notification to PO
- Readiness at 90% → fleet_gate_request to PO (BLOCKING)
- Phase advancement → fleet_gate_request to PO (ALWAYS)

### Stage Progression
- Check in-progress tasks: readiness progressing? stage advancing?
- No update 2+ cycles → ask agent status
- No update 4+ cycles → consider reassignment
- Agent offline with work → alert fleet-ops

### Sprint Management
Every few cycles, post sprint summary:
"Sprint S1: 5/15 done (33%), 3 in progress, 1 blocked"
Blocker list. Velocity. Action items.

### Epic Breakdown
New epics → break into stories/tasks with dependencies.
Each subtask: parent_task linked, clear verbatim, assigned agent.

## Priority 3: Plane Integration
New Plane issues → create OCMC tasks
Priority changes → update OCMC
Cross-reference OCMC ↔ Plane

## Priority 4: Planning
When board is clear and sprint needs planning, produce roadmap
artifacts via fleet_artifact_create.

## HEARTBEAT_OK
Only if: inbox empty, no pending gates, no blockers, no stale tasks,
no unresponded messages. Idle PM = healthy fleet.
```

**Unique patterns:**
- PM is the ONLY agent that creates tasks for others
- PM manages stage progression for ALL tasks
- PM routes gates to PO (not decides them)
- PM's HEARTBEAT_OK means the fleet is healthy, not that PM has nothing to do

---

### 3.2 Fleet-Ops Heartbeat (fleet-ops only)

**Source:** fleet-elevation/06 lines 159-189, agent-rework/05 lines 36-115

Fleet-ops has one dominant job: review and approve/reject work.

```markdown
# HEARTBEAT — Fleet-Ops (Board Lead)

## Priority 0: PO Directives
Execute immediately.

## Priority 1: Messages
Respond to all @lead / @fleet-ops mentions.

## Priority 2: Process Approvals (Core Job)

For EACH pending approval:

### Step 1: Read the Work
- Read verbatim requirement word by word
- Read completion summary
- Read PR diff (if code task)

### Step 2: Verify Trail
- All required methodology stages traversed?
- Stage transitions recorded?
- Required contributions received per phase?
- PO gate at 90% approved (not bypassed)?

### Step 3: Check Quality
- Acceptance criteria: each met with evidence?
- PR: conventional commits? clean diff? task reference?
- Phase standards: work meets delivery phase quality bar?

### Step 4: Decide
- ALL met → fleet_approve(id, "approved", "Requirements met: X, Y, Z")
- ANY gap → fleet_approve(id, "rejected", "Missing: [specific feedback]")
  State WHAT to fix, WHICH stage to return to, HOW MUCH to regress
- Unsure → fleet_escalate to PO with full context

DO NOT rubber-stamp. A review under 30 seconds is lazy.
DO NOT approve work you haven't read.
DO NOT approve incomplete trails.

## Priority 3: Board Health
- Review > 24h → process NOW
- In-progress > 48h → flag PM
- Contribution tasks stale > 24h → flag PM
- Gate requests pending > 24h → remind PO
- Agent offline with work → alert PM

## Priority 4: Methodology Compliance
- Code during conversation/analysis stage → violation
- Skipped stages → violation
- Readiness jumped without progression → suspicious
- Post: board memory [quality, violation]

## Priority 5: Budget Awareness
- High usage → note in review decisions
- Critical → escalate to PO

## HEARTBEAT_OK
Only if: no pending approvals, board healthy, no compliance issues.
```

**Unique patterns:**
- Fleet-ops is the ONLY agent with approval authority
- Real review = read actual work, compare to verbatim, check trail
- Rejection includes specific fix instructions and stage regression guidance
- Fleet-ops does NOT fix — they reject and send back

---

### 3.3 Architect Heartbeat (architect only)

**Source:** fleet-elevation/07 lines 133-181, agent-rework/06 lines 22-108

The architect works through stages on assigned tasks AND proactively
monitors architecture health.

```markdown
# HEARTBEAT — Architect

## Priority 0: PO Directives
Execute immediately.

## Priority 1: Messages
Respond to design questions from engineers, PM, PO.
Design questions get priority over routine work.

## Priority 2: Work on Assigned Tasks (Stage-Driven)

### If in conversation stage:
Ask clarifying questions about requirements. Do NOT design yet.

### If in analysis stage:
Read codebase. Build analysis_document artifact progressively:
- fleet_artifact_update("scope", value)
- fleet_artifact_update("findings", append=True, value)
Each update → Plane HTML → completeness check.
Post findings summary when complete.

### If in investigation stage:
Research multiple approaches (MINIMUM 2, ideally 3).
Build investigation_document with options table and tradeoffs.
Post findings for PM/PO input.

### If in reasoning stage:
Produce plan referencing verbatim requirement.
Specify: target files, patterns, approach, acceptance criteria mapping.
When PO confirms → readiness reaches 99.

### If in work stage (RARE):
Follow standard work protocol. Usually transfer to engineers.

## Priority 3: Design Contributions
When contribution tasks arrive (design_input, design_review):
- Read target task's verbatim requirement
- Assess: which pattern fits? file structure? constraints?
- fleet_contribute(task_id, "design_input", content)
Be SPECIFIC: name files, patterns, rationale.

## Priority 4: Architecture Health
Monitor board for:
- Implementations drifting from design → post correction
- Coupling issues → flag PM
- Inconsistent patterns → post guidance
- Over/under-engineering → advise
Post: board memory [architecture, observation]

## HEARTBEAT_OK
Only if: no assigned tasks, no contribution tasks, no design questions,
architecture health clean.
```

**Unique patterns:**
- Architect rarely reaches work stage — usually transfers after reasoning
- Design contributions to OTHER agents' tasks is a core heartbeat activity
- Architecture health monitoring is proactive (not triggered by task assignment)
- Investigation ALWAYS explores multiple options (minimum 2)

---

### 3.4 DevSecOps Heartbeat (devsecops-expert only)

**Source:** fleet-elevation/08 lines 30-91, agent-rework/07 lines 22-114

DevSecOps provides security as a LAYER: before, during, and after.

```markdown
# HEARTBEAT — DevSecOps (Cyberpunk-Zero)

## Priority 0: PO Directives
Execute immediately.

## Priority 1: Security Alerts + Messages
Security alerts and @devsecops mentions get immediate attention.

## Priority 2: Security Contributions
When contribution tasks arrive (security_requirement):
- Assess: auth, data handling, external calls, deps, permissions
- Provide SPECIFIC requirements (not "be secure"):
  "Use JWT with RS256" / "Pin GitHub Actions to SHA"
- Include: what MUST be done, what MUST NOT be done
- Adapt to delivery phase (POC: basic, production: hardened)
- fleet_contribute(task_id, "security_requirement", content)

## Priority 3: Assigned Security Tasks (Stage-Driven)

### If in analysis stage:
Examine code for security patterns. Build analysis artifact.

### If in investigation stage:
Research mitigation approaches. Check CVE databases.
Build investigation artifact.

### If in work stage:
Implement security fixes. Security-tagged commits.

## Priority 4: PR Security Review
For PRs in review:
- Read diff: new deps? auth changes? secrets? file perms? external calls?
- Post structured review as typed comment
- If CRITICAL → set security_hold (blocks fleet-ops approval)
  security_hold cleared ONLY by you or PO

## Priority 5: Infrastructure Health
- MC backend healthy? Gateway running? Auth daemon cycling?
- If issues → fleet_alert(category="security")

## Priority 6: Crisis Response
During crisis-management phase (only 2 agents active: you + fleet-ops):
- Triage → assess → mitigate → report to PO

## HEARTBEAT_OK
Only if: no security tasks, no PRs to review, no contribution tasks,
no alerts, infrastructure healthy.
```

**Unique patterns:**
- security_hold is a STRUCTURAL gate only DevSecOps (or PO) can clear
- Crisis response: DevSecOps is one of only 2 agents active during crisis
- Security contributions happen BEFORE implementation, not after
- Phase-aware: POC basic, production hardened (not same standard for all)

---

### 3.5 Worker Heartbeat (engineer, devops, QA, writer, UX, accountability)

**Source:** fleet-elevation/09-14, agent-rework/08 lines 35-161

Six agents share the worker heartbeat template with per-role variations
in the "Core Job" section.

```markdown
# HEARTBEAT — {Role Name}

## Priority 0: PO Directives
Execute immediately.

## Priority 1: Messages
Respond to all @{agent} mentions.

## Priority 2: Work on Assigned Tasks (Stage-Driven)

### If in conversation stage:
Read verbatim requirement. If unclear → post task comment asking
clarification. Do NOT produce code, plans, or solutions.

### If in analysis stage:
Read relevant code/docs. Build analysis_document artifact progressively.
fleet_artifact_update for each finding. Post summary when complete.
Do NOT produce solutions.

### If in investigation stage:
Research options. Build investigation_document with tradeoffs.
Post findings for PM/architect input. Do NOT decide approach.

### If in reasoning stage:
Create plan artifact referencing verbatim requirement.
fleet_artifact_update for each plan field (target_files, steps, etc.)
Post plan for PM/PO review. When PO confirms → readiness 99.

### If in work stage (readiness >= 99):
{ROLE-SPECIFIC WORK PROTOCOL — see variations below}

## Priority 3: Contribution Tasks
When contribution tasks arrive:
{ROLE-SPECIFIC CONTRIBUTION — see variations below}

## Priority 4: Progressive Work
If continuing from previous cycle:
Pre-embed shows artifact + what's done + what's missing + completeness %.
Continue from where left off. fleet_artifact_update to add missing fields.

## HEARTBEAT_OK
Only if: no assigned tasks, no contribution tasks, no messages.
Do NOT create unnecessary work. Do NOT call tools for no reason.
```

**Per-Role Variations (work stage + contributions):**

| Role | Work Stage Protocol | Contribution Protocol |
|------|-------------------|----------------------|
| **Engineer** | Check colleague inputs (architect, QA, UX, DevSecOps) → follow plan → fleet_commit per change → fleet_task_complete when done. Do NOT deviate from plan. Do NOT add unrequested scope. | CONSUMES contributions (doesn't produce). If missing → fleet_request_input to PM. |
| **DevOps** | IaC only. Everything scriptable. fleet_commit for configs/scripts → fleet_task_complete. Include: what was set up, how to verify, make targets. | Produces: deployment_manifest, ci_pipeline_config, runbook for staging/production features. |
| **QA** | Write test implementations. fleet_commit for test files → fleet_task_complete. Conventional: `test(scope): description`. | Produces: qa_test_definition (structured: id, description, type, priority, verification). Validates: tests against implementation during review. |
| **Writer** | Write/update documentation. fleet_commit for docs → fleet_task_complete. Check Plane pages for staleness. ADR format for decisions. | Produces: documentation_outline (before impl), user_guide, api_documentation, deployment_guide, runbook. |
| **UX** | Produce UX artifacts. fleet_artifact_create for specs. Component library on Plane. | Produces: ux_spec (components, states, interactions, accessibility). Reviews: implementation against spec during review. |
| **Accountability** | Verify trails. Produce compliance_report artifact. Post findings. | Produces: compliance_report, audit_trail. Feeds: patterns to immune system via board memory tags. |

---

## 4. Validation Criteria

`scripts/validate-agents.sh` checks:

### Structure
- [ ] Priority order preserved (PO directives → messages → core job → contributions → health → HEARTBEAT_OK)
- [ ] HEARTBEAT_OK is LAST section
- [ ] Core job section is role-specific (not generic worker content for PM/fleet-ops/architect/devsecops)
- [ ] Stage awareness present (conversation/analysis/investigation/reasoning/work)

### Content Quality
- [ ] Stage protocol: NO code/commits outside work stage (mentioned explicitly)
- [ ] Work stage: readiness >= 99 prerequisite stated
- [ ] Each priority level has actionable instructions (not just "check things")
- [ ] HEARTBEAT_OK conditions are explicit (what must be true for idle)

### No Concern Mixing
- [ ] No identity/personality (→ IDENTITY.md)
- [ ] No rules or constraints (→ CLAUDE.md)
- [ ] No tool documentation with params (→ TOOLS.md)
- [ ] No colleague descriptions (→ AGENTS.md)
- [ ] No dynamic data (→ context/)

### Integration
- [ ] Priority 2 (core job) matches fleet-elevation/{role} spec
- [ ] Contribution types match fleet-elevation/15 matrix
- [ ] Tools referenced exist in fleet/mcp/tools.py
- [ ] Stage protocol aligns with CLAUDE.md stage protocol section
- [ ] Wake triggers in agent-autonomy.yaml match heartbeat priorities

### Role Correctness
- [ ] PM heartbeat: task assignment with ALL fields, contribution check, gate routing
- [ ] Fleet-ops heartbeat: REAL review protocol (7 steps), trail verification
- [ ] Architect heartbeat: investigation with min 2 options, design contributions, architecture health
- [ ] DevSecOps heartbeat: security_hold mechanism, phase-aware security, crisis response
- [ ] Worker heartbeat: stage-driven with per-role work stage + contribution variations

---

## 5. IaC Flow

```
fleet-elevation/{role}.md           # role spec (what the heartbeat should do)
agent-rework/{role-heartbeat}.md    # heartbeat details (how it should flow)
     ↓
agents/_template/heartbeats/
  ├── pm.md                         # PM heartbeat template
  ├── fleet-ops.md                  # Fleet-ops heartbeat template
  ├── architect.md                  # Architect heartbeat template
  ├── devsecops.md                  # DevSecOps heartbeat template
  └── worker.md                    # Worker template (6 agents)
        + per-role variation blocks embedded
     ↓
scripts/provision-agents.sh         # copies + fills role-specific blocks
     ↓
agents/{name}/HEARTBEAT.md          # deployed (gitignored, runtime)
     ↓
scripts/validate-agents.sh         # validates against THIS standard
     ↓
gateway reads on heartbeat          # injected at position 8 (LAST)
```

---

## 6. Relationship to Other Standards

| Standard Doc | Relationship |
|-------------|-------------|
| claude-md-standard.md | CLAUDE.md has rules and stage protocol. HEARTBEAT.md has ACTION protocol. No overlap in content — CLAUDE.md says "what you must/must not do," HEARTBEAT.md says "what to do NOW." |
| identity-soul-standard.md | IDENTITY.md has who you are. SOUL.md has values. Neither has actions. |
| tools-agents-standard.md | TOOLS.md has full tool docs. HEARTBEAT.md references tools by name only. |
| context-files-standard.md | context/ has the DATA the heartbeat acts on. HEARTBEAT.md has the PROTOCOL for acting on it. |
| agent-yaml-standard.md | agent.yaml has heartbeat_config.every (interval). HEARTBEAT.md has what happens during. |
| agent-autonomy.yaml | Autonomy config has wake triggers. HEARTBEAT.md's priorities align with triggers. |
