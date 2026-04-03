# Diagrams — Visual Validation of Fleet Architecture

**Date:** 2026-03-30
**Status:** Design — ASCII diagrams for validation and reference
**Part of:** Fleet Elevation (document 25 — added to series)

---

## PO Requirements (Verbatim)

> "we will need to write diagrams too. part of what I said."

> "a general review and simulation and diagram writing in order to
> validate the flow and logic"

---

## 1. System Architecture — Complete Relationship Map

```
                        ┌─────────┐
                        │   PO    │
                        │ (Human) │
                        └────┬────┘
                 ┌───────────┼───────────┐
                 ↓           ↓           ↓
           ┌─────────┐ ┌─────────┐ ┌──────────┐
           │  Plane   │ │  OCMC   │ │   ntfy   │
           │(Project) │ │(Board)  │ │  (Push)  │
           └────┬─────┘ └────┬────┘ └──────────┘
                │            │            ↑
                │     ┌──────┴──────┐     │
                │     │             │     │
           ┌────┴─────┴─┐    ┌─────┴─────┴──┐
           │  Sync Layer │    │    Brain     │
           │  (plane_    │    │(Orchestrator)│
           │   sync.py)  │    │  30s cycle   │
           └─────────────┘    └──────┬───────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
        ┌─────┴──────┐        ┌─────┴──────┐        ┌─────┴──────┐
        │  Chain     │        │  Logic     │        │  Lifecycle │
        │  Registry  │        │  Engine    │        │  Manager   │
        │ (handlers) │        │ (dispatch) │        │(sleep/wake)│
        └─────┬──────┘        └─────┬──────┘        └─────┬──────┘
              │                     │                      │
              ↓                     ↓                      ↓
        ┌──────────┐         ┌──────────┐          ┌──────────┐
        │  Event   │         │  Context │          │  Budget  │
        │  Bus     │         │  Writer  │          │  Monitor │
        │ (~50 evt)│         │(pre-embed)│          │(OAuth API)│
        └────┬─────┘         └────┬─────┘          └──────────┘
             │                    │
             ↓                    ↓
        ┌──────────┐     ┌────────────────┐
        │  IRC     │     │   Agent Files  │
        │ #fleet   │     │  context/*.md  │
        │ #alerts  │     └───────┬────────┘
        │ #reviews │             │
        │ #gates   │             ↓
        └──────────┘     ┌────────────────┐
                         │    Gateway     │
                         │  (OpenClaw)    │
                         │  Heartbeat +   │
                         │  Sessions      │
                         └───────┬────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │         │        │        │         │
         ┌────┴───┐┌───┴───┐┌──┴───┐┌──┴────┐┌──┴────┐
         │  PM   ││ Ops  ││ Arch ││  Eng  ││  QA   │ ...
         │       ││      ││      ││       ││       │
         └───────┘└──────┘└──────┘└───────┘└───────┘
              10 Agents (each: IDENTITY + SOUL +
              CLAUDE.md + TOOLS.md + HEARTBEAT.md)
```

Key data flows:
- PO → Plane (requirements) → Sync → OCMC (tasks)
- Brain → Context Writer → Agent Files → Gateway → Agents
- Agents → MCP Tools → Tool Trees → MC + Plane + IRC + Events
- Brain → Lifecycle → Gateway (sleep/wake commands)
- Events → Chain Registry → Handlers → More Events (cascade)
- Budget Monitor → Brain (pause/continue decisions)

---

## 2. Task State Machine

```
                    ┌──────────────────────────────────┐
                    │                                  │
                    ↓                                  │
              ┌──────────┐                             │
 Created ────→│  INBOX   │                             │
              │          │                             │
              │ PM sets: │                             │
              │ type,    │                             │
              │ stage,   │                             │
              │ agent,   │                             │
              │ phase    │                             │
              └────┬─────┘                             │
                   │ Brain dispatches                  │
                   │ (10 gates pass)                   │
                   ↓                                   │
              ┌──────────┐                             │
              │IN_PROGRESS│←───────────────────────┐   │
              │          │                         │   │
              │ Agent    │  Rejected:              │   │
              │ works    │  readiness regressed    │   │
              │ through  │  stage reverted         │   │
              │ stages   │  specific feedback      │   │
              └────┬─────┘                         │   │
                   │ fleet_task_complete            │   │
                   │ (creates PR, approval)         │   │
                   ↓                                │   │
              ┌──────────┐                         │   │
              │  REVIEW  │─── Rejected ────────────┘   │
              │          │                             │
              │ Fleet-ops│                             │
              │ + QA     │                             │
              │ + DevSec │                             │
              │ + Trail  │                             │
              └────┬─────┘                             │
                   │ Approved                          │
                   ↓                                   │
              ┌──────────┐                             │
              │   DONE   │                             │
              │          │                             │
              │ Trail    │── PO regresses ─────────────┘
              │ finalized│   (any time, any amount)
              │ Sprint   │
              │ updated  │
              └──────────┘
```

