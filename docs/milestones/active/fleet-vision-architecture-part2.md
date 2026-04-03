# Fleet Vision Architecture — Part 2

**Continuation of fleet-vision-architecture.md**
**Date:** 2026-03-31
**Status:** ACTIVE — code-verified

---

## 20. Gateway Integration — How Agents Actually Run

### 20.1 OpenClaw Gateway (VERIFIED from filesystem)

**Gateway location:** WebSocket JSON-RPC on `ws://localhost:18789`
**Config:** `~/.openclaw/openclaw.json`
**Agent data:** `~/.openclaw/agents/{name}/` — model configs + session data
**Workspace:** `/home/jfortin/openclaw-fleet` (the fleet repo)

**How it works:**
1. Gateway reads agent workspace files from `agents/{name}/`
2. Gateway builds system prompt from agent files (exact injection order: NEEDS EMPIRICAL VERIFICATION — design doc says IDENTITY→SOUL→CLAUDE→TOOLS→AGENTS→context→HEARTBEAT but this is not verified in gateway code)
3. Gateway runs Claude Code CLI (`claude --permission-mode bypassPermissions`)
4. Agent session receives system prompt + user message
5. Agent responds, calls MCP tools, produces output
6. Gateway manages session lifecycle (heartbeats, cron jobs)

### 20.2 Gateway Client Interface (VERIFIED)

**Source:** `fleet/infra/gateway_client.py`

| Function | Gateway RPC | Purpose |
|----------|------------|---------|
| `prune_agent(session_key)` | `sessions.delete` | Kill sick session (immune response) |
| `force_compact(session_key)` | `sessions.compact` | Reduce context (teaching) |
| `inject_content(session_key, content)` | `chat.send` | Inject lesson/wake data |
| `create_fresh_session(session_key)` | `sessions.patch` | Fresh session after prune |
| `disable_gateway_cron_jobs()` | file edit | Pause all heartbeats |
| `enable_gateway_cron_jobs()` | file edit | Resume heartbeats |

Auth: reads token from `~/.openclaw/openclaw.json` → `gateway.auth.token`

### 20.3 Agent Template Files — What Gateway Reads (VERIFIED)

Gateway workspace files per agent:

| File | In Template | Committed | Gateway Reads | Purpose |
|------|------------|-----------|---------------|---------|
| `agent.yaml` | Yes | All agents | Yes (registration) | Identity, mission, capabilities |
| `CLAUDE.md` | — | All agents | Yes (system prompt) | Role-specific rules (max 4000 chars) |
| `HEARTBEAT.md` | Yes | All agents | Yes (action prompt) | What to do on heartbeat |
| `MC_WORKFLOW.md` | Yes (template only) | — | Yes (if present) | Workflow instructions |
| `STANDARDS.md` | Yes (template only) | — | Yes (if present) | Fleet standards |
| `MC_API_REFERENCE.md` | Yes (template only) | — | Yes (if present) | MCP tool reference |
| `mcp.json` | Yes (template only) | — | Yes (MCP config) | Fleet MCP server config |
| `.claude/settings.json` | Yes (template only) | — | Yes (permissions) | Tool permissions |
| `IDENTITY.md` | — | Persistent only | Yes (if present) | Agent identity |
| `SOUL.md` | — | Persistent only | Yes (if present) | Values, boundaries |
| `TOOLS.md` | — | Never | Yes (if present) | Generated tool reference |
| `AGENTS.md` | — | Persistent only | Yes (if present) | Colleague knowledge |
| `USER.md` | — | Persistent only | Yes (if present) | Who agent serves |
| `context/fleet-context.md` | — | Overwritten | Yes (heartbeat data) | Pre-embedded role data |
| `context/task-context.md` | — | Overwritten | Yes (task data) | Pre-embedded task data |

**Key finding:** Template files (MC_WORKFLOW.md, STANDARDS.md, MC_API_REFERENCE.md, mcp.json, .claude/settings.json) are in `_template/` but NOT automatically copied to each agent directory. If an agent doesn't have them, the gateway doesn't inject them.

**This means:** Worker agents may be running WITHOUT the workflow instructions, standards, and API reference unless these were manually copied. This is a deployment gap.

