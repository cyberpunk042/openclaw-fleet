# Detection — How Diseases Are Found

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Part of:** Fleet Immune System (document 5 of 7)

---

## PO Requirements (Verbatim)

> "detect lazyness, detect deviation, detect AI going Z when A was
> specified"

> "you are the proof that even when the job are clear AI will go ahead
> and deviate and/or do its own retard thing... or make an hallucination
> and work on it, or convince itself its right or something is done
> and/or done well when its not."

---

## What Detection Is

The doctor's ability to identify disease in agents. Without detection,
the immune system is blind. Detection must catch diseases while they're
happening or shortly after — not days later in a retrospective.

---

## Detection Targets

From discussion with PO and disease catalogue:

### Laziness
Agent takes shortcuts, does partial work, skips hard parts.

**Signals identified so far:**
- Acceptance criteria partially met
- Partial completion of scope (updated some but not all)
- Missing artifacts that should be present (tests, docs)
- Unusually fast completion relative to complexity
- Pattern of corrections on completed work

### Deviation
Agent drifts from the spec. Spectrum from minor to severe.

**Signals identified so far:**
- Agent's plan doesn't match verbatim requirement
- Agent touched files/areas not relevant to the task
- Agent added unrequested scope
- Agent's output doesn't address key terms in requirement

### Confident-but-wrong (Z when A)
Agent confidently builds the wrong thing entirely.

**Signals identified so far:**
- Agent's plan describes fundamentally different approach than spec
- Agent creates artifacts the spec didn't ask for
- Agent is productive but on the wrong track
- Agent doesn't flag uncertainty despite ambiguous requirement

### Stuck/Spinning
Agent goes in circles without progress.

**Signals identified so far:**
- No commits for extended period despite active session
- Agent re-reading same files repeatedly
- No progress updates

### Abstraction Disease
Agent replaces literal words with its own interpretation.

**Signals identified so far:**
- Agent's plan uses different terminology than the requirement
- Agent redefines the task in its own words before working

### Context Contamination
Old context warps new requests.

**Signals identified so far:**
- Agent references topics/systems not mentioned in the task
- Agent's output includes concepts from previous tasks

### Cascading Fix-on-Fix
Agent layers fixes, making things worse.

**Signals identified so far:**
- Multiple commits addressing the same issue
- Each commit introduces new problems
- Agent not reverting to known-good state

---

## Detection Timing

From the conversation with PO about how deviation compounds:

**Early detection (plan stage) is cheaper than late detection (code
stage).** An agent's plan is 10-20 lines. Its code diff might be 500
lines. Catching the wrong direction at the plan saves all the tokens
and time of building the wrong thing.

In this session, if the agent's plan had been checked at the point where
it said "I'll create a /fleet-control page in the sidebar" — that's one
sentence that contradicts "in the header bar." Catching it there costs
almost nothing. Catching it after the agent built the whole page,
component tree, and route costs everything.

Detection should happen at multiple stages:
- **At plan submission** — does the plan match the verbatim requirement?
- **During work** — is the agent touching files in scope? Staying on track?
- **At completion claim** — does the output match what was asked?
- **Over time** — is this agent showing patterns of disease across tasks?

Earlier is better. The immune system should prioritize early detection.

---

## Detection Approaches

From research and discussion:

- **Deterministic checks** — code that validates without AI judgment.
  File scope, commit format, structural checks. Cannot be hallucinated
  around. This is the most reliable approach (MIT Technology Review:
  "rules fail at the prompt, succeed at the boundary").
- **Pattern matching** — signals over time. Agent health history.
  Trends in behavior. An agent that consistently gets corrected is
  showing a pattern.
- **Comparison against verbatim requirements** — the anchor for all
  semantic detection. Without the original words, semantic deviation
  is undetectable. This is why verbatim requirements are the "first
  cure" — they enable detection of everything else.

The specific detection mechanisms need further design. The disease
catalogue is a living document — new signals get added as diseases are
observed.

---

