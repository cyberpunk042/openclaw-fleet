# /sandbox

**Type:** Claude Code Built-In Command
**Category:** Configuration
**Available to:** ALL agents

## What It Actually Does

Toggles sandbox mode on/off. When sandboxed, Claude Code runs Bash commands in an isolated environment (macOS: Apple Sandbox, Linux: Docker container). File system writes are restricted to the project directory. Network access may be limited. Provides an additional layer of protection against destructive commands.

## When Fleet Agents Should Use It

**Fleet agents run in controlled environments already.** The gateway manages the execution context. Sandbox mode adds OS-level isolation on top of:
- Permission modes (auto/plan/default)
- PreToolUse hooks (safety-net pattern)
- Guardrails (AICP Think/Edit/Act modes)
- Stage gating (methodology enforcement)

**DevSecOps may enable sandbox** for security-sensitive analysis — running untrusted code, analyzing malware patterns, or testing exploit scenarios in isolation.

**High-risk operations:** When an agent needs to execute commands that could affect the host system (Docker builds, system-level scripts), sandbox provides containment.

## Defense in Depth

```
Layer 1: Sandbox (OS-level isolation)
Layer 2: Permission mode (tool-level allow/deny)
Layer 3: PreToolUse hook (safety-net pattern — catch destructive commands)
Layer 4: Stage gating (methodology — only certain tools in certain stages)
Layer 5: Guardrails (AICP — Think/Edit/Act mode enforcement)
```

## Relationships

- CONNECTS TO: /permissions (complementary — sandbox is OS-level, permissions are tool-level)
- CONNECTS TO: PreToolUse hook (safety-net catches destructive commands even without sandbox)
- CONNECTS TO: code-container plugin (Docker-based isolation for agent execution)
- CONNECTS TO: guardrails system (AICP Think/Edit/Act — conceptual alignment)
- CONNECTS TO: DevSecOps role (security-sensitive work benefits most)
- CONNECTS TO: gateway (could set sandbox mode per dispatch based on task risk)
