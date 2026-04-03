# CwdChanged

**Type:** Claude Code Hook (lifecycle event)
**Category:** Workspace (fires when working directory changes)
**Handler types:** command, http, prompt, agent
**Can block:** NO (observation only)

## What It Actually Does

Fires when the current working directory changes within a Claude Code session. The handler can react by loading project-specific context, switching knowledge map scope, or updating the agent's understanding of which project it's working in.

## Fleet Use Case: Project Context Switching

```
CwdChanged fires (working directory changed)
├── Identify new project:
│   ├── openclaw-fleet/ → fleet context
│   ├── devops-expert-local-ai/ → AICP context
│   ├── devops-solution-product-development/ → DSPD context
│   └── Narrative-to-Neutral-Report-Transformer/ → NNRT context
├── Load project context:
│   ├── Read new project's CLAUDE.md
│   ├── Switch knowledge map scope
│   ├── Update available tools (project-specific MCP servers)
│   └── Adjust guardrails (project-specific paths)
├── Logging:
│   ├── Trail event: cwd_changed
│   └── Previous dir → new dir
└── Return: {} (observation only)
```

## Fleet Context

Fleet agents typically work in a single project directory (openclaw-fleet/) for the entire session. CwdChanged is more relevant for:
- **Cross-project work:** DevOps agent working on both fleet and AICP
- **Worktree operations:** /batch creates worktrees in different paths
- **AICP operations:** AICP controller working across multiple project directories

## Relationships

- FIRES ON: working directory change (cd or equivalent)
- CANNOT BLOCK: observation only
- CONNECTS TO: CLAUDE.md (new directory may have different project instructions)
- CONNECTS TO: InstructionsLoaded hook (may re-fire after directory change)
- CONNECTS TO: knowledge map (scope changes with project)
- CONNECTS TO: 4-project ecosystem (fleet, AICP, DSPD, NNRT)
- CONNECTS TO: WorktreeCreate hook (worktree creation may change cwd)
- TIER: low priority (fleet agents rarely change directories mid-session)
