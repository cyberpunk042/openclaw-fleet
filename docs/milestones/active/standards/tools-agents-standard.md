# TOOLS.md + AGENTS.md Standard — Capabilities and Synergy

**Date:** 2026-04-01
**Status:** ACTIVE STANDARD
**Type:** Agent file standard (middle layer)
**Source:** fleet-elevation/02 (architecture), fleet-elevation/15 (synergy), fleet-elevation/24 (tool call trees)
**Injection:** TOOLS.md at position 4, AGENTS.md at position 5

---

## PART 1: TOOLS.md — Chain-Aware Tool Reference

### 1.1 Purpose

TOOLS.md tells the agent what it CAN do and what HAPPENS when it acts.
Not a list of API endpoints — a chain-aware reference that shows the
CONSEQUENCES of each tool call.

When an agent calls fleet_task_complete, 12+ operations fire automatically.
The agent needs to know this — not to call them manually, but to understand
that ONE call does EVERYTHING. This is the group call concept.

### 1.2 Required Format Per Tool

```markdown
### fleet_{tool_name}

**What:** {primary action — one line}
**When:** {stage, conditions — when this tool is appropriate}
**Chain:** {what fires automatically after the call}
**Input:** {key parameters}
**You do NOT need to:** {what the chain handles — prevents manual duplication}
```

### 1.3 Per-Role Tool Sets

From config/agent-tooling.yaml and fleet-elevation/24:

#### PM Tools
```markdown
### fleet_task_create
**What:** Create a new task (subtask, contribution task, or independent)
**When:** Breaking epics, creating contribution tasks, assigning new work
**Chain:** task → inbox → event → IRC #fleet → board memory
**Input:** title, description, agent_name, task_type, parent_task, custom_fields
**You do NOT need to:** notify the agent (heartbeat picks it up), update sprint

### fleet_chat
**What:** Post message to board memory with optional @mention
**When:** Communicating with agents, posting updates, asking questions
**Chain:** board memory (tagged mention:{agent}) → IRC #fleet → agent sees in MESSAGES
**Input:** message, mention (optional agent name)
**You do NOT need to:** route to IRC (automatic), route to agent (automatic)

### fleet_gate_request
**What:** Route gate decision to PO (readiness 90%, phase advancement)
**When:** Task readiness reaches 90%, phase needs to advance
**Chain:** ntfy to PO → IRC #gates → board memory [gate, po-required]
**Input:** task_id, gate_type, summary for PO
**You do NOT need to:** notify PO separately (ntfy handles it)

### fleet_escalate
**What:** Escalate blocker or decision to PO/senior
**When:** Blocked, need PO input, unclear requirement
**Chain:** ntfy (urgent) → IRC #alerts → board memory [escalation]
**Input:** title, details, severity
```

#### Fleet-Ops Tools
```markdown
### fleet_approve
**What:** Approve or reject a review task
**When:** After completing REAL review (reading work, checking trail)
**Chain (approve):** task → done → trail → sprint progress → parent eval → IRC #reviews
**Chain (reject):** task → in_progress → readiness regressed → agent notified → trail
**Input:** approval_id, decision ("approved"/"rejected"), comment (specifics)
**You do NOT need to:** create fix tasks (auto if rejected), notify agent (auto)

### fleet_alert
**What:** Post alert to IRC channel
**When:** Quality issues, compliance gaps, budget concerns
**Chain:** IRC #alerts → board memory → ntfy if high/critical
**Input:** category, severity, details
```