## Data Sources — Where the Doctor Looks

The doctor doesn't observe agents directly (it doesn't sit inside their
sessions). It reads the ARTIFACTS and TRACES agents leave behind.

### MC API (task state and metadata)

What it provides:
- Task custom fields: task_readiness, requirement_verbatim, task_stage,
  agent_name, story_points, complexity, pr_url
- Task status: inbox, in_progress, review, done
- Task comments: conversation history, PO corrections
- Approvals: pending, approved, rejected — with comments
- Agent status: online, offline, last_seen_at

What the doctor checks:
- Task readiness vs task stage vs actual agent behavior (protocol violation)
- Correction count in approval history (reversion detection)
- Time since last status change (stuck detection)
- Custom field changes (readiness changed without PO confirmation)

### Event Store (.fleet-events.jsonl)

What it provides:
- Every MCP tool call: which agent called what, when, with what parameters
- Task transitions: when tasks changed status
- Commit events: when agents committed code
- Error events: when things went wrong
- Mode change events: fleet control state changes

What the doctor checks:
- Tool call sequence: did agent call fleet_read_context before
  fleet_commit? (code without reading)
- Tool call timing: fleet_task_accept to fleet_task_complete too fast?
  (laziness)
- fleet_commit during conversation stage? (protocol violation)
- fleet_task_complete without fleet_commit? (lazy — claiming done
  without producing)
- No tool calls for extended period despite active session? (stuck)

### Git (agent work artifacts)

What it provides:
- Diff: which files changed, what was added/removed
- Commit history: sequence, messages, frequency
- Branch state: conflicts, staleness

What the doctor checks:
- Files in diff vs task target_files (scope violation)
- Commit message format (conventional commits standard)
- Commit frequency pattern (many small commits then nothing = stuck?)
- Multiple commits touching same lines (cascading fix-on-fix)

### Plane API (project management state)

What it provides:
- Issue state, assignees, start date, due date, estimates
- Cycle assignment, module membership
- Labels, priority

What the doctor checks:
- Start date + no progress = stuck detection
- High estimate + fast completion = laziness suspicion
- State change without methodology stage alignment = protocol violation

### fleet_task_accept Plan Text

What it provides:
- The agent's stated plan when it accepted the task

What the doctor checks:
- Plan vs verbatim requirement: do the key terms match?
- Plan references specific files? (grounded vs vague)
- Plan describes a fundamentally different approach than requirement?
  (Z when A — the most critical early detection point)

---

## Detection at Each Stage of the Doctor Cycle

The doctor runs each orchestrator cycle (30s). Each cycle:

```
1. READ all active tasks and their custom fields
2. READ recent events from event store (since last cycle)
3. For each agent with active tasks:
   a. Check methodology compliance (right protocol for stage?)
   b. Check for laziness signals (fast completion, missing artifacts)
   c. Check for deviation signals (plan/output vs requirement)
   d. Check for stuck signals (no progress)
   e. Check for contamination signals (off-topic references)
   f. Check for cascade signals (repeated fixes on same issue)
4. For each completed task pending review:
   a. Verify completion claim (PR exists? Tests pass? Criteria met?)
5. Aggregate findings into DoctorReport
6. Execute responses (trigger teaching, prune, compact)
```

Not every check runs every cycle for every agent. The doctor can
prioritize based on:
- Agent health history (agents with prior disease get more scrutiny)
- Task complexity (high story point tasks get more monitoring)
- Time elapsed (agents working longer get more frequent checks)

---

## Open Questions

- How are signals weighted? Which signals are strong indicators vs weak?
- Can multiple diseases be present simultaneously? How does the doctor
  prioritize?
- What's the false positive rate? How does the doctor avoid flagging
  healthy agents?
- How does detection evolve as new diseases are discovered?
- How much of detection is per-cycle vs event-driven (triggered by
  specific events like fleet_task_complete)?
- Should the doctor cache agent health profiles between cycles to
  avoid re-reading everything each time?