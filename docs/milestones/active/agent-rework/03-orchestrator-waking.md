# Orchestrator Waking — Trigger Agent Heartbeats on Demand

**Date:** 2026-03-30
**Status:** Design
**Part of:** Agent Rework (document 3 of 13)

---

## PO Requirements (Verbatim)

> "the orchestrator should be waking the project-manager and the fleet-ops
> if there are items in the Inbox unassigned then it would instantly
> heartbeat"

---

## The Problem

The orchestrator detects unassigned inbox tasks but doesn't wake the PM.
It detects pending approvals but only sends IRC notifications — doesn't
trigger fleet-ops to actually heartbeat and process them.

The gateway manages heartbeat intervals (every 10-35 minutes). But when
there's urgent work — unassigned tasks, pending approvals — the agent
should wake immediately, not wait for the next scheduled heartbeat.

---

## What "Waking" Means

Sending a message via the gateway (`chat.send`) to the agent's session.
This triggers the agent's Claude Code session to execute. The agent
reads its HEARTBEAT.md, gets its pre-embedded context, and does its job.

The gateway already supports this — `_send_chat` in dispatch.py sends
messages to agent sessions. The orchestrator needs to use the same
mechanism to wake driver agents.

---

## When to Wake

### Wake PM when:
- Unassigned tasks in inbox (PM should assign agents)
- Blocked tasks need resolution (PM should unblock)
- New Plane issues ingested (PM should evaluate)
- PO posted a directive targeting PM

### Wake fleet-ops when:
- Pending approvals (fleet-ops should review)
- Tasks stuck in review > threshold
- Health alerts from immune system
- PO posted a directive targeting fleet-ops

### Don't wake when:
- Already woken this cycle (cooldown)
- Agent has an active in-progress task (let them finish)
- Fleet is in paused mode

---

## What Needs to Change

### Orchestrator

Add a new step: "Wake drivers if work pending"

```
Orchestrator Cycle:
  ...
  Step N: Wake drivers — PM if unassigned inbox, fleet-ops if pending approvals
  ...
```

The wake sends a message via gateway that includes the pre-embedded
context data so the agent has full awareness when it wakes.

### Gateway Integration

Use the existing `inject_content` from `gateway_client.py` to send
the pre-embedded data + a wake message to the agent's session.

---

## Open Questions

- Should waking be throttled (max once per N cycles)?
- What message does the agent receive when woken? Just data, or
  data + explicit instruction ("You have 6 unassigned tasks")?
- Does waking interrupt a currently running heartbeat?