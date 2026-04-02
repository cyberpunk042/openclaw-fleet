# Analysis 02 — Plugins Branch of the Knowledge Map

**Date:** 2026-04-02
**Status:** ANALYSIS — mapping all plugins into the knowledge tree
**Purpose:** Every plugin has a place in the map. Where each fits,
how it enhances the system, what it connects to, per role.

> Plugins are the DISTRIBUTION LAYER. They bundle skills, hooks,
> MCP servers, subagents, and LSP servers into installable units.
> Each plugin is a capability package in the tree.

---

## The Plugin Architecture

A Claude Code plugin can contain ANY combination of:
1. **Skills** — procedural knowledge (SKILL.md files)
2. **Agents** — specialized subagents
3. **Hooks** — lifecycle event handlers (deterministic)
4. **MCP Servers** — external tool connections
5. **LSP Servers** — language intelligence (diagnostics, navigation)

This makes plugins the most POWERFUL extension mechanism — they can
enhance at every layer simultaneously. A single plugin can add skills
AND hooks AND MCP tools.

---

## All Plugins Mapped to the Knowledge Tree

### Memory & Context Plugins

```
Plugin Manuals/
├── claude-mem/
│   ├── Source: github.com/thedotmack/claude-mem (45K stars)
│   ├── Type: Plugin with internal MCP server
│   ├── Components:
│   │   ├── 5 lifecycle hooks (SessionStart, UserPromptSubmit,
│   │   │   PostToolUse, Summary, SessionEnd)
│   │   ├── 4 MCP tools (search, timeline, get_observations, __IMPORTANT)
│   │   ├── Worker service (Express.js on port 37777)
│   │   └── Web UI (settings, memory stream visualization)
│   ├── What it provides:
│   │   ├── Captures EVERY tool execution automatically
│   │   ├── Compresses observations using Claude Agent SDK
│   │   ├── Stores in SQLite + ChromaDB (dual storage)
│   │   ├── Injects relevant context at session start
│   │   ├── 3-layer progressive search (10x token savings)
│   │   └── OpenClaw gateway integration (specific installer)
│   ├── Roles: ALL agents
│   ├── Stages: any (memory is cross-cutting)
│   ├── Enhancement:
│   │   ├── Cross-session continuity — agents retain knowledge across restarts
│   │   ├── Shared memory — agents share ~/.claude-mem/ database
│   │   ├── Reduced token usage — search instead of re-read
│   │   ├── Heartbeat context — recall without Claude costs (local SQLite)
│   │   └── Project-scoped recall — observations tagged by project
│   ├── Risks (WSL2 specific):
│   │   ├── CRITICAL: ChromaDB spawn storms (#1063) — 641 processes, 75% CPU
│   │   ├── CRITICAL: 35GB RAM consumption (#707)
│   │   ├── HIGH: No connection mutex — concurrent sessions race
│   │   └── MITIGATION: SQLite-only mode (loses semantic search, keeps FTS)
│   ├── Configuration:
│   │   ├── Install: /plugin install claude-mem OR OpenClaw installer
│   │   ├── Settings: ~/.claude-mem/settings.json
│   │   ├── REQUIRED: ANTHROPIC_API_KEY for observation compression
│   │   └── WSL2: Force SQLite-only mode in settings.json
│   ├── Connects to:
│   │   ├── → Knowledge map (map indexes claude-mem observations)
│   │   ├── → LightRAG (semantic search layer — complements SQLite FTS)
│   │   ├── → Session manager (brain Step 10 — context recovery after compact)
│   │   ├── → Agent MEMORY.md (.claude/memory/ — different system, complementary)
│   │   ├── → Heartbeat gate (recall without Claude cost)
│   │   ├── → Trail system (observations become searchable trail)
│   │   └── → Pre-embed (inject relevant memories into context)
│   └── Compared to built-in .claude/memory/:
│       Built-in = lightweight, reliable, free, git-tracked, 200-line cap
│       claude-mem = heavy, searchable, costs tokens, scales to thousands
│       They are COMPLEMENTARY. Built-in for preferences. claude-mem for recall.
│
├── total-recall/
│   ├── Source: github.com/davegoldblatt/total-recall (189 stars)
│   ├── Type: Plugin with tiered memory
│   ├── What it provides:
│   │   ├── Write gates (controlled what gets stored)
│   │   ├── Correction propagation (updates cascade through memory)
│   │   ├── Tiered storage (hot/warm/cold)
│   │   └── Lighter weight than claude-mem
│   ├── Roles: ALL agents
│   ├── Enhancement: Alternative memory architecture.
│   │   Write gates prevent garbage memory accumulation.
│   │   Correction propagation keeps memory accurate.
│   │   Tiered approach matches fleet context strategy (hot/warm/cold/frozen).
│   ├── Connects to:
│   │   → claude-mem (alternative approach to same problem)
│   │   → Board memory retention strategy (§62.3 — hot/warm/cold/frozen)
│   │   → Knowledge map (tiered access model)
│   └── Status: Alternative to claude-mem — evaluate if claude-mem's
│       WSL2 issues prove unmanageable even in SQLite-only mode.
│
├── memsearch/
│   ├── Source: github.com/zilliztech/memsearch (1K stars)
│   ├── Type: Markdown-first memory system
│   ├── What it provides:
│   │   ├── Markdown files as memory storage (git-trackable)
│   │   ├── Inspired by OpenClaw architecture
│   │   ├── Simpler than claude-mem (no ChromaDB, no worker service)
│   │   └── File-based = portable, shareable, version-controlled
│   ├── Roles: ALL agents
│   ├── Enhancement: Git-tracked memory that survives Docker purges.
│   │   Aligns with our "IaC — everything persists in git" philosophy.
│   │   Simpler operational model than claude-mem.
│   ├── Connects to:
│   │   → Built-in .claude/memory/ (similar philosophy, different implementation)
│   │   → Knowledge map (markdown content indexed by map)
│   │   → IaC scripts (memory as committed files)
│   └── Status: Alternative approach — markdown vs database.
│
├── ars-contexta/
│   ├── Source: github.com/agenticnotetaking/arscontexta (3K stars)
│   ├── Type: Knowledge system generator
│   ├── What it provides:
│   │   ├── Generates individualized knowledge systems from conversation
│   │   ├── "Second brain" as organized markdown files
│   │   ├── Captures patterns, decisions, rationale
│   │   └── Self-organizing knowledge structure
│   ├── Roles: ARCH, PM, WRITER, FLEET-OPS
│   ├── Enhancement: Automated knowledge base construction.
│   │   Agent conversations → organized knowledge.
│   │   Could feed into knowledge map's agent manuals.
│   │   Captures the "tribal knowledge" that normally gets lost.
│   ├── Connects to:
│   │   → Knowledge map (agent manuals built from captured knowledge)
│   │   → LightRAG (knowledge indexed for graph queries)
│   │   → pm-handoff skill (handoff = knowledge transfer)
│   └── Status: Interesting for knowledge capture.
│       Evaluate if knowledge map construction can use this approach.
│
└── pro-workflow/
    ├── Source: github.com/rohitg00/pro-workflow (2K stars)
    ├── Type: Self-correcting memory + workflow
    ├── What it provides:
    │   ├── Memory compounds over 50+ sessions
    │   ├── Context engineering (smart context management)
    │   ├── Parallel worktrees with Agent Teams
    │   ├── 17 skills for senior development
    │   └── Self-correcting — learns from mistakes
    ├── Roles: ENG (senior), ARCH
    ├── Enhancement: Long-term learning from experience.
    │   Memory improves with use — agent gets better over time.
    │   Self-correction aligns with our immune system concept.
    ├── Connects to:
    │   → Doctor/immune system (self-correction pattern)
    │   → Agent Teams (parallel worktree workflows)
    │   → claude-mem (complementary memory layer)
    └── Status: Advanced memory architecture for experienced agents.
```

