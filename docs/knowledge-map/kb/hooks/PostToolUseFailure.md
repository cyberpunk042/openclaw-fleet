# PostToolUseFailure

**Type:** Claude Code Hook (lifecycle event)
**Category:** Error Handling (fires when a tool FAILS)
**Handler types:** command, http, prompt, agent
**Can block:** NO — the failure already happened

## What It Actually Does

Fires AFTER a tool execution FAILS. Receives the tool name, input, and error details. Different from PostToolUse (which fires on SUCCESS). This hook handles: MCP server crashes, permission denials, network timeouts, invalid parameters, tool-internal errors.

## Fleet Use Case: Error Detection Pipeline

```
PostToolUseFailure fires (tool failed)
├── Classify error:
│   ├── MCP server not responding → dead server detection
│   ├── Permission denied → permission configuration issue
│   ├── Network timeout → connectivity issue
│   ├── Rate limit → quota exhaustion (also caught by StopFailure)
│   └── Tool-internal error → bug or invalid input
├── Record for pattern detection:
│   ├── Same tool failing repeatedly → circuit breaker candidate
│   ├── Same agent failing repeatedly → agent health concern
│   └── Write to error_reporter.py signal file
├── Trail event: tool failure recorded
└── Return: {} (acknowledged)
```

## Relationships

- FIRES ON: tool execution FAILURE (different from PostToolUse which fires on success)
- CANNOT BLOCK: failure already happened
- CONNECTS TO: error_reporter.py (agent error reporting → orchestrator reads each cycle)
- CONNECTS TO: doctor.py detect_stuck (repeated failures → stuck detection)
- CONNECTS TO: circuit breakers (storm_integration.py — repeated failures → breaker trips)
- CONNECTS TO: outage_detector.py (MCP server failures → outage detection)
- CONNECTS TO: trail system (tool failure events)
- DIFFERENT FROM: StopFailure (API-level errors like rate limits — PostToolUseFailure is tool-level)
