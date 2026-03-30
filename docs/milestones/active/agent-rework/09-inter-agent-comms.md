# Inter-Agent Communication

**Date:** 2026-03-30
**Status:** Design
**Part of:** Agent Rework (document 9 of 13)

---

## PO Requirements (Verbatim)

> "just like the PM would probably talk to the architect and the software
> engineer or whoever of concern in order to move forward the progress of
> the tasks."

---

## How Agents Communicate

Three surfaces for inter-agent communication:

### Task Comments
- Specific to a task
- PM posts assignment reasoning
- Engineers post progress, questions
- fleet-ops posts review feedback
- Architect posts design guidance

### Board Memory (fleet_chat)
- Fleet-wide visibility
- @mentions target specific agents
- Decisions, alerts, knowledge sharing
- Tagged for filtering

### IRC (#fleet, #reviews, #alerts)
- Real-time notifications
- Visible to human in The Lounge
- Automated event notifications

---

## Communication Patterns

### PM → Agent (assignment)
PM assigns a task and posts a comment explaining what's needed and why
this agent was chosen.

### Agent → PM (questions)
Agent is in conversation stage and needs clarity. Posts task comment
or fleet_chat mentioning PM.

### PM → Architect (design request)
PM creates a design task, assigns to architect, posts context about
why architecture input is needed.

### Architect → Engineers (guidance)
Architect posts design decisions to board memory or task comments.
Engineers see this in their pre-embedded context.

### Agent → fleet-ops (escalation)
Agent uses fleet_escalate when stuck or unsure. fleet-ops evaluates
and responds.

### fleet-ops → Agent (review feedback)
fleet-ops rejects with specific feedback. Agent sees the rejection
in their task context.

---

## What Needs Building

Agents currently can fleet_chat and post comments. What's missing:
- Agents don't actually USE fleet_chat in their heartbeats
- Agents don't read task comments from other agents
- The pre-embedded data should include recent comments on assigned tasks
- Agents should proactively communicate, not just when asked