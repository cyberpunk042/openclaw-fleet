# ElicitationResult

**Type:** Claude Code Hook (lifecycle event)
**Category:** MCP (fires when user responds to MCP elicitation)
**Handler types:** command, http, prompt, agent
**Can block:** YES (can modify or reject the response)

## What It Actually Does

Fires when a response is provided to an MCP elicitation request (from the Elicitation hook). The handler receives the user's response before it's sent back to the MCP server. Can validate, modify, or reject the response.

## Fleet Use Case: Response Validation

```
ElicitationResult fires (response to MCP question)
├── Validate response:
│   ├── Is it safe? (no secrets in clear text)
│   ├── Is it correct? (matches expected format)
│   ├── Is it authorized? (PO confirmed this answer)
│   └── If issues: exit code 2 → reject, re-ask
├── Security check:
│   ├── Response contains API key? → ensure it's from env var, not hardcoded
│   ├── Response contains credentials? → validate source
│   └── Response contains paths? → validate within allowed scope
├── Logging:
│   ├── Trail event: elicitation_responded
│   ├── Response (redacted if sensitive)
│   └── Destination MCP server
├── Route response:
│   ├── Forward to requesting MCP server
│   └── If from PO (via fleet_request_input) → validate before forwarding
└── Return: {} or exit code 2 (reject response)
```

## Relationships

- FIRES ON: response to MCP elicitation
- CAN BLOCK: yes (exit code 2 — reject or modify response)
- CONNECTS TO: Elicitation hook (complementary — request/response pair)
- CONNECTS TO: fleet_request_input tool (PO responses flow through here)
- CONNECTS TO: security validation (prevent secret leakage in responses)
- CONNECTS TO: trail system (trail.elicitation.responded event)
- CONNECTS TO: external MCP servers (response forwarded to requesting server)
- TIER: low priority (dependent on Elicitation hook implementation)
