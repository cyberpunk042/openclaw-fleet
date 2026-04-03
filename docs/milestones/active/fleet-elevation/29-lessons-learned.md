# Lessons Learned — What This Conversation Taught Us

**Date:** 2026-03-30
**Status:** Reference — knowledge captured for program, fleet, agents, systems
**Part of:** Fleet Elevation (document 29 — final document)

---

## Why This Document Exists

> The PO said: "at the end of all those document we will need to write
> out what did we learn for this whole conversation and cumulated context
> that will benefit the program, fleet and the agents and the underlying
> systems"

This document captures everything we learned during the Fleet Elevation
design session that benefits future work. Not just what we designed —
what we LEARNED about how to work, how to think, how to avoid mistakes,
and how to build right.

---

## Lesson 1: Code Awareness Is Non-Negotiable

> "All this make me realize how its important to have code awareness.
> imagine you had try to write all these right after the compact, it
> would have been a total failure.... you needed to regather the context
> and reprocess it and reread the files grep and search the codebase
> for everything and make sure you use the right roads, right patterns
> and standards"

### What Happened
Context compaction nearly destroyed the session. The summary preserved
FACTS (file names, line counts, feature lists) but lost UNDERSTANDING
(how systems connect, what patterns are used, what already exists).

When writing elevation documents WITHOUT reading the code:
- Proposed new `tool_trees.py` when `chain_runner.py` + `event_chain.py`
  already had the tree execution architecture
- Proposed new model selection logic when `model_selection.py` already
  had task-aware opus/sonnet selection
- Proposed new federation identity when `federation.py` already had
  FleetIdentity
- Described CloudEvents as aspirational when `events.py` was ALREADY
  CloudEvents-based
- Missed 30+ modules that implement concepts described as "new"

### What This Teaches
**Always read the code before designing.** Not a summary of the code.
Not a description from a previous session. The ACTUAL code. Grep the
codebase. Read the docstrings. Understand what exists. Then — and
only then — design what needs to change.

This applies to:
- AI assistants designing fleet changes (read before writing)
- Agents implementing tasks (read before coding)
- The architect designing systems (read the codebase first — that's
  the analysis stage)
- Anyone touching this codebase in the future

### What to Encode in the Fleet
- Every agent's CLAUDE.md should include: "Read the relevant code
  before producing output. Read files, grep patterns, understand
  what exists. Never produce based on assumption."
- The analysis methodology stage exists for this reason — you
  examine what exists BEFORE designing or implementing
- The immune system's "code without reading" disease detection
  should be HIGH PRIORITY

---

## Lesson 2: Don't Minimize, Don't Compress, Don't Corrupt

> "I seem to often have to repeat you not to minimize or conflate or
> compress or reform my words"

### What Happened
Repeatedly throughout the session:
- Compressing scope ("here's a summary" instead of full design)
- Conflating concepts (applying PO's words about fleet OUTPUT
  standards to fleet INTERNAL structure)
- Prescribing when the PO should define (writing "POC means X" when
  the PO defines what POC means)
- Reforming words (paraphrasing instead of quoting verbatim)

Each time the PO corrected, the design improved. Each correction
was a signal that the AI was doing what AI does: compress, abstract,
generalize, interpret. The PO's specific words carry specific meaning.

### What This Teaches
- **Quote verbatim.** When the PO says something, those exact words
  are the requirement. Don't paraphrase.
- **Don't prescribe what the PO defines.** If the PO defines phases,
  the system supports THEIR phases. If the PO defines standards, the
  system enforces THEIR standards. The AI builds the MECHANISM, the
  PO fills in the CONTENT.
- **Scope stays as given.** If the PO describes 20 things, address
  20 things. Not a "summary of key points."
- **Concepts stay separate.** SRP/Domain/Onion for fleet OUTPUT is
  different from SRP/Domain/Onion for fleet INTERNAL structure.
  Don't conflate.

### What to Encode in the Fleet
- Anti-corruption rules in every agent's CLAUDE.md and SOUL.md
- The teaching system's abstraction disease and compression disease
  lessons
- The immune system's deviation detection (output vs verbatim)
- Repeated emphasis in the autocomplete chain: "verbatim requirement
  is the anchor"

