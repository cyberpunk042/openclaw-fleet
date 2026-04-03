# config-secrets

**Type:** Skill (AICP Lifecycle)
**Location:** devops-expert-local-ai/.claude/skills/config-secrets/
**Invocation:** /config-secrets
**Effort:** medium
**Roles:** DevSecOps

## What It Does

Secret management and rotation: identify secrets in the codebase (API keys, tokens, passwords), ensure they're in environment variables (not hardcoded), set up rotation procedures, audit .env files, verify .gitignore protects secrets.

## Fleet Use Case

DevSecOps audits secrets across all fleet projects. Fleet uses: LOCAL_AUTH_TOKEN, PLANE_API_KEY, LIGHTRAG_API_KEY, CLAUDE_MEM_OPENROUTER_API_KEY, GITHUB_TOKEN. All must be in .env (gitignored), documented in .env.example (no real values).

## Relationships

- USED BY: devsecops-expert
- CONNECTS TO: foundation-auth skill (auth tokens are secrets)
- CONNECTS TO: foundation-config skill (config loader reads env vars)
- CONNECTS TO: .env.example (secrets template)
- CONNECTS TO: security-guidance plugin (detects hardcoded secrets)
- CONNECTS TO: fleet_alert tool (exposed secret → alert)
