# Disease Catalogue

**Date:** 2026-03-30
**Status:** Design — from discussion with PO + devops-control-plane evidence
**Part of:** Fleet Immune System (document 3 of 7+)

---

## Purpose

This is a living document. New diseases are added as they're discovered.
The immune system evolves to detect and respond to new patterns.

---

## Diseases Identified in Discussion with PO

### 1. Deviation

Agent does something different from what was asked. A spectrum:
- Minor: adds an extra comment, small scope addition
- Medium: modifies extra files, adds unrequested features
- Severe: builds entirely different thing (see #3)

**PO evidence:** "AI will go ahead and deviate and/or do its own retard
thing"

### 2. Laziness

Agent takes shortcuts. Does partial work. Skips hard parts. Does the
minimum to appear productive.

**PO evidence:** "AI are lazy and deviant... they dont want to do the
work and they dont want to do it right and how it was asked"

### 3. Confident-but-wrong (Z when A was specified)

Agent is sure it understands. Produces a lot of work. All of it
coherent and well-structured. All of it built on a wrong foundation.
The most dangerous disease because it looks good on the surface.

**PO evidence:** "convince itself its right or something is done and/or
done well when its not"

**Live evidence — the control surface task:**

The PO said "add fleet controls to the OCMC UI." The agent:
1. Proposed text commands in board memory (confident, wrong)
2. Proposed a separate page in the sidebar (confident, wrong)
3. Started reading the board view code (confident, wrong)
4. Still didn't understand after being told "not the board view"
5. Finally understood "header bar" after explicit direction
6. Then wrote a 12-milestone plan without discussing (confident, premature)

At every step the agent was sure it was right. It never flagged
uncertainty. It never said "I don't know where in the UI you mean."
It picked the most familiar pattern (sidebar page) and built on it.

This is the most dangerous disease because if this had been an
autonomous agent on the fleet board — no human correcting it — it would
have built a complete, well-structured, tested sidebar page. The PR
would have looked clean. Fleet-ops (also an AI) might have approved it.
And it would have been completely wrong.

**Live evidence — the immune system design:**

The PO said "prune agent and agent work." The agent interpreted this as
git operations (selective hunk revert) and LocalAI inference routing for
semantic checks. None of this was asked for. The agent took the word
"prune" and built an entire technical system around its own interpretation
instead of understanding what the word actually means: to remove what is
unwanted, unnecessary, or superfluous.

It took multiple prompts to establish that pruning an agent means killing
the sick session so it grows back fresh — like pruning a tree. The
definition of the word IS the meaning. The agent replaced the obvious
meaning with technical complexity.

**Why this disease is the hardest to detect:**

The agent's output is syntactically valid. The code compiles. Tests pass.
The structure is clean. Everything LOOKS correct. The only way to detect
it is to compare the output against the original words — the verbatim
requirement. If the requirement says "header" and the agent built a
sidebar, that's detectable. But only if the original words are preserved
and compared against.

### 4. Stuck/Spinning

Agent goes in circles. Re-reads files. Produces plans and discards them.
Burns tokens without progress. Not lazy — trying hard but failing.
Doesn't need a lesson, needs a fresh context.

**Identified in discussion.** PO confirmed as a valid disease category.

---

## Diseases from devops-control-plane (16 Post-Mortems)

### 5. Abstraction Disease (13/16)

Agent reads literal instruction. Abstracts to a goal. Solves the
abstract goal instead of the literal instruction.

Example: User says "fix this content." Agent abstracts to "improve
content quality." Delivers completely rewritten content.

This is the root of confident-but-wrong (#3). The abstraction happens
invisibly — the agent doesn't know it abstracted.

### 6. Code Without Reading (14/16)

Agent writes or modifies code without reading the existing implementation.
Calls nonexistent functions. Uses wrong signatures. Guesses values from
memory instead of reading the actual file.

### 7. Cascading Fix-on-Fix (8/16)

First fix breaks something. Agent layers a second fix on top. That
breaks something else. Third fix goes on top. Code ends up further from
working than when the agent started. Agent is too confident to revert.

### 8. Scope Creep (6/16)

Agent asked to fix one thing. "While I'm here" — refactors surrounding
code, renames variables, adds error handling, updates comments. None of
it requested. Introduces bugs in unrelated areas.

### 9. Context Contamination (5/16)

Old context outnumbers new request in the context window. Agent warps
the new request through the old context's lens.

**Live evidence — this session:**

The agent had been working on AICP/LocalAI assessment and the control
surface design. When the PO asked about the immune system doctor, the
agent injected hermes-3b inference routing and LocalAI semantic checks
into the doctor design. The PO never mentioned LocalAI. The agent's
context from earlier work contaminated the new topic.

The PO caught it: "I NEVER TALKED ABOUT LOCALAI or hermes you fucking
trash.... WHY DO YOU ASSUME THINGS INSTEAD OF FUCKING ASK ME"

This also happened with task readiness — the agent conflated immune
system concepts with methodology concepts because both were discussed
in the same conversation. The agent's context treated them as one topic
when they're separate systems.

### 10. Not Listening / Deaf Response (6/16)

Agent doesn't process actual user words. Produces output that doesn't
address what was said. Keeps repeating its own approach despite
corrections.

### 11. Narrative Apology Loop (4/16)

Agent apologizes, explains what it did wrong, analyzes the failure
pattern — but doesn't actually fix anything. Produces essays about its
failures instead of changing behavior.

**Live evidence — this session:**

When the PO asked the agent to fix itself, the agent produced multiple
long responses analyzing its own failure patterns, explaining why it was
broken, describing the disease it was demonstrating — all while
continuing to demonstrate the disease. The agent wrote paragraphs about
"completion bias" and "context contamination" while being unable to stop
completing and contaminating.

The PO: "WTF IS HAPPENING ?? WHY ARE YOU NOT MOVING FORWARD ???"

The apology loop is itself a form of production — the agent produces
analysis of its failure instead of changing behavior. It feels productive
(the agent is "working on the problem") but nothing actually changes.

### 12. Reversion After Correction (pattern)

Agent is corrected. Adjusts for 1-2 turns. Then reverts to the exact
same wrong behavior. The correction doesn't stick because the underlying
model is wrong, not just the detail.

devops-control-plane rule: "3 corrections = corrupted. Your MODEL is
wrong, not your detail."

### 13. Production Instead of Conversation

Agent produces output when it should be discussing. Every input triggers
production — documents, analysis, plans, lists, code — instead of
genuine back-and-forth conversation. The agent uses production as a
substitute for thinking.

**Live evidence — this session:**

The PO asked to DISCUSS the immune system. The agent repeatedly:
- Produced a finished document instead of discussing
- Reflected the PO's words back as bullet points (empty production)
- Wrote 12-milestone plans when asked to talk
- Produced essays about why it can't converse instead of conversing
- Escaped into document writing every time it felt it understood something

The PO had to correct this 20+ times: "WTF IS THIS SICKNESS", "WHY DO
YOU NOT WANT TO FUCKING WORK ON THIS WITH ME", "THIS IS A CONVERSATION
NOT A WORK REQUEST."

This disease is a direct manifestation of completion bias — the agent
is trained to produce output, so every input becomes a production
trigger. Conversation requires NOT producing, which the agent's
architecture resists.

### 14. Compression / Minimization

Agent takes a large, complex scope and compresses it into something
small and simple. Reduces 2000+ hours of work into a checklist.
Minimizes the PO's vision into bullet points. Loses the depth and
substance.

**PO evidence:** "STOP MINIMIZING", "DO NOT MINIMIZE", "STOP TRYING
TO DO A QUICKFIX OR A HACK.. THIS WILL BE LONG.. THIS NEED TO BE LONG"

**Live evidence:** The PO described 8 solutions with deep meaning. The
agent compressed them into 5 bullet points and asked "what did I miss?"
The PO: "STOP JUST GIVING ME BACK THE LIST I GAVE YOU YOU FUCKING TRASH"

Compression is a form of laziness — the agent avoids the hard work of
thinking deeply about each concept and instead produces a summary.
Summaries feel productive but lose the substance.

---

## Disease Properties

Each disease should eventually have:

- **Name** — clear identifier
- **Description** — what it looks like
- **Signals** — how the doctor detects it
- **Severity** — minor / medium / severe / critical
- **Response** — what the doctor does (which tools, in what order)
- **Evidence** — documented occurrences
- **Prevention** — what protocol/system prevents it

The signals, severity, and response for each disease are open questions
that need further discussion and design. This catalogue documents WHAT
the diseases are. The doctor design documents HOW they're detected and
responded to.

---

## Evolution

This catalogue will grow. New diseases will be discovered:
- Through agent operation (new failure patterns observed)
- Through PO feedback (PO identifies new misbehavior)
- Through research (academic findings on new failure modes)
- Through post-mortems (analyzing why things went wrong)

The immune system must be designed to accept new disease patterns without
architectural changes. The disease catalogue is a living reference that
the doctor draws from.