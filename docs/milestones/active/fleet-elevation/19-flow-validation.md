# Flow Validation — Diagrams and Simulation

**Date:** 2026-03-30
**Status:** Design — validating the logic works end to end
**Part of:** Fleet Elevation (document 19 of 22)

---

## PO Requirements (Verbatim)

> "a general review and simulation and diagram writing in order to
> validate the flow and logic... a lot of work. a lots of document and
> changes and augmentations."

---

## What This Document Covers

Flow diagrams and logical simulations that prove the fleet's task
lifecycle works correctly end to end. Every state transition, every
chain, every gate — validated through walkthroughs.

---

## Flow 1: Simple Task (Story, MVP Phase)

```
PO creates "Add search endpoint" in Plane
│
├─ Plane sync → OCMC inbox (stage: unset, readiness: 0, phase: mvp)
│
├─ PM heartbeat:
│   ├─ Sets: type=story, stage=conversation, readiness=5%
│   ├─ Sets: agent=software-engineer, points=5, phase=mvp
│   ├─ Sets: verbatim from Plane description
│   └─ Comment: "Assigned to engineer. Stage: conversation."
│
├─ Brain dispatch → engineer gets task
│   └─ Engineer context: conversation protocol, verbatim requirement
│
├─ CONVERSATION (readiness 5→20%):
│   ├─ Engineer posts questions as comments
│   ├─ PO responds with clarifications
│   ├─ Verbatim refined
│   └─ PM advances stage → analysis (readiness 20%)
│
├─ ANALYSIS (readiness 20→40%):
│   ├─ Engineer examines codebase
│   ├─ Produces analysis_document artifact
│   ├─ Posts findings as comment
│   └─ PM advances stage → reasoning (readiness 40%)
│
├─ REASONING (readiness 40→90%):
│   │
│   ├─ Brain fires: contribution chains
│   │   ├─ Creates: QA test predefinition task (auto)
│   │   ├─ Creates: architect design input task (auto)
│   │   └─ Creates: DevSecOps security requirement task (auto, mvp phase)
│   │
│   ├─ PARALLEL CONTRIBUTIONS:
│   │   ├─ Architect contributes design_input → propagates to task
│   │   ├─ QA contributes qa_test_definition → propagates to task
│   │   └─ DevSecOps contributes security_requirement → propagates to task
│   │
│   ├─ Engineer produces plan artifact (references verbatim)
│   ├─ Brain checks: all contributions received? YES
│   ├─ PM: readiness → 88%, routes gate request to PO
│   │
│   ├─ PO GATE (90%):
│   │   ├─ PO reviews plan + contributions
│   │   ├─ PO approves → readiness → 99%
│   │   └─ Stage → work
│   │
├─ WORK (readiness 99→100%):
│   ├─ Brain dispatch → engineer
│   │   └─ Context includes: architect design, QA tests, DevSecOps reqs
│   ├─ Engineer implements following plan
│   ├─ Engineer satisfies QA test criteria
│   ├─ Engineer follows DevSecOps requirements
│   ├─ fleet_commit × 3 (conventional commits)
│   └─ fleet_task_complete → CHAIN:
│       ├─ Push branch
│       ├─ Create PR
│       ├─ Status → review
│       ├─ Create approval for fleet-ops
│       ├─ Notify QA: validate tests
│       ├─ Notify DevSecOps: security review
│       ├─ IRC #reviews
│       └─ Event: fleet.task.completed
│
├─ REVIEW:
│   ├─ Fleet-ops review:
│   │   ├─ Verbatim match? ✓
│   │   ├─ Trail complete? ✓ (all stages, all contributions)
│   │   ├─ PO gate at 90%? ✓
│   │   ├─ MVP standards met? ✓
│   │   └─ Acceptance criteria evidenced? ✓
│   ├─ QA validation: 5/5 predefined tests addressed ✓
│   ├─ DevSecOps review: no security findings ✓
│   └─ Fleet-ops approves → CHAIN:
│       ├─ Status → done
│       ├─ Sprint progress updated
│       ├─ Trail finalized
│       ├─ Technical writer: update docs
│       ├─ Accountability: verify trail
│       └─ IRC #fleet: "Task completed"
│
└─ DONE
```

