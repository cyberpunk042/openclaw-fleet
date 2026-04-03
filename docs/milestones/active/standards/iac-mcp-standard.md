# IaC + MCP Configuration Standard — Provisioning, Tools, Validation

**Date:** 2026-04-01
**Status:** ACTIVE STANDARD
**Type:** Infrastructure standard (scripts, configs, deployment)
**Source:** fleet-elevation/02 (template system), config/agent-tooling.yaml, PO requirements

---

## PO Requirement (Verbatim)

> "No hack. only good iac"
> "Everything must be scripted IaC-style"
> "make them available to them with the project + config + IaC + setups"

---

## 1. IaC Principles (Non-Negotiable)

| Principle | What It Means |
|-----------|--------------|
| **Idempotent** | Running a script twice produces the same result |
| **Config-driven** | Scripts read from YAML config, not hardcoded values |
| **Zero manual steps** | `make setup` from fresh clone → everything configured |
| **Validate before write** | Check config is valid before deploying files |
| **Report what changed** | Output what was created/updated/skipped |
| **Handle dependencies** | Install jq/npx/python/etc. if missing |
| **Source of truth in git** | Templates + config committed. Runtime output gitignored. |

---

## 2. Required Scripts

### 2.1 scripts/provision-agents.sh — Master Provisioning

**Purpose:** Create all agent directories from templates + config.
**Reads from:**
- `agents/_template/` (file templates)
- `config/agent-identities.yaml` (names, roles, fleet identity)
- Fleet-elevation specs (role-specific content for CLAUDE.md, HEARTBEAT.md)

**Produces:**
- `agents/{name}/` directory with all files for each of 10 agents

**Behavior:**
```bash
for each agent in config/agent-identities.yaml:
  1. Create agents/{name}/ directory if not exists
  2. Copy template files, fill {placeholders} from config
  3. Copy role-specific CLAUDE.md from _template/CLAUDE.md/{role}.md
  4. Copy role-specific HEARTBEAT.md from _template/heartbeats/{type}.md
  5. Generate TOOLS.md via generate-tools-md.sh
  6. Generate AGENTS.md via generate-agents-md.sh
  7. Generate mcp.json via setup-agent-tools.sh
  8. Report: "  [created|updated|skipped] agents/{name}/{file}"
```

**Idempotency:** Compares file hashes. Only writes if content differs.

### 2.2 scripts/setup-agent-tools.sh — MCP Server Deployment

**Purpose:** Deploy per-agent mcp.json from config/agent-tooling.yaml.
**Reads from:** `config/agent-tooling.yaml`
**Produces:** `agents/{name}/mcp.json` for each agent

**mcp.json structure:**
```json
{
  "mcpServers": {
    "fleet": {
      "command": "{FLEET_VENV}/bin/python",
      "args": ["-m", "fleet.mcp.server"],
      "env": {
        "FLEET_DIR": "{FLEET_DIR}",
        "FLEET_AGENT": "{AGENT_NAME}"
      }
    }
  }
}
```

**Per-role servers added from config:**
```yaml
# config/agent-tooling.yaml drives this:
agents:
  architect:
    mcp_servers:
      - name: filesystem
        package: "@modelcontextprotocol/server-filesystem"
        args: ["{{WORKSPACE}}"]
      - name: github
        package: "@modelcontextprotocol/server-github"
```

**Behavior:** For each agent, merge defaults + role-specific servers into mcp.json. Resolve `{{WORKSPACE}}`, `{{FLEET_DIR}}`, `{{FLEET_VENV}}`, `{{AGENT_NAME}}` placeholders.

### 2.3 scripts/install-plugins.sh — Claude Plugin Deployment

**Purpose:** Install Claude-Mem, Context7, and other plugins per agent.
**Reads from:** `config/agent-tooling.yaml` (plugins section)
**Executes:** `claude plugin install {plugin}` in each agent workspace

**Behavior:**
```bash
for each agent:
  for each plugin in config defaults + role overrides:
    if not already installed:
      cd agents/{name}
      claude plugin install {plugin}
      echo "  [installed] {agent}: {plugin}"
    else:
      echo "  [skipped] {agent}: {plugin} (already installed)"
```

### 2.4 scripts/generate-tools-md.sh — TOOLS.md Generation

**Purpose:** Generate chain-aware TOOLS.md per agent from code + config.
**Reads from:**
- `fleet/mcp/tools.py` (tool definitions, parameter signatures)
- Fleet-elevation/24 (tool call tree catalog — chain documentation)
- `config/agent-tooling.yaml` (which tools each role uses)

**Produces:** `agents/_template/TOOLS.md/{role}.md`

**This ensures TOOLS.md never drifts from actual tool implementations.**

### 2.5 scripts/generate-agents-md.sh — AGENTS.md Generation

**Purpose:** Generate AGENTS.md per role from synergy matrix.
**Reads from:**
- Fleet-elevation/15 (contribution matrix)
- `config/agent-identities.yaml` (display names)

**Produces:** `agents/_template/AGENTS.md/{role}.md`

**This ensures bidirectional consistency** — when the matrix changes,
ALL agents' AGENTS.md files update together.

### 2.6 scripts/validate-agents.sh — Standards Validation

