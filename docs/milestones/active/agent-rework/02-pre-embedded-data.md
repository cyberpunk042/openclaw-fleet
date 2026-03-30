# Pre-Embedded Data — Full Context, Not Compressed

**Date:** 2026-03-30
**Status:** Design
**Part of:** Agent Rework (document 2 of 13)

---

## PO Requirements (Verbatim)

> "it must be pre-embedded into its heartbeat with not only the ocmc board
> but also the related plane data if connected and existing."

> "I NEVER SAID WE WERE GOING TO INJECT A COMPACTED VERSION OF THE DATA"

> "THE GOAL OF CALLING A TOOL IS TO AGGREGATE ANOTHER TRAIL OR LARGER OR
> WHATNOT... NOT TO GATHER WHAT WE ALREADY KNOW WE ABSOLUTELY NEED"

---

## The Problem

The current preembed.py produces 300-char compressed summaries. That's
the compression disease injected into the code. The agent gets a tiny
summary and needs to make MCP calls to get the full data.

This is wrong. The pre-embedded data IS the full data. The agent gets
everything it needs before it starts thinking. MCP calls are for
aggregating ADDITIONAL data — not for getting what should already be
there.

---

## What Gets Pre-Embedded (FULL, not compressed)

### For Heartbeat

The agent wakes up with FULL data already in its context:

- **All assigned tasks** — not just IDs, but title, description,
  stage, readiness, verbatim requirement, story points, priority
- **All messages** — full content, not truncated
- **All pending directives** — full directive text
- **Events since last heartbeat** — full event detail
- **Role-specific data** — fleet-ops gets the full approval queue
  with task details, PM gets the full unassigned list with descriptions
- **Fleet state** — mode, phase, backend, agents online
- **Plane data** — if connected, sprint state, recent issues

### For Task Work

When dispatched to work on a task, the agent has:

- **Full task data** — all fields, description, custom fields
- **Full verbatim requirement** — never truncated
- **Full artifact object** — the structured data from transpose layer
- **Full comment history** — progressive work trail
- **Stage instructions** — full protocol text
- **Completeness status** — what's done, what's missing
- **Related tasks** — parent, children, dependencies

### What MCP Calls Are For

MCP calls (`fleet_task_context`, `fleet_heartbeat_context`) are for
getting ADDITIONAL aggregated data that isn't standard pre-embed:

- Pulling in related task artifacts across multiple tasks
- Getting a cross-task view of sprint progress
- Fetching Plane data on demand when not pre-embedded
- Getting deeper comment/activity history

NOT for getting what should already be there.

---

## What Needs to Change

### preembed.py

Currently builds 300-char summaries. Needs complete rewrite to deliver
full data. The size limit is the gateway's context/ file limit (1000
chars per file). If the data exceeds that — use multiple context files
or inject via chat.send which has no practical limit.

### context_writer.py

Currently writes one small file. May need to write multiple files or
use a different injection mechanism for larger data.

### HeartbeatBundle

Currently renders a compact text. Needs to render the full role-specific
data in a format the agent can read and act on.

### Gateway Integration

The gateway reads context/ files at execution time. Need to verify
there's no hard limit that forces compression. If there is, use
chat.send injection instead.

---

## Open Questions

- What is the actual size limit for gateway context injection?
- Should pre-embed be a single large context file or multiple files?
- Should the format be structured (JSON) or narrative (markdown)?
- How does pre-embed interact with HEARTBEAT.md? Does HEARTBEAT.md
  reference the pre-embedded data by section?