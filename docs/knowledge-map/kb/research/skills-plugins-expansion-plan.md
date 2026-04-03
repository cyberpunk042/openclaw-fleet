# Skills & Plugins Expansion Plan — Per Agent

**Type:** Research Conclusion / Plan
**Date:** 2026-04-02
**Inputs:** agent-tooling.yaml (current), research group-02 (ecosystem), analysis-04 (commands), analysis-05 (hooks)
**Status:** PLAN — needs PO evaluation before implementation

## Current vs Target (Gap Analysis)

### Defaults (ALL agents)

| Category | Current | Target (from research) | Gap |
|----------|---------|----------------------|-----|
| MCP | fleet | fleet | — |
| Plugins | claude-mem | claude-mem, safety-net | **+safety-net** (catches destructive commands) |
| Skills | fleet-communicate | fleet-communicate | — |

**safety-net for ALL agents:** Research found safety-net (1K stars) hooks into PreToolUse to catch `rm -rf`, `git reset --hard`, `DROP TABLE`, etc. This is Line 1 anti-corruption — structural prevention. EVERY agent should have it.

---

### Architect

| Category | Current | Target | Gap |
|----------|---------|--------|-----|
| MCP | filesystem, github | filesystem, github, **Context7** | Context7 currently as plugin — evaluate as MCP |
| Plugins | context7 | context7, **superpowers**, **adversarial-spec**, **harness** | +3 plugins |
| Skills | 5 skills | 5 + **brainstorming**, **writing-plans** | +2 skills |

**Why superpowers:** 132K stars. TDD methodology, 20+ skills including writing-plans and brainstorming — core architect activities during reasoning stage.

**Why adversarial-spec:** 518 stars. Multi-LLM debate for spec refinement. Architect designs specs that need stress-testing from multiple perspectives.

**Why harness:** 2K stars. Meta-skill: designs agent teams. Architect may orchestrate multi-agent design sessions.

---

### Software Engineer

| Category | Current | Target | Gap |
|----------|---------|--------|-----|
| MCP | filesystem, github, playwright | filesystem, github, playwright, **ESLint**, **pytest-mcp**, **Context7** | +3 MCP |
| Plugins | context7 | context7, **superpowers**, **pyright-lsp** | +2 plugins |
| Skills | 7 skills | 7 + **systematic-debugging**, **TDD**, **verification** | +3 skills |

**Why superpowers:** TDD methodology (from superpowers plugin) aligns with fleet quality standards. systematic-debugging, TDD, and verification are superpowers skills.

**Why pyright-lsp:** Automatic Python type error detection. Fleet is Python-heavy (fleet/, aicp/).

**Why ESLint MCP:** If any frontend work exists. Evaluate need.

**Why pytest-mcp:** Test failure analysis, coverage reports, debug traces. Engineer runs tests constantly.

---

### QA Engineer

| Category | Current | Target | Gap |
|----------|---------|--------|-----|
| MCP | filesystem, playwright | filesystem, playwright, **pytest-mcp**, **test-runner** | +2 MCP |
| Plugins | (none) | **superpowers**, **claude-octopus** | +2 plugins |
| Skills | 8 skills | 8 + **TDD**, **systematic-debugging** | +2 skills |

**Why claude-octopus:** 2K stars. Multi-model review (up to 8 AIs). QA validates from multiple perspectives.

**Why test-runner MCP:** Unified test runner across pytest/jest/bats — QA runs tests in multiple frameworks.

---

### DevOps

| Category | Current | Target | Gap |
|----------|---------|--------|-----|
| MCP | filesystem, github, docker | filesystem, github, docker, **GitHub Actions** | +1 MCP |
| Plugins | (none) | **hookify**, **commit-commands** | +2 plugins |
| Skills | 10 skills | 10 (already comprehensive) | — |

**Why GitHub Actions MCP:** Workflow monitoring, run logs, artifacts. DevOps manages CI/CD.

**Why hookify:** Official Anthropic plugin. Natural-language hook creation — DevOps manages hook infrastructure.

**Why commit-commands:** Official Anthropic plugin. Git commit workflows — DevOps does infrastructure commits.

---

### DevSecOps (Cyberpunk-Zero)

