# Claude-Mem — Cross-Session Memory Infrastructure

**Type:** Infrastructure Component
**Source:** github.com/thedotmack/claude-mem
**Version:** v10.5.2+
**Stars:** ~37.2K
**License:** AGPL-3.0
**Port:** 37777 (per-instance worker)

## What Claude-Mem Is

A cross-session memory plugin for Claude Code. Captures tool usage during sessions, compresses it via AI into structured observations (97% token reduction), stores in SQLite + ChromaDB, and injects relevant history into future sessions via SessionStart hook. Progressive disclosure via 4 MCP tools achieves ~10x token savings vs bulk RAG retrieval.

For the fleet: each agent gets persistent memory across sessions — learnings, decisions, patterns, gotchas. Combined with LightRAG (graph RAG) and auto-memory (MEMORY.md), this creates a three-layer knowledge pipeline.

## Storage Architecture

### Dual-Database Strategy

| Store | Technology | Purpose | Path |
|-------|-----------|---------|------|
| Primary | SQLite (WAL mode) | Source of truth, FTS5 full-text search | `~/.claude-mem/claude-mem.db` |
| Semantic | ChromaDB | Vector similarity search | `~/.claude-mem/vector-db/` |

ChromaDB can be DISABLED (`CLAUDE_MEM_CHROMA_ENABLED=false`) — SQLite-only mode. Important for RAM: ChromaDB can consume 35GB+ on macOS.

### SQLite Schema (5 tables)

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `sdk_sessions` | Session tracking | dual IDs (sdk + claude), project, status, timestamps |
| `observations` | Compressed tool memories | title, narrative, facts (JSON), concepts (JSON), files, type, content_hash |
| `session_summaries` | End-of-session summaries | request, investigated, learned, completed, next_steps |
| `user_prompts` | User input history | prompt_text, prompt_number |
| `pending_messages` | Async processing queue | status (pending/processing), self-healing after 60s |

### FTS5 Full-Text Search (3 virtual tables)

- `observations_fts` — indexes title, subtitle, narrative, text, facts, concepts
- `session_summaries_fts` — indexes all summary fields
- `user_prompts_fts` — indexes prompt text
- Trigger-based sync on INSERT/UPDATE/DELETE
- Boolean operators: AND, OR, NOT, phrases, column-specific (`title:auth`)

### Deduplication

SHA-256 content hash of `{title, narrative, facts}`. 30-second dedup window prevents duplicate observations.

## 4 MCP Tools (Progressive Disclosure)

### Layer 1: `search` — Index Discovery (~50-100 tokens/result)

Find relevant memories. Parameters: query (FTS5), limit, offset, type, obs_type, project, dateStart, dateEnd, orderBy. Returns compact index with IDs + titles.

### Layer 2: `timeline` — Chronological Context (~100-200 tokens/observation)

Navigate around a specific memory. Parameters: anchor (observation ID), query, depth_before, depth_after, project. Returns chronological neighborhood.

### Layer 3: `get_observations` — Full Detail (~500-1000 tokens/result)

Fetch complete observation data. Parameters: ids (array), orderBy, limit, project. Returns full structured observations.

### Layer 4: `__IMPORTANT` — Workflow Documentation

Auto-displayed reminder of the 3-layer workflow. No invocation needed.

**Typical query budget:** ~3,000 tokens total (search 10 results → timeline → 3 full observations) vs ~20,000 for traditional RAG.

## Observation Types and Concepts

### 6 Observation Types

bugfix, feature, refactor, discovery, decision, change

### 7 Concept Tags

how-it-works, why-it-exists, what-changed, problem-solution, gotcha, pattern, trade-off

### Hierarchical Compression Fields

| Field | ~Tokens | Purpose |
|-------|---------|---------|
| title | 5-10 | One-line summary |
| subtitle | 10-20 | Additional context |
| narrative | 100-300 | What happened and why |
| facts | 50-200 | Technical details (JSON array) |
| concepts | 20-100 | Domain concepts (JSON array) |
| files_read | 10-50 | Files accessed |
| files_modified | 10-50 | Files changed |

**Compression ratio:** ~97% savings vs raw session transcripts.

## Integration with Claude Code (5 Hooks)

| Hook | Trigger | Function |
|------|---------|----------|
| SessionStart | Session begins | Inject MEMORY.md from past observations |
| UserPromptSubmit | User sends prompt | Record input for history |
| PostToolUse | Tool executes | Queue observation for AI compression |
| Stop (Summary) | Session ending | Generate session summary |
| SessionEnd | Session complete | Mark session complete |

**Fire-and-return pattern** — hooks immediately return exit 0 while queuing work asynchronously. Avoids 30s/120s hook timeouts.

## Advanced Features

### AI Compression Providers (3)

| Provider | Model Default | Cost |
|----------|-------------|------|
| Claude (SDK) | sonnet | Expensive (spawns CLI subprocess) |
| Gemini | gemini-2.5-flash-lite | Cheap |
| OpenRouter | xiaomi/mimo-v2-flash:free | FREE |

### Endless Mode (Beta — Experimental)

Biomimetic architecture: working memory (compressed, in-context) + archive memory (full, on disk). Changes scaling from O(N²) to O(N). Theoretical 20x tool calls per session (~1000 vs ~50). **60-90s latency per tool call.** Not battle-tested.

### Privacy Controls