### 20.4 MCP Server Configuration (VERIFIED)

**Source:** `agents/_template/mcp.json`

The fleet MCP server runs as: `{venv}/bin/python -m fleet.mcp.server`

Environment variables set per agent:
- `FLEET_DIR` — fleet repo root
- `FLEET_AGENT` — agent name
- `FLEET_WORKSPACE` — workspace path
- `FLEET_TASK_ID`, `FLEET_PROJECT` — set at dispatch time

---

## 21. Per-Agent Current State — Honest Inventory

### 21.1 CLAUDE.md Content Assessment

| Agent | Lines | Has Anti-Corruption? | Has Stage Protocol? | Has Tool Chains? | Has Contributions? | Quality |
|-------|-------|---------------------|--------------------|--------------------|-------------------|---------|
| architect | 74 | No | No | No | Partial | Functional, not per spec |
| software-engineer | 89 | No | No | No | Partial | Functional, not per spec |
| qa-engineer | 73 | No | No | No | No | Generic |
| ux-designer | 66 | No | No | No | No | Generic |
| devops | 63 | No | No | No | No | Generic |
| technical-writer | 69 | No | No | No | No | Generic |
| fleet-ops | 85 | No | No | No | No | Functional, not per spec |
| project-manager | 105 | No | No | No | Partial | Most complete |
| devsecops-expert | 139 | No | No | No | No | Rich personality, best done |
| accountability-generator | ~60 | No | No | No | No | Minimal |

**Summary:** 0/10 agents have anti-corruption rules. 0/10 have stage protocol per methodology. 0/10 have tool→chain documentation. 0/10 have contribution model per fleet-elevation/15. Devsecops has the richest identity but even it doesn't follow the fleet-elevation spec structure.

### 21.2 HEARTBEAT.md Assessment

| Agent | Source | Stage-Aware? | Tool Chains? | Per-Role Priorities? |
|-------|--------|-------------|--------------|---------------------|
| architect | Custom | Partial | No | Partial |
| software-engineer | Template | Yes (from template) | Yes (from template) | No (generic) |
| qa-engineer | Template | Yes (from template) | Yes (from template) | No (generic) |
| ux-designer | Template | Yes (from template) | Yes (from template) | No (generic) |
| devops | Custom | Partial | No | Yes |
| technical-writer | Template | Yes (from template) | Yes (from template) | No (generic) |
| fleet-ops | Custom | No | No | Yes (approval-focused) |
| project-manager | Custom | No | No | Yes (assignment-focused) |
| devsecops-expert | Custom | Yes | Yes | Yes (security-focused) |
| accountability-generator | Custom | No | No | No |

**Summary:** Workers use the template HEARTBEAT.md which IS stage-aware (good). Drivers have custom heartbeats but they're NOT aligned with fleet-elevation specs. Devsecops has the best heartbeat.

---

## 22. Data Flow Diagram — Verified

