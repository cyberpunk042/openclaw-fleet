# safety-net

**Type:** Claude Code Plugin
**Source:** github.com/kenryu42/claude-code-safety-net (1K stars)
**Assigned to:** ALL agents

## Purpose

PreToolUse hook that catches destructive git and filesystem commands before execution. Zero performance impact, passive protection.

## Configuration

Passive hook — only fires on pattern match. No configuration needed.

## Relationships

anti-corruption Line 1 (structural prevention), PreToolUse hook infrastructure, agent permissions (§53), trail system (blocked commands recorded), PO guardrails (preserve working state)