| Category | Current | Target | Gap |
|----------|---------|--------|-----|
| MCP | filesystem, docker | filesystem, docker, **Semgrep**, **Trivy**, **Snyk** | +3 MCP (evaluate which) |
| Plugins | (none) | **sage**, **security-guidance**, **code-container** | +3 plugins |
| Skills | 5 skills | 5 + **security-scan**, **vuln-assess** | +2 skills (create new) |

**Why security MCP servers:** DevSecOps NEEDS automated scanning tools. Three options:
- **Semgrep** — 30+ languages, custom rules, free tier. Most flexible.
- **Trivy** — Container/filesystem/repo scan, open source. Best for containers.
- **Snyk** — Most comprehensive (SAST, SCA, IaC, container, SBOM), needs token. Enterprise-grade.

**PO decision needed:** Which security MCP servers to adopt (can start with Semgrep free + Trivy open source).

**Why sage:** 162 stars. Agent Detection and Response (ADR). DevSecOps detects agent misbehavior.

**Why security-guidance:** Official Anthropic plugin. 9 security patterns monitored via hooks.

**Why code-container:** 202 stars. Run agents in Docker containers. DevSecOps tests in isolated environments.

---

### Fleet-Ops

| Category | Current | Target | Gap |
|----------|---------|--------|-----|
| MCP | github | github | — |
| Plugins | (none) | **pr-review-toolkit**, **claude-octopus** | +2 plugins |
| Skills | 8 skills | 8 (already comprehensive for review role) | — |

**Why pr-review-toolkit:** Official Anthropic plugin. 5 parallel Sonnet agents per review. Massively enhances fleet-ops review quality.

**Why claude-octopus:** Multi-model review (up to 8 AIs). Independent validation perspectives.

---

### Project Manager

| Category | Current | Target | Gap |
|----------|---------|--------|-----|
| MCP | github | github, **Plane** | +1 MCP |
| Plugins | (none) | **plannotator**, **plan-cascade** | +2 plugins |
| Skills | 11 skills | 11 (already comprehensive) | — |

**Why Plane MCP:** Official `makeplane/plane-mcp-server`. PM manages Plane issues/cycles/modules. Currently using direct API calls in fleet_plane_* tools — MCP server provides standardized interface.

**Why plannotator:** 4K stars. Visual plan/diff annotation, team feedback. PM communicates plans visually.

**Why plan-cascade:** 149 stars. Cascading parallel task decomposition. PM breaks epics into sprints into tasks.

---

### Technical Writer

| Category | Current | Target | Gap |
|----------|---------|--------|-----|
| MCP | filesystem, github | filesystem, github, **Context7** | +1 MCP |
| Plugins | (none) | **context7**, **ars-contexta** | +2 plugins |
| Skills | 4 skills | 4 + **documentation-review** | +1 skill (create new) |

**Why Context7:** Writer needs library/framework documentation for accurate technical writing.

**Why ars-contexta:** 3K stars. Knowledge systems from conversation. Writer captures institutional knowledge.

---

### UX Designer

| Category | Current | Target | Gap |
|----------|---------|--------|-----|
| MCP | filesystem, playwright | filesystem, playwright | — |
| Plugins | (none) | (none — minimal plugin needs) | — |
| Skills | 1 skill | 1 + **ux-audit**, **design-system** | +2 skills (create new) |

UX designer is the leanest role. May gain more as UX-specific tools emerge.

---

### Accountability Generator

