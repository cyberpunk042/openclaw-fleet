# /effort

**Type:** Claude Code Built-In Command
**Category:** Model & Effort
**Available to:** ALL agents

## What It Actually Does

Sets the extended thinking effort level — how much reasoning Claude does before responding. Four levels: low, medium (default), high, max (Opus only, current session only). Higher effort = more thinking tokens before responding = better reasoning for complex problems = more expensive.

The effort level persists across sessions (except max, which is session-only). Can also be set via `CLAUDE_CODE_EFFORT_LEVEL` env var, skill frontmatter `effort:` field, or subagent frontmatter.

Keyword trigger: include "ultrathink" in a prompt for one-turn high effort without changing the persistent setting.

## Effort Levels

| Level | Persistence | When to Use |
|-------|-------------|-------------|
| low | Across sessions | Simple updates, doc changes, routine commits. Quick responses, less reasoning. |
| medium | Default, across sessions | Standard implementation work. Balanced reasoning vs speed. |
| high | Across sessions | Architecture decisions, complex debugging, security analysis. Deep reasoning. |
| max | Current session ONLY | Critical security analysis, complex architecture that needs maximum reasoning. Opus only — Sonnet doesn't support max. Resets to default after session. |
| auto | Reset to default | Return to medium after temporary override. |

## Per-Role Defaults

The orchestrator's model_selection.py sets effort at dispatch:
- Complex/critical tasks → high effort
- Standard tasks → medium effort
- Simple/routine → low effort

Agents can OVERRIDE within session using /effort. Common pattern: dispatched with medium, agent hits a complex section → `/effort high` → resolves → `/effort medium`.

## When Fleet Agents Should Use It

| Role | Scenario | Level |
|------|----------|-------|
| Architect | Architecture decision with 3+ options | high |
| Architect | Complex pattern selection | high |
| DevSecOps | Security vulnerability analysis | high or max |
| DevSecOps | Threat model assessment | max |
| Engineer | Complex algorithm implementation | high |
| Engineer | Routine file edits | low |
| QA | Edge case analysis | high |
| PM | Sprint planning | medium |

## Relationships

- SET BY: model_selection.py at dispatch (effort per task complexity)
- OVERRIDDEN BY: agent within session (/effort command)
- SET BY: skill frontmatter (`effort: high` in SKILL.md)
- SET BY: subagent frontmatter (per-agent effort)
- CONNECTS TO: /model command (model + effort together control reasoning depth)
- CONNECTS TO: /fast command (fast mode = speed-optimized API, different from effort)
- CONNECTS TO: LaborStamp (effort field recorded in stamp)
- CONNECTS TO: S14 router (effort part of RoutingDecision)
- CONNECTS TO: injection-profiles.yaml (effort affects token budget)
- CONNECTS TO: S22 agent intelligence (escalation dimension — effort escalates with complexity)
- ENV VAR: CLAUDE_CODE_EFFORT_LEVEL (persistent override)
- KEYWORD: "ultrathink" in prompt → one-turn high (doesn't change persistent setting)
