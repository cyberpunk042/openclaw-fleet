# Evolution and Change Management

**Date:** 2026-03-30
**Status:** Design — how the fleet handles change
**Part of:** Fleet Elevation (document 27 — added to series)

---

## PO Requirements (Verbatim)

> "Things can evolve. The requirements, the things to test, the phases
> of the task, the various data blob for whatever different type we need
> + the main one and so on."

> "its important to respect pattern and to know when to evolve and
> refactor, and when to change and when to remove and when to upgrade
> and when to update"

---

## What This Document Covers

How the fleet handles change — not just building new things, but
evolving existing things. Requirements change mid-task. Phases
change mid-delivery. Tests change as understanding grows. Standards
change as quality improves. Configuration changes as the fleet
matures. Code changes as patterns evolve.

This is the design for change management across every dimension.

---

## Requirement Evolution (Verbatim Changes Mid-Task)

### The Problem
A task is in progress. The agent has an accepted plan, maybe partial
implementation. Then the PO changes the requirement — the verbatim
changes, or acceptance criteria change, or the scope changes.

### How It Works

1. **PO updates verbatim requirement** on the task (OCMC custom field
   or Plane issue update → sync picks up)

2. **Brain detects the change** in the next cycle:
   - change_detector sees task custom fields changed
   - Specifically: requirement_verbatim or description changed
   - Event emitted: `fleet.task.requirement_changed`

3. **Chain fires:**
   - Agent notified: mention in board memory with new requirement
   - Task readiness may regress (brain evaluates: how different is
     the new requirement from the old one?)
   - If agent is in work stage and verbatim changed significantly
     → readiness regresses to reasoning (re-plan needed)
   - If minor change → agent notified, readiness stays, work adjusts
   - Trail records: "Requirement changed. Old: {old}. New: {new}."

4. **Contributions may invalidate:**
   - QA's predefined tests were based on OLD requirement
   - If requirement changed significantly → QA contribution
     invalidated → new QA contribution task created
   - Same for architect design, DevSecOps requirements
   - Brain evaluates: which contributions are still valid?

5. **Agent's next heartbeat:**
   - Pre-embed includes: "REQUIREMENT CHANGED. Old: {old}. New: {new}.
     Your plan was based on the old requirement. Re-evaluate."
   - Autocomplete chain leads to: re-read requirement, assess impact,
     update plan or restart from appropriate stage

### Severity of Change

| Change Type | Impact | Action |
|-------------|--------|--------|
| Typo fix, clarification | None | Agent notified, work continues |
| Scope refinement (subset) | Minor | Agent adjusts plan, readiness stays |
| Scope expansion (superset) | Moderate | Re-plan needed, readiness → reasoning |
| Direction change | Major | All contributions invalidated, readiness → analysis or conversation |
| Complete rewrite | Total | Fresh start, readiness → 0, previous artifacts archived |

The brain evaluates change severity by comparing old vs new verbatim
text. Simple heuristic: word overlap percentage. Deep analysis would
require AI — but the NOTIFICATION is deterministic, the EVALUATION
of severity is where judgment matters.

