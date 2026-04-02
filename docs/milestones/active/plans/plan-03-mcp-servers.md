# Plan 03 — MCP Server Deployment

**Phase:** 3 (independent of Plan 02, can parallel)
**Source:** Synthesis D5, D6, D7, D8, D15 | Analysis 01 (tools)
**Milestone IDs:** EA-002, EA-008, EA-011 to EA-017

---

## What This Plan Delivers

Agents get: role-specific MCP servers beyond the current 5 types.
Security agents get vulnerability scanners. QA gets pytest integration.
PM gets official Plane MCP. All Python agents get Context7 MCP tools.

**PO decisions required:**
- D5: Security stack (Trivy alone vs Trivy+Semgrep vs Snyk)
- D6: pytest-mcp for Python stack
- D7: Plane MCP (alongside vs replace direct API)
- D8: GitHub MCP upgrade (basic → official 80+ tools)
- D15: Additional servers (git, SQLite, sequential-thinking, etc.)

---

## 1. Install Context7 MCP server (EA-002)

**What:** Library/framework documentation via MCP tools (resolve-library-id, query-docs)
**Currently:** context7 plugin installed for architect + engineer
**Enhancement:** MCP server adds on-demand query tools alongside plugin injection

**Steps:**
1. Add to agent-tooling.yaml for architect, engineer, writer:
   ```yaml
   - name: context7
     package: "@upstash/context7-mcp"
   ```
2. Run `scripts/setup-agent-tools.sh` to regenerate mcp.json
3. Verify: MCP tools resolve-library-id and query-docs available

**Test (in Claude Code):**
- Call resolve-library-id with "flask" — returns library ID?
- Call query-docs with library ID + query — returns current docs?

---

## 2. Install security MCP stack (D5)

**Options (PO decides):**

### Option A: Trivy only (free, zero cost)
```yaml
devsecops-expert:
  mcp_servers:
    - name: trivy
      command: "trivy"
      args: ["--mcp"]
```
- Install: `sudo apt install trivy` or Docker
- Covers: containers, filesystems, repos, IaC configs
- 5 tools: scan_image, scan_filesystem, scan_repo, scan_config, get_vulnerabilities

### Option B: Trivy + Semgrep (free, code patterns)
```yaml
devsecops-expert:
  mcp_servers:
    - name: trivy
      command: "trivy"
      args: ["--mcp"]
    - name: semgrep
      command: "semgrep"
      args: ["--mcp"]
```
- Semgrep adds: code-level SAST across 30+ languages, custom rules
- 4 additional tools: scan, get_findings, list_rules, apply_fix
- Connects to Trail of Bits semgrep-rule-creator skill

### Option C: Trivy + Semgrep + mcp-pypi (free, Python deps)
- Add `mcp-pypi` (pip install): scan_package, audit_dependencies, get_vulnerabilities, check_license
- Directly relevant — our stack is Python

### Option D: Snyk (freemium, all-in-one)
```yaml
devsecops-expert:
  mcp_servers:
    - name: snyk
      command: "snyk"
      args: ["--mcp"]
      env:
        SNYK_TOKEN: "{{SNYK_TOKEN}}"
```
- 11 tools covering everything
- Requires SNYK_TOKEN

**IaC:** All options go in agent-tooling.yaml → setup-agent-tools.sh generates mcp.json
**Also install for:** devops (container scanning at minimum)

---

## 3. Install pytest-mcp-server (D6)

**What:** 8 tools for Python test analysis: failures, coverage, debug trace, compare runs
**Directly relevant:** Our entire codebase is Python. 1732+ tests.

**Steps:**
1. Install: `pip install pytest-mcp-server` (in fleet venv)
2. Add to agent-tooling.yaml for QA + engineer:
   ```yaml
   - name: pytest-mcp
     command: "{{FLEET_VENV}}/bin/python"
     args: ["-m", "pytest_mcp_server"]
   ```
3. Run setup-agent-tools.sh
4. Verify: 8 tools available (get_failures, analyze_error, suggest_fix, etc.)

**Test (in Claude Code):**
- Run get_failures — shows any failing tests?
- Run get_coverage — shows coverage report?
- Run debug_trace on a specific test — useful output?

**Connects to:** quality-coverage skill, fleet-test skill, /debug command, systematic-debugging

---

## 4. Evaluate Plane MCP (D7)

**What:** Official makeplane/plane-mcp-server vs our direct API (plane_sync.py)
**Currently:** 7 fleet_plane_* MCP tools call Plane API directly via plane_client.py

**Evaluation steps:**
1. Clone: `git clone https://github.com/makeplane/plane-mcp-server`
2. Review: what tools does it provide vs our 7?
3. Test: run alongside our existing integration
4. Compare: standard MCP vs custom integration — what do we gain/lose?
5. Decision: complement (both), replace (migrate), or skip (ours is sufficient)

**Key question:** Does Plane MCP add tools our 7 don't have? Or is it the same surface?

---

## 5. Evaluate GitHub MCP upgrade (D8)

**What:** Current @modelcontextprotocol/server-github vs official github/github-mcp-server (80+ tools)
**Currently:** Basic GitHub MCP with standard tools

**Evaluation steps:**
1. Check: does current server cover Actions (get_workflow_runs)?
2. Check: does current server cover Dependabot alerts?
3. If gaps: install official server alongside or replace
4. Official server: Go binary or Docker, PAT auth, prompt injection protection

**Key question:** What capabilities does the 80+ tool server add that we actually need?

---

## 6. Additional MCP servers (D15)

**Candidates (PO decides which):**

| Server | For | Value |
|--------|-----|-------|
| Git MCP | ENG, DEVOPS, ARCH | Structured git output vs Bash |
| SQLite MCP | ENG, QA | Access fleet's own data stores |
| Sequential Thinking | ARCH, PM | Structured reasoning for complex decisions |
| Memory MCP | FLEET-OPS, ARCH | Lightweight knowledge graph |
| Diagram Bridge | ARCH, WRITER | Render architecture diagrams |

Each follows the same pattern:
1. Add to agent-tooling.yaml per role
2. Run setup-agent-tools.sh
3. Verify tools available
4. Test in Claude Code

---

## IaC Updates

All MCP server changes flow through:
1. `config/agent-tooling.yaml` — source of truth
2. `scripts/setup-agent-tools.sh` — generates per-agent mcp.json
3. `scripts/validate-agents.sh` — verifies mcp.json valid + servers respond

New servers may need:
- System dependencies (trivy binary, semgrep pip, pyright npm)
- Add dependency install to `scripts/install-dependencies.sh` (new script)
- Or handle in setup-agent-tools.sh dependency section

---

## Validation Checklist

- [ ] Context7 MCP tools working for architect + engineer + writer
- [ ] Security MCP stack installed for devsecops (per D5 decision)
- [ ] pytest-mcp-server working for QA + engineer
- [ ] Plane MCP evaluated (D7 decision recorded)
- [ ] GitHub MCP evaluated (D8 decision recorded)
- [ ] Additional servers installed (per D15 decisions)
- [ ] All mcp.json files regenerated via setup-agent-tools.sh
- [ ] validate-agents.sh passes for all 10 agents
- [ ] Each new MCP server tested with at least one tool call

---

## What This Enables

With this plan complete:
- DevsecOps has REAL security scanning tools (not just skills)
- QA has DEEP pytest integration (failures, coverage, debug trace)
- Agents can QUERY library docs on demand (Context7 MCP)
- Plane integration potentially upgraded to official MCP
- All MCP servers deployed via IaC (config-driven, reproducible)
