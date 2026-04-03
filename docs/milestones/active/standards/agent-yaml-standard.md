# agent.yaml Standard — Gateway Configuration and Fleet Identity

**Date:** 2026-04-01
**Status:** ACTIVE STANDARD — every agent.yaml must meet this
**Type:** Agent file standard (inner layer, read by gateway for session creation)
**Source:** fleet-elevation/02 (architecture), fleet-elevation/16 (multi-fleet identity)
**Template location:** `agents/_template/agent.yaml.template`
**Deployed to:** `agents/{name}/agent.yaml` by `scripts/provision-agents.sh`
**Validated by:** `scripts/validate-agents.sh`

---

## 1. Purpose

agent.yaml is the agent's **gateway configuration and fleet identity**.
The gateway reads this file to:
- Create and configure agent sessions
- Build the system prompt (knows which files to inject)
- Set heartbeat intervals
- Choose default model and mode

The orchestrator reads this file to:
- Identify agent roles for dispatch decisions
- Know contribution relationships for synergy
- Apply role-specific lifecycle thresholds

**This is the ONLY file both the gateway AND the orchestrator read.**
It's the bridge between the two systems.

---

## 2. Required Fields

### Complete Schema

```yaml
# Identity — who this agent is
name: "alpha-{role}"                   # Machine name (fleet-role format)
display_name: "{Role} Alpha"           # Human-readable name
fleet_id: "alpha"                      # Fleet identifier
fleet_number: 1                        # Fleet number (1 = alpha, 2 = bravo)
username: "alpha-{role}"               # Agent username for IRC/comms

# Gateway — how the gateway treats this agent
type: "agent"                          # Always "agent"
mode: "heartbeat"                      # Always "heartbeat" (gateway-driven cycles)
backend: "claude"                      # Default backend ("claude" or "localai")
model: "opus"                          # Default model (overridable by brain)

# Mission — what this agent does
mission: "{one-line mission statement}" # Brief, specific, role-defining
capabilities:                           # 4-8 specific capabilities
  - "capability_1"
  - "capability_2"
  - "capability_3"
  - "capability_4"

# Roles — how this agent connects to others
roles:
  primary: "{role-name}"               # Matches fleet role names
  contributes_to:                      # Who this agent provides input to
    - "role-name-1"
    - "role-name-2"

# Heartbeat — timing
heartbeat_config:
  every: "{interval}"                  # e.g., "10m", "30m", "1h"
```

### Per-Role Values

| Role | name | model | mission | capabilities (min 4) | contributes_to | heartbeat |
|------|------|-------|---------|---------------------|----------------|-----------|
| PM | alpha-project-manager | opus | "Board driver — task assignment, sprint management, PO routing" | task_assignment, sprint_management, epic_breakdown, stakeholder_communication, blocker_resolution | software-engineer, devops, qa-engineer, architect, ux-designer, technical-writer | 10m |
| Fleet-Ops | alpha-fleet-ops | opus | "Quality guardian — work review, methodology compliance, approval authority" | work_review, methodology_compliance, approval_decisions, board_health, budget_awareness | (none — review IS the contribution) | 10m |
| Architect | alpha-architect | opus | "Design authority — architecture, patterns, complexity assessment" | architecture_design, complexity_assessment, design_review, pattern_selection, investigation | software-engineer, devops | 10m |
| DevSecOps | alpha-devsecops-expert | opus | "Security layer — requirements before, review during, validation after" | security_assessment, vulnerability_scanning, dependency_auditing, security_review, crisis_response | software-engineer, devops | 15m |
| Engineer | alpha-software-engineer | sonnet | "Implementation — follows confirmed plans, consumes contributions" | code_implementation, testing, debugging, code_review, refactoring | (consumers, not contributors) | 10m |
| DevOps | alpha-devops | sonnet | "Infrastructure owner — IaC, CI/CD, deployment, fleet health" | infrastructure_automation, ci_cd_pipelines, docker_management, deployment, monitoring | software-engineer | 15m |
| QA | alpha-qa-engineer | sonnet | "Test authority — predefinition before, validation during review" | test_predefinition, test_automation, quality_assurance, regression_testing | software-engineer | 15m |
| Writer | alpha-technical-writer | sonnet | "Living documentation — maintained alongside code, not after" | documentation, api_docs, adr_management, plane_pages, changelog | (documentation is the contribution) | 20m |
| UX | alpha-ux-designer | sonnet | "UX thinking — patterns, interactions, accessibility before build" | ux_design, accessibility, component_patterns, interaction_flows | software-engineer | 20m |
| Accountability | alpha-accountability-generator | sonnet | "Process verifier — trail compliance, governance, immune system feed" | compliance_reporting, trail_verification, governance, audit | (reports are the contribution) | 30m |

