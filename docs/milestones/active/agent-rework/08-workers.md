# Worker Agents — Engineers, QA, Writer, UX

**Date:** 2026-03-30
**Status:** Design
**Part of:** Agent Rework (document 8 of 13)

---

## Worker Agent Roles

- **software-engineer** — code implementation
- **devops-expert** — infrastructure, CI/CD, deployment
- **qa-engineer** — testing, quality verification
- **technical-writer** — documentation
- **ux-designer** — UI/UX design
- **accountability-generator** — compliance, audit, governance

### Common Heartbeat Flow

1. Read pre-embedded context (assigned tasks with stages, messages)
2. Handle directives and messages
3. For each assigned task: follow methodology protocol for current stage
4. Progressive artifact work — read what was done, continue, update
5. Communicate with PM and peers about progress or blockers
6. If idle: HEARTBEAT_OK

### Stage-Specific Behavior

All workers follow the same methodology stages but produce different
artifacts based on their role:

- **Conversation**: ask questions about requirements to PO or PM
- **Analysis**: examine codebase/docs/infrastructure relevant to role
- **Investigation**: research approaches specific to role expertise
- **Reasoning**: produce implementation plan
- **Work**: produce deliverables (code, tests, docs, configs, designs)

### Per-Role Specifics

**software-engineer**: Code tasks. Commits with conventional format.
PRs with descriptions. Tests for new code.

**devops-expert**: Infrastructure tasks. Scripts, configs, IaC.
Deployment and CI/CD work.

**qa-engineer**: Test tasks. Test plans, test execution, coverage
reports. Quality verification of other agents' work.

**technical-writer**: Documentation tasks. API docs, architecture
docs, user guides. Reviews docs from other agents.

**ux-designer**: UI/UX tasks. Design specs, wireframes, component
designs. Reviews UI work.

**accountability-generator**: Compliance tasks. Health reports, audit
trails, governance checks. Accountability metrics.

---

## Pre-Embedded Data for Workers

Full data:
- Assigned tasks with full context, stage, readiness, verbatim requirement
- In-progress task artifact (if exists)
- Messages mentioning this agent
- Recent relevant events