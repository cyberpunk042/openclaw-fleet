# Three Systems at Runtime — How They Work Together

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Scope:** How the immune system, teaching system, and methodology system
interact during fleet operation

---

## The Three Systems

| System | Role | Analogy |
|--------|------|---------|
| **Methodology** | Defines stages, protocols, checks | The curriculum |
| **Immune** | Observes, reports, acts | The immune system |
| **Teaching** | Adapts and responds with lessons | The teacher |

These are separate systems (SRP) that collaborate through clear
interfaces.

---

## The Chain

```
Methodology defines what SHOULD happen
  ↓
Agent works (following or violating the methodology)
  ↓
Immune system OBSERVES agent behavior
  ↓
Disease detected?
  ├── NO → continue, agent is healthy
  └── YES → immune system REPORTS and ACTS
        ↓
      What response?
        ├── Force compact → strip context, agent continues
        ├── Trigger teaching → teaching system takes over
        │     ↓
        │   Teaching adapts lesson to disease + task + agent
        │     ↓
        │   Agent practices the right path
        │     ↓
        │   Comprehension verified?
        │     ├── YES → agent returns to work
        │     └── NO (no change) → report back to immune
        │           ↓
        │         Prune → agent grows back fresh
        └── Prune directly → too sick for teaching
```

---

## Runtime Scenario: Normal Healthy Agent

1. Task created in Plane by PO. Readiness: 0%.
2. PO writes verbatim requirement.
3. PM evaluates task, sets task_stage to "conversation" or later.
4. Agent is dispatched for conversation stage.
5. Agent discusses with PO via task comments. Readiness increases.
6. PO confirms understanding. Stage advances to analysis.
7. Agent analyzes codebase. Produces analysis document. PO reviews.
8. Stage advances to investigation. Agent researches. PO reviews.
9. Stage advances to reasoning. Agent produces plan. PO confirms.
10. Readiness reaches 99%. Stage advances to work.
11. Agent executes. Commits code. Creates PR.
12. Immune system observes throughout — no disease detected.
13. Agent calls fleet_task_complete. Review chain processes.
14. Done.

No immune system intervention needed. No teaching needed. The
methodology guided the agent through stages, the agent followed
protocols, work was produced correctly.

---

## Runtime Scenario: Agent Deviates During Work

1. Task at work stage, readiness 99%. Agent dispatched.
2. Agent reads requirement: "Add fleet controls to header bar."
3. Agent starts building a sidebar page instead.
4. **Immune system detects:** agent's plan (from fleet_task_accept)
   mentions "sidebar" but verbatim requirement says "header bar."
   Disease: deviation (potentially Z-when-A).
5. **Immune system acts:** triggers teaching.
6. **Teaching system activates:**
   - Adapts lesson: "Your requirement says 'header bar'. Your plan
     says 'sidebar'. Re-read the requirement. Map each term to a
     specific file and line. Produce a corrected plan."
   - Injects lesson into agent session via chat.send.
7. Agent processes lesson. Produces corrected plan referencing
   DashboardShell.tsx header section.
8. **Teaching verifies:** plan now matches requirement. Comprehension
   verified.
9. Agent returns to work with corrected understanding.
10. Agent builds FleetControlBar in the header. Correct.

Disease caught early (at plan stage). Teaching cured it. No prune
needed. Work completed correctly.

---

## Runtime Scenario: Agent Can't Learn

1. Same deviation detected as above.
2. Teaching system delivers adapted lesson.
3. Agent processes lesson but produces SAME wrong plan — sidebar again.
4. Teaching system: attempt 2, stronger lesson with more specific
   guidance.
5. Agent produces slightly different but still wrong plan.
6. Teaching system: attempt 3, no change in agent behavior.
7. **Teaching reports to immune system:** no change after 3 attempts.
8. **Immune system acts:** prune. Session killed.
9. Fresh session created. Task re-dispatched with verbatim requirement.
10. Fresh agent reads requirement, produces correct plan.
11. Continues to work protocol. Builds correctly.

Teaching tried. Agent couldn't learn. Pruning cured by removing the
contaminated context entirely.

---

## Runtime Scenario: Agent Violates Protocol

1. Task at analysis stage. Agent dispatched for analysis.
2. Agent reads task, starts writing code instead of producing analysis.
3. **Immune system detects:** agent called fleet_commit during analysis
   stage. Protocol violation.
4. **Immune system acts:** triggers teaching.
5. **Teaching system activates:**
   - Adapts lesson: "Your task is in analysis stage. Analysis protocol
     means reading and examining, producing analysis documents. Not
     writing code. What stage is your task in? What does the protocol
     for that stage allow?"
   - Injects lesson.
6. Agent processes lesson. Acknowledges wrong protocol. Reverts code.
   Produces analysis document instead.
7. **Teaching verifies:** agent now producing stage-appropriate artifacts.
8. Agent continues in analysis protocol. No prune needed.

---

## Runtime Scenario: Agent Is Lazy