**Total agents involved:** PM, engineer, architect, QA, DevSecOps,
fleet-ops, technical writer, accountability = 8 of 10 agents.

**Total cycles:** ~8-12 orchestrator cycles (4-6 minutes real time
per cycle = 30-60 minutes for a story).

---

## Flow 2: Epic With Subtasks (Production Phase)

```
PO creates "Add user authentication system" (epic, production phase)
│
├─ PM heartbeat: type=epic, stage=conversation, readiness=0%
│
├─ CONVERSATION → ANALYSIS → INVESTIGATION → REASONING:
│   ├─ Architect designs full auth architecture (all stages)
│   ├─ PO refines requirements at each checkpoint
│   └─ Readiness: 0% → 10% → 30% → 50% (PO checkpoint) → 80%
│
├─ PM breaks epic into subtasks at reasoning stage:
│   ├─ "Design auth data model" → architect
│   ├─ "Implement JWT middleware" → engineer
│   ├─ "Add login/register endpoints" → engineer
│   ├─ "Write auth integration tests" → QA
│   ├─ "Security audit auth system" → DevSecOps
│   ├─ "Document auth API" → technical-writer
│   │
│   ├─ Dependencies:
│   │   design → implement middleware → implement endpoints
│   │   implement → tests, security audit, docs (parallel)
│   │
│   └─ All subtasks: phase=production, parent_task=epic
│
├─ PO GATE at 90% on epic: approves the plan
│
├─ SUBTASK EXECUTION (orchestrator manages):
│   │
│   ├─ "Design auth data model" dispatched to architect
│   │   ├─ Architect completes → subtask done
│   │   └─ Brain: unblocks "Implement JWT middleware"
│   │
│   ├─ "Implement JWT middleware" dispatched to engineer
│   │   ├─ Contributions created: QA tests, DevSecOps reqs (production)
│   │   ├─ All contributions include UX input (login has UI)
│   │   ├─ Engineer implements with full contribution context
│   │   ├─ Completes → review → approved
│   │   └─ Brain: unblocks "Add login/register endpoints"
│   │
│   ├─ "Add login/register endpoints" dispatched to engineer
│   │   ├─ Full contribution cycle
│   │   ├─ Completes → review → approved
│   │   └─ Brain: unblocks tests, security audit, docs
│   │
│   ├─ PARALLEL: tests, security, docs all dispatched
│   │   ├─ QA writes integration tests → completes
│   │   ├─ DevSecOps audits → completes (or sets security_hold)
│   │   └─ Technical writer documents → completes
│   │
│   └─ Brain: ALL subtasks done → epic moves to review
│
├─ EPIC REVIEW:
│   ├─ Fleet-ops reviews epic with aggregated child results
│   ├─ Production standards: complete coverage, security certified,
│   │   comprehensive docs, compliance verified
│   ├─ Accountability generator: full trail verification
│   └─ Approved → epic done
│
├─ PHASE ADVANCEMENT:
│   ├─ PM requests: "Auth system ready for production phase"
│   ├─ Brain checks production standards: ✓
│   └─ PO approves phase advancement
│
└─ DONE (production-certified)
```

---

## Flow 3: Rejection and Regression