**Purpose:** Validate all agent files against per-type standards.
**Reads from:** This document + all per-type standard docs
**Checks per agent:**

```bash
for each agent:
  # Structure checks
  check_file_exists "IDENTITY.md"
  check_file_exists "SOUL.md"
  check_file_exists "CLAUDE.md"
  check_file_exists "HEARTBEAT.md"
  check_file_exists "TOOLS.md"
  check_file_exists "AGENTS.md"
  check_file_exists "agent.yaml"
  check_file_exists "mcp.json"

  # CLAUDE.md specific
  check_char_count "CLAUDE.md" 4000
  check_section_exists "CLAUDE.md" "Core Responsibility"
  check_section_exists "CLAUDE.md" "Stage Protocol"
  check_section_exists "CLAUDE.md" "Anti-Corruption"
  check_no_generic_content "CLAUDE.md"

  # SOUL.md specific
  check_anti_corruption_rules "SOUL.md" 10
  check_section_exists "SOUL.md" "Humility"

  # IDENTITY.md specific
  check_fleet_identity_fields "IDENTITY.md"
  check_top_tier_language "IDENTITY.md"

  # agent.yaml specific
  check_required_yaml_fields "agent.yaml"
  check_fleet_consistency "agent.yaml"

  # mcp.json specific
  check_fleet_mcp_present "mcp.json"
  check_role_servers_match_config "mcp.json"

  # Cross-file checks
  check_no_concern_mixing
  check_contribution_consistency
  check_tool_references_valid
```

**Output:**
```
Validating agents/alpha-architect...
  [PASS] IDENTITY.md: fleet identity fields present
  [PASS] SOUL.md: 10 anti-corruption rules present
  [PASS] CLAUDE.md: 3847 chars (under 4000 limit)
  [PASS] CLAUDE.md: all required sections present
  [WARN] TOOLS.md: fleet_contribute chain description missing
  [PASS] AGENTS.md: 9 colleagues listed
  [PASS] agent.yaml: all required fields present
  [PASS] mcp.json: filesystem + github servers present
  [PASS] Cross-file: no concern mixing detected
  Result: 9 PASS, 1 WARN, 0 FAIL
```

---

## 3. Config File Standards

### 3.1 config/agent-identities.yaml

**Purpose:** Fleet roster. Names, roles, display names for all agents.
**Used by:** provision-agents.sh, generate-agents-md.sh, validate-agents.sh

```yaml
fleet:
  id: "alpha"
  name: "Fleet Alpha"
  number: 1

agents:
  - name: "alpha-project-manager"
    role: "project-manager"
    display_name: "Project Manager Alpha"
  - name: "alpha-fleet-ops"
    role: "fleet-ops"
    display_name: "Fleet-Ops Alpha"
  # ... 10 agents total
```

### 3.2 config/agent-tooling.yaml

**Purpose:** Per-role MCP servers, plugins, skills.
**Used by:** setup-agent-tools.sh, install-plugins.sh, generate-tools-md.sh
**Already exists:** YES (created 2026-04-01)
**Standard:** See current file for structure.

### 3.3 config/agent-autonomy.yaml

**Purpose:** Per-role lifecycle thresholds, wake triggers.
**Used by:** agent_lifecycle.py, orchestrator.py
**Already exists:** YES (created 2026-04-01)
**Standard:** See current file for structure.

---

## 4. Makefile Integration

```makefile
# Agent provisioning
provision:        scripts/provision-agents.sh
setup-tools:      scripts/setup-agent-tools.sh
install-plugins:  scripts/install-plugins.sh
validate-agents:  scripts/validate-agents.sh

# Full setup from zero
setup: provision setup-tools install-plugins validate-agents

# Regenerate generated files
generate: generate-tools generate-agents
generate-tools:   scripts/generate-tools-md.sh
generate-agents:  scripts/generate-agents-md.sh
```

`make setup` from a fresh clone → everything provisioned, configured,
validated. Zero manual steps.

---

## 5. Validation Criteria for Scripts

| Criterion | How to Verify |
|-----------|--------------|
| Idempotent | Run script twice, diff output — should be identical |
| Config-driven | Grep for hardcoded agent names — should find none |
| Zero manual steps | Fresh clone + `make setup` → all agents ready |
| Validates before writing | Script checks config structure before deploying |
| Reports changes | Script outputs what it did for each agent/file |
| Handles deps | Missing jq/npx → installs or errors with instructions |
| Source of truth | Templates in git, agent dirs gitignored |

---

## 6. Relationship to Other Standards

| Standard Doc | Relationship |
|-------------|-------------|
| claude-md-standard.md | IaC provisions CLAUDE.md from template. Validates against CLAUDE.md standard. |
| heartbeat-md-standard.md | IaC provisions HEARTBEAT.md from template. Validates against HEARTBEAT.md standard. |
| agent-yaml-standard.md | IaC generates agent.yaml from config. Validates against agent.yaml standard. |
| identity-soul-standard.md | IaC provisions IDENTITY.md + SOUL.md. Validates against identity-soul standard. |
| tools-agents-standard.md | IaC GENERATES TOOLS.md + AGENTS.md (not hand-written). Validates against standard. |
| context-files-standard.md | context/ is generated by BRAIN at runtime, not by IaC. IaC creates empty context/ dir. |