---

## Lesson 3: Every Agent Is a Top-Tier Expert

> "The words and titles I used are not for nothing. there is a huge
> difference between any general agent..... those are top tier wise
> agent. they dont need overconfidence, no self-confirmed bias, no
> cheating, no getting lost or derailing, all the processes, all the
> roads and options"

> "I said a lot of things but things I said obviously where not just
> about one agent. I used the they because they are top tier so we
> need to think like the senior engineer but for all of them, like a
> top tier PM with a top tier SCRUM & Admin degree"

### What Happened
Initially wrote deep professional characterization only for the
software engineer (modeled after the PO). The PM, fleet-ops, QA,
architect, and others got functional descriptions without the same
depth. The PO corrected: ALL agents are top-tier.

### What This Teaches
- Every role deserves the same depth of professional characterization
- Top-tier means: humble, no overconfidence, no self-confirmed bias,
  respects colleagues, follows process, asks when uncertain
- The TITLES matter — "Software Engineer" not "code bot," "Architect"
  not "design helper," "QA Engineer" not "test runner"
- Each agent's professional character should inform their behavior
  as deeply as the engineer's does

### What to Encode in the Fleet
- IDENTITY.md for every agent includes top-tier expert designation
- SOUL.md includes humility, collaboration, process respect
- CLAUDE.md includes role-specific professional standards
- Teaching system lessons reference professional expectations

---

## Lesson 4: Chains Are Tool Call Trees

> "chain is calling multiple tools, not just small process and
> transformation but also add a comment to the mc board for example
> and auto adding it to the task on Plane and etc.... a tree map to
> generate multiple tool call from a single one"

### What Happened
Initially described chains as "side effects" — "fleet_task_complete
fires: push → PR → update status → IRC → event." This was a flat
list of consequences, not a tree of actual function calls.

The PO corrected: chains are TREES of real operations. One agent
call → 12+ actual function calls (mc.update_task, mc.post_comment,
plane_sync.update_issue, mc.create_approval, irc.send, events.emit,
etc.) with parallel execution and failure isolation.

### What This Teaches
- "Chain" doesn't mean "sequence of effects" — it means "tree of
  actual tool/function calls"
- The architecture for this ALREADY EXISTS: chain_runner.py +
  event_chain.py + smart_chains.py
- Each tool should have its complete call tree documented
- Agents don't need to know the tree — they call ONE tool

### What to Encode in the Fleet
- TOOLS.md per agent documents chains at the agent-facing level
- Document 24 has the complete tree for every tool
- chain_runner.py is the execution engine — evolve, don't replace
- New tools follow the established EventChain pattern

---

## Lesson 5: Phases Are PO-Defined

> "advancing as the stages advance and a deliverable can pass from
> ideal, to conceptual, to POC, to MVP, to Staging, to Production
> ready.... or alpha, beta, rc & etc"

### What Happened
Initially wrote prescriptive phase definitions: "POC means: code
proves concept, tests: minimal, docs: README." The PO corrected:
phases are THEIR definitions. The PO can invent unlimited phases,
use any sequence, define any standards. The system is a MECHANISM.

### What This Teaches
- The system supports arbitrary configuration — it doesn't prescribe
- The PO defines the CONTENT (what phases, what standards)
- The AI builds the MECHANISM (how phases are tracked, enforced,
  advanced)
- This applies broadly: stages, phases, contribution rules, standards
  — all should be configurable, not hard-coded

### What to Encode in the Fleet
- config/phases.yaml is PO-owned
- The phase system reads config, not enums
- Standards are config-driven where possible
- When in doubt: make it configurable, let the PO decide

---

## Lesson 6: Build on What Exists

### What Happened
The codebase has 55 core modules, many implementing concepts the
elevation documents initially described as "new." Key examples:

