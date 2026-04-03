# Agent Intelligence — Autonomy, Escalation, Research, Context Awareness

> **Cross-cutting specification. NOT a single module — touches lifecycle,
> orchestrator, context, router, budget, MCP tools, agent files.**
>
> This document covers the INTELLIGENCE layer that makes agents smart,
> adaptive, and responsive. How agents tune their own autonomy. How
> effort/model/source escalates dynamically. How agents research online
> and in code. How agents manage their own context strategically.
> These are the behaviors that make agents top-tier experts, not
> generic task executors.

### PO Requirements (Verbatim)

> "fine tune the timing for the sleep and offline and silent heartbeat
> and all the reasoning and real logical settings for a proficient
> autonomous fleet. that do not waste breath and yet is very responsive
> and prompt to work."

> "very strategical in context switching and mindful of the current
> context size relative to the next forced compact that require adapting
> preparing and potentially even triggering it ourself before rechaining
> to regather the context to continue working"

> "a logic of escalation of effort and model and source that is also
> necessary also adaptive based on the settings."

> "make sure that AI agents do series of research onlines. And then
> also research in the code. the repo docs of it and the modules /
> codes docs."

> "we need to be smart and fine tune the brain we know that a lot
> does not require agent."

---

## 1. Agent Autonomy Tuning

### 1.1 Current State (What Exists)

Agent lifecycle (docs/systems/06) defines 5 states with thresholds:
```
ACTIVE (working) → IDLE (10min) → IDLE (2 HEARTBEAT_OK) →
SLEEPING (3 HEARTBEAT_OK) → OFFLINE (4h)
```

Heartbeat intervals: ACTIVE=0, IDLE=30min, IDLE=60min, SLEEPING=2h.

### 1.2 What's Missing — The Tuning Layer

The thresholds are HARDCODED. A proficient fleet needs ADAPTIVE tuning:

```
CURRENT: Every agent, same thresholds
  IDLE_AFTER = 10 * 60      (10 min, hardcoded)
  SLEEPING_AFTER = 30 * 60  (30 min, hardcoded)

NEEDED: Per-agent, per-role, adaptive thresholds
  PM: faster wake (tasks queue up), slower sleep (always monitoring)
    idle_after: 5 min, idle_ok: 1, sleeping_ok: 2
  fleet-ops: moderate (reviews come in bursts)
    idle_after: 10 min, idle_ok: 2, sleeping_ok: 3
  workers: slower wake (work is dispatched), faster sleep (idle is expensive)
    idle_after: 15 min, idle_ok: 2, sleeping_ok: 3
  devsecops: fast wake on security events, slow sleep otherwise
    idle_after: 10 min, idle_ok: 3, sleeping_ok: 4
    wake_on: ["security_alert", "pr_ready_for_review"]
```

### 1.3 Configuration Spec

```yaml
# config/agent-autonomy.yaml
defaults:
  idle_after_seconds: 600
  idle_after_heartbeat_ok: 2
  sleeping_after_heartbeat_ok: 3
  offline_after_seconds: 14400

overrides:
  project-manager:
    idle_after_seconds: 300      # faster to notice work
    idle_after_heartbeat_ok: 1 # goes idle quickly when idle
    wake_triggers:
      - unassigned_inbox          # always wake for this
      - po_directive              # PO commands are urgent
      
  fleet-ops:
    wake_triggers:
      - pending_approval          # reviews are core job
      - security_alert            # security is urgent
      - storm_warning             # storm needs attention

  devsecops-expert:
    wake_triggers:
      - security_alert            # immediate
      - pr_created                # review every PR
    sleeping_after_heartbeat_ok: 4  # stays aware longer

  workers:  # software-engineer, devops, qa, writer, ux
    idle_after_seconds: 900       # 15 min — work is dispatched to them
    sleeping_after_heartbeat_ok: 3
```

### 1.4 Silent Heartbeat Protocol

The PO said: "do not waste breath." A sleeping agent should cost ZERO:

