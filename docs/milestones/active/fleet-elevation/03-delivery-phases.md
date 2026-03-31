# Delivery Phases — Maturity Progression System

**Date:** 2026-03-30
**Status:** Design — comprehensive phase system
**Part of:** Fleet Elevation (document 3 of 22)

---

## PO Requirements (Verbatim)

> "phases are important too. not to confuse with state and stage that
> relate to the preparing and processing than the delivery and the
> phases of this delivery."

> "advancing as the stages advance and a deliverable can pass from ideal,
> to conceptual, to POC, to MVP, to Staging, to Production ready.... or
> alpha, beta, rc & etc....."

> "this like the stages are not set in stone and are meant to allow
> mature delivery with docs defs and code docs and tests and security and
> logical work and not disconnected unless already planned otherwise need
> to plan this to continue"

> "We do not go small we go big..."

> "Things can evolve. The requirements, the things to test, the phases
> of the task, the various data blob for whatever different type we need
> + the main one and so on."

---

## What This Document Covers

The delivery phase system — a SECOND axis of tracking alongside
methodology stages. Stages track HOW you work (conversation, analysis,
investigation, reasoning, work). Phases track HOW MATURE the deliverable
is (ideal, conceptual, POC, MVP, staging, production).

These are two independent dimensions. A deliverable can be in "work"
stage while in "POC" phase. A different deliverable can be in "analysis"
stage while in "MVP" phase (analyzing what's needed to advance from POC
to MVP).

---

## Two Axes — The Complete Picture

```
              STAGES (how you work on the task)
              conversation → analysis → investigation → reasoning → work
PHASES        ┌──────────────────────────────────────────────────────────┐
(how mature   │                                                          │
the delivery) │                                                          │
              │                                                          │
ideal         │  The idea exists. No concrete requirements.              │
              │  → conversation with PO to explore what this could be    │
              │                                                          │
conceptual    │  Direction confirmed. High-level requirements exist.     │
              │  → analysis of problem space, investigation of options   │
              │                                                          │
POC           │  Prove the concept works. Minimum viable proof.          │
              │  → reasoning about minimal approach → work to build it   │
              │                                                          │
MVP           │  Core functionality for real use. Not complete, but      │
              │  usable. Tests cover main flows. Docs explain setup.     │
              │  → new analysis cycle: what gaps exist? → work to fill   │
              │                                                          │
staging       │  Full-featured. Security hardened. Integration tested.   │
              │  Deployment pipeline validated. Monitoring in place.     │
              │  → investigation of edge cases → work to harden          │
              │                                                          │
production    │  Production-ready. Fully tested, documented, secured,    │
              │  monitored. Can run with confidence. PO certifies.       │
              │  → final work cycle: docs, monitoring, load tests        │
              └──────────────────────────────────────────────────────────┘
```

A deliverable goes through MULTIPLE rounds of stages as it advances
through phases. The POC phase might require one cycle of reasoning →
work. The MVP phase might require new analysis → investigation →
reasoning → work. Each phase advancement triggers a new round of
methodology stages.

---

## Phase Progressions — Not Set in Stone

The PO specified two progressions and said "etc" — meaning more are
possible:

### Standard Progression
```
ideal → conceptual → poc → mvp → staging → production
```
Used for: features, systems, modules — anything that matures from
an idea to a running system.

### Release Progression
```
alpha → beta → rc → release
```
Used for: versioned releases, products, packages — anything that
goes through a release cycle.

### Custom Progressions
The PO said "not set in stone." Different deliverables may use
different progressions. A research spike might use:
```
ideal → conceptual → findings
```
A documentation effort might use:
```
draft → review → published
```

The phase system must support arbitrary progressions defined per
deliverable, not a single hard-coded sequence. Configuration over
code.

---

## Phase vs Stage — The Distinction

