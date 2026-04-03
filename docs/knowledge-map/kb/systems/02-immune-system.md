# System 02: Immune System — Disease Detection, Prevention, and Response

**Type:** Fleet System
**ID:** S02
**Files:** doctor.py (417 lines), behavioral_security.py (196 lines), self_healing.py (133 lines)
**Total:** 746 lines
**Tests:** 50+

## What This System Does

Observes agent behavior, detects disease patterns, and responds automatically. AI agents are "sick by default" — LLMs produce plausible output, not correct output. The doctor runs HIDDEN from agents every 30 seconds. Agents experience consequences (teaching, compaction, pruning) but never see the detection machinery. This prevents gaming — if agents knew what the doctor looks for, they'd optimize to pass checks rather than doing good work.

The PO's insight: "seeing the pattern does not break the pattern, it's forging the right path multiple times that does."

## Three Lines of Defense

### Line 1: Structural Prevention (before disease appears)

Make correct behavior the EASY path. Agents don't need willpower — the system guides them.

- **Stage-gated tool access** — fleet_commit BLOCKED in non-work stages (tools.py, PreToolUse hook)
- **Verbatim anchoring** — PO's exact words in EVERY context injection (can't lose the requirement)
- **Contribution requirements as gates** — can't skip to work without architect design, QA tests, DevSecOps review (not yet implemented)
- **Autocomplete chain engineering** — data ordered so correct behavior is the natural continuation

### Line 2: Detection (when disease appears despite prevention)

The doctor runs in orchestrator Step 2 every cycle. For each active task with an assigned agent:

| Detection | What It Catches | Severity | Signal |
|-----------|----------------|----------|--------|
| `detect_protocol_violation` | Work tools called in wrong stage | MEDIUM | tool_calls outside work stage |
| `detect_laziness` | Fast completion (<2min/SP) or partial criteria (<80% met) | MEDIUM/HIGH | time vs SP, criteria coverage |
| `detect_stuck` | No activity for 60 minutes | LOW | minutes since last action |
| `detect_correction_threshold` | 3+ corrections on same issue | HIGH | correction_count in AgentHealth |

**7 detections NOT YET IMPLEMENTED:** abstraction (agent's terms vs PO's verbatim), code_without_reading (tool call order — edit before read), scope_creep (committed files vs plan's target_files), cascading_fix (fix→break→fix chain), context_contamination (patterns across compaction), not_listening (same correction repeated), compression (task scope vs agent's plan scope).

### Line 3: Correction (after detection)

Response decision tree:
```
Already in lesson? → NONE (don't pile on)
3+ corrections?    → PRUNE (model is wrong, not the detail)
Critical severity? → PRUNE
High + repeat?     → PRUNE
Stuck?             → FORCE_COMPACT (context overload suspected)
Medium/Low?        → TRIGGER_TEACHING (adapted lesson)
```

| Action | What Happens |
|--------|-------------|
| TEACH | Adapted lesson injected via gateway. Agent must complete exercise. 3 attempts before prune. |
| FORCE_COMPACT | Context stripped via gateway sessions.compact. Agent continues lean. |
| PRUNE | Session killed via gateway sessions.delete. Fresh session on next heartbeat. All context lost. |
| ESCALATE | Alert PO via ntfy. Human decides. |

## Behavioral Security Scanner (Step 1, BEFORE doctor)

10 regex patterns for: credential exfiltration, DB destruction, security disable, permission escalation, supply chain attacks. Critical findings set `security_hold` on task (blocks approval — only DevSecOps or PO can clear). Human directives are flagged but NEVER blocked — PO always has authority.

## Self-Healing (Step 8, AFTER everything else)

Detects operational issues: stale in-progress tasks, stale reviews, unassigned inbox, offline agents with work, stale dependencies. Creates tasks or escalates — NEVER modifies data directly.

## AgentHealth Profiles

Per-agent health profiles PERSIST across orchestrator cycles: correction_count, total_lessons, total_prunes, last_disease, is_in_lesson, is_pruned. This enables cumulative pattern detection — an agent that's been corrected twice is closer to pruning than a fresh agent.

## DoctorReport Output

Every cycle produces a DoctorReport consumed by the orchestrator:
- `detections` — what was found
- `interventions` — what to do about it
- `agents_to_skip` — don't dispatch to these agents (they're being treated)
- `tasks_to_block` — don't dispatch these tasks (they're flagged)

## Relationships

- RUNS IN: orchestrator.py Step 1 (security) + Step 2 (doctor) + Step 8 (self-healing)
- PRODUCES: DoctorReport → consumed by orchestrator dispatch gate
- TRIGGERS: teaching.py (TRIGGER_TEACHING → adapted lesson with exercises)
- USES: gateway_client.py (inject_content for lessons, force_compact, prune_agent)
- CONNECTS TO: S01 methodology (protocol violations from stage system)
- CONNECTS TO: S03 teaching (treatment arm — lessons, exercises, verification)
- CONNECTS TO: S04 event bus (disease.detected events emitted)
- CONNECTS TO: S06 agent lifecycle (AgentHealth profiles, prune/regrow)
- CONNECTS TO: S07 orchestrator (Step 2 every cycle, DoctorReport gates dispatch)
- CONNECTS TO: S13 labor (laziness detection uses SP vs time from LaborStamp)
- CONNECTS TO: S15 challenge (challenge analytics → teaching signals for repeated failures)
- CONNECTS TO: PreToolUse hook (structural prevention — Line 1)
- CONNECTS TO: PostToolUse hook (trail records tool calls — doctor can analyze patterns)
- CONNECTS TO: safety-net plugin (Line 1 — destructive command prevention)
- HIDDEN FROM: agents (they don't know about the doctor — prevents gaming)
- NOT YET IMPLEMENTED: 7 of 11 disease detections, contribution-related diseases (siloed_work, synergy_bypass), readiness regression on disease detection

## For LightRAG Entity Extraction

Key entities: Doctor, DoctorReport, Detection, Intervention, AgentHealth, Severity (LOW/MEDIUM/HIGH/CRITICAL), ResponseAction (NONE/MONITOR/FORCE_COMPACT/TRIGGER_TEACHING/PRUNE/ESCALATE_TO_PO), behavioral_security, security_hold, self_healing.

Key relationships: Doctor DETECTS diseases. Doctor PRODUCES DoctorReport. Orchestrator CONSUMES DoctorReport. Teaching TREATS detected diseases. Gateway EXECUTES interventions (inject/compact/prune). AgentHealth PERSISTS across cycles. Security scanner SETS security_hold. Self-healing CREATES remediation tasks.

11 disease categories: deviation, laziness, confident_but_wrong, protocol_violation, abstraction, code_without_reading, scope_creep, cascading_fix, context_contamination, not_listening, compression. 4 implemented. 7 pending.