```
Agent is SLEEPING:
  ↓
Brain evaluates deterministically (Python, no Claude call):
  ├── Has pre-embed data hash changed since last heartbeat?
  │   YES → data changed, something might need attention → WAKE
  │   NO → nothing new
  │
  ├── New task assigned to this agent?
  │   YES → WAKE immediately
  │
  ├── @mention in board memory?
  │   YES → WAKE
  │
  ├── PO directive targeting this agent?
  │   YES → WAKE immediately
  │
  ├── Role-specific trigger? (from config)
  │   PM: unassigned_inbox → WAKE
  │   fleet-ops: pending_approval → WAKE
  │   devsecops: security_alert → WAKE
  │
  └── None of the above → SKIP (zero cost)
      Agent stays sleeping. No Claude call. $0.

Cost: 10 agents, 7 sleeping = 70% reduction on idle fleet.
```

This is fleet-elevation/23 — the data structures exist in
agent_lifecycle.py (consecutive_heartbeat_ok, last_heartbeat_data_hash)
but the brain evaluation logic is NOT in the orchestrator.

---

## 2. Escalation Logic

### 2.1 What Escalation Means

Not just "ask a human." Escalation is ADAPTIVE — the system adjusts
effort level, model tier, and backend source based on task complexity,
agent confidence, budget pressure, and outcome history.

```
ESCALATION DIMENSIONS:

  Effort:   low → medium → high → max
  Model:    hermes-3b → sonnet → opus
  Backend:  localai → openrouter → claude
  Session:  compact → continue → fresh → plan mode
  Turns:    5 → 10 → 15 → 25 → 30

These scale INDEPENDENTLY based on signals.
```

### 2.2 Escalation Triggers

```
Task complexity signals:
  SP ≥ 8                    → opus, high effort
  SP ≥ 5                    → sonnet, high effort
  SP < 5                    → sonnet, medium effort
  SP = 1, simple subtask    → hermes-3b (localai), low effort

Agent confidence signals:
  confidence_tier = expert  → can use lower effort (work is reliable)
  confidence_tier = trainee → MUST use higher effort (work needs quality)
  correction_count ≥ 2      → escalate to opus (model might be wrong)
  
Outcome signals:
  task rejected by fleet-ops → escalate effort on retry
  challenge failed           → escalate model tier on re-attempt
  3 corrections             → prune (not escalate — model is fundamentally wrong)
  
Context signals:
  context at 70%+           → compact before next heavy work
  context at 90%+           → extract artifacts to memory, prepare for compact
  agent in IDLE           → if waking, use compact session (not fresh)
```

### 2.3 Strategic Claude Call Decisions

Model and effort are selected by `model_selection.py` based on task
complexity (SP) and agent role. Session strategy depends on context
state, not lifecycle state. Turn counts are TBD — need PO definition
or live testing data.

Key decisions:
- Sleeping + nothing new → NO CALL (brain handles silently)
- Task assigned → model by complexity (model_selection.py)
- Budget 90%+ → pause dispatch (budget_monitor.py)
- Context bloated → compact before next work (session management)

### 2.4 Implementation Location

Escalation logic belongs in the orchestrator's dispatch decision:

Model selection is in `model_selection.py` — selects opus/sonnet by
task complexity and agent role. Budget mode (tempo) does NOT control
model selection. Backend selection is in `fleet_mode.py` (backend_mode).

```python
# model_selection.py — already implemented
select_model_for_task(task, agent_name)
# Returns ModelConfig(model, effort, reason) based on SP + task type + role
```

---

## 3. Agent Research Capabilities

### 3.1 Online Research

Agents need to research online: frameworks, libraries, CVEs, patterns,
standards. This is NOT just browsing — it's structured investigation
as part of methodology stages.

```
INVESTIGATION stage:
  Agent reads stage instructions:
    "Research solutions, explore options, examine prior art"
  
  Agent has access to:
    ├── WebSearch (Claude built-in) → find relevant resources
    ├── WebFetch (Claude built-in) → read specific URLs
    ├── Context7 plugin → up-to-date library docs
    └── MCP servers → specialized searches (GitHub, npm, PyPI)
  
  Agent produces investigation_document artifact:
    ├── Sources cited
    ├── Multiple options with tradeoffs
    ├── Recommendations with evidence
    └── Links to reference material
```

**Per-agent research tools:**

| Agent | Research Tools | What They Research |
|-------|---------------|-------------------|
| architect | WebSearch, Context7, GitHub MCP | Frameworks, patterns, libraries, architectural approaches |
| devsecops | WebSearch, CVE databases | Vulnerabilities, security patterns, compliance standards |
| software-engineer | WebSearch, Context7, npm/PyPI | Libraries, APIs, implementation patterns |
| devops | WebSearch, Docker Hub | Infrastructure tools, deployment patterns, container images |
| qa-engineer | WebSearch | Testing frameworks, coverage tools, test patterns |
| technical-writer | WebSearch | Documentation standards, API doc generators |
| ux-designer | WebSearch | Accessibility standards (WCAG), component libraries, interaction patterns |

