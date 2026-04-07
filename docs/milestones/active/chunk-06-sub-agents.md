# Chunk 6: Sub-Agent Definitions Per Role

**Date:** 2026-04-07
**Status:** Planning
**Part of:** [tools-system-session-index.md](tools-system-session-index.md) — Chunk 6 of 9
**Depends on:** Chunk 2 (plugins provide sub-agents: superpowers code-reviewer, pr-review-toolkit 6 agents, feature-dev 3 agents), Chunk 4 (skills that sub-agents may need)
**Blocks:** Chunk 8 (generation pipeline needs sub-agent info for TOOLS.md)

---

## What This Chunk Accomplishes

Each agent gets custom sub-agent definitions for delegation and parallel work. After this chunk, agents can spawn specialized sub-agents for focused tasks — codebase exploration, test execution, parallel research, security scanning — without bloating their main context.

Additionally, Agent Teams is evaluated for within-task multi-agent collaboration as a complement to the fleet orchestrator.

---

## Sub-Agents From Plugins (Available After Chunk 2)

These come "free" with plugin installation:

| Plugin | Sub-Agent | Model | Purpose |
|--------|-----------|-------|---------|
| superpowers | code-reviewer | inherit | Senior code review: plan alignment, quality, architecture, docs |
| pr-review-toolkit | code-reviewer | opus | CLAUDE.md compliance, style, bugs |
| pr-review-toolkit | code-simplifier | inherit | Simplification preserving functionality |
| pr-review-toolkit | comment-analyzer | inherit | Comment accuracy, doc completeness |
| pr-review-toolkit | pr-test-analyzer | inherit | Behavioral coverage, test gaps |
| pr-review-toolkit | silent-failure-hunter | inherit | Error handling audit |
| pr-review-toolkit | type-design-analyzer | inherit | Type encapsulation, invariant expression |
| feature-dev | code-explorer | sonnet | Trace execution paths, map architecture |
| feature-dev | code-architect | sonnet | Design features, implementation blueprints |
| feature-dev | code-reviewer | sonnet | Confidence-based code review |

**Note:** feature-dev is NOT currently assigned to any agent in config/agent-tooling.yaml. It should be evaluated in Chunk 2 for architect and engineer.

---

## Custom Sub-Agent Design Approach

Each custom sub-agent definition (.claude/agents/{name}.md) needs:

1. **name** — unique identifier
2. **description** — CRITICAL: this drives when the main agent auto-delegates. Must clearly describe when to use this sub-agent.
3. **model** — cost-appropriate (sonnet for most, haiku for simple read-only, opus only for deep analysis)
4. **tools** — principle of least privilege (read-only agents get Read/Grep/Glob only, no Write/Edit/Bash)
5. **tools_deny** — explicitly block dangerous tools if using allowlist isn't cleaner
6. **isolation** — worktree for code modifications, none for analysis
7. **skills** — preload relevant skills
8. **mcpServers** — only the MCP servers needed
9. **System prompt** — focused instructions for the sub-agent's specialty

### Design Per Role

Each role needs evaluation of:
- What tasks does this role repeatedly delegate or could benefit from delegating?
- What tasks bloat context when done in the main session?
- What tasks benefit from parallel execution (even simulated sequential)?
- What tool/model combination is appropriate per delegation type?

Below is the structure for per-role sub-agent design. The ACTUAL definitions require per-role design sessions — these are the CATEGORIES to evaluate, not prescriptive definitions.

### Architect Sub-Agents (to evaluate)

| Category | Purpose | Model | Tools | Isolation |
|----------|---------|-------|-------|-----------|
| Codebase navigator | Explore code structure without bloating main context | sonnet | Read, Grep, Glob, filesystem MCP | none |
| Dependency mapper | Trace import chains and module relationships | haiku | Read, Grep, Glob | none |
| Pattern analyzer | Identify design patterns in existing code | sonnet | Read, Grep, Glob | none |

**Note:** feature-dev plugin's code-explorer may cover the codebase navigator need. Evaluate before building custom.

### Engineer Sub-Agents (to evaluate)

| Category | Purpose | Model | Tools | Isolation |
|----------|---------|-------|-------|-----------|
| Test executor | Run tests and report results in isolation | sonnet | Bash, Read, filesystem MCP, pytest-mcp | none |
| Parallel researcher | Web research while main agent works | sonnet | WebSearch, WebFetch, Read | none |

**Note:** superpowers' dispatching-parallel-agents skill teaches when/how to spawn parallel sub-agents. This skill may be sufficient without custom definitions.

