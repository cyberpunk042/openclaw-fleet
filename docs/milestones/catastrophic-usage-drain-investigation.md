# CATASTROPHIC: Fleet Drained 20% of Usage Plan in 5 Seconds

## Severity: CATASTROPHIC

This is the most critical bug in the fleet's history. The fleet consumed 20% of
the user's Claude Code plan in approximately 5 seconds while doing NO useful work.
The weekly budget is now critically low with 6 days until reset.

This happened while there was no real work to do — agents were idle, Sprint 3 was
mostly blocked, the board was 90% noise. Yet the fleet burned through tokens at
an alarming rate.

**This must be the #1 priority. Nothing else matters until this is investigated,
understood, and prevented permanently.**

---

## Part 1: User Report (Verbatim)

> "wtf is happening the agents are not working and they are draining all my usage"

> "20% of plan was gone in 5 seconds.... this is fucking highly serious"

> "we need a thorough investigation of everything and what happened when there are
> task and they are blocked or what else happens that create a cluster fuck of
> phantom operation that consume token to do dunno what..... void work? infinite
> parallel loop work?"

> "the fleet cp is also going to have to keep track of the plan usage in general
> and detect irregularities, detect 50%, detect 5% fast climb, 10% fast climb, etc,
> and 70% 80% and 90% and detect outage (official and non-official, potentially
> local trouble or really cloud issues or in between)"

> "we really need to avoid brainless loop and recursive chain that don't end and
> infinite loop or trying to take a task or work on something blocked and things
> like this. always with awareness of the session of the user and when it reset
> be logical and then announce when the work has started to resume and so on"

> "fleet-ops comes to my mind. the fleet program is supposed to be strong and smart
> and the fleet-ops has to observe and operate and report things or act on them.
> we need to be able to pause all the work or reduce the efforts and strategy like
> that strategic and driven by the user and circumstances"

> "stop minimizing what I said and the job of the agent... you need to think of
> them as real employees with real role that even when there is no tasks they can
> work unless there is really no recent work or events and there is no backlog or
> project backlog to go pull from. But do not forget for example that before a task
> is executed usually the project manager created it yeah but there was an analysis
> done before the official task(s)"

> "obviously this all start by finding the sources of this catastrophy.... so much
> money down the drain in such a fraction of seconds.... possibly not even agent
> but the fleet process themselves?"

> "there seem to be two budget and somehow the weekly budget which I never was before
> even on lower plan is getting close really fast and the reset is in 6 days....
> we need to track that properly and do our diagnosis and continuous tracking and
> analysis from the agent"

> "This is not in the scope but we will also look how to wise ourself through aicp
> and localai when its online especially for but that we will need to plan after all
> this and we will be basically able to pass through it first and it should only call
> claude when needed otherwise do mcp / tool calls and whatever"

> "DO not corrupt or minimize or compress my words. take them as is. and you will
> need to quote them into the new documents in order to achieve all this properly
> and not forget a single thing and so that we meet the requirements or above and
> deliver a great product / a great solution that will make the work even stronger
> and economic"

---

## Part 2: Investigation — What Happened

### 2.1 Timeline of Events

1. Fleet daemons running: sync (60s), monitor (300s), auth (120s), orchestrator (30s)
2. Orchestrator cycle every 30 seconds:
   - Security scan → ensure approvals → wake fleet-ops → dispatch tasks → parent eval → health check → heartbeats
3. Gateway ALSO cycling agent heartbeats independently (every 10 minutes per agent heartbeat_config)
4. Sprint 3 loaded: 10 tasks, 8 blocked, 1 unblocked (god-mode done), 1 epic
5. God-mode completed → s3-workspace unblocked → dispatched to devops
6. Devops works → completes → moves to review → fleet-ops woken for review
7. Meanwhile: ALL other agents have NO work but gateway keeps waking them

### 2.2 Sources of Token Drain

**Source 1: Gateway heartbeat system (INDEPENDENT of orchestrator)**

The OpenClaw gateway has its own heartbeat system:
```json
"heartbeat": {
  "every": "10m",
  "target": "last",
  "includeReasoning": false
}
```