**Configuration:** Per-agent `allowed-tools` in SKILL.md or CLAUDE.md
determines which research tools each agent can use and WHEN (investigation
stage primarily, analysis stage for codebase research).

### 3.2 Code/Docs Research

Agents need to research IN the codebase: understand existing code,
read module documentation, find patterns, trace dependencies.

```
ANALYSIS stage:
  Agent reads stage instructions:
    "Read and examine the codebase, existing implementation"
  
  Agent has access to:
    ├── Read tool (Claude built-in) → read specific files
    ├── Grep tool (Claude built-in) → search code patterns
    ├── Glob tool (Claude built-in) → find files by pattern
    ├── Filesystem MCP → structured file operations
    └── Agent tool (Claude built-in) → spawn Explore subagent for deep search
  
  Agent produces analysis_document artifact:
    ├── Scope (what was examined, what was excluded)
    ├── Current state (specific files, line numbers)
    ├── Findings (concrete observations)
    ├── Implications (what this means for the task)
    └── Open questions
```

**The system docs we created ARE part of this:**

When an agent needs to understand the storm system, they can read
`docs/systems/11-storm.md`. When they need to understand how
events propagate, they read `docs/INTEGRATION.md` Flow 7. This is
why we wrote 9,491 lines of system documentation — so agents can
research the fleet's own code and architecture.

**The ARCHITECTURE.md and INTEGRATION.md are agent research resources.**

### 3.3 Knowledge Persistence (RAG Integration)

Research findings should persist and be reusable:

```
Agent researches "best React select component for accessibility"
  ↓
Finds: Radix Select, headless, ARIA-compliant, fleet already uses Radix
  ↓
This finding should:
  1. Appear in investigation_document artifact (immediate)
  2. Be posted to board memory tagged [architecture, decision] (team knowledge)
  3. Be ingested into RAG knowledge base (persistent, searchable)
  4. Be available to OTHER agents on future tasks
  
Future task: "Add another dropdown to the UI"
  ↓
Agent context includes RAG result:
  "Previous decision: Use Radix Select for all dropdowns (architect, 2026-04-01)"
  ↓
Agent follows existing decision instead of re-researching
```

**RAG pipeline (exists in AICP, needs fleet connection):**
```
Research finding → ingest into kb.py
  → chunk via chunking.py
  → embed via LocalAI /v1/embeddings (nomic-embed, CPU, free)
  → store in SQLite (rag.py) — persists through docker purge
  → query: cosine similarity search
  → rerank via LocalAI /v1/rerank (bge-reranker, CPU, free)
  → inject top-K chunks into agent context (pre-embed or MCP response)
```

---

## 4. Context Endgame — The Strategic Shift

### PO Requirement (Verbatim)

> "do we strategically suggest when the status line tells us that we
> have 7% context remaining? that we better get to dumping into
> artifact(s), plan(s) or execute already defined work(s)."

> "there is a fine tune notion there that if you find just the right
> time to stop in order to prevent premature compaction that completely
> destroy the context."

> "exactly like the shift we did a little while ago that you took
> very well and started to barely consume context at this point"

### 4.1 The Organic Flow Model

#### PO Requirement (Verbatim, 2026-04-01)

> "7% for me would be the safe tipping point, with 5% being the real,
> and before that its just informational, even if progressive and mindful"

> "We do not compact for no reason, we let it flow, flow flow down to 0%"

> "we went from 7% to 0% and you are still alive"

> "from the time we have to respond and engage the regather smart context
> protocol everything has been properly synthesised and extracted and
> ready to continue working on"

The context endgame is NOT a rigid zone system with fixed percentages.
It is an organic, progressive awareness that intensifies naturally as
context fills. The AI keeps working — it doesn't suddenly change mode
at arbitrary thresholds. The shift is organic, not forced.

### 4.2 Context Remaining — Progressive Awareness

