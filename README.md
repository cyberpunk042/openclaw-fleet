# OpenClaw Fleet

An AI agent workforce powered by [OpenClaw Mission Control](https://github.com/abhi1693/openclaw-mission-control).

## What Is This

OpenClaw Fleet operates a team of specialized AI agents that collaborate to build, maintain, and operate software. Mission Control provides the operations surface — UI, task management, approvals, audit trails. Our gateway executes work through Claude Code and LocalAI.

```
User ──→ Mission Control (UI/API)
              │
              ├── Agent management
              ├── Task boards & approvals
              ├── Activity log
              │
              └── Gateway ──→ OCF Gateway (this repo)
                                  │
                                  ├── Claude Code CLI
                                  ├── LocalAI
                                  └── Agent-specific logic
```

## Agent Roster

### Core Agents (workforce)

| Agent | Role |
|-------|------|
| **Architect** | System design, architecture review, component structure |
| **Software Engineer** | Code implementation, features, bug fixes, refactoring |
| **UX Designer** | Interface design, user flows, accessibility |
| **QA Engineer** | Testing, validation, quality assurance |
| **DevOps** | CI/CD, deployment, infrastructure, monitoring |
| **Technical Writer** | Documentation, API docs, guides, changelogs |

### Mission Agents

| Agent | Initiative |
|-------|-----------|
| **Accountability Generator** | Evidence-to-pressure system for civic accountability |

## Quick Start

```bash
# Clone
git clone <repo-url>
cd openclaw-fleet

# Configure
cp .env.example .env
# Edit .env with your settings

# Start (Mission Control + Gateway)
docker compose up -d

# Access Mission Control
open http://localhost:3000
```

## Architecture

See [docs/architecture.md](docs/architecture.md).

## Built with AICP

This project is developed and operated using [AICP](https://github.com/jfortin/devops-expert-local-ai) — AI Control Platform.