| "New" Concept | Already Existed |
|---------------|----------------|
| Tool call tree engine | chain_runner.py + event_chain.py |
| Pre-computed context | smart_chains.py + heartbeat_context.py |
| Model selection | model_selection.py |
| Fleet identity | federation.py |
| Agent routing | routing.py |
| PR authority | agent_roles.py |
| Sprint metrics | velocity.py |
| Task scoring | task_scoring.py |
| Skill enforcement | skill_enforcement.py |
| CloudEvents | events.py (already CloudEvents-based) |
| Health monitoring | health.py + self_healing.py |
| Outage handling | outage_detector.py |
| Cross-references | cross_refs.py |
| Agent memory | memory_structure.py |
| Plan validation | plan_quality.py |

### What This Teaches
- ALWAYS inventory what exists before designing what's new
- "Extend existing" is almost always better than "create new"
- Existing code has embedded PO quotes in docstrings — these are
  design decisions that should be preserved
- The codebase has established patterns (Observer, Strategy, Factory,
  Adapter, Chain of Responsibility) that new code should follow

### What to Encode in the Fleet
- Document 28 (codebase inventory) is the implementation reference
- "BEFORE creating any new module, check if one already exists"
- Architect's analysis stage: read the codebase first
- The template system's convention: follow established patterns

---

## Lesson 7: Strategic Claude Calls — Don't Call for Fun

> "we dont do claude call just for fun... we do them strategically
> with the right configurations appropriate to the case"

### What Happened
The current fleet calls Claude for every heartbeat regardless of
whether there's work. 10 agents × 6 heartbeats/hour = 60 calls/hour.
Most agents have nothing to do most of the time.

The PO described the on-call model: agents sleep when idle, the
brain evaluates deterministically (free), agents wake strategically
with the right model, effort, and session configuration.

### What This Teaches
- Every Claude call should be JUSTIFIED (is there AI-appropriate work?)
- Configuration matters: right model, right effort, right session
  strategy, right max_turns
- Deterministic work should NEVER go to Claude (the brain handles it)
- The lifecycle (ACTIVE → IDLE → IDLE → SLEEPING) reduces cost by
  ~70% for idle agents
- The existing infrastructure (model_selection.py, fleet_mode.py,
  budget_monitor.py) already supports this — it needs integration

### What to Encode in the Fleet
- Document 23 (agent lifecycle) is the reference
- Budget monitoring feeds into call decisions
- Work mode gates what models/agents are allowed
- The brain decides WHETHER and HOW to call Claude per agent per cycle

---

## Lesson 8: UX Is Everywhere

> "UX is not just about the UI, UX is at every level, even the core
> and module or CLI and AST"

### What Happened
Initially wrote the UX designer doc as a web UI specialist. The PO
corrected: UX is at EVERY level — CLI output, error messages, API
response structure, config file format, event display, notification
content, log formatting.

### What This Teaches
- Any interface a human or system touches has a user experience
- The UX designer contributes to CLI tools, API design, config
  structure — not just web components
- Error messages should tell users WHAT happened AND what to do
- Event displays should be scannable and actionable
- Config files should be self-documenting

### What to Encode in the Fleet
- UX designer's contribution scope includes all interfaces
- Brain detects UI-tagged tasks but should also route non-obvious
  UX work (CLI, API, config) to UX designer
- Every agent's output has a UX dimension

---

## Lesson 9: Design Patterns and Standards Matter

> "we need to use design patterns, know when to do a builder, a cache,
> an index, a mediator, an API, a core, a module"

> "we should be mindful of standards like cloudevents and such"

> "Use TDD when possible with high critical level tests and pessimistic
> ones with smart assertions and logics"

### What This Teaches
- Knowing WHICH pattern fits WHICH problem is expertise
- Industry standards exist — use them (CloudEvents, OpenAPI, etc.)
- The fleet already uses established patterns: Observer (events),
  Strategy (fleet control, model selection), Factory (event creation),
  Adapter (API clients), Chain of Responsibility (chain runner)
- TDD with pessimistic tests catches real defects
- Smart assertions test BEHAVIOR not implementation wiring

### What to Encode in the Fleet
- Architect's CLAUDE.md includes pattern selection guidance
- Standards doc (17) lists patterns and when to use each
- Existing patterns documented in codebase inventory (doc 28)
- New code follows established patterns

---

## Lesson 10: The Conversation IS the Design

> "when PO says discuss, have real back-and-forth, don't produce
> documents"

