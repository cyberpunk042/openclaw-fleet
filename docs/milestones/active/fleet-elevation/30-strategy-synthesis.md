# Strategy Synthesis — Lessons Into Action

**Date:** 2026-03-31
**Status:** Design — embedding learnings into the solution
**Part of:** Fleet Elevation (document 30)

---

## PO Requirements (Verbatim)

> "if we look at the lessons learned is our plan answering it properly?
> did we learn from this session or did you again just scratch the
> surface?"

> "there are strategy to where we aim at something and we go in reverse
> from it. its a bit what planning is for in reality and then there is
> the reverse where we walk the path to get to it. those are important
> notions and it just is an example of the kind of notions we need to
> synthesize and plan for into our solution."

---

## What This Document Covers

The lessons from document 29 weren't just observations — they need
to be EMBEDDED in the solution. This document synthesizes the lessons
into concrete changes to the plan, the methodology, and the fleet's
operational design. It also introduces backward/forward planning as
a first-class concept in how the fleet works.

---

## Backward/Forward Planning — The Concept

### Backward Planning (Goal → Steps)
Start from the end state. Work backward to figure out what needs
to be true for it to exist.

"We want a task to complete with full quality."
→ Fleet-ops needs to verify trail completeness.
→ Trail needs all stage transitions, contributions, PO gates recorded.
→ Trail recording needs to happen at every lifecycle event.
→ The brain needs to record trail events in every chain.
→ event_chain.py chain builders need trail events in every chain.
→ event_chain.py already has `build_task_complete_chain` — extend it.

Each "→" is a requirement derived from the previous one. The last
step connects to EXISTING code. That's the validated plan.

### Forward Planning (Current → Goal)
Start from what exists. Walk forward to see what's possible and
what breaks.

"We have event_chain.py with 3 chain builders."
→ If we add trail recording to each chain, what changes?
→ chain_runner.py needs to handle TRAIL surface (or use INTERNAL).
→ mc.post_memory needs to be called with trail tags.
→ This is a small change — add one Event per chain for trail.
→ Tests: verify trail event exists in every chain's output.

Each "→" is a consequence traced forward. If it hits a contradiction
or impossible requirement, the backward plan needs adjustment.

### Where They Meet
Backward says: "every chain needs trail recording."
Forward says: "adding one Event per chain in event_chain.py, using
existing mc.post_memory via INTERNAL surface, is straightforward."
They AGREE. The plan is validated.

If backward said: "every chain needs real-time video recording"
and forward said: "no video infrastructure exists" — they DISAGREE.
The backward plan is unrealistic. Adjust.

---

## The Fleet's End State — Backward Decomposition

### End State Definition
When the fleet elevation is complete, this is true:

```
1. Every task has a complete TRAIL from creation to completion
   — every stage transition, contribution, gate, approval recorded

2. Every task gets CONTRIBUTIONS from relevant specialists before
   work begins — QA tests, architect design, DevSecOps reqs, UX specs

3. Every agent operates as a TOP-TIER EXPERT — humble, disciplined,
   collaborative, with role-specific professional standards

4. The BRAIN handles all deterministic work — agents only activate
   for cognitive tasks, reducing Claude cost by ~70% on idle agents

5. DELIVERY PHASES are PO-defined and enforced — standards adapt
   per phase, gates require PO approval for advancement

6. TOOL CALL TREES fire from single agent calls — one call, many
   operations, across all surfaces, with failure isolation

7. The AUTOCOMPLETE CHAIN leads agents to correct actions naturally
   — context injection is engineered, not just data dumping

8. MULTI-FLEET identity supports multiple fleets on shared Plane
   — naming, attribution, no collisions

9. Every system PLAYS ITS PART AT THE RIGHT TIME — immune detects,
   teaching corrects, methodology guides, brain orchestrates,
   standards enforce, governance controls

10. The fleet EVOLVES — requirements change, phases change, standards
    tighten, agents improve, all managed and trailed
```

### Backward from Each End State

**End state 1 (complete trails):**
← Fleet-ops verifies trail during review
← Accountability generator audits trail completeness
← Brain records trail events at every lifecycle point
← Every chain builder includes trail event
← event_chain.py chain builders get trail Events
← ALREADY EXISTS: event_chain.py has EventSurface.INTERNAL
← EXTENSION: add trail event to each chain builder

