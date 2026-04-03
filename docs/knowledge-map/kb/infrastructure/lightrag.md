# LightRAG — Graph-Based RAG for Fleet Knowledge

**Type:** Infrastructure Component
**Source:** github.com/HKUDS/LightRAG
**Version:** 1.4.11+ (as of 2026-04-02)
**Port:** 9621
**Framework:** FastAPI
**Docker:** ghcr.io/hkuds/lightrag:latest

## What LightRAG Is

A graph-based Retrieval-Augmented Generation framework. Unlike traditional RAG (chunk → embed → retrieve), LightRAG builds a knowledge graph: entities + relationships extracted from documents, stored in a graph database, queried via entity/relationship traversal. This captures the STRUCTURE of knowledge, not just the content.

For the fleet: LightRAG indexes our 175+ KB entries and extracts the entity-relationship web that connects systems → tools → agents → hooks → commands → skills → plugins → layers. The graph IS the autocomplete map.

## Graph Construction Pipeline

```
Documents → Chunk (1200 tokens, 100 overlap)
         → Entity Extraction (LLM-based, with gleaning)
         → Relationship Extraction (binary pairs, keywords, descriptions)
         → Deduplication + Profiling (merge across documents)
         → Embedding (entities, relationships, chunks → 3 vector DBs)
         → Graph Storage (nodes + edges)
```

### Entity Extraction

- LLM extracts: entity_name, entity_type, entity_description
- **Custom entity types** — configurable per domain:
  ```
  ENTITY_TYPES=system,agent,command,hook,skill,plugin,layer,tool,module,workflow
  ```
- **Gleaning** — iterative re-prompting for completeness (default: 1 pass)
- Documents deduplicated by MD5 hash

### Relationship Extraction

- N-ary relationships decomposed into binary pairs
- Five fields: source_entity, target_entity, relationship_keywords, relationship_description, strength
- High-level keywords capture broader themes

### Three Embedding Spaces

| VDB Instance | What It Embeds | Used By |
|-------------|---------------|---------|
| `entities_vdb` | Entity descriptions | local, hybrid, mix queries |
| `relationships_vdb` | Relationship descriptions | global, hybrid, mix queries |
| `chunks_vdb` | Raw text chunks | naive queries |

## Six Query Modes

| Mode | Sources | When to Use |
|------|---------|-------------|
| **naive** | chunks_vdb only | Simple factual lookups, basic search |
| **local** | entities_vdb + entity chunks | "What is system X?" — entity-focused |
| **global** | relationships_vdb + relation chunks | "How are X and Y related?" — thematic |
| **hybrid** | entities + relationships | Balanced — both specific and thematic |
| **mix** | ALL three VDBs | **Best quality** — recommended with reranker |
| **bypass** | None (direct LLM) | Direct conversation, no retrieval |

### Query Pipeline

1. Extract low-level keywords `k_l` + high-level keywords `k_g` from query (via LLM)
2. Match against entity/relationship embeddings
3. Traverse neighboring nodes in graph (subgraph retrieval)
4. Assemble context from full entity/relation descriptions
5. Generate response with assembled context

### Token Budget Control

- `MAX_ENTITY_TOKENS` — budget for entity descriptions
- `MAX_RELATION_TOKENS` — budget for relationship descriptions
- `MAX_TOTAL_TOKENS` — total context window including system prompt
- `TOP_K` — entities/relations retrieved
- `CHUNK_TOP_K` — chunks for vector search

## Storage Backends

### Graph Storage

| Backend | Type | Use Case |
|---------|------|----------|
| **NetworkXStorage** | In-memory, file-persisted | Default, development, single machine |
| **Neo4JStorage** | Graph database | Production, large-scale, visualization |
| **PGGraphStorage** | PostgreSQL + AGE extension | All-in-one PostgreSQL |

### Vector Storage

| Backend | Type | Use Case |
|---------|------|----------|
| **NanoVectorDB** | In-memory | Default, development |
| **PGVectorStorage** | PostgreSQL + pgvector | Production |
| **ChromaVectorDB** | ChromaDB | Familiar to claude-mem users |
| **MilvusVectorDB** | Milvus | Enterprise-scale |
| **FaissVectorDB** | FAISS | GPU-accelerated similarity |
| **QdrantVectorDB** | Qdrant | Production vector search |

