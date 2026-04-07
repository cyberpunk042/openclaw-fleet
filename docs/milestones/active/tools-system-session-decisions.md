# Tools System — Session Decisions, Open Questions, PO Requirements

**Date:** 2026-04-07
**Status:** Active — captures decisions and open items from this session
**Part of:** [tools-system-session-index.md](tools-system-session-index.md)

---

## PO Requirements From This Session (Verbatim)

These are NEW requirements from this session that go beyond what's captured in the 31 fleet-elevation docs. They refine and extend the vision.

### On the Scale of the Tools System

> "this tools system task is massive"

> "Lets not minimize or reduce the task to something small. its is over 42 of effort. only for tools, considering it aggregate a bunch of things"

> "IN THIS THERE IS ALMOST NO REAL AGENT SPECIFIC SKILLS, IT ONLY CONTAINS MY OWN PERSONAL PREWRITEN LIST OF SKILLS FOR LOCALAI PROJECT.... IN REALITY THERE 1000+ skills.... 10-40 generic depending on the methodologies and 40+ per roles per methodology and cases or situations..."

> "Then there is the task-specific skills vs the project management specific skills and project creation specific skills and so on...."

> "We use packs and the goals is to aggregate the appropriate packs like those with superpowers and to install them to the appropriate agent and to direct them when to use which in appropriate times. everything properly structured and distributed."

### On Agent-Specific Capabilities

> "what I have in mind is the agent. TOP-TIER EXPERT they have their own tools so they need their own mcps and own chains and own groups calls, not only the normal ones but also the roles specific ones on all angles with their own directives and way to use the tools and their multiple layers and impact and reasons and requirements."

### On Extended Thinking and Strategic Features

> "I just realized that we did not even integrate the extended thinking mode for when appropriate"

> "hooks can help enhance our agent tracking too. I could connect via a stream to a selected agent and see his current feed for example and possibly other advantages"

> "the agents can also use sub-agents when appropriate with the right strategy, like parallel research or group of self-contained tasks that can be aggregated as they come back. it has to be done well though."

### On CRONs and Scheduled Operations

> "CRON e.g. ops agent -> 01:00 ->Scan environment for XYZ... based of ABC.... AND... AND... and then do this and that and call this...."

> "Based off a yaml config again where we would load those and keep the live CRONs in sync like we do with the heartbeats."

> "and turning them off too like the heartbeat when we are on Pause or out of budget and such."

> "proper model, proper effort, proper context size, proper methodology & etc... This is how we think."

### On Methodology and Stage Progression

> "there are also things relative to skills usage and commands usage and per methodology recommendations, like time to clear or compact or time to plan"

> "Considering also what I just said and how it influence where and what is happening but sure that everything will happens and the right way at the right level."

### On Strategic Call Decisions

> "This connect a bit with the effort and models of choices and backend possible for the available option based of the router config & adapted executions and trails and signatures."

> "This connect a bit with the notions of giving strategic keypoint for moment to do plans, adversarial-reviews, spawn sub-agents and such feature like when to use tools and why and how."

### On the Group Call / Tree Concept

> "chain is calling multiple tools, not just small process and transformation but also add a comment to the mc board for example and auto adding it to the task on Plane and etc.... a tree map to generate multiple tool call from a single one."

> "its good to have them to understand the trees and original or individual possibilities but the truth is that the tools we will give to the agents do not need to be ambiguous or limited or 1 to 1 operations"

> "you need to understand the difference between the basic chains and the group calls which are basically trees with possibly independent branches with individual failures mode."

### On the Config Architecture

> "config/tool-roles.yaml — If we put something in config its to be able to wire which agent receive which tools directives / knowledge for which tools"

### On Naming

> "openclaw is not even real anymore... the fleet is called openfleet and openclaw is just one of my AI assistant Vendor with openarms being our default."

---

## Decisions Made This Session

### Decision 1: Two Companion Documents for Tools

The tools system has two distinct scopes:
- **Document 1:** Fleet group calls (shared MCP tools with tree execution) — tool-chain-elevation-plan.md
- **Document 2:** Role-specific tooling (MCP servers, plugins, skills, CRONs, sub-agents, hooks) — role-specific-tooling-elevation-plan.md

These are separate because they have different dependency chains, different implementation approaches, and different audiences. Group calls are infrastructure (Python code). Role-specific tooling is configuration and ecosystem (YAML, SKILL.md, plugin installs).

### Decision 2: ChainRunner for Tool Trees, Chain Registry for Brain

