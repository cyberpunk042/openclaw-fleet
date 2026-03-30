# New Custom Fields — OCMC and Plane

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Scope:** New custom fields needed on OCMC board and Plane for the
immune system, conversation protocol, and task readiness

---

## PO Requirements (Verbatim)

> "TASK READINESS = CUSTOM FIELD. (ON THE BOARD AND ON THE PROJECT
> MANAGEMENT....)"

> "WE HAVE TO BE ABLE TO MAKE THE DIFFERENCE BETWEEN A TASK THAT IS READY
> FOR WORK AND ONE THAT ISN'T."

> "QUOTE WHAT I SAY AND THAT MAKE THEM REQUIREMENTS AND YOU CANNOT
> MODIFY IT.... ITS ONE OF THE FIRST CURE"

> "The increase of Readiness has to come from a clear evaluation and
> confirmed with the PO."

> "we will need a series of new Custom Fields for OCMC and Plane"

---

## Context: Existing Custom Fields

The OCMC board currently has 14 custom fields configured via
`scripts/configure-board.sh`:

| Field | Type | Visibility | Purpose |
|-------|------|-----------|---------|
| project | text | always | Target project name |
| branch | text | if_set | Git branch |
| pr_url | url | if_set | GitHub PR URL |
| worktree | text | hidden | Local worktree path |
| agent_name | text | if_set | Assigned agent |
| story_points | integer | if_set | Effort estimate |
| sprint | text | if_set | Sprint identifier |
| complexity | text | if_set | low/medium/high |
| model | text | hidden | AI model used |
| parent_task | text | if_set | Parent task ID |
| task_type | text | always | epic/story/task/subtask/etc |
| plan_id | text | if_set | Sprint plan reference |
| review_gates | json | if_set | Review gate status |
| security_hold | text | if_set | Blocks approval |

MC supports 9 field types: text, text_long, integer, decimal, boolean,
date, date_time, url, json.

Plane supports custom fields on issues, mirrored via the sync worker.

---

## New Fields Identified in Discussion

### 1. task_readiness

**Discussed:** PO explicitly specified this as a custom field on both
OCMC and Plane. PO specified the threshold: "the only moment when you
can write work would be when the readiness is at 99 or 100%."

- **Field key:** `task_readiness`
- **Type:** integer (percentage, 0-100)
- **Visibility:** always — visible on every task card
- **Default:** 0
- **On:** OCMC board AND Plane issues
- **Who can change it:**
  - PO can set any value
  - PM can increase, with PO confirmation
  - Individual agents can increase on their own tasks to some degree,
    with PO confirmation — they communicate with the PO through comments
  - The increase of readiness has to come from a clear evaluation and
    confirmed with the PO
  - Agents can leave comments to discuss readiness with the PO, the PO
    confirms, readiness increases
- **Orchestrator behavior:** Tasks with `task_readiness < 99` are NOT
  dispatched for work protocol. Lower readiness values may be dispatched
  for conversation, analysis, investigation, or reasoning protocols
  depending on the readiness level.

**Open questions:**
- What readiness percentage maps to which protocol? e.g., 0-20% =
  conversation needed, 20-50% = analysis, 50-80% = investigation,
  80-99% = reasoning, 99-100% = work? Or is it not that linear?
- Can readiness decrease? Agent finds uncertainty during work, readiness
  drops back, agent must re-enter conversation with PO?
- How granular is the percentage in practice? Does the PO set exact
  numbers or rough ranges?

### 2. requirement_verbatim

**Discussed:** PO said verbatim requirements are the "first cure."
Agents cannot modify the PO's words.

