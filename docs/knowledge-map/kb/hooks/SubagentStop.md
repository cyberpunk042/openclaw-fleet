# SubagentStop

**Type:** Claude Code Hook (lifecycle event)
**Category:** Agent Teams (fires when a subagent finishes)
**Handler types:** command, http, prompt, agent
**Can block:** YES (can reject subagent output)

## What It Actually Does

Fires when a subagent completes its work and returns results to the parent. The handler receives the subagent's output. Can validate output quality, log completion, or block (reject the output if quality check fails, forcing rework).

## Fleet Use Case: Output Validation + Trail

```
SubagentStop fires (subagent finished)
├── Validate output:
│   ├── Does output match expected format?
│   ├── Quality check on subagent results
│   ├── If issues: exit code 2 → reject, force rework
│   └── If acceptable: pass through
├── Log completion:
│   ├── Trail event: subagent_completed
│   ├── Duration, token cost
│   ├── Output summary for trail
│   └── Update active subagent count
├── Trigger downstream:
│   ├── If review subagent → feed results to fleet-ops
│   ├── If research subagent → feed results to parent task
│   └── If test subagent → feed results to QA
└── Return: {} or exit code 2 (reject)
```

## Why Blocking Matters

SubagentStop can BLOCK — reject the subagent's output. This enables quality gates on subagent work:
- A research subagent that returned shallow results → reject, re-run with higher effort
- A code subagent that introduced security issues → reject, explain why
- A review subagent that rubber-stamped → reject, require deeper analysis

## Relationships

- FIRES ON: subagent completes and returns results
- CAN BLOCK: yes (exit code 2 — reject output, force rework)
- CONNECTS TO: SubagentStart hook (complementary — start/stop pair)
- CONNECTS TO: Agent Teams (teammate completion)
- CONNECTS TO: trail system (trail.subagent.completed event)
- CONNECTS TO: budget system (subagent cost recorded)
- CONNECTS TO: quality standards (output validation)
- TIER: 3 in implementation priority (Agent Teams integration)
