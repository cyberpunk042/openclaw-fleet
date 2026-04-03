# security-guidance

**Type:** Claude Code Plugin (Official Anthropic)
**Source:** Anthropic marketplace
**Installed for:** DevSecOps

## What It Does

Monitors 9 security patterns via hooks. Fires on PostToolUse to check for security anti-patterns in code changes — SQL injection, XSS, command injection, hardcoded secrets, insecure crypto, path traversal, SSRF, deserialization, and authentication bypass.

## Fleet Use Case

DevSecOps (Cyberpunk-Zero) is the security layer. security-guidance runs automatically on every tool use in the devsecops agent's session — catching security issues as they happen, not just at review time.

Also valuable as a default for ALL agents (currently devsecops only) — but that's a PO decision on plugin count per agent.

## Relationships

- INSTALLED FOR: devsecops-expert
- FIRES VIA: PostToolUse hook (automatic, every tool call)
- CONNECTS TO: fleet-security-audit skill (broader security review)
- CONNECTS TO: fleet_alert tool (flag security issues)
- CONNECTS TO: PreToolUse hook (safety-net catches destructive commands, security-guidance catches code patterns)
- CONNECTS TO: OWASP Top 10 (9 patterns map to OWASP categories)
