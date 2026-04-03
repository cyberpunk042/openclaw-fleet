# PermissionDenied

**Type:** Claude Code Hook (lifecycle event)
**Category:** Post-Action (fires when auto mode denies a tool call)
**Handler types:** command, http, prompt, agent
**Can block:** NO (observation only — the denial already happened)

## What It Actually Does

Fires when the auto permission classifier denies a tool call. The handler can only OBSERVE — the denial has already occurred. Use cases: logging denied operations for audit, detecting permission misconfigurations, alerting on suspicious tool attempts.

## Fleet Use Case: Audit + Misconfig Detection

```
PermissionDenied fires (auto mode denied a tool)
├── Log for audit trail:
│   ├── Which agent, which tool, which arguments
│   ├── What task was the agent working on
│   └── Trail event: permission_denied
├── Detect misconfiguration:
│   ├── Is this a tool the agent SHOULD have access to?
│   │   YES → alert fleet-ops: "permission misconfiguration"
│   │   NO → normal — auto mode correctly denied
├── Detect suspicious patterns:
│   ├── Repeated denials of same tool → agent may be confused
│   ├── Denied tools outside agent's role → possible scope creep
│   └── Alert threshold reached → flag for review
└── Return: {} (cannot modify outcome)
```

## Relationships

- FIRES AFTER: auto mode denies a tool call
- CANNOT BLOCK: observation only — denial already happened
- CONNECTS TO: PermissionRequest hook (PermissionRequest can prevent denial; PermissionDenied observes it)
- CONNECTS TO: /permissions command (view/modify permission rules)
- CONNECTS TO: trail system (trail.permission.denied event)
- CONNECTS TO: doctor system (repeated denials may indicate agent confusion)
- CONNECTS TO: storm monitor (high denial rate could be an indicator)
- TIER: low priority (useful for audit but not critical path)