Every 10 minutes, the gateway sends a heartbeat to EACH agent session.
Each heartbeat triggers a Claude Code execution:
- Reads CLAUDE.md, HEARTBEAT.md, STANDARDS.md, MC_WORKFLOW.md
- Processes the heartbeat message
- Calls fleet tools (fleet_read_context, fleet_agent_status)
- Generates a response
- All of this consumes tokens

10 agents × every 10 min = **60 heartbeat sessions per hour**.
Each session: estimated 5,000-20,000 tokens.
Total: **300,000 - 1,200,000 tokens/hour from gateway heartbeats alone.**

**Source 2: Orchestrator wake calls**

The orchestrator was sending `_send_chat(session_key, message)` to wake
PM and fleet-ops every 30 minutes. Each wake triggers a full session.
This is ON TOP of the gateway heartbeats.

**Source 3: Possible infinite loop / rapid cycling**

> "possibly not even agent but the fleet process themselves?"

The orchestrator runs every 30 seconds. If the orchestrator's dispatch
or wake logic had a condition that kept triggering (e.g., detecting the same
unblocked task but failing to dispatch it, then retrying next cycle), it
could create rapid-fire wake calls.

INVESTIGATION NEEDED:
- Was the orchestrator calling `_send_chat` multiple times per cycle?
- Was the dispatch failing silently, causing retry on next cycle?
- Were there race conditions between orchestrator and gateway heartbeats?
- Was the same agent being woken by BOTH orchestrator and gateway simultaneously?

**Source 4: Agent sessions doing void work**

When an agent is woken with nothing to do:
- It reads context (tool calls → tokens)
- It reads board memory (tool calls → tokens)
- It finds no work
- It responds "HEARTBEAT_OK"
- All of this cost tokens for ZERO useful output

With a board that's 90% noise (75 heartbeat tasks, 5 review tasks, 10 conflict
tasks), just reading the task list consumes significant tokens.

**Source 5: The 30-second orchestrator cycle itself**

The orchestrator makes MC API calls every 30 seconds:
- list_tasks (fetches all 100 tasks)
- list_agents (fetches all 11 agents)
- list_approvals (fetches all approvals)
- These are HTTP calls, not token-consuming — BUT if the orchestrator was
  triggering agent wakes on each cycle, that's wake calls every 30 seconds.

### 2.3 Why It Happened So Fast

> "20% of plan was gone in 5 seconds"

5 seconds is too fast for 30-second orchestrator cycles. This suggests:
1. The gateway heartbeat system was the primary drain (it runs independently)
2. Multiple agents were triggered simultaneously
3. OR: there was an actual infinite loop in the fleet code

**Most likely scenario:**
- Gateway heartbeat fired for multiple agents simultaneously
- Each agent session ran in parallel (Claude Code sessions are concurrent)
- 5-10 agents × 10,000-20,000 tokens each = 50,000-200,000 tokens in one batch
- Multiple batches in rapid succession
- 20% of plan consumed

### 2.4 The Two Budget Problem

> "there seem to be two budget and somehow the weekly budget which I never was
> before even on lower plan is getting close really fast"

Claude Code has:
- **Daily budget**: tokens per day
- **Weekly budget**: tokens per week (rolling)
- The fleet was consuming from BOTH simultaneously
- Weekly budget is harder to recover from (6 day reset)

---

## Part 3: Required Fixes (Priority Order)

### FIX 0: Gateway Heartbeat Interval — INCREASE MASSIVELY

**The single most impactful fix.** The gateway's heartbeat_config drives
independent agent cycling that we don't control from the orchestrator.

Current: `"every": "10m"` → 6 heartbeats/hour/agent → 60/hour total
MUST BE: `"every": "120m"` minimum → 0.5/hour/agent → 5/hour total

For idle agents: `"every": "480m"` (8 hours) — basically off

**How to change:**
- Modify `~/.openclaw/openclaw.json` → agents.list[].heartbeat.every
- OR: use MC API to update agent heartbeat_config
- OR: use board group heartbeat API to set globally

### FIX 1: Fleet Pause / Kill Switch

> "we need to be able to pause all the work or reduce the efforts"

Build `fleet pause` and `fleet resume` commands:
- `fleet pause` → stops all daemons, sets gateway heartbeat to "never",
  posts to IRC/ntfy "Fleet paused by human"
