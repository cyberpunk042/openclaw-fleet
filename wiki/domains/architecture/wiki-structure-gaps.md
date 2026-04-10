---
title: "Wiki Structure Gaps — LLM Wiki Model Alignment"
type: reference
domain: architecture
status: processing
confidence: medium
created: 2026-04-10
updated: 2026-04-10
tags: [wiki, llm-wiki, second-brain, gaps, structure, evolution]
sources:
  - id: src-model-llm-wiki
    type: documentation
    file: /home/jfortin/devops-solutions-research-wiki/wiki/spine/model-llm-wiki.md
    title: "Model: LLM Wiki"
  - id: src-second-brain
    type: documentation
    file: /home/jfortin/devops-solutions-research-wiki/wiki/spine/model-second-brain.md
    title: "Model: Second Brain"
---

# Wiki Structure Gaps — LLM Wiki Model Alignment

## Summary

OpenFleet's wiki/ partially implements the LLM Wiki model. Three layers exist (backlog, domains, log). Seven are missing. Alignment is incremental per the old-model-tolerance directive.

## Current State

### Exists
- wiki/backlog/ — epics, modules, tasks (PM track)
- wiki/domains/ — knowledge pages by domain (partial)
- wiki/log/ — PO directives, session notes

### Missing from the LLM Wiki Model

| Layer | Directory | Purpose | Priority |
|-------|-----------|---------|----------|
| Sources | wiki/sources/ | Source synthesis (L1). One page per ingested source with provenance. | Medium — needed when we start proper research ingestion |
| Comparisons | wiki/comparisons/ | Structured comparison matrices (L3). | Low — create when 2+ options need formal comparison |
| Lessons | wiki/lessons/ | Codified experience (L4). Requires evidence from 3+ independent sources. | Medium — the anti-patterns page is a proto-lesson |
| Patterns | wiki/patterns/ | Recurring structures (L5). 2+ instances across contexts. | Medium — SFIF is already a pattern, needs formal page |
| Decisions | wiki/decisions/ | Choice frameworks (L6). Alternatives + rationale + reversibility. | High — design decisions should be here, not scattered |
| Spine | wiki/spine/ | Navigation. Model guides, domain overviews, adoption guide. | Low — needed at scale |
| Config | wiki/config/ | methodology.yaml, agent-directive.md. Work process definition. | Already exists as config/ at project root |

### Missing from Second Brain Architecture

| PARA Concept | OpenFleet Equivalent | Gap |
|-------------|---------------------|-----|
| Capture (raw/) | None | No raw source provenance layer. Research findings go directly to wiki/domains/ without source preservation. |
| Progressive distillation | Partial | Pages don't have maturity lifecycle (seed → growing → mature → canonical) in frontmatter. |
| Review cadence | None | No scheduled wiki health check (gaps, stale pages, orphans). |

## Adoption Path

Per the old-model-tolerance directive: introduce new layers as additions, not replacements. Create directories when there's content for them.

1. **wiki/decisions/** — next time a design decision is made, create it here instead of in docs/
2. **wiki/sources/** — next time a source is researched, save raw to raw/ (create if needed), synthesize to wiki/sources/
3. **wiki/lessons/** — the anti-patterns page could be promoted to a formal lesson
4. **wiki/patterns/** — SFIF, autocomplete chain, contribution lifecycle are all patterns

The existing docs/ continues to serve its purpose (old model tolerance). Knowledge migrates to wiki/ over time, not all at once.
