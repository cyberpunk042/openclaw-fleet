# claude-mem

**Type:** Claude Code Plugin
**Source:** github.com/thedotmack/claude-mem (45K stars)
**Assigned to:** ALL agents

## Purpose

Cross-session memory. Captures every tool execution, compresses observations, stores in SQLite, provides 4 MCP search tools (search, timeline, get_observations). 10x token savings via 3-layer progressive disclosure.

## Configuration

SQLite-only mode for WSL2 (avoids ChromaDB spawn storms). Worker on port 37777. Needs ANTHROPIC_API_KEY for compression.

## Relationships

knowledge map (indexes observations), LightRAG (semantic complement), session_manager.py (context recovery), agent_lifecycle.py (recall without Claude costs), SessionStart hook (injects past context)
