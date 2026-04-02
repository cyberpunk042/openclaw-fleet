# Methodology Manual — Per-Stage Tool/Skill/Command Recommendations

**Part of:** Fleet Knowledge Map → Methodology Manual branch
**Purpose:** For each methodology stage, what tools, skills, commands,
and plugins are relevant. Drives the intent-map injection logic.
**Source:** stage_context.py, analysis-01 to analysis-05

---

## Stage 1: CONVERSATION

**Purpose:** Understand the requirement. Ask questions. Extract knowledge from PO.

**MUST DO:** Discuss with PO, ask specific questions, identify gaps, propose understanding
**MUST NOT:** Write code, commit, create PRs, produce finished deliverables
**CAN PRODUCE:** Questions in comments, draft proposals, WIP analysis (marked as draft)
**ADVANCE WHEN:** PO confirms understanding, verbatim requirement populated, no open questions

### Tools
| Tool | Why |
|------|-----|
| fleet_read_context | Load task + project context |
| fleet_chat | Communicate with PO and colleagues |
| fleet_escalate | If requirements are unclear after discussion |

### Skills
| Skill | Why |
|-------|-----|
| fleet-communicate | Know which surface to use for which message |
| idea-capture | Structure raw PO input into idea document |
| brainstorming (Superpowers) | Socratic design refinement before ANY code |

### Commands
| Command | Why |
|---------|-----|
| /context | Before reading large codebases for context |

### MCP Servers
| Server | Why |
|--------|-----|
| (none beyond fleet) | Conversation is about understanding, not tools |

---

## Stage 2: ANALYSIS

**Purpose:** Examine what exists. Read codebase, architecture, dependencies.

