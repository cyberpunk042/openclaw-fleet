# Chunk 2: MCP Server + Plugin Verification & Deployment

**Date:** 2026-04-07
**Status:** Planning
**Part of:** [tools-system-session-index.md](tools-system-session-index.md) — Chunk 2 of 9
**Depends on:** Chunk 1 (chain wiring — for tools.py to be stable before verifying MCP integration)
**Blocks:** Chunk 3 (skills from plugins), Chunk 6 (sub-agents from plugins), Chunk 7 (hooks from plugins)

---

## What This Chunk Accomplishes

Every agent's role-specific MCP servers are verified, installed, and reaching their workspaces. Every agent's configured plugins are verified, installed, and functional. After this chunk, the raw capability surface (Layers 2+3) is deployed and working.

---

## Current State

### MCP Servers (Layer 2)

**Config:** config/agent-tooling.yaml defines per-role MCP servers.
**Generation:** scripts/setup-agent-tools.sh generates per-agent mcp.json — WORKS.
**Deployment:** scripts/push-soul.sh now deploys per-agent mcp.json — FIXED this session.
**Verification:** Whether MCP server packages (npm/npx) are actually available in agent workspaces — UNKNOWN.

| MCP Server | Package | Agents | Verified? |
|------------|---------|--------|-----------|
| fleet | python -m fleet.mcp.server | ALL | YES — core fleet operation |
| lightrag | python -m daniel_lightrag_mcp | ALL (default) | NO — LocalAI dependency |
| filesystem | @modelcontextprotocol/server-filesystem | 8 agents | NO |
| github | @modelcontextprotocol/server-github | 6 agents | NO |
| playwright | @playwright/mcp@latest | 3 agents | NO |
| pytest-mcp | python -m pytest_mcp_server | 2 agents | NO |
| docker | @modelcontextprotocol/server-docker | 2 agents | NO |
| github-actions | github-actions-mcp-server | 1 agent (devops) | NO |
| semgrep | semgrep --mcp | 1 agent (devsecops) | NO |
| plane | makeplane/plane-mcp-server | 1 agent (PM) | NO |

### Plugins (Layer 3)

**Config:** config/agent-tooling.yaml defines per-role plugins.
**Installation:** scripts/install-plugins.sh exists — reads config, registers marketplaces, installs per agent.
**Verification:** Whether plugins are actually installed on any agent workspace — UNKNOWN.

| Plugin | Source | Agents | What It Provides | Verified? |
|--------|--------|--------|------------------|-----------|
| claude-mem | thedotmack/claude-mem | ALL | Cross-session semantic memory | NO |
| safety-net | kenryu42/claude-code-safety-net | ALL | PreToolUse destructive command detection | NO |
| context7 | Upstash (official external plugin) | architect, engineer, writer | Version-specific library docs | NO |
| superpowers | obra/superpowers | architect, engineer, QA | 14 skills + code-reviewer sub-agent + SessionStart hook | NO |
| pyright-lsp | Anthropic official | engineer | Python type checking | NO |
| pr-review-toolkit | Anthropic official | fleet-ops | 6 parallel review sub-agents | NO |
| security-guidance | Anthropic official | devsecops | 9 PreToolUse security hooks | NO |
| sage | Unknown source (162 stars) | devsecops | Agent Detection and Response | NO — source repo not found |
| hookify | Anthropic official | devops | Natural-language hook creation | NO |
| commit-commands | Anthropic official | devops | /commit, /commit-push-pr, /clean_gone | NO |
| plannotator | backnotprop/plannotator | PM | Visual plan/diff annotation | NO |
| adversarial-spec | zscole/adversarial-spec | architect | Multi-LLM spec debate | NO |
| ars-contexta | allgemeiner-intellekt/arscontexta | writer | Knowledge systems from conversation | NO — limited public info |

---

## What Needs to Happen

### Step 1: Verify MCP Server Package Availability

For each npx-based MCP server:
- Can npx resolve the package in the gateway environment?
- Does the server respond to a tool list query?
- Are there authentication requirements (GitHub MCP needs GITHUB_TOKEN)?

For each command-based MCP server:
- Is the command available (python -m pytest_mcp_server, semgrep --mcp)?
- Are Python packages installed in the fleet venv (pytest-mcp-server)?
- Is semgrep binary installed?

For the Plane MCP server:
- Is makeplane/plane-mcp-server compatible with self-hosted Plane?
- Does it work with the fleet's Plane API credentials?

