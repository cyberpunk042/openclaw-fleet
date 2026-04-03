# /agents

**Type:** Claude Code Built-In Command
**Category:** Agents & Tasks
**Available to:** ALL agents (especially Architect, Fleet-ops)

## What It Actually Does

Manage subagent configurations. Shows available custom subagents defined in `.claude/agents/` directory. Subagents are specialized autonomous workers with their own model, tools, permissions, and skills — spawned by Claude for complex subtasks.

Custom agents are defined as markdown files (`.claude/agents/<name>.md`) with frontmatter specifying: name, description, tools, disallowedTools, model, permissionMode, maxTurns, skills, mcpServers, hooks, memory, background, effort, isolation, color, initialPrompt.

## When Fleet Agents Should Use It

**Task decomposition:** Architect spawning parallel design review agents for different components.

**Parallel work:** Engineer using /batch which spawns subagents per worktree.

**Specialized work:** Creating a temporary agent with specific tools/permissions for a narrow task.

## Built-In Subagent Types

| Type | Model | Tools | Purpose |
|------|-------|-------|---------|
| Explore | Haiku | Read-only | Fast codebase exploration |
| Plan | Inherited | Read-only | Design implementation plans |
| general-purpose | Inherited | All | Multi-step tasks |
| statusline-setup | Sonnet | Read, Edit | Configure statusline |
| claude-code-guide | Haiku | Web, Read | Answer questions about Claude Code |

## Relationships

- MANAGES: .claude/agents/ directory (custom agent definitions)
- SPAWNS: Agent tool (launches subagents from definitions)
- CONNECTS TO: Agent Teams (CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS — multi-agent collaboration)
- CONNECTS TO: /batch command (uses subagents for parallel work)
- CONNECTS TO: dispatching-parallel-agents skill (Superpowers — concurrent subagent work)
- CONNECTS TO: subagent-driven-development skill (Superpowers — fresh subagent per task)
- CONNECTS TO: SubagentStart/SubagentStop hooks (lifecycle events for subagents)
- CONNECTS TO: fleet dispatch model (fleet orchestrator dispatches TO agents, not VIA subagents — different pattern)
