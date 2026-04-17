---
title: "Analysis: Why TK-01 Produces 88 Lines of Low-Value Output"
type: reference
domain: architecture
status: draft
confidence: high
created: 2026-04-11
updated: 2026-04-11
tags: [analysis, context-injection, output-quality, blockers, systemic, contribution, navigator, events, preembed]
epic: E001
sources: []
---

# Analysis: Why TK-01 Produces 88 Lines Instead of 200+

## Summary

TK-01 is the golden path: software-engineer, work stage, 40% progress, expert tier, all contributions received, MVP phase, full injection. This is the SIMPLEST scenario — every feature should be visible. Instead, 88 lines of generic boilerplate. Every feature we built is absent from the output.

This analysis traces each missing piece to its root cause in the code.

---

## Finding 1: Contribution content never appears — marker stripped

### What should happen
The architect's design_input (~15 lines: approach, target files, patterns, constraints) and QA's qa_test_definition (~10 lines: TC-001 through TC-007) should appear INLINE in the task-context.md between "## INPUTS FROM COLLEAGUES" and "### Required Contributions." Expert tier = full content inline.

### What actually happens
The checklist shows "✓ received" but the content blocks are absent. 88 lines instead of 113+ lines.

### Root cause
fleet/core/preembed.py lines 344-347 (now line 344): `build_task_preembed` strips the `<!-- CONTRIBUTIONS_ABOVE -->` marker at the end of the function. The orchestrator's contribution preservation code (fleet/cli/orchestrator.py:714-716) tries to insert `## CONTRIBUTION:` blocks at this marker. The generator's `render_task_scenario` (scripts/generate-validation-matrix.py:286-288) also tries to insert at this marker. Both fail because the marker is already gone by the time they try.

### Production flow
In production, `fleet_contribute()` MCP tool (fleet/mcp/tools.py:3232-3241) calls `append_contribution_to_task_context()` (fleet/core/context_writer.py:88-151) which APPENDS `## CONTRIBUTION:` blocks directly to the existing task-context.md file. The orchestrator's preservation code then extracts these blocks from the EXISTING file and re-inserts them into the NEW preembed output. So the marker stripping means the contribution content can only survive if it's already in the file — new renders always lose the marker.

### Impact
~25 lines of the highest-value content missing. The engineer sees "contributions received ✓" but not WHAT they say. The protocol says "Consume all contributions" but there's nothing to consume.

---

## Finding 2: Knowledge context is a static skill menu — Navigator bypassed

### What should happen
The Navigator (fleet/core/navigator.py:106-170) assembles knowledge-context.md from 3 layers:
1. Knowledge map (90+ KB entries, 13 branches per injection profile)
2. LightRAG graph queries (zero-LLM with pre-extracted keywords)
3. Claude-mem per-agent cross-session memory

For engineer-work intent (docs/knowledge-map/intent-map.yaml:324-336), this means: agent manual, methodology, 4 fleet skills with descriptions, 6 pack skills, 5 commands, 4 fleet tools with purpose, 4 MCP servers, contribution status, standards, context awareness, 2 sub-agents. At opus-1m profile depth, this is ~50-80 lines of curated content.

### What actually happens
The generator (scripts/generate-validation-matrix.py:95-109) hardcodes a 10-line static list: 4 skill names, 2 sub-agent names, 1 MCP line, 1 plugin line. No descriptions, no commands, no standards, no trail, no context awareness, no graph context, no agent memory.

### Root cause
The generator never calls `Navigator.assemble()`. It bypasses the entire knowledge assembly pipeline and substitutes a manually written constant. The Navigator IS wired in the orchestrator (fleet/cli/orchestrator.py:740-770) — it runs every 30 seconds in production. But the generator doesn't use it.

### Impact
~40-70 lines of curated knowledge context missing. The engineer gets a menu of skill names instead of actionable knowledge — tool chains, standards, relevant system descriptions, graph-connected context, past session insights.

---

## Finding 3: heartbeat_context.py calls preembed with wrong parameters — dead code

### What should happen
fleet/core/heartbeat_context.py builds a HeartbeatBundle with pre-computed context. Line 302 calls `build_heartbeat_preembed()` to generate preembed_text for the bundle.

