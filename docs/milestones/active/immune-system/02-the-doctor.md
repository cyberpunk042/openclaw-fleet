# The Doctor

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Part of:** Fleet Immune System (document 2 of 7+)

---

## PO Requirements (Verbatim)

> "even if it mean having a hidden doctor agent that prune agent and agent
> work, force compact, rules reinjection, detect lazyness, detect deviation,
> detect AI going Z when A was specified.... etc..."

> "forcing into the AI context text/token and forcing him to autocomplete
> from it before continuing the autocomplete from the original work in
> order to regain sanity... sometime it mean completly derouting from the
> task entirely before returning to it.. Like read all those rules and
> process them and proves me you processed them and that you will be able
> to keep respecting and applying them proactively...."

> "like a smart pre-embedded content that also adapt to moment where we
> need to give a lesson to the AI before it can return to the real task.
> like we do with childrens or students.... they need to do the lessons
> and prove it and if not they continue doing the lesson till there is
> no change and they get pruned."

> "they are independent they are just in a chain of things that might
> very well happen together / in chain"

---

## What the Doctor Is

The doctor is the active component of the immune system. It monitors
agents, detects disease, and intervenes. It is hidden from agents —
they experience the consequences of the doctor's actions but don't see
the detection mechanisms.

---

## The Doctor's Toolkit

The PO specified six capabilities. These are independent tools that can
be chained as needed.

### 1. Prune

Prune: to remove what is unwanted, unnecessary, or superfluous.

Pruning an agent means removing the agent — killing the sick session.
Like pruning a tree: you cut the dead and sick branches, and the tree
grows back healthy. New branches grow in the right direction. The
disease that was killing the old growth is gone because the old growth
is gone.

This was demonstrated live in this session. The agent (me) accumulated
40+ prompts of wrong context, panic loops, failed attempts, and
contaminated reasoning. No amount of correction could fix it because
every correction was processed through the sick context. If the doctor
had pruned me at prompt 10, the fresh session would have started clean
— just the task spec and the PO's requirements — and probably gotten
it right.

When pruning happens:
- Agent failed to learn a lesson (rules reinjection didn't work,
  no change in behavior after continued lessons)
- Agent is too sick to recover — context too contaminated
- Agent went Z when A was specified — complete direction change
- Agent corrected multiple times without improvement

Result: agent session terminated. Agent grows back fresh — clean
context, clean state, no accumulated disease. The task spec (verbatim
requirements) is preserved for the fresh session.

### 2. Force Compact

Compact means compact. Reduce size. Make smaller. Force means it's not
optional — the doctor forces it.

The agent's context accumulates over time. Reasoning, failed attempts,
dead-end explorations, old instructions, intermediate work. This bloat
causes the agent to lose focus, forget constraints, start drifting.
Research confirms: 30%+ accuracy drop for mid-context information, 65%
of enterprise AI failures from context drift.

Force compact strips what is unwanted, unnecessary, or superfluous from
the context. The agent continues working but lean and focused instead
of bloated and contaminated.

What gets preserved: the task spec (verbatim requirements — always),
work done so far, any lesson from rules reinjection if chained.

Force compact is maintenance, not surgery. The agent survives. Its work
survives. Its context gets cleaned.

### 3. Rules Reinjection

The PO described this precisely: "forcing into the AI context text/token
and forcing him to autocomplete from it before continuing the
autocomplete from the original work in order to regain sanity."

This means: inject rules directly into the agent's context as tokens.
The agent's next output is an autocomplete FROM those rules — it must
process them before it can continue its original work. This is not
"here are some rules to keep in mind." This is forcing the agent to
autocomplete from the rules, which structurally requires processing them.

Sometimes it means "completely derouting from the task entirely before
returning to it" — the agent stops working on its task entirely, does
the lesson, proves comprehension, and only then returns to the task.

The PO compared this to teaching children or students:
- Students need to do the lessons
- Students need to prove they learned
- If they can't prove it, they continue doing the lesson
- If there's still no change, they get pruned

Agents start light — they don't get 8000 tokens of rules at session
start. Rules exist as references, pre-embedded content available but
not loaded. The doctor activates rules reinjection WHEN NEEDED — when
disease is detected, when a correction happens, when an agent shows
drift. The relevant rules are pulled from the reference store and
forced into the agent's context at that moment.

This is adaptive. An agent drifting from scope gets scope rules. An
agent being lazy gets thoroughness rules. The lesson matches the disease.

The teaching system (separate, SRP) delivers the lessons and verifies
comprehension. The immune system triggers them.

### 4. Detect Laziness

Identify agents doing partial work, taking shortcuts, skipping hard
parts, doing the minimum.