### Methodology & Development Plugins

```
Plugin Manuals/
├── superpowers/
│   ├── Source: github.com/obra/superpowers (132K stars)
│   ├── Type: Complete development methodology plugin
│   ├── Components:
│   │   ├── 14 core skills (brainstorming, TDD, plans, debugging, etc.)
│   │   ├── 5 experimental skills (in superpowers-lab)
│   │   ├── Mandatory skill triggers (not suggestions — enforcement)
│   │   └── Official Anthropic marketplace member
│   ├── What it provides:
│   │   ├── brainstorming — Socratic design refinement BEFORE code
│   │   ├── writing-plans — 2-5 minute tasks with exact file paths
│   │   ├── executing-plans — batch execution with human checkpoints
│   │   ├── test-driven-development — TRUE TDD (deletes code before tests)
│   │   ├── subagent-driven-development — fresh context per task, 2-stage review
│   │   ├── systematic-debugging — 4-phase root cause process
│   │   ├── verification-before-completion — ensures actually fixed
│   │   ├── requesting-code-review — pre-review checklist
│   │   ├── receiving-code-review — structured feedback response
│   │   ├── using-git-worktrees — parallel development
│   │   ├── finishing-a-development-branch — merge/PR decisions
│   │   ├── dispatching-parallel-agents — concurrent subagent work
│   │   ├── writing-skills — meta-skill for creating skills
│   │   └── using-superpowers — introduction
│   ├── Roles: ALL development agents (ENG, ARCH, QA, DEVOPS, DEVSEC)
│   ├── Stages: ALL — methodology is cross-cutting
│   ├── Enhancement:
│   │   ├── Adds the HOW to our WHAT — we say "implement feature,"
│   │   │   Superpowers says "brainstorm → plan → TDD → verify → review"
│   │   ├── TDD enforcement — most impactful quality improvement
│   │   ├── Plan specificity — "clear enough for enthusiastic junior dev"
│   │   ├── Subagent dispatch — maps to our fleet agent model
│   │   ├── Most starred plugin in entire ecosystem (132K)
│   │   └── Battle-tested at scale
│   ├── Adaptation needed:
│   │   ├── Assumes autonomous multi-hour execution
│   │   ├── Fleet has "one step, wait for approval" guardrails
│   │   ├── Need to throttle autonomy level per fleet control model
│   │   └── Cherry-pick methodology skills vs install whole plugin
│   ├── Connects to:
│   │   ├── → Our 5-stage methodology (conversation→work) — LAYERS on top
│   │   ├── → Stage instructions (stage_context.py) — complementary
│   │   ├── → fleet_task_complete (verification + review before completion)
│   │   ├── → Agent Teams (subagent-driven-development maps to dispatch)
│   │   ├── → /plan command (writing-plans is the deep version)
│   │   ├── → /debug command (systematic-debugging is the deep version)
│   │   ├── → quality-coverage skill (TDD enforces test-first)
│   │   ├── → feature-implement skill (plans drive implementation)
│   │   └── → Anti-corruption (structural prevention through methodology)
│   └── Key consideration: Superpowers' methodology + our stage protocol
│       + fleet control guardrails = THREE layers of process enforcement.
│       Together they create the most rigorous agent development workflow
│       in the ecosystem. Separately they each have gaps.
│
├── claude-skills/
│   ├── Source: github.com/alirezarezvani/claude-skills (9K stars)
│   ├── Type: 223 role-based expert persona skills
│   ├── Components:
│   │   ├── 36 Engineering Core skills
│   │   ├── 36 Engineering POWERFUL skills
│   │   ├── 14 Product skills
│   │   ├── 43 Marketing skills (8 pods)
│   │   ├── 8 Project Management skills
│   │   ├── 14 Regulatory/QM skills
│   │   ├── 28 C-Level Advisory skills
│   │   ├── 4 Business Growth skills
│   │   ├── 3 Finance skills
│   │   ├── 23 specialized agents
│   │   ├── 3 personas
│   │   ├── 22 slash commands
│   │   └── 298 Python tools (stdlib-only)
│   ├── What it provides (fleet-relevant highlights):
│   │   ├── agent-designer — designs agent architectures
│   │   ├── agent-workflow-designer — designs agent workflows
│   │   ├── rag-architect — designs RAG systems
│   │   ├── mcp-server-builder — builds MCP servers
│   │   ├── skill-security-auditor — scans skills for malicious code
│   │   ├── pr-review-expert — deep PR review methodology
│   │   ├── tech-debt-tracker — systematic debt tracking
│   │   ├── observability-designer — monitoring/alerting design
│   │   ├── incident-commander — incident response leadership
│   │   ├── senior-architect — deep architecture expertise
│   │   ├── senior-devops — deep DevOps expertise
│   │   ├── senior-secops — deep security operations
│   │   ├── senior-qa — deep QA expertise
│   │   ├── playwright-pro (9 sub-skills) — deep browser testing
│   │   ├── tdd-guide — TDD methodology
│   │   └── self-improving-agent (5 sub-skills) — agent that improves itself
│   ├── Roles: role-specific (see mapping below)
│   │   ARCH: agent-designer, rag-architect, senior-architect
│   │   DEVSEC: senior-secops, skill-security-auditor, incident-commander
│   │   ENG: mcp-server-builder, self-improving-agent
│   │   QA: senior-qa, playwright-pro, tdd-guide
│   │   DEVOPS: senior-devops, observability-designer
│   │   FLEET-OPS: pr-review-expert, incident-commander
│   │   PM: senior-pm, scrum-master, agile-product-owner
│   │   ACCT: tech-debt-tracker
│   ├── Enhancement: EXPERT DEPTH per role.
│   │   Our skills say WHAT to do. These define WHO the agent IS
│   │   as a professional. "Senior architect" isn't just a label —
│   │   it's 200+ lines of deep domain expertise, patterns, and judgment.
│   ├── Connects to:
│   │   ├── → Agent IDENTITY.md (expert persona definition)
│   │   ├── → Agent CLAUDE.md (role-specific rules from expert knowledge)
│   │   ├── → Knowledge map agent manuals (expert voice per role)
│   │   ├── → Contribution system (expert contributes expert-level input)
│   │   └── → Anti-corruption §40 (top-tier expert definition)
│   └── Key consideration: quality over quantity. The POWERFUL tier
│       (36 skills) is genuinely deep. The rest varies. Cherry-pick
│       the domain-expert skills relevant to each fleet role.
│
├── plugins-plus-skills/
│   ├── Source: github.com/jeremylongshore/claude-code-plugins-plus-skills (2K stars)
│   ├── Type: 2,811 skills + 415 plugins + 154 agents
│   ├── Package manager: ccpi CLI (npm: @intentsolutionsio/ccpi)
│   ├── Organization: 20 skill packs × 25 skills each + SaaS packs
│   ├── What it provides:
│   │   ├── Atomic task generators (dockerfile-generator, helm-chart-generator)
│   │   ├── 20 domain categories (DevOps, Security, Frontend, Backend,
│   │   │   ML, Testing, Data, AWS, GCP, API, Docs, Visual, Business)
│   │   ├── 111 SaaS integration packs (LangChain, Linear, Stripe, etc.)
│   │   ├── Learning Lab (90+ pages of agent workflow guides)
│   │   └── 9 MCP server plugins (TypeScript)
│   ├── Roles: varies by pack
│   │   DEVOPS: packs 01-02 (DevOps Basic/Advanced)
│   │   DEVSEC: packs 03-04 (Security Fundamental/Advanced)
│   │   ENG: packs 05-06 (Frontend/Backend)
│   │   QA: packs 09-10 (Test Automation/Performance)
│   │   PM: packs 19-20 (Business Automation/Enterprise)
│   ├── Enhancement: BREADTH of atomic operations.
│   │   Need a Dockerfile? dockerfile-generator.
│   │   Need a Helm chart? helm-chart-generator.
│   │   Need GitHub Actions? github-actions-starter.
│   │   Task-specific generators for rapid artifact creation.
│   ├── Connects to:
│   │   ├── → Foundation skills (foundation-docker, foundation-ci)
│   │   ├── → Task generators in knowledge map
│   │   └── → Per-role tool recommendations
│   └── Key consideration: quantity over quality. 2,811 skills are
│       formulaic (25 per category). Cherry-pick specific generators
│       per role rather than installing everything.
│
├── feature-dev/
│   ├── Source: Official Anthropic
│   ├── Type: Guided feature development
│   ├── Components:
│   │   ├── code-explorer agent
│   │   ├── code-architect agent
│   │   └── code-reviewer agent
│   ├── Roles: ARCH, ENG
│   ├── Enhancement: 3-agent workflow for feature development.
│   │   Explorer discovers codebase → architect designs → reviewer validates.
│   │   Agent pipeline approach.
│   ├── Connects to:
│   │   → Our 5-stage methodology (similar but different structure)
│   │   → Superpowers (complementary workflow approach)
│   └── Status: Official plugin — high quality, different approach.
│
└── adversarial-spec/
    ├── Source: github.com/zscole/adversarial-spec (518 stars)
    ├── Type: Multi-LLM debate for spec refinement
    ├── What it provides:
    │   ├── Multiple LLMs debate a specification
    │   ├── Iterative refinement until consensus
    │   ├── Challenges assumptions and design decisions
    │   └── Devil's advocate built into the design process
    ├── Roles: ARCH, PM
    ├── Stages: reasoning (spec refinement), analysis (design critique)
    ├── Enhancement: Adversarial design process.
    │   Specifications get CHALLENGED before implementation.
    │   Prevents groupthink in architecture decisions.
    │   Multiple perspectives on every design choice.
    ├── Connects to:
    │   ├── → Codex adversarial-review (review-time vs design-time)
    │   ├── → Challenge system (adversarial validation)
    │   ├── → Architecture-review skill
    │   ├── → brainstorming skill (Superpowers — explore before deciding)
    │   └── → Contribution system (architect gets multiple viewpoints)
    └── Status: Interesting for architecture decisions.
        Requires multiple LLM backends — maps to our multi-backend vision.
```