| Dimension | Stages | Phases |
|-----------|--------|--------|
| What it tracks | HOW you're working on a task | HOW MATURE the deliverable is |
| Values | conversation, analysis, investigation, reasoning, work | ideal, conceptual, poc, mvp, staging, production |
| Scope | Per-task | Per-deliverable (may span multiple tasks) |
| Cycles | One progression per task dispatch | Multiple rounds — each phase may trigger new stage cycles |
| Who advances | PM with PO confirmation (stages), PO at 90% gate | PO ONLY (phase advancement is always a gate) |
| Custom field | task_stage (on task) | delivery_phase (on task AND on Plane module) |
| Affects | What protocol the agent follows | What STANDARDS apply to the work |

Key insight: a task can be in "work" stage AND "poc" phase. The work
protocol tells the agent HOW to work (commit, test, PR). The POC phase
tells the agent WHAT STANDARDS apply (minimal tests, basic docs, no
hardcoded secrets).

A task can also be in "analysis" stage AND "mvp" phase. This happens
when the team is analyzing what gaps exist between the current POC and
the MVP target. The analysis protocol governs the work (examine what
exists, produce analysis document). The MVP phase tells them what
standards the analysis should evaluate against.

---

## Phase-Aware Standards — PO-DEFINED

The PO defines what each phase means. The PO defines what standards
apply at each phase. The PO can invent unlimited phases, use any
sequence, and define any criteria. The SYSTEM supports arbitrary
phases — it does NOT prescribe what a phase is or what it contains.

### How Phases Are Defined

Phases live in configuration. The PO defines each phase with:
- A name (any name — "poc", "alpha", "experimental", "v2-candidate")
- A description (what this phase means for this project/deliverable)
- Standards (what quality bars apply — tests, docs, security, etc.)
- Required contributions (which roles must contribute at this phase)
- Gate type (PO approval, PM approval, automatic)

```yaml
# config/phases.yaml — PO-defined, project-specific

progressions:
  # Example progression — PO defines this
  standard:
    - name: ideal
      description: "The idea exists"
      # PO defines standards for this phase:
      standards: {}
      required_contributions: []
      gate: false

    - name: conceptual
      description: "Direction confirmed by PO"
      standards:
        design: required
        requirements: captured
      required_contributions: [architect]
      gate: true  # PO must approve advancement

    - name: poc
      # PO defines what POC means for THEIR projects:
      description: "Proves the concept works"
      standards:
        # PO defines quality bars:
        tests: "happy path"
        docs: "readme"
        security: "no secrets in code"
      required_contributions: [architect]
      gate: true

    - name: mvp
      description: "Core functionality usable for real"
      standards:
        tests: "main flows and critical edges"
        docs: "setup, usage, API for public"
        security: "auth, validation, dep audit"
      required_contributions: [architect, qa-engineer, devsecops-expert]
      gate: true

    # PO can add ANY phase here:
    # - name: "beta"
    # - name: "load-tested"
    # - name: "compliance-certified"
    # etc.

  # Alternate progression — also PO-defined
  release:
    - name: alpha
      description: "Feature-complete, internal testing"
      standards: {tests: "integration", docs: "draft"}
      gate: true
    - name: beta
      # ...
    - name: rc
      # ...
    - name: release
      # ...

  # PO can create entirely custom progressions:
  research:
    - name: hypothesis
    - name: experiment
    - name: findings
    - name: published
```

### Key Design Principle

The system NEVER assumes what a phase name means. The system reads
the phase definition from config and applies whatever standards the
PO defined. If the PO creates a phase called "dinosaur" with standards
requiring 100% test coverage, the system enforces 100% test coverage
for tasks in "dinosaur" phase. The system is a MECHANISM, not a
prescriber.

The PO can:
- Create unlimited phases
- Define any progression sequence
- Define any standards per phase
- Change standards at any time
- Add phases to an existing progression
- Remove phases
- Create project-specific progressions
- Override progression per deliverable

