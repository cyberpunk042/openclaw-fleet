# Fleet Milestone Plans

## Workstreams

| # | Workstream | Doc | Milestones | Priority |
|---|-----------|-----|------------|----------|
| 1 | [Standards & Discipline](standards-and-discipline.md) | Conventional commits, changelogs, coding standards | M44-M47 | **Immediate** |
| 2 | [Skills Ecosystem](skills-ecosystem.md) | OpenClaw + OCMC skills, packs, fleet skills | M48-M52 | **High** |
| 3 | [Observability & Channels](observability-and-channels.md) | Control UI, WS monitor, external channels | M53-M56 | **High** |
| 4 | [Navigability & Traceability](navigability-and-traceability.md) | Commit↔task linking, smart refs, trace tool | M57-M60 | **Medium** |

## Recommended Execution Order

### Phase 1: Foundation Standards (M44-M47)
Do this FIRST — it affects everything that follows. Every subsequent milestone
produces commits and tasks that should follow these standards.

### Phase 2: Visibility (M53-M54)
Control UI documentation + WS event monitor. Low effort, high value.
These are already running — just need documentation and a CLI wrapper.

### Phase 3: Skills (M48-M50)
Inventory what exists, register packs, install useful skills.
This makes agents more capable before we send them on real missions.

### Phase 4: Traceability (M57-M58)
Commit↔task linking and smart references.
This ties the standards from Phase 1 to the task system.

### Phase 5: Deep Integration (M51-M52, M55-M56, M59-M60)
Fleet-specific skills, channel setup, unified dashboard, trace tool.
These build on everything above.

## Completed Milestones

| # | Milestone | Status |
|---|-----------|--------|
| M38 | Provisioning + E2E test | Done |
| M39 | Autonomous task execution | Done |
| M40 | Observation & interaction tools | Done |
| — | Infrastructure hardening | Done |
| — | Project workspace strategy (worktrees) | Done |

## Dependencies

```
M44 (conventional commits) ← everything after this
M45 (changelog) ← M44
M46 (standards) ← M44
M47 (frequent commits) ← M44

M48 (skill inventory) ← nothing
M49 (register packs) ← M48
M50 (install skills) ← M49
M51 (fleet skills) ← M46, M50
M52 (skill-agent mapping) ← M50

M53 (control UI) ← nothing
M54 (WS monitor) ← M53
M55 (external channel) ← M54
M56 (unified dashboard) ← M53, M55

M57 (commit↔task) ← M44
M58 (smart links) ← M57
M59 (trace tool) ← M57
M60 (cross-repo refs) ← M57, M58
```