- **Field key:** `requirement_verbatim`
- **Type:** text_long
- **Visibility:** always — always visible, always present
- **Default:** empty
- **On:** OCMC board AND Plane issues
- **Who can change it:**
  - PO can write and modify
  - PM can write (when capturing PO's words during conversation)
  - Agents CANNOT modify this field
- **Purpose:** The PO's exact words. The anchor for deviation detection.
  The source of truth that the immune system compares agent work against.
- **Relationship to task_readiness:** A task without a populated
  requirement_verbatim probably shouldn't be `ready`. A task with
  clear verbatim requirements is closer to ready.

### 3. task_stage (methodology stage)

**Discussed:** PO explained that methodology is "just linked to another
custom field its relative to the stage of work on a task / issue or
module."

- **Field key:** `task_stage`
- **Type:** text (with documented valid values)
- **Visibility:** always — visible on every task card
- **Default:** (depends on task type and requirements)
- **Values:** `conversation` | `analysis` | `investigation` | `reasoning` | `work`
- **On:** OCMC board AND Plane issues/modules
- **Purpose:** Tracks which stage of work the task is in. The agent
  must respect the protocol for the current stage. Each stage has
  methodology checks — when checks pass per the task/module
  requirements, the stage can advance.
- **Relationship to task_readiness:** Stages progress toward readiness.
  The most advanced stage (work) is when readiness reaches 99-100%.
- **Who can change it:** Advances when methodology checks pass. PO
  confirms stage transitions. Agent can request advancement.

### 4. Plane State Integration

**PO requirement:** "we will need to use the state of the work items
and such from Plane in our system. as the updates happens keeping in
right state in parallel of the ocmc. state assignees, start date...."

Plane already tracks rich metadata on issues that the fleet systems
need to consume:

| Plane Field | Purpose | Fleet Usage |
|------------|---------|-------------|
| **State** | backlog, unstarted, started, completed, cancelled | Task lifecycle, dispatch decisions, immune system monitoring |
| **Assignees** | Who's responsible | Agent dispatch, workload tracking |
| **Start date** | When work began | Duration tracking, stuck detection |
| **Due date** | Deadline | Priority decisions, overdue detection |
| **Priority** | urgent, high, medium, low, none | Dispatch ordering |
| **Labels** | Categorization | Task type, project, disease flags |
| **Cycle** | Sprint assignment | Sprint tracking, velocity |
| **Module** | Feature/component grouping | Module-level methodology tracking |
| **Estimate** | Story points | Complexity assessment, laziness detection (fast completion of high-point tasks) |

These must flow bidirectionally between Plane and OCMC:
- Plane state changes → reflected in OCMC
- OCMC status changes → reflected in Plane
- New custom fields (task_readiness, requirement_verbatim, task_stage)
  must exist and sync on BOTH platforms

The sync worker (`fleet/core/plane_sync.py`) exists but needs evolution
to handle:
- The new custom fields
- Bidirectional state synchronization
- Real-time or near-real-time updates (not just periodic polling)
- Conflict resolution when both platforms are updated

The methodology system needs Plane state data to function — task_stage
progression depends on knowing the Plane state, assignees, and metadata.
The immune system needs it for detection — start date enables stuck
detection, estimates enable laziness detection, state enables lifecycle
monitoring.

### 5. Additional fields — to be identified

The PO said "a series of new custom fields." task_readiness,
requirement_verbatim, and task_stage are the three identified so far,
plus Plane state integration. More will emerge as we design:

- The immune system (doctor flags, correction count, disease signals?)
- The teaching system (lesson status, comprehension verified?)
- Observability (who authorized transitions, when, why?)
- Methodology checks (per-stage check results, what passed/failed?)

These are NOT defined yet. They will be identified as each system is
designed. This document will be updated as new fields are identified.

---

## Open Questions

- Should task_readiness values be exactly `draft | needs-alignment |
  ready | blocked`, or are there more states? The PO mentioned protocols
  as phases — does readiness map to protocol phases?
- How does requirement_verbatim get populated in practice? PO types
  directly into OCMC/Plane? PO tells PM verbally and PM captures?
  PO writes in board memory and PM transfers to the field?
- What validation exists on requirement_verbatim? Can it be empty on a
  `ready` task? Should the orchestrator check for it?
- How do these fields sync between OCMC and Plane? The sync worker
  already mirrors custom fields — do these need special handling?
- MC doesn't have dropdown/select field types — task_readiness is a text
  field with documented valid values. Is that sufficient, or does the
  immune system need to validate the value?

---

## Implementation Notes

Adding custom fields to the OCMC board is already scripted in
`scripts/configure-board.sh` using the MC API:

```
POST /api/v1/organizations/me/custom-fields
{
  "field_key": "task_readiness",
  "label": "Task Readiness",
  "field_type": "text",
  "ui_visibility": "always",
  "description": "draft | needs-alignment | ready | blocked",
  "board_ids": ["<board-uuid>"]
}
```

On Plane, custom fields exist on issues and are configured via
`scripts/plane-setup-members.sh` or the Plane API.

The sync worker (`fleet/core/plane_sync.py`) already handles custom
field synchronization between platforms.

---

## Iterative

This document will grow as more custom fields are identified during
the design of the immune system, teaching system, conversation protocol,
and other protocols. Each new field will be added here with the same
structure: PO requirement (verbatim if available), field definition,
who can change it, purpose.