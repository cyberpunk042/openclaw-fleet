# Infrastructure — Client Libraries & IaC

> **8 infra files + IaC scripts. ~1908 lines. Every external service accessed through typed clients.**
>
> The fleet never makes raw HTTP calls. Every external service has a
> client: gateway (WebSocket RPC), MC (REST), Plane (REST), IRC
> (gateway WebSocket), ntfy (HTTP push), GitHub (CLI), config (YAML).
> Plus SQLite cache for API responses. Plus IaC scripts for codex
> plugin, statusline, skill packs, model optimization.

---

## 1. Why It Exists

Without typed clients:
- Every module that talks to MC would duplicate auth logic
- Gateway WebSocket protocol would be reimplemented per use
- Plane API changes would break 7 MCP tools simultaneously
- Error handling and retry logic would be inconsistent
- Credentials would be scattered across modules

Typed clients centralize: auth, error handling, caching, and protocol.
One change in the client = every consumer updated.

---

## 2. Client Inventory

### 2.1 Gateway Client (`fleet/infra/gateway_client.py`)

Talks to OpenClaw Gateway via WebSocket JSON-RPC on `ws://localhost:18789`.

```
Auth: ~/.openclaw/openclaw.json → gateway.auth.token

Available operations:
  prune_agent(session_key)    → sessions.delete  (kill sick session)
  force_compact(session_key)  → sessions.compact (reduce context)
  inject_content(session_key, content) → chat.send (wake/teach)
  create_fresh_session(key)   → sessions.patch   (regrow after prune)
  disable_gateway_cron_jobs() → file edit         (pause heartbeats)
  enable_gateway_cron_jobs()  → file edit         (resume heartbeats)
```

Used by: orchestrator (wake drivers, inject lessons), doctor (prune, compact).

### 2.2 MC Client (`fleet/infra/mc_client.py`)

Mission Control REST API client. CRUD for tasks, agents, board memory,
approvals, comments. SQLite cache for response caching.

```
Auth: LOCAL_AUTH_TOKEN from env or TOOLS.md

Key methods:
  list_tasks(board_id)
  get_task(board_id, task_id)
  create_task(board_id, title, ...)
  update_task(board_id, task_id, status, comment, custom_fields)
  list_agents()
  list_memory(board_id, limit)
  post_memory(board_id, content, tags)
  list_approvals(board_id)
  create_approval(board_id, task_id, ...)
  update_approval(board_id, approval_id, decision, comment)
  post_comment(board_id, task_id, comment)
  get_board(board_id) / get_board_id()
```

Used by: orchestrator (every cycle), MCP tools (every tool call), context assembly.

### 2.3 Plane Client (`fleet/infra/plane_client.py`)

Plane CE REST API. Issues, labels, states, comments, sprints, modules.

```
Auth: PLANE_API_KEY from env

Key methods:
  list_issues(workspace, project_id)
  get_issue(workspace, project_id, issue_id)
  create_issue(workspace, project_id, title, ...)
  update_issue(workspace, project_id, issue_id, state, labels, ...)
  list_labels(workspace, project_id)
  create_label(workspace, project_id, name, color)
  list_cycles(workspace, project_id) — sprints
  list_modules(workspace, project_id) — epics
  post_comment(workspace, project_id, issue_id, comment)
```

Used by: plane_sync, MCP tools (7 fleet_plane_* tools), context assembly.

### 2.4 IRC Client (`fleet/infra/irc_client.py`)

Posts messages to IRC via gateway WebSocket (not raw IRC protocol).

```
Auth: gateway token from ~/.openclaw/openclaw.json

Key methods:
  notify_event(agent, event, title, url)
  post_message(channel, message)
```

Used by: orchestrator (notifications), MCP tools (fleet_chat, fleet_alert), event chains.

### 2.5 ntfy Client (`fleet/infra/ntfy_client.py`)

Push notifications to PO's mobile via ntfy HTTP API.

```
Key methods:
  publish(title, message, priority, topic, tags, click_url)

Topics: progress (info), review (important), alert (urgent)
```

Used by: notification router, MCP tools (fleet_escalate, fleet_notify_human), storm.

### 2.6 GitHub Client (`fleet/infra/gh_client.py`)

Git and GitHub operations via `gh` CLI.

```
Key methods:
  create_pr(title, body, branch, base)
  push_branch(branch)
  get_pr_status(pr_url)
```

