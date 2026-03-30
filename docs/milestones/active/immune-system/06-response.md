# Response — What Happens When Disease Is Found

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Part of:** Fleet Immune System (document 6 of 7)

---

## PO Requirements (Verbatim)

> "hidden doctor agent that prune agent and agent work, force compact,
> rules reinjection"

> "we need a way to instaure a DICTATURE with very strict guideline and
> removing any TRASH"

---

## What Response Is

When the doctor detects disease, it responds. The response uses the
doctor's toolkit — prune, force compact, rules reinjection. These tools
are independent but chain naturally based on the situation.

---

## The Doctor's Response Tools

### Prune
Remove the agent. Kill the sick session. Agent grows back fresh.
Used when the agent is too sick to recover.

### Force Compact
Reduce the agent's context. Strip what is unwanted, unnecessary, or
superfluous. Agent continues with lean, focused context.
Used when the agent is drifting but recoverable.

### Rules Reinjection
Pull the agent out of its task. Force it to read and process rules.
Agent must prove comprehension before returning to work. If it can't
prove it learned, and there's no change, it gets pruned.
The teaching system delivers the lessons; the immune system triggers them.

---

## Tool Chains

The tools chain based on the situation. From discussion with PO:

> "they are independent they are just in a chain of things that might
> very well happen together / in chain"

Example chains discussed:
- Detect → rules reinjection → comprehension proved → agent continues
- Detect → rules reinjection → no change → prune → fresh start
- Detect stuck → force compact → agent continues with lean context
- Detect → force compact + rules reinjection (in either order)

The doctor reads the situation and chains the right tools. Sometimes
one tool is enough. Sometimes the full chain ending in prune.

---

## Disease-Response Mapping

From discussion with PO, different diseases have different natural
responses. The four primary disease categories identified:

### Deviation → Lesson
Agent is drifting from spec. Deviation is a spectrum — minor drift gets
a nudge, medium drift gets a lesson (rules reinjection). The lesson
forces the agent to re-read the verbatim requirement, process it, prove
it understands. If the lesson works, agent continues. If not, escalate
to prune.

### Laziness → Stricter oversight
Agent is taking shortcuts. Force compact to strip the bloated context
that might be causing loss of focus. Increase monitoring — more frequent
checks, harder acceptance criteria, faster escalation. The agent isn't
sick in the same way as deviation — it's not going the wrong direction,
it's just not going far enough.

### Confident-but-wrong → Verbatim comparison, then prune
Agent is confidently building the wrong thing. This is the hardest to
recover from because the agent's entire mental model is wrong, not just
a detail. Compare output against verbatim requirements to confirm the
mismatch. Rules reinjection (lesson on the verbatim requirement) may
work if the misunderstanding is shallow. If the agent's model is
fundamentally wrong, prune — the fresh start is cheaper than trying to
reorient a deeply confused agent.

### Stuck/spinning → Force compact
Agent is going in circles. Not sick — trying hard but failing. The
context is full of dead-end reasoning that's weighing the agent down.
Force compact strips the dead ends. Agent continues with lean context
and a fresh perspective. Like sleeping on a hard problem — you come
back and see it clearly. No lesson needed, just cleanup.

### Escalation

If the first response doesn't work, escalate:
- Lesson → lesson again → no change → prune
- Force compact → still stuck → prune
- Prune → fresh agent still fails → flag for PO attention

The threshold for "no change" needs design. The devops-control-plane
uses 3 corrections as the corruption signal. The fleet may use a
similar threshold.

---

## The Dictatorship Principle

> "DICTATURE with very strict guideline and removing any TRASH"

Responses are not advisory. Not suggestions. Not flags for someone
to review later. The doctor acts. Trash gets removed. Sick agents get
pruned. This is structural enforcement, not guidelines.

---

## Escalation Logic — When to Lesson vs Compact vs Prune

The doctor must decide which tool to use. Wrong choice wastes time
(lesson when prune was needed) or wastes progress (prune when compact
would have been enough).

### Decision Factors

