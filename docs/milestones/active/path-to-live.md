# Path to Live — From Documentation to Running Fleet

**Date:** 2026-04-01
**Status:** PLANNING — ordered work from current state to live operation
**Depends on:** All system documentation (docs/systems/), ecosystem deployment plan, unified implementation plan

---

## 1. Where We Are

### Built and Tested (code exists, unit tested)
- 94 core modules across 20 systems
- 1800+ unit tests, 23 integration tests
- Orchestrator runs (9-step cycle, 30s interval)
- Gateway integration (WebSocket RPC, prune/compact/inject)
- Event bus (47 event types, 6 surfaces, routing)
- Methodology (5 stages, stage gating on MCP tools)
- Immune system (4 detections, teaching, self-healing)
- 25 MCP tools (stage-gated, event chains)
- Budget system (6 modes, real OAuth quota monitoring)
- Storm prevention (9 indicators, circuit breakers)
- Agent lifecycle (ACTIVE→DROWSY→SLEEPING, content-aware)

### Documented but NOT Built
- Contribution flow (fleet_contribute tool, brain subtask creation)
- Brain-evaluated heartbeats (DROWSY/SLEEPING deterministic eval)
- Per-agent tooling (MCP servers, plugins, skills per role)
- Agent CLAUDE.md per fleet-elevation specs (0/10 have anti-corruption rules)
- HEARTBEAT.md per role per fleet-elevation specs
- Full role-specific pre-embed (AR-01)
- 3 missing MCP tools (fleet_contribute, fleet_request_input, fleet_gate_request)

### Never Done
- ONE live test with a real agent doing real work through full lifecycle
- PM assigning a real task → agent working through stages → fleet-ops reviewing

---

## 2. The Ordered Path

### Step 1: Deploy Ecosystem Tier 1 (zero risk, immediate value)

From ecosystem-deployment-plan.md:

```
E-01: Enable prompt caching in openclaw.json → 90% savings
E-02: Install Claude-Mem plugin → cross-session memory
E-03: Install Context7 for architect + engineer → library docs
E-04: Filesystem MCP for all workers → structured file ops
```

**Why first:** These improve every subsequent step. Caching saves
money on everything that follows. Claude-Mem means agents retain
learning. Context7 means agents use current docs. Filesystem MCP
means agents can properly explore code.

**IaC:** `make configure-caching`, `make install-plugins`, `make agent-setup-all`

**Time:** 1-2 hours. Config + install. No code changes.

### Step 2: Deploy Template Files to Agent Directories

Currently `MC_WORKFLOW.md`, `STANDARDS.md`, `MC_API_REFERENCE.md`,
`mcp.json` are in `agents/_template/` but NOT copied to agent
directories. Workers may run without workflow instructions.

```
For each agent:
  Copy _template/MC_WORKFLOW.md → agents/{name}/MC_WORKFLOW.md
  Copy _template/STANDARDS.md → agents/{name}/STANDARDS.md
  Copy _template/MC_API_REFERENCE.md → agents/{name}/MC_API_REFERENCE.md
  Generate per-agent mcp.json from config/agent-tooling.yaml
```

**IaC:** `scripts/push-framework.sh` (already exists, may need update)

**Time:** 1 hour. Script execution + verify.

### Step 3: Write Agent CLAUDE.md Per Fleet-Elevation Specs

This is the agent refactor — the work all the documentation enables.

For each of 10 agents, write CLAUDE.md that follows fleet-elevation/02 spec:
- Max 4000 chars, dense, role-specific
- 10 anti-corruption rules (from fleet-elevation/20)
- Stage protocol per role (conversation/analysis/investigation/reasoning/work)
- Tool → chain documentation per role
- Contribution model (what this agent contributes to others)
- What this agent does NOT do (boundary setting)