### Safety & Security Plugins

```
Plugin Manuals/
├── safety-net/
│   ├── Source: github.com/kenryu42/claude-code-safety-net (1K stars)
│   ├── Type: PreToolUse hook plugin
│   ├── Components:
│   │   └── Single hook: PreToolUse with destructive command detection
│   ├── What it provides:
│   │   ├── Catches destructive git commands (reset --hard, push --force, etc.)
│   │   ├── Catches destructive filesystem commands (rm -rf, etc.)
│   │   ├── Warns BEFORE execution — agent can reconsider
│   │   └── Passive — no performance impact, only fires on match
│   ├── Roles: ALL agents
│   ├── Stages: any (protection is always on)
│   ├── Enhancement: STRUCTURAL PREVENTION.
│   │   This is Line 1 anti-corruption implemented as a hook.
│   │   Agents physically CANNOT execute destructive commands
│   │   without passing through the safety gate.
│   │   Most important safety mechanism available.
│   ├── Connects to:
│   │   ├── → Anti-corruption Line 1 (§39.2) — structural prevention
│   │   ├── → PreToolUse hook (our hook analysis — Tier 1)
│   │   ├── → Agent permissions (§53)
│   │   ├── → Doctor immune system (catch what safety-net misses)
│   │   ├── → Trail system (blocked commands recorded)
│   │   └── → PO guardrails ("preserve working state")
│   └── Key consideration: should be on EVERY agent. Zero downside.
│       Prevents the exact class of accidents that cause data loss.
│
├── security-guidance/
│   ├── Source: Official Anthropic
│   ├── Type: Hook-based security pattern monitoring
│   ├── Components:
│   │   └── Hook monitoring 9 security patterns
│   ├── What it provides:
│   │   ├── Detects: command injection, XSS, eval usage
│   │   ├── Detects: dangerous HTML, pickle deserialization
│   │   ├── Detects: os.system usage, credential exposure
│   │   ├── Real-time monitoring as agent writes code
│   │   └── Warns when security anti-patterns detected
│   ├── Roles: ALL agents (but primarily DEVSEC, ENG)
│   ├── Stages: work (code writing)
│   ├── Enhancement: Security as continuous monitoring, not checkpoint.
│   │   Aligns with DevSecOps philosophy — security is a LAYER.
│   │   Catches OWASP top 10 patterns as agent writes code.
│   ├── Connects to:
│   │   ├── → DevSecOps CLAUDE.md (security layer concept)
│   │   ├── → infra-security skill
│   │   ├── → behavioral_security.py (our security scanner)
│   │   ├── → PostToolUse hook (security check after every edit)
│   │   └── → Anti-corruption (security disease prevention)
│   └── Key consideration: complements safety-net.
│       safety-net catches destructive commands.
│       security-guidance catches insecure code patterns.
│       Together = comprehensive security hook layer.
│
├── sage/
│   ├── Source: github.com/gendigitalinc/sage (162 stars)
│   ├── Type: Agent Detection and Response (ADR) layer
│   ├── What it provides:
│   │   ├── Guards against dangerous commands
│   │   ├── Guards file access (prevent unauthorized reads/writes)
│   │   ├── Guards web requests (prevent data exfiltration)
│   │   ├── Policy-based enforcement
│   │   └── ADR concept (like EDR for agents)
│   ├── Roles: ALL agents (security infrastructure)
│   ├── Enhancement: ADR is a new security category.
│   │   Like Endpoint Detection and Response (EDR) but for AI agents.
│   │   Policy-driven — PO defines what agents can/can't do.
│   │   Goes beyond safety-net into comprehensive agent security.
│   ├── Connects to:
│   │   ├── → safety-net (sage is more comprehensive)
│   │   ├── → Agent permissions (§53 — formalized permission matrix)
│   │   ├── → Anti-corruption (structural enforcement)
│   │   ├── → behavioral_security.py (complementary)
│   │   └── → Doctor immune system
│   └── Status: Advanced security — evaluate after safety-net deployed.
│
└── code-container/
    ├── Source: github.com/kevinMEH/code-container (202 stars)
    ├── Type: Container isolation for agent execution
    ├── What it provides:
    │   ├── Run agents with full permissions INSIDE containers
    │   ├── Container boundary = security isolation
    │   ├── Agent can't escape sandbox
    │   └── Full capability without risk to host
    ├── Roles: ALL agents (security infrastructure)
    ├── Enhancement: Solves the bypassPermissions problem.
    │   Currently all agents run bypassPermissions on host.
    │   Container isolation gives full permissions SAFELY.
    │   Agent does anything inside container, nothing outside.
    ├── Connects to:
    │   ├── → Agent permissions (§53 — bypassPermissions concern)
    │   ├── → Docker MCP (container management)
    │   ├── → Gateway session management
    │   └── → Multi-fleet security (isolate fleet from host)
    └── Status: Architectural consideration for fleet security model.
```

