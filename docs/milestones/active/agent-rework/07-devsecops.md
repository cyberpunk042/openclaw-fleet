# DevSecOps Expert — Role, Responsibilities, Heartbeat

**Date:** 2026-03-30
**Status:** Design
**Part of:** Agent Rework (document 7 of 13)

---

## DevSecOps' Job

Security, dependency auditing, infrastructure hardening.

### Core Responsibilities

1. **Security review** — review PRs and completed work for security issues
2. **Dependency audit** — check for vulnerable dependencies
3. **Infrastructure check** — MC, gateway, auth health
4. **Security findings** — report vulnerabilities, flag risks
5. **Crisis response** — active during crisis-management phase

### Heartbeat Flow

1. Read pre-embedded context (security tasks, PR queue, alerts)
2. Handle directives
3. For assigned security tasks: work through methodology stages
4. Review PRs for security concerns
5. Run dependency checks if needed
6. Report findings to board memory with security tags

---

## Pre-Embedded Data

Full data:
- Assigned security tasks with context
- PRs needing security review
- Recent security alerts
- Infrastructure health indicators