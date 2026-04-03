# Elicitation

**Type:** Claude Code Hook (lifecycle event)
**Category:** MCP (fires when MCP server requests user input)
**Handler types:** command, http, prompt, agent
**Can block:** YES (can auto-respond or reject the elicitation)

## What It Actually Does

Fires when an MCP server sends an elicitation request — asking the user for input (e.g., "Choose a database to connect to", "Enter your API key", "Select the deployment target"). The handler can auto-respond with predefined answers, route the question to the PO, or block the elicitation.

## Fleet Use Case: Automated MCP Responses

```
Elicitation fires (MCP requests user input)
├── Check if auto-respondable:
│   ├── Known question pattern? → auto-respond with config value
│   │   Example: "database?" → use fleet db config
│   ├── Security-sensitive? → route to PO via ntfy
│   │   Example: "API key?" → NEVER auto-respond
│   └── Unknown question? → route to PO
├── Route to PO:
│   ├── ntfy notification with question text
│   ├── Wait for PO response via fleet_request_input
│   └── Forward PO response to MCP server
├── Logging:
│   ├── Trail event: elicitation_received
│   ├── From which MCP server, what question
│   └── How it was handled (auto/routed/blocked)
└── Return: auto-response or exit code 2 (block)
```

## Why This Matters for Fleet Agents

Fleet agents run without a human at the terminal. When an MCP server asks for input, there's nobody to answer. Elicitation hook bridges this gap:
- Auto-respond to predictable questions (using fleet config)
- Route unpredictable questions to PO
- Block questions that shouldn't be asked in fleet context

Without this hook, MCP elicitations hang indefinitely for fleet agents.

## Relationships

- FIRES ON: MCP server requests user input
- CAN BLOCK: yes (exit code 2 — reject the elicitation)
- CONNECTS TO: ElicitationResult hook (complementary — request/response pair)
- CONNECTS TO: fleet MCP server (fleet/mcp/tools.py — fleet's own MCP)
- CONNECTS TO: fleet_request_input tool (fleet's mechanism for requesting PO input)
- CONNECTS TO: ntfy notifications (route questions to PO)
- CONNECTS TO: external MCP servers (Plane, GitHub, Docker — may ask questions)
- TIER: low priority (few MCP servers use elicitation currently)
