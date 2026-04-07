# Phase B: MCP + Plugin Verification Findings

**Date:** 2026-04-07
**Status:** Investigation findings — before deployment
**Part of:** [tools-system-session-index.md](tools-system-session-index.md) — Phase B

---

## Environment

- Node.js v22.16.0, npm 10.9.2, npx available
- Claude CLI available at /home/jfortin/.local/bin/claude
- Gateway CLI (openarms/openclaw) NOT in current shell PATH
- Python 3.8.10 system + 3.11 in .venv
- WSL2 Linux 5.15.167.4-microsoft-standard-WSL2
- 7 of 10 agent workspaces exist (missing: qa-engineer, ux-designer, devsecops-expert)

---

## MCP Server Package Verification

### npm Registry Results

| Package | Config Name | Version | Status |
|---------|------------|---------|--------|
| @modelcontextprotocol/server-filesystem | filesystem | 2026.1.14 | ✅ AVAILABLE |
| @modelcontextprotocol/server-github | github | 2025.4.8 | ✅ AVAILABLE |
| @playwright/mcp | playwright | 0.0.70 | ✅ AVAILABLE |
| @makeplane/plane-mcp-server | plane | 0.1.5 | ✅ AVAILABLE (note: package is @makeplane/, config says makeplane/) |
| @modelcontextprotocol/server-docker | docker | — | ❌ NOT IN REGISTRY |
| github-actions-mcp-server | github-actions | — | ❌ NOT IN REGISTRY |

### Alternative Packages Found

| Original | Alternative | Version | Notes |
|----------|------------|---------|-------|
| @modelcontextprotocol/server-docker | @hypnosis/docker-mcp-server | 1.4.1 | Community package, universal Docker MCP |
| github-actions-mcp-server | github-actions-mcp | 1.0.1 | Different package name |

### Command-Based MCP Servers

| Server | Command | Status |
|--------|---------|--------|
| fleet | python -m fleet.mcp.server | ✅ WORKS (core fleet operation) |
| lightrag | python -m daniel_lightrag_mcp | ❌ NOT INSTALLED (LocalAI dependency) |
| pytest-mcp | python -m pytest_mcp_server | ❌ NOT INSTALLED in .venv |
| semgrep | semgrep --mcp | ❌ NOT INSTALLED |

### Config Corrections Needed

| Config Entry | Current | Should Be |
|-------------|---------|-----------|
| docker package | @modelcontextprotocol/server-docker | @hypnosis/docker-mcp-server (or evaluate alternatives) |
| github-actions package | github-actions-mcp-server | github-actions-mcp |
| plane package | makeplane/plane-mcp-server | @makeplane/plane-mcp-server |
| lightrag | In defaults (ALL agents) | Should be CONDITIONAL — only when LocalAI running |

### Packages to Install

| Package | Where | Command |
|---------|-------|---------|
| pytest-mcp-server | .venv | pip install pytest-mcp-server |
| semgrep | System | pip install semgrep (or binary install) |
| lightrag MCP | .venv | pip install daniel-lightrag-mcp (conditional) |

---

## Current Workspace Deployment State

### What's Deployed (from sample — software-engineer workspace)

| Component | Status |
|-----------|--------|
| .mcp.json | ONLY fleet server (template, not per-agent) |
| .claude/settings.json | Present (permissions + effort) |
| .claude/skills/ | EMPTY (fleet workflow skills not symlinked yet) |
| .agents/skills/ | PRESENT (13 gateway operation skills via symlink) |
| SOUL.md | Present |
| CLAUDE.md | Present |
| HEARTBEAT.md | Present |
| TOOLS.md | Present |
| Plugins | NONE installed |

### What SHOULD Be Deployed (after Phase B)

| Component | What's Needed |
|-----------|--------------|
| .mcp.json | Per-agent with role-specific servers (from agents/{name}/mcp.json) |
| .claude/skills/ | Fleet workflow skills (7 skills via symlink) |
| .claude/agents/ | Sub-agent definitions (future — Phase F) |
| Plugins | Per-role from config/agent-tooling.yaml |

### Missing Workspaces

3 agents have no workspace:
- qa-engineer
- ux-designer
- devsecops-expert

These need MC agent provisioning (gateway creates workspaces when agents are registered). This is a gateway/MC issue, not a deployment script issue.

---

## Deployment Actions Needed

### Action 1: Fix config/agent-tooling.yaml package references

Update incorrect package names:
- docker: @modelcontextprotocol/server-docker → @hypnosis/docker-mcp-server (or evaluate)
- github-actions: github-actions-mcp-server → github-actions-mcp
- plane: makeplane/plane-mcp-server → @makeplane/plane-mcp-server
- lightrag: move from defaults to conditional (only when LocalAI available)

### Action 2: Install missing Python packages

```bash
.venv/bin/pip install pytest-mcp-server    # for engineer + QA
pip install semgrep                         # for devsecops (system-wide)
# lightrag: defer until LocalAI is running
```

### Action 3: Run setup-agent-tools.sh to regenerate per-agent mcp.json

After fixing config, regenerate:
```bash
bash scripts/setup-agent-tools.sh
```

### Action 4: Run push-soul.sh to deploy to workspaces

The fix we made earlier (per-agent mcp.json + .claude/skills/ symlink) needs to be executed:
```bash
bash scripts/push-soul.sh
```

### Action 5: Verify deployment

After running scripts, verify:
- Each workspace has per-agent mcp.json with role-specific servers
- Each workspace has .claude/skills/ symlinked
- MCP servers can be spawned (npx packages resolve)

### Action 6: Missing workspaces

3 agents need workspaces. This requires:
- MC agent registration (if not done)
- Gateway provisioning cycle
- Or manual workspace creation

This may be blocked by gateway not running. Defer if needed.

---

## Plugin Verification (Deferred)

Plugin installation requires either:
- Gateway CLI (openarms/openclaw) in PATH — NOT AVAILABLE in current shell
- Claude CLI within each workspace — AVAILABLE but needs workspace-level execution

Plugin installation is best done when the gateway is running (it manages workspace-level plugin state). Since the gateway CLI isn't in PATH and we can't verify gateway status, plugin installation is DEFERRED to when the fleet is running.

What CAN be done now:
- Verify plugin marketplace sources exist (GitHub URLs)
- Update install-plugins.sh if needed
- Document which plugins to install per agent

What REQUIRES running fleet:
- Actual plugin installation
- Plugin verification (skills appear, hooks active)

---

## Evaluation: Unassigned Plugins

From the ecosystem research, these should be evaluated:

| Plugin | For | Priority | Rationale |
|--------|-----|----------|-----------|
| feature-dev | architect, engineer | HIGH | 3 sub-agents for code exploration + architecture + review |
| skill-creator | all | HIGH | Essential for building fleet-specific skills (Phase D) |
| episodic-memory | all | MEDIUM | Cross-session conversation search |
| double-shot-latte | all | MEDIUM | Auto-continuation reduces wasted heartbeat cycles |
| claude-code-setup | all | MEDIUM | Analyze codebase, recommend automations |
| elements-of-style | writer | LOW | Writing quality rules |
| serena | architect, engineer | LOW | Semantic code analysis (needs evaluation) |
| frontend-design | UX, engineer | LOW | Production-grade frontend (needs UI work) |

Evaluation requires: install in test workspace → verify functionality → assess context cost → decide per role. This is Phase B5 work.
