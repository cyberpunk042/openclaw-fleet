# Brainstorming

**Type:** Skill (Superpowers Plugin)
**Source:** superpowers plugin (obra/superpowers, 132K stars)
**Invocation:** /brainstorming or invoked as skill by superpowers
**Roles:** Architect, Project Manager

## What It Does

Socratic design refinement BEFORE committing to an approach. Uses structured questioning to explore the design space — challenges assumptions, surfaces hidden constraints, identifies tradeoffs. Forces explicit consideration of alternatives before locking in a direction.

Not random idea generation — guided, critical exploration that produces a defended decision.

## Fleet Use Case

Architect uses during REASONING stage before producing architecture-propose output. PM uses during CONVERSATION to refine PO's requirements through targeted questions. The methodology says "explore MULTIPLE options during investigation" — brainstorming structures that exploration.

## Relationships

- PROVIDED BY: superpowers plugin (obra/superpowers)
- USED BY: architect (REASONING stage), project-manager (CONVERSATION stage)
- CONNECTS TO: architecture-propose skill (brainstorming feeds architecture decisions)
- CONNECTS TO: idea-refine skill (complementary — idea-refine is document-focused, brainstorming is conversation-focused)
- CONNECTS TO: adversarial-spec plugin (brainstorming explores, adversarial-spec stress-tests)
- CONNECTS TO: /branch command (explore alternative branches after brainstorming)