**Read before writing each agent:**
- fleet-elevation/{agent_number}.md (per-role spec)
- agent-rework/{agent_number}.md (pre-embed, heartbeat details)
- fleet-elevation/02 (architecture — injection order, SRP, 4000 char limit)
- fleet-elevation/20 (anti-corruption rules)
- fleet-elevation/15 (cross-agent synergy)

**IaC:** CLAUDE.md files are committed (all agents). Not generated.
They're the IDENTITY of each agent. Human/AI writes them with care.

**Time:** 2-4 hours per agent. 10 agents = 20-40 hours of careful work.

### Step 4: Write Role-Specific HEARTBEAT.md

Each agent gets a heartbeat rewritten per fleet-elevation specs:

- **PM:** PO directives → unassigned tasks → stage progression → epic breakdown → sprint → Plane sync → inter-agent comms
- **Fleet-ops:** PO directives → approval processing (REAL review) → methodology compliance → board health → budget → immune awareness
- **Architect:** PO directives → design contributions → complexity assessment → ADRs → progressive artifacts
- **DevSecOps:** PO directives → security contributions → PR review → infrastructure health → crisis response
- **Workers (template):** PO directives → messages → stage protocol (conversation/analysis/investigation/reasoning/work) → progressive artifacts → communication → idle

**Read before writing:** agent-rework/04-08 (heartbeat details per role)

**Time:** 1-2 hours per role. 5 unique heartbeats = 5-10 hours.

### Step 5: Enhance Pre-Embed Per Role (AR-01)

Update role_providers.py to provide FULL data per role:

- PM gets: Plane sprint data, module progress, new Plane issues
- Fleet-ops gets: full approval context (requirement + criteria + PR + completion summary + stage history + artifact completeness)
- Architect gets: tasks needing design (with full context, not just title)
- Workers get: artifact completeness + suggested readiness + contributions received

**Time:** 4-8 hours. Code changes to role_providers.py + preembed.py.

### Step 6: Minimum Viable Live Test

Skip contribution flow. Simplest possible test:

```
1. Create task on OCMC (manually)
2. Set: agent=software-engineer, stage=reasoning, readiness=99
3. Set: requirement_verbatim="Add a README.md to fleet/core/"
4. Start orchestrator daemon
5. Orchestrator dispatches task to agent
6. Agent receives context → follows work protocol
7. Agent calls fleet_commit → fleet_task_complete
8. Task moves to review
9. Fleet-ops heartbeats → sees pending approval
10. Fleet-ops approves with reasoning
11. Done.
```

**What this tests:** Dispatch, agent execution, MCP tools, event
chains, approval flow. 

**What this skips:** Contribution flow, PM assignment, stage
progression from conversation→work, Plane sync.

**Time:** 1-2 hours to set up + observe.

### Step 7: Build Contribution Flow

The largest missing piece. Without it, specialists can't contribute
before implementation.

1. Build `fleet_contribute` MCP tool:
   - Agent posts design_input, qa_test_definition, security_requirement,
     ux_spec, or documentation_outline to another agent's task
   - Fires `build_contribution_chain()` (already exists in event_chain.py)
   - Updates target task custom fields

2. Build brain logic in orchestrator:
   - When task enters REASONING with readiness approaching 80
   - Create parallel contribution subtasks (auto_created=true)
   - Each subtask: parent_task linked, contribution_type set, assigned to specialist

3. Build `fleet_request_input` MCP tool:
   - Agent requests missing contribution from PM
   - PM creates contribution subtask

4. Update pre-embed: include received contributions in worker task context

**Time:** 8-16 hours. New MCP tool + orchestrator logic + pre-embed changes.

### Step 8: Full Lifecycle Live Test

PM assigns real task → agent works through ALL stages → contributions
received → work executed → challenge → review → done.