**End state 2 (contributions):**
← Engineer's context includes colleague inputs
← Brain propagates contributions to target task context
← Brain creates contribution opportunity tasks at reasoning stage
← Config defines which roles contribute to which task types
← contributions section in fleet.yaml
← NEW: config section + brain logic + fleet_contribute tool

**End state 3 (top-tier agents):**
← Agents behave as professionals in every interaction
← CLAUDE.md has role-specific professional rules
← IDENTITY.md has top-tier expert characterization
← SOUL.md has anti-corruption + humility values
← Autocomplete chain leads to professional behavior
← ALREADY EXISTS: good CLAUDE.md (67-95 lines per agent)
← EXTENSION: add anti-corruption, contribution, phase sections

**End state 4 (brain handles deterministic work):**
← Sleeping agents cost $0 (brain evaluates)
← Brain decides whether/how to call Claude per agent
← Lifecycle tracks ACTIVE/IDLE/IDLE/SLEEPING
← ALREADY EXISTS: agent_lifecycle.py has 4 states
← EXTENSION: add IDLE, content-aware transitions, strategic calls

**End state 5 (PO-defined phases):**
← Standards library applies phase-specific quality bars
← Brain enforces phase gates
← Phase labels sync to Plane
← Phase config is PO-owned YAML
← NEW: phases.py module + phases.yaml + check_standard with phase

**End state 6 (tool call trees):**
← Every MCP tool fires a complete tree of operations
← ALREADY EXISTS: chain_runner.py + event_chain.py with 3 builders
← ALREADY USED by fleet_task_complete in MCP tools
← EXTENSION: add 5+ new builders, upgrade existing tool trees

**End state 7 (autocomplete chain):**
← Pre-embed data engineers the AI's next action
← Context structured: identity → state → protocol → inputs → action
← ALREADY EXISTS: preembed.py + heartbeat_context.py
← EXTENSION: restructure output format for autocomplete

**End state 8 (multi-fleet):**
← Agent names prefixed with fleet_id
← Git/IRC/Plane attributions include fleet
← ALREADY EXISTS: federation.py has FleetIdentity
← EXTENSION: wire federation into sync, IRC, git operations

**End state 9 (systems at right time):**
← Orchestrator cycle runs systems in correct order
← ALREADY EXISTS: 9-step cycle with 21 modules wired in
← EXTENSION: add steps for event queue, gates, contributions, propagation

**End state 10 (evolution):**
← Requirement changes detected and handled
← Config versioned and trackable
← ALREADY EXISTS: change_detector.py, config_watcher.py
← EXTENSION: per-agent change tracking, requirement change detection

---

## Forward from Current State — What Exists and What Changes

### Current State Summary

```
Core modules:       55 (21 wired into orchestrator, rest in MCP/CLI)
MCP tools:          25 (chain_runner used by fleet_task_complete)
Tests:              821
Daemons:            5 concurrent (sync, monitor, orchestrator, auth, plane)
CLI commands:       17
Scripts:            43
Agent files:        10 agents × 7-8 files (CLAUDE.md already good,
                    IDENTITY/SOUL generic, TOOLS.md auto-generated)
Chain builders:     3 (task_complete, alert, sprint_complete)
Event types:        16 CloudEvents-based
Agent lifecycle:    4 states (ACTIVE, IDLE, SLEEPING, OFFLINE)
Unused modules:     smart_chains.py (never imported)
```

### Forward Trace — What Each Change Ripples Into

**Adding delivery_phase to TaskCustomFields:**
→ mc_client._parse_task needs to extract it
→ configure-board.sh needs the custom field registered
→ plane_sync needs to sync phase labels
→ preembed needs to include phase in context
→ standards.py needs phase-aware checking
→ doctor needs phase violation detection
→ orchestrator dispatch needs phase gate
→ event_display needs phase event renderers
**Ripple count: 8 modules touched from ONE field addition**

**Adding fleet_contribute tool:**
→ event_chain.py needs build_contribution_chain
→ chain_runner.py needs to handle contribution operations
→ context_assembly needs to include contributions
→ preembed needs contributions in autocomplete chain
→ role_providers needs contribution status data
→ change_detector needs per-agent contribution tracking
→ doctor needs contribution avoidance detection
→ teaching needs contribution neglect lessons
→ agent CLAUDE.md needs contribution awareness
→ agent TOOLS.md needs fleet_contribute documentation
**Ripple count: 10 modules + 20 agent files from ONE tool**