---

## 3. Methodology Stage Progression

```
 ┌───────────────┐     ┌──────────┐     ┌───────────────┐
 │ CONVERSATION  │────→│ ANALYSIS │────→│ INVESTIGATION │
 │               │     │          │     │               │
 │ Discuss w/ PO │     │ Examine  │     │ Research      │
 │ Clarify reqs  │     │ codebase │     │ options       │
 │ Ask questions │     │ Findings │     │ Tradeoffs     │
 │               │     │ document │     │ Multiple opts │
 │ NO code       │     │ NO solve │     │ NO decide     │
 │ Readiness:    │     │ Readiness│     │ Readiness:    │
 │ 0% → 20%     │     │ 20%→40%  │     │ 40% → 60%    │
 └───────────────┘     └──────────┘     └──────┬────────┘
                                               │
                    ┌──────────────────────────┘
                    ↓
 ┌───────────────┐               ┌──────────────────┐
 │   REASONING   │──── 90% ────→ │      WORK        │
 │               │   PO GATE     │                  │
 │ Plan approach │   (blocking)  │ Execute plan     │
 │ Ref verbatim  │               │ fleet_commit     │
 │ Target files  │               │ fleet_complete   │
 │ Accept crit.  │               │ Stay in scope    │
 │               │               │                  │
 │ NO implement  │               │ Readiness:       │
 │ Readiness:    │               │ 99% → 100%       │
 │ 60% → 90%    │               │                  │
 └───────────────┘               └──────────────────┘

     ← ← ← Rejection can send back to ANY stage ← ← ←
         (PO or fleet-ops decides which stage)

 Not every task goes through every stage:
   epic:    conversation → analysis → investigation → reasoning → work
   story:   conversation → reasoning → work
   task:    reasoning → work
   bug:     analysis → reasoning → work
   spike:   conversation → investigation → reasoning (no work)
```

---

## 4. Contribution Flow

```
 Task enters REASONING stage
          │
          ↓
    ┌─────────────────────────────────────────────┐
    │           BRAIN: Chain Registry             │
    │  Event: fleet.methodology.stage_changed     │
    │  Handler: create_contribution_opportunities │
    └──────────────────┬──────────────────────────┘
                       │
          ┌────────────┼────────────┬─────────────┐
          ↓            ↓            ↓             ↓
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ Architect│ │    QA    │ │ DevSecOps│ │    UX    │
    │  design  │ │   test   │ │ security │ │   spec   │
    │  input   │ │   def    │ │   reqs   │ │  (if UI) │
    └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
         │            │            │             │
         │  PARALLEL  │            │             │
         │ (all work  │            │             │
         │  at once)  │            │             │
         ↓            ↓            ↓             ↓
    fleet_contribute  fleet_contribute  fleet_contribute  fleet_contribute
         │            │            │             │
         └────────────┴────────────┴─────────────┘
                       │
                       ↓
              ┌────────────────┐
              │  BRAIN checks: │
              │  All required  │
              │  contributions │
              │  received?     │
              └───────┬────────┘
                  YES │ NO
              ┌───────┴───────┐
              ↓               ↓
        PM notified      PM notified
        "Ready for       "Missing:
         90% gate"       QA tests"
              │
              ↓
        PO approves
        at 90% gate
              │
              ↓
        Task advances
        to WORK stage
        (engineer's context
         includes ALL
         contributions)
```

---

## 5. Agent Lifecycle (Sleep/Wake)

