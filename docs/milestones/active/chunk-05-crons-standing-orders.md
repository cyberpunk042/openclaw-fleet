# Chunk 5: CRONs + Standing Orders Design

**Date:** 2026-04-07
**Status:** Planning
**Part of:** [tools-system-session-index.md](tools-system-session-index.md) — Chunk 5 of 9
**Depends on:** Chunk 4 (skills exist — CRONs reference skills in their procedures), Chunk 2 (gateway CRON system verified)
**Blocks:** Chunk 8 (generation pipeline needs CRON info for TOOLS.md)

---

## What This Chunk Accomplishes

Top-tier experts have scheduled responsibilities — they don't just react to tasks. After this chunk, each agent has:
1. **Standing orders** — persistent autonomous authority defining WHAT they're authorized to do, with scope, triggers, approval gates, and escalation rules
2. **CRONs** — scheduled operations defining WHEN to act, referencing standing orders for the procedure
3. **Fleet state integration** — CRONs respect pause mode, budget gates, active hours
4. **IaC** — config/agent-crons.yaml + scripts/sync-agent-crons.sh for reproducible deployment

---

## Design Principles (from gateway docs + PO direction)

### Standing Orders Define WHAT, CRONs Define WHEN

The standing order says: "DevSecOps is authorized to scan dependencies for known vulnerabilities. Scope: all project dependencies. Escalation: critical findings → PO via ntfy. Format: structured security report."

The CRON says: "Fire at 01:00 daily, isolated session, opus model, high thinking."

The CRON message says: "Execute nightly dependency scan per standing orders."

Changing the procedure = change the standing order. Changing the schedule = change the CRON. They're independent.

### Execute-Verify-Report Pattern

