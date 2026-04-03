# /exit

**Type:** Claude Code Built-In Command
**Category:** Session Management
**Available to:** ALL agents

## What It Actually Does

Exits the Claude Code CLI session. Terminates the current process. In fleet context, this ends the gateway session for the agent — the orchestrator detects the agent is no longer running.

## When Fleet Agents Should Use It

**Fleet agents generally do NOT use /exit.** The gateway manages session lifecycle. The orchestrator wakes agents and the gateway process ends naturally after the agent's turn completes.

**Manual sessions only:** When a human operator is interacting directly with Claude Code CLI (not through the fleet gateway), /exit cleanly terminates.

## Relationships

- TRIGGERS: SessionEnd hook (fires before process exits)
- DETECTED BY: orchestrator (agent no longer running → available for next dispatch)
- CONNECTS TO: gateway lifecycle (gateway manages start/stop, not the agent)
- DIFFERENT FROM: /clear (clears conversation but keeps session alive)