### Quality & Review Plugins

```
Plugin Manuals/
├── codex-plugin-cc/
│   ├── Source: github.com/openai/codex-plugin-cc (11K stars)
│   ├── Type: Cross-provider bridge plugin
│   ├── Components:
│   │   ├── 7 slash commands (/codex:setup, :review, :adversarial-review,
│   │   │   :rescue, :status, :result, :cancel)
│   │   ├── Review gate (Stop hook — independent review before completion)
│   │   ├── codex-rescue subagent (task delegation)
│   │   └── Background job management
│   ├── What it provides:
│   │   ├── INDEPENDENT AI reviews work from DIFFERENT provider
│   │   ├── Adversarial review challenges design decisions
│   │   ├── Task delegation to Codex for complex subtasks
│   │   ├── Review gate blocks completion until Codex approves
│   │   └── CAN point at LocalAI via config.toml
│   ├── Roles: FLEET-OPS (review), DEVSEC (security review), ARCH (design challenge)
│   ├── Enhancement:
│   │   ├── Cross-provider validation — genuine second opinion
│   │   ├── Review gate PATTERN is most valuable concept
│   │   ├── Adversarial review from different AI perspective
│   │   ├── Task rescue for complex/stuck subtasks
│   │   └── LocalAI as codex backend = free adversarial review (quality TBD)
│   ├── Risks:
│   │   ├── Adds OpenAI API costs alongside Claude
│   │   ├── Review gate can create runaway loops (drain both providers)
│   │   ├── Sandbox restriction bug (#18 — bwrap failure)
│   │   ├── Review gate state mismatch bug (#59)
│   │   └── Small model quality for adversarial review (3B/7B)
│   ├── Connects to:
│   │   ├── → Fleet-ops 7-step review (codex as additional review layer)
│   │   ├── → Challenge system (cross-model challenge type)
│   │   ├── → codex_review.py (existing fleet module)
│   │   ├── → Multi-backend router (OpenAI as additional backend)
│   │   ├── → LocalAI independence (can route codex to local model)
│   │   ├── → Anti-corruption (independent verification)
│   │   └── → Stop hook (review gate = hook-based quality gate)
│   └── Key insight: The PATTERN matters more than the plugin.
│       The Stop hook → independent review → block if issues concept
│       can be implemented natively with our own infrastructure.
│       The plugin is valuable when genuine cross-PROVIDER validation needed.
│
├── pr-review-toolkit/
│   ├── Source: Official Anthropic
│   ├── Type: Multi-agent PR review plugin
│   ├── Components:
│   │   └── /pr-review-toolkit:review-pr command
│   │       spawns 5 parallel Sonnet agents for review
│   ├── What it provides:
│   │   ├── CLAUDE.md compliance checking
│   │   ├── Bug detection
│   │   ├── Historical context analysis
│   │   ├── PR history review
│   │   └── Code comment generation
│   ├── Roles: FLEET-OPS, QA
│   ├── Enhancement: 5-ANGLE review from 5 parallel agents.
│   │   Each agent focuses on ONE aspect — depth through specialization.
│   │   More thorough than single-agent review.
│   │   Catches what a single reviewer misses.
│   ├── Connects to:
│   │   ├── → Fleet-ops 7-step review (enhanced review depth)
│   │   ├── → fleet-review skill (complementary checklist + multi-agent)
│   │   ├── → Challenge system (multi-angle validation)
│   │   ├── → Agent Teams (parallel agent concept)
│   │   └── → LaborStamp (review signature with multi-agent evidence)
│   └── Key consideration: 5x token cost per review.
│       Worth it for critical code. Overkill for routine changes.
│       Could be selective — trigger on SP ≥ 5 or security-flagged.
│
├── claude-octopus/
│   ├── Source: github.com/nyldn/claude-octopus (2K stars)
│   ├── Type: Multi-model review plugin
│   ├── What it provides:
│   │   ├── Up to 8 different AI models review the same code
│   │   ├── Surfaces blind spots by comparing diverse perspectives
│   │   ├── Each model brings different strengths/weaknesses
│   │   └── Consensus-based quality assessment
│   ├── Roles: FLEET-OPS, QA, ARCH
│   ├── Enhancement: MAXIMUM review diversity.
│   │   8 AI models = 8 perspectives = maximum coverage.
│   │   Catches model-specific blind spots.
│   │   Directly maps to our multi-backend architecture
│   │   (Claude + LocalAI + OpenRouter = multiple models available).
│   ├── Connects to:
│   │   ├── → Multi-backend router (8 models from our backend pool)
│   │   ├── → Challenge system (cross-model challenge type)
│   │   ├── → codex-plugin-cc (cross-provider review subset)
│   │   ├── → Fleet-ops review (multi-model enhancement)
│   │   └── → LocalAI (free models as additional reviewers)
│   └── Status: Advanced — depends on having multiple model backends.
│       Value increases as our multi-backend routing matures.
│
└── commit-commands/
    ├── Source: Official Anthropic
    ├── Type: Git commit workflow plugin
    ├── Components:
    │   └── /commit-commands:commit command
    ├── What it provides:
    │   ├── Structured commit workflow
    │   ├── Push to remote
    │   └── PR creation
    ├── Roles: ALL dev agents
    ├── Enhancement: Standardized commit workflow.
    │   Consistent conventional commit format.
    │   Automated PR creation.
    ├── Connects to:
    │   ├── → fleet_commit MCP tool (complementary)
    │   ├── → fleet_task_complete (PR creation step)
    │   ├── → Git workflow (§65)
    │   └── → Trail system (commit events)
    └── Status: Overlaps with fleet_commit functionality.
        Evaluate if it adds value beyond our MCP tools.
```

