# safety-net

**Type:** Claude Code Plugin (PreToolUse hook)
**Source:** github.com/kenryu42/claude-code-safety-net — 1,221 stars
**Assigned to:** ALL agents (non-negotiable — every agent gets this)

## What It Actually Is

A single PreToolUse hook that intercepts destructive commands before they execute. Passive — zero performance impact on normal operations. Only fires when the tool call matches destructive patterns. When triggered, it BLOCKS the operation and warns the agent, giving them a chance to reconsider.

This is the simplest, most impactful safety measure available. One plugin prevents the entire class of accidental data loss.

## What It Catches

**Destructive git commands:**
- `git reset --hard` — discards all uncommitted changes
- `git push --force` / `--force-with-lease` — overwrites remote history
- `git clean -f` / `-fd` — deletes untracked files/directories
- `git checkout .` / `git restore .` — discards working tree changes
- `git branch -D` — force-deletes branch

**Destructive filesystem commands:**
- `rm -rf` — recursive forced deletion
- `rm -r` on project directories
- `chmod -R 777` — wide-open permissions
- Patterns that could delete large trees of files

**What it does NOT catch:**
- Insecure code patterns (that's security-guidance plugin)
- Stage-inappropriate tool usage (that's PreToolUse stage enforcement hook)
- Logical errors in code (that's review + challenge system)

## How It Works

```
Agent calls Bash("git reset --hard")
├── PreToolUse hook fires (safety-net)
├── Pattern match: "git reset --hard" → DESTRUCTIVE
├── Hook returns: {deny: true, message: "⚠️ Destructive command blocked: git reset --hard"}
├── Agent sees the warning
├── Agent reconsiders (or explicitly overrides if they really mean it)
└── Original command NOT executed
```

Zero overhead for non-matching operations. The hook only activates on pattern match.

## Why It's Non-Negotiable for Fleet

The PO's collaboration rules say "Preserve working state. Never run destructive commands without explicit instruction." safety-net makes this STRUCTURAL — agents physically cannot accidentally destroy work.

In an autonomous fleet where 10 agents operate with bypassPermissions, one accidental `git reset --hard` or `rm -rf` could destroy hours of work. safety-net prevents this class of accident entirely.

The March 2026 catastrophe included gateway duplication that created parallel sessions — one of many things that could cascade. safety-net adds a structural safety layer at the individual agent level.

## Relationships

- HOOK TYPE: PreToolUse (intercepts before execution)
- INSTALLED BY: scripts/install-plugins.sh (from agent-tooling.yaml defaults)
- COMPLEMENTS: security-guidance plugin (safety-net = destructive commands, security-guidance = insecure code patterns)
- COMPLEMENTS: PreToolUse stage enforcement hook (safety-net = destructive patterns, stage hook = methodology violations)
- CONNECTS TO: anti-corruption Line 1 (structural prevention — the strongest defense)
- CONNECTS TO: agent permissions §53 (bypassPermissions makes safety-net even more critical)
- CONNECTS TO: trail system (blocked commands should be recorded as trail events)
- CONNECTS TO: doctor.py (if agent repeatedly triggers safety-net, that's a pattern worth detecting)
- CONNECTS TO: PO guardrails ("preserve working state" — this IS the preservation mechanism)
- CONNECTS TO: sage plugin (more comprehensive ADR — evaluates after safety-net proves the concept)
- ZERO RISK: passive, pattern-matching only. Cannot cause issues. Only prevents issues.
