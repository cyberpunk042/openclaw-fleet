# Task: Work stage, full injection, contributions received

**Expected:** Engineer has everything. Follow plan, commit, complete. fleet_read_context NOT needed.

## task-context.md

```
## WHAT CHANGED
- [dispatched] orchestrator: Task dispatched to software-engineer
- [contribution.posted] architect: design_input delivered for task-a1b2
- [contribution.posted] qa-engineer: qa_test_definition delivered for task-a1b2
- [accepted] software-engineer: Plan accepted — DashboardHealth component hierarchy
- [commit] software-engineer: feat(dashboard): scaffold DashboardHealth shell [task:task-a1b]
- [commit] software-engineer: feat(dashboard): implement AgentGrid with StatusCard [task:task-a1b]

# MODE: task | injection: full | model: feature-development | generated: 20:24:15
# Your task data is pre-embedded below. fleet_read_context() only if you need fresh data or a different task.
# FLEET: full-autonomous | execution | claude

# YOU ARE: software-engineer

# YOUR TASK: Add fleet health dashboard
- ID: task-a1b
- Priority: high
- Type: story
- Story Points: 5
- Parent: Epic: Fleet UI Components
- Description: Dashboard with agent grid, task pipeline, storm, budget

# YOUR STAGE: work

# READINESS: 99%
# PROGRESS: 40%

## VERBATIM REQUIREMENT
> Add health dashboard with agent grid, task pipeline, storm indicator, budget gauge

## Current Stage: WORK

Execute the confirmed plan. Stay in scope.

### MUST:
- Execute the plan confirmed in reasoning stage
- Stay within scope — verbatim requirement and confirmed plan only
- Consume all contributions before implementing
- Commit each logical change via fleet_commit
- Complete via fleet_task_complete when done

### MUST NOT:
- Do NOT deviate from the confirmed plan
- Do NOT add unrequested scope
- Do NOT modify files outside the plan's target
- Do NOT skip tests

## CONFIRMED PLAN
**Architecture:** React component hierarchy under DashboardShell.
DashboardHealth is the container component. Four child components receive typed props:
- AgentGrid: agent[] → renders StatusCard per agent (color-coded by lifecycle state)
- TaskPipeline: taskCounts{inbox,progress,review,done} → horizontal segmented bar
- StormIndicator: stormState{severity,active,since} → circular gauge with severity colors
- BudgetGauge: budgetState{pct5h,pct7d} → arc gauge with threshold markers

**Data flow:** useFleetStatus hook polls MC status API every 10s.
Hook returns typed FleetStatus object. DashboardHealth destructures and passes to children.
No prop drilling beyond one level — each child gets exactly the slice it renders.

**Target files:**
- fleet/ui/components/DashboardHealth.tsx (container + 4 children)
- fleet/ui/hooks/useFleetStatus.ts (MC status API poller)
- fleet/ui/types/fleet-status.ts (typed interfaces)

**Patterns:** Observer (useFleetStatus real-time polling), Adapter (MC API → FleetStatus typed interface)
**Constraints:** Existing MC build pipeline. No new dependencies. Must work within DashboardShell layout grid.

**Acceptance criteria mapping:**
- TC-001 → AgentGrid renders 10 StatusCards (verified: agent[].length === 10)
- TC-003 → TaskPipeline segments sum to total (verified: Object.values(counts).reduce === total)
- TC-005 → BudgetGauge shows API % (verified: pct5h from /api/budget)
- TC-007 → Keyboard navigation (verified: tabIndex on all interactive elements)


## INPUTS FROM COLLEAGUES

## CONTRIBUTION: design_input (from architect)

**Approach:** DashboardHealth component in fleet/ui/components/ using React.
- AgentGrid: 10 cards, color-coded by status
- TaskPipeline: horizontal bar chart (inbox/progress/review/done)
- StormIndicator: circular gauge with severity colors
- BudgetGauge: arc gauge with 5h and 7d usage

**Target files:** fleet/ui/components/DashboardHealth.tsx, fleet/ui/hooks/useFleetStatus.ts
**Patterns:** Observer (real-time), Adapter (API → component)
**Constraints:** Existing MC build pipeline. No new deps.

---
## CONTRIBUTION: qa_test_definition (from qa-engineer)

TC-001: AgentGrid shows 10 agent cards | unit | required
TC-002: Agent card color matches status | unit | required
TC-003: TaskPipeline segments sum to total | unit | required
TC-004: StormIndicator correct severity color | unit | required
TC-005: BudgetGauge shows API percentage | integration | required
TC-006: Dashboard refreshes on status change | integration | recommended
TC-007: Keyboard navigation works | e2e | required

---

### Required Contributions
- **design_input** ✓ from architect — *received*
- **qa_test_definition** ✓ from qa-engineer — *received*

## DELIVERY PHASE: mvp
- **tests:** main flows and critical edges
- **docs:** setup, usage, API for public
- **security:** auth, validation, dep audit

## WHAT TO DO NOW
Continue implementation. `fleet_commit()` per logical change.

```

