# Cross-Agent Synergy Map

**Date:** 2026-03-30
**Status:** Design — who contributes what to whom and when
**Part of:** Fleet Elevation (document 15 of 22)

---

## PO Requirements (Verbatim)

> "everyone is the fleet is a generalist expert to some degree but
> everyone has their speciality and we need to create synergy and allow
> everyone to bring their piece. their segments and artifacts."

---

## What This Document Covers

The complete map of cross-agent contributions: who contributes what
to whom, at which stage, for which task types, at which delivery phases.
This is the matrix that drives the brain's contribution opportunity
creation.

---

## The Contribution Matrix

### When Task Enters REASONING Stage

| Task Type | Architect | QA | UX | DevSecOps | Tech Writer |
|-----------|-----------|-----|-----|-----------|-------------|
| epic | design_input (required) | qa_test_def (required) | ux_spec (if UI) | security_req (required) | doc_outline (recommended) |
| story | design_input (required) | qa_test_def (required) | ux_spec (if UI) | security_req (if security) | doc_outline (recommended) |
| task | design_input (if complex) | qa_test_def (recommended) | — | security_req (if security) | — |
| subtask | — | — | — | — | — |
| bug | — | qa_test_def (regression test) | — | security_req (if security bug) | — |
| spike | — | — | — | — | — |

### When Task Enters REVIEW Stage

| Reviewer | What They Check | Artifact Type |
|----------|----------------|---------------|
| Fleet-Ops | Verbatim match, trail, acceptance criteria, phase standards | approval_decision |
| QA | Predefined test criteria validated against implementation | qa_validation |
| DevSecOps | Security review of PR diff and changes | security_review |
| Architect | Design alignment, pattern compliance | architecture_review (optional) |
| UX | UX spec compliance, interaction correctness | ux_review (if UI) |

### When Task COMPLETES (After Approval)

| Agent | What They Do | Trigger |
|-------|-------------|---------|
| Technical Writer | Update Plane pages for documented feature | brain chain |
| Accountability | Verify trail completeness | brain chain |
| PM | Update sprint progress, plan next work | heartbeat |

---

## Phase-Dependent Contribution Requirements

The delivery phase determines how many contributions are required:

| Phase | Required Contributions |
|-------|----------------------|
| ideal | None |
| conceptual | Architect (design direction) |
| poc | Architect (design input) |
| mvp | Architect + QA + DevSecOps (if applicable) |
| staging | Architect + QA + DevSecOps + Tech Writer |
| production | ALL applicable contributions required |

This means a POC task can proceed with just architect input, but a
production task needs the full synergy chain.

---

## Contribution Flow Diagram

```
Task created (inbox)
│
├─ PM assigns and sets fields
│
├─ Task enters REASONING stage
│   │
│   ├─ Brain creates contribution tasks:
│   │   ├─ Architect: design_input (if epic/story)
│   │   ├─ QA: qa_test_definition (if epic/story/task)
│   │   ├─ UX: ux_spec (if tagged "ui")
│   │   ├─ DevSecOps: security_requirement (if epic or tagged "security")
│   │   └─ Tech Writer: documentation_outline (if staging/production phase)
│   │
│   ├─ Contributors produce artifacts in parallel
│   │
│   └─ Brain checks: all required contributions received?
│       ├─ YES → PM can advance to work (after PO gate at 90%)
│       └─ NO → PM notified of gaps, dispatch blocked
│
├─ Task in WORK stage
│   │
│   └─ Agent implements with ALL contributions in context:
│       - Architect's design approach
│       - QA's test criteria to satisfy
│       - UX's component patterns to follow
│       - DevSecOps' security requirements to respect
│
├─ Task enters REVIEW
│   │
│   ├─ Fleet-Ops: primary review (trail + verbatim + criteria)
│   ├─ QA: validate predefined tests
│   ├─ DevSecOps: security review (if applicable)
│   ├─ Architect: alignment review (optional)
│   └─ UX: spec compliance (if UI)
│   │
│   └─ Fleet-Ops aggregates: "QA: ✓, Security: ✓, Architecture: ✓"
│
├─ Task APPROVED
│   │
│   ├─ Tech Writer: update documentation
│   ├─ Accountability: verify trail
│   └─ PM: update sprint progress
│
└─ DONE
```

---

## Parallel vs Serial Contributions

Contributions happen in PARALLEL, not serial:
- Architect, QA, UX, DevSecOps all receive their contribution tasks
  at the same time (when the main task enters reasoning)
