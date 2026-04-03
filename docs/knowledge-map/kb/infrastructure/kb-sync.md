# KB Graph Sync — Direct KB-to-Graph Pipeline

**Type:** Infrastructure Component (Fleet Module)
**Source:** fleet/core/kb_sync.py
**CLI:** python -m fleet.core.kb_sync --full/--sync/--stats
**IaC:** scripts/setup-lightrag.sh --clean/--sync

## What It Does

Parses ## Relationships sections from all 219+ KB markdown entries and inserts entities + relationships directly into LightRAG via the graph API (/graph/entity/create, /graph/relation/create). No LLM needed. No ML models. The relationships are already written by hand in the KB — the parser just structures them for the graph.

## Why It Exists

LightRAG's LLM-based entity extraction with hermes 7B produced inconsistent, shallow results (32/0, 15/7, 21/21, 10/3 entities/relationships across runs). Our KB entries already have explicit, high-quality ## Relationships sections. The parser extracts what we already wrote — zero randomness, zero model dependency.

## How It Works

1. Parse every KB markdown file for title, type, description, branch
2. Extract ## Relationships section — each `- VERB: target (context)` line becomes an edge
3. Normalize entity names to UPPERCASE (LightRAG convention)
4. Insert entities via /graph/entity/create (populates graph + vector store)
5. Insert relationships via /graph/relation/create
6. Track file mtimes for incremental sync (.kb-graph-sync.json)

## Stats

- 1,545 entities (219 primary + 1,326 referenced targets)
- 2,295 relationships (from explicit ## Relationships lines)
- 13 entity types: system, tool, command, hook, skill, plugin, agent, mcp_server, layer, infrastructure, research, module, concept
- Top relationship verbs: connects to (1,189), depends on (70), used by (60), feeds (44)

## Modes

- `--full`: Parse all KB files, insert all entities and relationships
- `--sync`: Incremental — only files changed since last sync
- `--stats`: Dry run — show graph statistics without inserting
- `--clean` (via setup-lightrag.sh): Wipe graph, Redis cache, sync state, then full sync

## Relationships

- READS: docs/knowledge-map/kb/ (all 219+ KB entries)
- INSERTS INTO: LightRAG graph via /graph/entity/create and /graph/relation/create
- STORES STATE: .kb-graph-sync.json (file mtimes for incremental sync)
- CALLED BY: scripts/setup-lightrag.sh (--clean, --sync, --all)
- REPLACES: LLM-based extraction for KB content (lightrag-index.sh text insertion)
- COMPLEMENTS: LLM extraction for non-KB content (external docs, code files)
- CONNECTS TO: navigator (navigator queries LightRAG which now has KB sync data)
- CONNECTS TO: LightRAG Redis storage (entities + relationships in Redis DB 1)