```
┌──────────────────────────────────────────────────────────────────────┐
│                        PO (Product Owner)                            │
│  Directives via board memory │ Plane issues │ Gates at 90% readiness │
└──────────┬───────────────────┴──────────────┴────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (Brain) — 30s cycle                   │
│                                                                      │
│  Step 0: Write context/ files (pre-embed FULL data per role)         │
│  Step 1: Security scan (behavioral_security.py)                      │
│  Step 2: Doctor (immune system — detect, teach, prune)               │
│  Step 3: Ensure review approvals exist                               │
│  Step 4: Wake PM (unassigned tasks) + fleet-ops (pending reviews)    │
│  Step 5: Dispatch ready tasks to assigned agents                     │
│  Step 6: Process PO directives                                       │
│  Step 7: Evaluate parent tasks (all children done → review)          │
│  Step 8: Health check (stuck tasks, offline agents)                  │
│                                                                      │
│  Guards: Storm monitor │ Budget monitor │ Fleet mode                 │
└──────────┬───────────────────────────────────────────────────────────┘
           │ writes context/ files        │ inject_content()
           │ (every cycle)                │ (wake/teach)
           ▼                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    GATEWAY (OpenClaw) — ws://localhost:18789          │
│                                                                      │
│  Reads agent workspace files:                                        │
│    agents/{name}/CLAUDE.md + HEARTBEAT.md + context/*.md + ...       │
│  Builds system prompt (injection order TBD)                          │
│  Runs Claude Code CLI                                                │
│  Manages sessions (heartbeat cron, prune, compact)                   │
│  MCP server: fleet/mcp/server.py (25 tools)                         │
└──────────┬───────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    AGENT (Claude Code Session)                        │
│                                                                      │
│  System prompt: IDENTITY → SOUL → CLAUDE → TOOLS → AGENTS           │
│                 → context/fleet-context → context/task-context        │
│                 → HEARTBEAT                                          │
│                                                                      │
│  Agent reads pre-embedded data → follows stage protocol              │
│  Calls MCP tools → tools execute actions + fire event chains         │
│                                                                      │
│  Stage gates: fleet_commit blocked outside work stage                │
│  Doctor watches: protocol violations detected + taught               │
└──────────┬───────────────────────────────────────────────────────────┘
           │ MCP tool calls
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    FLEET MCP SERVER (25 tools)                        │
│                                                                      │
│  fleet_read_context → MC API (task, board memory, agents)            │
│  fleet_commit → git commit + event                                   │
│  fleet_task_complete → push + PR + review + approval + IRC           │
│  fleet_artifact_create/update → Plane HTML (transpose layer)         │
│  fleet_chat → board memory + @mention routing + IRC                  │
│  fleet_alert → board memory + IRC #alerts + ntfy                     │
│  fleet_approve → approval chain + event + IRC                        │
│  fleet_plane_* → Plane API (issues, sprints, comments, sync)         │
│                                                                      │
│  Each tool call fires EVENT CHAINS across surfaces:                  │
│    INTERNAL (MC) + PUBLIC (GitHub) + CHANNEL (IRC) + NOTIFY (ntfy)   │
│    + PLANE (sync) + META (metrics)                                   │
└──────────┬───────────────────────────────────────────────────────────┘
           │ Events propagate to
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SURFACES                                 │
│                                                                      │
│  Mission Control (OCMC) ← tasks, agents, board memory, approvals     │
│  Plane ← issues, labels, descriptions (transpose), comments         │
│  GitHub ← branches, PRs, commits                                    │
│  IRC (The Lounge) ← real-time notifications, cross-refs             │
│  ntfy ← push notifications to PO mobile                             │
│  LocalAI ← inference (NOT connected to fleet routing yet)            │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 23. Contribution Flow — Implementation Design

### 23.1 What Needs Building (Verified Gap)

The contribution flow is the mechanism by which specialists provide input BEFORE implementation begins. The PO said: "everyone brings their piece, their segments and artifacts."

**Required new MCP tools:**
1. `fleet_contribute(task_id, contribution_type, content)` — post contribution to another agent's task
2. `fleet_request_input(task_id, target_role, request)` — request missing contribution

**Required brain logic:**
3. When task enters REASONING stage with readiness approaching 80:
   - Check task_type against contribution matrix
   - Create parallel contribution subtasks (auto_created=true)
   - Each subtask: parent_task linked, contribution_type set, assigned to specialist
4. Before allowing WORK stage (readiness 99):
   - Check: all required contributions received for this phase?
   - Missing → block advancement, notify PM

**Required context enhancement:**
5. Worker's task-context.md must include received contributions
6. Architect's design_input, QA's test criteria, DevSecOps's requirements — all in the worker's context before work begins

### 23.2 Contribution Matrix (from fleet-elevation/15)

| Task Enters REASONING | Architect | QA | UX | DevSecOps | Writer |
|-----------------------|-----------|-----|-----|-----------|--------|
| epic | design_input (required) | qa_test_def (required) | ux_spec (if UI) | security_req (required) | doc_outline (recommended) |
| story | design_input (required) | qa_test_def (required) | ux_spec (if UI) | security_req (if security) | doc_outline (recommended) |
| task | design_input (if complex) | qa_test_def (recommended) | — | security_req (if security) | — |
| bug | — | qa_test_def (regression) | — | security_req (if security) | — |

### 23.3 Phase-Dependent Requirements (from config/phases.yaml)

| Phase | Required Contributors |
|-------|---------------------|
| POC | Architect |
| MVP | Architect + QA + DevSecOps |
| Staging | Architect + QA + DevSecOps + Writer |
| Production | ALL applicable |

---

## 24. AICP ↔ Fleet Bridge — What Exists

### 24.1 AICP Has (Not Connected)

| AICP Module | What It Does | Fleet Could Use It For |
|-------------|-------------|----------------------|
| `aicp/core/router.py` | Backend routing (LocalAI vs Claude) | Route agent tasks to cheapest backend |
| `aicp/core/rag.py` | SQLite vector store + cosine search | Agent knowledge queries |
| `aicp/core/kb.py` | Knowledge base + reranker | Project-specific knowledge |
| `aicp/core/stores.py` | LocalAI /stores/ client | Fast similarity search |
| `aicp/core/skills.py` | 3-layer skill system | Agent skill management |
| `aicp/core/tools.py` | LocalAI function calling | Direct tool use without Claude |
| `aicp/core/context.py` | Project context builder | Agent context enrichment |
| `aicp/core/gpu.py` | GPU detection + auto-config | LocalAI model management |
| `aicp/core/cluster.py` | Multi-node coordination | Fleet Alpha + Bravo peering |

### 24.2 Fleet Has (Not Connected to AICP)

| Fleet Module | What It Does | AICP Connection Point |
|-------------|-------------|----------------------|
| `backend_router.py` | Route by complexity + budget | → `aicp/core/router.py` |
| `model_swap.py` | Swap LocalAI models | → `aicp/core/gpu.py` |
| `session_telemetry.py` | Parse Claude Code session JSON | → budget/storm/labor systems |
| `backend_health.py` | Track backend health | → `aicp/core/stores.py` (LocalAI health) |
| `router_unification.py` | Unified routing request schema | → bridge module (NOT built) |

### 24.3 The Bridge (NOT Built)

The bridge would:
1. Fleet's `backend_router.py` decides: this task goes to LocalAI
2. Bridge translates fleet routing decision into AICP router call
3. AICP's `router.py` routes to LocalAI
4. Result flows back through bridge to fleet MCP tool response

This is `router_unification.py` (M-BR08) — currently a FUTURE schema only.

---

## 25. LocalAI Integration — What's Available (VERIFIED)

### 25.1 Current Docker Config

**Source:** `docker-compose.yaml`

- Port: 8090 (host) → 8080 (container)
- GPU: NVIDIA via WSL2 `/dev/dxg`, CUDA 12
- Single active backend: only one GPU model at a time
- Watchdog: auto-recover stuck backends (15m idle, 5m busy)
- Context size: 8192
- Data volume: `./data:/data` (JUST ADDED — persistence fix)

### 25.2 Models Configured (VERIFIED from models/*.yaml)

| Model | Size | GPU Layers | KV Cache Quant | Flash Attn | Prompt Cache | Function Calling |
|-------|------|-----------|----------------|------------|-------------|-----------------|
| hermes-3b | 2.0GB | 32 (full) | Q4_0 ✓ | ✓ | ✓ | ✓ (grammar) |
| hermes (7B) | 4.4GB | 24 | Q4_0 ✓ | ✓ | ✓ | ✓ (parallel) |
| codellama (7B) | 4.4GB | 99 (full) | Q4_0 ✓ | ✓ | ✓ | ✓ (grammar) |
| phi-2 (2.7B) | 1.6GB | 0 (CPU) | Q4_0 ✓ | ✓ | ✓ | ✓ (grammar) |
| llava (7B) | 4.4GB | GPU | Q4_0 ✓ | ✓ | — | ✓ (grammar) |
| nomic-embed | — | 0 (CPU) | — | — | — | — (embedding only) |
| bge-reranker | — | 0 (CPU) | — | — | — | — (reranking only) |
| whisper | — | — | — | — | — | — (STT only) |
| piper-tts | — | — | — | — | — | — (TTS only) |
| stablediffusion | — | GPU | — | — | — | — (image gen only) |

**Optimizations applied this session:** KV cache Q4_0, Flash Attention, function calling grammar, prompt caching, repeat penalty, context 4096→8192. All via IaC (`make optimize-models`).

### 25.3 RAG Stack (Available, Not Wired)

```
Embedding (nomic-embed, CPU) ─── runs simultaneously with GPU LLM
     │
     ▼