`<private>content</private>` tags exclude sensitive content from storage. Stripped at hook layer.

### Self-Healing

- Pending messages stuck >60s in `processing` auto-reset to `pending`
- Orphan reaper: every 30s, kills SDK processes not in active sessions
- Stale session reaper: every 2m, marks sessions >6h inactive as `failed`

### HTTP REST API (22+ endpoints)

Full API on port 37777. **No authentication.** Key endpoints:
- `GET /api/observations` — paginated observations
- `GET /api/stats` — DB statistics by project
- `GET /api/context/inject` — generate MEMORY.md for injection
- `POST /sessions/:id/observations` — add observation
- `GET /stream` — SSE feed of events

External tools CAN query this API — enables fleet integration.

## Configuration Reference (Key Settings)

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAUDE_MEM_DATA_DIR` | `~/.claude-mem` | Data directory (isolate per agent) |
| `CLAUDE_MEM_WORKER_PORT` | `37777` | HTTP API port (unique per agent) |
| `CLAUDE_MEM_PROVIDER` | `claude` | AI provider (claude/gemini/openrouter) |
| `CLAUDE_MEM_MODEL` | `sonnet` | Model for compression |
| `CLAUDE_MEM_CHROMA_ENABLED` | `true` | Enable/disable ChromaDB |
| `CLAUDE_MEM_CONTEXT_OBSERVATIONS` | `50` | Observations injected per session |
| `CLAUDE_MEM_CONTEXT_SESSION_COUNT` | `10` | Sessions to pull from |
| `CLAUDE_MEM_CONTEXT_FULL_COUNT` | `5` | Observations with expanded detail |
| `CLAUDE_MEM_SKIP_TOOLS` | 5 tools | Tools to skip observation for |
| `CLAUDE_MEM_MODE` | `code` | Mode profile |

## Fleet Deployment Architecture

### Recommended: Per-Agent Instances

```
Agent 1 → claude-mem worker (port 37771, data: ~/.claude-mem-agent1/)
Agent 2 → claude-mem worker (port 37772, data: ~/.claude-mem-agent2/)
...
Agent 10 → claude-mem worker (port 37780, data: ~/.claude-mem-agent10/)
```

Each agent gets:
- Own SQLite database (no locking contention)
- Own port (no conflicts)
- Own data directory (clean isolation)
- Own provider settings (some agents use free OpenRouter, critical agents use Claude)

### Integration with LightRAG (Cross-Agent Knowledge)

```
Per-Agent claude-mem instances (isolated memory)
     |
     v  (periodic sync via HTTP API)
LightRAG Indexer
     |-- Reads observations from each agent's GET /api/observations
     |-- Extracts entities from facts/concepts/files
     |-- Builds cross-agent knowledge graph
     |
     v
LightRAG Graph Store (unified fleet knowledge)
     |-- Any agent can query cross-agent knowledge
     |-- Graph traversal finds related observations across agents
     |-- MCP server makes it available to all agents
```

**claude-mem provides per-agent memory. LightRAG provides cross-agent knowledge.**

### Three-Layer Knowledge Pipeline

| Layer | System | Scope | Storage | Injection |
|-------|--------|-------|---------|-----------|
| Per-project state | Auto-memory (MEMORY.md) | Per-project, human-curated | Markdown files | Loaded at session start (200 lines) |
| Per-agent memory | claude-mem | Per-agent, AI-compressed | SQLite + ChromaDB | SessionStart hook (configurable depth) |
| Cross-agent knowledge | LightRAG | Fleet-wide, graph-indexed | Graph DB + Vector DB | MCP tools / HTTP API |

## Limitations

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| No knowledge graph | Observations are isolated, not interconnected | LightRAG provides the graph layer |
| No memory decay/forgetting | Database grows indefinitely | AutoDream (external) or manual pruning |
| No importance scoring | All observations weighted equally | LightRAG reranking on query |
| No multi-agent support | Single worker, no agent namespacing | Per-agent instances (different ports/dirs) |
| ChromaDB RAM consumption | 35GB+ possible | Disable with CLAUDE_MEM_CHROMA_ENABLED=false |
| No authentication on API | All data exposed on port | Bind to localhost only, firewall |
| No LocalAI as provider | Can't use local models for compression | OpenRouter free tier as alternative |
| SQLite locking under concurrency | SQLITE_BUSY errors | Per-agent isolated databases |

## Relationships

- INSTALLED AS: Claude Code plugin (per agent)
- STORES: per-agent cross-session memory (observations, summaries, prompts)
- INJECTS VIA: SessionStart hook (MEMORY.md generation)
- CAPTURES VIA: PostToolUse hook (async observation creation)
- CONNECTS TO: LightRAG (observations → entity extraction → knowledge graph)
- CONNECTS TO: auto-memory (MEMORY.md) (complementary — different scopes)
- CONNECTS TO: knowledge map (claude-mem captures what agents LEARN, map captures what agents KNOW)
- CONNECTS TO: agent-tooling.yaml (installed as default plugin for ALL agents)
- CONNECTS TO: IaC scripts (install-plugins.sh provisions claude-mem)
- CONNECTS TO: trail system (observations ≈ trail events, but compressed)
- CONNECTS TO: session_manager.py (context injection at session start)
- CONNECTS TO: budget system (compression costs tracked per provider)
- CONNECTS TO: AICP rag.py (AICP's RAG module — claude-mem ChromaDB is a vector store)
