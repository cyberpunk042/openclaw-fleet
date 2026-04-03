# /fast

**Type:** Claude Code Built-In Command
**Category:** Model & Effort
**Available to:** ALL agents

## What It Actually Does

Toggles fast mode — same Opus 4.6 model with speed-optimized API settings. This does NOT switch to a different model. It optimizes the API call parameters for faster responses at the same quality level.

Usage: `/fast on` or `/fast off` or `/fast` (toggle)

## When Fleet Agents Should Use It

**Routine implementation work:** Engineer doing straightforward code changes where speed matters more than extended thinking. Toggle on → faster responses → toggle off when hitting complex section.

**Batch operations:** During /batch parallel changes where many quick edits are needed across files.

**Simple updates:** Documentation edits, config changes, formatting fixes — don't need deep reasoning.

## When NOT to Use It

- Architecture decisions (need deep reasoning)
- Security analysis (can't rush)
- Complex debugging (need systematic investigation)
- Plan creation (need thorough exploration)

## Relationships

- SAME MODEL: does NOT change model — still Opus 4.6
- DIFFERENT FROM: /effort (effort changes thinking depth, fast changes API speed)
- DIFFERENT FROM: /model (model changes the actual model)
- CONNECTS TO: LaborStamp (fast mode may affect token patterns)
- CONNECTS TO: budget awareness (faster responses may consume quota differently)