### What actually happens
Lines 302-312 call `build_heartbeat_preembed()` with `messages_count=len(bundle.chat_messages)` and `events_count=len(bundle.domain_events)`. These parameters DO NOT EXIST in the function signature (fleet/core/preembed.py:350-365). The real parameters are `messages: list[dict]` and `events: list[dict]`. TypeError caught by `except Exception: pass`. Bundle's preembed_text is always empty string.

### Root cause
Parameter names changed when the function was refactored. The call site was not updated.

### Impact
The HeartbeatBundle.preembed_text field never contains content. Any code path that uses the bundle's preembed_text (rather than calling build_heartbeat_preembed directly) gets nothing. The orchestrator works around this by calling build_heartbeat_preembed directly, so production heartbeats still work. But the heartbeat_context module is dead code.

---

## Finding 4: Contributions depth status_only and summary never handled

### What should happen
config/tier-profiles.yaml defines `contributions: status_only` (capable) and `contributions: summary` (flagship_local). These should render contribution lists at reduced depth.

### What actually happens
fleet/core/preembed.py line 267: `if contrib_depth == "names_only"` is the only depth check. Everything else falls through to the default `full_inline` path. Capable and flagship_local agents get full_inline contribution lists despite the config.

### Root cause
The depth values `status_only` and `summary` were added to the config but never implemented in the rendering code.

### Impact
Tier adaptation for contributions is broken for 2 of 4 tiers. Capable-tier agents get the same full contribution lists as expert-tier agents. The "don't overwhelm the trainee" principle is violated for this section.

---

## Finding 5: fleet_mode absent from task preembed

### What should happen
The agent should know the current fleet state when working on a task: work_mode, cycle_phase, backend_mode. These affect what the agent CAN do (e.g., work-paused = no new dispatch, crisis-management = only fleet-ops + devsecops active).

### What actually happens
fleet_mode appears in build_heartbeat_preembed (fleet/core/preembed.py:379, cosmetic header line). It is NEVER passed to or rendered by build_task_preembed. The agent working on a task has zero visibility into fleet state.

### Root cause
build_task_preembed (fleet/core/preembed.py:71) has no fleet_mode parameter. The orchestrator's _refresh_agent_contexts passes fleet state to build_heartbeat_preembed but not to build_task_preembed.

### Impact
An agent in work stage doesn't know if the fleet is paused, in crisis mode, or over budget. They can't adapt behavior to fleet-wide conditions.

---

## Finding 6: Confirmed plan is a TODO list in the fixture

### What should happen
The confirmed plan comes from fleet_task_accept comments (fleet/cli/orchestrator.py:620-632). In the reasoning stage, the engineer produces a DESIGN PLAN (architecture, rationale, component relationships, data flow). The plan is submitted via fleet_task_accept which posts it as a comment. The orchestrator loads it and renders it in §6b.

### What actually happens
The generator fixture (scripts/generate-validation-matrix.py:319) hardcodes:
```
1. Create DashboardHealth.tsx component
2. Implement AgentGrid (10 cards, color-coded)
...
7. Tests for TC-001 through TC-007
```
This is an operations TODO list, not a design plan. Per PO directive (wiki/log/2026-04-11-directive-plan-types.md): a plan is what we DELIVER and how we REACH there, not a list of steps.

### Root cause
The fixture was written before the plan types directive was established. The generator doesn't model what a real design plan looks like.

### Impact
TK-01 demonstrates the exact anti-pattern the PO identified. The "confirmed plan" section is ~7 lines of low-value steps instead of ~20-30 lines of architecture rationale, component design, data flow, and constraints.

---

## Finding 7: No WHAT CHANGED events in any scenario

### What should happen
The EventStore (fleet/core/events.py) tracks all fleet events. The orchestrator queries it for unseen events (fleet/cli/orchestrator.py:577-596) and prepends a "## WHAT CHANGED" section to the context. This tells the agent what happened since their last cycle — task status changes, contribution deliveries, PR comments, review decisions.

### What actually happens
The generator passes no events. Zero of 29 scenarios have a WHAT CHANGED section.

### Root cause
The generator doesn't simulate EventStore data. It calls build_task_preembed directly, bypassing the orchestrator's event query logic.

### Impact
The agent has no awareness of what changed between cycles. No continuity. Progress at 40% but no indication of what the first 40% produced or what happened since the last heartbeat.

---

## Finding 8: context_assembly.py has richer data than preembed

