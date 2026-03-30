# Standards Integration Per Role

**Date:** 2026-03-30
**Status:** Design
**Part of:** Agent Rework (document 10 of 13)

---

## How Standards Apply

The standards library defines 7 artifact types. Each role produces
different artifacts. Standards are enforced per role based on what
they produce.

| Role | Primary Artifacts | Standards Applied |
|------|-------------------|-------------------|
| PM | Tasks, subtasks | task standard |
| fleet-ops | Approvals, reviews | completion_claim standard |
| architect | Analysis, plans | analysis_document, plan |
| devsecops | Security findings | bug, analysis_document |
| software-engineer | Code, PRs | pull_request, completion_claim |
| devops-expert | Code, configs | pull_request, completion_claim |
| qa-engineer | Test results | analysis_document, bug |
| technical-writer | Docs | analysis_document, plan |

Standards are checked by the artifact tracker when agents update
artifacts. Completeness feeds readiness. Immune system detects when
standards aren't met.

---

## Per-Role Standards Awareness

Each agent's context should include the standards relevant to their
current task's artifact type. When an engineer is in work stage, they
see the pull_request and completion_claim standards — what fields
are required, what quality looks like.