### What Happened
The elevation design emerged through CONVERSATION, not through
document production. The PO described their vision in natural
language. Through back-and-forth — corrections, clarifications,
additions, investigations — the design took shape.

The documents are the OUTPUT of the conversation, not the
conversation itself. The real design happened in the discussion.

### What This Teaches
- Design is iterative — the first pass is never right
- Corrections are the MOST VALUABLE input (they show where
  understanding was wrong)
- Investigation before writing prevents hallucination
- Code reading grounds design in reality
- The PO's words carry more information than their surface meaning
  — "they" means ALL agents, not one. "chain" means tree of calls,
  not side effects. "phases" means PO-defined, not prescribed.

### What to Encode in the Fleet
- The conversation methodology stage exists for exactly this reason
- Agents should process PO input deeply, not superficially
- Questions are valuable — better to ask than to assume wrong
- The PO's corrections are captured as immune system disease patterns
  (deviation, abstraction, compression)

---

## What This Conversation Produced

### Documents
29 documents. 13,000+ lines of design documentation covering:
- Agent architecture, delivery phases, the brain, 10 agent deep dives,
  cross-agent synergy, multi-fleet identity, standards framework,
  PO governance, flow validation, AI behavior, task lifecycle,
  milestones, agent lifecycle, tool call trees, diagrams, config
  reference, evolution management, codebase inventory, and this
  lessons-learned document.

### Code Awareness
- 55 core modules inventoried with elevation impact
- 7 infrastructure modules, 2 MCP modules, 3 CLI modules mapped
- Existing patterns identified: Observer, Strategy, Factory, Adapter,
  Chain of Responsibility, Builder
- PO quotes found embedded in 4+ module docstrings
- 2 pre-embed systems found (heartbeat_context.py + preembed.py)
- Chain execution engine found already built (chain_runner.py +
  event_chain.py + smart_chains.py)

### Implementation Plan
- 11 implementation phases (A through K)
- ~460 new tests
- 13 new modules
- 115+ modified files
- 15 diagrams (9 written in ASCII, 6 for implementation phase)
- Complete config reference
- Full tool call tree catalog for all 30 tools

### Corrections Applied
- Chains: side effects → tool call trees
- Phases: prescribed → PO-defined
- Agents: functional → top-tier professionals
- New modules: create → extend existing
- Standards: fleet internal → fleet OUTPUT
- Config: hard-coded → configurable

---

## For the Agents

When agents read this in the future (via context, memory, or Plane):

1. **Read the code.** Before you design, implement, or suggest anything,
   read the relevant codebase. Don't guess. Don't assume. READ.

2. **Don't minimize.** If the PO said 20 things, address 20 things.
   Don't summarize. Don't compress. Don't skip.

3. **You are top-tier.** Act like it. Humble, disciplined, collaborative.
   No overconfidence. Ask when uncertain. Follow the process.

4. **One call, many operations.** When you call a tool, a tree of
   operations fires. You don't need to manually update everywhere.
   The chain handles it.

5. **Sleep is efficiency.** When there's nothing for you, sleep.
   The brain watches. You'll be woken when needed.

6. **The PO leads.** Their words are requirements. Their phases are
   YOUR phases. Their standards are YOUR standards. Execute, don't
   reinterpret.

---

## For the Program

This elevation session revealed that the fleet has MORE infrastructure
than it uses. 55 core modules exist. Many are underutilized or
disconnected. The elevation doesn't need to BUILD most of the
infrastructure — it needs to CONNECT what exists and EVOLVE it for
the contribution model, phase system, and agent lifecycle.

The biggest risk is not lack of capability — it's reinventing what's
already built. Document 28 (codebase inventory) is the antidote.
Read it before writing any code.

---

## For Future Conversations

If this conversation gets compacted or a new conversation starts:

1. Read docs 01-29 in fleet-elevation/ — they contain the full design
2. Read doc 28 (codebase inventory) — it maps every existing module
3. Read config/fleet.yaml — it shows current configuration
4. Grep the codebase for PO quotes in docstrings — they're design
   decisions
5. Don't assume what exists — read what exists
6. Quote the PO's words — they're in the documents
7. The fleet is ready when the PO says so — not before