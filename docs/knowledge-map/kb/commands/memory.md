# /memory

**Type:** Claude Code Built-In Command
**Category:** Configuration
**Available to:** ALL agents

## What It Actually Does

Two functions:
1. **Edit CLAUDE.md** — opens the project's CLAUDE.md for editing
2. **Toggle auto-memory** — enables/disables the automatic memory system (`~/.claude/projects/<project>/memory/MEMORY.md`)

Auto-memory writes memories to individual markdown files with frontmatter (name, description, type) and indexes them in MEMORY.md. Up to 200 lines of MEMORY.md are loaded into every conversation. Memory types: user, feedback, project, reference.

## When Fleet Agents Should Use It

**Auto-memory for fleet agents:** Each agent can accumulate knowledge across sessions — patterns learned, mistakes to avoid, project state. This complements claude-mem (cross-session memory via SQLite+ChromaDB).

**CLAUDE.md editing:** Agents should NOT edit their own CLAUDE.md. CLAUDE.md is managed by IaC scripts and the gateway. Self-modification risks anti-corruption violations.

**Memory as trail complement:** Auto-memory captures WHY decisions were made. Trail captures WHAT happened. Together they provide full audit history.

## Memory vs claude-mem vs Knowledge Map

| System | Scope | Storage | Injection |
|--------|-------|---------|-----------|
| Auto-memory (/memory) | Per-project, per-agent | Markdown files | Loaded at session start (200 lines) |
| claude-mem (plugin) | Cross-project, cross-session | SQLite + ChromaDB | MCP search tools on demand |
| Knowledge map | Fleet-wide, all agents | KB entries in docs/ | InstructionsLoaded hook + intent-map |

## Relationships

- MANAGES: ~/.claude/projects/<project>/memory/MEMORY.md
- MANAGES: CLAUDE.md (Layer 3 of 8-layer onion)
- CONNECTS TO: claude-mem plugin (complementary cross-session memory)
- CONNECTS TO: InstructionsLoaded hook (MEMORY.md loaded at session start)
- CONNECTS TO: SessionStart hook (memory restoration)
- CONNECTS TO: PreCompact hook (save key decisions to memory before context loss)
- CONNECTS TO: knowledge map (fleet-wide knowledge vs per-agent memory)
- CONNECTS TO: trail system (trail captures WHAT, memory captures WHY)