**MUST DO:** Read and examine codebase, produce analysis document with file references, present findings to PO
**MUST NOT:** Produce solutions (that's reasoning), write implementation code
**CAN PRODUCE:** Analysis documents, current state assessments, gap analysis, dependency mapping
**ADVANCE WHEN:** Analysis document exists, PO reviewed findings, implications clear

### Tools
| Tool | Why |
|------|-----|
| fleet_read_context | Full task context |
| fleet_artifact_create | Create analysis_document artifact |
| fleet_commit | Commit analysis document (stages 2-5 allowed) |
| fleet_chat | Discuss findings with colleagues |

### Skills
| Skill | Why |
|-------|-----|
| pm-assess | Project state assessment |
| quality-audit | Comprehensive quality check |
| quality-debt | Identify technical debt |
| architecture-review | Architecture completeness check |
| fleet-communicate | Communication guidance |
| openclaw-health | Fleet health assessment (fleet-ops) |
| openclaw-fleet-status | Operational status (fleet-ops) |

### Commands
| Command | Why |
|---------|-----|
| /context | Before heavy codebase reads |
| /diff | Review existing changes |
| /plan | Enter read-only exploration mode |

### MCP Servers
| Server | Why |
|--------|-----|
| filesystem | Read codebase files |
| github | Search code, view PRs, check Actions |
| Context7 | Library/framework documentation lookup |
| pytest-mcp | Coverage analysis, test history |

### Plugins
| Plugin | Why |
|--------|-----|
| pyright-lsp | Type diagnostics while reading Python code |
| claude-mem | Recall past analysis of same codebase |

---

## Stage 3: INVESTIGATION

**Purpose:** Research what's possible. Explore multiple options.

**MUST DO:** Research solutions, explore MULTIPLE options, cite sources, present findings to PO
**MUST NOT:** Decide on an approach (that's reasoning), write implementation code
**CAN PRODUCE:** Research findings, option comparisons with tradeoffs, technical explorations
**ADVANCE WHEN:** Research document exists with multiple options, PO reviewed, enough info to decide

### Tools
| Tool | Why |
|------|-----|
| fleet_read_context | Full task context |
| fleet_artifact_create | Create investigation_document artifact |
| fleet_artifact_update | Update findings as research progresses |
| fleet_commit | Commit research document |
| fleet_chat | Discuss options with colleagues |
| fleet_request_input | Request expert input from specific role |

### Skills
| Skill | Why |
|-------|-----|
| infra-search | Evaluate infrastructure options |
| infra-security | Security investigation (devsecops) |
| fleet-security-audit | Security review of code/infra/supply chain |
| quality-performance | Performance investigation |
| fleet-communicate | Communication guidance |
| systematic-debugging (Superpowers) | 4-phase root cause for bugs |

### Commands
| Command | Why |
|---------|-----|
| /debug | Systematic troubleshooting for bugs |
| /plan | Read-only exploration mode |
| /context | Before heavy research reads |
| /security-review | Branch vulnerability analysis (devsecops) |

### MCP Servers
| Server | Why |
|--------|-----|
| filesystem | Read codebase for research |
| github | Search code, explore PRs and issues |
| Context7 | Library/framework docs for option evaluation |
| Trivy | Vulnerability scanning (devsecops) |
| Semgrep | Code pattern analysis (devsecops) |
| playwright | Web research, UI investigation (QA, UX) |

### Plugins
| Plugin | Why |
|--------|-----|
| pyright-lsp | Type analysis during code investigation |
| claude-mem | Recall past research on similar topics |
| context7 | Up-to-date library documentation |

---

## Stage 4: REASONING

**Purpose:** Plan your approach. Create implementation plan referencing verbatim.

**MUST DO:** Decide approach from requirements + analysis + investigation, produce plan referencing verbatim, specify target files, map criteria to steps, present to PO for confirmation
**MUST NOT:** Start implementing, commit code
**CAN PRODUCE:** Implementation plans with file/component references, design decisions, task breakdown, criteria mapping
**ADVANCE WHEN:** Plan exists referencing verbatim, target files specified, PO confirmed, readiness 99

### Tools
| Tool | Why |
|------|-----|
| fleet_read_context | Full task context |
| fleet_task_accept | Submit plan for task (triggers plan_quality check) |
| fleet_artifact_create | Create plan artifact |
| fleet_commit | Commit plan document |
| fleet_gate_request | Request PO gate approval at readiness 90% |
| fleet_task_create | Break down into subtasks if needed |
| fleet_request_input | Request contributions from specialists |

### Skills
| Skill | Why |
|-------|-----|
| architecture-propose | Propose buildable architecture (architect) |
| feature-plan | Plan changes for features |
| pm-plan | Create project plan with milestones (PM) |
| fleet-plan | Break epic into sprint tasks with dependencies (PM) |
| writing-plans (Superpowers) | 2-5 min tasks with exact file paths + verification |
| brainstorming (Superpowers) | Socratic refinement before committing to approach |
| fleet-communicate | Communication guidance |

### Commands
| Command | Why |
|---------|-----|
| /plan | Enter plan mode for structured planning |
| /branch | Explore alternative approaches without losing context |
| /context | Check context before heavy planning session |
| /effort high | Set high effort for architecture decisions |

### MCP Servers
| Server | Why |
|--------|-----|
| filesystem | Verify approach against codebase |
| github | Check related PRs, architecture decisions |
| Context7 | Verify library APIs for planned approach |
| sequential-thinking | Structured step-by-step reasoning (architect) |

### Plugins
| Plugin | Why |
|--------|-----|
| pyright-lsp | Verify type compatibility of planned approach |
| claude-mem | Recall past decisions on similar designs |
| adversarial-spec | Multi-LLM debate for spec refinement (architect) |

---

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
| foundation-docker | Containerization (devops) |
| foundation-ci | CI/CD pipeline (devops) |
| ops-deploy | Deployment (devops) |
| scaffold | Project structure (architect) |
| fleet-review | 7-step review checklist (fleet-ops) |
| fleet-test | Run + analyze tests for review (QA) |
| fleet-sprint | Sprint lifecycle management (PM) |
| fleet-security-audit | Security review (devsecops) |
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
| /loop | Monitoring checks during deployment (devops) |
| /security-review | Branch vulnerability scan before completion (devsecops) |

### MCP Servers
| Server | Why |
|--------|-----|
| filesystem | Read/write code files |
| github | PR management, code search |
| playwright | UI testing (QA, engineer, UX) |
| docker | Container operations (devops, devsecops) |
| Context7 | Library docs during implementation |
| pytest-mcp | Test failures, coverage, debug trace |
| Trivy | Vulnerability scanning (devsecops) |
| Semgrep | Code pattern scanning (devsecops) |
| Plane MCP | Sprint management (PM) |

### Plugins
| Plugin | Why |
|--------|-----|
| pyright-lsp | Continuous type diagnostics during coding |
| safety-net | Block destructive commands before execution |
| security-guidance | Detect insecure code patterns as written |
| claude-mem | Recall past implementations of similar features |
| context7 | Up-to-date library APIs during implementation |
| codex-plugin-cc | Adversarial review before completion (fleet-ops, devsecops) |

---

## Cross-Stage Connections

| From Stage | To Stage | Via |
|------------|----------|-----|
| CONVERSATION → ANALYSIS | PO confirms understanding | readiness increase |
| ANALYSIS → INVESTIGATION | Findings need research | readiness increase |
| INVESTIGATION → REASONING | Options need decision | readiness increase |
| REASONING → WORK | PO confirms plan | readiness = 99, gate approval |
| WORK → REVIEW | Agent completes | fleet_task_complete, task_progress = 70 |
| REVIEW → DONE | Fleet-ops approves | fleet_approve, task_progress = 90→100 |
| REVIEW → REGRESSION | Fleet-ops rejects | readiness drops, stage may revert |
