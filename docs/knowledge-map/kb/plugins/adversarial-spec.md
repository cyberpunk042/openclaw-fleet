# adversarial-spec

**Type:** Claude Code Plugin
**Source:** github.com/zscole/adversarial-spec
**Stars:** 518
**Installed for:** Architect

## What It Does

Multi-LLM debate for specification refinement. Pits multiple AI perspectives against a proposed design spec — each challenger argues from a different angle (performance, security, simplicity, edge cases). The architect gets stress-tested feedback on their designs BEFORE implementation begins.

## Fleet Use Case

Architect produces a plan during REASONING stage. Before fleet_contribute sends design_input to the engineer, adversarial-spec generates counter-arguments. The architect either defends or revises. Result: stronger specs that survive scrutiny.

## Relationships

- INSTALLED FOR: architect
- USED IN: reasoning stage (spec refinement before implementation)
- CONNECTS TO: architecture-propose skill (produces spec → adversarial-spec challenges it)
- CONNECTS TO: fleet_contribute (design_input sent after spec survives challenge)
- CONNECTS TO: codex adversarial review concept (independent cross-perspective validation)
- CONNECTS TO: quality standards (stronger specs = fewer rejections at review)