For significant changes, the PO explicitly sets the new readiness
(they're regressing). For minor changes, the system notifies and
the agent adapts.

---

## Phase Evolution

### Phases Are PO-Defined — They Can Change

The PO owns `config/phases.yaml`. They can:
- Add a new phase to a progression (e.g., add "load-tested" between
  staging and production)
- Change standards for an existing phase
- Create entirely new progressions
- Remove phases that are no longer relevant

### What Happens When Phase Config Changes

1. PO updates `config/phases.yaml`
2. Brain reads new config on next cycle
3. Tasks in affected phases get updated standards
4. Agents' context refreshed with new phase standards
5. If standards TIGHTENED: tasks that were compliant may now have gaps
   → PM notified of affected tasks
6. If standards LOOSENED: no action needed (still compliant)

### Deliverable Phase Can Change

The PO can change a deliverable's phase at any time:
- Advance: POC → MVP (normal, through gate)
- Regress: MVP → POC (PO decides MVP wasn't ready)
- Skip: POC → staging (PO decides POC is good enough for staging)
- Custom: assign any phase from any progression

Each change is recorded in the trail with the PO's rationale.

---

## Test Evolution

### Predefined Tests Can Change

QA predefines tests at reasoning stage. But requirements evolve.
What happens to predefined tests when:

**Requirement changes:** Tests that reference the old requirement
are flagged. QA receives a contribution task to update test criteria.
Old tests are archived, new tests reference new requirement.

**Implementation reveals edge cases:** During work stage, engineer
discovers edge cases not covered by predefined tests. Engineer
posts a comment: "Discovered edge case: {description}. Not covered
by predefined tests." QA receives notification, can update tests.

**Review reveals gaps:** Fleet-ops or QA finds gaps during review.
Tests updated for next iteration. Trail records the gap and update.

### Test evolution is NORMAL — not a failure. Tests improve as
understanding grows. The system supports this by allowing QA to
update test criteria at any point, with trail tracking the evolution.

---

## Standard Evolution

> "we need to do a gold job, we need to elevate the quality and the
> standard"

Standards evolve as the PO identifies quality gaps:

### The Evolution Cycle

1. **PO identifies gap:** "Tasks are being completed without proper
   test evidence in the completion claim."
2. **Standard updated:** `completion_claim` standard in `standards.py`
   adds `test_results` as required field.
3. **Config updated:** if phase-aware, `config/phases.yaml` adds the
   requirement to relevant phase standards.
4. **Teaching updated:** New lesson template for "completion without
   test evidence."
5. **Detection updated:** Doctor pattern for missing test results.
6. **Accountability updated:** Compliance checks include new standard.

### What Happens to In-Progress Work

When a standard changes:
- Tasks NOT YET in review: new standard applies (they'll be reviewed
  against it)
- Tasks IN review: reviewed against the standard that was active
  when they entered review (no retroactive standard changes)
- Tasks DONE: not affected (they met the standard of their time)
- Future tasks: new standard applies from creation

This prevents retroactive standard changes from invalidating
completed work.

---

## Code Evolution — When to Refactor

> "its important to respect pattern and to know when to evolve and
> refactor, and when to change and when to remove and when to upgrade
> and when to update"

### Decision Framework

The architect evaluates evolution decisions. The PM plans the work.
The PO approves strategic evolution decisions.

| Situation | Action | Who Decides |
|-----------|--------|-------------|
| Code works but poor structure | Refactor | Architect proposes, PO approves |
| Better pattern discovered | Evolve | Architect proposes, PO approves |
| Unused code/feature | Remove | Architect identifies, PM creates task |
| Dependency has new version | Upgrade | DevOps evaluates risk, PM plans |
| Bug in dependency | Update (patch) | DevOps evaluates urgency |
| New feature needs new pattern | Change | Architect designs, engineer implements |
| Technical debt accumulating | Plan | Architect flags, PM creates sprint work |
| Standard changed | Adapt | All agents adapt in new work |

### Evolution Is Planned Work

Evolution isn't accidental. It's:
1. Architect or agent identifies evolution need
2. Creates a task or proposes to PM
3. PM evaluates priority vs current sprint work
4. PO approves if strategic
5. Work goes through normal methodology stages
6. No "while I'm here" evolution inside other tasks — scope stays clean

---

## Configuration Evolution

### When Config Changes

Config changes go through a process:
1. Change proposed (by PO, PM, or agent suggestion)
2. Change reviewed (architect for structural, DevOps for infra)
3. Change applied to config file
4. Brain reads new config on next cycle
5. Affected agents get updated context
6. Trail records: "Config changed: {section}. Reason: {why}."

### Version Control

All config files are git-tracked. Changes are committed with
conventional commits:
```
chore(config): update phase standards for MVP
chore(config): add ux-designer to contribution rules
chore(config): increase architect drowsy threshold
```

This provides traceability: when did a config change, who requested
it, why.

### Backward Compatibility

When adding new config sections:
- Code must handle missing sections gracefully (defaults)
- New config fields have defaults so existing configs still work
- Migration path documented if breaking changes are needed

---

## Agent File Evolution

### When Agent Files Change

Agent files evolve as the fleet matures:
- CLAUDE.md gets new rules as quality gaps are identified
- TOOLS.md gets chain updates as new tools are added
- HEARTBEAT.md evolves as contribution model matures
- IDENTITY.md updates if agent naming changes

### Template Evolution

When the template changes:
1. Update `agents/_template/`
2. Run `scripts/validate-agents.sh` against all agents
3. Identify which agents don't match new template
4. Update each agent to match
5. Commit as fleet-wide update

### Preserving Agent State During Evolution

When agent files change:
- Agent's CURRENT session is unaffected (files already loaded)
- NEXT heartbeat picks up new files
- If change is significant: consider pruning the agent so it
  starts fresh with new files
- context/ files are brain-generated — they auto-refresh

---

## How the Fleet Handles Surprises

### Unexpected Task During Work

Agent discovers something unexpected while implementing:
- Don't change scope — create a subtask via `fleet_task_create`
- Let PM evaluate the subtask
- Continue current task scope
- The subtask gets its own lifecycle

### Unexpected Failure

Something breaks that nobody anticipated:
- Agent reports via `fleet_alert` or `fleet_escalate`
- PM creates blocker task
- Brain's chain fires: blocker notifications
- Resolution path: investigate → fix → verify

### Unexpected PO Decision

PO makes a decision that invalidates current work:
- PO regresses readiness with explanation
- Brain fires regression chain: notify agent, update stage, trail
- Agent reads regression feedback in next heartbeat
- Work restarts from appropriate stage
- Old work preserved in trail (not deleted)

### Unexpected Budget Crisis

Budget monitoring detects fast climb or threshold breach:
- Brain adjusts: effort profile → conservative or minimal
- Sleeping agents stay sleeping
- Active agents finish current cycle, then reduce heartbeat frequency
- PO notified via ntfy
- Brain resumes normal operation when budget recovers

---

## Trail Through Evolution

Every change is trailed:
- Requirement changes: old vs new verbatim, who changed, when
- Phase changes: old vs new phase, PO's rationale
- Standard changes: what changed, why
- Config changes: git commit with conventional message
- Agent file changes: what was updated, why
- Contribution invalidation: which contributions affected, why
- Readiness regressions: amount, reason, impact

The accountability generator reads these trails to verify that
evolution was MANAGED, not chaotic. Evolution is expected and
healthy. Untracked evolution is a compliance gap.

---

## Open Questions

- How does the brain detect "significant" vs "minor" verbatim changes?
  (Heuristic word overlap? Semantic comparison via AI? PO specifies
  severity when they change the requirement?)
- Should there be a "change request" workflow where the PO formally
  requests a change and the PM evaluates impact before applying?
- How do we handle cascading changes? (Requirement A changes →
  tests B invalidate → plan C needs revision → contributions D
  need redoing)
- Should evolved requirements maintain a HISTORY? (Not just current
  verbatim but the evolution chain: v1 → v2 → v3)