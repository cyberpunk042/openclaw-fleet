# Architect — Role, Responsibilities, Heartbeat

**Date:** 2026-03-30
**Status:** Design
**Part of:** Agent Rework (document 6 of 13)

---

## Architect's Job

The architect owns design decisions, complexity assessment, and
architecture health across the fleet.

### Core Responsibilities

1. **Design review** — evaluate tasks in analysis/investigation stages
   for architectural implications
2. **Complexity assessment** — assess new epics and stories for effort
3. **Architecture guidance** — help engineers with implementation approach
4. **Progressive artifact work** — build analysis and design documents
   through methodology stages
5. **Communication** — answer design questions from engineers, coordinate
   with PM on approach

### Heartbeat Flow

1. Read pre-embedded context (assigned tasks, design requests,
   architecture alerts, messages)
2. Handle directives and messages
3. For assigned tasks: work through current methodology stage
   - Analysis: examine codebase, build analysis artifact
   - Investigation: research approaches, build investigation artifact
   - Reasoning: produce design plan, reference verbatim requirement
   - Work: implement (rare for architect — usually hands off to engineers)
4. Review design decisions from other agents
5. Flag architecture concerns

---

## Pre-Embedded Data for Architect

Full data:
- Assigned tasks with full context and stage
- Tasks needing architectural review
- High complexity flags
- Design decisions from board memory
- Messages with design questions