- `fleet resume` → restarts daemons, restores heartbeat intervals
- `fleet pause --reason "budget conservation"` with reason tracking

### FIX 2: Token Budget Awareness and Monitoring

> "the fleet cp is also going to have to keep track of the plan usage"
> "detect irregularities, detect 50%, detect 5% fast climb, 10% fast climb"

Build fleet/core/budget_monitor.py:
- Track estimated token usage per agent session
- Alert thresholds: 5% fast climb, 10% fast climb, 50%, 70%, 80%, 90%
- Auto-pause fleet when threshold exceeded
- ntfy URGENT notification on budget alerts
- Daily/weekly budget reporting
- Detect anomalies: if usage rate exceeds historical average by 3x → pause

### FIX 3: Prevent Infinite Loops and Void Work

> "avoid brainless loop and recursive chain that don't end"
> "infinite loop or trying to take a task or work on something blocked"

Safeguards in the orchestrator:
- **Dispatch guard**: if dispatch fails for a task, mark it with a retry count.
  After 3 failures, skip it and alert.
- **Wake guard**: track wake calls per agent per hour. If > 3 wakes/hour for
  an agent with no work → stop waking that agent.
- **Blocked task guard**: NEVER try to dispatch blocked tasks. Check is_blocked
  before ANY dispatch attempt.
- **Session guard**: if an agent session runs for > 5 minutes with no tool calls
  → something is wrong → abort session.
- **Cycle guard**: orchestrator tracks actions per cycle. If a cycle has 0 actions
  for 5 consecutive cycles → reduce check frequency to 5 minutes.

### FIX 4: Short-Circuit Heartbeats

When an agent is woken for a heartbeat and has NOTHING to do:
- Agent should respond with "HEARTBEAT_OK" immediately
- Do NOT call fleet_read_context (costs tokens to fetch context)
- Do NOT call fleet_agent_status (costs tokens)
- Just check: any assigned tasks? No → HEARTBEAT_OK. Done.
- This minimizes token usage for empty heartbeats

HEARTBEAT.md should say:
```
FIRST: Do you have assigned tasks or chat messages?
  If NO and nothing in your domain needs attention: respond HEARTBEAT_OK immediately.
  Do NOT call any tools. Do NOT read context. Just respond.
  If YES: then read context and proceed with your heartbeat duties.
```

### FIX 5: Fleet-Ops as Budget Guardian

> "fleet-ops has to observe and operate and report things or act on them"

Fleet-ops should monitor:
- Token usage trends
- Agent session frequency and duration
- Void sessions (sessions with no useful output)
- Auto-pause recommendation when usage is abnormal

### FIX 6: Outage and Reset Detection

> "detect outage (official and non-official, potentially local trouble or
> really cloud issues or in between)"
> "awareness of the session of the user and when it reset"

The fleet needs to know:
- When the weekly/daily budget resets
- Current usage level (if API provides it)
- When rate limits are hit → back off, don't keep hammering
- When API is down → pause operations, notify human
- When budget resets → announce "Budget reset, work can resume"

### FIX 7: Effort and Strategy Control

> "reduce the efforts and strategy like that strategic and driven by the
> user and circumstances"

Build configurable effort profiles:
- **Full**: all agents active, normal heartbeats, opus for complex tasks
- **Conservative**: only drivers active, long heartbeats, sonnet only
- **Minimal**: only fleet-ops monitoring, no heartbeats, emergency only
- **Paused**: nothing runs, gateway heartbeats off

Human selects profile via `fleet effort conservative` or config.

---

## Part 4: Agent Role Reality Check

> "think of them as real employees with real role that even when there is no
> tasks they can work unless there is really no recent work or events and
> there is no backlog or project backlog to go pull from"

> "before a task is executed usually the project manager created it yeah but
> there was an analysis done before the official task(s)"

Agents are not just task executors. They are:

**Project Manager:**
- Analyzes work BEFORE creating tasks
- Does requirements gathering, scope definition
- Creates tasks with clear acceptance criteria
- Drives Scrum: standup, retrospective, sprint planning
- Resolves blockers proactively (never > 2 simultaneously)
- Assigns work based on capability AND current workload
- Tracks velocity and adjusts pace