Used by: MCP tools (fleet_task_complete creates PR).

### 2.7 Config Loader (`fleet/infra/config_loader.py`)

Loads `config/*.yaml` files: fleet.yaml, phases.yaml, agent-identities.yaml,
skill-assignments.yaml, url-templates.yaml, projects.yaml.

### 2.8 SQLite Cache (`fleet/infra/cache_sqlite.py`)

Caches API responses to reduce MC API calls. TTL-based expiration.
Used by MCClient for task/agent/board data.

---

## 3. IaC Scripts

```
scripts/
├── install-codex-plugin.sh   Codex CLI + .codex/config.toml + instructions
├── install-statusline.sh     Claude Code statusline (context %, cost, rate limits)
├── install-skills.sh         Install skills from skill-assignments.yaml
├── register-skill-packs.sh   Register external skill packs
├── optimize-models.sh        KV cache quant, Flash Attn, function calling grammar
├── configure-board.sh        Set up OCMC board custom fields and tags
├── setup-mc.sh               Mission Control setup (register agents, skills)
├── dispatch-task.sh           Dispatch a task to an agent (set env, start session)
└── push-framework.sh         Push fleet framework to agent workspaces
```

Makefile targets:
- `make codex-setup` → install-codex-plugin.sh
- `make install-statusline` → install-statusline.sh
- `make skills-install` → install-skills.sh
- `make skills-sync` → register-skill-packs.sh

setup.sh wires: Step 13b (codex), Step 13c (statusline), Step 14 (board).

---

## 4. File Map

```
fleet/infra/
├── gateway_client.py   WebSocket RPC to OpenClaw gateway      (varies)
├── mc_client.py        Mission Control REST API                (varies)
├── plane_client.py     Plane CE REST API                       (varies)
├── irc_client.py       IRC via gateway WebSocket               (varies)
├── ntfy_client.py      Push notifications HTTP API             (varies)
├── gh_client.py        GitHub via gh CLI                       (varies)
├── config_loader.py    YAML config loading                     (varies)
└── cache_sqlite.py     SQLite response cache with TTL          (varies)

scripts/
├── install-codex-plugin.sh    Codex plugin IaC
├── install-statusline.sh      Claude Code statusline IaC
├── install-skills.sh          Skill installation
├── register-skill-packs.sh    Skill pack registration
├── optimize-models.sh         LocalAI model optimization
├── configure-board.sh         OCMC board setup
├── setup-mc.sh                MC initialization
├── dispatch-task.sh           Agent task dispatch
└── push-framework.sh          Framework push to agents
```

---

## 5. Consumers

Every system uses infrastructure clients:

| Client | Used By |
|--------|---------|
| Gateway | Orchestrator (wake, inject), Doctor (prune, compact), Teaching (inject) |
| MC | Orchestrator (every cycle), MCP Tools (every tool), Context Assembly |
| Plane | Plane Sync, MCP Tools (7 tools), Context Assembly, Transpose |
| IRC | Orchestrator, MCP Tools (chat, alert), Event Chains, Notifications |
| ntfy | Notification Router, MCP Tools (escalate, notify), Storm |
| GitHub | MCP Tools (fleet_task_complete → PR) |
| Config | Everywhere (fleet.yaml, phases.yaml, url-templates.yaml) |
| Cache | MC Client (reduces API calls) |

---

## 6. Design Decisions

**Why typed clients, not raw HTTP?** Auth, retry, error handling, and caching centralized. One fix in mc_client.py fixes every MC call in the fleet.

**Why gateway WebSocket, not HTTP?** OpenClaw's gateway protocol is WebSocket JSON-RPC. The client authenticates once and sends commands. HTTP would require auth per request.

**Why SQLite cache, not in-memory?** In-memory cache is lost on restart. SQLite survives restarts, gives warm starts. TTL-based expiration keeps data fresh.

**Why IaC scripts, not manual setup?** PO requirement: "I will certainly not manually enter the mission... it will be proper IaC with proper configs and scripts." Every setup step is scripted and reproducible via `make`.

---

---

## 7. Ecosystem Gap — Researched vs Deployed

We researched a massive ecosystem. We deployed almost none of it.

### 7.1 What We Researched (March 2026)