### KV Storage

| Backend | Type | Use Case |
|---------|------|----------|
| **JsonKVStorage** | File-based JSON | Default, development |
| **PGKVStorage** | PostgreSQL | Production |
| **RedisKVStorage** | Redis | High-speed caching |
| **MongoKVStorage** | MongoDB | Document-oriented |

### All-in-One

- **PostgreSQL**: KV + Vector (pgvector) + Graph (AGE) + DocStatus — single database
- **MongoDB**: KV + Vector + DocStatus
- **OpenSearch**: KV + Vector + Graph + DocStatus

## LLM Backend Integration

### LocalAI Integration (Our Setup)

```env
LLM_BINDING=openai
LLM_MODEL=hermes-3b
LLM_BINDING_HOST=http://localai:8080/v1
LLM_BINDING_API_KEY=dummy

EMBEDDING_BINDING=openai
EMBEDDING_MODEL=bge-m3
EMBEDDING_BINDING_HOST=http://localai:8080/v1
EMBEDDING_DIM=1024
```

### Hybrid Strategy (Recommended for Quality)

- **Indexing**: Use Claude (stronger model) for entity/relationship extraction quality
- **Querying**: Use LocalAI (hermes-3b) for retrieval — cheaper, faster
- **Embeddings**: Use LocalAI (bge-m3) for all embeddings — local, free
- **Reranking**: Use LocalAI (bge-reranker-v2-m3) — already in our model configs

### Supported Providers (14+)

OpenAI, Azure OpenAI, Ollama, AWS Bedrock, Google Gemini, Hugging Face, Anthropic, NVIDIA, plus any OpenAI-compatible API (LocalAI).

### Concurrency

- `MAX_ASYNC=4` — concurrent LLM requests
- `EMBEDDING_FUNC_MAX_ASYNC=16` — concurrent embedding requests
- `EMBEDDING_BATCH_NUM=32` — chunks per embedding batch
- Retry: 3 attempts with exponential backoff (4-60s)

## Docker Deployment

### docker-compose Integration

```yaml
lightrag:
  image: ghcr.io/hkuds/lightrag:latest
  ports:
    - "9621:9621"
  volumes:
    - ./data/lightrag/rag_storage:/app/data/rag_storage
    - ./data/lightrag/inputs:/app/data/inputs
  extra_hosts:
    - "host.docker.internal:host-gateway"
  environment:
    WORKING_DIR: "/app/data/rag_storage"
    INPUT_DIR: "/app/data/inputs"
    LLM_BINDING: openai
    LLM_MODEL: hermes-3b
    LLM_BINDING_HOST: http://localai:8080/v1
    EMBEDDING_BINDING: openai
    EMBEDDING_MODEL: bge-m3
    EMBEDDING_BINDING_HOST: http://localai:8080/v1
    EMBEDDING_DIM: 1024
    ENTITY_TYPES: "system,agent,command,hook,skill,plugin,layer,tool,module,workflow"
  depends_on:
    - localai
  restart: unless-stopped
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/documents/upload` | POST | Upload documents (100MB limit) |
| `/documents/scan` | POST | Scan for new documents |
| `/query/stream` | POST | Streaming query responses |
| `/api/chat` | POST | Ollama-compatible chat completion |

### Authentication

- API Key: `X-API-Key` header, configured via `LIGHTRAG_API_KEY`
- JWT: HS256, bcrypt password hashing
- Whitelist: `WHITELIST_PATHS=/health,/api/*`

## Advanced Features

### Incremental Updates

- Add documents without rebuilding the entire graph
- Entities/relations merged into existing graph via union
- ~50% less computation vs full rebuild (GraphRAG comparison)
- Documents deduplicated by MD5 hash

### Document Deletion with KG Reconstruction

