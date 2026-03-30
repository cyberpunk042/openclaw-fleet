# Teaching System — Overview

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Scope:** How agents learn, how lessons are delivered, how comprehension
is verified. Separate from the immune system (SRP).

---

## PO Requirements (Verbatim)

> "rules reinjection... forcing into the AI context text/token and forcing
> him to autocomplete from it before continuing the autocomplete from the
> original work in order to regain sanity..."

> "sometime it mean completly derouting from the task entirely before
> returning to it.. Like read all those rules and process them and proves
> me you processed them and that you will be able to keep respecting and
> applying them proactively.... stuff like that..."

> "it not like we normally give a 8000 weight based context when we start
> a new agent, we want him to work light. but we need a minimum and we need
> to be able to Force him to read things that are only there as ref in his
> memory when its needed."

> "like a smart pre-embedded content that also adapt to moment where we
> need to give a lesson to the AI before it can return to the real task.
> like we do with childrens or students.... they need to do the lessons
> and prove it and if not they continue doing the lesson till there is
> no change and they get pruned."

---

## What the Teaching System Is

The teaching system adapts and responds. When the immune system triggers
it, the teaching system takes over — creates adapted lessons, delivers
them, verifies comprehension through practice.

The key insight from the PO: **seeing the pattern does not break the
pattern. It's forging the right path multiple times that does.** That's
why the teaching system creates adapted lessons with a smart format.
Not "here are the rules, acknowledge them." Not "do you understand?"
The agent must PRACTICE the right path. Multiple times. Until the right
path is forged.

It is separate from the immune system. The immune system observes,
reports, and acts — it detects disease and triggers the teaching system.
The teaching system adapts and responds — it delivers the lesson and
verifies through practice. Separation of responsibility.

---

## How Teaching Works (From PO Description)

1. **The agent is pulled out of its task.** Not a background injection.
   The agent stops working and enters learning mode.

2. **Rules/content are forced into the agent's context.** Text and tokens
   injected that the agent must autocomplete from. This forces the agent
   to process the content before continuing its original work.

3. **The agent must PROVE it processed the rules.** Not just "I understand."
   Demonstrated comprehension. The specific mechanism of proof needs
   design, but the principle is clear — acknowledgment is not enough.

4. **If comprehension is proved, the agent returns to work.** It can
   continue its task with the lesson internalized.

5. **If comprehension is NOT proved, the lesson continues.** The agent
   keeps doing the lesson until there's no change in behavior.

6. **If there's no change, the agent gets pruned.** The immune system
   takes over — kill the session, agent grows back fresh.

---

## Agents Start Light

Agents don't get loaded with 8000 tokens of rules at the start of every
session. They work light. Rules exist as references — pre-embedded
content available but not loaded.

The teaching system activates WHEN NEEDED. When the immune system
detects disease, when a correction happens, when an agent shows drift.
The relevant rules are pulled from the reference store and injected into
the agent's context at that moment.

This is adaptive — not every agent gets every rule every time. The rules
injected match the disease detected. An agent drifting from scope gets
scope rules. An agent being lazy gets thoroughness rules. An agent
hallucinating gets verification rules.

---

## The Student-Teacher Dynamic

The PO compared this to teaching children or students:
- Students need to do the lessons
- Students need to prove they learned
- If they can't prove it, they keep doing the lesson
- If there's no change, they get held back (pruned)

This is the same dynamic. The agent is the student. The teaching system
is the teacher. The immune system is the school administration that
decides when a student needs remedial education and when they need to
be held back entirely.

---

## Adapted Lessons — Not Generic Rules

> "seen the pattern does not break the pattern, it forging the right path
> multiple time that does. that's why you create adapted lessons. with a
> smart format."

The teaching system does NOT give generic lessons. "Follow the protocol"
is useless. The lesson must be adapted to:

- **The specific disease** — what did this agent do wrong?
- **The specific task** — what should the agent have done instead?
- **The specific agent** — has this agent shown this pattern before?

And the format must be smart — it must force the agent to practice the
right path, not just read about it. Reading "don't deviate from the
spec" doesn't forge the path. Practicing "re-read the verbatim
requirement, now produce a plan that matches it, now show me how your
plan addresses each word in the requirement" — that forges the path.