Store (SQLite via aicp/core/rag.py OR LocalAI /stores/)
     │
     ▼
Query (cosine similarity search)
     │
     ▼
Rerank (bge-reranker, CPU) ─── runs simultaneously with GPU LLM
     │
     ▼
Inject into agent context (via pre-embed or MCP tool response)
```

**Zero GPU cost for RAG operations.** Embedding and reranking run on CPU independently.

---

## 26. Ecosystem Available (VERIFIED by Research)

### 26.1 What We Could Use But Don't

| Resource | Scale | What It Offers | Status |
|----------|-------|----------------|--------|
| OpenClaw Skills Registry | 5,400+ skills | Ready-made agent capabilities | NOT EXPLORED |
| Claude Code Plugins | 9,000+ plugins | Packaged skills, agents, hooks, MCP | NOT EXPLORED |
| MCP Server Registry | 1,000+ servers | GitHub, Slack, Postgres, browser | NOT EXPLORED |
| Agent Teams (Swarm Mode) | Built into SDK | Lead + teammates, mailbox messaging, shared tasks | NOT EVALUATED |
| Prompt Caching | 90% off cached input | Massive cost reduction | NOT ENABLED |
| Batch API | 50% off async work | Non-latency-critical savings | NOT USED |
| Claude-Mem Plugin | Cross-session memory | Semantic retrieval across sessions | NOT INSTALLED |

### 26.2 Cost Optimization Potential

| Mechanism | Estimated Savings | Implementation Effort |
|-----------|------------------|----------------------|
| Silent heartbeats (brain evaluates sleeping) | ~70% on idle agents | Medium (brain logic) |
| Prompt caching | ~90% on repeated context | Low (config change) |
| LocalAI for simple tasks | ~100% on heartbeats | Medium (routing) |
| Batch API for non-urgent work | ~50% on async | Low (API parameter) |
| Reduced wake frequency (IDLE/SLEEPING) | ~50-80% per idle agent | Already partially implemented |

---

## 27. The Real Priority — What Blocks Live Testing

### 27.1 Critical Path to First Live Test

```
BLOCKER 1: Template files not deployed to agents
  → MC_WORKFLOW.md, STANDARDS.md, MC_API_REFERENCE.md, mcp.json
    not in agent directories, only in _template/
  → Agents may run without workflow instructions
  → FIX: Deploy template files OR verify gateway reads from _template/