### PO Suggestions (Examples Only)

The PO mentioned these progressions as examples:
> "ideal, to conceptual, to POC, to MVP, to Staging, to Production
> ready.... or alpha, beta, rc & etc....."

These are the PO's initial suggestions. They may change. They may
expand. They may be completely different per project. The system
supports whatever the PO decides.

---

## Phase as Custom Field

### On OCMC Board
```
delivery_phase:
  type: text
  # Values are NOT hard-coded — derived from phase config
  values: [loaded from config/phases.yaml at board setup]
  default: ""  # no phase = no standards enforced
  on: task custom fields
```

### On Plane (labels — CE has no custom fields)
Labels created dynamically from phase config:
`phase:{name}` for each phase in each progression.

The label set is NOT fixed — it grows as the PO defines new phases.
The board setup script reads config/phases.yaml and creates labels.

Sync: bidirectional via `plane_sync.py`, same mechanism as stage/
readiness labels.

### On Plane Modules
Modules can also have a phase — representing the overall maturity of
a body of work. The immune system module might be in `phase:mvp` while
individual tasks within it are at various stages.

Module phase is set by PM/PO and represents a strategic decision about
where this body of work is in its maturity journey.

---

## Phase Advancement — Always a PO Gate

Phase advancement is ALWAYS a gate. The brain cannot automatically
advance a deliverable's phase. The PO decides when a deliverable is
mature enough for the next phase.

### Advancement Flow

1. **PM evaluates readiness for phase advancement:**
   - Are all phase standards met for the current phase?
   - Is the work at the right quality level?
   - Are tests, docs, security appropriate for the next phase?

2. **PM requests phase advancement:**
   ```
   fleet_gate_request(task_id, "phase_advance",
     "Requesting advance from POC to MVP. Evidence:
      - Tests added (12 test cases, 3 integration)
      - Docs updated (setup guide, API reference)
      - Security review complete (no findings)
      - All acceptance criteria met")
   ```

3. **Brain fires gate chain:**
   - Checks: current phase standards met? (deterministic check against
     standards library with phase context)
   - If standards not met: blocks advancement, notifies PM of gaps
   - If standards met: routes to PO for approval
   - ntfy notification to PO: "Phase advancement requested: POC → MVP"
   - Board memory: tagged [gate, phase-advance, po-required]
   - IRC #gates: "Phase advance requested: {task} POC → MVP"

4. **PO decides:**
   - Approve: phase label updated, new standards apply, event emitted
   - Reject: feedback posted, stays at current phase
   - Regress: PO can also REGRESS to a previous phase if quality drops

5. **Post-advancement:**
   - New phase standards apply to all work on this deliverable
   - Brain updates pre-embed for all agents working on related tasks
   - Context includes: "DELIVERY PHASE: MVP. MVP standards apply."
   - If the deliverable needs more work for the new phase, the brain
     may trigger new analysis/investigation cycles

### Phase Regression

The PO can regress a phase. If a deliverable was advanced to MVP but
the PO discovers the POC standards aren't actually met:

- Phase regresses: mvp → poc
- All related tasks get updated
- Comment: "Phase regressed by PO. Reason: {reason}"
- Event: fleet.phase.regressed
- PM notified to plan remediation
- Standards revert to the lower phase

---

## Multiple Rounds of Stages Per Phase

This is the key insight: a deliverable going from POC to MVP doesn't
just have one cycle of work. It has a FULL round of methodology stages:

**POC → MVP advancement cycle:**

1. Analysis stage: examine the current POC implementation. What exists?
   What gaps exist relative to MVP standards? What's missing: tests,
   docs, security, error handling?

2. Investigation stage: research what's needed. Are there better
   approaches now that the POC proved the concept? Should the
   architecture change for MVP? What tools/libraries are needed?

3. Reasoning stage: plan the MVP work. Reference the MVP standards.
   Map each gap to specific implementation steps. Get PO confirmation.

