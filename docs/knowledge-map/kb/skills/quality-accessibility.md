# quality-accessibility

**Type:** Skill (AICP Lifecycle)
**Location:** devops-expert-local-ai/.claude/skills/quality-accessibility/
**Invocation:** /quality-accessibility
**Effort:** medium
**Roles:** UX Designer

## What It Does

Accessibility audit: check WCAG compliance, keyboard navigation, screen reader compatibility, color contrast, focus management, ARIA attributes. Produces an accessibility report with violations and fixes.

## Fleet Use Case

UX designer validates that fleet UIs (Mission Control frontend, LightRAG WebUI) meet accessibility standards. Uses Playwright MCP for automated accessibility checks. Currently the UX designer's only assigned skill — their contribution is accessibility specs.

## Relationships

- USED BY: ux-designer
- CONNECTS TO: Playwright MCP (automated accessibility testing)
- CONNECTS TO: fleet_contribute tool (ux_spec with accessibility requirements)
- CONNECTS TO: Mission Control frontend (primary fleet UI to audit)
