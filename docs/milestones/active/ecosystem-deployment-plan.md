# Ecosystem Deployment Plan — From Research to Reality

**Date:** 2026-04-01
**Status:** PLANNING — prioritized deployment of researched ecosystem
**Predecessor:** Research completed 2026-03-31 (session telemetry, LocalAI, OpenClaw, Claude plugins, model compression)

---

## 1. The Gap

We researched a massive ecosystem. We deployed almost none of it.

| Researched | Scale | Deployed |
|-----------|-------|---------|
| OpenClaw Skills Registry | 5,400+ skills | 1 pack (Anthropic) with 19 generic skills |
| Claude Code Plugins | 9,000+ plugins | 1 plugin (codex-plugin-cc) |
| MCP Server Registry | 1,000+ servers | 0 (only fleet MCP server) |
| Agent Teams (Swarm Mode) | Built into SDK | Not evaluated |
| Claude-Mem Plugin | Cross-session memory | Not installed |
| Context7 Plugin | Library documentation | Not installed |
| Prompt Caching | 90% savings | Not enabled |
| Batch API | 50% savings | Not used |
| LocalAI RAG Stack | CPU-only (zero GPU cost) | Not connected to fleet |
| LocalAI v4.0 Agents | Per-agent knowledge bases | Not evaluated |
| AICP RAG Pipeline | SQLite-backed, persist through docker | Not connected to fleet |

This document turns research into a deployment plan.

---

## 2. Deployment Tiers

### Tier 1: IMMEDIATE (Config/install only, no code changes)

These are settings or installs that provide value with near-zero risk.

| # | Item | What to Do | Savings/Impact | IaC |
|---|------|-----------|---------------|-----|
| E-01 | **Prompt Caching** | Enable `cacheRetention` in openclaw.json agent model configs | **90% savings on cached input tokens** | Config edit |
| E-02 | **Claude-Mem Plugin** | `claude plugin install claude-mem` per agent | Cross-session semantic memory for all agents | `scripts/install-plugins.sh` |
| E-03 | **Context7 Plugin** | `claude plugin install context7` for architect + engineer | Up-to-date framework/library docs in context | `scripts/install-plugins.sh` |
| E-04 | **Filesystem MCP** | Add `@modelcontextprotocol/server-filesystem` to agent mcp.json | Agents can read/write files properly | Per-agent mcp.json |

### Tier 2: SHORT-TERM (Evaluation + focused integration)

These need evaluation against our architecture before deployment.

| # | Item | What to Do | Impact | Depends On |
|---|------|-----------|--------|-----------|
| E-05 | **GitHub MCP Server** | Add `@modelcontextprotocol/server-github` for 5 agents | PR management, CI status, branch operations | Tier 1 mcp.json pattern |
| E-06 | **Playwright MCP** | Add `@playwright/mcp@latest` for engineer + QA + UX | Browser automation, UI testing, visual verification | Tier 1 mcp.json pattern |
| E-07 | **Docker MCP** | Add `@modelcontextprotocol/server-docker` for devops + devsecops | Container management, image inspection | Tier 1 mcp.json pattern |
| E-08 | **Per-Agent Skill Assignment** | Evaluate OpenClaw skills registry. Install domain-specific skills per role. | Each agent becomes specialist with right tools | config/agent-tooling.yaml |
| E-09 | **LocalAI RAG → Fleet** | Wire AICP's rag.py + kb.py into fleet agent context via MCP server | Agents query project knowledge at zero GPU cost | Custom MCP server |
| E-10 | **Batch API** | Route non-urgent work (documentation, analysis) through Batch API | **50% savings on async work** | API parameter per request |

### Tier 3: STRATEGIC (Architecture decisions required)

These change how the fleet operates fundamentally.

| # | Item | What to Do | Impact | Depends On |
|---|------|-----------|--------|-----------|
| E-11 | **Agent Teams (Swarm Mode)** | Evaluate `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` against current orchestrator | Inter-agent mailbox messaging, shared task lists | Architecture review |
| E-12 | **AICP ↔ Fleet Bridge** | Build router_unification.py bridge | Unified routing across both systems | router_unification schema |
| E-13 | **LocalAI v4.0 Agents** | Evaluate built-in agent system with per-agent KBs | May replace some fleet orchestration | Full architecture review |
| E-14 | **OpenRouter Free Tier** | Build client for 29 free models | Community-tier routing for simple tasks | OpenRouter client |
| E-15 | **Multi-Fleet Identity** | Deploy fleet-elevation/16 design | Fleet Alpha + Fleet Bravo coordination | Second machine |

