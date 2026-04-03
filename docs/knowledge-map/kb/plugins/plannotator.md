# plannotator

**Type:** Claude Code Plugin
**Source:** github.com/backnotprop/plannotator
**Stars:** 4K
**Installed for:** Project Manager

## What It Does

Visual plan/diff annotation with team feedback. Renders plans as visual diagrams with annotation points — team members can comment on specific sections. Creates a feedback loop on plans before execution begins.

## Fleet Use Case

PM creates sprint plans (fleet_plan, fleet_sprint skills). plannotator visualizes the plan structure so the PO can review visually. Annotations capture PO feedback directly on plan sections — not as separate messages that lose context.

## Relationships

- INSTALLED FOR: project-manager
- USED IN: reasoning stage (plan visualization before execution)
- CONNECTS TO: pm-plan skill (produces plans → plannotator visualizes them)
- CONNECTS TO: fleet_plan skill (sprint task breakdown → visualized)
- CONNECTS TO: /plan command (plan mode exploration → annotated output)
- CONNECTS TO: fleet_gate_request tool (PO reviews annotated plan)
