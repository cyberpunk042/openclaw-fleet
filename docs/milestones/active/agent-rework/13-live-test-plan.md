# Live Test Plan — Agent Rework Verification

**Date:** 2026-03-30
**Status:** Planning
**Part of:** Agent Rework (document 13 of 13)

---

## How to Test

Each test is verified against the live running fleet. Real agents.
Real tasks. Real data flowing. No mocks.

---

## PM Tests

| # | Test | What to Verify |
|---|------|----------------|
| 1 | PM wakes when unassigned tasks exist | Orchestrator sends gateway message, PM heartbeats |
| 2 | PM assigns agent to unassigned task | Task gets agent_name set, assigned_agent_id set |
| 3 | PM sets task metadata | task_type, task_stage, readiness, story_points set |
| 4 | PM sets verbatim requirement | requirement_verbatim populated on task |
| 5 | PM breaks down epic | Subtasks created with parent_task link |
| 6 | PM communicates assignment | Comment posted on task explaining assignment |
| 7 | PM tracks sprint progress | Board memory post with sprint summary |
| 8 | PM handles PO directive | Directive parsed, action taken |
| 9 | PM reads Plane data | Plane sprint visible in PM context |
| 10 | PM resolves blocker | Blocked task gets unblocked or reassigned |

## Fleet-Ops Tests

| # | Test | What to Verify |
|---|------|----------------|
| 11 | fleet-ops wakes on pending approval | Gateway message triggers heartbeat |
| 12 | fleet-ops reads task before approving | Review takes > 30s, references requirement |
| 13 | fleet-ops approves with reasoning | Approval has specific reason, not rubber stamp |
| 14 | fleet-ops rejects with feedback | Rejection has specific actionable feedback |
| 15 | fleet-ops checks methodology compliance | Flags protocol violations |
| 16 | fleet-ops monitors budget | Budget concern triggers alert |
| 17 | fleet-ops handles escalation | Escalation evaluated, action taken |

## Worker Tests

| # | Test | What to Verify |
|---|------|----------------|
| 18 | Worker reads pre-embedded task context | Full data available without MCP call |
| 19 | Worker follows conversation protocol | Asks questions, doesn't produce code |
| 20 | Worker follows analysis protocol | Produces analysis artifact, not solutions |
| 21 | Worker follows investigation protocol | Researches options, doesn't decide |
| 22 | Worker follows reasoning protocol | Produces plan referencing verbatim |
| 23 | Worker follows work protocol | Commits, PR, complete — proper sequence |
| 24 | Worker updates artifact progressively | Artifact grows across cycles |
| 25 | Worker communicates with PM | Posts status, asks questions |

## System Flow Tests

| # | Test | What to Verify |
|---|------|----------------|
| 26 | Full task lifecycle | Create → assign → stage progression → work → review → done |
| 27 | PM assigns → worker works → fleet-ops reviews | Three agents collaborate on one task |
| 28 | Progressive readiness | Task readiness increases: 0 → 30 → 50 → 80 → 99 |
| 29 | Artifact completeness drives readiness | Standards check matches readiness suggestion |
| 30 | Plane ↔ OCMC sync during work | Task state synced between platforms during work |
| 31 | Doctor detects real disease | Agent actually violates protocol, doctor catches it |
| 32 | Teaching delivers real lesson | Agent receives lesson, demonstrates comprehension |
| 33 | Mode change affects behavior | Change work mode, verify agents respond differently |
| 34 | Directive routes to agent | PO posts directive, target agent receives and acts |
| 35 | Inter-agent conversation | PM asks architect for design input, architect responds |

---

## Total: 35 live tests

These are in addition to the 69 milestone verification tests.
Combined: 100+ real verifications of the fleet operating as a team.