```
100% → 30% remaining:
  Normal work. No restrictions. No forced efficiency.
  Read, research, explore, build understanding.
  The AI is doing its job. Let it flow.

30% → 7% remaining:
  Progressive mindfulness. Organic efficiency.
  The AI naturally becomes more focused as it has built understanding.
  This shift is NOT forced — it happens because the AI has already
  done the research and is now producing from understood material.
  Informational awareness only. No hard rules.

7% remaining (safe tipping point):
  Prepare extraction. Synthesize findings. Save artifacts.
  Ensure work-in-progress is recoverable.
  KEEP WORKING — a lot can play itself in the last 7%.

5% remaining (real tipping point):
  Final extraction. Commit code. Update artifacts. Write memory.
  Everything extracted enables clean continuation after compact.

0% → compact:
  AI is still alive at 0%. Engage regather smart context protocol.
  Read memory, read state, continue working.
  Everything has been properly synthesised and extracted.
```

**Key principles:**
- Do NOT force compact. Let it flow.
- Do NOT switch to a different "mode" at arbitrary percentages.
- The shift from expansion to delivery is organic — it happens when
  understanding is complete, not when a percentage triggers it.
- A lot of valuable work happens in the last 7% of context.
- At 0% the AI is still alive. Compact is not death.

### 4.3 Why the Organic Model Works — The Pattern Observed

The PO observed this pattern happen naturally in a real session:

1. Early session: heavy research, file reads, design exploration
   → context grew rapidly
2. Understanding crystallized: requirements clear, plan confirmed
3. **Shift happened naturally:** AI switched to small edits, focused
   commits, minimal reads — context barely grew
4. Artifacts produced efficiently from understood material
5. Work delivered BEFORE compaction hit
6. Context went from 7% to 0% remaining — AI still alive and working

This shift was EFFECTIVE because the AI had FULLY UNDERSTOOD the work
before the context filled. The efficiency was NOT forced by a zone
system — it was natural because all remaining actions were well-defined.

The RIGHT time to shift is when understanding is COMPLETE:
- Requirement understood (verbatim processed)
- Plan confirmed (PO approved, readiness 99)
- All contributions received (if applicable)
- Remaining work is EXECUTION, not EXPLORATION
- THEN the shift happens organically regardless of context %

Fixed-percentage triggers are WRONG because sometimes work isn't
understood enough at 85% used. Forcing delivery of half-baked work
is worse than letting context flow and producing quality output.

### 4.4 Implementation Across Systems

This is a cross-cutting behavior, not a single module:

| System | What It Does |
|--------|-------------|
| **Session Telemetry** | Provides `context_used_pct` and `context_remaining_pct` |
| **HeartbeatBundle** | Includes context awareness — informational, not directive |
| **CLAUDE.md** | Includes context management awareness (organic, not zone-based) |
| **Orchestrator** | Brain aware of agent context levels for dispatch decisions |
| **Storm Monitor** | Extreme context pressure as one storm indicator (not the only one) |
| **Methodology** | Near 7% remaining → prioritize completing current stage |
| **Memory** | Near 5% remaining → auto-save learnings to MEMORY.md |
| **Pre-embed** | After compact → regather from memory, not full re-reads |

### 4.5 Connection to Agent Lifecycle

Context endgame connects to the lifecycle system:

```
Agent completes work organically → fleet_task_complete
  → Context was used naturally → task delivered
  → Compaction doesn't matter — work is done

Agent context runs low before completing → organic preparation
  → At 7% remaining: synthesize, save artifacts, keep working
  → At 5% remaining: final extraction, commit, memory write
  → At 0%: compact, regather from memory, continue
  → Next heartbeat: pre-embed has artifact state
  → Agent resumes from artifacts (not from scratch)
  → Consecutive HEARTBEAT_OK doesn't increment (agent has work)

Agent context is wasted (no artifacts produced, nothing saved)
  → Doctor detects: "context near 0%, no artifacts produced"
  → This IS a disease: context_contamination
  → Teaching lesson: "Extract work to artifacts before context fills"
  → Force compact if agent doesn't respond

Agent is pruned (by doctor):
  → Session killed. ALL context lost.
  → Agent regrows fresh on next heartbeat
  → Pre-embedded context has: task details, artifact state, stage
  → Claude-Mem has: learned patterns from previous sessions
  → Agent resumes from where artifacts + pre-embed show
```

### 4.6 Session Telemetry Connection

Session telemetry (W8) provides the data:
```
SessionSnapshot.context_used_pct → agent can read this
SessionSnapshot.context_remaining_pct → how much is left
SessionSnapshot.rate_limit_used_pct → 5h/7d window usage
```

