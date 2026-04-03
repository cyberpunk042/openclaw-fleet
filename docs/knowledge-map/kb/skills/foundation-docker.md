# foundation-docker

**Type:** Skill (AICP)
**Location:** devops-expert-local-ai/.claude/skills/foundation-docker/SKILL.md
**Invocation:** /foundation-docker
**Effort:** medium
**Allowed tools:** Read, Write, Edit, Bash, Glob, Grep

## Purpose

Containerize the project with multi-stage Dockerfile, docker-compose with services/volumes/networking, .dockerignore, and Makefile targets. Production image must be minimal. Dev compose must support hot reload. Never bake secrets. Always include health checks.

## Process

1. Analyze project structure and dependencies
2. Create `Dockerfile`:
   - Multi-stage build (builder + runtime) — minimal final image
   - Non-root user for security
   - Health check endpoint
   - Proper layer caching (deps installed before code copied)
3. Create `docker-compose.yaml`:
   - Application service
   - Database service if needed
   - Volume mounts for development (hot reload)
   - Environment variables from .env
   - Port mappings
   - Network configuration
4. Create `.dockerignore` (appropriate for tech stack)
5. Add Makefile targets: `build`, `up`, `down`, `logs`
6. Test: `docker compose up` works

## Rules

- Production image: as SMALL as possible (multi-stage, minimal base)
- Dev compose: support hot reload via volume mounts
- NEVER bake secrets into images (use .env + env_file)
- ALWAYS include health checks

## Assigned Roles

| Role | Priority | Why |
|------|----------|-----|
| DevOps | ESSENTIAL | Core infrastructure skill |
| Engineer | RECOMMENDED | Engineers containerize their services |

## Methodology Stages

| Stage | Usage |
|-------|-------|
| work | Create containerization after project scaffolded |

## Relationships

- FOLLOWS: scaffold (project structure must exist), foundation-deps (dependencies defined)
- FOLLOWED BY: ops-deploy (deploy using these containers)
- FOLLOWED BY: foundation-ci (CI builds these containers)
- CONNECTS TO: docker MCP server (agents can manage containers via MCP)
- CONNECTS TO: LocalAI docker-compose (fleet's own Docker setup)
- CONNECTS TO: OCMC docker-compose (MC + PostgreSQL + Redis)
- CONNECTS TO: ops-maintenance skill (container updates, base image patches)
- CONNECTS TO: IaC principle — Docker configs committed to git, reproducible from fresh clone
- OUR FLEET: LocalAI runs via docker-compose.yaml with GPU passthrough (WSL2 /dev/dxg, 8GB VRAM)
