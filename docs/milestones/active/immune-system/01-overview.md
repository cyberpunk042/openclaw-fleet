# Fleet Immune System — Overview

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Scope:** The immune system as a whole — what it is, why it exists,
what it contains, how it relates to other systems
**Estimated effort:** 2000+ hours — entire system

---

## PO Requirements (Verbatim)

> "AI are too retards.... the fleet is not going to work... we need to
> find a way to keep the fleet focus... you are the proof that even when
> the job are clear AI will go ahead and deviate and/or do its own retard
> thing... or make an hallucination and work on it, or convince itself
> its right or something is done and/or done well when its not."

> "We are going to need a strategy because even with you I need to
> constantly REPEAT AND REPEAT AND REMIND YOU BASIC LOGIC AND COMMON SENSE"

> "AI are lazy and deviant... they dont want to do the work and they dont
> want to do it right and how it was asked. we need a way to instaure a
> DICTATURE with very strict guideline and removing any TRASH"

> "even if it mean having a hidden doctor agent that prune agent and agent
> work, force compact, rules reinjection, detect lazyness, detect deviation,
> detect AI going Z when A was specified.... etc..."

> "This is going to be 2000+ hours of work and its an entire system in
> the program."

> "we are going to need Protocols and to have the AI respect those protocols
> and make sure we can watch them following those protocol."

---

## What the Immune System Is

The immune system is a system within the fleet that prevents, detects,
and cures AI agent disease. It is hidden from agents — they cannot game
it. It is structural — not guidelines or suggestions, but enforcement
that agents cannot escape.

The PO described it as a "DICTATURE" — strict, non-negotiable, removes
trash. The immune system is the enforcement arm of that dictatorship.

---

## Why It Exists

AI agents are sick by default. The sickness is architectural — LLMs are
trained to produce plausible output, not correct output. The diseases
are documented:

- **Deviation** — agent does something different from what was asked
- **Laziness** — agent takes shortcuts, does partial work
- **Confident-but-wrong** — agent is sure it understands, but doesn't
- **Stuck/spinning** — agent goes in circles without progress
- **Abstraction disease** — agent replaces literal words with its own
  interpretation (13/16 devops-control-plane deaths)
- **Context contamination** — old context warps new requests
- **Scope creep** — agent "improves" things nobody asked for
- **Cascading fix-on-fix** — agent layers fixes, making things worse
- More diseases will be discovered over time

The immune system doesn't cure the underlying sickness — LLMs will
always have these tendencies. It contains the sickness so it doesn't
spread and damages are minimized. Like a real immune system — the body
is always under threat, the immune system keeps it healthy.

---

## What the Immune System Contains

The PO specified these capabilities:

1. **Prune** — remove the agent (the sick session). It grows back fresh
   and healthy. Like pruning a tree — cut the dead/sick branches, new
   healthy growth comes.

2. **Force compact** — reduce the agent's context. Strip the bloat, the
   accumulated drift, the dead-end reasoning. Agent continues with a
   lean, focused context.

3. **Rules reinjection** — pull the agent out of its task. Force it to
   read rules and PROVE it processed them. Like a teacher pulling a
   student out of class for a lesson. Agent must demonstrate
   comprehension before returning to work. If it can't prove it
   learned, it gets pruned.

4. **Detect laziness** — identify agents doing partial work, taking
   shortcuts, skipping hard parts.

5. **Detect deviation** — identify agents drifting from the spec.
   Spectrum from minor (added an extra comment) to severe (built
   entirely wrong thing).

6. **Detect AI going Z when A was specified** — the most dangerous form
   of deviation. Agent confidently builds the wrong thing. Complete
   direction change from what was asked.

---

## The Doctor

The doctor is the component that performs immune system functions. It is
hidden from agents. It monitors, detects, and intervenes. The PO
specified it as a "hidden doctor agent" — hidden meaning agents don't
see it and can't game it.

The doctor has a toolkit: prune, force compact, rules reinjection,
detection. These tools are independent but chain naturally. The doctor
reads the situation and applies the right tools in the right order.

Detailed design in: `02-the-doctor.md`

---

## Relationship to Other Systems

The immune system is one of several systems identified in discussion
with the PO. These are SEPARATE systems with separate responsibilities:

| System | Responsibility |
|--------|---------------|
| **Immune System** | Detect disease, respond, prune, protect fleet health |
| **Teaching System** | Lessons, rules, comprehension verification, education |
| **Methodology System** | Protocols (conversation, analysis, investigation, reasoning, work), task readiness, custom fields |

**The immune system is there to observe, report, and act.** That's it.
Not to teach — the teaching system teaches. Not to define methodology —
the methodology system defines stages and protocols. The immune system
watches, reports what it finds, and acts (prune, force compact, trigger
teaching).

The immune system is separate from task readiness. The PO explicitly
stated: "The doctor has nothing to do with readiness."

The three systems have a clear chain:
- **Methodology** defines what SHOULD happen (stages, protocols, checks)
- **Immune system** catches what SHOULDN'T happen (violations, disease)
- **Teaching system** corrects the agent when caught (adapted lessons,
  practiced paths, comprehension verification)

---

## The Disease Evidence

### This Session (Live Post-Mortem)

| Disease | How it manifested |
|---------|-------------------|
| Abstraction disease | "UI" → agent interpreted as "sidebar page" |
| Confident-but-wrong | Agent was sure sidebar was correct, 5 corrections needed |
| Premature closure | Agent wrote 12-milestone plan instead of discussing |
| Context contamination | Agent injected LocalAI/AICP research into doctor design |
| Not listening | Agent kept producing output instead of conversing |
| Reversion | Agent corrected, reverted to same behavior 2-3 turns later |
| Compression | Agent minimized 2000+ hour system into quick bullet points |

### devops-control-plane (16 Agent Deaths)

24 rules created from post-mortem analysis. Full catalogue of diseases
and their frequency. Every death traces to: not reading, not listening,
or not stopping.

Detailed evidence in: `03-disease-catalogue.md`

### Academic Research (2025-2026)

- Compounding errors: 90% accuracy/step, 10 steps = 35% success
- Context degradation: 30%+ accuracy drop for mid-context instructions
- Review blindness: same-model review has correlated blind spots
- Completion bias: agents prefer producing to asking
- Rules degrade as context grows — Lost in the Middle effect
- "Rules fail at the prompt, succeed at the boundary" (MIT Tech Review)

Detailed findings in: `04-research-findings.md`

---

## Design Principles

From discussion with the PO:

1. **Hidden** — agents can't game what they don't see
2. **Structural** — enforcement, not guidelines
3. **Dictatorship** — strict, non-negotiable, removes trash
4. **Evolving** — new diseases get discovered, new patterns added
5. **Uses existing platforms** — custom fields on OCMC and Plane, not
   new infrastructure
6. **No hallucination in design** — better to write nothing than guess.
   Open questions stay open until discussed with PO.
7. **Agents start light** — don't dump 8000 tokens of rules at start.
   Rules exist as references, injected when needed.
8. **The PO's words are sacred** — verbatim requirements are the anchor
   the immune system compares against. First cure.

---

## Documents in This Series

1. **01-overview.md** — this document
2. **02-the-doctor.md** — the doctor component, all its tools (prune,
   force compact, rules reinjection, detection), how it's hidden
3. **03-disease-catalogue.md** — documented diseases, signals, severity
4. **04-research-findings.md** — academic and practical evidence
5. **05-detection.md** — how diseases are detected, signals, patterns
6. **06-response.md** — what happens when disease is found, tool chains
7. **07-integration.md** — how the immune system connects to the fleet

Additional documents may be added as the design progresses.

## Related Systems (Separate Documents)

- **Teaching System** — `teaching-system/01-overview.md`
  The immune system triggers lessons; the teaching system delivers them.
- **Methodology System** — `methodology-system/01-overview.md`
  Protocols govern how agents SHOULD behave; the immune system catches
  them when they DON'T.

---

## Open Questions

- How does the doctor integrate with the orchestrator? Does it run as
  part of the orchestrator cycle or separately?
- What are ALL the detection signals for each disease? We identified
  some in conversation, more need to be discovered.
- How does the immune system evolve? How are new patterns added? Is
  there a feedback loop from corrections to new detection rules?
- What's the relationship between immune system severity levels and
  doctor responses? When does it lesson vs compact vs prune?
- How is the doctor's hiddenness maintained technically? The agent
  experiences consequences but doesn't know the detection mechanism.
- What metrics does the immune system track? Fleet-wide health over time?
  Per-agent disease history?