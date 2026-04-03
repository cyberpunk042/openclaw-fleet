# System 11: Storm Prevention — Automatic Graduated Response

**Type:** Fleet System
**ID:** S11
**Files:** storm_monitor.py (~450 lines), storm_integration.py (~400 lines), storm_analytics.py (~280 lines), incident_report.py (~310 lines)
**Total:** 1,440 lines
**Tests:** 90 (highest test count of any system)

## What This System Does

Monitors 9-10 indicators for fleet misbehavior (void sessions, session bursts, budget climbs, gateway duplication, context pressure). Evaluates severity on 5 levels with confirmation windows (sustained signals, not spikes). Applies graduated automatic response from monitoring to full fleet halt. Circuit breakers trip per-agent and per-backend. Diagnostic snapshots captured on WARNING+. Post-incident reports generated after storms clear.

Built after the March catastrophe: 15 bugs combined into a storm that burned through the weekly quota in hours. Gateway duplication spawned multiple instances. Void sessions consumed tokens producing nothing.

## 9-10 Indicators

| # | Indicator | Trigger | Confirmation | March Cause? |
|---|-----------|---------|-------------|-------------|
| 1 | session_burst | >10 sessions/min | 60s | Yes |
| 2 | fast_climb | Budget +5% in 10min | 300s | Yes |
| 3 | void_sessions | >50% void rate | 120s | Yes |
| 4 | dispatch_storm | Too many dispatches | 30s | No |
| 5 | cascade_depth | Task-creates-task chains too deep | 30s | No |
| 6 | agent_thrashing | Wake with no work repeatedly | 120s | No |
| 7 | error_storm | High error rate | 60s | No |
| 8 | gateway_duplication | Multiple gateway processes | IMMEDIATE (0s) | YES (root cause) |
| 9 | context_pressure | Context ≥70% from session telemetry | from W8 | No |
| 10 | aggregate_context | Fleet-wide context vs remaining quota | designed, not built | No |

Each indicator: reported via report_indicator(name, value), has confirmation window (sustained before confirmed), exception: gateway_duplication is IMMEDIATE.

## 5 Severity Levels

| Severity | Indicators | Dispatch | Action |
|----------|-----------|----------|--------|
| CLEAR | 0 confirmed | Normal | Normal operation |
| WATCH | 1 confirmed | Normal | Logging only |
| WARNING | 2+ confirmed | Max 1 | Diagnostic snapshot, IRC #alerts |
| STORM | 3+ OR critical combo | 0 | Alert PO (ntfy), no new dispatch |
| CRITICAL | fast_climb + session_burst | HALT cycle | Urgent ntfy PO, fleet FROZEN |

Special: fast_climb + session_burst together → CRITICAL (the March pattern).

## De-Escalation (Slower Than Escalation)

| Transition | Indicator-Free Period |
|-----------|---------------------|
| CRITICAL → STORM | 10 minutes |
| STORM → WARNING | 10 minutes |
| WARNING → WATCH | 15 minutes |
| WATCH → CLEAR | 30 minutes |

Slow de-escalation prevents oscillation (storm → clear → storm → clear).

## Circuit Breakers

Per-agent AND per-backend:
- CLOSED → (3 failures) → OPEN → (cooldown) → HALF_OPEN → (success) → CLOSED
- Cooldown doubles on repeated trips (5min agent, 2min backend, max 1hr)
- Used by backend_router for fallback decisions
- Both breakers OPEN → queue task, no dispatch

## Diagnostic Snapshots

Captured on WARNING+: severity, active indicators, session counts, void rate, agent states, budget mode, fleet state. Persisted to disk (50-file cap). Available for post-incident analysis.

## Post-Incident Reports

Generated when storm severity drops to CLEAR: peak severity, duration, active indicators, root cause analysis, response timeline, estimated cost impact, void session stats, prevention recommendations. Posted to board memory tagged [storm, incident, postmortem].

## Relationships

- RUNS IN: orchestrator.py pre-check (every cycle)
- GATES: dispatch decisions (severity → max dispatch)
- PRODUCES: diagnostic snapshots (persisted to disk)
- PRODUCES: incident reports (posted to board memory)
- CONNECTS TO: S07 orchestrator (pre-check gate — CRITICAL halts cycle)
- CONNECTS TO: S12 budget (fast_climb indicator from budget readings)
- CONNECTS TO: S14 router (circuit breakers per backend)
- CONNECTS TO: S19 session (context_pressure indicator from session telemetry)
- CONNECTS TO: S18 notifications (storm alerts → IRC #alerts + ntfy)
- CONNECTS TO: gateway_guard.py (gateway duplication detection)
- CONNECTS TO: StopFailure hook (rate_limit → storm indicator)
- NOT YET IMPLEMENTED: session telemetry feeding indicators (W8 adapter → to_storm_indicators), aggregate_context indicator (#10), auto-posting incident reports, rule-based prevention recommendations, de-escalation speed tuning

## For LightRAG Entity Extraction

Key entities: StormMonitor (9-10 indicators), StormSeverity (5 levels), CircuitBreaker (per-agent, per-backend), DiagnosticSnapshot, IncidentReport, confirmation_window.

Key relationships: Indicator FIRES when threshold breached. Confirmation window VALIDATES sustained signal. Severity EVALUATED from confirmed count. Response GRADUATED from WATCH to CRITICAL. Circuit breaker TRIPS on failures. Storm GATES dispatch. Incident report GENERATED on de-escalation to CLEAR.

Historical context: built to prevent the March 2026 catastrophe from repeating. Gateway duplication was root cause — now IMMEDIATE indicator.