---

## 3. Tier 1 Implementation Details

### E-01: Prompt Caching

**What:** Claude caches repeated prompt prefixes. When CLAUDE.md,
SOUL.md, and system instructions are the same across turns, the
cached portion costs 90% less.

**How:** Already partially configured in openclaw.json:
```json
"models": {
  "anthropic/claude-cli": {
    "params": {
      "cacheRetention": "short"
    }
  }
}
```

Need to verify this is active for all agents. May need `"cacheRetention": "long"` for persistent agents (PM, fleet-ops, devsecops) whose sessions last longer.

**IaC:** Update `~/.openclaw/openclaw.json` via setup script or `make configure-caching`.

**Risk:** None. This is a billing optimization with zero behavior change.

### E-02: Claude-Mem Plugin

**What:** Captures tool usage observations during sessions, generates
semantic summaries, injects relevant memories into future sessions.
Agents remember what they learned across session boundaries.

**How:**
```bash
# Per agent workspace
cd agents/{name}
claude plugin install claude-mem
```

**IaC:** `scripts/install-plugins.sh` iterates agents, installs Claude-Mem.

**Risk:** Low. Plugin adds memory injection to context — slightly
increases context size but provides cross-session continuity.

**Value:** Agents currently lose all session context on restart/prune.
Claude-Mem means: architect remembers codebase patterns from last session,
engineer remembers where they left off, QA remembers test patterns.

### E-03: Context7 Plugin

**What:** Provides up-to-date documentation for libraries and frameworks.
When architect or engineer references a library, Context7 injects
current docs instead of relying on LLM training data (which may be stale).

**How:**
```bash
cd agents/architect
claude plugin install context7
cd agents/software-engineer
claude plugin install context7
```

**IaC:** `scripts/install-plugins.sh` with per-agent plugin config.

**Value:** Prevents agents from using deprecated API patterns.
Especially valuable for: React/Radix (OCMC UI), Python libraries
(fleet framework), Docker/compose patterns.

### E-04: Filesystem MCP Server

**What:** Standard MCP server that provides file read/write/search
operations. Currently agents can only access files through Claude
Code's built-in tools — adding filesystem MCP gives structured
file operations with better error handling.

**How:** Per-agent mcp.json:
```json
{
  "mcpServers": {
    "fleet": { ... },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem",
               "/home/jfortin/openclaw-fleet"]
    }
  }
}
```

**IaC:** Generated from `config/agent-tooling.yaml` by `scripts/setup-agent-tools.sh`.

**Risk:** Low — read/write already available via Claude Code built-ins.
This adds structured operations with better feedback.

---

## 4. Tier 2 Implementation Details

### E-05: GitHub MCP Server

**Agents:** architect, software-engineer, devops, devsecops-expert, fleet-ops

Provides: PR creation/review, branch management, CI status, commit
history, issue tracking. Currently handled through `gh` CLI wrapper
in `fleet/infra/gh_client.py`. MCP server would give agents DIRECT
access to GitHub operations without fleet CLI abstraction.

**Evaluation needed:** Does GitHub MCP replace gh_client.py or complement it? Should agents have direct GitHub access or should it go through fleet tools?

### E-06: Playwright MCP

**Agents:** software-engineer, qa-engineer, ux-designer

Provides: browser automation, page navigation, element interaction,
screenshot capture, accessibility audit. Critical for:
- QA: automated UI testing, visual regression
- UX: accessibility verification, interaction flow testing
- Engineer: debugging UI issues, verifying implementations

**Evaluation needed:** Which test scenarios can use Playwright? How
does it integrate with challenge engine scenario tests?

### E-07: Docker MCP

**Agents:** devops, devsecops-expert

Provides: container listing, image inspection, log viewing, compose
management. Currently devops manages Docker through shell commands.
MCP server would give structured container operations.

### E-08: Per-Agent Skill Assignment

**Current state:** 19 generic skills installed gateway-wide. No per-agent
specialization. skill-assignments.yaml is documentary, not enforced.

**Target:** Each agent gets skills relevant to their domain:

| Agent | Skills to Evaluate |
|-------|-------------------|
| architect | architecture-propose, architecture-review, scaffold |
| software-engineer | feature-implement, debug, refactor-extract |
| qa-engineer | quality-coverage, quality-audit, foundation-testing |
| devops | foundation-docker, foundation-ci, ops-deploy |
| devsecops-expert | infra-security, quality-audit |
| technical-writer | feature-document, pm-changelog, pm-handoff |
| ux-designer | quality-accessibility |
| project-manager | pm-plan, pm-status-report, pm-retrospective |
| fleet-ops | pm-assess, quality-audit |

