# claude-mem

**Type:** Claude Code Plugin (with internal MCP server + worker service)
**Source:** github.com/thedotmack/claude-mem — 44,666 stars, AGPL-3.0
**Docs:** https://docs.claude-mem.ai
**Assigned to:** ALL agents

## What It Actually Is

Not just a plugin — it's an entire memory SYSTEM with 5 lifecycle hooks, 4 MCP search tools, a background worker service (Express.js on port 37777), dual storage (SQLite + ChromaDB), and a web UI for settings and memory stream visualization. Requires ANTHROPIC_API_KEY because it uses the Claude Agent SDK to compress observations in the background.

## How It Works

```
Agent works in Claude Code session
├── 5 hooks capture everything:
│   ├── SessionStart → inject past context (recent summaries + observations)
│   ├── UserPromptSubmit → capture user intent
│   ├── PostToolUse → capture EVERY tool execution (read, write, edit, bash, etc.)
│   ├── Summary → capture session summaries
│   └── SessionEnd → cleanup, final observations
├── Observations sent to worker (HTTP → port 37777)
├── Worker compresses observations using Claude Agent SDK (background, async)
├── Stored in dual database:
│   ├── SQLite (source of truth, ACID, FTS5 full-text search)
│   └── ChromaDB (vector embeddings for semantic search) ← DISABLE ON WSL2
└── At next session start:
    ├── SessionStart hook queries recent summaries (10) + observations (50)
    └── Injects via hookSpecificOutput.additionalContext (silent, no user message)
```

## 4 MCP Search Tools

The 3-layer progressive disclosure pattern saves ~10x tokens vs naive RAG:

1. **search** — full-text search across all observations. Returns compact INDEX table (~50-100 tokens per result). AND/OR/NOT/phrase support. Order by date or relevance.

2. **timeline** — chronological view around a specific observation. Anchor ID + depth_before/after. Project-scoped.

3. **get_observations** — fetch FULL details for specific observation IDs (from search/timeline results). This is where the detail lives (~500-1000 tokens per observation).

4. **__IMPORTANT** — context/instruction tool.

**Workflow:** search (20 results = ~2K tokens) → identify 3 relevant IDs → get_observations (3 details = ~3K tokens) → total ~5K vs ~50K for dumping everything.

## CRITICAL: WSL2 Configuration

**ChromaDB MUST be disabled on WSL2.** Three documented issues:

- **Issue #1063 (spawn storm):** Killing worker with 6+ sessions caused 641 chroma-mcp processes, 75%+ CPU, ~64GB virtual memory, nearly crashed WSL2. This was on WSL2 specifically.

- **Issue #707 (35GB RAM):** ChromaDB can consume 35GB+ RAM loading vector DB on macOS.

- **Issue #1077 (OOM):** 146 orphaned chroma-mcp processes never cleaned up, consumed 5.6GB on 32GB machine.

**Mitigation:** SQLite-only mode. Set in `~/.claude-mem/settings.json`:
```json
{ "chromaEnabled": false }
```
This keeps full-text search (FTS5) but loses semantic/vector search. LightRAG can provide semantic search as a separate system.

## OpenClaw Gateway Integration

Explicit support exists:
- One-liner installer: `curl -fsSL https://install.cmem.ai/openclaw.sh | bash`
- Plugin exports `claudeMemPlugin()` for OpenClaw gateway API
- Subscribes to 7 OpenClaw lifecycle events
- Commands: `/claude-mem-status`, `/claude-mem-feed`

**Known bugs:** Issue #1106 (missing openclaw.extensions field), Issue #1471 (MCP server not registered properly in marketplace root .mcp.json).

## Fleet Relevance

| Aspect | Value |
|--------|-------|
| Cross-session continuity | Agents retain knowledge across session restarts, prunes, compacts |
| Shared memory | Multiple agents share ~/.claude-mem/ — one agent's discoveries visible to all |
| Token savings | 3-layer search = 10x reduction vs dumping full context |
| Heartbeat context | Recall without Claude costs (local SQLite FTS, not LLM) |
| Project-scoped | Observations tagged by working directory → project-specific recall |
| Context recovery | After /compact or /clear, agent searches claude-mem to recover key facts |

## Compared to Built-in .claude/memory/

| Feature | Built-in Memory | claude-mem |
|---------|----------------|------------|
| Storage | Git-tracked .md files | SQLite + (optionally) ChromaDB |
| Capture | Corrections only (auto-memory) | ALL tool executions (automatic) |
| Search | None — Claude reads index, guesses | FTS5 + semantic (if ChromaDB enabled) |
| Token cost | Free (files in context, 200-line cap) | Background API calls for compression |
| Complexity | Zero | Significant (worker, Bun, ChromaDB) |
| Reliability | Rock solid | Known process management issues |
| Scalability | 200-line index cap | Thousands of observations |

**They are COMPLEMENTARY.** Built-in = lightweight preferences. claude-mem = large-scale recall with search.

## Relationships

- INSTALLED BY: scripts/install-plugins.sh (from agent-tooling.yaml)
- CONFIGURED BY: ~/.claude-mem/settings.json (chromaEnabled: false for WSL2)
- REQUIRES: ANTHROPIC_API_KEY (background observation compression)
- WORKER: Express.js on port 37777 (managed by Bun daemon)
- HOOKS: SessionStart (inject), PostToolUse (capture), SessionEnd (cleanup)
- CONNECTS TO: knowledge map (map indexes claude-mem observations)
- CONNECTS TO: LightRAG (semantic search complement — claude-mem SQLite has FTS, LightRAG has graph+vectors)
- CONNECTS TO: session_manager.py (brain Step 10 — context recovery after compact uses claude-mem)
- CONNECTS TO: heartbeat_gate.py (brain evaluates agent state — claude-mem data available locally)
- CONNECTS TO: .claude/memory/ (different system — file-based vs database, both persist)
- CONNECTS TO: trail system (claude-mem observations become searchable trail)
- CONNECTS TO: PreCompact hook (save key decisions to claude-mem BEFORE compact)