### QA Sub-Agents (to evaluate)

| Category | Purpose | Model | Tools | Isolation |
|----------|---------|-------|-------|-----------|
| Coverage analyzer | Generate and analyze coverage reports | sonnet | Bash, Read, filesystem MCP | none |
| Regression checker | Run specific regression test suites | sonnet | Bash, Read, pytest-mcp | none |

### DevSecOps Sub-Agents (to evaluate)

| Category | Purpose | Model | Tools | Isolation |
|----------|---------|-------|-------|-----------|
| Dependency scanner | Scan all project deps for known issues | sonnet | Bash, Read, filesystem MCP | none |
| Secret detector | Scan repository for exposed credentials | haiku | Read, Grep, Glob | none |

### Fleet-Ops Sub-Agents (to evaluate)

pr-review-toolkit provides 6 parallel review agents. Evaluate whether additional custom sub-agents are needed:

| Category | Purpose | Model | Tools | Isolation |
|----------|---------|-------|-------|-----------|
| Trail reconstructor | Build complete task trail from board memory | sonnet | Read, Grep | none |

### PM, Writer, UX, Accountability Sub-Agents

These roles likely need fewer or no custom sub-agents. Evaluate based on observed patterns once the fleet is running.

---

## Agent Teams Evaluation

### What Agent Teams Would Add

Agent Teams enables TRUE PARALLEL execution — multiple Claude instances with shared task lists and peer-to-peer messaging. Unlike sub-agents (sequential, results return to parent), teammates work simultaneously.

### Where Agent Teams Could Complement the Fleet

| Scenario | How It Would Work |
|----------|-------------------|
| Epic breakdown | PM leads team of architect + engineer to explore, design, and plan simultaneously |
| Parallel review | Fleet-ops leads team of 3 reviewers checking different aspects |
| Investigation | Architect leads team exploring multiple approaches, debating via mailbox |
| Implementation | Engineer leads teammates working on different modules via shared task list |

### Evaluation Questions (Need Answers Before Adoption)

1. How does Agent Teams interact with the fleet orchestrator? The orchestrator manages 10 agents via heartbeat/dispatch. Agent Teams creates additional sessions not managed by the orchestrator. Do they conflict?
2. What permissions do teammates get? They inherit the lead's permission mode. Is this appropriate for fleet agents?
3. Cost implications? Each teammate is a full Claude instance. With 10 fleet agents, adding teams could multiply cost significantly.
4. Session management? Agent Teams sessions are separate from the fleet's session management. The brain can't track teammate context.
5. How does it interact with the heartbeat system? Teammate sessions are independent — they don't have heartbeats.
6. Quality gates? Agent Teams supports TeammateIdle and TaskCompleted hooks for enforcement.
7. Known limitations? Experimental feature. No session resumption, task status lag, one team per session, no nested teams.

### Recommendation

Evaluate Agent Teams AFTER the fleet has basic live operation (path-to-live Phase D: first live test). Agent Teams adds complexity to a system that isn't running yet. The fleet orchestrator handles inter-agent coordination. Agent Teams could complement it later for within-task parallel work — but only after the baseline works.

---

## Deployment

Sub-agent definitions go to:
- agents/{name}/.claude/agents/{subagent-name}.md — per-role definitions
- Deployed to workspaces via push-agent-framework.sh (needs update to include .claude/agents/)

### push-agent-framework.sh Update Needed

Currently pushes: CLAUDE.md, HEARTBEAT.md, STANDARDS.md, MC_WORKFLOW.md
Needs to also push: .claude/agents/ directory (sub-agent definitions)

---

## Verification Criteria

- [ ] Plugin sub-agents verified as available (after Chunk 2)
- [ ] Custom sub-agent definitions designed per role (where needed)
- [ ] Sub-agent definitions deployed to agent workspaces
- [ ] At least one custom sub-agent tested: agent spawns → sub-agent works → results return
- [ ] Agent Teams evaluated with recommendation (adopt/defer/skip)
- [ ] push-agent-framework.sh updated to deploy .claude/agents/
- [ ] Sub-agent definitions don't exceed agent's tool permissions

---

## Outputs

| Output | Description |
|--------|-------------|
| Per-role .claude/agents/{name}.md files | Custom sub-agent definitions |
| Agent Teams evaluation document | Recommendation with rationale |
| Updated push-agent-framework.sh | Deploys sub-agent definitions to workspaces |