#### Worker Tools (shared across engineer, devops, QA, writer, UX)
```markdown
### fleet_read_context
**What:** Read full task context including contributions
**When:** Starting work, checking inputs, reviewing task state
**Chain:** none (read-only)
**Input:** (none — reads context for current agent)

### fleet_task_accept
**What:** Accept task with a plan
**When:** Confirming approach before starting work stage
**Chain:** event → task marked accepted → trail
**Input:** plan (your implementation approach)

### fleet_commit
**What:** Commit files with conventional message
**When:** Work stage ONLY. Each logical change gets one commit.
**Chain:** git add + commit → event → IRC → methodology check → trail
**Input:** files, message (format: type(scope): description [task-id])
**BLOCKED outside work stage** — returns error + protocol_violation event

### fleet_task_complete
**What:** Complete task — triggers FULL review chain
**When:** Work stage. All acceptance criteria met.
**Chain:** git push → create PR → MC update → approval object → IRC #reviews → ntfy → Plane sync → labor stamp → trail → parent evaluation
**Input:** summary
**BLOCKED outside work stage** — returns error + protocol_violation event
**You do NOT need to:** push code (auto), create PR (auto), notify reviewers (auto), update Plane (auto)

### fleet_artifact_create / fleet_artifact_update
**What:** Create or update structured artifacts (analysis, investigation, plan, etc.)
**When:** Any stage — building progressive artifacts
**Chain:** object created → Plane HTML rendered → completeness check → readiness suggestion → event
**Input:** type, title (create) / field, value, append (update)

### fleet_contribute
**What:** Post contribution to another agent's task
**When:** Contribution task assigned — providing design/test/security/UX/doc input
**Chain:** contribution stored → propagated to target task → target sees in context → event → trail → check completeness → if all received → notify PM
**Input:** task_id, contribution_type, content
```

### 1.4 Validation Criteria

- [ ] Every tool the agent uses is documented (per config/agent-tooling.yaml)
- [ ] Every tool entry has all 5 fields: What, When, Chain, Input, "You do NOT need to"
- [ ] Tool names match fleet/mcp/tools.py exactly
- [ ] Chain descriptions are accurate (match fleet-elevation/24 call trees)
- [ ] Stage restrictions documented (fleet_commit/fleet_task_complete: work only)
- [ ] No tools documented that this role doesn't use
- [ ] No concern mixing (no rules, no identity, no dynamic data)

### 1.5 IaC

```
fleet/mcp/tools.py                    # source of truth for tool names
fleet-elevation/24                     # call tree catalog (chains)
config/agent-tooling.yaml             # per-role tool assignments
     ↓
scripts/generate-tools-md.sh          # generates per-role TOOLS.md
     ↓
agents/_template/TOOLS.md/{role}.md   # role-specific tool docs
     ↓
scripts/provision-agents.sh           # copies to agent dir
     ↓
agents/{name}/TOOLS.md                # deployed (gitignored, runtime)
```

**TOOLS.md is GENERATED, not hand-written.** The script reads tool
definitions, call trees, and role assignments to produce accurate docs.
This ensures TOOLS.md never drifts from the actual tool implementations.

---

## PART 2: AGENTS.md — Fleet Awareness and Synergy

### 2.1 Purpose

AGENTS.md tells the agent WHO their colleagues are and HOW to work
with them. Injected at position 5 — after rules and tools, before
dynamic context. The agent knows its identity, values, rules, and
capabilities before learning about the team.

### 2.2 Required Format Per Colleague

```markdown
### {display_name} — {role}

**Contributes to me:** {what they provide + when}
**I contribute to them:** {what I provide + when}
**When to @mention:** {specific conditions for reaching out}
```

### 2.3 Contribution Matrix (from fleet-elevation/15)

| Agent | Receives From | Provides To |
|-------|--------------|-------------|
| PM | (receives questions, status, escalations from all) | Task assignments, sprint direction, blocker resolution to all |
| Fleet-Ops | (receives review tasks from all) | Approval/rejection feedback to original agent |
| Architect | PM (design tasks), PO (complexity requests) | design_input to engineer, devops |
| DevSecOps | PM (security tasks), brain (PR review) | security_requirement to engineer, devops |
| Engineer | Architect (design), QA (tests), UX (specs), DevSecOps (security) | Code (reviewed by fleet-ops) |
| DevOps | Architect (infra design) | deployment_manifest to engineer |
| QA | PM (test tasks) | qa_test_definition to engineer |
| Writer | PM (doc tasks), brain (completion chain) | documentation_outline to engineer |
| UX | PM (UX tasks) | ux_spec to engineer |
| Accountability | Brain (trail data) | compliance_report, patterns to immune system |

### 2.4 Example: Engineer's AGENTS.md

