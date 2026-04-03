# codex-plugin-cc

**Type:** Claude Code Plugin (cross-provider bridge)
**Source:** github.com/openai/codex-plugin-cc — 10,541 stars
**Released:** 2026-03-30 by OpenAI
**Assigned to:** Fleet-ops (review), DevSecOps (security review), Architect (design challenge)

## What It Actually Is

A Claude Code plugin that lets you call OpenAI's Codex engine from WITHIN a Claude Code session. The key value: INDEPENDENT AI reviews work from a DIFFERENT provider. This gives genuine cross-provider validation — not the same model reviewing its own output.

NOT an MCP server — uses Claude Code's plugin system (slash commands, hooks, subagents). Internally communicates via JSON-RPC 2.0 with the Codex App Server.

## 6 Slash Commands

| Command | What It Does |
|---------|-------------|
| `/codex:setup` | Check/install Codex CLI, configure auth, enable/disable review gate |
| `/codex:review` | Standard code review against uncommitted changes or branch diffs. Read-only. NOT steerable (can't provide custom focus). |
| `/codex:adversarial-review` | Devil's advocate — challenges design trade-offs, hidden assumptions, failure modes, risk areas. Customizable focus. |
| `/codex:rescue` | Delegate a complete task to Codex as a subagent. Foreground or background. Can resume previous Codex threads. |
| `/codex:status` | Check background job progress |
| `/codex:result` | Get completed job output, session ID for resume |

## The Review Gate Pattern

The most valuable architectural concept in this plugin:

```
/codex:setup --enable-review-gate
├── Installs a Claude Code Stop hook
├── Before Claude can stop a session:
│   ├── Codex runs a targeted review of Claude's response
│   ├── Issues found → stop is BLOCKED
│   ├── Claude must address the issues
│   └── Only when Codex approves → session can stop
└── WARNING: can create long-running Claude/Codex loops
    draining BOTH providers' limits rapidly
```

This pattern — independent review before completion — is worth implementing NATIVELY with our own infrastructure (LocalAI as the reviewer), even if we don't use the Codex plugin itself.

## Authentication

Two paths:
- **ChatGPT subscription (OAuth):** `codex login` → browser flow. Works with Plus ($20/mo), Pro ($200/mo), Business, Enterprise. Free/Go plans temporarily included.
- **OpenAI API key:** `codex login --api-key`. Billed at API rates.

## Can It Use LocalAI?

Yes, in theory. Codex CLI supports custom providers via `config.toml`:
```toml
[model_providers.localai]
name = "LocalAI"
base_url = "http://localhost:8090/v1"
model = "hermes"
model_provider = "localai"
```

**Reality:** Codex expects models with strong instruction-following. hermes-3b/7B unlikely to produce useful adversarial reviews. Qwen3.5-9B might handle basic structured reviews. This is untested territory.

## Known Issues

- **Issue #18:** Sandbox restriction — `bwrap: loopback: Failed RTM_NEWADDR` in restricted environments
- **Issue #59:** Review gate state mismatch — setup writes to temp dir but hook reads from persistent dir
- `/codex:review` is NOT steerable — must use adversarial-review for custom focus
- Review gate can create runaway loops draining both Claude AND Codex limits

## Fleet Relevance

| Aspect | Value |
|--------|-------|
| Cross-provider validation | HIGH — genuine second opinion from different AI |
| Adversarial design review | HIGH — challenges assumptions from different perspective |
| Task delegation | MEDIUM — rescue for complex subtasks |
| Review gate pattern | HIGH as CONCEPT — implement natively with LocalAI |
| Cost impact | NEGATIVE — adds OpenAI costs alongside Claude |
| LocalAI independence | CONFLICTS — adds cloud dependency |

**Key insight:** The PATTERN (independent review before completion via Stop hook) is more valuable than the plugin itself. We can implement this natively:
- Use LocalAI as the independent reviewer (free)
- Or use our challenge system (cross-model challenge type)
- The Stop hook → independent check → block if issues concept = our review gate

## Relationships

- INSTALLED BY: scripts/install-plugins.sh (optional — PO decision D6)
- REQUIRES: ChatGPT subscription or OpenAI API key
- CONNECTS TO: fleet-ops 7-step review (additional review layer)
- CONNECTS TO: challenge system (cross-model challenge type — same concept)
- CONNECTS TO: codex_review.py (fleet module for trigger/decision logic)
- CONNECTS TO: multi-backend router (OpenAI as additional backend)
- CONNECTS TO: LocalAI independence mission (can route codex to local model — quality TBD)
- CONNECTS TO: Stop hook (review gate = hook-based quality gate)
- CONNECTS TO: fleet_task_complete (review gate fires before completion)
- CONNECTS TO: anti-corruption (independent verification prevents confident-but-wrong)
