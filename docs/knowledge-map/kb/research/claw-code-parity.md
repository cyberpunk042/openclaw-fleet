# Claw-Code-Parity — Clean-Room Claude Code Rewrite

**Type:** Research Finding
**Source:** github.com/ultraworkers/claw-code-parity (forked from instructkr/claw-code)
**Date:** 2026-04-02
**Stars:** 2,869
**Language:** 94.2% Rust, 5.8% Python (~1.5M lines)
**Status:** Rust port in progress — 40/40 tool specs defined, ~20 implemented, ~20 stubs

## What This Project Is

A clean-room rewrite of Claude Code's agent harness in Rust. Reverse-engineered from source briefly exposed 2026-03-31. Provides an open-source alternative to the Claude Code CLI — same tool system, same config format, same hook system, same MCP client, same permission modes. Binary name: `claw`.

This is NOT a plugin or extension — it is a REPLACEMENT that reimplements Claude Code from scratch.

## Architecture (6 Rust Crates)

| Crate | Purpose |
|-------|---------|
| `api/` | HTTP client, SSE streaming, providers (Anthropic + OpenAI-compat + xAI) |
| `commands/` | 36 slash command registry with metadata |
| `compat-harness/` | TS manifest extraction from upstream source |
| `plugins/` | Plugin system (manifest, hooks, lifecycle, tool injection) |
| `runtime/` | Core engine — 18 modules (the brain) |
| `tools/` | 40 built-in tools + global tool registry |

### Runtime Modules (18)

| Module | What It Does |
|--------|-------------|
| `conversation.rs` | Agentic loop — generic over API client + tool executor, auto-compaction, hook invocation |
| `permissions.rs` | 5 modes (ReadOnly/WorkspaceWrite/DangerFullAccess/Prompt/Allow), rule-based pattern matching |
| `config.rs` | Three-tier config hierarchy (User > Project > Local), deep-merge JSON, MCP server configs |
| `bash.rs` | Async shell execution with timeout, background tasks, sandbox integration |
| `sandbox.rs` | Linux `unshare` namespace isolation, network/filesystem isolation, container detection |
| `hooks.rs` | PreToolUse/PostToolUse, subprocess execution with JSON stdin, permission override from hooks |
| `session.rs` | JSONL persistence with rotation (256KB), atomic writes, fork support, compaction tracking |
| `compact.rs` | Token estimation, structured summaries (user requests, tools, key files, pending work), multi-compaction merging |
| `prompt.rs` | System prompt builder — CLAUDE.md hierarchy discovery, git status/diff injection, environment context |
| `mcp_client.rs` | MCP client bootstrapping — 6 transport types (Stdio/SSE/HTTP/WebSocket/SDK/ManagedProxy) |
| `mcp_stdio.rs` | JSON-RPC over stdin/stdout — initialize/list-tools/call-tool/list-resources/read-resource |
| `oauth.rs` | OAuth PKCE flow — authorization, token exchange, refresh, credential persistence |
| `usage.rs` | Token/cost tracking with model-specific pricing (Haiku/Sonnet/Opus in USD) |
| `prompt_cache.rs` | Completion caching with TTL, FNV hashing, cache break detection, persistent stats |
| `bootstrap.rs` | Bootstrap phase planning |
| `remote.rs` | Upstream proxy and remote session context |
| `sse.rs` | Incremental SSE parser |
| `json.rs` | Custom JSON value type |

## Features AICP Should Consider

### HIGH Priority

| Feature | What It Does | AICP Gap |
|---------|-------------|----------|
| **Pattern-based permission rules** | `bash(git:*)` allow, `bash(rm -rf:*)` deny — match tool name + input content | Our guardrails/checks.py is simpler. Pattern rules on tool+input are more powerful |
| **Multi-provider API client** | Unified Provider trait: Anthropic + OpenAI-compat + xAI, with retry/backoff | Our router.py routes LocalAI vs Claude but lacks unified provider abstraction with retry |
| **Session compaction with summary merging** | Preserve recent N messages + structured summaries, merge across multiple compactions | Our session.py has no smart compaction. Essential for long fleet agent sessions |
| **Sandbox for bash execution** | Linux `unshare` namespace isolation per-command: network, filesystem, PID | We don't sandbox commands. Critical for Act-mode fleet agents |
| **Hook system as external shell commands** | PreToolUse/PostToolUse fire shell commands with JSON stdin, return Allow/Deny/Ask | We have guardrails but not external extensibility. Hooks let fleet agents customize without code changes |

### MEDIUM Priority

| Feature | What It Does | AICP Gap |
|---------|-------------|----------|
| **Plugin system with tool injection** | Manifest format (plugin.json) — hooks, lifecycle, custom tools, permissions | We have no plugin system. Plugins inject tools + hooks via manifest |
| **Prompt cache with break detection** | FNV hash requests, TTL cache, detect unexpected invalidations, persistent stats | We don't track prompt cache effectiveness. Saves significant cost |
| **Config hierarchy (3-tier merge)** | User > Project > Local with deep-merge JSON | Our config/loader.py uses YAML but no three-tier merge. Per-agent override important |
| **Cost tracking per model tier** | Model-specific USD pricing (Haiku/Sonnet/Opus), cumulative tracking | Our budget.py tracks tokens but not USD cost per model tier |
| **MCP client (not just server)** | Consume tools from external MCP servers via 6 transport types | We have MCP server (fleet tools) but no MCP client for external servers |

### LOW Priority

| Feature | What It Does | AICP Gap |
|---------|-------------|----------|
| **Instruction file discovery** | Walk parent directories for CLAUDE.md chain | Our prompt.py doesn't walk parents. Useful for monorepo |
| **Slash command registry** | Registry pattern enables plugin commands + tab completion | Our CLI has commands but not a registry |
| **Session forking** | Fork session with parent reference + branch name | Nice for exploration but not critical path |

## What AICP Has That Claw-Code-Parity Does NOT

| AICP Feature | Why It Matters |
|-------------|---------------|
| **LocalAI backend** | Local model support — they only have cloud APIs |
| **Think/Edit/Act modes** | Intentional mode system beyond permission levels |
| **Backend routing by complexity** | Route cheap tasks to LocalAI, complex to Claude |
| **Fleet orchestration** | 10-agent fleet, Mission Control, multi-agent coordination |
| **GPU management** | Model swapping, VRAM management, single-active-backend |
| **RAG/Knowledge base** | rag.py, kb.py, stores.py — they have none |
| **Budget system** | Token budget tracking with modes (turbo/aggressive/standard/economic) |

## Relationships

- INFORMS: AICP architecture (aicp/core/router.py, aicp/guardrails/checks.py, aicp/core/session.py)
- INFORMS: fleet guardrails (pattern-based permission rules)
- INFORMS: fleet hooks (external shell command handlers)
- INFORMS: fleet sandbox (Act-mode command isolation)
- INFORMS: fleet plugin system (manifest-based tool injection)
- CONNECTS TO: AICP Think/Edit/Act modes (maps to their ReadOnly/WorkspaceWrite/DangerFullAccess)
- CONNECTS TO: gateway (their prompt builder ≈ our gateway context injection)
- CONNECTS TO: session_manager.py (their compaction ≈ our context management)
- CONNECTS TO: budget system (their USD cost tracking ≈ our LaborStamp)
- CONNECTS TO: MCP server (they have MCP client — we need both client AND server)