**Source:** Skills already exist in our skill library (`.claude/skills/`).
Many were created during this session. Need to evaluate which are
production-ready and install per agent.

### E-09: LocalAI RAG → Fleet

**What exists:**
- AICP: `rag.py` (SQLite vector store), `kb.py` (knowledge base with reranker), `stores.py` (LocalAI /stores/ API)
- LocalAI: `/v1/embeddings` (nomic-embed, CPU), `/v1/rerank` (bge-reranker, CPU), `/stores/` (vector similarity)
- All run on CPU simultaneously with GPU LLM — zero GPU cost for RAG

**Integration path:**
1. Create custom MCP server: `fleet-rag-server` that wraps AICP's kb.py
2. Register as MCP server per agent: agents query project knowledge
3. Ingest: design docs, code comments, architecture decisions → knowledge base
4. Query: before each task, relevant knowledge chunks injected into context

**Or simpler:** Add RAG query to context_assembly — orchestrator
queries KB during context refresh, includes relevant chunks in
pre-embedded context. No MCP server needed.

### E-10: Batch API

**What:** Claude's Batch API processes requests asynchronously at 50% cost.
Results available within 24 hours (usually faster).

**Fleet use cases:**
- Documentation generation (technical-writer) — not latency-sensitive
- Analysis documents (architect) — can wait for quality
- Security audit reports (devsecops) — thorough > fast
- Challenge reviews (cross-model) — batch multiple challenges

**Implementation:** API parameter on request: `batch: true`.
Budget mode determines: blitz/standard → real-time. Economic/frugal → batch.

---

## 5. Tier 3 Evaluation Criteria

### E-11: Agent Teams

**Question:** Does Agent Teams (swarm mode) replace our orchestrator?

| Feature | Fleet Orchestrator | Agent Teams |
|---------|-------------------|-------------|
| Coordination | Deterministic Python (30s cycle) | Lead agent + teammates |
| Communication | Board memory + @mentions | Mailbox messaging |
| Task management | OCMC tasks + custom fields | Shared task list |
| File isolation | Agent workspaces | Git worktrees per teammate |
| Quality gates | Fleet-ops review + challenge engine | TeammateIdle, TaskCompleted hooks |
| Cost control | Budget modes + storm prevention | Not built-in |

**Assessment:** Agent Teams provides inter-agent communication we DON'T
have (mailbox messaging). But our orchestrator provides cost control,
storm prevention, immune system, and methodology enforcement that
Agent Teams doesn't. Likely COMPLEMENT, not replace.

**Recommendation:** Enable Agent Teams for specific multi-agent tasks
(epic breakdowns where architect + engineer + QA collaborate) while
keeping the orchestrator for fleet-wide coordination.

### E-12: AICP ↔ Fleet Bridge

**When:** After LocalAI routing is tested and working independently.

**What:** `router_unification.py` schema exists. Bridge translates
fleet routing decisions into AICP router calls. AICP's router.py
routes to LocalAI. Result flows back through bridge.

### E-13: LocalAI v4.0 Agents

**When:** After evaluating current architecture stability.

**Risk:** LocalAI v4.0's built-in agent system may conflict with
our orchestrator. Need to determine: use LocalAI agents for simple
tasks (heartbeats, structured responses) and fleet orchestrator
for complex work? Or one system for everything?

---

## 6. IaC Plan

### New Scripts

```
scripts/
├── install-plugins.sh        Install Claude-Mem, Context7 per agent
├── setup-agent-tools.sh      Deploy per-agent mcp.json from config
├── configure-caching.sh      Enable prompt caching in openclaw.json
├── setup-rag-server.sh       Deploy RAG MCP server from AICP modules
└── evaluate-skills.sh        List available skills, compare to assignments
```

### New Config

```
config/
├── agent-tooling.yaml        Per-agent MCP servers, plugins, skills
├── ecosystem-status.yaml     Track what's deployed vs available
└── caching-config.yaml       Prompt caching settings per model
```

### New Makefile Targets

```makefile
# Tier 1
configure-caching:
	bash scripts/configure-caching.sh

install-plugins:
	bash scripts/install-plugins.sh

agent-setup:
	bash scripts/setup-agent-tools.sh $(AGENT)

agent-setup-all:
	@for agent in ...; do bash scripts/setup-agent-tools.sh $$agent; done

# Tier 2
setup-rag:
	bash scripts/setup-rag-server.sh

evaluate-skills:
	bash scripts/evaluate-skills.sh
```

