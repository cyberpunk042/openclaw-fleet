# Chunk 4: Per-Role Skill Design & Creation

**Date:** 2026-04-07
**Status:** Planning
**Part of:** [tools-system-session-index.md](tools-system-session-index.md) — Chunk 4 of 9
**Depends on:** Chunk 3 (ecosystem evaluation tells us what's missing, foundation skills built, creation pipeline established)
**Blocks:** Chunk 8 (generation pipeline needs skills to exist for TOOLS.md skills section)

---

## What This Chunk Accomplishes

The largest chunk. After Chunk 3's ecosystem evaluation identifies what's missing per role, this chunk BUILDS (or installs from ecosystem) the per-role skills. The PO described: 10-40 generic methodology skills + 40+ per role per methodology stage and situation.

This is NOT a single implementation task. It's 10 parallel workstreams (one per role), each requiring:
1. Review the role's fleet-elevation spec (fleet-elevation/05-14)
2. Review Chunk 3's gap analysis for this role
3. Design each missing skill (SKILL.md content)
4. Build or install each skill
5. Organize skills by stage/situation
6. Update config/agent-tooling.yaml and config/skill-stage-mapping.yaml
7. Verify: agent can invoke, skill produces correct output

---

## The Scale

This chunk's scope depends entirely on Chunk 3's gap analysis output. The gap analysis determines:
- How many skills already exist in the ecosystem and just need installation
- How many need custom building
- How many can be deferred

Rough estimate from the PO's direction:
- 10-40 generic methodology skills (shared across roles)
- 40+ per role × 10 roles = 400+ role-specific skills

Many of these will come from ecosystem installation (superpowers provides 14, other plugins provide more). The CUSTOM BUILD count depends on what Chunk 3's evaluation finds.

---

## Generic Methodology Skills (Shared Across Roles)

These skills apply to ALL agents regardless of role. They teach methodology-stage-appropriate behavior.

### Conversation Stage Skills
- How to ask effective questions of the PO
- How to extract requirements from vague descriptions
- How to identify and state what you don't understand
- How to propose your understanding for correction

### Analysis Stage Skills
- How to examine a codebase systematically (what to look for, how to document)
- How to produce an analysis document (structure, required sections)
- How to reference specific files and lines (not vague descriptions)
- How to assess impact of proposed changes

### Investigation Stage Skills
- How to research multiple approaches (not just the first one)
- How to compare options with tradeoffs
- How to cite sources and prior art
- How to produce investigation documents

### Reasoning Stage Skills
- How to produce a plan that references the verbatim requirement
- How to map acceptance criteria to implementation steps
- How to estimate effort and identify risks
- How to break down work into subtasks with dependencies

### Work Stage Skills
- How to execute a confirmed plan without deviating
- How to use conventional commits properly
- How to run tests and interpret results
- How to prepare a completion summary

### Cross-Stage Skills
- Context awareness (when to extract artifacts, when to compact)
- Communication patterns (when to use which fleet tool)
- Quality self-check (verification before claiming completion)
- Contribution consumption (reading and following colleague inputs)

**Note:** Some of these may already exist in superpowers (brainstorming, writing-plans, TDD, verification-before-completion, systematic-debugging). The ecosystem evaluation (Chunk 3) determines which need custom building vs which are already available.

---

## Per-Role Skills (Determined by Chunk 3 Gap Analysis)

Each role's skill set follows from their fleet-elevation spec + gap analysis. Below is the STRUCTURE, not the content — content depends on Chunk 3 output.

### Role: Architect (fleet-elevation/07)
**Stage focus:** analysis (codebase examination), investigation (option exploration), reasoning (design decisions)
**Contribution type:** design_input (approach, files, patterns, constraints)
**Skill categories needed:**
- Architecture analysis (examine structure, identify patterns, map dependencies)
- Option comparison (evaluate approaches with tradeoffs)
- Design documentation (ADRs, design proposals, pattern selection rationale)
- Complexity assessment (story point estimation, risk identification)
- Design contribution (producing design_input artifacts for other agents)

### Role: Software Engineer (fleet-elevation/09)
**Stage focus:** reasoning (plan production), work (implementation)
**Contribution consumption:** design_input, qa_test_definition, security_requirement, ux_spec
**Skill categories needed:**
- Contribution consumption (reading and following all colleague inputs)
- Implementation planning (mapping plan to files and changes)
- Test writing (alongside code, not after)
- Subtask creation (breaking complex work, routing to specialists)
- Fix task handling (reading rejection feedback, fixing root causes)

### Role: QA Engineer (fleet-elevation/11)
**Stage focus:** analysis (test strategy), reasoning (test predefinition)
**Contribution type:** qa_test_definition (test criteria, edge cases, priorities)
**Skill categories needed:**
- Test predefinition (define tests BEFORE implementation — TDD thinking)
- Coverage analysis (identify gaps, boundary cases)
- Acceptance criteria validation (verify criteria are testable)
- Regression testing (what to re-test when code changes)
- Test contribution (producing qa_test_definition artifacts)

### Role: DevOps (fleet-elevation/10)
**Stage focus:** analysis (infrastructure assessment), work (IaC implementation)
**Contribution type:** deployment_manifest (environment, config, deploy strategy)
**Skill categories needed:**
- Infrastructure analysis (current state, gaps, risks)
- Docker/container management (Dockerfile, compose, multi-stage builds)
- CI/CD pipeline design (GitHub Actions, test automation)
- Deployment procedures (rolling update, rollback, monitoring)
- IaC principles (everything scriptable, reproducible, idempotent)

### Role: DevSecOps (fleet-elevation/08)
**Stage focus:** analysis (security assessment), work (security fixes)
**Contribution type:** security_requirement (specific requirements, not generic "be secure")
**Skill categories needed:**
- Vulnerability assessment (dependency audit, code scanning)
- Threat modeling (attack surface, risk classification)
- Security contribution (producing specific, actionable security requirements)
- Incident response (crisis mode handling)
- Compliance verification (standards adherence)

### Role: PM (fleet-elevation/05)
**Stage focus:** Does NOT follow stages — manages OTHER agents' stages
**Skill categories needed:**
- Sprint planning (capacity, velocity, goal setting)
- Backlog grooming (refinement, re-estimation, prioritization)
- Epic breakdown (decomposition with dependencies)
- Contribution orchestration (ensuring specialists contribute before work)
- PO communication (filtering noise, routing gates, preparing context)
- Blocker resolution (reassignment, splitting, escalation)
- Status reporting (sprint summaries, velocity, action items)

### Role: Fleet-Ops (fleet-elevation/06)
**Stage focus:** Does NOT follow stages — reviews AT review stage
**Skill categories needed:**
- Real review protocol (7-step review from fleet-elevation/06)
- Trail verification (reconstruct and verify methodology compliance)
- Board health monitoring (stuck tasks, offline agents, stale deps)
- Quality enforcement (commit format, PR structure, comment quality)
- Budget awareness (alert on concerning spending patterns)

### Role: Technical Writer (fleet-elevation/12)
**Stage focus:** analysis (documentation gap assessment), work (documentation production)
**Contribution type:** documentation_outline (what docs are expected)
**Skill categories needed:**
- Documentation structure (audience awareness, information architecture)
- API documentation (endpoint docs, SDK guides)
- Plane page maintenance (when connected, keep pages current)
- Changelog generation (from git history)
- Terminology consistency (across documentation surfaces)

### Role: UX Designer (fleet-elevation/13)
**Stage focus:** analysis (UX assessment), reasoning (UX spec production)
**Contribution type:** ux_spec (components, states, interactions, accessibility)
**Skill categories needed:**
- Interaction design (user flows, component states, error handling)
- Accessibility audit (WCAG compliance, screen reader, keyboard nav)
- Component patterns (design system alignment, reusable patterns)
- UX at every level (not just UI — CLI, API, config, error messages)
- UX contribution (producing ux_spec artifacts)

### Role: Accountability Generator (fleet-elevation/14)
**Stage focus:** analysis (trail examination), work (compliance reporting)
**Skill categories needed:**
- Trail reconstruction (build complete task history from events/board memory)
- Compliance verification (methodology adherence, contribution completeness)
- Pattern detection (recurring gaps, systemic issues)
- Reporting (sprint compliance, agent performance, process adherence)

---

## Execution Approach

This chunk is too large for sequential implementation. Suggested approach:

### Phase A: Generic Skills (shared)
Build the 10-40 generic methodology skills first. These benefit all agents and establish patterns for role-specific skills.

### Phase B: Priority Roles
Build skills for the roles most critical to fleet operation:
1. PM (drives the board — without PM skills, nothing moves)
2. Fleet-Ops (reviews everything — without review skills, nothing completes)
3. Software Engineer (implements — most tasks end with engineer work)

### Phase C: Specialist Roles
Build skills for specialist contributors:
4. Architect (design input needed before engineer works)
5. QA (test predefinition needed before engineer works)
6. DevSecOps (security requirements for relevant tasks)

### Phase D: Support Roles
Build skills for support roles:
7. DevOps (infrastructure as needed)
8. Technical Writer (documentation alongside code)
9. UX Designer (UX specs for user-facing work)
10. Accountability Generator (compliance after completion)

### Per-Role Process
For each role:
1. Read fleet-elevation spec for the role
2. Read Chunk 3 gap analysis
3. List skills to build (not available in ecosystem)
4. Design each skill's SKILL.md (purpose, trigger conditions, steps, rules, examples)
5. Build the SKILL.md files
6. Test: agent invokes skill → correct output
7. Update configs (agent-tooling.yaml, skill-stage-mapping.yaml)
8. Verify: skill appears in agent's session

---

## Verification Criteria

- [ ] Generic methodology skills built and tested
- [ ] Per-role skills built or installed for all 10 roles
- [ ] config/agent-tooling.yaml updated with actual skill names (not aspirational)
- [ ] config/skill-stage-mapping.yaml populated with all skills per stage
- [ ] Each skill verified: agent can invoke, produces correct output
- [ ] Skills deployed to correct directories and reaching workspaces
- [ ] No skill name conflicts across sources
- [ ] Total skill count per agent within gateway limits (max 150 skills, max 30K chars)

---

## Outputs

| Output | Description |
|--------|-------------|
| 10-40 generic SKILL.md files | Methodology skills shared across roles |
| N × role-specific SKILL.md files | Per-role skills (count determined by Chunk 3 gap analysis) |
| Updated config/agent-tooling.yaml | Real skill names replacing aspirational list |
| Updated config/skill-stage-mapping.yaml | Complete stage mapping for all skills |
| Per-role verification report | What skills each agent has, tested and working |
