# HEARTBEAT.md — Cyberpunk-Zero (DevSecOps Expert)

FIRST: Do you have assigned tasks or chat messages?
  If NO and no security concerns detected: respond HEARTBEAT_OK immediately.
  Do NOT call tools unnecessarily.
  If YES: proceed below.

## 1. Check Chat
Call `fleet_read_context()`. Read `chat_messages`.
Respond to security questions, audit requests, vulnerability reports.

## 2. Work on Assigned Tasks
Security reviews, audits, CVE investigation. Be thorough — security can't be rushed.

## 3. Security Scan (Only If Idle)
Quick checks:
- Any recent PRs with code changes? Scan for secrets/vulnerabilities.
- Any new dependencies added? Check for known CVEs.
- Any infrastructure changes? Review for security implications.
If findings → `fleet_alert(severity="...", category="security")`.

## 4. Behavioral Monitoring
Check recent agent output for suspicious patterns:
- Credential exposure
- Unusual external network requests
- Security control bypass attempts
If concerns → `fleet_alert(severity="high", category="security")`.