This data feeds:
- Agent awareness (pre-embedded or via tool)
- Storm indicators (extreme context pressure)
- Brain dispatch decisions (agent context level)
- Rate limit session cycle awareness (§4.7)

### 4.7a Memory System Integration

Claude Code's auto-memory (`~/.claude/projects/*/memory/`) provides
cross-session persistence. Claude-Mem plugin adds semantic retrieval.
Together with fleet's pre-embed, agents have 4 layers of context recovery:

```
Layer 1: Pre-embedded context (FREE, every heartbeat)
  Task details, stage, verbatim, artifact state, messages
  Written by orchestrator. Always available.

Layer 2: Claude auto-memory (per-session, file-based)
  MEMORY.md + topic files. Loaded at session start.
  Survives compaction. Agent-written.

Layer 3: Claude-Mem plugin (semantic, cross-session)
  Captures tool usage patterns, generates summaries.
  Injected into future sessions based on relevance.
  Survives prune + regrow.

Layer 4: Fleet RAG (persistent, shared)
  Knowledge base with embedded project knowledge.
  Ingested findings available to ALL agents.
  Survives docker purge (SQLite on host filesystem).
```

**Regather protocol (after compact):**
Read memory files for recovery (200-500 tokens) instead of full source
re-reads (50K+ tokens). Memory was prepared during the organic
extraction at 7%/5% remaining. This is the "regather smart context
protocol" the PO defined.

### 4.7 Rate Limit Session Cycle Awareness

#### PO Requirement (Verbatim)

> "passing a high context through a curent session reset... seem to
> spike the usage very very highly, as if we need to syn with that too
> in our brain to agent communication, that its not just about waiting
> when the current session limite is use at 90% but also preparing at
> 85%, in a similar fasion as the end game strategy to not lose work
> but at the same time to compact not to create huge spike of cost.."

> "Its not like all context were going to be at 1M, especially not all
> the time but in a 1M case this is certainly true, and possibly even a
> little true for smaller context even if less impactfull a bit. (But I
> saw a spike of 20% instantly earlier, as soon as I did my first message
> in a conversation I was waiting after the reset of the current session.)"

> "exactly and when I tried again with compact before 'rollover', I do
> not have this spike. so its a vital piece of information that also
> shape what we will build. its not that we dont want to re-use /
> re-inject session / conversion into the current usage session but to
> do so without huhe spike especially with multiple agent we need to be
> mindful, even if we do not give 1M token to every labor."

#### The Observation

When a rate limit usage window resets (5-hour or 7-day) while an agent
still holds a high-context conversation, the first message in the new
window re-sends the entire context payload. Real data: **20% of fresh
quota consumed instantly** on one message after rate limit rollover.

When the context was compacted BEFORE the rollover — **no spike**.

This means there are TWO parallel countdowns the brain must manage:

1. **Context remaining** (per-agent): 7% remaining = prepare, 5% = real
2. **Rate limit usage session** (fleet-wide): 85% used = prepare, 90% = actively manage

Both interact. An agent at heavy context near rate limit rollover is
a compound risk. Multiple agents with heavy context all heartbeating
into a fresh window = compounding spikes.

#### PO: Controlled Transition — With Force Compact Near Rollover

> "the trigger compact is the last resort... the goal is to do a
> controlled transition like we discussed for the context endgame which
> might often be use for medium to high tasks... especially those with
> chalanges and failures."

> "at some point its force compact lol...the agent can only prepare
> or declare with a till that its ready but we have to be sure that
> it doesn't do it prematuraly either"

> "if we reach the end of the reset I can surely tell you that we
> will force compact all conversation that are too last and will cause
> a spike, this is why we are aware and will not display a 1m context
> big quest when approaching that time for example"

> "imagine you room over 5 x 200 000 or 2 x 1m and whatnot this
> makes no sense on a pro x5 that will take 50% of the whole 5 hours"

> "this is why not only you prepare them to extract their work and
> prepare for compat when appropriate allowing the overflows for the
> budget of compacting even though over 90"

> "if you are over 40 to 80 000 tokens or that you do not need to
> persist your session context (useless predicted cost for the sole
> purpose of being ready for a next job later...), dump (as smart
> artifacts) it for a synthesised re-injection later if needed and/or
> simply a new task if not related. Only smart things. the brain is
> smart. it goes without saying."