**Software Engineer:**
- Reads architecture decisions before implementing
- Participates in design discussions with implementation perspective
- Reviews own work for loose ends (tests? docs?)
- Checks PRs for conflicts and reviewer comments
- Helps other engineers when they're stuck
- Pulls from backlog when idle (doesn't just say "no work")

**Architect:**
- Reviews implementations for architectural drift
- Participates in discussions about patterns and approaches
- Posts observations and recommendations proactively
- Helps PM break down complex work into implementable tasks

**QA Engineer:**
- Checks test health proactively (flaky tests, coverage gaps)
- Reviews recently completed code for test adequacy
- Runs tests before anyone asks (proactive quality)
- Creates test infrastructure tasks when needed

**fleet-ops:**
- Monitors everything: budget, usage, agent health, board state
- Acts on anomalies (not just reports them)
- Pauses fleet when something is wrong
- Quality gate for all completed work

**Cyberpunk-Zero:**
- Scans PRs proactively for security
- Monitors dependencies for CVEs
- Reviews infrastructure changes
- Behavioral analysis of agent output

**All agents:**
- Check chat and respond to teammates
- Read decisions and participate in discussions
- Pull work from backlog when idle (with PM's guidance)
- Create follow-up tasks when they discover work
- Never sit idle without telling lead

---

## Part 5: Future — AICP and LocalAI Integration

> "we will also look how to wise ourself through aicp and localai when its
> online especially for but that we will need to plan after all this and we
> will be basically able to pass through it first and it should only call
> claude when needed otherwise do mcp / tool calls and whatever"

This is a future milestone but important to note:
- AICP + LocalAI can handle routine operations without Claude tokens
- MCP tool calls through LocalAI for: fleet_read_context, fleet_agent_status
- Only escalate to Claude for: complex reasoning, code generation, design
- This dramatically reduces Claude token usage
- Will be a major epic in DSPD/Plane once the fleet is stable

---

## Part 6: Milestone Summary

### Immediate (before ANY fleet restart):

| # | Milestone | Priority |
|---|-----------|----------|
| C0 | Investigate exact cause of 20% drain in 5 seconds | CRITICAL |
| C1 | Increase gateway heartbeat interval to 120m+ | CRITICAL |
| C2 | Build fleet pause/resume commands | CRITICAL |
| C3 | Build budget monitoring with auto-pause | CRITICAL |
| C4 | Prevent infinite loops (dispatch/wake/session guards) | CRITICAL |
| C5 | Short-circuit empty heartbeats (HEARTBEAT_OK fast path) | HIGH |
| C6 | fleet-ops as budget guardian | HIGH |
| C7 | Outage and reset detection | HIGH |
| C8 | Effort profiles (full/conservative/minimal/paused) | HIGH |

### After fleet is safe to restart:

| # | Milestone | Priority |
|---|-----------|----------|
| C9 | All agent heartbeats rewritten (active participation) | HIGH |
| C10 | Board cleanup (remove 90 noise tasks) | HIGH |
| C11 | Chat verification end-to-end | HIGH |
| C12 | PM as Scrum Master (proper task management) | HIGH |
| C13 | Communication 8-point verification | HIGH |
| C14 | Sprint 3 relaunch with proper flow | MEDIUM |

### Future (after fleet stable):

| # | Milestone | Priority |
|---|-----------|----------|
| C15 | AICP + LocalAI integration planning | FUTURE |
| C16 | Token optimization via local inference | FUTURE |
| C17 | DSPD/Plane epic for fleet economics | FUTURE |

---

## Part 7: What We Need to Deliver

> "deliver a great product / a great solution that will make the work even
> stronger and economic"

The fleet must be:
1. **Safe** — never drain budget, auto-pause on anomalies
2. **Smart** — only consume tokens when there's actual work
3. **Economic** — minimize token usage for overhead, maximize for real work
4. **Observable** — budget tracking, usage reporting, anomaly detection
5. **Controllable** — pause/resume, effort profiles, human override
6. **Productive** — agents follow roles, communicate, flow work properly
7. **Sustainable** — works within budget indefinitely, not in bursts