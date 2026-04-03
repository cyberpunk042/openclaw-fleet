# /skills

**Type:** Claude Code Built-In Command
**Category:** Agents & Tasks
**Available to:** ALL agents

## What It Actually Does

Lists all skills available in the current session. Shows skills from: enterprise (managed), personal (~/.claude/skills/), project (.claude/skills/), and installed plugins. Each skill appears with its name and description.

This is the DISCOVERY mechanism — agents use /skills to see what capabilities they have. The output depends on which skills are deployed to the agent's workspace via scripts/deploy-skills.sh.

## When Fleet Agents Should Use It

**Orientation:** Agent starting a new task checks /skills to see what's available for this type of work.

**Stage transitions:** Moving from analysis to investigation — /skills shows which research skills are available.

**After plugin installation:** Verify new skills from installed plugins are visible.

## What It Shows

```
Available skills:
  /architecture-propose  — Propose a system architecture from an idea document
  /architecture-review   — Review an architecture document for gaps and risks
  /fleet-review          — How to review a task as board lead or QA reviewer
  /fleet-plan            — How to break down an epic into sprint tasks
  /feature-implement     — Implement a feature following project patterns
  ...
```

Skills come from:
1. AICP skills (devops-expert-local-ai/.claude/skills/) — symlinked to agent workspace
2. Fleet skills (openclaw-fleet/.claude/skills/) — symlinked to agent workspace
3. Plugin skills (installed plugins like Superpowers) — plugin provides them
4. Personal skills (~/.claude/skills/) — user-created

## Relationships

- SHOWS: skills deployed via scripts/deploy-skills.sh
- SHOWS: skills from installed plugins (superpowers, claude-skills, etc.)
- CONFIGURED BY: agent-tooling.yaml (per-role skill assignments)
- CONNECTS TO: methodology-manual.md (per-stage skill recommendations)
- CONNECTS TO: CLAUDE.md Layer 3 (agent's rules reference available skills)
- CONNECTS TO: TOOLS.md Layer 4 (tool reference may mention related skills)
- CONNECTS TO: /plan command (some skills work best in plan mode)
- CONNECTS TO: /debug command (debug is itself a bundled skill)