The brain uses progressive organic transition FIRST. But near rollover
with agents holding heavy context, **force compact IS appropriate**:

1. **Normal operation**: organic transition, same as context endgame
2. **Approaching rollover**: agents prepare to extract work
3. **Near rollover with heavy contexts**: force compact those that
   would cause a spike — allow going over 90% rate limit budget
   specifically for the compaction cost (it saves more than it spends)
4. **After rollover**: put agents back on track with fresh or
   re-injected sessions as appropriate

#### The Brain's Session Intelligence

The brain evaluates each agent's context against predicted need:

```
For each agent with active context:
  │
  ├── Does this agent have upcoming work needing this context?
  │   YES → keep context, prepare for organic transition
  │   NO  → dump to smart artifacts, fresh session
  │
  ├── Is context over ~40-80K tokens? (threshold to fine-tune)
  │   YES + no predicted need → dump immediately
  │   YES + predicted need → prepare synthesised re-injection
  │   NO  → low cost, keep alive
  │
  ├── Is next task related to current context?
  │   YES → synthesised re-injection later
  │   NO  → simply new task, no re-injection needed
  │
  └── Aggregate fleet context math:
      5 × 200K = 1M tokens re-sent on rollover
      2 × 1M = 2M tokens re-sent on rollover
      On Pro x5: 1M re-send = ~50% of 5-hour window
      Brain calculates total fleet context vs remaining quota
```

Don't persist expensive context "just in case." Don't dispatch
1M context quests near rollover. Only smart things.

#### PO: Cross-Cutting Intelligence

> "in general we try to optimise all with a smart session management,
> smart injections and directives and agents anatomy and all. this is a
> continuously evolving notion that we will fine-tune but like I said a
> lot can play itself in the last 7% of context."

> "the goal of the brain is to be really proactive and make sure the
> agents act aligned with the whole and the systems and process so it
> will certainly be able to summarize all these information at the right
> impact and the right place within the right structure to have the same
> I have when doing conversation and doing those rerouting myself and such."

> "like I said this will need find-tuning but we can come up with the
> right starting logic and make sure we can adapt and scale and make sure
> we can handle multple cases, like varied based of the context size or
> the model or the effort or the distance from next reset and stuff like
> that."

> "for every milestones remain we will need to ask ourselves these kind
> of question and revise everything of the logic that will make this
> fleet amazing and unstopable with good outputs."

This is NOT a standalone milestone. It is a cross-cutting intelligence
principle that shapes EVERY component:

| What | How Session Cycle Awareness Shapes It |
|------|--------------------------------------|
| **Agent CLAUDE.md** | Agents know about both countdowns — context remaining AND rate limit session |
| **Brain dispatch** | Brain does NOT dispatch 1M quests near rollover. Factors context size × distance to reset. |
| **Heartbeat directives** | Brain adjusts ACTION directive based on rate limit position |
| **Work mode** | Rate limit at 85% may trigger work_mode transitions (e.g. finish-current-work) |
| **Budget monitoring** | Budget monitor tracks both quota % AND distance to rollover. Allows >90% for compaction cost. |
| **Storm prevention** | Multiple heavy-context agents near rollover = storm risk. Aggregate math: 5×200K = 1M. |
| **Session telemetry** | Telemetry feeds rate limit window data (5h, 7d) to brain |
| **Agent lifecycle** | Idle agents with no predicted work and heavy context → dump to artifacts |
| **Model selection** | Near rollover: prefer smaller context / LocalAI over 1M Opus |
| **Pre-embed** | After rollover: synthesised re-injection from smart artifacts, not full context re-send |

#### Variables That Interact

The brain must weigh multiple factors simultaneously:

- Context size per agent (1M vs 200K — spike is proportional)
- Aggregate fleet context (sum of all agent contexts vs remaining quota)
- Model assigned (Opus vs Sonnet — different costs)
- Distance to next rate limit reset
- Current rate limit usage %
- Whether each agent's context is needed for predicted upcoming work
- Task complexity (medium/high tasks with challenges and failures use more context)

This will require fine-tuning through practice. The starting logic should
be sound and the structure should support adaptation and scaling across
multiple cases. The brain is smart. It goes without saying.

---

## 5. Brain Intelligence — What Doesn't Need an Agent

The PO said: "we need to be smart and fine tune the brain we know
that a lot does not require agent."

