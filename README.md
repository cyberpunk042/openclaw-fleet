# OpenClaw Fleet

AI agent workforce powered by [OpenClaw](https://openclaw.ai) + [Mission Control](https://github.com/abhi1693/openclaw-mission-control).

## Prerequisites

- Python 3.11+
- Docker + Docker Compose
- [Claude Code](https://claude.ai/claude-code) CLI (`npm install -g @anthropic-ai/claude-code`)
- Claude Code authenticated (`claude auth login`)
- Git, curl, jq

## Setup

```bash
git clone <this-repo>
cd openclaw-fleet
./setup.sh
```

Setup handles everything: installs OpenClaw, configures auth, registers agents, starts Mission Control (Docker), starts the gateway, provisions agent credentials, pushes SOUL.md instructions.

## Usage

### Task lifecycle

```bash
# Create and dispatch a task to an agent
make create-task TITLE="Fix the auth module" AGENT=software-engineer DESC="..." DISPATCH=true

# Or create first, dispatch later
make create-task TITLE="Review architecture" AGENT=architect
make dispatch AGENT=architect TASK=<uuid>

# Monitor a task
make monitor TASK=<uuid>

# Chat with agents via board memory
make chat MSG="Status update please"
make chat MSG="@architect review the gateway config"
```

### Fleet management

```bash
make status          # agents, tasks, activity overview
make provision       # re-sync after SOUL.md or config changes
make refresh-auth    # refresh Claude Code token + restart gateway
make agents          # list OpenClaw agents
```

### Infrastructure

```bash
make gateway         # start OpenClaw gateway
make gateway-stop    # stop gateway
make gateway-restart # restart gateway
make mc-up           # start Mission Control (Docker)
make mc-down         # stop Mission Control
make mc-logs         # tail MC logs
make logs            # tail gateway logs
```

### Code integration

```bash
# Integrate agent work into a target project
make integrate TASK=<uuid> TARGET=/path/to/project

# Creates a branch, copies agent files, commits.
# Add --push to push, --pr to create a PR.
```

### Auto-start on boot

```bash
bash scripts/install-service.sh
systemctl --user start openclaw-fleet-gateway
loginctl enable-linger $USER
```

## Architecture

```
Human → make create-task / chat
  ↓
Mission Control (Docker: Postgres, Redis, FastAPI, Next.js)
  ↓ chat.send via WebSocket
OpenClaw Gateway (ws://localhost:18789)
  ↓ Claude Code CLI backend
Agent (reads TOOLS.md → does work → calls MC REST API)
  ↓
Mission Control (task updates, comments, board memory)
  ↓
Human → make status / monitor / integrate
```

## Agents

| Agent | Mode | Role |
|-------|------|------|
| architect | think | System design, architecture review |
| software-engineer | edit | Implementation, bug fixes, tests |
| qa-engineer | act | Testing, validation, coverage |
| ux-designer | think+edit | UI design, accessibility |
| devops | act | CI/CD, infrastructure, deployment |
| technical-writer | edit | Documentation |
| accountability-generator | think+edit | Accountability systems (ocf-tag) |

Agent definitions: `agents/<name>/agent.yaml` + `SOUL.md`

## Project Structure

```
openclaw-fleet/
├── setup.sh                    # Full setup from scratch
├── Makefile                    # All operations
├── docker-compose.yaml         # Mission Control services
├── agents/                     # Agent definitions
│   ├── _template/              # Shared template (MC_WORKFLOW.md, .claude/settings.json)
│   ├── architect/              # Agent role + config
│   └── ...
├── scripts/
│   ├── configure-auth.sh       # Claude Code → OpenClaw auth bridge
│   ├── configure-openclaw.sh   # Exec approval, CLI backend, permissions
│   ├── create-task.sh          # Create MC tasks from CLI
│   ├── dispatch-task.sh        # Dispatch tasks via gateway
│   ├── monitor-task.sh         # Monitor task progress
│   ├── chat-agent.sh           # Human↔agent board memory chat
│   ├── fleet-status.sh         # Fleet overview
│   ├── integrate-task.sh       # Workspace → project code integration
│   ├── push-soul.sh            # Push SOUL.md to agent workspaces
│   ├── refresh-auth.sh         # Detect and refresh rotated tokens
│   ├── install-service.sh      # Install systemd user service
│   └── ...
├── gateway/                    # Fleet gateway (Python)
├── config/                     # Fleet configuration
├── systemd/                    # Service template (rendered by install-service.sh)
├── vendor/                     # Mission Control (cloned at setup)
└── workspace-mc-*/             # Agent workspaces (gitignored, MC-provisioned)
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Agents failing with 401 | `make refresh-auth` (token rotated) |
| Agents blocked on exec approval | `bash scripts/configure-openclaw.sh` |
| MC not reachable | `make mc-up` |
| Gateway not starting | Check port 18789, validate `~/.openclaw/openclaw.json` |
| Task stuck in inbox | `make dispatch AGENT=<name> TASK=<uuid>` |

## Built with AICP

Developed and operated using [AICP](https://github.com/jfortin/devops-expert-local-ai) — AI Control Platform.