For LightRAG MCP:
- Is this a fleet-specific MCP server or an external package?
- Does it require LocalAI to be running?
- Should it be conditional (only loaded when LocalAI is available)?

### Step 2: Verify Plugin Marketplace Sources

For each marketplace source in install-plugins.sh:
- Does the GitHub repository still exist at the listed URL?
- Is the marketplace registration command correct for the current Claude Code version?
- Are there any authentication requirements?

Known concerns:
- sage — repository not publicly findable. Needs alternative or removal.
- ars-contexta — limited public information. Needs verification.
- Some marketplace sources may have moved or renamed since initial research.

### Step 3: Test Plugin Installation End-to-End

For ONE agent (suggestion: software-engineer as it has the most plugins):
1. Run install-plugins.sh for that agent
2. Verify each plugin appears in the agent's .claude/ directory
3. Verify plugin skills appear in skill listing
4. Verify plugin hooks are active (if applicable)
5. Verify plugin sub-agents are available (if applicable)

### Step 4: Deploy MCP + Plugins to All Agents

1. Run setup-agent-tools.sh for all agents (generates per-agent mcp.json)
2. Run push-soul.sh (deploys per-agent mcp.json to workspaces — fixed this session)
3. Run install-plugins.sh for all agents
4. Verify: each agent workspace has correct mcp.json + installed plugins

### Step 5: Evaluate Unassigned Plugins

From the ecosystem research, several plugins are HIGH relevance but not assigned:

| Plugin | Potential Agents | What It Would Add |
|--------|-----------------|-------------------|
| feature-dev | architect, engineer | 3 sub-agents: code-explorer, code-architect, code-reviewer |
| code-review | fleet-ops, QA | Confidence-based automated code review |
| claude-code-setup | ALL | Analyze codebase, recommend automations |
| claude-md-management | ALL | CLAUDE.md quality auditing |
| skill-creator | architect, engineer | Create/eval/benchmark skills at scale |
| serena | architect, engineer | Semantic code analysis via LSP |
| elements-of-style | writer | Writing quality from Strunk's rules |
| episodic-memory | ALL | Cross-session conversation search |
| double-shot-latte | ALL | Auto-continuation (stops "shall I continue?") |
| frontend-design | UX, engineer | Production-grade frontend design |

Each needs evaluation:
- Does it conflict with existing plugins?
- Does it add meaningful capability for the role?
- What's the context cost (skills injected into system prompt)?
- Is it compatible with the fleet's gateway version?

Evaluation produces a recommendation: install, skip, or defer to later chunk.

### Step 6: Update config/agent-tooling.yaml

Based on verification and evaluation:
- Remove plugins that can't be sourced (sage if repo not found)
- Add evaluated plugins that passed assessment
- Fix any MCP server package references that changed
- Mark LightRAG as conditional on LocalAI availability
- Update any changed marketplace source URLs

### Step 7: Update session index

Mark Chunk 2 complete. Document what was verified, what was installed, what was deferred.

---

## Verification Criteria

- [ ] Every MCP server in config/agent-tooling.yaml is verified (package available, responds to queries)
- [ ] Every plugin in config/agent-tooling.yaml is verified (source exists, installs successfully)
- [ ] Per-agent mcp.json reaches workspaces with role-specific servers
- [ ] At least one agent tested end-to-end (MCP servers + plugins functional)
- [ ] Unassigned plugins evaluated with recommendation per role
- [ ] config/agent-tooling.yaml updated to reflect verified state
- [ ] install-plugins.sh works from clean state for all agents
- [ ] Non-verifiable plugins (sage, ars-contexta) either resolved or removed with replacement evaluation

---

## Known Risks

- **npx availability in gateway environment** — gateway runs Node.js but npx may not be in PATH for all MCP server spawning. May need gateway config adjustment.
- **Plugin marketplace API changes** — Claude Code plugin installation may have changed since install-plugins.sh was written. Needs testing.
- **Plugin conflicts** — multiple plugins may inject conflicting SessionStart hooks or overlapping skills. superpowers' SessionStart hook is aggressive (injects into EVERY session).
- **Context cost** — superpowers alone injects 14 skills. With context7, pr-review-toolkit sub-agents, etc., total skill/agent injection could approach the 150 skill / 30K char gateway limit.
- **Self-hosted Plane MCP** — the official makeplane/plane-mcp-server may expect cloud Plane, not self-hosted. Needs compatibility testing.