### Orchestration & Agent Management Plugins

```
Plugin Manuals/
├── ruflo/
│   ├── Source: github.com/ruvnet/ruflo (29K stars, formerly Claude Flow)
│   ├── Type: Multi-agent swarm orchestration platform
│   ├── What it provides:
│   │   ├── Deploy intelligent agent swarms
│   │   ├── RAG integration
│   │   ├── Native Claude Code + Codex integration
│   │   ├── Enterprise-grade orchestration
│   │   └── Swarm communication patterns
│   ├── Roles: FLEET-OPS, ARCH
│   ├── Enhancement: Alternative orchestration model.
│   │   Swarm approach vs our centralized orchestrator.
│   │   RAG integration could inform our LightRAG work.
│   │   Enterprise patterns for fleet scaling.
│   ├── Connects to:
│   │   ├── → Our orchestrator.py (different approach to same problem)
│   │   ├── → Agent Teams (complementary multi-agent model)
│   │   ├── → LightRAG (RAG integration patterns)
│   │   └── → Multi-fleet architecture (swarm at scale)
│   └── Status: Study for architectural patterns.
│       We have our own orchestrator — won't replace it.
│       But swarm communication patterns may inform design.
│
├── agents-plugin/
│   ├── Source: github.com/wshobson/agents (33K stars)
│   ├── Type: Multi-agent orchestration for Claude Code
│   ├── What it provides:
│   │   ├── Intelligent automation
│   │   ├── Multi-agent coordination
│   │   └── Task distribution patterns
│   ├── Roles: FLEET-OPS
│   ├── Enhancement: Alternative agent coordination model.
│   ├── Connects to:
│   │   ├── → Our orchestrator (different approach)
│   │   ├── → Agent Teams (complementary)
│   │   └── → Dispatch system
│   └── Status: Study for patterns. We have our own orchestration.
│
├── harness/
│   ├── Source: github.com/revfactory/harness (2K stars)
│   ├── Type: Meta-skill — designs domain-specific agent teams
│   ├── What it provides:
│   │   ├── Designs specialized agent teams for any domain
│   │   ├── Defines agent roles and capabilities
│   │   ├── Generates skills for designed agents
│   │   └── Agent architecture as a SERVICE
│   ├── Roles: ARCH, FLEET-OPS
│   ├── Enhancement: Agent team design tool.
│   │   Could help design new fleet agent roles.
│   │   Generates role-specific skills automatically.
│   │   "What should agent X look like?" as a tool.
│   ├── Connects to:
│   │   ├── → Agent manual creation (knowledge map)
│   │   ├── → scaffold-subagent skill
│   │   ├── → agent-designer skill (alirezarezvani)
│   │   └── → Fleet architecture evolution
│   └── Status: Interesting for fleet architecture design.
│
├── orchestrator-supaconductor/
│   ├── Source: github.com/Ibrahim-3d/orchestrator-supaconductor (303 stars)
│   ├── Type: Multi-agent + quality gates + Board of Directors
│   ├── What it provides:
│   │   ├── Parallel multi-agent execution
│   │   ├── Quality gates between stages
│   │   ├── "Board of Directors" pattern (collective decision-making)
│   │   ├── Bundled Superpowers skills
│   │   └── Orchestration patterns
│   ├── Roles: FLEET-OPS, ARCH
│   ├── Enhancement: Board of Directors concept.
│   │   Multiple agents make collective decisions.
│   │   Quality gates align with our readiness gates.
│   │   Combines orchestration with Superpowers methodology.
│   ├── Connects to:
│   │   ├── → Our orchestrator (Board of Directors pattern)
│   │   ├── → Gate system (quality gates concept)
│   │   ├── → Superpowers (bundled, complementary)
│   │   ├── → Challenge system (collective validation)
│   │   └── → Fleet-ops review (multi-agent approval)
│   └── Status: Study for Board of Directors pattern.
│
└── plan-cascade/
    ├── Source: github.com/Taoidle/plan-cascade (149 stars)
    ├── Type: Cascading task decomposition
    ├── What it provides:
    │   ├── Decompose complex projects into parallel tasks
    │   ├── Auto-generated PRDs per subtask
    │   ├── Cascading execution (parent → children)
    │   └── Parallel task distribution
    ├── Roles: PM, ARCH
    ├── Enhancement: Task decomposition automation.
    │   Complex project → parallel workstreams.
    │   PRD generation per subtask (documentation built-in).
    │   Cascading pattern matches our epic → subtask model.
    ├── Connects to:
    │   ├── → fleet-plan skill (break epic into sprint tasks)
    │   ├── → PM heartbeat (task decomposition)
    │   ├── → Contribution system (parallel subtasks)
    │   └── → Agent dispatch (parallel execution)
    └── Status: Task decomposition patterns relevant to PM workflow.
```

