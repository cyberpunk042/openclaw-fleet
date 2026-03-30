# Pre-Embedded Data — Full Context Per Role

**Date:** 2026-03-30
**Status:** Design — what each agent gets before they start thinking
**Part of:** Agent Rework (document 2 of 13)

---

## PO Requirements (Verbatim)

> "it must be pre-embedded into its heartbeat with not only the ocmc board
> but also the related plane data if connected and existing."

> "I NEVER SAID WE WERE GOING TO INJECT A COMPACTED VERSION OF THE DATA"

> "THE GOAL OF CALLING A TOOL IS TO AGGREGATE ANOTHER TRAIL OR LARGER OR
> WHATNOT... NOT TO GATHER WHAT WE ALREADY KNOW WE ABSOLUTELY NEED"

---

## Principle: FULL, Not Compressed

The pre-embedded data is the FULL data the agent needs. Not a summary.
Not a 300-char teaser. The COMPLETE data set for this agent's role.

MCP group calls (fleet_task_context, fleet_heartbeat_context) are for
aggregating ADDITIONAL data — pulling in a different task's context,
getting a cross-task view, fetching data that isn't part of the
standard pre-embed for this role. NOT for getting what should already
be there.

The current preembed.py builds compressed summaries. This is the
compression disease injected into the code. It needs complete rewrite.

---

## What Each Role Gets Pre-Embedded

### Project Manager — Full Board View

The PM gets EVERYTHING about the board:

```
ALL inbox tasks (each with):
  - id, title, description (full, not truncated)
  - assigned agent (or "UNASSIGNED")
  - task_type, task_stage, task_readiness
  - requirement_verbatim (full text)
  - story_points, priority, complexity
  - is_blocked, blocked_by
  - plane_issue_id (if linked)
  - last comment (most recent, who said what)
  - artifact completeness (if artifact exists)

Sprint metrics:
  - Tasks by status: inbox / in_progress / review / done (counts + lists)
  - Story points: completed / remaining
  - Blocked tasks list
  - Velocity (points per cycle period)

Agent status:
  - Each agent: name, status (online/offline), current task (if any),
    idle time, last heartbeat

Plane data (if connected):
  - Current sprint/cycle: name, dates, status
  - Sprint issues with priorities
  - New issues not yet on OCMC
  - Module progress

PO directives: full content of each directive
Messages: full content of each @pm or @all message
Events: significant events since last heartbeat
```

### Fleet-Ops — Full Quality View

```
Approval queue (each with):
  - approval_id, task_id, task_title
  - verbatim requirement (full text)
  - acceptance criteria (full list)
  - completion summary
  - PR URL, diff summary
  - agent who did the work
  - story_points, time to complete
  - methodology stage history (did it go through right stages?)
  - artifact completeness at completion

Review queue:
  - Tasks in review status with time in review

Health indicators:
  - Doctor findings: diseases detected, actions taken
  - Agent health profiles: who's been pruned, who's in lessons
  - Stale tasks (in any status too long)
  - Offline agents with assigned work

Budget:
  - Token usage current period
  - Budget alerts if any
  - Usage trend (increasing/stable/decreasing)

Board state:
  - Tasks by status with counts
  - Blocker count and list

Messages: @lead mentions, escalations
Events: completions, rejections, mode changes, prunes
```

### Architect — Full Design View

```
Assigned tasks (each with):
  - Full task context
  - Current artifact state (what was done, what's missing, completeness)
  - Verbatim requirement
  - Stage and stage instructions

Tasks needing architecture review:
  - Tasks with architecture implications (tagged or high complexity)
  - Design questions from other agents (from comments or messages)

Recent design decisions:
  - Board memory entries tagged [architecture, decision]
  - Architect's own previous findings/plans

Messages: design questions from engineers and PM
```

### DevSecOps — Full Security View

```
Assigned security tasks with full context
PRs needing security review:
  - PR URL, diff summary, what was changed, by whom
  - Task linked to PR
Security alerts:
  - Behavioral security findings
  - Dependency vulnerability flags
Infrastructure health indicators
Messages: security mentions
Events: security-tagged events
```

### Workers (engineer, devops, qa, writer, ux, accountability)

```
Assigned tasks (each with):
  - Full task context: title, description, verbatim requirement
  - Current stage and stage instructions (full protocol text)
  - Readiness percentage
  - Artifact state: structured object, what's done, what's missing,
    completeness percentage, suggested readiness
  - Comments on this task (progressive work trail from all participants)
  - Related tasks: parent, children, dependencies
  - Plane issue data (if linked)

Messages: @mentions for this agent
Directives: PO orders targeting this agent
Fleet state: mode, phase (in case it affects behavior)
```

---

## Delivery Mechanism

### Current: context/ files (limited)

The gateway reads files from `agents/{name}/context/` and includes
them in the agent's system prompt. Max ~1000 chars per file.

This is too small for full pre-embedded data. The PM needs the entire
board state — that's potentially 10KB+ of data.

### Option A: Multiple context files

Split the data across multiple files:
- `context/01-tasks.md` — task list
- `context/02-sprint.md` — sprint metrics
- `context/03-agents.md` — agent status
- `context/04-messages.md` — messages and directives
- `context/05-plane.md` — Plane data

Each file ~1000 chars. 5 files = 5000 chars. May be enough for
compact representation.

### Option B: Gateway chat.send injection

Use the gateway's `chat.send` to inject data as a message into the
agent's session before the heartbeat executes. No size limit.

### Option C: System prompt extension

Modify the gateway to accept larger system prompt data. The gateway
builds the system prompt from agent.yaml + CLAUDE.md + context/ files.
Could add a larger data section.

### Which to use?

Needs investigation:
- Does the gateway have a hard limit on total system prompt size?
- Does chat.send data persist across turns within a session?
- Can multiple context files be read simultaneously?

The answer determines the implementation approach.

---

## What preembed.py Becomes

The current preembed.py builds 300-char summaries. It needs to become:

```python
def build_full_heartbeat_data(agent_name, role, ...) -> str:
    """Build FULL pre-embedded data for this agent's role.

    Not compressed. Not summarized. The complete data set.
    Format: structured markdown that the AI reads naturally.
    """
    # Uses context_assembly but renders to full markdown
    # NOT truncated, NOT summarized
```

The format should be structured markdown — headers, lists, details —
that the AI reads as part of its context and naturally acts on.

---

## Open Questions

- What's the actual gateway limit for system prompt / context data?
- Should the format be markdown or JSON? Markdown is natural for AI
  but JSON is precise for structured data.
- How often does pre-embed data refresh? Every heartbeat? Only when
  orchestrator wakes the agent?
- Should HEARTBEAT.md reference the pre-embedded data by section?
  "Read your TASK LIST section for unassigned tasks."