### What should happen
There are two assembly paths: preembed.py (orchestrator push, 30s cycle) and context_assembly.py (MCP pull, on-demand). context_assembly (fleet/core/context_assembly.py:35-298) includes: task comments (up to 20), Plane artifact completeness (type, data, missing fields, suggested readiness), related tasks (children, parent, blockers with titles and status), activity history (up to 15 events), skill recommendations. None of this reaches preembed.

### What actually happens
The preembed output has: task fields, stage, readiness/progress, verbatim, protocol, contributions checklist, phase standards, action directive. No comments, no artifact completeness, no related tasks, no activity history, no skill recommendations.

### Root cause
The two paths were built independently. context_assembly.py was designed for MCP tool responses. preembed.py was designed for the orchestrator push path. They never converged.

### Impact
The push path (what agents see every 30s) is significantly poorer than what they'd get from a fleet_read_context call. The promise of "your data is pre-embedded — fleet_read_context NOT needed" is only partially true.

---

## Finding 9: Confirmed plan loading is brittle

### What should happen
The orchestrator loads the confirmed plan from task comments (fleet/cli/orchestrator.py:620-632) to embed in §6b.

### What actually happens
The code searches for comments where `"plan" in content.lower()[:50] and ("fleet_task_accept" in content.lower() or "accepted" in content.lower())`. This is substring matching on an arbitrary 50-char prefix.

### Root cause
No structured format for plan comments. fleet_task_accept posts plans as free-text comments. The loader guesses which comment is the plan based on keywords in the first 50 characters.

### Impact
If the plan comment starts with something other than "plan" in the first 50 chars, or if fleet_task_accept changes its comment format, the plan silently disappears from the context.

---

## Finding 10: The generator doesn't exercise the real pipeline

### What the generator does
scripts/generate-validation-matrix.py creates Task objects with hardcoded CustomFields, calls build_task_preembed() and build_heartbeat_preembed() directly, and hardcodes knowledge-context.md as a static string.

### What the real pipeline does
The orchestrator (fleet/cli/orchestrator.py:434-770) runs _refresh_agent_contexts which:
1. Loads global state from MC
2. Creates TierRenderer from backend_mode
3. Per agent: loads messages, directives, role data from providers
4. Builds heartbeat preembed with events, context awareness
5. Loads rejection feedback from comments
6. Loads confirmed plan from comments
7. Resolves target task for contributions
8. Computes received contribution types from task relationships
9. Queries EventStore for WHAT CHANGED
10. Preserves contribution content from existing files
11. Runs Navigator for knowledge-context.md

The generator skips steps 1, 3, 4 (partially), 8, 9, 10, 11. It creates its own simplified versions of steps 5, 6, 7 with hardcoded data.

### Impact
The generated scenarios don't represent what agents actually see. They represent a partial, simplified, frozen simulation. Any feature that depends on the full pipeline (Navigator, EventStore, contribution preservation, context awareness) is invisible in the scenarios.

---

## Summary: 10 Systemic Issues

| # | Issue | Missing output | Lines lost |
|---|-------|---------------|------------|
| 1 | Contribution content stripped (marker bug) | design_input + qa_test_definition | ~25 |
| 2 | Navigator bypassed in generator | 13-branch knowledge assembly | ~40-70 |
| 3 | heartbeat_context.py dead code | HeartbeatBundle.preembed_text | 0 (workaround exists) |
| 4 | contributions depth unimplemented | status_only, summary | 0 (affects non-expert tiers) |
| 5 | fleet_mode absent from task preembed | fleet state line | ~2 |
| 6 | Confirmed plan fixture is TODO list | design plan content | ~15-20 |
| 7 | No events in scenarios | WHAT CHANGED section | ~5-10 |
| 8 | context_assembly data not in preembed | comments, artifact, related tasks | ~15-20 |
| 9 | Plan loading is brittle | plan may silently disappear | N/A |
| 10 | Generator skips 7 of 11 pipeline steps | everything above compounds | N/A |

**Total missing from TK-01: ~100-145 lines of high-value content.**

Current output: 88 lines. With all issues fixed: ~190-230 lines.

## Relationships

- FEEDS INTO: investigation stage (solution design)
- RELATES TO: [Context Injection Decision Tree](context-injection-tree.md)
- RELATES TO: [Critical Review Findings](critical-review-findings.md)
- RELATES TO: [Directive: Plan Types](../../log/2026-04-11-directive-plan-types.md)