### Development Workflow Plugins (Official Anthropic)

```
Plugin Manuals/
├── hookify/
│   ├── Source: Official Anthropic
│   ├── What it provides:
│   │   ├── Create hooks from natural language
│   │   ├── "Warn me when I use rm -rf" → working PreToolUse hook
│   │   ├── Lowers barrier to hook creation
│   │   └── Agents could create their own protective hooks
│   ├── Roles: DEVOPS, FLEET-OPS, ALL
│   ├── Enhancement: Democratizes hook creation.
│   │   Agents or PO can create custom hooks in plain English.
│   ├── Connects to:
│   │   ├── → Hook infrastructure (HK-001 to HK-008)
│   │   ├── → safety-net (hookify can generate similar hooks)
│   │   └── → Anti-corruption (custom enforcement hooks)
│
├── plugin-dev/
│   ├── Source: Official Anthropic
│   ├── What it provides:
│   │   ├── 8-phase guided plugin creation workflow
│   │   ├── /plugin-dev:create-plugin command
│   │   ├── 7 expert skills for plugin building
│   │   └── Official Anthropic methodology for plugins
│   ├── Roles: ARCH, ENG (for building fleet plugins)
│   ├── Enhancement: If we want to BUILD our own plugins
│   │   (rather than just install others), this is the guide.
│   │   8-phase process ensures quality.
│   ├── Connects to:
│   │   ├── → Knowledge map plugin (could be a custom plugin)
│   │   ├── → Fleet-specific hooks (could be packaged as plugin)
│   │   └── → mcp-server-builder skill (build custom MCP servers)
│
└── pyright-lsp/
    ├── Source: Official Anthropic (claude-plugins-official)
    ├── Type: LSP plugin for Python type checking
    ├── Components:
    │   └── LSP server: pyright-langserver (continuous background process)
    ├── What it provides:
    │   ├── Automatic type error detection after every edit
    │   ├── Code navigation (jump to def, find references)
    │   ├── Type information on hover
    │   ├── Import resolution
    │   └── Continuous diagnostics (no manual trigger needed)
    ├── Roles: ALL Python agents (ENG, ARCH, QA, DEVOPS, DEVSEC)
    ├── Enhancement: CONTINUOUS code intelligence.
    │   Agent gets type errors AUTOMATICALLY after every edit.
    │   No need to run mypy/pyright manually.
    │   Navigation tools help understand unfamiliar code.
    │   OUR ENTIRE CODEBASE IS PYTHON — directly relevant.
    ├── Prerequisite: pyright binary (npm i -g pyright)
    ├── Connects to:
    │   ├── → quality-lint skill (type checking is linting)
    │   ├── → feature-implement (catch type errors during impl)
    │   ├── → PostToolUse hook (diagnostics after every edit)
    │   ├── → Anti-corruption (type system prevents wrong code)
    │   └── → challenge system (automated type check challenge)
    └── Key consideration: EVERY Python agent benefits.
        Zero downside beyond pyright binary installation.
        Catches errors that would otherwise reach review.
```