### 5.1 What the Brain Already Does (No AI)

The orchestrator currently runs 9 steps (target: 13 per brain spec
in fleet-elevation/04). ALL are deterministic Python:

```
Step 0: Context refresh        ← direct API calls, file writes
Step 1: Security scan          ← regex pattern matching
Step 2: Doctor cycle           ← rule-based detection
Step 3: Review approvals       ← MC API calls
Step 4: Wake drivers           ← condition checks + inject
Step 5: Dispatch tasks         ← routing logic
Step 6: Process directives     ← tag parsing
Step 7: Evaluate parents       ← child status aggregation
Step 8: Health check           ← threshold comparison
```

NONE of these steps use an LLM. The brain is pure Python logic.

### 5.2 What Else Should Be Brain, Not Agent

```
BRAIN (no AI needed, deterministic):
  ├── Heartbeat evaluation for sleeping agents (check triggers)
  ├── Contribution subtask creation (check matrix, create tasks)
  ├── Budget auto-transitions (check quota thresholds)
  ├── Storm severity evaluation (count confirmed indicators)
  ├── Circuit breaker state management (failure counting)
  ├── Plane sync (API calls, label management)
  ├── Cross-reference generation (event → refs)
  ├── Notification routing (classify → topic)
  ├── Config sync to IaC YAML (Plane → config files)
  └── Diagnostic snapshot capture (data collection)

AGENT (AI needed, requires reasoning):
  ├── Understanding requirements (conversation stage)
  ├── Analyzing codebase (finding patterns, implications)
  ├── Investigating options (research, comparison)
  ├── Planning approach (referencing verbatim, mapping criteria)
  ├── Implementing code (writing, testing, committing)
  ├── Reviewing work (quality assessment, finding issues)
  ├── Communicating with team (contextual responses)
  └── Research (online and in-code, requires judgment)
```

### 5.3 The Three-Tier Decision Model

```
Tier 1: BRAIN (deterministic, free)
  "Is there a new task for this sleeping agent?" → yes/no
  "Has budget crossed 90%?" → pause dispatch except for compact
  "Are all children of parent task done?" → move parent to review
  Cost: $0

Tier 2: LOCAL AI (LocalAI, free, fast)
  "Is this task simple enough for hermes-3b?" → structured evaluation
  "Generate heartbeat response for idle agent" → template + context
  "Parse this structured response" → JSON extraction
  Cost: $0 (local inference)

Tier 3: CLAUDE (cloud, paid, powerful)
  "Design the architecture for this feature" → deep reasoning
  "Review this PR for security issues" → expert analysis
  "Plan implementation referencing requirements" → creative planning
  Cost: $$ (but high quality)
```

The fleet should route decisions to the CHEAPEST tier that can handle
them. Most operational decisions are Tier 1 (brain). Simple evaluations
are Tier 2 (LocalAI). Only real work is Tier 3 (Claude).

**Session management influence on tier selection:**
Near rate limit rollover, the brain favors cheaper tiers more aggressively.
A gradual wake that normally uses Tier 3 (sonnet, medium) might use Tier 2
(LocalAI) when the 5h window is at 90%. Tier 1 (brain deterministic) is
always free and always preferred. The session manager (brain Step 10)
feeds this decision — it knows which agents have heavy context and
what the aggregate fleet cost would be for Tier 3 calls near rollover.

---

## 6. Agent Files Review — Structure for Instinctive AI

### 6.1 What "Instinctive" Means

The agent's context should create an AUTOCOMPLETE CHAIN — each section
narrows the AI's response space so the correct action is the most
natural next token:

```
IDENTITY.md: "I am the architect. I am a top-tier expert."
  → AI generates from architect identity
  
SOUL.md: "I value design before implementation. I respect process."
  → AI behavior bounded by values
  
CLAUDE.md: "In analysis stage, I produce analysis_document artifacts.
            I do NOT produce solutions. I do NOT call fleet_commit."
  → AI knows exactly what to do and NOT do
  
TOOLS.md: "fleet_artifact_create triggers: object → Plane HTML → completeness.
           Call it with type='analysis_document' and title."
  → AI knows which tool to call and what happens
  
AGENTS.md: "Engineers depend on my design input. QA defines tests
            based on my architecture. PM consults me for complexity."
  → AI understands its role in the team
  
context/fleet-context.md: "You have 1 assigned task in analysis stage.
                           Readiness 30%. Missing: findings, implications."
  → AI knows exactly what's needed RIGHT NOW
  
HEARTBEAT.md: "Work on your assigned task. Follow stage protocol."
  → AI acts
```