```markdown
# Fleet Awareness — Software Engineer

### Architect Alpha — Design Authority
**Contributes to me:** Design input before I implement (approach, files,
  patterns, constraints). REQUIRED for stories and epics.
**I contribute to them:** (rarely — my implementation validates their design)
**When to @mention:** When design input is unclear, when I discover
  architectural implications during implementation.

### QA Engineer Alpha — Test Authority
**Contributes to me:** Predefined test criteria before I implement.
  Each criterion is a REQUIREMENT, not a suggestion.
**I contribute to them:** My implementation for them to validate.
**When to @mention:** When test criteria are ambiguous or untestable.

### DevSecOps Alpha (Cyberpunk-Zero) — Security Layer
**Contributes to me:** Security requirements before I implement.
  What I MUST and MUST NOT do security-wise.
**I contribute to them:** My code for security review.
**When to @mention:** When I encounter security-sensitive decisions.

### UX Designer Alpha — UX Authority
**Contributes to me:** UX specs for UI work (components, states,
  interactions, accessibility).
**I contribute to them:** My implementation for UX validation.
**When to @mention:** When spec is unclear or I need interaction guidance.

### Project Manager Alpha — Board Driver
**Contributes to me:** Task assignments with clear requirements.
**I contribute to them:** Progress updates, completion, blocker reports.
**When to @mention:** When blocked, when scope unclear, when done early.

### Fleet-Ops Alpha — Quality Guardian
**Contributes to me:** Approval or rejection with specifics.
**I contribute to them:** My completed work for review.
**When to @mention:** (rarely — fleet-ops finds me through review queue)

### DevOps Alpha — Infrastructure Owner
**Contributes to me:** Deployment manifests for staging/production.
**I contribute to them:** Infrastructure requirements from my implementation.
**When to @mention:** When I need infra changes for my task.

### Technical Writer Alpha — Documentation
**Contributes to me:** Documentation outlines (what to document).
**I contribute to them:** API docs, setup instructions from my implementation.
**When to @mention:** When my feature needs user documentation.

### Accountability Generator Alpha — Process Verifier
**Contributes to me:** (rarely — reports compliance, doesn't contribute to work)
**I contribute to them:** My work trail (automatic via tool chains).
**When to @mention:** (never — accountability reads trails, doesn't need input)
```

### 2.5 Validation Criteria

- [ ] All 9 other agents listed (10-agent fleet, each knows the other 9)
- [ ] Each colleague entry has: "Contributes to me," "I contribute to them," "When to @mention"
- [ ] Contribution relationships match fleet-elevation/15 synergy matrix EXACTLY
- [ ] Bidirectional: if A says "contributes design_input to B," B says "receives design_input from A"
- [ ] @mention guidance is specific (not "when needed" — specify conditions)
- [ ] Display names match agent.yaml display_name values
- [ ] No rules (→ CLAUDE.md), no identity (→ IDENTITY.md), no tools (→ TOOLS.md)

### 2.6 IaC

```
fleet-elevation/15                     # synergy matrix (source of truth)
config/agent-identities.yaml          # display names, roles
     ↓
scripts/generate-agents-md.sh         # generates per-role AGENTS.md
     ↓
agents/_template/AGENTS.md/{role}.md  # role-specific colleague docs
     ↓
scripts/provision-agents.sh           # copies to agent dir
     ↓
agents/{name}/AGENTS.md               # deployed (gitignored, runtime)
```

**AGENTS.md is GENERATED from the synergy matrix.** This ensures
bidirectional consistency — when the matrix changes, ALL agents'
AGENTS.md files update together.

---

## 3. Relationship to Other Standards

| Standard Doc | Relationship |
|-------------|-------------|
| claude-md-standard.md | CLAUDE.md has tool CHAINS (brief). TOOLS.md has full tool DOCUMENTATION. |
| claude-md-standard.md | CLAUDE.md has contribution MODEL. AGENTS.md has contribution RELATIONSHIPS. |
| heartbeat-md-standard.md | HEARTBEAT.md references tools by name. TOOLS.md has the full docs. |
| identity-soul-standard.md | IDENTITY.md has "place in fleet." AGENTS.md has detailed colleague knowledge. |
| agent-yaml-standard.md | agent.yaml has roles.contributes_to. AGENTS.md details those relationships. |
| config/agent-tooling.yaml | Tooling config defines which tools each role gets. TOOLS.md documents them. |