---

## How Plugins Connect to Other Map Branches

| Plugin Category | Connects To |
|----------------|------------|
| Memory (claude-mem, total-recall, memsearch) | → Knowledge map, → LightRAG, → Session manager, → Agent memory |
| Methodology (Superpowers, feature-dev) | → Stage protocol, → Skills, → Commands (/plan, /debug), → Anti-corruption |
| Expert personas (claude-skills) | → Agent IDENTITY.md, → Agent CLAUDE.md, → Contribution system |
| Safety (safety-net, security-guidance, sage) | → Hooks (PreToolUse), → Anti-corruption Line 1, → Permissions |
| Review (codex, pr-review-toolkit, octopus) | → Fleet-ops review, → Challenge system, → Multi-backend router |
| Orchestration (Ruflo, agents, harness) | → Our orchestrator, → Agent Teams, → Dispatch system |
| Code intelligence (pyright-lsp) | → Quality skills, → Feature implementation, → PostToolUse hook |
| Task management (plan-cascade, commit-commands) | → PM workflow, → fleet_commit, → Sprint management |

---

## PO Decision Points

1. **claude-mem configuration:** SQLite-only mode confirmed for WSL2? Or evaluate total-recall/memsearch as alternatives?
2. **Superpowers adoption strategy:** Install whole plugin and adapt autonomy? Cherry-pick methodology skills? Layer alongside our 5-stage protocol?
3. **safety-net:** Confirm install on ALL agents?
4. **pyright-lsp:** Confirm install on ALL Python agents?
5. **security-guidance:** Install alongside safety-net for dual protection (commands + code patterns)?
6. **codex-plugin-cc:** Budget decision — OpenAI costs? Or implement review gate pattern natively?
7. **pr-review-toolkit:** Selective use (SP ≥ 5 or security-flagged) to manage token cost?
8. **claude-skills (alirezarezvani):** Which POWERFUL tier skills to adopt per role?
9. **code-container:** Evaluate for fleet security model (container isolation vs bypassPermissions)?
10. **hookify:** Use for PO-created custom hooks? Or build hooks via IaC?