| Factor | Favors Lesson | Favors Compact | Favors Prune |
|--------|--------------|----------------|--------------|
| **Severity** | Minor-medium deviation | Bloated context, drift starting | Severe deviation, Z-when-A |
| **History** | First occurrence of this disease | Agent working long without reset | Repeated same disease |
| **Recoverability** | Agent's work is partially correct | Agent is struggling, not misbehaving | Agent's entire direction is wrong |
| **Work investment** | Significant good work to preserve | Good work exists, just needs focus | Work is wrong, saving it causes more harm |
| **Correction count** | 0-1 corrections on this task | N/A | 3+ corrections (devops-control-plane threshold) |
| **Time pressure** | Low priority task, time to teach | Agent needs to unblock quickly | Urgent task, can't afford more wrong work |

### Decision Flow

```
Disease detected
  ↓
Is this the 3rd+ correction on this task for this agent?
  ├── YES → PRUNE (model is wrong, not just detail)
  └── NO ↓
Is the agent's entire direction wrong? (Z when A)
  ├── YES → Can it be corrected with one lesson?
  │     ├── Maybe (shallow misunderstanding) → LESSON first
  │     └── No (fundamental wrong model) → PRUNE
  └── NO ↓
Is the agent stuck/spinning (no progress, high token burn)?
  ├── YES → FORCE COMPACT (not sick, just overloaded)
  └── NO ↓
Is the agent deviating or lazy?
  ├── Deviating → LESSON (teach correct path)
  ├── Lazy → FORCE COMPACT + increase monitoring
  └── Protocol violation → LESSON (teach correct protocol)
```

### After Each Response

- After LESSON: monitor next output. Did the agent demonstrate
  comprehension? Did behavior change? If not after 3 attempts → PRUNE.
- After FORCE COMPACT: monitor next output. Is the agent making
  progress now? If still stuck → PRUNE.
- After PRUNE: fresh session gets the task. If the FRESH agent also
  fails → the TASK might be the problem, not the agent. Flag for PO.

---

## What Happens to Work When an Agent Is Pruned

The agent's session is killed. But its work artifacts may survive:

**What survives pruning (in git):**
- Committed code — it's in git on the agent's branch
- Created branches — they persist
- PRs — if submitted, they persist on GitHub

**What is lost:**
- Uncommitted work — anything not committed is gone
- In-session reasoning — the agent's thought process, plans, context
- Draft documents not yet saved — gone with the session

**What happens to surviving work:**
- If the work was partially good and partially bad: the fresh agent
  (or a different agent) can review the branch, keep what's good,
  discard or fix what's bad.
- If the work was entirely wrong direction: the branch may be abandoned.
  A new branch starts from main.
- If the agent was pruned for laziness (partial work): the fresh agent
  picks up where the committed work left off and completes it.

The task's verbatim requirement is preserved regardless — it lives in
the custom field, not in the agent's session. The fresh agent starts
with the same requirement the pruned agent had.

---

## Response Communication

Every response emits events and notifications:

| Response | Event Type | IRC | ntfy | Board Memory |
|----------|-----------|-----|------|-------------|
| Lesson triggered | `fleet.immune.teaching_triggered` | Yes — #fleet | No (unless repeated) | Yes — tagged |
| Force compact | `fleet.immune.context_compacted` | Yes — #fleet | No | Yes — tagged |
| Prune | `fleet.immune.agent_pruned` | Yes — #fleet + #alerts | Yes — PO notified | Yes — tagged |
| Escalation to PO | `fleet.immune.escalated_to_po` | Yes — #alerts | Yes — urgent | Yes — tagged |

Prune always notifies the PO. Lessons and compactions are visible in
the event stream but don't push-notify unless they escalate.

---

## PO Override

The PO is always in control. The PO can:
- Override a prune decision ("don't prune this agent, I'll talk to it")
- Override a lesson ("skip the lesson, just compact")
- Direct a prune ("prune this agent now")
- Direct a lesson ("give this agent the scope rules")
- Decrease an agent's readiness (forcing it back to earlier protocol)
- Reassign a task from a sick agent to a different one

The PO's directives take precedence over the doctor's automated
decisions. The doctor is a tool. The PO is the authority.

---

## Open Questions

- What exact severity thresholds trigger which responses? The decision
  flow above is a starting framework — it needs tuning with real data.
- How fast does response happen? Within the same orchestrator cycle
  (30s) or on the next cycle?
- How does the doctor track correction count? Through approval history?
  Through a dedicated counter custom field?
- Should the doctor have a "confidence" score for its detections?
  High-confidence → act immediately. Low-confidence → flag for PO
  instead of acting.
- What's the cool-down period after a prune? Should the fresh agent
  get extra monitoring for its first few cycles?