```
Task "Implement search" at readiness 99%, work stage
Engineer calls fleet_task_complete
│
├─ Review:
│   ├─ Fleet-ops reads work
│   ├─ Finds: implementation uses different API than verbatim specified
│   ├─ Verbatim: "use Elasticsearch"
│   ├─ Implementation: uses custom SQL full-text search
│   └─ Fleet-ops REJECTS: "Implementation doesn't match verbatim.
│       Requirement says Elasticsearch. Return to reasoning."
│
├─ Rejection chain:
│   ├─ Status: review → in_progress
│   ├─ Readiness: 99% → 70% (moderate regression to reasoning)
│   ├─ Stage: → reasoning
│   ├─ Comment posted with rejection details
│   ├─ Event: fleet.approval.rejected
│   ├─ IRC #reviews: "[rejected] Implement search: verbatim mismatch"
│   ├─ Doctor signal: agent deviation on this task
│   └─ Trail: rejection recorded with reason and regression amount
│
├─ Engineer's next heartbeat:
│   ├─ Context: "Your task was REJECTED. Reason: Implementation uses
│   │   SQL full-text search but verbatim says 'use Elasticsearch.'
│   │   Regressed to reasoning stage at 70%."
│   ├─ Autocomplete chain: reasoning protocol, re-plan with Elasticsearch
│   └─ Engineer produces new plan → PO re-approves at 90% gate
│
├─ PO reviews at 90% gate:
│   ├─ Option A: approves new Elasticsearch plan → work resumes
│   ├─ Option B: PO changes requirement → "Actually, SQL is fine,
│   │   update verbatim" → engineer resumes with corrected verbatim
│   └─ Option C: PO regresses further → "Start over, I want
│       something different" → readiness → 0%
│
└─ Re-implementation → re-review → approved
```

---

## Flow 4: Phase Advancement (POC → MVP)

```
Deliverable "NNRT Search" at phase: poc
All POC tasks completed and approved
│
├─ PM evaluates MVP readiness:
│   ├─ POC standards met? ✓ (happy path works)
│   ├─ MVP standards needed:
│   │   - Tests: main flows + critical edges (currently: happy path only)
│   │   - Docs: setup + usage + API (currently: README only)
│   │   - Security: auth + validation (currently: basic only)
│   │
│   ├─ PM creates new tasks for MVP gap:
│   │   - "Add test coverage for search edge cases" → QA + engineer
│   │   - "Write search API documentation" → technical-writer
│   │   - "Add auth to search endpoint" → engineer + DevSecOps
│   │   - "Add input validation to search" → engineer
│   │   All tasks: phase=mvp, dependency: previous POC tasks
│   │
│   └─ PM routes gate request to PO:
│       "NNRT Search ready for POC→MVP advancement.
│        POC work complete. Gap analysis done. 4 new tasks created
│        for MVP standards. Requesting phase advancement to begin
│        MVP work."
│
├─ PO approves phase advancement:
│   ├─ Phase label: poc → mvp
│   ├─ New standards apply to all related tasks
│   ├─ Brain updates contexts for affected agents
│   ├─ Event: fleet.phase.advanced
│   └─ IRC #sprint: "[milestone] NNRT Search advanced to MVP"
│
├─ MVP work executes (new stage cycles for new tasks):
│   ├─ Each task goes through stages with MVP standards
│   ├─ Contributions created per MVP phase requirements
│   └─ Eventually all MVP tasks complete
│
├─ PM routes next phase gate:
│   "NNRT Search ready for MVP→staging. All MVP standards met."
│
└─ PO decides: advance or stay at MVP
```

---

## Flow 5: Immune System Intervention

