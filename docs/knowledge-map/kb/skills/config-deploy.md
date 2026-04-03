# config-deploy

**Type:** Skill (AICP Lifecycle)
**Location:** devops-expert-local-ai/.claude/skills/config-deploy/
**Invocation:** /config-deploy
**Effort:** medium
**Roles:** DevOps

## What It Does

Deployment configuration: set up deployment scripts, CI/CD pipeline configs, environment-specific settings, health checks, rollback triggers. Ensures deployments are reproducible and automated.

## Fleet Use Case

DevOps manages fleet deployment via docker-compose and IaC scripts. config-deploy ensures new services (like LightRAG) have proper deployment configuration: docker-compose entry, .env.example vars, health check, restart policy, setup script.

## Relationships

- USED BY: devops
- CONNECTS TO: ops-deploy skill (deploy executes, config-deploy configures)
- CONNECTS TO: foundation-docker skill (Docker-based deployments)
- CONNECTS TO: foundation-ci skill (CI/CD pipeline configuration)
- CONNECTS TO: docker-compose.yaml (fleet deployment manifest)