4. Work stage: implement the plan. Write the tests. Update the docs.
   Add the security measures. Follow MVP standards.

5. Review: fleet-ops reviews against MVP standards (not POC standards).
   QA validates against predefined tests. DevSecOps reviews security.

6. PM requests phase advancement to MVP. PO approves.

Each phase transition potentially triggers a full round of stages.
The tasks for this round are created by the PM or brain, linked to
the deliverable via parent_task or plan_id.

---

## Phase Interaction with the Brain

The brain's chain registry needs phase-aware logic:

### Dispatch
When dispatching a task, the brain includes the delivery phase in the
context. The agent's autocomplete chain includes: "DELIVERY PHASE: POC.
POC standards apply: {specific standards}."

### Standards Check
When fleet_task_complete is called, the brain checks completion against
phase-appropriate standards. A task in POC phase is checked against POC
standards. Same task type in production phase is checked against
production standards.

### Contribution Requirements
Phase affects what contributions are required:
- POC: architect design input may be sufficient
- MVP: architect + QA test predefinition required
- staging: architect + QA + DevSecOps security review required
- production: all contributions required + accountability compliance check

### Phase-Aware Effort Profiles
POC work should use lighter effort profiles (less expensive, faster).
Production work uses full effort profiles (thorough, more expensive).
The brain routes accordingly.

---

## Phase Interaction with the Immune System

New detection patterns for phase violations:

### Phase-standards mismatch
Agent claims work complete but phase standards aren't met. Example:
task is in MVP phase but has no tests. Doctor detects:
"Task in MVP phase completed without test coverage. MVP standards
require: main flows + critical edge cases."

### Phase skipping
Deliverable jumps from conceptual to production without intermediate
phases. Doctor detects: "Readiness went from 20% to 99% with phase
still at 'conceptual'. No POC or MVP phase was traversed."

### Over-engineering for phase
Agent applies production-level effort to a POC. While not harmful,
it wastes budget. Doctor may flag: "Production-level test suite
written for POC phase task. POC standards: happy path only."

### Under-delivering for phase
Agent produces POC-quality work for a production task. Doctor detects:
"Production phase task completed with minimal tests. Production
standards require: complete coverage."

---

## Phase Interaction with the Teaching System

New lesson templates:

### Phase standards ignorance
```
Your task is in {phase} phase.
{phase} standards require: {standard_list}
Your work provided: {what_agent_delivered}
Missing for {phase}: {what_is_missing}

The delivery phase determines what "done" looks like. POC quality
is different from production quality. Check the phase before
completing work.

Exercise: List the standards for {phase} phase. For each standard,
state whether your work meets it. Identify the gaps.
```

### Phase over-engineering
```
Your task is in {phase} phase.
{phase} standards require: {standard_list}
You delivered: {what_agent_delivered}

Your work exceeds what {phase} requires. While quality is valued,
over-engineering at early phases wastes budget and delays delivery.
Save the extra effort for later phases when it's needed.

Exercise: Identify which parts of your work exceed {phase} standards.
State what the appropriate level of effort would be.
```

---

## Phase Interaction with Plane

### Labels
Phase labels are synced bidirectionally:
- OCMC → Plane: when delivery_phase custom field changes, label updated
- Plane → OCMC: when PO changes label in Plane, sync picks it up

### Module Phases
Plane modules can have phase labels representing the overall maturity
of a body of work. The sync layer handles module-level phase labels
separately from task-level phase labels.

### Phase in Description
When a task's phase changes, the Plane issue description can include
a phase indicator: "**Delivery Phase: MVP** — MVP standards apply."
This is visible to anyone looking at the Plane issue.

### Filtering
In Plane, teams can filter by phase label to see all POC tasks, all
MVP tasks, etc. This gives the PO a view of where each deliverable
stands in its maturity journey.

---

## Phase Interaction with Context Assembly