```
                    ┌──────────┐
 Task assigned ────→│  ACTIVE  │←── Prompt wake
                    │          │    (mention, task,
                    │ Real     │     contribution,
                    │ Claude   │     PO directive)
                    │ sessions │
                    └────┬─────┘
                         │ Task completes
                         │ HEARTBEAT_OK ×1
                         ↓
                    ┌──────────┐
                    │   IDLE   │←── Gradual wake
                    │          │    (general activity,
                    │ Real     │     role data changed)
                    │ heartbeat│
                    │ 30min    │
                    └────┬─────┘
                         │ HEARTBEAT_OK ×2
                         ↓
                    ┌──────────┐
                    │  IDLE  │
                    │          │
                    │ Reduced  │
                    │ heartbeat│
                    │ Brain    │
                    │ evaluates│
                    └────┬─────┘
                         │ HEARTBEAT_OK ×3+
                         │ or brain says nothing new
                         ↓
                    ┌──────────┐
                    │ SLEEPING │
                    │          │
                    │ NO Claude│
                    │ calls    │
                    │          │
                    │ Brain    │
                    │ evaluates│
                    │ every 30s│
                    │ for FREE │
                    └────┬─────┘
                         │ 4+ hours
                         ↓
                    ┌──────────┐
                    │ OFFLINE  │
                    │          │
                    │ Deep     │
                    │ sleep    │
                    │ Slow     │
                    │ wake     │
                    └──────────┘

   Cost:
     ACTIVE   = normal Claude cost (productive work)
     IDLE     = reduced Claude cost (30min intervals)
     IDLE   = minimal Claude cost (60min intervals)
     SLEEPING = $0 (brain evaluates in Python)
     OFFLINE  = $0 (rare checks only)
```

---

## 6. Tool Call Tree (fleet_task_complete)

```
 Agent calls: fleet_task_complete(summary)
         │
         ├──→ git.push(branch)
         │
         ├──→ github.create_pr(branch, title, body)
         │
         ├──→ mc.update_task(status=review, pr_url, branch)
         │         │
         │         ├──→ mc.post_comment(completion_summary)
         │         │
         │         ├──→ mc.create_approval(task_id)
         │         │
         │         └──→ plane_sync.update_issue(status, labels)
         │
         ├──→ irc.send(#reviews, "review needed")    ─┐
         │                                             │ PARALLEL
         ├──→ irc.send(#fleet, "completed")           ─┘
         │
         ├──→ events.emit("fleet.task.completed")
         │
         ├──→ mc.post_memory(trail: "completed")
         │
         ├──→ notify_contributors(QA, DevSecOps)
         │         ├──→ mc.post_memory(mention:qa)
         │         └──→ mc.post_memory(mention:devsecops)
         │
         └──→ evaluate_parent(parent_id)
                   ├──→ mc.list_tasks(children)
                   ├──→ if ALL done:
                   │      ├──→ mc.update_task(parent, review)
                   │      ├──→ mc.post_comment(parent, summary)
                   │      └──→ mc.create_approval(parent)
                   └──→ else:
                          └──→ mc.post_comment(parent, progress)
```

---

## 7. Dispatch Decision Tree (10 Gates)

```
 Task candidate for dispatch
         │
         ├─ Gate 1: Fleet mode allows dispatch?
         │    NO → "Fleet {mode} blocks dispatch"
         │    YES ↓
         ├─ Gate 2: Agent active for cycle phase?
         │    NO → "Agent not active in {phase}"
         │    YES ↓
         ├─ Gate 3: Task unblocked?
         │    NO → "Blocked by {tasks}"
         │    YES ↓
         ├─ Gate 4: Agent online?
         │    NO → "Agent offline"
         │    YES ↓
         ├─ Gate 5: Agent not busy?
         │    NO → "Agent busy with {task}"
         │    YES ↓
         ├─ Gate 6: Doctor cleared?
         │    NO → "Doctor: agent flagged"
         │    YES ↓
         ├─ Gate 7: Readiness appropriate for stage?
         │    NO → "Work needs readiness ≥ 99"
         │    YES ↓
         ├─ Gate 8: PO gate passed?
         │    NO → "PO gate at 90% not approved"
         │    YES ↓
         ├─ Gate 9: Required contributions received?
         │    NO → "Missing: QA tests, architect design"
         │    YES ↓
         ├─ Gate 10: Phase prerequisites met?
         │    NO → "Phase {phase} standards not met"
         │    YES ↓
         │
         └─→ DISPATCH: build autocomplete chain,
              write context, notify, emit events
```

