# /export

**Type:** Claude Code Built-In Command
**Category:** Session Management
**Available to:** ALL agents (especially PM, Accountability, Writer)

## What It Actually Does

Exports the current conversation as plain text to a file. The full conversation — all turns, tool calls, results — saved as readable text. Useful for archiving decisions, creating handoff documents, or preserving session content for audit.

Usage: `/export [filename]` — exports to specified file or auto-generated name.

## When Fleet Agents Should Use It

**PM handoff:** Creating handoff documentation for sprint transitions or project transfers. Export the planning session → clean up → pm-handoff skill.

**Accountability audit:** Preserving complete session records for compliance reporting. Export captures every tool call, every decision, every result.

**Decision archival:** After a complex architecture session with multiple options explored — export preserves the full reasoning chain.

**Sprint boundary:** PM exports sprint planning session for reference.

## Relationships

- PRODUCES: text file with full conversation
- CONNECTS TO: pm-handoff skill (export feeds handoff documentation)
- CONNECTS TO: accountability-generator (export provides raw audit data)
- CONNECTS TO: trail system (export supplements board memory trail with full session detail)
- CONNECTS TO: claude-mem (claude-mem captures observations; export captures full conversation)
- DIFFERENT FROM: claude-mem (claude-mem is searchable compressed observations; export is raw full text)
