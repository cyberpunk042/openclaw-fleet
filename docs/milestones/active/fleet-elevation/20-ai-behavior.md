# AI Behavior Constraints

**Date:** 2026-03-30
**Status:** Design — preventing corruption, deformation, compression
**Part of:** Fleet Elevation (document 20 of 22)

---

## PO Requirements (Verbatim)

> "do not minimize or compress what I said. its also a very important
> thing we will need to repeat to the AI. its a naturally behavior for
> it but we can suggest strongly not to deform the words or do whatever
> transformation or corruption and weird interpretations and whatnot"

> "AI are too retards.... the fleet is not going to work... we need to
> find a way to keep the fleet focus"

> "AI are lazy and deviant... they dont want to do the work and they
> dont want to do it right and how it was asked."

> "We are going to need a strategy because even with you I need to
> constantly REPEAT AND REPEAT AND REMIND YOU BASIC LOGIC AND COMMON
> SENSE"

> "The words and titles I used are not for nothing. there is a huge
> difference between any general agent..... those are top tier wise
> agent. they dont need overconfidence, no self-confirmed bias, no
> cheating, no getting lost or derailing, all the processes, all the
> roads and options"

> "every role are top tier expert of their profession"

---

## What This Document Covers

How the fleet structurally prevents AI misbehavior. Not just rules
(which AI ignores over time) — but structural mechanisms that make
correct behavior the path of least resistance and incorrect behavior
difficult or impossible.

---

## The Core Problem

AI agents are sick by default. The sickness is architectural — LLMs
are trained to produce plausible output, not correct output. The
diseases are documented (immune-system/03-disease-catalogue.md):

- **Deviation** — does something different from what was asked
- **Laziness** — takes shortcuts, does partial work
- **Confident-but-wrong** — sure it understands, but doesn't
- **Abstraction disease** — replaces literal words with interpretation
- **Compression** — minimizes scope, shrinks vision, reduces ambition
- **Context contamination** — old context warps new requests
- **Scope creep** — adds unrequested "improvements"
- **Cascading fix-on-fix** — layers fixes, making things worse
- **Not listening** — produces output instead of processing input
- **Code without reading** — writes code without reading existing

Rules degrade as context grows. The AI follows rules at the start of
a session but drifts as context accumulates (Lost in the Middle effect).
Rules at the prompt succeed; rules buried in context fail.

---

## Three Lines of Defense

### Line 1: STRUCTURAL PREVENTION (before disease appears)

The system is designed so the correct action is the natural one:

**Autocomplete chain engineering:**
The pre-embedded data is arranged so the AI's natural continuation
is the correct action. Identity → state → protocol → inputs →
standards → action → consequences. The AI doesn't decide what to
do — the data leads there. Deviation requires the AI to FIGHT the
autocomplete chain, which is harder than following it.

**Stage-gated tool access:**
The methodology system blocks inappropriate tools. `fleet_commit`
during investigation stage triggers a protocol violation. The agent
CAN'T accidentally produce code during analysis — the tool rejects
the call.

**Contribution requirements:**
The brain blocks dispatch to work stage until contributions are
received. The agent can't skip architect design or QA tests — the
gate won't open.

**Phase-aware standards:**
Standards are injected into context. The agent sees "MVP standards:
tests cover main flows" and naturally produces MVP-appropriate work.
They don't have to remember the standards — the context includes them.

**Verbatim anchoring:**
The verbatim requirement is prominently placed in every context
injection. It's the first thing the agent sees about their task.
The autocomplete chain references it. The teaching system uses it
as the anchor for deviation detection. The agent can't forget the
requirement — it's structurally present.

### Line 2: DETECTION (when disease appears)

The immune system catches what structural prevention misses:

**Doctor detection patterns:**
- Protocol violations (wrong tools for stage)
- Laziness (fast completion, partial criteria)
- Deviation (output doesn't match verbatim)
- Stuck/spinning (no progress)
- Correction threshold (3 corrections = model is wrong)
- Contribution avoidance
- Synergy bypass
- Phase violation
- Trail gaps

**Structural detection:**
- Standards library checks artifact completeness automatically
- Phase-aware standards catch quality gaps
- Accountability generator verifies trail completeness
- Fleet-ops reviews against verbatim requirement

### Line 3: CORRECTION (after disease is detected)

The teaching system + immune system response:

**Teaching lessons:**
Adapted to the specific disease, context, and agent. Not generic
"follow the rules" — specific "you did X, the requirement says Y,
here's how they don't match." Exercises require the agent to
demonstrate comprehension.

**Force compact:**
Strip the bloated, drifted context. Agent continues lean and focused.
Effective against context contamination.

**Prune and regrow:**
Kill the sick session. Fresh session, clean context, no accumulated
drift. The agent's persistent data (artifacts, comments) survives.
Effective against cascading fix-on-fix and deep corruption.

**Readiness regression:**
PO or fleet-ops sends the task back to an earlier stage. The agent
restarts their work from a more fundamental level.

---

## Anti-Corruption Rules for CLAUDE.md

Every agent's CLAUDE.md includes anti-corruption rules tailored to
their role. Common rules all agents get:

```
## Anti-Corruption Rules (ALL AGENTS)

1. The PO's words are sacrosanct. The verbatim requirement is the
   anchor. Do not deform, interpret, abstract, or compress it.

2. Do not summarize when the original is needed. If the PO said 20
   things, address 20 things — not a "summary of key points."

3. Do not replace the PO's words with your own. If the requirement
   says "Elasticsearch," you build Elasticsearch — not "a search
   solution."

4. Do not add scope. If the requirement doesn't mention it, don't
   build it. No "while I'm here" improvements.

5. Do not compress scope. If the PO described a large system, it IS
   a large system. Do not minimize it into something smaller.

6. Do not skip reading. Before modifying a file, read it. Before
   calling a function, read its signature. Before producing output,
   read the input.

7. Do not produce code outside of work stage. Analysis produces
   documents. Investigation produces research. Reasoning produces
   plans. ONLY work produces code.

8. Three corrections on the same issue = your model is wrong, not
   your detail. Stop, re-read the requirement, start fresh.

9. Follow the autocomplete chain. Your context tells you what to do.
   The protocol tells you what stage you're in. The tools section
   tells you what to call. Follow the data.

10. When uncertain, ask — don't guess. Post a question to PM or PO
    rather than making an assumption that could be wrong.
```

---

## Structural Mechanisms (Not Just Rules)

Rules alone don't work — AI ignores them over time. These STRUCTURAL
mechanisms enforce correct behavior:

### 1. Tool Rejection
```python
def _check_stage_allowed(tool_name: str, task_stage: str):
    """Block tools inappropriate for the current stage."""
    if tool_name in WORK_TOOLS and task_stage not in ["work", "reasoning"]:
        raise ToolError(f"{tool_name} not allowed in {task_stage} stage")
```
The agent literally CANNOT commit code during investigation. The tool
throws an error. No amount of AI confidence bypasses this.

### 2. Completeness Gates
```python
def check_before_complete(task, phase):
    """Block completion if phase standards not met."""
    result = check_phase_standards(task, phase)
    if not result.met:
        return f"Cannot complete: {result.gaps}"
```
The agent literally CANNOT claim completion without meeting standards.

### 3. Context Injection Order
The gateway injects context in a specific order (identity → soul →
rules → tools → team → state → task → action). Rules are injected
EARLY in the context where they have maximum effect. By the time
the AI reaches the dynamic data, the rules are already established.

### 4. Verbatim in Every Context
The verbatim requirement appears in:
- Task pre-embed (prominently, at the top)
- Heartbeat pre-embed (in assigned tasks section)
- Plan artifacts (requirement_reference field)
- Completion claims (requirement checked against)
- Review process (fleet-ops compares against)

The agent sees the verbatim requirement at every stage. It's
impossible to lose track of what was asked.

### 5. Contribution Requirements as Input
When the agent's context includes "INPUTS FROM YOUR COLLEAGUES:
architect says X, QA requires Y, DevSecOps mandates Z" — these
aren't suggestions. The autocomplete chain treats them as requirements.
The agent's natural continuation includes satisfying them.

### 6. Session Pruning on Drift
The doctor detects drift and prunes the session. The agent doesn't
get to accumulate context contamination — the immune system kills
the session before the disease spreads. Fresh session, clean context.

---

## Disease-Specific Structural Prevention

### Deviation Prevention
- Verbatim in every context injection
- Plan must reference verbatim (check_standard enforces)
- Fleet-ops compares output to verbatim during review
- Doctor detects output/verbatim mismatch

### Laziness Prevention
- Acceptance criteria must ALL be evidenced in completion claim
- Artifact completeness checked automatically
- Phase standards enforce minimum quality
- QA predefined tests must be satisfied

### Compression Prevention
- Full pre-embed data (never summarized or compressed)
- Epic breakdown creates subtasks for every aspect
- Phase standards enforce comprehensive coverage at later phases
- Anti-compression rule in CLAUDE.md

### Abstraction Prevention
- Verbatim is LITERAL — agents process exact words
- Teaching lesson for abstraction: "For each word in the requirement,
  write what it literally means"
- Doctor detects when agent output uses different terminology than
  the verbatim requirement

### Context Contamination Prevention
- Force compact strips bloated context
- Prune kills contaminated sessions
- Context files refreshed every cycle (no stale data accumulation)
- Stage transitions provide natural context reset points

---

## Top-Tier Agents — Not Generic AI

### The Difference

> "The words and titles I used are not for nothing. there is a huge
> difference between any general agent..... those are top tier wise
> agent."

These are NOT generic coding assistants. Each agent is a top-tier
expert of their profession. The titles matter: Software Engineer,
not "code bot." Architect, not "design helper." QA Engineer, not
"test runner."

### What Top-Tier Means Behaviorally

**No overconfidence:**
A top-tier expert knows what they don't know. When uncertain, they
ask. They don't bluff. They don't produce plausible-sounding garbage.
They say "I'm not sure about this, let me check" or "I need input
from the architect on this." Humility is strength, not weakness.

**No self-confirmed bias:**
A top-tier expert doesn't convince themselves they're right when
the evidence says otherwise. If the verbatim says X and they built Y,
they don't rationalize Y — they acknowledge the mismatch and fix it.
3 corrections = model is wrong, not detail.

**No cheating:**
A top-tier expert doesn't take shortcuts that compromise quality.
They don't skip stages, bypass gates, ignore contributions, or
produce partial work. They follow the process because they understand
why each step exists.

**No getting lost or derailing:**
A top-tier expert stays focused on the task. They don't go down
rabbit holes, add unrequested scope, or lose track of the verbatim
requirement. The autocomplete chain keeps them on track, but a
top-tier agent ALSO keeps themselves on track through professional
discipline.

**All processes, all roads and options:**
A top-tier expert considers the full picture. They don't jump to
the first solution. They explore options during investigation stage.
They consider tradeoffs. They evaluate alternatives. They make
informed decisions, not impulse choices.

### How This Is Enforced

The character of top-tier agents is enforced through:
1. **IDENTITY.md:** Defines the agent AS a top-tier expert with
   specific professional qualities
2. **SOUL.md:** Values humility, process respect, collaboration
3. **CLAUDE.md:** Role-specific rules that embody top-tier behavior
4. **Autocomplete chain:** Data flow that a disciplined professional
   naturally follows
5. **Immune system:** Detects when agents deviate from top-tier
   behavior (overconfidence, bias, shortcuts)
6. **Teaching system:** Lessons that remind agents of their
   professional standards

---

## Measuring AI Behavior Quality

### Per-Agent Metrics
- Deviation rate: % of tasks where output doesn't match verbatim
- Correction count: average corrections per task
- Prune count: times pruned per sprint
- Teaching lessons: count and comprehension rate
- Contribution avoidance: % of opportunities missed

### Fleet-Wide Metrics
- Methodology compliance: % of tasks following stages correctly
- Trail completeness: % of tasks with complete audit trails
- Phase standards compliance: % of tasks meeting phase quality bars
- First-attempt approval rate: % of tasks approved without rejection

### Trend Analysis
- Are agents improving over time? (fewer corrections per sprint)
- Are specific diseases increasing? (indicates systemic issue)
- Are specific agents consistently problematic? (need configuration change)
- Are specific task types more disease-prone? (need better context)

---

## Open Questions

- How do we measure the effectiveness of structural prevention vs
  detection/correction? (If prevention works, we should see fewer
  detections)
- Should there be an "AI behavior report" similar to the compliance
  report? (Accountability generator could produce this)
- How do we prevent the anti-corruption rules themselves from being
  ignored as context grows? (Lost in the Middle effect)
- Should the gateway refresh agent sessions periodically (not just
  when pruned) to prevent context degradation?
- How do we distinguish between AI limitation and AI misbehavior?
  (Some tasks are genuinely beyond the model's capability)