---

## 8. Immune System Flow

```
 Orchestrator Cycle — Step 2: Doctor
         │
         ↓
 ┌──────────────────────┐
 │ For each active task  │
 │ with assigned agent:  │
 └──────────┬───────────┘
            │
            ├──→ detect_protocol_violation(agent, stage, tools)
            ├──→ detect_laziness(agent, task, time, criteria)
            ├──→ detect_stuck(agent, task, inactivity)
            ├──→ detect_correction_threshold(agent, corrections)
            ├──→ detect_contribution_avoidance(agent, opportunities)
            ├──→ detect_synergy_bypass(agent, required, received)
            ├──→ detect_phase_violation(task, phase, standards)
            └──→ detect_trail_gap(task, trail, required)
                      │
                      ↓
              ┌───────────────┐
              │  Detections?  │
              └───────┬───────┘
               NO     │ YES
               │      ↓
               │  ┌────────────────────┐
               │  │ decide_response()  │
               │  │ severity × history │
               │  └────────┬───────────┘
               │           │
               │    ┌──────┼──────┬──────────┐
               │    ↓      ↓      ↓          ↓
               │  TEACH  COMPACT  PRUNE   ESCALATE
               │    │      │       │         │
               │    ↓      ↓       ↓         ↓
               │  adapt   force   kill     notify
               │  lesson  compact session   PO
               │    │      │       │
               │    ↓      ↓       ↓
               │  inject  gateway  gateway
               │  into    compact  delete
               │  session          + regrow
               │    │
               │    ↓
               │  Agent must
               │  complete exercise
               │  before continuing
               │    │
               │    ├─→ Comprehension verified → cleared
               │    └─→ No change (×3) → PRUNE
               │
               ↓
         DoctorReport:
           agents_to_skip (dispatch blocked)
           tasks_to_block
           interventions executed

    *** HIDDEN from agents — they don't see the doctor ***
```

---

## 9. PO Governance — Gate Flow

```
 Task readiness approaching gate
         │
         ↓
 PM calls fleet_gate_request(task_id, "readiness_90", summary)
         │
         ├──→ mc.post_memory(tags: [gate, po-required])
         ├──→ irc.send(#gates, "PO approval needed")
         ├──→ ntfy.send(PO, "Gate: readiness 90%")
         └──→ task flagged: gate_pending = "readiness_90"
                   │
                   ↓
         ┌────────────────────┐
         │   PO decides       │
         │   (via board memory│
         │    or direct OCMC) │
         └────────┬───────────┘
                  │
          ┌───────┼───────┐
          ↓       ↓       ↓
       APPROVE  REJECT  REGRESS
          │       │       │
          ↓       ↓       ↓
     readiness  readiness  readiness
     → 99%     stays     → PO value
     stage     same      stage
     → work    feedback  reverts
               posted    feedback
                         posted
```

---

## Diagrams Not Yet Written (Future)

The following diagrams from document 19 still need to be produced
during implementation:

10. **Two-axis diagram:** stages × phases matrix showing how a
    deliverable moves through both dimensions simultaneously

11. **Synergy matrix visual:** the contribution matrix from doc 15
    as a visual grid (who → whom → what → when)

12. **Communication map:** which agent talks to which via which bus
    (task comments, board memory, IRC, fleet_chat, fleet_contribute)

13. **Orchestrator cycle detail:** the 12 steps with data flow arrows
    between them

14. **Data flow diagram:** how data flows from PO requirement →
    task fields → agent context → agent output → review → approval

15. **Onion architecture:** inner (identity) → middle (rules) →
    outer (dynamic) for agent context layering

These will be produced as implementation progresses and the actual
data flows are verified against running infrastructure.

---

## Open Questions

- Should diagrams be auto-generated from system state? (Live
  architecture diagram that reflects actual configuration?)
- What format for final diagrams? (Mermaid for git, ASCII for agent
  context, rendered PNG for Plane pages?)
- Should agents receive relevant diagrams in their context to
  understand the system they operate in?