BLOCKER 2: CLAUDE.md not per fleet-elevation spec
  → No anti-corruption rules, no stage protocol, no contribution model
  → Agents won't follow methodology properly
  → FIX: Rewrite all 10 CLAUDE.md files per fleet-elevation specs

BLOCKER 3: Contribution flow not implemented
  → No fleet_contribute tool, no brain creates subtasks
  → Specialists can't provide input before implementation
  → FIX: Add fleet_contribute tool + brain logic
  → NOTE: Can do first live test WITHOUT this (simpler flow first)

BLOCKER 4: Pre-embed not fully role-specific
  → PM doesn't get Plane sprint data in pre-embed
  → Workers don't get artifact completeness in pre-embed  
  → FIX: Enhance role_providers.py with full data per AR-01 spec
  → NOTE: Current pre-embed is functional, just not per AR spec
```

### 27.2 Minimum Viable Live Test

Skip contribution flow for first test. Simplest possible live test:

```
1. Create a task on OCMC (manually)
2. Assign to software-engineer (manually set agent_name)
3. Set stage=reasoning, readiness=99 (skip earlier stages)
4. Start orchestrator (daemon)
5. Orchestrator dispatches task to agent
6. Agent receives context, follows work protocol
7. Agent calls fleet_commit, fleet_task_complete
8. Task moves to review
9. Fleet-ops heartbeats, sees pending approval
10. Fleet-ops approves/rejects
11. Done.
```

This tests: dispatch, agent execution, MCP tools, event chains, approval flow. It does NOT test: contribution flow, stage progression, PM assignment, Plane sync.

But it would be the FIRST proof that the fleet actually works.

---

## 28. Document Index — All Design Docs and Their Status

### 28.1 Fleet Elevation (31 docs)

| Doc | Title | Code Exists? | Live Tested? |
|-----|-------|-------------|-------------|
| 01 | Overview | — | — |
| 02 | Agent Architecture | Partial (file structure exists) | No |
| 03 | Delivery Phases | Yes (phases.py) | No |
| 04 | The Brain | Yes (orchestrator.py) | Partial |
| 05 | Project Manager | Partial (role_providers) | No |
| 06 | Fleet-Ops | Partial (role_providers) | No |
| 07 | Architect | Partial (role_providers) | No |
| 08 | DevSecOps | Partial (behavioral_security) | No |
| 09 | Software Engineer | Template heartbeat | No |
| 10 | DevOps | Template heartbeat | No |
| 11 | QA Engineer | Template heartbeat | No |
| 12 | Technical Writer | Template heartbeat | No |
| 13 | UX Designer | Template heartbeat | No |
| 14 | Accountability Generator | Partial (src/) | No |
| 15 | Cross-Agent Synergy | No (contribution flow missing) | No |
| 16 | Multi-Fleet Identity | No | No |
| 17 | Standards Framework | Yes (standards.py) | No |
| 18 | PO Governance | Partial (directives, gates) | No |
| 19 | Flow Validation | No (diagrams only) | No |
| 20 | AI Behavior | Partial (doctor, teaching) | No |
| 21 | Task Lifecycle Redesign | Yes (task_lifecycle.py) | No |
| 22 | Milestones | Tracking doc | — |
| 23 | Agent Lifecycle | Yes (agent_lifecycle.py) | No |
| 24 | Tool Call Tree Catalog | Partial (skill_enforcement.py) | No |
| 25 | Diagrams | Reference only | — |
| 26 | Unified Config Reference | Partial (config/*.yaml) | No |
| 27 | Evolution & Change Management | Process doc | — |
| 28 | Codebase Inventory | Reference only | — |
| 29 | Lessons Learned | Reference only | — |
| 30 | Strategy Synthesis | Planning doc | — |
| 31 | Transition Strategy | Planning doc | — |

### 28.2 Agent Rework (14 docs, 20 milestones)

| AR | Title | Code Exists? | Status |
|----|-------|-------------|--------|
| AR-01 | Fix preembed | Partial (preembed.py exists, not fully per-role) | PARTIALLY DONE |
| AR-02 | Wake PM | Yes (_wake_drivers in orchestrator) | IMPLEMENTED |
| AR-03 | Wake fleet-ops | Yes (_wake_drivers in orchestrator) | IMPLEMENTED |
| AR-04 | PM heartbeat rewrite | Custom HEARTBEAT.md exists | NOT PER SPEC |
| AR-05 | Fleet-ops heartbeat | Custom HEARTBEAT.md exists | NOT PER SPEC |
| AR-06 | Architect heartbeat | Custom HEARTBEAT.md exists | NOT PER SPEC |
| AR-07 | DevSecOps heartbeat | Custom HEARTBEAT.md exists | CLOSEST TO SPEC |
| AR-08 | Worker template | Template HEARTBEAT.md exists | FUNCTIONAL, NOT PER SPEC |
| AR-09 | Agent.yaml updates | All have agent.yaml | MISSING fleet_id, roles |
| AR-10 | Per-agent CLAUDE.md | All have CLAUDE.md | NOT PER SPEC (0/10 have anti-corruption) |
| AR-11 | Plane data for PM | Plane sync exists, not in PM pre-embed | NOT DONE |
| AR-12 | Artifact pre-embed | Artifact tracker exists, not in worker pre-embed | NOT DONE |
| AR-13 | Inter-agent comms | fleet_chat exists, not in heartbeat flows | PARTIAL |
| AR-14 | Standards in context | Standards exist, not injected per task type | NOT DONE |
| AR-15–20 | Live tests | — | NOT DONE (0/6) |

---

*End of Part 2. This document + Part 1 = complete verified system map.*
*Total: ~1190 lines across both files.*
*Next action: reconcile this map with implementation plan, then build.*