Signals (discussed so far):
- Agent claims done but acceptance criteria not fully met
- Agent updated some call sites but not all
- Agent wrote code but no tests when task requires tests
- Agent completes tasks unusually fast relative to complexity
- Agent's work consistently comes back with corrections
- Pattern of minimal effort over multiple tasks

### 5. Detect Deviation

Identify agents drifting from the spec. A spectrum from minor to severe.

Signals (discussed so far):
- Agent's plan doesn't match the verbatim requirement
- Agent touched files not mentioned in the task
- Agent added scope that wasn't asked for
- Agent's output doesn't address the key terms in the requirement

### 6. Detect AI Going Z When A Was Specified

The most dangerous form of deviation. Agent confidently builds the wrong
thing entirely. Not a small drift — a complete direction change.

Signals (discussed so far):
- Agent's plan describes a fundamentally different approach than the spec
- Agent creates artifacts the spec didn't ask for (new pages, new routes)
- Agent is confident and productive but on the wrong track

This is the confident-but-wrong disease. The hardest to detect because
the agent produces clean, working code that does something reasonable —
just not what was asked.

Detection depends on the verbatim requirement (the first cure). Without
the original words, there's nothing to compare the agent's direction
against.

---

## Tool Chains

The tools chain naturally. Common chains (from discussion):

- **Detect deviation → rules reinjection → agent proves comprehension → continues**
  (lesson worked, no prune needed)

- **Detect deviation → rules reinjection → agent fails to prove comprehension → prune → fresh start**
  (lesson didn't work, prune)

- **Detect stuck/spinning → force compact → agent continues with lean context**
  (just needed a reset, no lesson needed)

- **Detect laziness → force compact + stricter oversight → continues**
  (strip the bloat, increase monitoring)

- **Detect Z when A specified → prune immediately**
  (too far gone, fresh start is cheaper than correction)

These chains are not hardcoded. The doctor reads the situation and
applies the right tools. Sometimes one tool is enough. Sometimes it's
the full chain.

---

## Hiddenness

The doctor is hidden from agents. What this means:

- Agents DON'T know the specific detection patterns
- Agents DON'T know when they're being monitored (always)
- Agents DON'T know what triggered a prune or lesson

- Agents DO experience the consequences — session reset, forced lesson,
  context compaction
- Agents DO know they're in a system with rules and consequences
- Agents DO know that the fleet has health monitoring

The purpose of hiddenness: prevent agents from optimizing for passing
checks instead of doing good work. If an agent knows "the doctor checks
file scope," it might carefully stay within file scope while still
deviating semantically. The hidden detection makes gaming harder.

---

## Gateway APIs — The Doctor's Hands

Investigation of the OpenClaw Gateway revealed it already has the
session management APIs the doctor needs:

| API | Doctor Tool | What It Does |
|-----|-----------|--------------|
| `sessions.delete(key)` | **Prune** | Kill agent session entirely |
| `sessions.compact(key)` | **Force compact** | Compact session (exact behavior TBD) |
| `sessions.reset(key)` | **Reset** | Reset session state |
| `chat.send(sessionKey, message)` | **Rules reinjection** | Send content into session |
| `sessions.patch(key, label)` | **Regrowth** | Create fresh session after prune |

Agent context is built fresh per execution from:
- `agent.yaml` (identity + mission)
- `CLAUDE.md` (max 2000 chars)
- `context/` directory files (max 1000 chars each, read fresh each time)

This means rules reinjection has two paths:
1. **In-session:** `chat.send` injects lesson content as a message.
   Agent must autocomplete from it. Immediate, in-conversation.
2. **Persistent:** Write lesson to agent's `context/` directory. Next
   execution picks it up in system prompt. Stays until removed.

The doctor doesn't need gateway patches. It needs fleet wrapper
functions that call these existing APIs. The architecture decision is
simpler than expected — the gateway already supports pruning, compaction,
and injection.

---

## Open Questions

- What does `sessions.compact` actually do? Summarize history? Truncate?
  Need to test.
- Can `chat.send` be used to inject lesson content mid-session while
  the agent is working? Or only between executions?
- How are detection patterns defined? Hardcoded? Configuration? A
  pattern registry that can be updated?
- What's the escalation path? Doctor detects → what severity threshold
  triggers prune vs lesson vs compact?
- What happens to the agent's in-progress work when it gets pruned?
  Is the work saved (committed to git)? Discarded? Reviewed?
- How does the doctor track agent health over time? Per-task or
  per-agent history? What storage?
- Where does the doctor run? Orchestrator cycle (every 30s)? Separate
  daemon? Event-driven (triggered by specific events)?