### Model Selection Rationale

| Model | Roles | Why |
|-------|-------|-----|
| opus | PM, fleet-ops, architect, devsecops | Strategic reasoning, complex decisions, review quality |
| sonnet | engineer, devops, QA, writer, UX, accountability | Implementation work, structured output, cost-effective |

The brain can OVERRIDE model per dispatch (strategic Claude call matrix).
agent.yaml sets the DEFAULT.

---

## 3. Validation Criteria

### Required Fields
- [ ] All 14 fields present (name, display_name, fleet_id, fleet_number, username, type, mode, backend, model, mission, capabilities, roles.primary, roles.contributes_to, heartbeat_config.every)
- [ ] No fields empty or placeholder

### Identity Consistency
- [ ] name format: `{fleet_id}-{role}` (e.g., "alpha-architect")
- [ ] display_name format: `{Role} {Fleet}` (e.g., "Architect Alpha")
- [ ] username = name (same value)
- [ ] fleet_id consistent across all 10 agents in same fleet
- [ ] fleet_number consistent across all 10 agents in same fleet

### Content Quality
- [ ] mission is ONE line, role-specific (not generic)
- [ ] capabilities list has 4-8 items (not generic like "works hard")
- [ ] capabilities are SPECIFIC to this role (no overlap with other roles)
- [ ] roles.primary matches one of: project-manager, fleet-ops, architect, devsecops-expert, software-engineer, devops, qa-engineer, technical-writer, ux-designer, accountability-generator
- [ ] roles.contributes_to matches fleet-elevation/15 synergy matrix

### Gateway Compatibility
- [ ] type = "agent"
- [ ] mode = "heartbeat"
- [ ] backend is "claude" or "localai"
- [ ] model is "opus" or "sonnet" (valid Claude models)
- [ ] heartbeat_config.every is valid interval string ("10m", "15m", etc.)

### Integration
- [ ] roles.contributes_to matches AGENTS.md synergy relationships
- [ ] capabilities align with skills in config/agent-tooling.yaml
- [ ] heartbeat interval aligns with agent-autonomy.yaml thresholds

---

## 4. IaC Flow

```
config/agent-identities.yaml       # fleet roster (names, roles)
fleet-elevation/16                  # multi-fleet identity design
fleet-elevation/15                  # synergy matrix (contributes_to)
     ↓
agents/_template/agent.yaml.template  # template with {placeholders}
     ↓
scripts/provision-agents.sh         # fills placeholders from config
     ↓
agents/{name}/agent.yaml            # deployed (gitignored, runtime)
     ↓
scripts/validate-agents.sh         # validates against THIS standard
     ↓
gateway reads on session creation   # configures agent sessions
orchestrator reads on cycle         # dispatch + lifecycle decisions
```

---

## 5. Relationship to Other Standards

| Standard Doc | Relationship |
|-------------|-------------|
| claude-md-standard.md | CLAUDE.md has role rules. agent.yaml has role identity + gateway config. |
| heartbeat-md-standard.md | HEARTBEAT.md has action protocol. agent.yaml has heartbeat_config.every (timing). |
| identity-soul-standard.md | IDENTITY.md has personality. agent.yaml has fleet identity fields used BY IDENTITY.md. |
| tools-agents-standard.md | TOOLS.md has tool docs. agent.yaml capabilities should align with available tools. |
| config/agent-tooling.yaml | Tooling config has per-role MCP servers + skills. agent.yaml capabilities align. |
| config/agent-autonomy.yaml | Autonomy config has per-role lifecycle thresholds. agent.yaml heartbeat interval aligns. |