- Each works independently and posts their contribution
- The brain tracks which have been received
- When all required contributions are in → the task can advance

This is NOT a waterfall where architect goes first, then QA, then
DevSecOps. It's parallel contribution with the brain aggregating.

However, some contributions BENEFIT from others:
- QA can write better test criteria if they see architect's design
- DevSecOps can write better security reqs if they see the plan

The brain creates all contribution tasks simultaneously, but
contributors can see each other's contributions as they come in
(contributions propagate to the parent task's context).

---

## The Contribution Task Type

Contribution tasks are a special category:
- `task_type: subtask`
- `contribution_type: qa_test_definition` (NEW custom field)
- `contribution_target: {parent_task_id}` (NEW custom field)
- `auto_created: true`
- `auto_reason: "Brain: {type} contribution for {task_id}"`
- They inherit parent's `delivery_phase`
- They start at `task_stage: reasoning, task_readiness: 50`
  (clear what to do, just needs to do it)
- They are SMALL — one heartbeat cycle, one artifact

---

## Synergy Patterns

### Pattern 1: Design-First
Architect contributes design → Engineer implements → QA validates
Best for: epics, stories with architectural implications.

### Pattern 2: Test-First
QA predefines tests → Engineer implements to satisfy → QA validates
Best for: bug fixes, feature tasks with clear acceptance criteria.

### Pattern 3: Security-Aware
DevSecOps provides requirements → Engineer follows → DevSecOps reviews
Best for: tasks touching auth, data handling, external APIs.

### Pattern 4: UX-Guided
UX provides spec → Engineer implements → UX reviews
Best for: frontend tasks, UI components, user-facing features.

### Pattern 5: Full Synergy
All contributors provide input → Engineer implements with all context
→ All contributors validate
Best for: production-phase epics where quality must be maximum.

---

## Anti-Patterns to Detect

### Siloed Work
Agent implements without consulting contributions. The brain created
the contribution tasks, but the implementing agent ignored them.
Detection: work stage started before contributions received.

### Sequential Bottleneck
One contributor blocks all others. Architect takes 3 cycles to
contribute design, QA and others wait. Brain detects: contribution
task stale > 2 cycles while main task is waiting.

### Contribution Inflation
Contributor produces excessive, irrelevant input. QA predefines
30 tests for a simple task. Phase awareness helps — POC doesn't
need 30 tests.

### Ghost Contributions
Contribution posted but never consumed. Engineer's work doesn't
reference it. Trail gap detection during review.

---

## Config-Driven Synergy Rules

```yaml
# config/fleet.yaml — contributions section

contributions:
  reasoning:  # when task enters reasoning stage
    - role: architect
      contribution_type: design_input
      required_for: [epic, story]
      optional_for: [task]
      condition: "complexity == 'high'"
    - role: qa-engineer
      contribution_type: qa_test_definition
      required_for: [epic, story, task]
      optional_for: [bug]
    - role: ux-designer
      contribution_type: ux_spec
      required_for: [story]
      condition: "tags contains 'ui'"
    - role: devsecops-expert
      contribution_type: security_requirement
      required_for: [epic]
      condition: "tags contains 'security' OR task_type == 'epic'"
    - role: technical-writer
      contribution_type: documentation_outline
      optional_for: [epic, story]
      condition: "phase in ['staging', 'production']"

  review:  # when task enters review stage
    - role: qa-engineer
      contribution_type: qa_validation
      required_for: [epic, story, task]
      condition: "qa_test_definition exists for this task"
    - role: devsecops-expert
      contribution_type: security_review
      required_for: [epic, story]
      condition: "pr_url is set"
    - role: ux-designer
      contribution_type: ux_review
      optional_for: [story]
      condition: "tags contains 'ui'"

  completion:  # when task is approved and done
    - role: technical-writer
      contribution_type: documentation_update
      required_for: [epic, story]
      condition: "phase in ['mvp', 'staging', 'production']"
    - role: accountability-generator
      contribution_type: trail_verification
      required_for: [epic, story, task]
```

---

## Per-Agent Operational Surface

For each agent: what they CREATE, what they CONSUME, what IMPRINTS
they leave, what TOOL CALL TREES they trigger, and what PROACTIVE
behaviors they have.

### Project Manager

**Creates:**
- Subtasks (fleet_task_create → tree: mc.create_task, mc.post_comment
  on parent, plane_sync.create_issue, events.emit, irc.send)
- Contribution tasks (fleet_task_create with contribution_type)
- Sprint plans (fleet_artifact_create → tree: object, transpose,
  Plane HTML, completeness, event)
- Gate requests (fleet_gate_request → tree: mc.post_memory, irc.send
  #gates, ntfy to PO, events.emit)

**Consumes:**
- Unassigned task list (heartbeat pre-embed)
- Sprint progress data (role provider)
- Contribution status (which tasks have/lack contributions)
- PO directives and gate decisions
- Agent messages and escalations

**Imprints (trail events):**
- Task assignment comment
- Stage advancement decision
- Epic breakdown summary
- Gate request submission
- Sprint standup summary

**Proactive behaviors:**
- Assigns unassigned tasks every heartbeat
- Creates contribution tasks when tasks enter reasoning
- Routes gate requests to PO at checkpoints
- Resolves blockers (max 2 active)
- Sprint standup with meaningful updates

### Fleet-Ops (Board Lead)

**Creates:**
- Approval decisions (fleet_approve → tree: mc.update_approval,
  mc.update_task status, mc.post_comment with decision, plane_sync,
  events.emit, irc.send #reviews, mc.post_memory trail)
- Quality alerts (fleet_alert → tree: irc.send #alerts, mc.post_memory,
  ntfy if critical)

**Consumes:**
- Pending approval list (role provider)
- Task trails (stage transitions, contributions, PO gates)
- Completion summaries and PRs
- Immune system health alerts
- Budget data

**Imprints:**
- Approval/rejection decision with reasoning
- Quality observations posted to board memory
- Process improvement suggestions
- Budget alert records

**Proactive behaviors:**
- Processes every pending approval every heartbeat
- Spot-checks recently completed tasks for quality
- Monitors board health (stuck tasks, offline agents)
- Reports methodology compliance violations

### Architect

**Creates:**
- Analysis documents (fleet_artifact_create → full tree)
- Investigation documents with multiple options
- Implementation plans referencing verbatim
- Design contributions (fleet_contribute → tree: mc.post_comment on
  target, plane_sync, context.update, mc.update_task contribution task,
  events.emit, mc.post_memory trail, notify_owner, check_completeness)
- Architecture decision records (mc.post_memory with tags)

**Consumes:**
- Design task assignments
- Contribution requests from brain
- Existing codebase (via fleet_read_context)
- PO requirements and feedback
- Other agents' questions about design

**Imprints:**
- Design decisions with rationale
- Complexity assessments
- Pattern recommendations
- Architecture health observations

**Proactive behaviors:**
- Reviews board memory for architecture concerns
- Monitors implementation alignment with designs
- Flags coupling issues and pattern inconsistencies
- Proposes refactoring when technical debt accumulates

### QA Engineer

**Creates:**
- Test predefinitions (fleet_contribute "qa_test_definition" → full tree)
- Test validation results (typed comment on reviewed task → tree:
  mc.post_comment, plane_sync, events.emit, mc.post_memory trail)
- Test suites (fleet_commit during assigned test tasks)

**Consumes:**
- Contribution tasks for test predefinition
- Tasks in review needing validation
- Verbatim requirements and acceptance criteria
- Architect design input (informs test strategy)
- Implementation PRs for validation

**Imprints:**
- Predefined test criteria with IDs (TC-001, TC-002...)
- Validation results (✓/✗ per criterion with evidence)
- Acceptance criteria quality feedback to PM

**Proactive behaviors:**
- Reviews inbox tasks for testable acceptance criteria
- Flags vague criteria to PM ("it works" is not testable)
- Predefines tests at reasoning stage (contribution)
- Validates against predefined tests at review stage

### Software Engineer

**Creates:**
- Code commits (fleet_commit → tree: git.add, git.commit,
  mc.post_comment, plane_sync, events.emit, mc.post_memory trail)
- Completion claims (fleet_task_complete → full 12+ operation tree)
- Progress updates (fleet_artifact_update)
- Discovered subtasks (fleet_task_create when finding new work needed)

**Consumes:**
- Architect design input (approach, files, patterns, constraints)
- QA predefined tests (criteria to satisfy)
- UX component specs (patterns, states, accessibility)
- DevSecOps security requirements (what to do/not do)
- Verbatim requirement and confirmed plan

**Imprints:**
- Code commits with conventional format
- Progress comments across cycles
- Completion summary with evidence per acceptance criterion
- Subtask creation when discovering new work

**Proactive behaviors:**
- Checks for colleague contributions before starting work
- Requests missing contributions via fleet_request_input
- Reports blockers to PM
- Builds progressively across cycles (artifacts accumulate)

### DevOps

**Creates:**
- Infrastructure configs (fleet_commit → tree)
- Deployment manifests (fleet_contribute "deployment_manifest" → tree)
- CI/CD pipelines
- Infrastructure assessments (fleet_artifact_create)
- Runbooks (fleet_artifact_create)

**Consumes:**
- Infrastructure task assignments
- Deployment contribution requests
- Phase advancement needs (what infra is needed for next phase)
- Architect infrastructure architecture

**Imprints:**
- IaC changes committed
- Deployment manifest contributions
- Infrastructure health observations
- CI/CD pipeline documentation

**Proactive behaviors:**
- Monitors fleet infrastructure health every heartbeat
- Flags infrastructure issues (MC, gateway, LocalAI)
- Reviews CI/CD pipeline efficiency
- Ensures IaC principle is followed (no manual ops)

### DevSecOps (Cyberpunk-Zero)

**Creates:**
- Security requirements (fleet_contribute "security_requirement" → tree)
- Security reviews (typed comment on PR → tree)
- Security assessments (fleet_artifact_create for assigned audits)
- Security alerts (fleet_alert → tree)
- security_hold (custom field that blocks approval chain)

**Consumes:**
- Security contribution requests
- PRs needing security review
- Dependency manifests
- Infrastructure security state
- Vulnerability databases

**Imprints:**
- Security requirements on target tasks
- Security review results (✓/⚠️/✗)
- security_hold decisions
- Vulnerability alerts

**Proactive behaviors:**
- Reviews every PR with code changes for security
- Scans dependencies for CVEs
- Monitors infrastructure security
- Crisis response in crisis-management phase

### Technical Writer

**Creates:**
- Documentation outlines (fleet_contribute "documentation_outline" → tree)
- User guides, API docs, deployment guides (fleet_artifact_create)
- ADRs formalized from architect decisions (Plane pages)
- Plane page updates (documentation maintenance)

**Consumes:**
- Recently completed features (need documentation)
- Stale Plane pages (need updating)
- Architect design decisions (to formalize)
- Engineer PRs (source material for API docs)
- DevOps deployment changes (for runbooks)

**Imprints:**
- Documentation contributions
- Plane page create/update records
- ADR formalization
- Documentation coverage metrics

**Proactive behaviors:**
- Scans for stale Plane pages every heartbeat (full-autonomous)
- Creates documentation for undocumented features
- Maintains ADR index
- Updates docs alongside feature development

### UX Designer

**Creates:**
- UX specs (fleet_contribute "ux_spec" → tree)
- UX reviews (typed comment on UI tasks → tree)
- Component patterns (fleet_artifact_create for library)

**Consumes:**
- UI tasks needing UX input
- Architect component architecture
- Existing component pattern library
- Implementation PRs for UX validation

**Imprints:**
- Component specs with states, interactions, accessibility
- UX review results
- Pattern library entries
- UX quality observations

**Proactive behaviors:**
- Reviews tasks tagged "ui" for UX input needs
- Maintains component pattern library on Plane
- Validates UX compliance during review
- Applies UX thinking at every level (CLI, API, not just web)

### Accountability Generator

**Creates:**
- Compliance reports (fleet_artifact_create → tree)
- Audit trail reconstructions
- Process improvement recommendations (board memory)

**Consumes:**
- Trail events for completed tasks
- Contribution records
- Gate decision records
- Approval/rejection records
- Sprint completion data

**Imprints:**
- Compliance metrics (methodology %, contribution %, gate %)
- Pattern findings (recurring compliance gaps)
- Process recommendations
- Trail verification records

**Proactive behaviors:**
- Verifies trails for every completed task
- Generates compliance reports at sprint boundaries
- Feeds patterns to immune system via board memory
- Monitors phase advancement compliance

---

## Testing Requirements

- Contribution matrix: correct contributions created for each
  task_type × phase combination
- Parallel creation: all contributions created simultaneously
- Propagation: contributions visible in target task's context
- Blocking: dispatch blocked when required contributions missing
- Phase-awareness: fewer contributions required at POC, more at
  production
- Config-driven: changing config changes contribution behavior

---

## Open Questions

- How do we handle contribution conflicts? (Architect says X, DevSecOps
  says opposite of X)
- Should contributors be able to see each other's contributions before
  posting theirs? (Currently yes — they propagate to parent)
- Should there be a "contribution deadline" after which the main task
  can proceed without optional contributions?
- How does the PM handle contribution tasks that are taking too long?
  (Reassign? Bypass? Escalate?)