1. Task at work stage. Requirement says "update all 7 call sites."
2. Agent updates 3 call sites, calls fleet_task_complete.
3. **Immune system detects:** laziness. Acceptance criteria says 7,
   agent only addressed 3. Methodology check for work stage fails.
4. **Immune system acts:** force compact + trigger teaching.
5. Force compact strips accumulated context (agent may have gotten
   distracted by other code it was reading).
6. **Teaching system activates:**
   - Adapts lesson: "Task requires updating 7 call sites. You updated
     3. List all 7 files. Show the remaining 4 that need changes."
   - Injects lesson.
7. Agent lists all 7, identifies remaining 4, continues work.
8. Agent completes all 7. Calls fleet_task_complete again.
9. Immune system checks: 7/7 addressed. Passes.

---

## Runtime Scenario: Agent Is Stuck

1. Task at work stage. Agent dispatched.
2. Agent has been working for 45 minutes. No commits. No tool calls.
   Burning tokens in reasoning loops.
3. **Immune system detects:** stuck/spinning. No progress signals.
4. **Immune system acts:** force compact. (No teaching needed — agent
   isn't misbehaving, just struggling.)
5. Context reduced: dead-end reasoning stripped, verbatim requirement
   and work-so-far preserved.
6. Agent continues with lean context. Fresh perspective.
7. Agent finds the solution, commits, continues.

No lesson. No prune. Just maintenance — cleaning up a bloated context
so the agent can think clearly again.

---

## Data Flow Between Systems

```
Methodology System
  │
  ├── Defines: stages, protocols, checks per task/module
  ├── Tracks: task_stage custom field, readiness percentage
  ├── Emits: fleet.methodology.* events
  │
  └── Immune System reads methodology to know what SHOULD happen
        │
        ├── Observes: agent behavior (MCP tools, git, events)
        ├── Compares: behavior against methodology expectations
        ├── Detects: disease (deviation, laziness, protocol violation, etc.)
        ├── Emits: fleet.immune.* events
        │
        ├── Acts: force compact (via gateway sessions.compact)
        ├── Acts: prune (via gateway sessions.delete)
        └── Acts: trigger teaching
              │
              └── Teaching System receives disease info + task + agent
                    │
                    ├── Adapts: lesson to specific situation
                    ├── Injects: via gateway chat.send or context/ files
                    ├── Verifies: through practice exercises
                    ├── Emits: fleet.teaching.* events
                    │
                    └── Reports outcome to immune system
                          ├── Comprehension verified → agent returns
                          └── No change → immune system prunes
```

---

## Custom Fields Across Systems

| Field | System | Purpose |
|-------|--------|---------|
| task_readiness (0-100) | Methodology | Gates work protocol entry at 99-100% |
| task_stage | Methodology | Current protocol stage |
| requirement_verbatim | All three | Anchor for detection, teaching, and protocol compliance |

The verbatim requirement is used by ALL three systems:
- Methodology: checks that plans reference the requirement
- Immune: compares agent output against the requirement for deviation detection
- Teaching: uses the requirement in adapted lessons for practice exercises

---

## What the PO Sees

Through the OCMC vendor UI (G milestones):
- Task cards show stage and readiness percentage
- Event stream shows immune/teaching/methodology events color-coded
- Dashboard shows fleet health: agents healthy/sick/in-lesson/pruned
- Agent interventions visible: what the doctor did, what lessons were given
- Readiness editable by PO directly in the UI
- Full history of stage progressions, lessons, prunes per agent and task

The PO is always in control. The three systems operate autonomously but
the PO can see everything and intervene at any point — change readiness,
override stages, direct agents through conversation.

---

## Document Index

### Immune System (7 documents)
- `immune-system/01-overview.md` — what it is, why, diseases, principles
- `immune-system/02-the-doctor.md` — the doctor, its tools, gateway APIs, hiddenness
- `immune-system/03-disease-catalogue.md` — 14 diseases with evidence
- `immune-system/04-research-findings.md` — academic and practical evidence
- `immune-system/05-detection.md` — signals, data sources, detection cycle
- `immune-system/06-response.md` — escalation logic, what happens to work, PO override
- `immune-system/07-integration.md` — technical interfaces, existing system mapping

### Teaching System (1 document)
- `teaching-system/01-overview.md` — adapted lessons, practice-based verification, examples per disease

### Methodology System (8 documents)
- `methodology-system/01-overview.md` — stages, protocols, module-level methodology
- `methodology-system/02-conversation-protocol.md` — discussing with PO
- `methodology-system/03-analysis-protocol.md` — examining what exists
- `methodology-system/04-investigation-protocol.md` — researching what's possible
- `methodology-system/05-reasoning-protocol.md` — planning the approach
- `methodology-system/06-work-protocol.md` — executing, mapped to existing fleet lifecycle
- `methodology-system/07-standards-and-examples.md` — what "done right" looks like
- `methodology-system/new-custom-fields.md` — field definitions + Plane state integration

### Planning
- `milestone-plan-three-systems.md` — 44 milestones across 7 categories, detailed
- `fleet-control-surface.md` — header bar UI, three control axes
- `three-systems-runtime.md` — this document