---

## 7. Cost Impact Projection

| Mechanism | Savings | When Available | Status |
|-----------|---------|---------------|--------|
| Prompt caching (E-01) | **~90% on cached input** | Immediate | Config change |
| Batch API (E-10) | **~50% on async work** | Immediate | API parameter |
| Silent heartbeats | **~70% on idle agents** | Needs brain evaluation | Code needed |
| LocalAI routing | **~100% on simple tasks** | Needs AICP bridge | Code needed |
| Claude-Mem (E-02) | Reduces re-learning tokens | Immediate | Plugin install |
| Per-agent tools (E-04-07) | Reduces tool call failures | Short-term | Config |

**Conservative estimate:** Tier 1 alone (prompt caching + Claude-Mem)
could reduce fleet costs by **40-60%** without any code changes.

---

## 8. OCMC Skill Visibility

The PO noted that OCMC already has features for skill management:

> "OCMC already has some level of feature we can use to make visible
> and see to which agent the skills are installed... Packs with good
> classification and enhancement and then install to specific agents."

This means:
1. Skill packs registered in OCMC → visible which are available
2. Skill assignments per agent → visible which agent has which skills
3. Install status → confirm IaC matches reality
4. Classification → organize by domain (security, testing, docs, etc.)

The `config/skill-assignments.yaml` + `scripts/register-skill-packs.sh`
+ `scripts/install-skills.sh` infrastructure already exists for this.
It just needs to be extended with the evaluated ecosystem skills.

---

## 9. Deployment Order

```
Week 1: Tier 1 (immediate, zero risk)
  ├── E-01: Enable prompt caching → 90% savings
  ├── E-02: Install Claude-Mem → cross-session memory
  ├── E-03: Install Context7 → library docs for architect+engineer
  └── E-04: Filesystem MCP → structured file operations

Week 2-3: Tier 2 evaluation
  ├── E-05: Evaluate GitHub MCP → PR management
  ├── E-06: Evaluate Playwright MCP → UI testing
  ├── E-07: Evaluate Docker MCP → container ops
  ├── E-08: Evaluate + assign skills per agent
  └── E-09: Evaluate RAG integration path

Week 3-4: Tier 2 deployment
  ├── Deploy evaluated MCP servers per agent
  ├── Deploy per-agent skill assignments
  ├── Wire RAG into fleet context
  └── E-10: Enable Batch API for non-urgent work

Month 2+: Tier 3 strategic
  ├── E-11: Agent Teams evaluation + pilot
  ├── E-12: AICP ↔ Fleet bridge
  └── E-14: OpenRouter free tier client
```

---

## 10. Milestone Integration

These ecosystem deployments map to existing milestone framework:

| Ecosystem Item | Milestone | Wave |
|---------------|-----------|------|
| E-01 Prompt Caching | M-IP05 (Cost Optimization) | 11 |
| E-02 Claude-Mem | U-11 (Agent Memory Lifecycle) | Phase C |
| E-03 Context7 | U-10 (Agent Research Capability) | Phase C |
| E-04-07 MCP Servers | U-09 (Agent Self-Knowledge) | Phase C |
| E-08 Skills | M-TS02 (Skill Assignment) | 9 |
| E-09 RAG | M-KB01 (Connect AICP RAG) | 8 |
| E-10 Batch API | M-IP05 (Cost Optimization) | 11 |
| E-11 Agent Teams | M-AI03 (Communication Protocol) | 6 |
| E-12 AICP Bridge | M-IP03 (AICP ↔ Fleet Bridge) | 11 |
| E-14 OpenRouter | M-BR04 (OpenRouter Integration) | Wave 2 |

---

## 11. Success Criteria

### Tier 1 Success

- [ ] Prompt caching active for all agents (verify in billing)
- [ ] Claude-Mem installed and persisting memories across sessions
- [ ] Context7 providing library docs to architect and engineer
- [ ] Filesystem MCP responding to file operations
- [ ] Cost reduction measurable (before/after comparison)

### Tier 2 Success

- [ ] Per-agent mcp.json deployed with role-specific servers
- [ ] Skills assigned per role via config/agent-tooling.yaml
- [ ] RAG queries returning relevant context for agent tasks
- [ ] Batch API routing non-urgent work at 50% cost
- [ ] OCMC shows correct skill assignment per agent

### Tier 3 Success

- [ ] Agent Teams pilot completed for one multi-agent task
- [ ] AICP bridge routing simple tasks to LocalAI
- [ ] Architecture decision documented: complement vs replace
