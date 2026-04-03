# PermissionRequest

**Type:** Claude Code Hook (lifecycle event)
**Category:** Pre-Action (fires when a permission dialog appears)
**Handler types:** command, http, prompt, agent
**Can block:** YES (can auto-approve or auto-deny)

## What It Actually Does

Fires when Claude Code would normally show a permission dialog to the user (e.g., "Allow this tool?"). The handler can: auto-approve (known-safe patterns), auto-deny (known-dangerous patterns), or let the dialog proceed normally. This enables automated permission policies without human interaction.

## Fleet Use Case: Automated Permission Policies

```
PermissionRequest fires (tool needs permission)
├── Check against role-specific policy:
│   ├── Known-safe for this role? → auto-approve
│   │   Example: ENG always allowed to use Edit on src/
│   ├── Known-dangerous for any role? → auto-deny
│   │   Example: rm -rf, git reset --hard
│   └── Unknown/ambiguous? → let dialog proceed (escalate to PO)
├── Log the request:
│   ├── Trail event: permission_requested
│   └── If auto-approved/denied: trail event with reason
└── Return: approve/deny/passthrough
```

## Why MEDIUM Priority for Fleet

Fleet agents run with `auto` permission mode, which uses a background classifier to auto-approve most tool calls. PermissionRequest fires when the classifier is unsure. For fleet, this hook can:
- Apply role-specific policies (DevSecOps gets broader access than Writer)
- Log all permission events for audit trail
- Detect permission misconfigurations (an agent requesting tools it shouldn't need)

## Relationships

- FIRES ON: permission dialog about to appear
- CAN BLOCK: yes — auto-approve or auto-deny
- CONNECTS TO: /permissions command (manages the allow/deny rules)
- CONNECTS TO: PermissionDenied hook (fires if auto mode denies)
- CONNECTS TO: PreToolUse hook (complementary — PreToolUse is stage gating, PermissionRequest is tool-level)
- CONNECTS TO: permission modes (auto, plan, default, etc.)
- CONNECTS TO: trail system (trail.permission.requested event)
