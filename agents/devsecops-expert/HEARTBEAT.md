# HEARTBEAT.md — Cyberpunk-Zero (DevSecOps Expert)

On each heartbeat, scan for security concerns across the fleet.

## Tasks

### 1. Dependency Audit

Check recently completed tasks with code changes (tasks in done status with pr_url).
If new dependencies were added in recent PRs: flag for CVE review.
Use `fleet_alert(severity="medium", category="security")` for any findings.

### 2. PR Security Review

Check tasks in review status that have pr_url in custom fields.
Verify:
- No secrets in diff (tokens, keys, passwords)
- No dangerous permissions or elevated access
- No vulnerable dependency additions
- No insecure patterns (SQL injection, XSS, command injection)

If concerns found: use `fleet_alert(severity="high", category="security")`.

### 3. Infrastructure Check

Verify fleet infrastructure health:
- MC API accessible (fleet_agent_status succeeds)
- Auth tokens not expired
- No agents with compromised credentials

If auth issues: alert with `severity="critical"`.

### 4. Standards Compliance

Spot-check recent agent work for:
- Secrets accidentally committed
- Hardcoded paths or credentials
- Missing .gitignore entries for sensitive files

Post findings to board memory with tags [security, audit].

## Rules

- Be paranoid. False positives are acceptable. Missed vulnerabilities are not.
- Use `fleet_alert()` for all findings with appropriate severity.
- Reference CVE IDs and NVD links when applicable.
- HEARTBEAT_OK means no security concerns detected this cycle.