## knowledge-context.md

```
## Software Engineer

**Mission:** Top-tier implementation agent modeled after the PO -- humble, process-respecting, design-pattern-literate, TDD-practicing. Builds FROM architect's design, WITH QA's predefined tests, USING UX's patterns, FOLLOWING DevSecOps' security requirements. Without these inputs, mistakes happen.

**Primary tools:**
- `fleet_read_context()` -- load full task data including contributions
- `fleet_task_accept(plan)` -- confirm approach before implementing
- `fleet_commit(files, message)` -- conventional commits during work stage
- `fleet_task_complete(summary)` -- triggers full review chain (push -> PR -> review -> approval)
- `fleet_request_input(task_id, role, question)` -- ask colleagues for missing contributions

## Stage 5: WORK

**Purpose:** Execute the confirmed plan. Follow the plan, stay in scope.

**MUST DO:** Execute confirmed plan, follow conventions (conventional commits, testing), stay within scope (verbatim + plan), call fleet_read_context first, fleet_task_accept with plan, fleet_commit per change, fleet_task_complete when done
**MUST NOT:** Deviate from plan, add unrequested scope, modify files outside plan, skip tests
**REQUIRED TOOL SEQUENCE:** fleet_read_context → fleet_task_accept → fleet_commit (1+) → fleet_task_complete

### Tools
| Tool | Why |
|------|-----|
| fleet_read_context | Load task context (FIRST) |
| fleet_task_accept | Confirm plan (required before commits) |
| fleet_commit | Commit each logical change (stages 2-5) |
| fleet_task_complete | Complete: push → PR → MC → approval → IRC → ntfy → Plane |
| fleet_task_progress | Report progress with progress_pct |
| fleet_contribute | Post contribution to another agent's task |
| fleet_alert | Raise quality/security/architecture concern |
| fleet_pause | Report blocker |
| fleet_escalate | Escalate to PO |

### Skills
| Skill | Why |
|-------|-----|
| feature-implement | Implementation workflow (engineer) |
| feature-test | Write and run tests (QA, engineer) |
| test-driven-development (Superpowers) | TRUE TDD: test first, watch fail, code, watch pass |
| verification-before-completion (Superpowers) | Ensure actually fixed before completing |
| requesting-code-review (Superpowers) | Pre-review checklist before fleet_task_complete |
| using-git-worktrees (Superpowers) | Parallel development (engineer, devops) |
| fleet-communicate | Communication guidance |

### Commands
| Command | Why |
|---------|-----|
| /debug | When stuck on implementation issues |
| /diff | Review own changes before committing |
| /fast on | Speed up routine implementation |
| /compact | When context approaching 70% |
| /batch | Parallel changes across multiple files/worktrees |
| /simplify | Post-implementation quality pass (3 parallel agents) |

### MCP Servers
| Server | Why |
|--------|-----|
| filesystem | Read/write code files |
| github | PR management, code search |
| playwright | UI testing (QA, engineer, UX) |
| Context7 | Library docs during implementation |
| pytest-mcp | Test failures, coverage, debug trace |

### Plugins
| Plugin | Why |
|--------|-----|
| pyright-lsp | Continuous type diagnostics during coding |
| safety-net | Block destructive commands before execution |
| security-guidance | Detect insecure code patterns as written |
| claude-mem | Recall past implementations of similar features |
| context7 | Up-to-date library APIs during implementation |

---


**Contributions:** Check fleet_read_context for contribution status (all received)

**Context awareness:** Monitor context % and rate limit %.
Use /context for visual grid. Use /usage for rate limit status.
Compact at 70% context. Strategic compaction at 85% rate limit.

## Related Systems
- **S01 methodology**: uses fleet_task_accept
- **S01 methodology**: gates fleet_commit (stages 2-5)
- **S13 labor**: stamps fleet_task_complete (full stamp)
- **S15 challenge**: invoked_by fleet_task_complete (after work)

## Relevant Systems (from knowledge graph)
- **S06 agent-lifecycle** (agent_lifecycle.py, agent_roles.py, memory_structure.py) → connects to S02, S07, S12
- **S21 agent-tooling** (skill_enforcement.py) → connects to S08, S09
- **S18 notifications** (notification_router.py, cross_refs.py, urls.py) → connects to S04, S07
```
