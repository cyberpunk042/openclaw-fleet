# ars-contexta

**Type:** Claude Code Plugin
**Source:** github.com/agenticnotetaking/ars-contexta
**Stars:** 3K
**Installed for:** Technical Writer

## What It Does

Knowledge systems from conversation. Extracts structured knowledge from conversational context — capturing decisions, rationale, patterns, and institutional knowledge that would otherwise be lost in session transcripts.

## Fleet Use Case

Technical Writer captures and documents fleet knowledge. ars-contexta automates extraction of knowledge artifacts from agent sessions — decisions made, patterns discovered, rationale documented. This feeds directly into the knowledge map.

Complements claude-mem (which captures tool observations) by focusing on CONVERSATIONAL knowledge — the reasoning and decisions that don't involve specific tool calls.

## Relationships

- INSTALLED FOR: technical-writer
- CONNECTS TO: claude-mem (complementary — claude-mem captures tool usage, ars-contexta captures conversation)
- CONNECTS TO: knowledge map (extracted knowledge becomes KB entries)
- CONNECTS TO: LightRAG (extracted knowledge indexed in graph)
- CONNECTS TO: feature-document skill (documentation from extracted knowledge)
- CONNECTS TO: trail system (ars-contexta captures WHY, trail captures WHAT)
