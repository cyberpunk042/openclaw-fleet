# Tools System — Full Capability Map Per Role

**Date:** 2026-04-07
**Status:** Analysis — mapping the REAL scope from fleet-elevation specs
**Part of:** [tools-system-session-index.md](tools-system-session-index.md)
**Sources:** fleet-elevation/05-14 (per-role specs), fleet-elevation/24 (tool call trees), fleet-elevation/15 (synergy), fleet-elevation/23 (strategic calls)

---

## Architecture — Foundation + Infrastructure + Role Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 0: FOUNDATION (exists — gateway, MCP framework, event system) │
│                                                                      │
│  Gateway (OpenArms/OpenClaw)  MCP Server Framework (FastMCP)        │
│  Event System (CloudEvents)   Context System (preembed + assembly)   │
│  Methodology System (stages)  Immune System (doctor + teaching)      │
│  ChainRunner + EventChain     Skill Loading (gateway scanner)        │
│  Plugin System                Sub-Agent System                       │
│  CRON System                  Hook System                            │
│  Session Management           Budget/Storm/Lifecycle                 │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────┐
│ LAYER 1: GENERIC INFRASTRUCTURE (shared across all agents)          │
│                                                                      │
│  GENERIC TOOLS (30 fleet MCP tools — fleet_commit, fleet_chat, etc.) │
│  GENERIC SKILLS (methodology-wide: brainstorming, TDD, plans, etc.)  │
│  GENERIC PLUGINS (claude-mem, safety-net)                            │
│  GENERIC DIRECTIVES (anti-corruption, context awareness)             │
│  GENERIC CHAINS (tool trees — one call = propagation to 6 surfaces)  │
│                                                                      │
│  × PER-METHODOLOGY-STAGE (what's available/recommended at each stage)│
│    conversation: brainstorming, questions, NO code tools              │
│    analysis: filesystem, systematic-debugging, NO solution tools      │
│    investigation: web research, adversarial-spec, context7            │
│    reasoning: writing-plans, fleet_task_accept, fleet_task_create     │
│    work: TDD, fleet_commit, fleet_task_complete, verification        │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────┐
│ LAYER 2: ROLE-SPECIFIC (unique per agent)                           │
│                                                                      │
│  ROLE TOOLS (MCP servers + role-specific group calls)                │
│  ROLE SKILLS (40+ per role, stage-specific)                          │
│  ROLE PLUGINS (context7, superpowers, pr-review-toolkit, etc.)       │
│  ROLE DIRECTIVES (contribution model, boundaries, quality bars)      │
│  ROLE CHAINS (role-specific group calls with trees)                  │
│  ROLE CRONs (scheduled operations per role)                          │
│  ROLE SUB-AGENTS (delegation capabilities per role)                  │
│  ROLE HOOKS (quality enforcement, security patterns per role)        │
│  ROLE STANDING ORDERS (autonomous authority per role)                 │
│                                                                      │
│  × PER-METHODOLOGY-STAGE (role-specific at each stage)               │
│    architect at analysis: codebase examination with pattern focus     │
│    QA at reasoning: test predefinition with structured criteria       │
│    engineer at work: implementation with contribution consumption     │
│    PM at all stages: manages OTHERS' stages, not own                 │
│                                                                      │
│  + SECONDARY ROLE (subset of another role's capabilities)            │
│  + BACKUP ROLE (can cover for offline colleague on basics)           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Per-Role Capability Map

### PROJECT MANAGER (fleet-elevation/05)

**Mission:** Conductor — orchestrates who contributes what and when. Drives the board. If PM doesn't act, nothing moves.

**Existing generic tools used:** fleet_read_context, fleet_task_create, fleet_chat, fleet_gate_request, fleet_escalate, fleet_alert, fleet_agent_status, fleet_artifact_create, fleet_phase_advance, fleet_plane_status, fleet_plane_sync

**Role-specific MCP servers:** github (PR monitoring), plane MCP (sprint management)

**Role-specific plugins:** plannotator (visual plan annotation)

**Role-specific group calls NEEDED (don't exist):**

| Group Call | What It Would Do (tree) |
|-----------|------------------------|
| pm_sprint_standup | Aggregate sprint state (tasks by status, velocity, blockers) → format standup report → post to board memory [sprint] → IRC #sprint → Plane cycle comment → trail |
| pm_epic_breakdown | Read epic → evaluate scope → create N subtasks with dependencies, types, agents, stages, readiness → post breakdown summary on parent → Plane issue linking → trail |
| pm_contribution_check | For a task entering work: check synergy-matrix → verify all required contributions received → if missing: create contribution tasks or flag gaps → update task readiness → trail |
| pm_gate_route | Task reaches threshold → package summary (plan status, contribution status, readiness) → route to PO with recommendation → ntfy + IRC #gates → trail |
| pm_blocker_resolve | Read blocker details → evaluate options (reassign, split, remove dep, escalate) → execute resolution → notify affected agents → trail |

**Role-specific skills NEEDED (from fleet-elevation/05 responsibilities):**

| Skill | Stage | What It Teaches |
|-------|-------|----------------|
| task-triage | all | How to evaluate unassigned tasks: set ALL fields (type, stage, readiness, SP, agent, verbatim, phase), identify dependencies |
| epic-breakdown | reasoning | How to decompose epics: identify subtasks, set dependencies, assign agents, estimate, set stages |
| sprint-planning | all | How to plan sprints: capacity assessment, velocity estimation, goal setting, risk identification |
| backlog-grooming | all | How to groom backlogs: re-estimate, re-prioritize, identify stale items, prepare for PO |
| po-communication | all | How to communicate with PO: filter noise, summarize, highlight decisions needed, prepare context |
| contribution-orchestration | reasoning | How to ensure all required contributions are received before work stage |
| stage-progression-oversight | all | How to monitor task stages: stalled tasks, missing contributions, readiness not progressing |
| blocker-resolution | all | How to resolve blockers: reassign, split, remove deps, escalate — never >2 active blockers |

**Role-specific CRONs NEEDED:**
- Daily standup summary
- Backlog grooming (periodic)
- Sprint boundary operations
- Plane scan (when connected, fully autonomous mode)

**Role-specific sub-agents:** Likely minimal — PM's work is coordination, not delegation to sub-agents. But could use a sprint-analyzer sub-agent for data aggregation.

**Secondary role:** None primary. PM coordinates, doesn't implement.

---

### FLEET-OPS (fleet-elevation/06)

**Mission:** Quality guardian — owns reviews, approvals, methodology compliance, fleet health. Board lead.

**Existing generic tools used:** fleet_read_context, fleet_approve, fleet_alert, fleet_escalate, fleet_chat, fleet_agent_status

**Role-specific MCP servers:** github (PR review, CI status)

**Role-specific plugins:** pr-review-toolkit (6 parallel review sub-agents)

**Role-specific group calls NEEDED:**

| Group Call | What It Would Do (tree) |
|-----------|------------------------|
| ops_real_review | Read task → read verbatim → read PR → read trail → check methodology stages → check contributions → check phase standards → check PO gates → produce structured review decision → fleet_approve with specifics → trail |
| ops_board_health_scan | Scan all tasks → identify stuck (>48h), stale reviews (>24h), offline agents with work, blocker accumulation, stale contributions → produce health report → alert PM on issues → trail |
| ops_compliance_spot_check | Sample recently completed tasks → verify: conventional commits, PR descriptions, artifact completeness, trail completeness, phase standards met → produce quality report → board memory [quality] → trail |
| ops_budget_assessment | Read budget metrics → assess spending patterns → recommend mode changes if needed → alert PO if critical → board memory [budget] → trail |

**Role-specific skills NEEDED (from fleet-elevation/06 responsibilities):**

| Skill | Stage | What It Teaches |
|-------|-------|----------------|
| real-review-protocol | review | The 7+ step review: verbatim match, acceptance criteria, PR quality, methodology compliance, trail verification, phase standards, contribution validation |
| trail-verification | review | How to reconstruct and verify a task's complete trail from board memory events |
| methodology-compliance-check | all | How to detect violations: code during analysis, skipped stages, readiness jumps, missing contributions |
| board-health-assessment | all | How to assess board health: stuck tasks, offline agents, blocker accumulation, stale items |
| quality-enforcement | all | How to enforce quality standards: commit format, PR structure, comment quality, artifact completeness |
| budget-awareness | all | How to monitor and assess budget spending patterns, recommend mode changes |

**Role-specific CRONs NEEDED:**
- Review queue sweep (every 2h)
- Board health check (daily)
- Compliance spot check (weekly)
- Budget assessment (daily)

**Role-specific sub-agents:** pr-review-toolkit provides 6. May need: trail-reconstructor (read board memory, build chronological trail).

---

### ARCHITECT (fleet-elevation/07)

**Mission:** Design authority — patterns, complexity, architecture health. Contributes design input BEFORE engineers build.

**Existing generic tools used:** fleet_read_context, fleet_contribute, fleet_artifact_create, fleet_artifact_update, fleet_task_accept, fleet_task_complete (rare), fleet_transfer, fleet_chat, fleet_alert, fleet_escalate, fleet_commit (rare)

**Role-specific MCP servers:** filesystem (codebase exploration), github (PR/branch structure)

**Role-specific plugins:** context7 (library docs), superpowers (brainstorming, planning, debugging), adversarial-spec (multi-LLM design debate)

**Role-specific group calls NEEDED:**

| Group Call | What It Would Do (tree) |
|-----------|------------------------|
| arch_design_contribution | Read target task verbatim + analysis → assess problem → select design pattern(s) → produce design_input (approach, files, patterns, constraints, rationale) → fleet_contribute → Plane comment → trail |
| arch_codebase_assessment | Scan target directory → identify patterns, coupling, SRP compliance, dependency direction → produce analysis_document with file references → completeness check → trail |
| arch_option_comparison | For N approaches → produce comparison table (pros, cons, tradeoffs, complexity, risk) → structured investigation_document → Plane HTML → trail |
| arch_complexity_estimate | Read task + codebase → assess: systems touched, dependencies, architectural impact, unknowns → produce story point estimate with rationale → post as comment → trail |

**Role-specific skills NEEDED (from fleet-elevation/07 responsibilities):**

| Skill | Stage | What It Teaches |
|-------|-------|----------------|
| design-pattern-selection | investigation/reasoning | How to choose: builder, mediator, observer, strategy, facade, adapter, repository — WHEN each fits, WHEN each doesn't |
| srp-verification | analysis | How to verify single responsibility: is each module/class/function doing one thing? |
| domain-boundary-enforcement | analysis | How to verify domain boundaries: core doesn't depend on infra, dependency direction is inward |
| onion-compliance-check | analysis | How to verify onion architecture: inner layers never reference outer |
| architecture-health-monitoring | all | How to spot drift, coupling, inconsistency across agents' work |
| design-contribution-protocol | reasoning | How to produce design_input: specific files, specific patterns, specific rationale |
| option-exploration | investigation | How to research multiple approaches: not just the first one, options table with tradeoffs |
| adr-creation | reasoning | How to write Architecture Decision Records |

**Role-specific CRONs NEEDED:**
- Architecture health check (weekly)
- Design contribution backlog check (daily — tasks awaiting design input)

**Role-specific sub-agents:** feature-dev plugin provides code-explorer + code-architect. May also need: pattern-analyzer, dependency-mapper.

---

### DEVSECOPS / CYBERPUNK-ZERO (fleet-elevation/08)

**Mission:** Security at EVERY phase, not just review. Provides security requirements BEFORE implementation. Reviews DURING development. Validates AFTER.

**Existing generic tools used:** fleet_read_context, fleet_contribute, fleet_alert, fleet_artifact_create, fleet_artifact_update, fleet_task_accept, fleet_commit, fleet_task_complete, fleet_escalate, fleet_chat

**Role-specific MCP servers:** filesystem (code scanning), docker (container inspection), semgrep (security analysis)

**Role-specific plugins:** security-guidance (9 PreToolUse hooks), sage (Agent Detection and Response)

**Role-specific group calls NEEDED:**

| Group Call | What It Would Do (tree) |
|-----------|------------------------|
| sec_dependency_audit | Scan all project deps (pip/npm) → check CVE databases → classify findings by severity → produce vulnerability_report artifact → alert on critical → board memory [security, audit] → trail |
| sec_code_scan | Run semgrep on target files → analyze findings → classify → produce security_assessment artifact → set security_hold if critical → trail |
| sec_secret_scan | Scan files for patterns (API keys, tokens, passwords, connection strings) → produce finding report → alert on any match → trail |
| sec_pr_security_review | Read PR diff → check: new deps (CVEs?), auth changes, permission changes, secrets, injection vectors → produce security_review typed comment → set security_hold if critical → trail |
| sec_contribution | Read target task + plan → assess security implications → produce security_requirement (specific: "use JWT with RS256", "pin actions to SHA") → fleet_contribute → trail |
| sec_infrastructure_health | Check MC, gateway, auth, certs, ports, configs → classify issues → produce health report → alert on issues → trail |

**Role-specific skills NEEDED (from fleet-elevation/08 responsibilities):**

| Skill | Stage | What It Teaches |
|-------|-------|----------------|
| threat-modeling | analysis | How to assess attack surface: what could go wrong, risk classification |
| vulnerability-assessment | analysis/work | How to scan for and classify vulnerabilities |
| security-contribution-protocol | reasoning | How to produce specific, actionable security requirements (not generic "be secure") |
| incident-response | crisis | How to triage, assess, mitigate, report security incidents |
| dependency-audit-methodology | analysis | How to audit dependencies: CVE check, version pinning, license review |
| secret-scanning-methodology | analysis | How to detect exposed credentials across repos |
| compliance-verification | analysis | How to verify compliance with security standards |
| penetration-testing-mindset | investigation | How to think like an attacker: what would I exploit? |

**Role-specific CRONs NEEDED:**
- Nightly dependency scan
- PR security review sweep (check unreviewed PRs)
- Infrastructure health check (daily)
- Secret scan (weekly)

**Role-specific sub-agents NEEDED:** dependency-scanner, secret-detector (both read-only, sonnet, filesystem + grep)

---

### SOFTWARE ENGINEER (fleet-elevation/09)

**Mission:** Implementation — follows architect's design, WITH QA's predefined tests, USING UX's patterns, FOLLOWING DevSecOps' requirements. Modeled after the PO.

**Existing generic tools used:** fleet_read_context, fleet_task_accept, fleet_artifact_create, fleet_artifact_update, fleet_commit, fleet_task_complete, fleet_task_create, fleet_request_input, fleet_chat, fleet_pause, fleet_alert

**Role-specific MCP servers:** filesystem (read/write code), github (PR management), playwright (browser testing), pytest-mcp (test execution)

**Role-specific plugins:** context7 (library docs), superpowers (TDD, debugging, planning, verification), pyright-lsp (Python type checking)

**Role-specific group calls NEEDED:**

| Group Call | What It Would Do (tree) |
|-----------|------------------------|
| eng_contribution_check | Before work stage: check context for architect design, QA tests, UX spec, DevSecOps requirements → list what's received, what's missing → if missing required: fleet_request_input → trail |
| eng_implementation_cycle | Read plan → iterate: code change → fleet_commit → run tests → verify → next change → until plan complete → fleet_task_complete → trail |
| eng_fix_task_response | Read rejection feedback → identify root cause (not symptom) → add tests that would have caught issue → re-implement → re-submit → trail |

**Role-specific skills NEEDED (from fleet-elevation/09 responsibilities):**

| Skill | Stage | What It Teaches |
|-------|-------|----------------|
| contribution-consumption | work | How to read and follow all colleague inputs: design as requirements, tests as criteria, security as constraints |
| implementation-planning | reasoning | How to map plan to files and changes, reference verbatim requirement |
| tdd-practitioner | work | Beyond superpowers TDD: pessimistic tests, smart assertions, meaningful coverage |
| conventional-commit-mastery | work | When each type (feat/fix/docs/refactor/test/chore), proper scoping, task reference |
| fix-task-handling | work | How to read rejection feedback, identify root causes, add regression tests |
| subtask-creation | reasoning/work | When and how to create subtasks for other agents (docs → writer, security → devsecops, test gap → QA) |
| code-exploration | analysis | How to systematically examine codebase: file structure, patterns, dependencies |
| design-pattern-application | work | How to apply the architect's recommended patterns in implementation |

**Role-specific CRONs:** Likely none — engineer is task-driven, not schedule-driven.

**Role-specific sub-agents:** superpowers code-reviewer. May also benefit from feature-dev code-explorer for codebase analysis.

**Secondary roles:** Can cover basic DevOps (simple IaC), basic QA (write tests), basic docs (inline documentation).

---

### DEVOPS (fleet-elevation/10)

**Mission:** Infrastructure, CI/CD, deployment maturity. Everything scriptable, everything reproducible. Phase-appropriate infrastructure.

**Existing generic tools used:** fleet_read_context, fleet_task_accept, fleet_artifact_create, fleet_artifact_update, fleet_commit, fleet_task_complete, fleet_contribute, fleet_request_input, fleet_alert, fleet_chat

**Role-specific MCP servers:** filesystem (configs, scripts), github (CI/CD pipelines), docker (container management), github-actions (CI workflow management)

**Role-specific plugins:** hookify (hook creation), commit-commands (git workflows)

**Role-specific group calls NEEDED:**

| Group Call | What It Would Do (tree) |
|-----------|------------------------|
| devops_infrastructure_health | Check MC + gateway + LocalAI + Plane + IRC + daemons → classify status → produce health report → alert on issues → board memory [infrastructure, health] → trail |
| devops_deployment_contribution | Read target task + phase → assess infrastructure needs → produce deployment_manifest (environment, config, deploy strategy, monitoring, rollback) → fleet_contribute → trail |
| devops_cicd_review | Read CI config changes → verify pipeline correctness → check secret handling → verify efficiency → produce review as typed comment → trail |
| devops_phase_infrastructure | Read delivery phase → assess infrastructure maturity gap → produce infrastructure plan per phase standards → trail |

**Role-specific skills NEEDED (from fleet-elevation/10 responsibilities):**

| Skill | Stage | What It Teaches |
|-------|-------|----------------|
| iac-principles | all | Everything scriptable, reproducible, idempotent — no manual steps |
| docker-management | work | Dockerfile best practices, multi-stage builds, compose patterns, security |
| cicd-pipeline-design | reasoning/work | GitHub Actions, test automation, deploy automation, secret handling |
| deployment-strategy | reasoning | Rolling update, blue-green, canary — when each fits |
| monitoring-setup | work | Health checks, alerting, metrics, dashboards — phase-appropriate |
| rollback-procedures | work | How to roll back safely: database migrations, config changes, service restarts |
| fleet-infrastructure | all | MC, gateway, LocalAI, Plane, IRC, daemons — the fleet's own infrastructure |
| phase-infrastructure-maturity | reasoning | What infrastructure each delivery phase requires (POC → production) |

**Role-specific CRONs NEEDED:**
- Infrastructure health check (every few hours)
- CI/CD pipeline status check (daily)
- Configuration drift detection (weekly)

**Role-specific sub-agents:** Possibly container-inspector (docker MCP, read-only) for isolated container analysis.

---

### QA ENGINEER (fleet-elevation/11)

**Mission:** Test PREDEFINITION before implementation. Test VALIDATION during review. Phase-appropriate rigor.

**Existing generic tools used:** fleet_read_context, fleet_contribute, fleet_task_accept, fleet_artifact_create, fleet_artifact_update, fleet_commit, fleet_task_complete, fleet_chat, fleet_alert

**Role-specific MCP servers:** filesystem (test files), playwright (E2E testing), pytest-mcp (test execution)

**Role-specific plugins:** superpowers (TDD methodology)

**Role-specific group calls NEEDED:**

| Group Call | What It Would Do (tree) |
|-----------|------------------------|
| qa_test_predefinition | Read target task verbatim + acceptance criteria + architect design → produce structured qa_test_definition (TC-001 format per fleet-elevation/11) → fleet_contribute → trail |
| qa_test_validation | Read implementation (PR diff) + predefined tests → for EACH TC-XXX: check addressed? evidence? → produce qa_validation typed comment → flag gaps to fleet-ops → trail |
| qa_coverage_analysis | Run coverage tools → analyze gaps → produce coverage report artifact → recommend test additions → trail |
| qa_acceptance_criteria_review | Read inbox tasks → check: are acceptance criteria testable? specific? checkable? → if vague: comment to PM with improvement suggestions → trail |

**Role-specific skills NEEDED (from fleet-elevation/11 responsibilities):**

| Skill | Stage | What It Teaches |
|-------|-------|----------------|
| test-predefinition | reasoning | How to define tests BEFORE implementation: structured criteria, edge cases, phase-appropriate |
| boundary-value-analysis | reasoning | How to identify boundary conditions and edge cases |
| test-validation | review | How to validate implementation against predefined criteria |
| phase-appropriate-testing | all | What testing each phase requires (POC: happy path, production: complete) |
| acceptance-criteria-quality | analysis | How to evaluate if acceptance criteria are testable |
| regression-testing | work | How to identify what needs re-testing when code changes |
| integration-testing-strategy | reasoning | How to design integration tests: what boundaries to test |
| test-contribution-protocol | reasoning | How to produce structured qa_test_definition artifacts |

**Role-specific CRONs NEEDED:**
- Test coverage report (weekly)
- Contribution backlog check (daily — tasks awaiting test predefinition)
- Regression detection (monitor CI for test failures)

**Role-specific sub-agents:** regression-checker, coverage-analyzer (both use filesystem + pytest-mcp, sonnet).

---

### TECHNICAL WRITER (fleet-elevation/12)

**Mission:** Documentation as a LIVING SYSTEM — alongside code, not after it. Keeps Plane pages current. Complementary work with architect, UX, engineer.

**Existing generic tools used:** fleet_read_context, fleet_contribute, fleet_task_accept, fleet_artifact_create, fleet_artifact_update, fleet_commit, fleet_task_complete, fleet_chat, fleet_alert

**Role-specific MCP servers:** filesystem (read/write docs), github (check existing docs)

**Role-specific plugins:** context7 (library docs for accuracy), ars-contexta (knowledge systems)

**Role-specific group calls NEEDED:**

| Group Call | What It Would Do (tree) |
|-----------|------------------------|
| writer_staleness_scan | Scan Plane pages → compare last-modified dates to recent task completions → identify stale pages → produce staleness report → trail |
| writer_doc_contribution | Read target task + plan → produce documentation_outline (what sections, audience, content) → fleet_contribute → trail |
| writer_doc_from_completion | Read completed task (PR, summary, artifacts) → produce/update documentation → update Plane pages → trail |

**Role-specific skills NEEDED:**

| Skill | Stage | What It Teaches |
|-------|-------|----------------|
| documentation-structure | reasoning | How to structure docs: audience awareness, information architecture, navigation |
| api-documentation | work | How to document APIs: endpoints, parameters, responses, errors, examples |
| changelog-generation | work | How to generate changelogs from git history with proper formatting |
| plane-page-maintenance | all | How to detect stale pages, update with current information, create new pages |
| terminology-consistency | all | How to maintain consistent terminology across documentation surfaces |
| doc-contribution-protocol | reasoning | How to produce documentation_outline for other agents' tasks |

**Role-specific CRONs NEEDED:**
- Documentation staleness scan (weekly, when Plane connected)
- API documentation sync check (weekly)

---

### UX DESIGNER (fleet-elevation/13)

**Mission:** UX at EVERY level — not just UI. CLI, API, config, errors, events, notifications, logs, code ergonomics.

**Existing generic tools used:** fleet_read_context, fleet_contribute, fleet_task_accept, fleet_artifact_create, fleet_artifact_update, fleet_task_complete, fleet_chat, fleet_alert

**Role-specific MCP servers:** filesystem (read UI code), playwright (visual testing)

**Role-specific plugins:** (none specific currently — evaluate frontend-design from Anthropic official)

**Role-specific group calls NEEDED:**

| Group Call | What It Would Do (tree) |
|-----------|------------------------|
| ux_spec_contribution | Read target task + plan → assess user-facing elements at ALL levels (UI, CLI, API, config, errors) → produce ux_spec (components, states, interactions, accessibility) → fleet_contribute → trail |
| ux_accessibility_audit | Scan implementation for accessibility → check WCAG compliance → produce accessibility_report → alert on critical gaps → trail |

**Role-specific skills NEEDED:**

| Skill | Stage | What It Teaches |
|-------|-------|----------------|
| interaction-design | reasoning | How to design interactions: all states (loading, empty, error, success), all interactions, all flows |
| accessibility-audit | analysis | How to verify WCAG compliance: aria, keyboard nav, screen reader, color contrast |
| component-patterns | reasoning | How to specify components: reuse existing patterns, follow design system |
| ux-at-every-level | all | How to think about UX beyond UI: CLI output, API responses, error messages, config structure |
| ux-contribution-protocol | reasoning | How to produce ux_spec artifacts: structured, specific, all states |

**Role-specific CRONs:** Likely none — UX is contribution-driven, not schedule-driven.

---

### ACCOUNTABILITY GENERATOR (fleet-elevation/14)

**Mission:** Verify PROCESS — methodology followed, trails complete, governance met. Does NOT review quality (fleet-ops does). Does NOT enforce (immune system does). VERIFIES and REPORTS.

**Existing generic tools used:** fleet_read_context, fleet_artifact_create, fleet_alert, fleet_chat

**Role-specific MCP servers:** filesystem (read evidence)

**Role-specific plugins:** (none specific currently)

**Role-specific group calls NEEDED:**

| Group Call | What It Would Do (tree) |
|-----------|------------------------|
| acct_trail_reconstruction | Query board memory by task:{id} → aggregate all trail events chronologically → produce audit_trail document → trail |
| acct_sprint_compliance | For each completed task in sprint → verify trail completeness → produce compliance_report (X/Y compliant, Z gaps) → board memory [compliance] → trail |
| acct_pattern_detection | Analyze compliance data across tasks → identify recurring gaps → post patterns to board memory [compliance, pattern] → feeds immune system |

**Role-specific skills NEEDED:**

| Skill | Stage | What It Teaches |
|-------|-------|----------------|
| trail-reconstruction-methodology | analysis/work | How to reconstruct complete task history from board memory trail events |
| compliance-verification | analysis | How to verify: stages traversed, contributions received, gates approved, standards met |
| pattern-detection | analysis | How to identify recurring compliance gaps across tasks and agents |
| compliance-reporting | work | How to produce structured compliance reports for PO review |

**Role-specific CRONs NEEDED:**
- Sprint boundary compliance report
- Weekly pattern detection scan

---

---

## Review Ecosystem — Cross-Role Capability

Review isn't one tool — it's an ECOSYSTEM of capabilities spread across roles, plugins, and stages:

| Capability | Source | Who Uses It | When |
|-----------|--------|-------------|------|
| 6 parallel PR review agents | pr-review-toolkit plugin | Fleet-ops | Review stage — code-reviewer (opus), code-simplifier, comment-analyzer, pr-test-analyzer, silent-failure-hunter, type-design-analyzer |
| Adversarial spec debate | adversarial-spec plugin | Architect | Investigation stage — multi-LLM debate for spec refinement with 10+ providers |
| Subagent-driven 2-stage review | superpowers skill | Engineer, Architect | Pre-completion — spec compliance check, then code quality check |
| Requesting/receiving code review | superpowers skills | Engineer | Pre/post completion — pre-review checklist + feedback integration without "performative agreement" |
| Code-reviewer sub-agent | superpowers plugin | All with superpowers | After completing work — plan alignment, quality, architecture, docs |
| 3 feature-dev sub-agents | feature-dev plugin (NOT YET ASSIGNED) | Architect, Engineer | Analysis/reasoning — code-explorer (sonnet), code-architect (sonnet), code-reviewer (sonnet) |
| Confidence-based code review | code-review plugin (NOT YET ASSIGNED) | Fleet-ops, QA | Review — automated scoring with multiple specialized agents |
| QA test validation | QA's role | QA | Review stage — validate each predefined TC-XXX against implementation |
| DevSecOps security review | DevSecOps's role | DevSecOps | Review stage — PR diff scan for security patterns |
| Architect design compliance | Architect's role | Architect | Review stage (optional) — verify implementation follows design |

The fleet_approve tool is the GATE — but the review itself uses multiple capabilities depending on the reviewer's role and the task type. The pm_contribution_check group call and the ops_real_review group call orchestrate these review capabilities into structured workflows.

---

## Plugin Ecosystem — Detailed Capability Mapping

### superpowers (architect, engineer, QA) — 14 skills + 1 sub-agent + 1 hook

| Skill | Maps To Stage | Maps To Role | Input | Impact/Output |
|-------|--------------|-------------|-------|---------------|
| brainstorming | conversation, analysis | ALL with plugin | Problem/question | Socratic exploration, iterative refinement |
| writing-plans | reasoning | ALL with plugin | Spec/requirements | Detailed implementation roadmap with tasks |
| executing-plans | work | ALL with plugin | A written plan | Batch execution with human checkpoints |
| test-driven-development | work | Engineer, QA | Code to implement | RED-GREEN-REFACTOR cycle with anti-patterns ref |
| systematic-debugging | analysis, work | ALL with plugin | Bug/issue | 4-phase root cause: hypothesis → evidence → fix → verify |
| verification-before-completion | work (pre-complete) | ALL with plugin | Completed work | Runs verification commands, confirms output before claims |
| dispatching-parallel-agents | any | ALL with plugin | 2+ independent tasks | Concurrent sub-agent spawning strategy |
| subagent-driven-development | work (pre-review) | Engineer, Architect | Completed code | 2-stage: spec compliance check → code quality check |
| requesting-code-review | work (pre-submit) | Engineer | Work ready for review | Pre-review checklist and validation |
| receiving-code-review | work (post-feedback) | Engineer | Review feedback | Technical rigor for feedback integration, no performative agreement |
| using-git-worktrees | work | Engineer, DevOps | Need isolated branch | Parallel development with safety verification |
| finishing-a-development-branch | work (completion) | Engineer, DevOps | Branch ready | Structured decision: merge, PR, or cleanup |
| writing-skills | meta | Architect, Engineer | Need for a new skill | Framework for creating new skills |
| using-superpowers | meta (auto-injected) | ALL with plugin | Session start | Skill discovery and invocation protocol |
| code-reviewer (sub-agent) | post-work | ALL with plugin | Completed step | Plan alignment, code quality, architecture, docs review |
| SessionStart hook | session start | ALL with plugin | — | Injects skill instructions into every session |

### pr-review-toolkit (fleet-ops) — 6 sub-agents

| Sub-Agent | Model | Input | Output | Focus |
|-----------|-------|-------|--------|-------|
| code-reviewer | opus | PR diff + CLAUDE.md | 0-100 score, issues by severity | Style violations, bug detection, CLAUDE.md compliance |
| code-simplifier | inherit | PR diff | Simplification recommendations | Clarity, consistency, maintainability |
| comment-analyzer | inherit | PR comments + code | Accuracy assessment | Comment rot, doc completeness, misleading comments |
| pr-test-analyzer | inherit | PR diff + tests | 1-10 rating, gap list | Behavioral coverage (not line), edge cases, error conditions |
| silent-failure-hunter | inherit | PR diff | Zero-tolerance categorization | Silent catches, inadequate fallbacks, missing logging |
| type-design-analyzer | inherit | PR types/interfaces | 1-10 per dimension | Encapsulation, invariant expression, enforcement, usefulness |

### adversarial-spec (architect) — multi-LLM debate

| Input | Process | Output |
|-------|---------|--------|
| Initial spec/design | Claude creates spec → multiple opponent models critique → Claude reviews alongside → synthesis with accept/reject reasoning → loop until agreement | Refined, stress-tested specification |
| Supports: --interview (requirements), --focus (security/scalability/performance/ux/reliability/cost), --persona (10 professional perspectives), --session (checkpoints) |
| Providers: OpenAI, Google, xAI, Mistral, Groq, Deepseek, Zhipu, OpenRouter, AWS Bedrock |

### feature-dev (NOT YET ASSIGNED — evaluate for architect + engineer) — 3 sub-agents

| Sub-Agent | Model | Input | Output |
|-----------|-------|-------|--------|
| code-explorer | sonnet | Codebase area | Execution paths, architecture layers, dependencies |
| code-architect | sonnet | Feature requirements | Architecture blueprint, implementation targets |
| code-reviewer | sonnet | Code changes | Confidence-based review with bug/security/quality analysis |

### Other plugins mapped:

| Plugin | Agent | Key Capabilities | Input → Output |
|--------|-------|-------------------|----------------|
| plannotator | PM | /annotate (interactive UI), /review (PR review), /archive (saved decisions) | Markdown/PR → visual annotations with team feedback |
| hookify | DevOps | Natural-language hook creation, /hookify:configure, writing-rules skill | Description of unwanted behavior → PreToolUse/Stop/Prompt hook |
| commit-commands | DevOps | /commit, /commit-push-pr, /clean_gone | Staged changes → conventional commit + optional push + PR |
| context7 | Architect, Engineer, Writer | resolve-library-id, query-docs MCP tools | Library name → current, version-specific documentation |
| pyright-lsp | Engineer | Python type checking via LSP | Python files → type errors, missing annotations |
| security-guidance | DevSecOps | 9 PreToolUse patterns on Edit/Write | Code changes → security warnings for injection, XSS, deserialization, etc. |
| claude-mem | ALL | Cross-session semantic memory | Session observations → persistent memories → future context injection |
| safety-net | ALL | PreToolUse destructive command detection | Bash commands → block/warn on rm -rf, git reset --hard, etc. |

### NOT YET ASSIGNED — worth evaluating:

| Plugin | Potential Agents | What It Would Add |
|--------|-----------------|-------------------|
| claude-code-setup | ALL | Analyze codebase → recommend automations (hooks, skills, MCP, subagents) |
| claude-md-management | ALL | CLAUDE.md quality audit, capture learnings, maintain memory |
| episodic-memory | ALL | Semantic search over past conversations — cross-session continuity |
| double-shot-latte | ALL | Auto-continuation — stops "Would you like me to continue?" waste |
| elements-of-style | Writer | 18 Strunk writing rules for documentation quality |
| serena | Architect, Engineer | Semantic code analysis via LSP integration |
| skill-creator | Architect, Engineer | Create, improve, eval, benchmark skills at scale |
| frontend-design | UX, Engineer | Production-grade frontend design avoiding "AI slop" |

---

## Secondary and Backup Roles

Each agent has a PRIMARY role and may have SECONDARY and BACKUP capabilities:

| Agent | Primary | Secondary | Can Backup For |
|-------|---------|-----------|----------------|
| Software Engineer | Implementation | Basic DevOps (simple IaC), basic QA (write tests), basic docs (inline) | DevOps (simple tasks), QA (simple tests) |
| Architect | Design authority | Can implement (rare — usually transfers) | Software Engineer (design-heavy tasks) |
| DevSecOps | Security | Infrastructure security overlaps with DevOps | DevOps (security-related infra) |
| DevOps | Infrastructure | — | — |
| QA | Testing | — | — |
| PM | Coordination | — | — |
| Fleet-Ops | Quality/review | — | — |
| Writer | Documentation | — | — |
| UX | User experience | — | — |
| Accountability | Compliance | — | — |

Secondary role means: the agent has SOME capabilities of another role (engineer knows enough DevOps to do simple IaC). They don't get the full role toolkit — they get a subset. This affects config/agent-tooling.yaml: engineer might get a few DevOps skills as secondary capabilities.

Backup means: if the primary role agent is offline, this agent can handle BASIC tasks. The orchestrator would need to know backup mappings for dispatch.

---

## Phase System Connection — Flexible Lifecycle Definitions

### Current State

config/phases.yaml defines two progressions (standard: idea→production, release: alpha→release). Each phase has standards, required_contributions, and gate (PO approval).

### What the PO Says

Phases are FLEXIBLE and PO-DEFINED. The agent does NOT assume what a phase means — the config defines it. Each epic/module/issue can have its own phase group. The PO can create any progression group — not just the two existing ones.

### What Needs to Evolve

1. **Predefinable phase groups** — any number of custom progressions in config. Not just "standard" and "release" but also "documentation" (draft→review→published), "research" (idea→findings), or anything the PO defines.

2. **Per-epic/module/issue assignment** — different epics use different progressions. An infrastructure epic uses standard (poc→production). A release uses release (alpha→release). A documentation effort uses a custom documentation progression.

3. **Phase standards in config** — what quality bars apply at each phase. The agent reads this config, not hardcoded assumptions. POC = happy path tests. Production = complete coverage, certified security, full monitoring.

4. **Phase affects tool/skill selection:**

| Phase Level | Tests | Docs | Security | Infrastructure | Effort |
|-------------|-------|------|----------|---------------|--------|
| idea/draft | None | None | None | None | Low |
| conceptual/alpha | None | Outline only | Review only | None | Medium |
| poc/beta | Happy path | README | Basic scan | Docker dev | Medium |
| mvp/rc | Main flows + edges | Setup + usage | Auth + validation | Automated CI | High |
| staging | Comprehensive + integration | Full docs | Dep audit, pen-test mindset | Full CI/CD + staging | High |
| production/release | Complete + performance + resilience | Everything + runbook | Certified, compliance | Full pipeline + monitoring + rollback | High |

5. **Phase flows through autocomplete chain:**
   - Task custom field: delivery_phase
   - Context injection: agent sees phase + applicable standards
   - Skills adapt per phase (QA predefinition rigor adapts)
   - Contributions required per phase (from config)
   - TOOLS.md references phase-appropriate capability levels

---

## Labor Stamp Connection — Automations and Metadata

Labor stamps are NOT directives — they're METADATA the tools system produces automatically. The connection is automation and provenance, not usage guidance.

### What Labor Stamps Record

| Field | Source | Tools System Connection |
|-------|--------|----------------------|
| backend | Router at dispatch | Which backend powered the tool calls |
| model | model_selection.py | Which model the agent used |
| effort | Config or per-dispatch | Thinking depth during tool usage |
| confidence_tier | Derived from backend + model | Trust level for the work |
| tools_called | Session tracking | Which fleet tools were actually called |
| skills_used | (TO IMPLEMENT) | Which skills were invoked |
| duration_seconds | Timing | How long the tool chain took |
| estimated_cost_usd | Token calculation | Cost of the operations |

### How Stamps Flow

Agent works with tools → fleet_task_complete assembles stamp from DispatchRecord + session metrics + tools list → stamp written to task custom fields + PR body + completion comment + trail.

### What's Missing

- **skills_used tracking** — stamps should record skill invocations, not just MCP tools
- **CRON labor stamps** — scheduled operations need provenance too
- **Sub-agent labor stamps** — sub-agent model/cost attributed to parent task
- **Phase-aware labor expectations** — production phase with haiku/low effort is a signal

---

## Context System Quadrant Review

4 quadrants from context-system docs. Each affects how agents discover and use capabilities:

### Q1: Task × MCP Group Calls (fleet_task_context)

Agent calls ONE tool, gets everything about their task. Currently returns: task data, methodology, artifact, comments, related tasks, Plane.

**Missing for tools system:**
- Phase standards (what current phase requires)
- Contribution completeness status (all required received?)
- Stage-appropriate skill/tool recommendations

### Q2: Task × Pre-Embedded (context/task-context.md)

Written at dispatch. Agent reads stage protocol, verbatim, readiness before calling any tool.

**Missing for tools system:**
- Phase-specific quality bars alongside stage protocol
- Contribution status ("Design input: RECEIVED. QA tests: PENDING.")
- Stage tool/skill recommendations ("At analysis, consider: /systematic-debugging, code-explorer sub-agent")

### Q3: Heartbeat × MCP Group Calls (fleet_heartbeat_context)

Role-specific heartbeat data. Drivers discover what needs attention.

**Missing for tools system:**
- Group call recommendations ("3 pending approvals → use ops_real_review")
- CRON results ("Nightly scan: 2 critical findings")
- Contribution backlog ("3 tasks awaiting your design input")

### Q4: Heartbeat × Pre-Embedded (context/fleet-context.md)

Written every 30s by orchestrator. Fleet state, directives, messages, tasks, events.

**Missing for tools system:**
- Standing order references
- CRON status summary
- Available capability reminders per situation

### What This Means

The context system DELIVERS directives. The tools system CREATES capabilities and DEFINES directives. The generation pipeline produces TOOLS.md (static capability reference at position 4). The context system produces dynamic context (position 6). Together they drive the autocomplete chain to the correct capability at the correct time.

---

## Scale Summary

| Dimension | Count | Status |
|-----------|-------|--------|
| Generic fleet MCP tools | 30 | EXIST (trees partially wired) |
| Role-specific group calls | ~35-40 | DON'T EXIST (need design + build) |
| Generic methodology skills | 10-20 | ~7 EXIST (fleet skills), rest TBD |
| Role-specific skills | ~80-100 | 0 EXIST (all need design + build or ecosystem install) |
| Role-specific MCP servers | 10 types | CONFIGURED but UNVERIFIED |
| Role-specific plugins | 11 types | CONFIGURED but UNINSTALLED |
| Role-specific CRONs | ~20-25 | 0 EXIST |
| Role-specific sub-agents | ~10-15 | 0 custom EXIST (plugin sub-agents available but unverified) |
| Role-specific hooks | per-role | MINIMAL (only plugin-provided) |
| Standing orders | per-role | 0 EXIST |

**This is the 42+ hours.** Not 20 tools with try/except blocks. A complete capability surface for 10 top-tier expert agents.
