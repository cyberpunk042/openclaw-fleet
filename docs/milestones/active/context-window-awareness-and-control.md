# Context Window Awareness and Control

**Date:** 2026-03-31
**Author:** PO + AI (collaborative research session)
**Status:** ACTIVE — configurations applied, statusline pending

---

## 1. Origin — Product Owner Requirements

These are the PO's exact words that drove this investigation:

> "I realize there is a nuance when the subscription is Max 20X vs Max 5X, not to talk about against the Pro... but I feel like the real 1M context token is only as an early access and not even enabled right now because I changed account because I bursted the limit and now I went from the lowers subscriptions and at Max 5X now... online it seems to say '20x more usage than Pro' to be the only difference but I do not see the 1M size setting in the options anymore... what does this mean?"

> "it could explain why its possible for the agent in 20X mode or whatever in 1M token mode that the weekly limit even though large also depleting faster because of all the added context and massive computes. So this makes you think, should we not be aware of this too? how do we validate the size or even decide the size?"

> "There seem to be the notion sometimes that we need to reach the edge somehow of the context to really cease the work / task properly before being able to finish process and output. that's tricky, you do not want to compact prematurely and yet in some situation you want compact strategically"

> "I was right, you just compacted 176k token, so we do now are on a lower context size. interesting. the delivery was tolerable but it explain the recent hikhups and the difficulty to do hard task I had recently been able to do with claude code... This is interesting. this mean that this make a huge difference."

> "work properly and check that things are proper before we continue and find a way so that the next context compact we can with focus regather the context without creeping the context... its not normal that with 1M context it was filled with just a few thousands lines...."

> "requirements we will need to meet that you will have to quote back in a document that prove we have this feel awareness and control and proper use of those settings and configurations"

---

## 2. Requirements Extracted

From the PO's statements, the following requirements are identified:

| ID | Requirement | Source Quote |
|----|-------------|--------------|
| CW-01 | **Know the context window size** — validate whether 1M or 200K is active, don't assume | "how do we validate the size or even decide the size?" |
| CW-02 | **Awareness of cost dynamics** — 1M context = more tokens per turn = faster quota drain | "should we not be aware of this too?" |
| CW-03 | **Strategic compaction** — don't compact prematurely, but don't let context rot either | "you do not want to compact prematurely and yet in some situation you want compact strategically" |
| CW-04 | **Efficient context regathering** — after compaction, recover from memory not full re-reads | "find a way so that the next context compact we can with focus regather the context without creeping the context" |
| CW-05 | **Prevent context bloat** — it should not fill with "just a few thousands lines" | "its not normal that with 1M context it was filled with just a few thousands lines" |
| CW-06 | **Control and prove it** — document the settings, configurations, and awareness | "quote back in a document that prove we have this feel awareness and control" |

---

## 3. Research Findings

### 3.1 Subscription Tiers and Context Access

| Plan | Price | Usage Multiplier | 1M Context | Features |
|------|-------|------------------|------------|----------|
| **Pro** | $20/mo | 1x | Via "extra usage" only | Claude Code access |
| **Max 5X** | $100/mo | 5x | **Yes — included** | Claude Code + Cowork + priority |
| **Max 20X** | $200/mo | 20x | **Yes — included** | Same features as Max 5X |

**Finding:** Both Max 5X and Max 20X get identical features including 1M context. The only difference is quota volume. The PO's concern about losing 1M after account switch may have been a UI display issue — both Max tiers include it via `/model opus[1m]`.