### Task Context Bundle
The `assemble_task_context()` function needs to include:
```python
result["phase"] = {
    "current_phase": cf.delivery_phase or "ideal",
    "phase_standards": get_phase_standards(cf.delivery_phase),
    "phase_progression": get_phase_progression(cf.delivery_phase),
    "next_phase": get_next_phase(cf.delivery_phase),
    "advancement_requirements": get_advancement_requirements(cf.delivery_phase),
}
```

### Pre-Embed
The pre-embed includes phase context in the autocomplete chain:
```
## DELIVERY PHASE: MVP
MVP standards apply to your work:
- Tests: main flows + critical edge cases
- Docs: setup guide, usage instructions
- Security: auth, validation, dependency audit
- Standard: "can someone use this for real?"

Your work will be reviewed against MVP standards.
```

This goes in the autocomplete chain BEFORE the "what to do now" section,
so the agent knows what standards apply before they start working.

### Heartbeat Context
Heartbeat pre-embed includes phase information for the agent's
assigned tasks, so they know which phase each task is in and what
standards apply.

---

## Phase Interaction with Standards Library

The standards library (`standards.py`) needs phase-aware checking:

```python
def check_standard(
    artifact_type: str,
    present_fields: dict[str, bool],
    phase: str = "production",  # default to strictest
) -> ComplianceResult:
    """Check an artifact against its standard for a specific phase."""
    standard = get_standard(artifact_type)
    if not standard:
        return ComplianceResult(artifact_type=artifact_type)

    result = ComplianceResult(artifact_type=artifact_type)
    phase_config = get_phase_standards(phase)

    for rf in standard.required_fields:
        # Phase determines which fields are actually required
        is_required_for_phase = phase_required(rf.name, phase_config)
        if is_required_for_phase and not present_fields.get(rf.name, False):
            result.missing_fields.append(rf.name)

    return result
```

Example: the "pull_request" standard requires "testing" field. At POC
phase, this is recommended but not blocking. At MVP phase, it's
required. At production phase, it's required AND must include specific
test result evidence.

---

## Configuration

Phases are config-driven, not hard-coded:

```yaml
# config/fleet.yaml — phases section

phases:
  # Standard maturity progression
  standard:
    - name: ideal
      description: "The idea exists"
      standards: none
      gate: false  # no PO gate to enter ideal
    - name: conceptual
      description: "Direction confirmed, high-level requirements"
      standards: conceptual
      gate: true  # PO must approve to enter
    - name: poc
      description: "Prove the concept works"
      standards: poc
      gate: true
    - name: mvp
      description: "Core functionality for real use"
      standards: mvp
      gate: true
    - name: staging
      description: "Full-featured, hardened, tested"
      standards: staging
      gate: true
    - name: production
      description: "Production-ready, fully certified"
      standards: production
      gate: true

  # Release progression
  release:
    - name: alpha
      description: "Feature-complete, internal testing"
      standards: alpha
      gate: true
    - name: beta
      description: "Stable for external testing"
      standards: beta
      gate: true
    - name: rc
      description: "Release candidate, final validation"
      standards: rc
      gate: true
    - name: release
      description: "Shipped"
      standards: release
      gate: true

  # Phase standards definitions
  phase_standards:
    poc:
      tests: minimal
      docs: readme
      security: basic
      required_contributions: [architect]
    mvp:
      tests: core_flows
      docs: setup_and_usage
      security: auth_and_validation
      required_contributions: [architect, qa-engineer]
    staging:
      tests: comprehensive
      docs: full
      security: hardened
      required_contributions: [architect, qa-engineer, devsecops-expert]
    production:
      tests: complete
      docs: comprehensive
      security: certified
      required_contributions: [architect, qa-engineer, devsecops-expert,
                                accountability-generator]
```

Adding a new phase, changing standards, or adjusting contribution
requirements is a config change — no code modification needed.

---

## Data Model Changes