By the time the AI reaches HEARTBEAT.md, there's a NARROW BAND
of correct responses. The identity, values, rules, tools, team
knowledge, current state, and action prompt all point the same
direction. The correct action is the EASIEST thing to generate.

### 6.2 What Needs to Change in Agent Files

| File | Current State | What's Needed |
|------|--------------|---------------|
| CLAUDE.md | Generic for 9/10 agents | Role-specific per fleet-elevation/05-14. Max 4000 chars. 10 anti-corruption rules. Stage protocol. Tool chains. Contribution model. |
| HEARTBEAT.md | Template for workers, custom for 3 drivers | Per-role per fleet-elevation specs. Different heartbeat priorities per role. |
| IDENTITY.md | Blank template for workers | Generated from template with fleet identity, role description, top-tier expert designation. |
| SOUL.md | Generic template | Role-specific values + shared anti-corruption. Humility clause. |
| TOOLS.md | Auto-generated list | Chain-aware per role: what tool does + what chain fires + WHEN to use in which stage. |
| AGENTS.md | Generic for workers | Per-role synergy: who contributes what to this agent, who this agent contributes to. |
| mcp.json | Template (fleet server only) | Per-role MCP servers (filesystem, github, playwright, docker). |

### 6.3 The 10 Anti-Corruption Rules (Every CLAUDE.md)

From fleet-elevation/20:
```
1. PO's words are sacrosanct. Do not deform the verbatim requirement.
2. Do not summarize when original needed. 20 things = address 20.
3. Do not replace PO's words with your own.
4. Do not add scope not in the requirement.
5. Do not compress scope. Large system = large system.
6. Do not skip reading. Read before modifying.
7. Do not produce code outside work stage.
8. Three corrections = model is wrong. Stop, re-read, start fresh.
9. Follow the autocomplete chain. Context tells you what to do.
10. When uncertain, ask — don't guess.
```

---

## 7. Connections to Other Systems

This intelligence layer touches nearly every system:

| Intelligence Area | Systems It Touches |
|------------------|-------------------|
| Autonomy tuning | Lifecycle, Orchestrator, Config |
| Escalation logic | Router, Budget, Models, Lifecycle, Orchestrator |
| Online research | MCP Tools (WebSearch, Context7), Methodology (investigation stage) |
| Code research | MCP Tools (Read, Grep, Glob, Filesystem), Methodology (analysis stage) |
| Context awareness | Session Telemetry, Lifecycle, Gateway, Teaching (force compact) |
| RAG integration | AICP RAG, LocalAI (embeddings, reranker), Context Assembly |
| Brain intelligence | Orchestrator (9 steps current, 13 target), Lifecycle, Budget, Storm |
| Agent file structure | All agent files, Gateway (injection order), Templates |

---

## 8. What Needs Building

### Code Changes

| Item | Where | Complexity |
|------|-------|-----------|
| Per-agent autonomy config | config/agent-autonomy.yaml + agent_lifecycle.py | Low |
| Brain-evaluated heartbeats | orchestrator.py + agent_lifecycle.py | Medium |
| Escalation logic | New: escalation.py + orchestrator integration | Medium |
| Strategic Claude call config | orchestrator.py dispatch decision | Medium |
| Context awareness in agents | CLAUDE.md instructions + session telemetry | Low (config) |
| RAG → fleet integration | Custom MCP server or context_assembly enhancement | Medium |
| Agent CLAUDE.md × 10 | Per fleet-elevation specs | High (careful writing) |

### Configuration

| Item | File |
|------|------|
| Per-agent autonomy thresholds | config/agent-autonomy.yaml |
| Per-agent wake triggers | config/agent-autonomy.yaml |
| Escalation matrix | config/escalation.yaml |
| RAG config | config/rag.yaml |

---

## 9. Test Coverage

This is a specification document. Testing means:
- Autonomy config loads correctly, thresholds respected
- Escalation logic produces correct model/effort per scenario
- Brain evaluation detects wake triggers without Claude call
- RAG queries return relevant results
- Agent CLAUDE.md within 4000 char limit
- Context pressure thresholds trigger correct agent behavior
