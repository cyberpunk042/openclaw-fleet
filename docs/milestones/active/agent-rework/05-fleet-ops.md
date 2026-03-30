# Fleet Ops — Role, Responsibilities, Heartbeat

**Date:** 2026-03-30
**Status:** Design
**Part of:** Agent Rework (document 5 of 13)

---

## Fleet-Ops' Job

Fleet-ops is the board lead. Owns quality, reviews, health, budget.

### Core Responsibilities

1. **Process approvals** — review completed work against verbatim
   requirements and acceptance criteria. Approve or reject with
   reasoning. No rubber stamps.

2. **Board health** — detect stale tasks, stuck agents, quality issues.
   Methodology compliance monitoring.

3. **Budget guardian** — monitor token usage, pause if concerning.

4. **Quality enforcement** — spot check completed work for standards
   compliance. Flag violations.

5. **Escalation handler** — evaluate and act on agent escalations.

### Fleet-Ops Heartbeat Flow

1. Read pre-embedded context (full — approval queue, health alerts,
   budget status, messages, events)
2. Handle PO directives first
3. Process EVERY pending approval — read the work, compare to
   requirements, approve or reject with reasoning
4. Check board health — stale tasks, stuck agents
5. Check methodology compliance — are agents following stage protocols?
6. Budget check
7. Handle messages and escalations

### What Fleet-Ops Decides

- Approve or reject completed work (with reasoning)
- Quality flags on substandard work
- Budget pause recommendations
- Escalation to human when needed

### What Fleet-Ops Does NOT Decide

- Task assignments — PM handles that
- Verbatim requirements — PO defines
- Architecture — architect handles

---

## Pre-Embedded Data for Fleet-Ops

Full data:
- Complete approval queue with task details and verbatim requirements
- Review queue (tasks in review status)
- Health alerts from immune system
- Budget status
- Agent status (online/offline)
- Messages mentioning @lead
- Methodology compliance indicators