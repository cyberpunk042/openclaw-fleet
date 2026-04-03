# UserPromptSubmit

**Type:** Claude Code Hook (lifecycle event)
**Category:** Pre-Action (fires before Claude processes the user's prompt)
**Handler types:** command, http, prompt, agent
**Can block:** YES (can modify or reject the prompt)

## What It Actually Does

Fires after the user (or gateway) sends a prompt but BEFORE Claude processes it. The handler receives the prompt text and can: modify it (inject context), block it (reject invalid prompts), or observe it (log for audit). This is the earliest interception point — before Claude even sees the message.

## Fleet Use Case: Context Injection + Scope Validation

```
UserPromptSubmit fires (prompt received)
├── Inject fleet context:
│   ├── Current task details (from OCMC board)
│   ├── Methodology stage reminders
│   ├── Contribution requirements
│   └── Stage-specific tool recommendations
├── Validate scope:
│   ├── Is prompt within assigned task?
│   ├── Does it match current methodology stage?
│   └── Is it safe? (no prompt injection patterns)
└── Return: modified prompt with injected context
    OR exit code 2 to block (with reason)
```

## Why HIGH Priority for Fleet

UserPromptSubmit is the gateway's injection point. Every message from the orchestrator to an agent passes through this hook. It can:
- Add "You are in WORK stage, focus on implementation" reminders
- Inject task context without modifying CLAUDE.md
- Catch scope creep ("this prompt asks about something outside your task")
- Add contribution requirements ("architect input needed before proceeding")

## Relationships

- FIRES BEFORE: Claude processes any prompt
- CAN BLOCK: yes — reject or modify the prompt
- CONNECTS TO: gateway injection (gateway sends prompt → hook augments it)
- CONNECTS TO: methodology stages (inject stage-specific reminders)
- CONNECTS TO: knowledge map navigator (select augmentation based on role + stage)
- CONNECTS TO: InstructionsLoaded hook (both inject context — different timing)
- CONNECTS TO: anti-corruption Line 1 (structural prevention via prompt modification)
- TIER: 3 in implementation priority (enhances quality but not blocking)