Two patterns for two contexts:
- **Tool trees** use the existing ChainRunner (flat execution with required/optional flags) — tools build EventChains, runner executes
- **Chain Registry** (event-driven cascading reactions) is a brain evolution task — NOT part of the tools system elevation

This means: tools emit events, the brain's future chain registry reacts to those events. But the tools themselves use the simpler ChainRunner pattern.

### Decision 3: Primary Action Outside the Tree

Tools do their core domain logic FIRST (the thing that must succeed), then fire the tree for propagation (the things that should happen but aren't blocking). If the tree fails, the primary action already succeeded.

### Decision 4: tool-chains.yaml Written From Scratch

The existing tool-chains.yaml was aspirational (documented trees that didn't fire). After chain wiring is complete, it gets rewritten from scratch to document only what ACTUALLY fires. Truth over aspiration.

### Decision 5: Plane Tools — Partial Internalization

- fleet_plane_comment → internalized into comment propagation chains
- fleet_plane_update_issue → internalized into state propagation chains
- fleet_plane_create_issue → internalized into fleet_task_create chain
- fleet_plane_status, fleet_plane_sprint, fleet_plane_sync, fleet_plane_list_modules → KEPT as PM/writer infrastructure queries

### Decision 6: 9-Chunk Execution Order

Follow the dependency chain: chain wiring → MCP/plugins → skill foundation → role skills → CRONs → sub-agents → hooks → generation pipeline → validation. Each chunk is planned before execution. Each chunk produces outputs that feed the next.

### Decision 7: Skills Scope Is Ecosystem-Scale

The current config/agent-tooling.yaml skills list is a starting point from the LocalAI project. The real scope is 1000+ skills across 5 sources, evaluated per role per methodology stage. This is an ongoing capability buildout, not a one-time implementation.

### Decision 8: Stage-Aware Effort Deferred to Brain Evolution

Static effort levels updated for now (higher across the board). Dynamic stage-aware effort (brain decides effort per situation) is a brain evolution task (fleet-elevation/23), not a tools system task. CRONs get per-job effort from config.

### Decision 9: Agent Teams Deferred to Post-Live

Agent Teams is experimental and adds complexity. Evaluate AFTER the fleet has basic live operation. Sub-agents (within a single session) are the immediate capability for delegation.

### Decision 10: IRC as 80% Monitoring Solution

After chain wiring, most agent activity is visible in IRC channels via The Lounge. HTTP hook-based monitoring (deeper observability) is evaluated as proof of concept, not built as full system. Full monitoring dashboard is a separate project.

---

## Open Questions Requiring PO Input

### Q1: Standing Order Authority Per Role

What is each agent AUTHORIZED to do autonomously? The standing orders need PO-directed scoping:
- Can PM assign agents autonomously? Change priorities? Create tasks?
- Can fleet-ops approve autonomously (already defined in review protocol — confirm)?
- Can DevSecOps set security holds autonomously?
- What actions require PO confirmation across all roles?

This affects: Chunk 5 (standing orders), Chunk 7 (hooks enforcing boundaries).

### Q2: CRON Schedules and Procedures Per Role

The chunk plan has SCAFFOLD examples. Actual schedules and procedures need PO direction:
- What does DevSecOps scan at 01:00? (all deps? specific projects? what tools?)
- What does PM report at 09:00? (sprint state? blocker list? what format?)
- How often does fleet-ops sweep reviews? (every 2h? more?)
- Which roles even NEED CRONs?

This affects: Chunk 5.

### Q3: Plugin Evaluation Priorities

32+ official Anthropic plugins, 9+ superpowers marketplace plugins. Which to evaluate first?
- feature-dev (3 sub-agents) for architect + engineer?
- code-review for fleet-ops + QA?
- serena (semantic code analysis) for architect + engineer?
- episodic-memory for all agents?

This affects: Chunk 2.

### Q4: Skill Creation vs Ecosystem Installation Balance

For the 40+ per-role skills: how much should come from ecosystem evaluation vs custom building?
- Should we prioritize installing existing packs (faster, less custom) or building fleet-specific skills (more tailored, more work)?
- Is there a preference for specific skill pack sources?

This affects: Chunks 3+4.

### Q5: Sub-Agent Definitions Per Role

Which roles actually need custom sub-agents (beyond what plugins provide)?
- Is the superpowers code-reviewer sufficient for code review delegation?
- Does architect need a custom codebase navigator, or does feature-dev's code-explorer suffice?
- Are there delegation patterns the PO has in mind that aren't covered?

This affects: Chunk 6.

### Q6: Monitoring Depth

How deep should agent monitoring go?
- IRC + The Lounge (80% solution, already works after chain wiring)?
- HTTP hooks for real-time tool-call-level monitoring?
- Full monitoring dashboard?

This affects: Chunk 7.

### Q7: config/agent-tooling.yaml Cleanup

The current skills list has outdated "openclaw-*" references and aspirational skill names. Should the config be:
- Cleaned up to only contain VERIFIED skills (after Chunk 3)?
- Kept as aspirational with a "verified" flag per entry?
- Restructured to separate "installed" from "planned"?

This affects: Chunks 2+3+4.

---

## Connections to Existing Work

### Path-to-Live Mapping

| Tools Chunk | Path-to-Live Phase | Path-to-Live Steps |
|-------------|-------------------|-------------------|
| Chunk 1 | Phase C (Brain Evolution) | Step 10 partial (chain builder), Step 11 (trail wiring) |
| Chunk 2 | Phase A (Foundation) | Step 3 (IaC scripts), Step 4 (Ecosystem Tier 1) |
| Chunk 3 | Phase B (Agent Identity) | Step 9 (Generate TOOLS.md) |
| Chunk 4 | Phase B (Agent Identity) | Step 9 continuation |
| Chunk 5 | Phase C (Brain Evolution) | New — not in original path-to-live |
| Chunk 6 | Phase E (Cross-Agent Synergy) | Related to Step 16 (contribution flow) |
| Chunk 7 | Phase C (Brain Evolution) | Step 12 (fleet settings), Step 14 (session telemetry) |
| Chunk 8 | Phase B (Agent Identity) | Step 9 (Generate TOOLS.md) |
| Chunk 9 | Phase D (First Live Test) | Step 15 (minimum viable live test) |

### Agent Elevation Connection

The previous session created:
- 10 × IDENTITY.md templates (all agents)
- 10 × SOUL.md templates (all agents)
- 10 × CLAUDE.md templates (all agents)
- 7 × HEARTBEAT.md templates (5 named + worker + software-engineer)
- Provisioning pipeline with {{placeholder}} substitution

These are Layers 0 (the onion's inner layers — who the agent IS). The tools system (this work) is Layer 4 in the onion (TOOLS.md at position 4). Together they form the complete agent file set.

### Methodology System Connection

The methodology system (config/methodology.yaml) was made configurable in the previous session. The tools system builds ON this:
- Stage names from methodology.yaml → section headers in TOOLS.md
- tools_blocked from methodology.yaml → "BLOCKED" annotations in TOOLS.md
- Stage protocols from methodology.yaml → inform which skills are recommended per stage
- skill-stage-mapping.yaml (new) → connects skills to methodology stages

### Brain Connection

The brain (orchestrator) was updated in the previous session:
- Readiness-based dispatch gate REMOVED
- Auto-set task_stage from readiness
- Instant wake on dispatch

The tools system feeds the brain:
- Tool chain events → brain's future chain registry (reactive cascading)
- Trail events → brain's trail system (accountability, fleet-ops review)
- CRON results → brain's health monitoring
- Hook data → brain's immune system (behavioral analysis)

---

## What the Next Session Needs

When this work resumes (this session or future):

1. Read tools-system-session-index.md FIRST — it's the map
2. Read the chunk plan for the chunk being executed
3. Check the open questions — some may need PO answers before execution
4. Follow the dependency chain — don't skip ahead
5. Update the session index as chunks complete
6. Write a decisions doc if new decisions are made

The chunk plans are designed to be executable WITHOUT re-reading all the research documents. Each plan has: what to do, what order, what to verify, what outputs to produce. The research docs are REFERENCE — consult them when details are needed.

---

## Known Issues

### Security Hook Content Detection

The security-guidance plugin's PreToolUse hooks trigger on document content that MENTIONS security patterns. This caused Write failures this session when writing docs that describe what the security plugin detects. Needs a solution before Chunk 7 (hook configurations).

### Outdated OpenClaw References

config/agent-tooling.yaml lists "openclaw-health", "openclaw-fleet-status", etc. These reference the vendor name. The fleet is OpenFleet, the vendor is OpenArms (or OpenClaw as fallback). These need updating when config is cleaned up.

### LightRAG MCP in Defaults

config/agent-tooling.yaml defaults include a LightRAG MCP server that depends on LocalAI running. This should be conditional, not default. When LocalAI is not available, this MCP server will fail to start, potentially blocking all other MCP tools for the agent.

### Disconnected Code Changes

This session made code changes (chain builders, ChainRunner actions, tools.py wiring) before the chunk plan was written. These changes work (verified) but were done without following the planned execution order. They're noted in the session index as "DONE — but DISCONNECTED from the full plan."