### TaskCustomFields (models.py)
```python
delivery_phase: Optional[str] = None  # ideal/conceptual/poc/mvp/staging/production
phase_progression: Optional[str] = None  # "standard" or "release" or custom
```

### New Module: fleet/core/phases.py
```python
class Phase:
    """A delivery phase with standards and gate requirements."""
    name: str
    description: str
    standards: dict  # phase-specific standard requirements
    gate: bool  # requires PO approval to enter
    required_contributions: list[str]  # roles that must contribute

class PhaseProgression:
    """An ordered sequence of phases a deliverable goes through."""
    name: str
    phases: list[Phase]

def get_current_phase(task) -> Phase
def get_next_phase(current_phase, progression) -> Optional[Phase]
def check_phase_standards(task, phase) -> ComplianceResult
def can_advance_phase(task, phase) -> tuple[bool, list[str]]  # (can_advance, missing)
```

### configure-board.sh
```bash
# New custom field
mc_create_custom_field "$BOARD_ID" "delivery_phase" "text"
```

### Plane Labels
```bash
# New labels for phase sync
plane_create_label "phase:ideal"
plane_create_label "phase:conceptual"
plane_create_label "phase:poc"
plane_create_label "phase:mvp"
plane_create_label "phase:staging"
plane_create_label "phase:production"
plane_create_label "phase:alpha"
plane_create_label "phase:beta"
plane_create_label "phase:rc"
plane_create_label "phase:release"
```

---

## MCP Tool Changes

### fleet_task_create
Add `delivery_phase` parameter. When PM creates subtasks for a phase
advancement cycle, they set the phase so standards are applied from
the start.

### fleet_task_complete
When called, check completion against phase-appropriate standards
(not just the generic standard). If phase standards aren't met,
warn but don't block — fleet-ops will review.

### fleet_phase_advance (NEW)
Request phase advancement for a deliverable:
```
fleet_phase_advance(task_id, from_phase, to_phase, evidence)
→ Chain: check standards → route to PO → approve/reject
→ Update phase field → sync to Plane → emit event → update standards
```

### fleet_read_context
Returns phase information in the context bundle so agents know what
standards apply.

---

## Event Types

```python
# New event types for phases
"fleet.phase.advance_requested"   # PM/agent requests phase advancement
"fleet.phase.advanced"            # PO approved, phase changed
"fleet.phase.advance_rejected"    # PO rejected advancement
"fleet.phase.regressed"           # PO regressed to earlier phase
"fleet.phase.standards_checked"   # Standards evaluated for phase compliance
```

---

## How a Task Knows Its Phase

Phase can be set at multiple levels:

1. **Task-level:** `delivery_phase` custom field on the task itself.
   Most specific. Overrides all others.

2. **Parent-level:** If a task's parent (epic) has a phase, child tasks
   inherit it unless overridden. An MVP epic's subtasks are MVP by
   default.

3. **Module-level:** Plane module has a phase label. Tasks in that
   module inherit the module's phase unless overridden.

4. **Default:** If no phase is set anywhere, default to "ideal" (no
   standards applied — safest default).

Resolution order: task → parent → module → default.

This means PM can set the phase on an epic and all subtasks
automatically apply those standards. Individual subtasks can be
overridden if needed (e.g., a security subtask might be at "staging"
standards even if the epic is at "poc").

---

## Example Flow: Feature From Ideal to Production

**Sprint 1 — Ideal → Conceptual:**
- PO creates epic: "Add search to NNRT"
- Phase: ideal (just an idea)
- PM assigns to architect for design exploration
- Architect: conversation with PO → analysis → investigation
- Phase advances to conceptual (PO approves direction)

**Sprint 2 — Conceptual → POC:**
- Architect produces design plan (reasoning stage)
- PM breaks into subtasks: backend search, frontend UI, indexing
- PM assigns subtasks to engineers
- Engineers implement POC (happy path, basic tests)
- Phase advances to POC (PO verifies concept works)