Multiple attempts. The agent practices until the right path is forged.
If there's no change — if the agent keeps failing the practice — it
gets pruned. The teaching system did its job. The agent couldn't learn.

---

## Adapted Lessons by Disease — What They Look Like

### For Deviation (agent drifted from spec)

The agent added sidebar navigation when the spec said header bar.
The lesson must make the agent practice READING THE SPEC AND MAPPING
OUTPUT TO IT.

Lesson injection:
"Your task's verbatim requirement says: 'Add three Select dropdowns to
the DashboardShell header bar, center section after OrgSwitcher.'
Your plan says: 'Create a new /fleet-control page in the sidebar.'

Exercise: Re-read the verbatim requirement word by word. For each
specific term (header bar, center section, after OrgSwitcher), state
which file and which line of code that maps to. Then produce a new
plan that addresses each term."

The agent must demonstrate it can connect words to code locations.
This forges the path: requirement → specific code → plan that matches.

### For Laziness (agent did partial work)

The agent updated 3 of 7 call sites and claimed done. The lesson
must make the agent practice THOROUGHNESS.

Lesson injection:
"Your task says 'update all call sites for function X.' You updated
3 files. Grep shows 7 files contain calls to X.

Exercise: List ALL 7 files that call function X. For each file, state
the line number of the call and what change is needed. Then confirm:
does your work address all 7?"

The agent must demonstrate it can find ALL instances, not just the
obvious ones. This forges the path: search exhaustively → verify
completeness → then claim done.

### For Confident-but-wrong (agent built Z when A was specified)

The agent was sure it understood but its understanding was fundamentally
wrong. The lesson must break the false confidence and rebuild from
the actual words.

Lesson injection:
"You were building: [what the agent built].
The requirement says: [verbatim requirement].
These are different things.

Exercise: Without referencing your previous plan, read ONLY the
verbatim requirement. Write a single sentence stating what is being
asked. Do not add interpretation. Use only words that appear in the
requirement."

The agent must demonstrate it can read without interpreting. This
forges the path: read literally → state literally → then plan.

### For Protocol Violation (agent produced code during conversation)

The agent started writing code when it should have been discussing.
The lesson must make the agent practice STAYING IN PROTOCOL.

Lesson injection:
"Your task is in conversation stage (task_stage = conversation).
During conversation, you should be discussing with the PO, not
producing code. You committed 3 files.

Exercise: State what stage your task is in. State what the protocol
for that stage allows. State what you did that violated the protocol.
Describe what you should have done instead."

The agent must demonstrate awareness of which protocol it's in and
what's allowed. This forges the path: check stage → check protocol →
act within protocol.

### For Stuck/Spinning

Stuck agents don't need lessons — they need force compact. The teaching
system is not involved. The immune system handles this directly with
context reduction.

## Relationship to Other Systems

| System | Role |
|--------|------|
| **Immune System** | Observes, reports, acts. Detects disease, triggers teaching, prunes if teaching fails |
| **Teaching System** | Adapts and responds. Creates adapted lessons, forges the right path through practice |
| **Methodology System** | Defines stages, protocols, checks. The "curriculum" — what agents should be doing at each stage |

The chain: methodology defines what SHOULD happen → immune system
catches what SHOULDN'T happen → teaching system corrects through
adapted practice.

---

## What the Teaching System Needs (To Be Designed)

- **A rule/lesson store** — where rules live as references, organized
  by disease category, retrievable on demand
- **An injection mechanism** — how rules get forced into agent context
- **A comprehension verification mechanism** — how agents prove they
  processed the rules (not just acknowledged)
- **A tracking mechanism** — which agents got which lessons, when, and
  whether comprehension was verified
- **Lesson content** — the actual rules and lessons, drawn from the
  devops-control-plane catalogue and fleet-specific needs
- **Adaptation logic** — which lessons match which diseases

---

## Open Questions

- How does comprehension verification work concretely? What does "prove
  you processed the rules" look like?
- How are lessons stored? Markdown files? Config? Database?
- How does the injection mechanism work technically?
- Can the PO create new lessons? Or only the system?
- How does the teaching system track lesson history per agent?
- What's the threshold for "no change" that triggers pruning?
- How long does a lesson session take? Is there a time limit?
- Can multiple lessons be delivered simultaneously?