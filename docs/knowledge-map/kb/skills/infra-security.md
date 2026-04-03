# infra-security

**Type:** Skill (AICP Lifecycle)
**Location:** devops-expert-local-ai/.claude/skills/infra-security/
**Invocation:** /infra-security
**Effort:** high
**Roles:** DevSecOps

## What It Does

Infrastructure security review: container image vulnerabilities, network exposure, port bindings, volume permissions, secret handling, dependency CVEs, TLS configuration. Produces a security posture report with findings and remediation steps.

## Fleet Use Case

DevSecOps reviews fleet infrastructure security. Key surfaces: Docker containers (127.0.0.1 binding), PostgreSQL (password in .env), Redis (no auth by default), LightRAG API (optional auth), LocalAI (no auth). All ports should bind to localhost only in development.

## Relationships

- USED BY: devsecops-expert
- CONNECTS TO: fleet-security-audit skill (code + infra combined audit)
- CONNECTS TO: Semgrep MCP (code pattern analysis)
- CONNECTS TO: Docker MCP (container inspection)
- CONNECTS TO: config-secrets skill (secret handling review)
- CONNECTS TO: sage plugin (Agent Detection and Response)
