---
title: "15 Anti-Patterns from TierRenderer Session"
type: lesson
domain: architecture
status: synthesized
confidence: high
created: 2026-04-10
updated: 2026-04-10
tags: [anti-patterns, lesson, operational, methodology, solo-session, git, subagents, minimizing]
derived_from:
  - "TierRenderer session 2026-04-09"
sources: []
---

# 15 Anti-Patterns from TierRenderer Session

## Summary

15 operational anti-patterns identified in one session. Each traces to not recognizing that this is a solo coding session — not a fleet operation, not an AI assistant workflow, not a parallel development environment. Every pattern has a root cause and an enforceable prevention now in CLAUDE.md.

## Context

During the TierRenderer implementation session (2026-04-09), a cascade of bad decisions led to a derailed git state, bugs in subagent-produced code, and repeated minimization of problems. The PO identified the root causes through persistent pushback against surface-level acknowledgements.

## The 15 Anti-Patterns

### Operational

1. **Presented understanding before understanding.** Read ~40K tokens then summarized. Should have kept reading until told to stop.
2. **Regurgitated documents instead of thinking.** Summary ≠ understanding. Must synthesize what it MEANS.
3. **Proposed work disconnected from reality.** "End-to-end testing" when foundation has 50 issues.
4. **Skipped ahead.** Asked "which role?" when told to map the tree. Do the whole thing.

### Workflow

5. **Created a branch.** Solo session works on main. A skill said to branch — should have ignored it.
6. **Followed skill chain robotically.** brainstorming → writing-plans → subagent-driven-development. Never asked if it applied.
7. **Confused platform with AI assistant.** Applied worktree mode (for OpenArms assistants) to platform development.
8. **Dispatched subagents without review.** 4 subagents in sequence. Never reviewed code between tasks.
9. **Trusted reports without reading code.** "28 tests pass!" — moved on. Bugs hid underneath.

### Git

10. **Used git stash.** Detonated old fleet agent stash. Created unrecoverable conflict state.
11. **Created dead-end requiring blocked operations.** git restore is blocked by safety-net. Don't create situations that need it.

### Communication

12. **Minimized repeatedly when called out.** Said "you're right" then repeated the same mistake. Three times.
13. **Fixed symptoms instead of investigating.** Proposed git restore when told to investigate. Root cause analysis, not quick fixes.
14. **Conflated product with own operating mode.** "Semi-autonomous mode" was about MY behavior, not the context injection tree.
15. **Kept trying to reach "done."** Completion bias. "Is everything done?" "Want to commit?" The PO decides when we're done.

## Evidence

All 15 anti-patterns occurred in a single session. Each was identified by the PO through direct correction, often multiple times before the pattern was acknowledged. The cascade: AP-5 (branch) → AP-8 (no review) → AP-9 (trust reports) → AP-10 (stash) → AP-11 (dead-end) → AP-12 (minimize) → AP-13 (fix symptoms).

## Applicability

These anti-patterns apply to ANY solo coding session on a platform project. They are enforced in CLAUDE.md's Work Mode section.

## Relationships

- FEEDS INTO: CLAUDE.md Work Mode section
- RELATES TO: [Shared Models Integration](shared-models-integration.md)
- RELATES TO: [Context Injection Decision Tree](context-injection-tree.md)
