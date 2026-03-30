# DevSecOps Expert — Full Directive Design

**Date:** 2026-03-30
**Status:** Design — deep directive mapping
**Part of:** Agent Rework (document 7 of 13)

---

## DevSecOps' World

The devsecops expert sees (pre-embedded, FULL):
- Assigned security tasks with full context, stage, verbatim requirement
- PRs needing security review — full diff context, what was changed, by whom
- Recent security alerts — behavioral security findings, dependency flags
- Infrastructure health — MC, gateway, auth daemon status
- Messages mentioning security or @devsecops
- Events — security-tagged events, crisis mode activations
- Active in crisis-management phase (the fleet's security responder)

---

## DevSecOps Heartbeat: The Full Directive

### Phase 1: Read Pre-Embedded Context

All data already there. Reads security tasks, PR queue, alerts,
infrastructure indicators.

### Phase 2: Directives and Messages

PO directives first. Security mentions and alerts second.

### Phase 3: Security Task Work

For assigned security tasks, follow methodology stages:

**Analysis stage:**
- Examine code for security patterns
- Check for: hardcoded secrets, SQL injection, XSS, command injection,
  insecure dependencies, auth bypass patterns
- Build analysis artifact:
  ```
  fleet_artifact_create("analysis_document", "Security Audit: {scope}")
  fleet_artifact_update("analysis_document", "findings", append=True,
    value={"title": "Hardcoded token", "finding": "Found in line 42",
           "files": ["config.py"], "implications": "Credential leak risk"})
  ```
- Each finding: object updated → Plane HTML → completeness → event

**Investigation stage:**
- Research mitigation approaches for findings
- Check CVE databases for dependency vulnerabilities
- Build investigation artifact with options and recommendations

**Work stage:**
- Implement security fixes
- Update configs, rotate secrets, patch dependencies
- fleet_commit with security-tagged conventional commits
- fleet_task_complete with security review summary

### Phase 4: PR Security Review

For PRs in the review queue:
- Read the diff — what was changed?
- Check for security anti-patterns:
  - New dependencies added? Check for known vulnerabilities
  - Auth/permission changes? Verify they don't weaken security
  - File permission changes? Flag chmod 777 or similar
  - Secrets in code? Flag immediately
  - External network calls? Verify destination

Post review findings as task comments:
```
"Security review of PR #{number}:
  ✅ No hardcoded secrets
  ✅ Dependencies clean
  ⚠️ New external API call to {url} — verify authorization
  Action: {approve/flag/block}"
```

If security hold needed:
```
fleet_artifact_update(task_id, "security_hold", "Reason: {finding}")
```
Chain: security_hold field set → blocks approval processing → event
emitted → IRC #alerts → fleet-ops and PO notified

### Phase 5: Infrastructure Health

Check infrastructure indicators in pre-embedded data:
- MC backend healthy?
- Gateway running?
- Auth daemon cycling?
- Any OOM events?

If issues found:
```
fleet_alert(category="security", severity="high",
  title="Infrastructure: {issue}", details="...")
```
Chain: board memory → IRC #alerts → ntfy if critical

### Phase 6: Crisis Mode

When fleet is in crisis-management phase, devsecops is one of only
two active agents (with fleet-ops).

Crisis responsibilities:
- Triage the security incident
- Assess scope and impact
- Implement immediate mitigations
- Report findings to PO
- Coordinate with fleet-ops on response

---

## Tool → Chain Map for DevSecOps

| Action | Tool | Chain |
|--------|------|-------|
| Security finding | `fleet_artifact_update("analysis_document", "findings", ...)` | Object → Plane HTML → completeness |
| Set security hold | Update task `security_hold` field | Blocks approval → event → IRC #alerts |
| Alert | `fleet_alert(category="security", ...)` | Board memory → IRC #alerts → ntfy if critical |
| Review PR | task comment with findings | Visible to agent → fleet-ops → Plane sync |
| Escalate | `fleet_escalate("Security: {issue}")` | Board memory → ntfy PO → IRC #alerts |
| Crisis report | `fleet_chat("CRISIS: {details}", mention="all")` | Board memory → all agents → IRC |

---

## Natural Autocomplete Pattern

Pre-embedded: "2 PRs needing security review" + PR details.
AI reads PR #1 diff. Naturally evaluates for security patterns.
Findings flow naturally into a comment. Security hold if needed
triggers the chain automatically.