# Plane Data in Agent Context

**Date:** 2026-03-30
**Status:** Design
**Part of:** Agent Rework (document 11 of 13)

---

## PO Requirements (Verbatim)

> "it must be pre-embedded into its heartbeat with not only the ocmc board
> but also the related plane data if connected and existing."

---

## Which Agents Need Plane Data

### PM (primary Plane user)
- Plane sprint: current cycle, issues, priorities
- Plane modules: which modules have work
- New Plane issues not yet on OCMC
- Plane state changes (issue moved to "In Progress")

### fleet-ops
- Plane issue state for tasks in review
- Cross-reference between OCMC task and Plane issue

### All agents (for their tasks)
- If their task is linked to a Plane issue:
  - Plane issue state, labels, description
  - Plane comments (from PO or other stakeholders)
  - Module membership

---

## How Plane Data Gets Pre-Embedded

The context assembly already fetches Plane data for tasks with
plane_issue_id. The pre-embed needs to include this data.

For PM heartbeat: the role provider should fetch Plane sprint data
and include it in the pre-embed.

For workers: if their task has a Plane link, the task pre-embed
includes the Plane issue state and description.