| Category | Current | Target | Gap |
|----------|---------|--------|-----|
| MCP | filesystem | filesystem | — |
| Plugins | (none) | (none — audit doesn't need plugins) | — |
| Skills | 4 skills | 4 (comprehensive for audit role) | — |

Accountability generator's power comes from fleet MCP tools (fleet_read_context, fleet_agent_status) and the trail system, not from plugins.

---

## Expansion Summary

### New Plugins Needed (by priority)

| Priority | Plugin | Agents | What It Provides |
|----------|--------|--------|-----------------|
| **P1** | safety-net | ALL (default) | PreToolUse hook catches destructive commands |
| **P1** | superpowers | ARCH, ENG, QA | TDD methodology, 20+ skills |
| **P2** | pr-review-toolkit | FLEET-OPS | 5 parallel Sonnet review agents |
| **P2** | security-guidance | DEVSEC | 9 security patterns via hooks |
| **P2** | pyright-lsp | ENG | Python type error detection |
| **P3** | plannotator | PM | Visual plan annotation |
| **P3** | adversarial-spec | ARCH | Multi-LLM spec debate |
| **P3** | claude-octopus | QA, FLEET-OPS | Multi-model review |
| **P3** | hookify | DEVOPS | Natural-language hook creation |
| **P3** | commit-commands | DEVOPS | Git commit workflows |
| **P3** | sage | DEVSEC | Agent Detection and Response |
| **P3** | code-container | DEVSEC | Isolated container execution |
| **P3** | ars-contexta | WRITER | Knowledge from conversation |
| **P3** | plan-cascade | PM | Task decomposition |
| **P3** | context7 | WRITER (plugin) | Library/framework docs |
| **P3** | harness | ARCH | Agent team design |

### New MCP Servers Needed

| Priority | Server | Agents | What It Provides |
|----------|--------|--------|-----------------|
| **P1** | Plane | PM | Official Plane MCP (issues, cycles, modules) |
| **P2** | pytest-mcp | ENG, QA | Test failures, coverage, debug traces |
| **P2** | Semgrep | DEVSEC | 30+ language security scanning |
| **P2** | Trivy | DEVSEC | Container/filesystem vulnerability scan |
| **P2** | GitHub Actions | DEVOPS | Workflow monitoring, logs, artifacts |
| **P2** | LightRAG | ALL (via daniel-lightrag-mcp) | Knowledge graph queries (22 tools) |
| **P3** | test-runner | QA | Unified test runner |
| **P3** | ESLint | ENG | Lint + fix |
| **P3** | Context7 (MCP) | WRITER, ARCH | Library documentation as MCP |

### New Skills Needed (to create)

| Skill | Agent | Purpose |
|-------|-------|---------|
| systematic-debugging | ENG, QA | From superpowers — structured debug methodology |
| TDD | ENG, QA | From superpowers — test-driven development workflow |
| verification | ENG | From superpowers — verify changes against requirements |
| brainstorming | ARCH | From superpowers — structured ideation |
| writing-plans | ARCH | From superpowers — plan writing methodology |
| security-scan | DEVSEC | Wrapper for security MCP server usage |
| vuln-assess | DEVSEC | Vulnerability assessment methodology |
| documentation-review | WRITER | Review documentation for accuracy/completeness |
| ux-audit | UX | UX audit methodology |
| design-system | UX | Design system compliance check |

### KB Entries Needed

For each new plugin added → KB entry in `kb/plugins/`
For each new skill created → KB entry in `kb/skills/`
For each new MCP server added → KB entry in `kb/tools/` or new `kb/mcp/` branch

**Estimated new KB entries:** 16 plugins + 10 skills + 9 MCP servers = **35 new entries**

## Implementation Approach

1. **PO evaluates this plan** — which plugins/MCP servers/skills to adopt
2. **Update agent-tooling.yaml** with approved additions
3. **Update install-plugins.sh** for new plugin installations
4. **Update setup-agent-tools.sh** for new MCP server configurations
5. **Create SKILL.md files** for new skills
6. **Write KB entries** for each addition
7. **Test** each agent has its tools working
8. **Update intent-map.yaml** with new tool/skill references per role per stage

## Relationships

- EXTENDS: config/agent-tooling.yaml (adds plugins, MCP servers, skills per role)
- EXTENDS: kb/plugins/ branch (16 new plugin KB entries)
- EXTENDS: kb/skills/ branch (10 new skill KB entries + fix 18 stubs)
- CREATES: kb/mcp/ branch (MCP server KB entries — new branch)
- CONNECTS TO: install-plugins.sh (IaC for plugin installation)
- CONNECTS TO: setup-agent-tools.sh (IaC for MCP server setup)
- CONNECTS TO: intent-map.yaml (new tools/skills referenced in intents)
- CONNECTS TO: injection-profiles.yaml (new content at each tier)
- CONNECTS TO: research group-02 (source of plugin/MCP evaluations)
- CONNECTS TO: analysis-04 (command recommendations per role)
- CONNECTS TO: analysis-05 (hook implementation priorities)
- GATES: PO decisions on which plugins/MCP to adopt
