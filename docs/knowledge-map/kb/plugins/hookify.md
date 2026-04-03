# hookify

**Type:** Claude Code Plugin (Official Anthropic)
**Source:** Anthropic marketplace
**Installed for:** DevOps

## What It Does

Natural-language hook creation. Describe what you want a hook to do in plain English → hookify generates the hook configuration (handler script, event type, matchers). Eliminates manual hook JSON editing.

## Fleet Use Case

DevOps manages fleet infrastructure including hook configurations. When new hooks are needed (e.g., "block all git push to main", "log every file edit in config/"), hookify lets DevOps create them from natural language descriptions.

Particularly useful for:
- Adding safety hooks per agent role
- Creating monitoring hooks for new systems
- Prototyping hook behavior before IaC codification

## Relationships

- INSTALLED FOR: devops
- CONNECTS TO: /hooks command (view configured hooks)
- CONNECTS TO: PreToolUse hook (hookify can create PreToolUse handlers)
- CONNECTS TO: PostToolUse hook (hookify can create PostToolUse handlers)
- CONNECTS TO: IaC scripts (hookify prototypes → codified in setup scripts)
- CONNECTS TO: safety-net plugin (complementary — safety-net is generic, hookify creates custom)