Every standing order task follows:
1. Execute — do the work
2. Verify — confirm the result (don't claim "done" without evidence)
3. Report — tell the owner what was done

3 attempts max, then escalate.

### Fleet State Awareness

CRONs must respect:
- **Pause mode** — fleet paused → CRONs don't fire (or fire and immediately return "fleet paused, skipping")
- **Budget gates** — over budget threshold → skip non-critical CRONs
- **Active hours** — configurable per agent (e.g., PM standup only on weekdays)

Implementation options:
- Standing orders include "If fleet is paused or over budget, skip and report" (simplest)
- sync-agent-crons.sh disables CRONs when fleet state changes (reactive)
- CRON messages check fleet state file at execution time (deterministic)

### Right Model, Right Effort, Right Context

Each CRON gets strategic call configuration:
- **Model:** opus for deep analysis (security scan), sonnet for routine (status summary), haiku for simple (health check)
- **Thinking:** high for thoroughness-critical (security), low for routine
- **Session:** isolated for most (no context contamination), custom-named for continuity (daily standup building on previous)
- **Light context:** true for CRONs that don't need full workspace bootstrap (reduces cost)
- **Tools restriction:** --tools flag limits what the CRON can do (security scan doesn't need write tools)
- **Timeout:** appropriate per operation (quick health check: 60s, deep analysis: 600s)

---

## Per-Role CRON + Standing Order Design

Each role needs its own design session. Below is the STRUCTURE showing what needs to be designed per role — NOT the final content. The actual standing orders and CRON configurations require PO direction on scope and authority.

### Project Manager

**Potential scheduled operations (need PO design):**
- Daily standup summary (sprint state, blocker list, velocity, action items)
- Backlog grooming session (re-estimate, re-prioritize, identify stale items)
- Sprint boundary operations (close sprint, open next, carry over incomplete)
- Plane scan (when connected — new issues, priority changes)

**Standing order considerations:**
- What is PM authorized to do autonomously? (assign agents? change priorities? create tasks?)
- What requires PO confirmation? (priority changes? sprint scope changes?)
- How does PM communicate with PO? (summary format, frequency, channel)

### Fleet-Ops

**Potential scheduled operations (need PO design):**
- Review queue sweep (process pending approvals)
- Board health check (stuck tasks, offline agents, stale reviews)
- Budget monitoring report (spending patterns, alerts)
- Methodology compliance scan (check recent completions for trail gaps)

**Standing order considerations:**
- Can fleet-ops approve autonomously? (already defined in CLAUDE.md review protocol)
- What board health actions can fleet-ops take? (alert only? or also reassign?)
- Budget alert thresholds and escalation paths

### DevSecOps (Cyberpunk-Zero)

**Potential scheduled operations (need PO design):**
- Nightly dependency scan (check all project dependencies for CVEs)
- PR security review sweep (review unreviewed PRs for security)
- Infrastructure security check (services, ports, configs)
- Secret scan (detect exposed credentials across repos)

**Standing order considerations:**
- Security hold authority (can DevSecOps block task completion for security issues?)
- Severity classification (what's critical vs high vs medium)
- Incident response authority (crisis mode actions)

### Architect

**Potential scheduled operations (need PO design):**
- Architecture health check (pattern consistency, dependency direction, coupling)
- Design debt assessment (track divergence from designed architecture)
- Contribution backlog check (tasks awaiting design input)

### QA Engineer

**Potential scheduled operations (need PO design):**
- Test coverage report (project-wide coverage analysis)
- Contribution backlog check (tasks awaiting test predefinition)
- Regression detection (monitor for test failures in CI)

### DevOps

**Potential scheduled operations (need PO design):**
- Infrastructure health check (services running, disk space, memory)
- CI/CD pipeline status (build failures, deployment status)
- Configuration drift detection (compare running config to IaC)

### Technical Writer

**Potential scheduled operations (need PO design):**
- Documentation staleness scan (when Plane connected — check page update dates)
- API documentation sync (compare code endpoints to documented endpoints)

### UX Designer, Accountability Generator

**Potential scheduled operations:** Likely fewer or none for these roles. Evaluate per PO direction.

---

## Config Architecture

### config/agent-crons.yaml

```yaml
# Per-agent CRON definitions
# Each CRON references standing orders in the agent's files
# Standing orders define WHAT to do, CRONs define WHEN

defaults:
  budget_gate: true           # Skip if fleet over budget threshold
  fleet_pause_aware: true     # Skip if fleet paused

agents:
  devsecops-expert:
    crons:
      - name: nightly-dependency-scan
        schedule: "0 1 * * *"       # Cron expression
        timezone: America/New_York
        session: isolated
        model: opus
        thinking: high
        light_context: false         # Needs workspace files for scanning
        timeout_seconds: 600
        message: "Execute nightly dependency scan per standing orders."
        delivery: announce
        delivery_channel: "#security"
        budget_gate: true
        active_days: "1-5"           # Weekdays only (optional)

  project-manager:
    crons:
      - name: daily-standup
        schedule: "0 9 * * 1-5"     # 9 AM weekdays
        timezone: America/New_York
        session: "session:pm-standup" # Named session for continuity
        model: sonnet
        thinking: low
        light_context: true
        timeout_seconds: 300
        message: "Generate daily standup summary per standing orders."
        delivery: announce
        delivery_channel: "#sprint"
        budget_gate: true

  # ... (each role's CRONs as designed)
```

### scripts/sync-agent-crons.sh

Reads config/agent-crons.yaml and manages CRONs via gateway CLI:

```bash
# For each agent with CRONs configured:
#   1. List existing CRONs for this agent
#   2. Compare with config
#   3. Create new CRONs that don't exist
#   4. Update CRONs where config changed
#   5. Remove CRONs that are no longer in config
# Idempotent — safe to re-run
```

Uses: openclaw cron add, openclaw cron edit, openclaw cron remove, openclaw cron list

### Standing Orders Location

Standing orders go in agent files that are injected into every session. Options:
- **AGENTS.md** — gateway docs recommend this location
- **HEARTBEAT.md** — already contains the agent's action protocol
- **A dedicated STANDING-ORDERS.md** — separate file for clarity

The choice affects the autocomplete chain — standing orders in HEARTBEAT.md (position 8, last) means they're read right before action. Standing orders in AGENTS.md (position 5) means they're read before context data. A dedicated file would need gateway configuration to be injected.

Recommendation: standing orders that define AUTONOMOUS AUTHORITY go in AGENTS.md (the gateway reads this). Standing orders that define CRON PROCEDURES can be referenced by name in the CRON message — the agent reads them from its AGENTS.md context when the CRON fires.

---

## Verification Criteria

- [ ] Each agent with CRONs has standing orders defined
- [ ] config/agent-crons.yaml created with all agent CRONs
- [ ] scripts/sync-agent-crons.sh creates/updates/removes CRONs from config
- [ ] CRONs fire on schedule in isolated sessions
- [ ] CRONs use correct model/thinking/context per design
- [ ] CRONs respect fleet pause and budget gates
- [ ] CRON results delivered to correct channels
- [ ] Standing orders have clear scope, triggers, gates, escalation
- [ ] Execute-Verify-Report pattern followed in all standing orders

---

## Outputs

| Output | Description |
|--------|-------------|
| Per-role standing orders | Autonomous authority programs in agent files |
| config/agent-crons.yaml | Complete CRON configuration for all agents |
| scripts/sync-agent-crons.sh | IaC script for CRON management |
| Verification report | CRONs tested, firing correctly, fleet-state-aware |