This is why the elevation is massive. Each new concept ripples
across the entire system. The plan must account for every ripple.

---

## Does Our Plan Answer the Lessons?

### Lesson 1: Code Awareness
**Current plan:** Doc 28 inventories modules. Implementation rules say
"read before creating."
**Gap:** The milestones (doc 22) phases don't explicitly start with
"read and verify existing code." They start with "create X, modify Y."
**Fix:** Every implementation phase should START with a code audit step:
"Read the modules you're about to touch. Verify what exists. Identify
what to extend vs create. Update doc 28 if new findings."

### Lesson 2: Don't Minimize
**Current plan:** Anti-corruption rules in CLAUDE.md. Teaching system
lessons for compression/abstraction.
**Gap:** No STRUCTURAL enforcement. The autocomplete chain helps but
doesn't guarantee it. The immune system detects compression AFTER it
happens.
**Fix:** The autocomplete chain should include the FULL verbatim
requirement at every context injection. The plan quality check
(plan_quality.py already exists) should verify the plan addresses
ALL aspects of the verbatim, not a subset.

### Lesson 3: Top-Tier Agents
**Current plan:** IDENTITY.md rewrites with characterization.
**Gap:** "Top-tier" is described but not MEASURED. How do we know
an agent is behaving as a top-tier professional?
**Fix:** The accountability generator should have "professional
behavior" metrics alongside compliance metrics. The doctor should
have detection patterns for unprofessional behavior (overconfidence,
bias, shortcuts that a top-tier expert wouldn't take).

### Lesson 4: Tool Call Trees
**Current plan:** Extend event_chain.py with new builders.
**Gap:** Plan validates correctly — event_chain.py already has the
pattern. No gap here.

### Lesson 5: PO-Defined Phases
**Current plan:** Config-driven phases.yaml.
**Gap:** The plan doesn't include the step where the PO ACTUALLY
DEFINES their phases. Implementation creates the mechanism, but who
fills in the content?
**Fix:** Phase A should include: "PO defines initial phases in
phases.yaml. This is PO input, not AI-generated. The PO writes
what each phase means for their projects."

### Lesson 6: Build on Existing
**Current plan:** Doc 28 maps modules. Implementation rules say
"extend, don't create."
**Gap:** The milestones list "NEW: phases.py, contributions.py,
trail.py" — but do ALL of these need to be new? Maybe trail
recording can be in event_chain.py (as trail events in chains).
Maybe contributions can be in smart_chains.py (finally wiring it in).
**Fix:** Each "NEW module" in the milestones should be RE-EVALUATED:
can it be done by extending an existing module instead?

### Lesson 7: Strategic Calls
**Current plan:** Phase I in milestones, doc 23.
**Gap:** Phase I is near the end. But strategic calls affect COST
from day one. If the fleet is burning budget during implementation,
the lifecycle savings should come earlier.
**Fix:** The lifecycle changes (IDLE state, content-aware sleep)
could be partially implemented in Phase A (foundation) since
agent_lifecycle.py already exists and the change is small.

### Lesson 8: UX Everywhere
**Current plan:** UX designer doc says "UX at every level."
**Gap:** But do OTHER agents' CLAUDE.md files mention UX awareness?
Does the engineer's CLAUDE.md say "consider the UX of your CLI
output, error messages, API responses"?
**Fix:** Every agent's anti-corruption / quality section should
include: "Consider the user experience of your output at every
level — not just UI. Error messages, CLI output, API responses,
log formatting, config structure."

---

## Backward/Forward Planning as Fleet Methodology

This isn't just for the elevation. This is how the fleet should
ALWAYS plan:

### For the Architect
**Backward:** "What does the done system look like?" → decompose into
components → identify interfaces → trace back to existing code.
**Forward:** "What exists today?" → trace consequences of changes →
identify ripple effects → validate against backward decomposition.

### For the PM
**Backward:** "What does sprint completion look like?" → which tasks
must be done → which dependencies must clear → which agents need
which work.
**Forward:** "What's the current sprint state?" → which tasks are
in progress → what's blocked → what's next → does it reach the goal?

### For QA
**Backward:** "What does 'correct' look like?" → define test criteria
from the end state → predefine before implementation.
**Forward:** "What does the implementation do?" → trace execution paths
→ compare to predefined criteria → validate or flag.

### For the Engineer
**Backward:** "What does the done feature look like?" → read the plan,
contributions, verbatim → understand end state → implement toward it.
**Forward:** "What does the codebase look like now?" → read existing
code → understand patterns → implement following them.

### For the Brain
**Backward:** "What does a healthy fleet look like?" → all agents
productive or sleeping, all tasks progressing, all gates respected,
budget under control.
**Forward:** "What's the current fleet state?" → which agents are
stuck, which tasks are stale, which gates are pending → take action
to move toward healthy state.

This should be in the methodology. The conversation and reasoning
stages already capture some of this (understand the requirement,
then plan the approach), but the EXPLICIT backward/forward thinking
should be named and taught.

---

## Revised Approach for Each Implementation Phase

Every phase now follows this structure:

```
1. CODE AUDIT: Read every module you're about to touch.
   Update doc 28 if new findings.

2. BACKWARD DECOMPOSITION: Define the end state for this phase.
   What must be true when this phase is done?
   Work backward to the specific code changes needed.

3. FORWARD TRACE: From current code, trace what each change
   ripples into. How many modules are affected?
   Does the ripple count match the backward decomposition?

4. TDD: Write tests FIRST for the end state. Tests are the
   backward plan in code form.

5. IMPLEMENT: Extend existing modules. Follow established patterns.
   One change at a time. Tests pass after each change.

6. VALIDATE: Run full test suite. Verify backward end state is met.
   Verify forward ripples are handled. Update docs.
```

This structure embeds ALL the lessons:
- Step 1 enforces code awareness (lesson 1)
- Step 2 uses backward planning (PO concept)
- Step 3 uses forward planning (PO concept)
- Step 4 uses TDD (PO requirement)
- Step 5 extends existing (lesson 6)
- Step 6 validates completeness (lesson 2 — don't minimize)

---

## What This Changes in the Milestones

Document 22 needs to be updated so that every phase starts with
"CODE AUDIT + BACKWARD DECOMPOSITION + FORWARD TRACE" before any
implementation. The current phases jump straight to "create X,
modify Y" without the planning steps.

This is a META-LESSON: the plan for the plan needs the same rigor
as the plan for the code. Planning is itself a process with stages
(investigate, reason, then act). Our milestones skipped the
investigation step within each phase.

---

## What This Changes for Agent Behavior

The backward/forward thinking should be embedded in agent context:

### In Stage Instructions (stage_context.py)

**Reasoning stage addition:**
```
Before producing your plan, think BACKWARD from the goal:
- What does "done" look like for this task?
- What must be true for that to exist?
- Work backward to the specific code changes.

Then think FORWARD from current state:
- What exists in the codebase now?
- What does each change ripple into?
- Do backward and forward agree?

Your plan should show BOTH: the end state AND the path to get there.
```

**Analysis stage addition:**
```
Think FORWARD from what exists:
- What is the current state of the code/system/feature?
- What are the consequences of changing it?
- What other systems are affected?
```

### In CLAUDE.md (All Agents)

```
## Planning Methodology
When planning any work:
1. Define the end state (what does done look like?)
2. Decompose backward (what needs to be true?)
3. Trace forward (what exists, what changes?)
4. Validate (do backward and forward agree?)
5. Execute (extend existing, follow patterns)
```

---

## Did We Actually Learn?

Yes — but the learning was INCOMPLETE until this document.

Document 29 listed lessons. This document SYNTHESIZES them:
- Lessons aren't just observations — they change the plan
- Backward/forward planning isn't just a concept — it's embedded
  in stage instructions, CLAUDE.md rules, and phase structure
- Each lesson has a GAP in the current plan and a FIX
- The implementation phases now have a structure that enforces
  the lessons (audit → backward → forward → TDD → implement → validate)

The question the PO asked — "did we learn?" — is answered by whether
the PLAN CHANGED because of the lessons. It did. Every implementation
phase now starts with code audit and bidirectional planning. Every
gap identified has a fix. The methodology gains backward/forward as
a named concept.

If the plan didn't change, we didn't learn. It changed.