| Resource | Scale | What It Offers |
|----------|-------|----------------|
| **OpenClaw Skills Registry** | 5,400+ skills | Ready-made agent capabilities via ClawHub |
| **Claude Code Plugins** | 9,000+ plugins | Packaged skills, agents, hooks, MCP servers, LSP |
| **MCP Server Registry** | 1,000+ servers | GitHub, Slack, Postgres, Playwright, filesystem, Docker |
| **Agent Teams (Swarm Mode)** | Built into SDK | Lead + teammates, mailbox messaging, shared task lists |
| **Claude-Mem Plugin** | Cross-session | Semantic memory retrieval across sessions |
| **Context7** | Documentation | Up-to-date library docs injected into context |
| **Prompt Caching** | 90% savings | Cached input tokens at 10% cost |
| **Batch API** | 50% savings | Async processing at half cost |
| **LocalAI v4.0** | Built-in agents | Per-agent knowledge bases, MCP support, chromem/postgres |
| **LocalAI RAG Stack** | CPU-only | Embeddings (nomic) + stores + reranker (bge) — zero GPU cost |
| **AICP RAG Pipeline** | SQLite-backed | rag.py + kb.py + stores.py — persist through docker purge |

### 7.2 What We Actually Deployed

| Item | Status |
|------|--------|
| codex-plugin-cc | ✅ IaC: `make codex-setup` |
| Anthropic skills pack | ✅ IaC: `make skills-sync` |
| Statusline | ✅ IaC: `make install-statusline` |
| KV cache + Flash Attention | ✅ IaC: `make optimize-models` |
| .claudeignore (4 projects) | ✅ Applied |
| Docker /data persistence | ✅ Applied |
| Function calling grammar | ✅ Applied |

### 7.3 What We Have NOT Deployed (But Researched)

| Item | What It Would Enable | Effort |
|------|---------------------|--------|
| **MCP servers for agents** | Playwright (browser automation), filesystem, Docker, databases | Medium — configure in .mcp.json per agent |
| **Claude-Mem plugin** | Semantic memory across agent sessions | Low — install plugin |
| **Prompt caching** | 90% savings on repeated context | Low — API parameter |
| **Batch API** | 50% savings on non-urgent work | Low — API parameter |
| **OpenClaw skills (5400+)** | Agent capabilities without custom code | Medium — evaluate + install |
| **Additional Claude plugins** | connect-apps (500+ SaaS), Local-Review, ship | Medium — evaluate + install |
| **Agent Teams (swarm mode)** | Inter-agent mailbox messaging | Medium — evaluate architecture fit |
| **LocalAI RAG (CPU)** | Knowledge base queries at zero GPU cost | Medium — wire AICP RAG to fleet |
| **LocalAI v4.0 agents** | Per-agent knowledge bases | High — evaluate vs current architecture |
| **OpenRouter free tier** | 29 free models for community-tier work | Medium — build client |
| **AICP ↔ Fleet bridge** | Unified routing, shared RAG, shared skills | High — router_unification.py |

### 7.4 What This Means

The fleet operates with a FRACTION of the available tooling. The
research proved these capabilities exist and are accessible. The
deployment gap is not technical — it's prioritization. Each item
above has a known path to deployment (IaC scripts, config files,
plugin installs). The question is: which ones first?

**Immediate wins (config/install only):**
1. Prompt caching — 90% savings, API parameter change
2. Claude-Mem plugin — cross-session memory, plugin install
3. MCP servers — Playwright for browser automation, .mcp.json config

**Medium-term (needs evaluation + integration):**
4. OpenClaw skills — evaluate which 5400+ skills are relevant
5. LocalAI RAG — wire AICP's existing rag.py/kb.py to fleet context
6. Agent Teams — evaluate swarm mode vs current orchestrator model

**Strategic (needs architecture decisions):**
7. AICP ↔ Fleet bridge — unify routing across both systems
8. LocalAI v4.0 agents — evaluate whether to use built-in agent system

---

## 8. What's Needed

### Client Gaps
- LocalAI client integration (AICP has `openai_client.py`, fleet uses separate pattern)
- OpenRouter client (for free tier routing — 29 free models)
- Health checking via clients (ping endpoints, measure latency)
- Connection pooling / retry hardening for production use

### Ecosystem Deployment
- Evaluate and install top MCP servers per agent role
- Enable prompt caching (immediate 90% savings)
- Install Claude-Mem plugin (cross-session memory)
- Evaluate OpenClaw skills registry for fleet-relevant capabilities
- Wire AICP RAG pipeline into fleet agent context

## 9. Test Coverage: **30+ tests** across client modules
