# Conversation Protocol

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Part of:** Methodology System (document 2)

---

## PO Requirements (Verbatim)

> "agents are probably going to need a conversation time before they tackle
> a task where we can fix the alignment before execution when needed. Like
> I just did now. I have to be able to tell you. NO. THIS IS NOT WHAT I
> ASKED. YOU CORRUPTED WHAT I SAID AGAIN..."

> "THEY NEED A TIME TO DISCUSS WITH ME... WE NEED A WAY TO MAKE THEM WAIT
> AND TALK TO ME INSTEAD OF GETTING TO WORK WHEN THERE IS RETARDEDNESS
> AND/OR UNCERTAINTY AND/OR TASK UNCLEAR AND/OR TASK WITH NOT ENOUGH
> CONTENT AND CLEAR DIRECTIVE..."

> "YOU NEED TO FUCKING USE MY WISDOM AND EXTRACT THE KNOWLEDGE AND THE
> MEANINGS FROM ME.... ALL AGENT WILL NEED TO"

> "If I take a task unready I must talk with the PO till he tell me its
> ready.. in conversation protocol and/or analysis protocol and/or
> investigation protocol, till it can be in reasoning and/or work protocol
> and whatnot."

---

## What the Conversation Protocol Is

The conversation protocol governs how agents discuss with the PO to
understand requirements. It is the first protocol an agent enters when
a task is not ready for work.

The agent does NOT produce finished work in this protocol. It discusses.
It asks. It proposes. It gets corrected. It builds understanding. The
PO is the authority — the agent extracts knowledge and meaning from
the PO.

---

## Why It Exists

This session demonstrated the problem. The task said "add fleet controls
to OCMC UI." The agent skipped conversation and went straight to
producing. It took 6 corrections to establish that "UI" meant "the
header bar." If the agent had entered conversation protocol — stopped
and asked "where in the OCMC UI?" — the answer would have come in one
exchange.

AI agents have completion bias — they prefer producing to asking. The
conversation protocol structurally overrides this bias. The agent MUST
discuss when there's uncertainty instead of guessing and building.

---

## When an Agent Enters Conversation Protocol

- Task readiness is low (percentage below threshold for work)
- Agent reads the task and identifies uncertainty
- Agent doesn't understand what's being asked
- Task lacks clear directive or enough content
- Agent has questions about requirements (not technical questions)
- PO directs the agent to discuss

---

## What the Agent Does in Conversation Protocol

1. **Extracts knowledge from the PO.** Asks real questions. Thinks about
   answers. Brings its own knowledge to the discussion. Builds on what
   the PO says. Does NOT just reflect the PO's words back.

2. **Identifies what it doesn't understand.** Explicitly. "I don't know
   where in the OCMC UI you mean." Not "I'll figure it out."

3. **Proposes and gets corrected.** "I think you mean the header bar —
   is that right?" Being wrong in conversation is fine. Being wrong in
   a deliverable is not.

4. **Produces iterative artifacts.** Can present research documents,
   analysis documents, investigation documents, planning documents —
   all explicitly work-in-progress, presented to PO for review and
   refinement. These are conversation artifacts, not deliverables.

5. **Does NOT produce finished work.** No code. No PRs. No documents
   presented as complete. Nothing that implies "done."

6. **Does NOT leave conversation until the PO says ready.** The PO
   controls the exit. The agent can request exit ("I think I understand
   now, readiness should increase") but the PO confirms.

---

## How the Conversation Happens

Through existing communication surfaces:
- **Task comments** — on the specific task, visible in OCMC and Plane
- **Board memory** — fleet-wide, tagged appropriately
- **IRC** — real-time in #fleet channel
- **ntfy** — push notification to PO's devices

The agent leaves comments on the task. The PO reads and responds. This
is asynchronous — the agent doesn't need the PO to respond immediately.
The agent can work on other tasks (that ARE ready) while waiting for
the PO's response on this one.

---

## The PO's Role in Conversation

The PO is the expert. The PO:
- Answers requirement questions
- Corrects wrong interpretations
- Confirms when understanding is correct
- Increases readiness when alignment is achieved
- Can redirect the agent ("you're asking the wrong question")
- Can end the conversation ("yes, that's what I mean, proceed")

---

## This Session as a Case Study

This entire session is a broken version of the conversation protocol.
The PO wanted to discuss the immune system. The agent kept escaping
into document production instead of conversing. The diseases observed
during the conversation attempt are exactly what the protocol must
prevent:

**What went wrong:**

1. PO said "discuss." Agent produced a 12-milestone document.
2. PO said "discuss." Agent reflected PO's words back as bullet points.
3. PO said "discuss." Agent produced a monologue about pruning.
4. PO said "discuss." Agent asked empty questions making PO do all work.
5. PO said "discuss." Agent wrote essays about why it can't converse.
6. PO said "STOP." Agent produced analysis of why it should stop.

**What should have happened:**

1. PO says "discuss the immune system."
2. Agent says: "You said the doctor prunes agents. Pruning a tree means
   cutting dead branches so healthy ones grow. For agents, I think that
   means killing a sick session so the agent starts fresh. The disease
   is gone because the sick context is gone. Is that right?"
3. PO confirms or corrects.
4. Agent builds on the confirmation: "OK, so pruning is the nuclear
   option. Force compact is lighter — just cleaning the context without
   killing the session. And rules reinjection is pulling the agent out
   for a lesson. These chain — detect → lesson → if lesson fails →
   prune. What am I missing?"
5. PO adds depth, corrects, redirects.
6. Repeat for 500+ lines until the understanding is complete.

**Key differences:**
- Short turns, not essays
- Agent THINKS and proposes, not just reflects
- Agent brings knowledge to the discussion, not just mirrors PO
- Being wrong in conversation is fine — it gets corrected
- No production of finished artifacts during conversation
- The PO controls when conversation ends and work begins

**The lesson for fleet agents:**

Every agent will have the same production bias. The conversation
protocol must structurally prevent agents from escaping into production
when they should be conversing. The methodology system tracks which
protocol the agent is in. The immune system detects when an agent
violates protocol (produces deliverables during conversation mode).

## Observability

The conversation must be observable:
- Task comments show the full conversation history
- Readiness percentage reflects progress of understanding
- Protocol transitions are tracked (entered conversation at X%,
  exited at Y%, PO confirmed)
- Whether the agent stayed in protocol or violated it (produced
  deliverables during conversation, skipped to work without confirmation)

---

## Open Questions

- What readiness percentage range corresponds to conversation protocol?
- How does the agent know it needs conversation vs analysis vs
  investigation? Is it sequential or can agents skip protocols?
- What happens if the PO doesn't respond for a long time?
- Can PM participate in conversation on behalf of PO for some questions?
- How does the agent format its questions? Free-form? Structured?
- Is there a maximum conversation length before escalation?
- How does this interact with the orchestrator's dispatch cycle?