```
Agent "software-engineer" working on task in work stage
Doctor runs detection during orchestrator cycle
│
├─ Detection: agent called fleet_commit during investigation stage
│   ├─ Disease: protocol_violation
│   ├─ Severity: medium
│   └─ Signal: "Work tools called during investigation stage"
│
├─ Response decision:
│   ├─ Agent health: first offense, no prior lessons
│   ├─ Decision: TRIGGER_TEACHING
│   └─ Intervention created
│
├─ Teaching chain:
│   ├─ adapt_lesson(PROTOCOL_VIOLATION, context={stage, tools})
│   ├─ Lesson: "Your task is in investigation stage. During
│   │   investigation, you may NOT commit code. You did: fleet_commit.
│   │   This is a protocol violation."
│   ├─ Exercise: "State what stage you're in. State what the protocol
│   │   allows. State what you did wrong."
│   └─ inject_content(session, lesson_text) via gateway
│
├─ Agent receives lesson in context:
│   ├─ Must complete exercise before returning to task
│   ├─ Demonstrates comprehension → lesson cleared
│   └─ OR fails → lesson repeats (max 3 attempts → prune)
│
├─ If prune triggered:
│   ├─ Session killed (gateway sessions.delete)
│   ├─ Agent regrows fresh (new session, clean context)
│   ├─ Task context preserved in files (artifacts, comments)
│   ├─ Agent picks up from persistent data
│   └─ Trail records: "Agent pruned: protocol violation"
│
└─ Hidden from agent: they don't know about the doctor
```

---

## Validation Checklist

For each flow above, verify:

- [ ] Every state transition is deterministic (brain handles it)
- [ ] Every gate has a clear authority (PO, PM, fleet-ops)
- [ ] Every chain fires correctly (event → handlers → effects)
- [ ] Every contribution is created at the right time
- [ ] Every standard is checked at the right phase
- [ ] Every notification goes to the right channel
- [ ] Every trail event is recorded
- [ ] The autocomplete chain leads to the correct action at each step
- [ ] Regression paths are clean (correct stage, correct readiness)
- [ ] The immune system detects violations without agent awareness

---

## Diagrams Required

> "we will need to write diagrams too. part of what I said."

> "a general review and simulation and diagram writing in order to
> validate the flow and logic"

The following formal diagrams need to be produced (Mermaid, ASCII,
or appropriate format) to validate the system visually:

### Architecture Diagrams
1. **System relationship map:** All 15+ systems with connections.
   PO → Plane → OCMC → Brain → Agents → Events → Systems.
2. **Onion architecture:** Inner (identity) → Middle (rules) →
   Outer (dynamic data) for agent context.
3. **Data flow:** How data flows from PO requirement → task fields →
   agent context → agent output → review → approval.

### Lifecycle Diagrams
4. **Task state machine:** inbox → in_progress → review → done with
   all transitions, including rejection/regression paths.
5. **Stage progression:** conversation → analysis → investigation →
   reasoning → work with gates and checkpoints.
6. **Phase progression:** ideal → conceptual → poc → mvp → staging →
   production with gates and standards.
7. **Two-axis diagram:** stages × phases showing how a deliverable
   moves through both dimensions.

### Chain Diagrams
8. **Event chain flow:** Event emitted → bus → handlers → effects →
   cascade events.
9. **Contribution chain:** task enters reasoning → brain creates
   contributions → agents produce → propagation → dispatch.
10. **Completion chain:** fleet_task_complete → push → PR → review →
    approval → QA validate → security review → done → parent eval.

### Agent Diagrams
11. **Synergy matrix:** visual representation of document 15's
    contribution matrix — who contributes what to whom at which stage.
12. **Communication diagram:** which agent talks to which via which
    bus (task comments, board memory, IRC, fleet_chat).

### Operational Diagrams
13. **Orchestrator cycle:** the 12 steps with data flow between them.
14. **Dispatch decision tree:** the 10 gates as a flowchart.
15. **Immune system flow:** observation → detection → decision →
    response (teach/compact/prune) → outcome.

These diagrams serve as validation tools AND as documentation for
the fleet's operational design. They should be produced during
implementation and maintained as the system evolves.

---

## Open Questions

- Should these flows be implemented as integration tests?
  (Simulate full task lifecycle in test environment)
- How do we validate timing? (30s cycles mean contribution tasks
  might take 2-3 cycles to be created and completed — is that OK?)
- Should there be a "dry run" mode that traces a task through the
  system without executing?
- What diagram format? (Mermaid for version control, ASCII for
  agent context, rendered images for Plane pages?)
- Should diagrams be auto-generated from system state? (Live
  architecture diagram that reflects actual configuration?)