```
1. PM heartbeats → sees unassigned task → assigns to software-engineer
2. Engineer heartbeats → sees task in conversation stage
3. Engineer asks questions → PO clarifies → stage advances to analysis
4. Engineer analyzes codebase → produces analysis artifact → stage advances
5. Task enters reasoning → brain creates contribution subtasks:
   - architect: design_input
   - qa-engineer: qa_test_definition
   - devsecops: security_requirement (if applicable)
6. Contributions arrive → pre-embedded in engineer's context
7. Engineer plans → references verbatim → PO confirms → readiness 99
8. Engineer implements → fleet_commit × N → fleet_task_complete
9. Challenge engine evaluates → automated checks → pass/fail
10. Fleet-ops reviews → real review against verbatim + criteria
11. Fleet-ops approves → done → Plane issue updated
```

**Time:** 2-4 hours to observe. Requires all previous steps working.

### Step 9: Deploy Ecosystem Tier 2

After live testing confirms the base works:
- Per-agent MCP servers (GitHub, Playwright, Docker)
- Per-agent skills from OpenClaw registry
- LocalAI RAG integration
- Batch API for non-urgent work

### Step 10: 24-Hour Fleet Observation

Operational readiness milestone #20:
- Fleet runs autonomously for 24 hours
- PO monitors via Plane + IRC + ntfy
- Storm prevention detects and responds to any issues
- Budget system tracks and constrains costs
- Immune system detects and corrects any agent diseases

---

## 3. What We Skip (For Now)

- **Brain-evaluated heartbeats** — data structures exist, can optimize later
- **Multi-fleet identity** — needs second machine
- **AICP ↔ Fleet bridge** — optimize later
- **Agent Teams** — evaluate after base works
- **LocalAI v4.0 agents** — evaluate after base works
- **Dual GPU / TurboQuant / cluster peering** — hardware dependent

These are valuable but not blocking live operation.

---

## 4. Documentation That Enables Each Step

| Step | Read Before Starting |
|------|---------------------|
| 1 | `ecosystem-deployment-plan.md` (Tier 1) |
| 2 | `fleet-elevation/02` (template system), `agents/_template/` |
| 3 | `fleet-elevation/02, 05-14, 20` (architecture, per-role, anti-corruption) |
| 4 | `agent-rework/04-08` (heartbeat details per role) |
| 5 | `agent-rework/02` (pre-embed spec), `docs/systems/19-session.md` |
| 6 | `docs/systems/07-orchestrator.md`, `08-mcp-tools.md` |
| 7 | `fleet-elevation/15` (synergy), `docs/systems/04-event-bus.md` (chains exist) |
| 8 | `docs/systems/01-methodology.md`, `15-challenge.md` |
| 9 | `ecosystem-deployment-plan.md` (Tier 2), `docs/systems/21-agent-tooling.md` |
| 10 | `docs/systems/11-storm.md`, `12-budget.md`, `02-immune-system.md` |

---

## 5. Estimated Timeline

| Step | Work | Hours | Cumulative |
|------|------|-------|-----------|
| 1. Ecosystem Tier 1 | Config + install | 1-2h | 1-2h |
| 2. Template deploy | Script execution | 1h | 2-3h |
| 3. CLAUDE.md × 10 | Careful writing | 20-40h | 22-43h |
| 4. HEARTBEAT.md × 5 | Careful writing | 5-10h | 27-53h |
| 5. Pre-embed enhance | Code changes | 4-8h | 31-61h |
| 6. MVP live test | Setup + observe | 1-2h | 32-63h |
| 7. Contribution flow | New tool + logic | 8-16h | 40-79h |
| 8. Full lifecycle test | Observe | 2-4h | 42-83h |
| 9. Ecosystem Tier 2 | Eval + deploy | 8-16h | 50-99h |
| 10. 24h observation | Monitor | 24h | 74-123h |

**Realistic:** 3-6 weeks of focused work to reach live fleet operation.

The heaviest work is Step 3 (CLAUDE.md for 10 agents) because each
must be written with deep understanding of the role, the methodology,
the contribution model, and the anti-corruption rules. This is NOT
template filling — it's the identity of each top-tier expert.
