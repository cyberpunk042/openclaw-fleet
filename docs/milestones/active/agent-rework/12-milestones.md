# Agent Rework Milestones

**Date:** 2026-03-30
**Status:** Planning
**Part of:** Agent Rework (document 12 of 13)

---

## Milestones

### AR-01: Fix preembed — full data, not compressed
Rewrite preembed.py to deliver full context assembly output.
Remove the 300-char compression. Full role data pre-embedded.

### AR-02: Orchestrator wakes PM on unassigned inbox
Detect unassigned inbox tasks → send gateway message to PM session
→ PM heartbeats with full context → PM assigns agents.

### AR-03: Orchestrator wakes fleet-ops on pending approvals
Detect pending approvals → send gateway message to fleet-ops session
→ fleet-ops heartbeats with full context → fleet-ops reviews.

### AR-04: Rewrite PM HEARTBEAT.md
Complete rewrite with methodology awareness, stage management,
task assignment, Plane integration, inter-agent communication.

### AR-05: Rewrite fleet-ops HEARTBEAT.md
Complete rewrite with approval processing, methodology compliance,
quality enforcement, budget monitoring.

### AR-06: Rewrite architect HEARTBEAT.md
Design review, complexity assessment, progressive artifact work.

### AR-07: Rewrite devsecops HEARTBEAT.md
Security review, dependency audit, infrastructure health.

### AR-08: Rewrite worker template HEARTBEAT.md
Stage-aware task handling, progressive artifacts, communication.

### AR-09: Update agent.yaml per agent
Mission, capabilities, model selection per role.

### AR-10: Per-agent CLAUDE.md
Project-specific rules and context per agent role.

### AR-11: Pre-embed Plane data for PM
PM gets Plane sprint data pre-embedded in heartbeat context.

### AR-12: Pre-embed task artifact for workers
Workers get their in-progress task's artifact pre-embedded.

### AR-13: Inter-agent communication patterns
Wire fleet_chat usage into heartbeat flows. Agents actually
communicate about their work.

### AR-14: Standards in agent context
Relevant standards pre-embedded based on current task type.

### AR-15: Live test PM heartbeat
PM wakes, sees unassigned tasks, assigns agents. Verified live.

### AR-16: Live test fleet-ops heartbeat
fleet-ops wakes, processes approval, approves/rejects. Verified live.

### AR-17: Live test worker heartbeat
Worker wakes, follows methodology stage, updates artifact. Verified live.

### AR-18: Live test inter-agent flow
PM assigns → worker works → fleet-ops reviews → done. Full cycle.

### AR-19: Live test progressive work
Task spans 3+ cycles. Artifact grows. Readiness increases. Verified.

### AR-20: Live test Plane integration
Plane issue → OCMC task → agent works → Plane synced. Verified.

---

## Total: 20 milestones

| Category | Count |
|----------|-------|
| Infrastructure fixes | 3 (AR-01 to AR-03) |
| Heartbeat rewrites | 5 (AR-04 to AR-08) |
| Agent config | 2 (AR-09 to AR-10) |
| Data integration | 3 (AR-11 to AR-13) |
| Standards | 1 (AR-14) |
| Live tests | 6 (AR-15 to AR-20) |
| **Total** | **20** |