- Chunks, entities, relationships belonging ONLY to deleted doc are removed
- Shared entities/relations (in other docs) are preserved
- Affected descriptions rebuilt from remaining documents
- No in-place update — delete then re-upload

### Custom Entity Types

```python
ENTITY_TYPES=system,agent,command,hook,skill,plugin,layer,tool
```

This is critical for fleet: instead of generic "person/organization/event" extraction, LightRAG extracts fleet-domain entities: systems, agents, commands, hooks, etc. The graph then captures the REAL relationships between fleet components.

### WebUI

Built-in at `/webui/` — interactive graph visualization, document indexing, RAG query interface. Directly useful for exploring the fleet knowledge graph.

### LLM Caching

- `ENABLE_LLM_CACHE=true` — cache all LLM responses by content hash
- `ENABLE_LLM_CACHE_FOR_EXTRACT=true` — cache entity extraction specifically
- Saves cost on repeated indexing runs

### Reranker Support

- BGE-reranker-v2-m3 (already in our LocalAI configs)
- Jina AI, Cohere, SiliconCloud rerankers
- `RERANK_BY_DEFAULT=true` — enable for all queries
- `MIN_RERANK_SCORE` — filter low-quality results

## MCP Server Integration

### daniel-lightrag-mcp (22 tools)

```json
{
  "mcpServers": {
    "lightrag": {
      "command": "python",
      "args": ["-m", "daniel_lightrag_mcp"],
      "env": {
        "LIGHTRAG_BASE_URL": "http://localhost:9621",
        "LIGHTRAG_API_KEY": "your-key"
      }
    }
  }
}
```

**Tools:** insert_text, upload_document, scan_documents, get_documents, delete_document, clear_documents, query_text, query_text_stream, get_knowledge_graph, get_graph_labels, check_entity_exists, update_entity, update_relation, delete_entity, delete_relation, get_pipeline_status, get_track_status, get_document_status_counts, clear_cache, get_health

## Performance

- vs GraphRAG: <100 tokens/query (LightRAG) vs ~610,000 tokens/query (GraphRAG)
- Win rate vs NaiveRAG: 80.95% comprehensiveness
- Win rate vs GraphRAG: 52.87% comprehensiveness
- Incremental updates: ~50% less cost than GraphRAG
- 175 markdown files: minutes to index (small dataset)

### Limitations for Our Setup

| Limitation | Mitigation |
|-----------|-----------|
| Recommends 32B+ for indexing | Use Claude for indexing, LocalAI for queries |
| Needs LLM + embedding model simultaneously | Single-active-backend constraint — may need model swapping or separate embedding service |
| No in-place document updates | Delete + re-upload workflow |
| Cold start (model swap) | Pre-warm embedding model, index during low-activity periods |

## Relationships

- INTEGRATES WITH: LocalAI (OpenAI-compatible API on port 8090)
- INTEGRATES WITH: docker-compose (alongside LocalAI container)
- USES: bge-m3 embeddings (via LocalAI)
- USES: bge-reranker-v2-m3 (already in LocalAI model configs)
- INDEXES: all KB entries (175+ markdown files across 8+ branches)
- INDEXES: system manuals, agent manuals, methodology manual, standards manual, module manuals
- PRODUCES: entity-relationship graph (the autocomplete map)
- CONNECTS TO: knowledge map (KB entries → LightRAG entities → graph navigation)
- CONNECTS TO: intent-map.yaml (intent-based retrieval via graph queries)
- CONNECTS TO: injection-profiles.yaml (retrieved content adapted per context tier)
- CONNECTS TO: claude-mem plugin (complementary — LightRAG = graph, claude-mem = vector + memory)
- CONNECTS TO: AICP rag.py (AICP's RAG module — LightRAG could replace or complement)
- CONNECTS TO: AICP stores.py (LocalAI /stores/ API — alternative vector store)
- CONNECTS TO: MCP (daniel-lightrag-mcp → 22 tools for fleet agents)
- CONNECTS TO: autocomplete chain (graph traversal = finding the right path through knowledge)
- CONNECTS TO: pre-embedding (LightRAG indexing = fleet knowledge pre-embedded)
