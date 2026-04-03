# idea-capture

**Type:** Skill (AICP)
**Location:** devops-expert-local-ai/.claude/skills/idea-capture/SKILL.md
**Invocation:** /idea-capture [idea text or "interactive"]
**Effort:** high
**Allowed tools:** Read, Write, Bash, Glob, Grep

## Purpose

Take raw user input (PO's idea, verbal description, brainstorm notes) and produce a structured idea document. Identifies core vision, target users, key differentiators, constraints, unknowns. Asks clarifying questions if critical information is missing.

## Input

Idea text as argument, or "interactive" for guided mode where the skill asks questions.

## Process

1. Read and understand the raw idea
2. Identify: core vision, target users, key differentiators, constraints, unknowns
3. Ask clarifying questions if critical information missing
4. Structure into formal idea document

## Output

Writes `docs/idea.md` with 8 required sections:
- **Vision** — one-line description
- **Problem** — what problem, who has it
- **Core Concepts** — each concept explained
- **Target Users** — who and why
- **Key Differentiators** — vs existing solutions
- **Constraints** — technical, resource, timeline
- **Open Questions** — decisions needed before building
- **Success Criteria** — how do we know it worked

Shows user the document and asks for adjustments.

## Assigned Roles

| Role | Priority | Why |
|------|----------|-----|
| PM | RECOMMENDED | PM captures PO ideas into structured docs |
| Architect | RECOMMENDED | Architect captures technical ideas |

## Methodology Stages

| Stage | Usage |
|-------|-------|
| conversation | Primary — capture the idea during discussion with PO |
| analysis | Structure findings from analysis into idea format |

## Relationships

- STARTS: the project lifecycle (idea → architecture → scaffold → foundation → features)
- FOLLOWED BY: idea-refine (critical analysis of the idea doc for gaps)
- FOLLOWED BY: architecture-propose (architecture from the refined idea)
- PRODUCES: docs/idea.md (consumed by architecture-propose, pm-plan)
- CONNECTS TO: brainstorming skill (Superpowers — Socratic refinement of the idea)
- CONNECTS TO: PO verbatim requirement (idea capture is WHERE verbatim gets recorded)
- CONNECTS TO: methodology CONVERSATION stage (idea capture IS the conversation)
- CONNECTS TO: fleet_gate_request (after idea captured, gate request for direction confirmation)
- KEY PRINCIPLE: the PO's words are sacrosanct — idea-capture RECORDS, does not INTERPRET