**Sprint 3 — POC → MVP:**
- PM triggers new analysis cycle: what gaps exist?
- QA predefines tests for MVP (main flows + edge cases)
- Engineers implement: proper error handling, full test suite
- Technical writer adds docs: setup, usage, API reference
- DevSecOps reviews: auth on search endpoint, input sanitization
- Phase advances to MVP (PO verifies it's usable for real)

**Sprint 4 — MVP → Staging:**
- New analysis: what's needed for staging?
- Engineers: load testing, performance optimization
- DevSecOps: pen testing, dependency audit
- DevOps: deployment pipeline, monitoring, alerting
- Technical writer: deployment guide, troubleshooting, runbook
- Phase advances to staging (PO verifies it's deployment-ready)

**Sprint 5 — Staging → Production:**
- Final validation: integration testing, chaos testing
- Accountability generator: compliance audit, trail verification
- Technical writer: architecture docs, decision records
- PO final review: all standards met, all trails complete
- Phase advances to production (PO certifies)

5 sprints. Multiple rounds of methodology stages. Progressive quality.
Each phase builds on the previous. Standards get stricter. Contributions
increase. The deliverable MATURES.

---

## Open Questions

- Should phase advancement create a new "phase advancement" task type
  that PM uses to plan the phase transition work?
- How does the sprint model handle multi-sprint phase progressions?
  Does each phase get its own sprint, or can multiple phase activities
  coexist in one sprint?
- Should the brain automatically create analysis tasks when a phase
  advancement is approved? ("Now that we're in MVP, analyze what's
  needed to reach MVP standards.")
- How do phases interact with the alternate release progression?
  Can a deliverable use BOTH progressions simultaneously? (MVP release
  as alpha, production release as 1.0?)
- Should there be a "phase readiness" concept separate from task
  readiness? Phase readiness = how close the deliverable is to
  advancing to the next phase.
- How does multi-fleet handle phases? If Fleet Alpha built the POC
  and Fleet Bravo is doing the MVP, how is the phase tracked across
  fleets on the shared Plane?

---

## Files to Create/Modify

| File | Change |
|------|--------|
| `fleet/core/phases.py` | NEW — Phase, PhaseProgression, phase checks |
| `fleet/core/models.py` | Add delivery_phase, phase_progression to TaskCustomFields |
| `fleet/core/standards.py` | Phase-aware check_standard() |
| `fleet/core/context_assembly.py` | Include phase data in task context |
| `fleet/core/preembed.py` | Include phase standards in autocomplete chain |
| `fleet/core/events.py` | Add phase event types |
| `fleet/core/event_display.py` | Renderers for phase events |
| `fleet/mcp/tools.py` | fleet_phase_advance tool, phase param on create/complete |
| `fleet/infra/mc_client.py` | Parse delivery_phase from task custom fields |
| `fleet/core/plane_sync.py` | Sync phase labels bidirectionally |
| `config/fleet.yaml` | Phase definitions and standards |
| `scripts/configure-board.sh` | delivery_phase custom field |
| `fleet/core/doctor.py` | Phase violation detection patterns |
| `fleet/core/teaching.py` | Phase-related lesson templates |
| `fleet/tests/core/test_phases.py` | NEW — phase system tests |

---

## Testing Requirements

- Phase progression: ideal → conceptual → poc → mvp → staging → production
- Phase standards: POC has lighter standards than production
- Phase gate: advancement requires PO approval (deterministic check)
- Phase inheritance: child tasks inherit parent phase
- Phase-aware completeness: check_standard with phase context
- Phase regression: PO can regress phase
- Phase events: all 5 event types emit correctly
- Phase labels: Plane sync for phase labels
- Phase config: config-driven, not hard-coded
- Phase + stages interaction: different stages work correctly at
  different phases
- Phase contribution requirements: POC needs architect, production
  needs all