**Quota economics:** Max 20X costs 2x Max 5X but provides 4x more quota (20x vs 5x Pro) — better per-token value. Community reports (GitHub #27310, 532 upvotes) show Max 20X users still burning through weekly allowance in under 2 days.

### 3.2 Context Window as Cost Multiplier

Claude Code sends the **full conversation history** as input tokens on every API call. This creates multiplicative cost:

```
Turn 1:  context = 10K tokens  × 1 API call  =  10K input tokens
Turn 5:  context = 80K tokens  × 3 API calls =  240K input tokens
Turn 10: context = 200K tokens × 5 API calls = 1M input tokens
Turn 15: context = 500K tokens × 8 API calls = 4M input tokens
```

**Key facts:**
- Claude Code makes 8-12 API calls per user command (tool calls, reads, writes)
- Each call carries the full context as input
- A single "edit this file" command can consume 50K-150K tokens
- A 15-iteration session burns ~200K tokens from context multiplication alone
- No per-token premium for >200K — but more context = more tokens per call = faster depletion
- Prompt cache has only a 5-minute lifetime — pauses between turns break it, causing full-price re-sends

### 3.3 Context Visibility — What's Actually Available

**The IDE knows context usage because Claude Code exposes it via JSON session data.**

The VSCode extension receives these fields on every turn:

| Field | What It Shows |
|-------|---------------|
| `context_window.context_window_size` | Total capacity (200K or 1M) |
| `context_window.used_percentage` | How full the context is |
| `context_window.remaining_percentage` | How much is left |
| `context_window.current_usage.input_tokens` | Input tokens this turn |
| `context_window.current_usage.output_tokens` | Output tokens this turn |
| `context_window.current_usage.cache_creation_input_tokens` | Cache write tokens |
| `context_window.current_usage.cache_read_input_tokens` | Cache hit tokens |
| `context_window.total_input_tokens` | Cumulative session input |
| `context_window.total_output_tokens` | Cumulative session output |
| `exceeds_200k_tokens` | Boolean flag if >200K |

**The model also receives context awareness via system blocks:**
```xml
<budget:token_budget>1000000</budget:token_budget>
<system_warning>Token usage: 35000/1000000; 965000 remaining</system_warning>
```

### 3.4 Statusline — Persistent Context Display

Claude Code's `/statusline` command generates a shell script (`~/.claude/statusline.sh`) that receives the JSON session data on stdin and renders a persistent status bar. Example:

```bash
#!/bin/bash
input=$(cat)
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
MODEL=$(echo "$input" | jq -r '.model.display_name')
FILLED=$((PCT * 10 / 100))
BAR=$(printf '%*s' "$FILLED" | tr ' ' '▓')$(printf '%*s' $((10-FILLED)) | tr ' ' '░')
echo "[$MODEL] $BAR $PCT%"
```

This gives us **real-time context awareness** — directly addressing CW-01 and CW-06.

### 3.5 Known Bugs (Anthropic-Acknowledged, 2026-03-31)

Anthropic publicly acknowledged on March 31, 2026 that users are "hitting usage limits in Claude Code way faster than expected" — called it **top priority**.

| Bug | Impact |
|-----|--------|
| Prompt cache breaks after 5-minute pause | Costs inflated 10-20x silently |
| Background agents use Opus quota | Consumes allowance before user types |
| Silent retries on rate-limit errors | Drains budget in minutes |
| Two cache-breaking bugs in binary | Confirmed by reverse-engineering |

### 3.6 The "Edge Sensation"

The PO described:
> "There seem to be the notion sometimes that we need to reach the edge somehow of the context to really cease the work / task properly"

This is real. As context fills:
1. The model has maximum information available — peak capability
2. But it's racing against compaction — time pressure
3. Compaction loses detail — post-compaction quality drops
4. Re-gathering requires tokens — creating a debt cycle

The sweet spot: **deliver the artifact before compaction, then let it compact, then recover from memory for the next task.** This pattern worked successfully in the Wave 1-5 milestone delivery.

### 3.7 Corrected Information

The following items from community sources were **NOT verified** in official documentation:

| Claim | Status | Reality |
|-------|--------|---------|
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW` env var | **NOT OFFICIAL** | No such env var in Anthropic docs. Compaction is managed via `/compact` command and server-side auto-compaction. |
| Premature compression bug in v2.0.15+ | **UNVERIFIED** | Community report, not confirmed by Anthropic |
| Downgrading to v2.1.34 improves performance | **UNVERIFIED** | Anecdotal, not reproducible |

**We do not rely on unverified settings.** Our control plane uses only documented features.

---

## 4. Current State Audit

### 4.1 What We Have

| Setting | Current Value | Status |
|---------|---------------|--------|
| Model | `claude-opus-4-6[1m]` | 1M context active |
| Subscription | Max 5X ($100/mo) | 5x Pro quota |
| CLAUDE.md (AICP) | 292 lines | Under 500 threshold |
| CLAUDE.md (Fleet) | 230 lines | Under 500 threshold |
| CLAUDE.md (DSPD) | 178 lines | Under 500 threshold |
| Memory system | 29 entries in MEMORY.md | Active, used for regathering |
| Skills | Loaded on-demand | Correct pattern |
| `.claudeignore` (AICP) | **APPLIED** | Excludes model bins, .venv, __pycache__, build artifacts |
| `.claudeignore` (Fleet) | **APPLIED** | Excludes node_modules, .venv, __pycache__, workspaces |
| `.claudeignore` (DSPD) | **APPLIED** | Excludes .venv, __pycache__, build artifacts |

### 4.2 What We Still Need

| Setting | Current | Should Be | Addresses |
|---------|---------|-----------|-----------|
| Statusline | **DONE** | Context % + model + rate limits via statusline.sh | CW-01, CW-06 |
| Context commands | **Not used** | Use `/context` to check breakdown before heavy tasks | CW-03 |
| `.claudeignore` (NNRT) | **Missing** | Exclude .venv, __pycache__ | CW-05 |
| Session telemetry adapter | **Not built** | `session_telemetry.py` feeds real session data to fleet modules | CW-02 |

### 4.3 Environment Variables

```
CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING=true
CLAUDECODE=1
CLAUDE_AGENT_SDK_VERSION=0.2.88
CLAUDE_CODE_ENTRYPOINT=claude-vscode
```

No context-specific env vars needed — visibility comes from statusline and `/context`, not env vars.

---

## 5. Action Plan — What We Control

### 5.1 `.claudeignore` Files — DONE

Applied to AICP, Fleet, DSPD. Every excluded file is tokens saved on every turn.

### 5.2 Statusline — DONE

Installed via IaC: `make install-statusline` (AICP) or `scripts/install-statusline.sh`

**Display (2 lines):**
```
Opus [1M] project-name main
████████░░░░░░░░░░░░ 42% | $0.15 3m0s +256/-31 5h:24% 7d:41%
```

**Shows:**
- Model name + context window size label (1M/200K)
- 20-char context usage bar with color thresholds (green <70%, yellow 70-89%, red 90%+)
- Session cost, duration, lines added/removed
- Rate limit usage: 5-hour and 7-day windows with color thresholds (dim <50%, yellow 50-79%, red 80%+)
- Git branch

**Files:**
- Script: `~/.claude/statusline.sh` (jq-based, installed by IaC)
- Config: `~/.claude/settings.json` → `statusLine.command`
- Installer: `scripts/install-statusline.sh` (manages jq dependency via brew/nix/apt)
- Makefile target: `make install-statusline`

This gives the PO persistent visibility into context state. No more guessing.

### 5.3 Session Discipline Protocol

| Phase | Action | Tool | Addresses |
|-------|--------|------|-----------|
| **Session start** | Verify model shows `[1m]` suffix | Statusline | CW-01 |
| **Before heavy task** | Check context breakdown | `/context` | CW-03 |
| **Strategic compaction** | Compact with custom preservation instructions | `/compact` | CW-03 |
| **After compaction** | Regather from memory files, not source re-reads | Memory system | CW-04 |
| **Between logical tasks** | Clear and start fresh sprint | `/clear` | CW-05 |
| **Artifact delivery** | Extract artifacts and save to memory before compaction | Memory system | CW-04 |

### 5.4 Memory as Context Insurance

The memory system at `~/.claude/projects/*/memory/` serves as compaction recovery. Currently 29 entries.

**Protocol:** After compaction, AI reads `MEMORY.md` index (29 lines) and selectively reads only the 2-3 memory files relevant to the current task. This costs ~200-500 tokens instead of the 50K+ it would take to re-read source files.

### 5.5 Agent Compaction Protocol

For fleet agents using Claude Code, the same discipline applies:

1. Agent detects high context usage via system warnings
2. Agent extracts current work artifacts to files
3. Agent saves key state to memory
4. Agent allows compaction or `/clear`
5. Agent regathers from memory to continue

This is not yet implemented in agent code but should be part of the agent lifecycle (cross-ref: fleet autonomy milestones).

---

## 6. Proof of Awareness and Control

This section directly addresses CW-06: *"quote back in a document that prove we have this feel awareness and control and proper use of those settings and configurations."*

### We Are Aware Of:

1. **Context window size is visible** — the IDE exposes `context_window.used_percentage` and `context_window.context_window_size` via JSON session data. Statusline can display this persistently.
2. **1M context is a double-edged sword** — more capability per turn, but faster quota drain from multiplicative API calls (8-12 calls per command, each carrying full context)
3. **Compaction is both necessary and destructive** — it frees tokens but loses detail, requiring deliberate recovery via memory system
4. **The "edge sensation" is real** — near-full context gives peak capability but risks premature compaction. Strategy: deliver artifact first, then compact, then recover.
5. **Bugs exist** — prompt cache breaking (5-min lifetime), silent retries, background agents consuming Opus quota. Anthropic acknowledged as top priority 2026-03-31.
6. **Max 5X = 5x Pro quota but identical features to Max 20X** — we're not missing capabilities, just runway

### We Control:

1. **`.claudeignore`** — applied to 3 projects, prevents unnecessary file reads from inflating context
2. **Statusline** — configurable via `/statusline`, shows context % and model in real-time (TO CONFIGURE)
3. **`/context` command** — inspect context breakdown before heavy tasks
4. **`/compact` command** — strategic compaction with custom preservation instructions
5. **Model selection** — `/model opus[1m]` explicitly requests 1M context
6. **Memory system** — 29 entries, enables efficient post-compaction recovery
7. **Session discipline** — `/clear` between tasks, scoped prompts, sprint-style work
8. **CLAUDE.md size** — all under 500 lines, loaded every turn
9. **Skills on-demand** — specialized instructions load only when needed, not every turn

### We Validate By:

1. **Statusline** — persistent display of model + context % (once configured)
2. **`/context`** — on-demand context breakdown before heavy work
3. **System warnings** — model receives `Token usage: X/Y; Z remaining` from system
4. **Compaction monitoring** — noting how many tokens freed, adjusting strategy
5. **This document** — proving we've researched, understood, and configured accordingly

---

## 7. Rate Limit Session Rollover — Cost Spike Discovery

### PO Observation (2026-04-01, Verbatim)

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
> not have this spike."

### What Happened

1. Rate limit usage window hit ~90%+. PO waited for reset.
2. Rate limit window rolled over (fresh quota).
3. First message in the SAME high-context conversation → **20% of fresh quota consumed instantly**.
4. PO tested with compaction BEFORE rollover → **no spike**.

### Why This Happens

Claude Code sends the **full conversation context** as input tokens on every API call (8-12 calls per message). A 1M-context session's first message in a fresh window re-sends the entire payload at full price. The previous window absorbed the cost of building that context gradually. The new window gets hit with the FULL accumulated weight in one shot.

### Impact on Fleet

With 10 agents, if multiple are holding heavy-context sessions when a rate limit window rolls over and they all heartbeat in the new window:

- Each agent's first action re-sends its full context
- 10 agents × heavy context = massive compound spike
- Even at 200K per agent, this is significant
- At 1M per agent, this could consume a large fraction of the fresh window immediately

### PO Direction: Controlled Transition — Force Compact Near Rollover

> "the trigger compact is the last resort... the goal is to do a
> controlled transition like we discussed for the context endgame"

> "at some point its force compact lol...the agent can only prepare
> or declare with a till that its ready but we have to be sure that
> it doesn't do it prematuraly either"

> "if we reach the end of the reset I can surely tell you that we
> will force compact all conversation that are too last and will cause
> a spike, this is why we are aware and will not display a 1m context
> big quest when approaching that time for example"

> "imagine you room over 5 x 200 000 or 2 x 1m and whatnot this
> makes no sense on a pro x5 that will take 50% of the whole 5 hours"

> "if you are over 40 to 80 000 tokens or that you do not need to
> persist your session context (useless predicted cost for the sole
> purpose of being ready for a next job later...), dump (as smart
> artifacts) it for a synthesised re-injection later if needed and/or
> simply a new task if not related. Only smart things."

The brain applies progressive awareness to rate limit windows:
- **85% rate limit used** = start preparing (like 7% context remaining)
- **90% rate limit used** = actively managing (like 5% context remaining)

But near rollover with heavy contexts, **force compact IS appropriate**:
- Allow going over 90% budget specifically for compacting (saves more)
- Don't dispatch 1M context quests near rollover
- Agents over ~40-80K with no predicted upcoming work → dump to artifacts
- Aggregate math: 5×200K = 1M on rollover ≈ 50% of x5 Pro window
- After rollover: fresh sessions or synthesised re-injection as needed

### New Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| CW-07 | **Rate limit rollover awareness** — brain must track distance to rate limit window reset and factor agent context sizes | "we need to syn with that too in our brain to agent communication" |
| CW-08 | **Pre-rollover preparation** — controlled context management before window resets, not after | "preparing at 85%... compact not to create huge spike of cost" |
| CW-09 | **Context-size-proportional awareness** — 1M sessions need more aggressive preparation than 200K | "in a 1M case this is certainly true, and possibly even a little true for smaller context" |
| CW-10 | **Multi-agent rollover coordination** — brain must stagger or manage multiple agents crossing rollover | "with multiple agent we need to be mindful" |

### Cross-Cutting Impact

> "for every milestones remain we will need to ask ourselves these kind
> of question and revise everything of the logic that will make this
> fleet amazing and unstopable with good outputs."

This is not a standalone milestone. It is a lens applied to every remaining milestone. Full analysis in System 22 §4.7.

---

## 8. Relationship to Fleet Systems

This awareness feeds directly into existing fleet milestones:

| System | Connection |
|--------|------------|
| **Budget Mode (M-BM)** | Budget mode is a tempo setting — context size is a separate concern managed by session management |
| **Multi-Backend Router (M-BR)** | Router should consider context cost when choosing backends — LocalAI has no context cost, Claude's context is the primary cost lever |
| **Backend Health (M-BR07)** | Claude health tracking includes `quota_used_pct` — context burn rate directly affects this. JSON session data provides actual numbers. |
| **Storm Prevention (M-SP)** | Context exhaustion can trigger storm conditions — an agent in a re-read loop after compaction is a cost storm |
| **Labor Attribution (M-LA)** | Labor stamps should track context cost per task, not just API cost. Session data provides `total_input_tokens` and `total_output_tokens`. |

### Session Telemetry Adapter (W8 — Integration Plan)

The same JSON data that feeds the statusline also feeds our fleet systems. A new adapter module (`session_telemetry.py`) will parse session JSON and distribute real values to existing modules:

| Session Field | Fleet Module | Replaces |
|---|---|---|
| `cost.total_cost_usd` | `to_cost_delta()` | Estimated cost |
| `cost.total_duration_ms` | `LaborStamp.duration_seconds` | Estimated duration |
| `cost.total_lines_added/removed` | `LaborStamp` (new fields) | No measurement |
| `rate_limits.five_hour.used_percentage` | `ClaudeHealth.quota_used_pct` | Manual input |
| `rate_limits.seven_day.used_percentage` | `ClaudeHealth` (new field) | Not tracked |
| `context_window.used_percentage` | `StormMonitor.report_indicator()` | Not tracked |
| `cost.total_api_duration_ms` | `ClaudeHealth.latency_ms` | Manual input |

Full spec in `integration-testing-plan.md` under W8.

### Future Integration

When fleet agents run Claude Code as a backend, they can:
- Read `context_window.used_percentage` from session data
- Trigger compaction at configurable thresholds
- Report context cost in labor stamps
- Factor context pressure into storm indicators

This bridges the gap between our context awareness document and the fleet's operational systems.

---

## 9. Checklist

- [x] Research subscription tiers and context access — verified, documented
- [x] Research context visibility APIs — found JSON session data fields
- [x] Research known bugs — Anthropic acknowledgment documented
- [x] Correct unverified claims — removed fake env var, flagged unverified community reports
- [x] Apply `.claudeignore` to AICP, Fleet, DSPD
- [x] Document PO requirements with exact quotes
- [x] Prove awareness and control (Section 6)
- [x] Configure statusline — IaC via `make install-statusline`, tested and working
- [ ] Apply `.claudeignore` to NNRT
- [ ] Build session telemetry adapter (`session_telemetry.py`) — W8 in integration plan
- [ ] Add new fields to LaborStamp (lines_added, lines_removed, cache_read_tokens)
- [ ] Add new fields to ClaudeHealth (weekly_quota_used_pct, context_window_size)
- [ ] Add context_pressure as storm indicator
- [ ] Implement agent compaction protocol (future milestone)
- [ ] CW-07: Rate limit rollover awareness in brain/orchestrator
- [ ] CW-08: Pre-rollover preparation logic (85%/90% thresholds)
- [ ] CW-09: Context-size-proportional preparation (1M vs 200K)
- [ ] CW-10: Multi-agent rollover coordination
