# CLAUDE.md — OpenClaw Fleet

## Project Overview

OpenClaw Fleet (OCF) is an AI agent workforce built on top of OpenClaw Mission Control. It operates specialized agents that collaborate to build software, conduct analysis, and execute missions.

## Architecture

```
Mission Control (UI/API) ──→ OCF Gateway ──→ Claude Code / LocalAI
```

- **Mission Control**: Central operations surface (FastAPI + Next.js + Postgres + Redis)
- **OCF Gateway**: Python service that receives work from Mission Control and executes via AI backends
- **Agents**: Specialized definitions with mission, capabilities, context, and constraints

## Tech Stack

- **Gateway**: Python 3.11+
- **Mission Control**: FastAPI (Python) + Next.js (TypeScript)
- **Database**: PostgreSQL 16 (via Mission Control)
- **Queue**: Redis 7 (via Mission Control)
- **AI Backends**: Claude Code CLI (primary), LocalAI (lightweight tasks)
- **Deployment**: Docker Compose

## Project Structure

```
gateway/          # OCF Gateway service
agents/           # Agent definitions and source
  architect/      # System design agent
  software-engineer/  # Implementation agent
  ux-designer/    # Interface design agent
  qa-engineer/    # Quality assurance agent
  devops/         # Infrastructure agent
  technical-writer/   # Documentation agent
  accountability-generator/  # First mission agent (ocf-tag)
config/           # Fleet configuration
integrations/     # Mission Control adapter
tests/            # Test suite
docs/             # Documentation
```

## Development Conventions

- Python: type hints, pytest, ruff for lint/format
- Each agent has: agent.yaml (config), CLAUDE.md (AI instructions), context/ (knowledge)
- Tests mirror source structure
- Config via environment variables, .env files
- Docker for all services

## Key Principles

1. Mission Control is the center — we feed it, we don't replace it
2. Agents are specialists — clear roles, clear boundaries
3. Claude Code does the heavy lifting — our code orchestrates
4. Everything is tracked — mission-control logs all activity
5. User is always in control — approvals, budgets, mode restrictions