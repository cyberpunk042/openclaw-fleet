# OpenFleet — wiki/config/

## Origin

Seeded from the second brain (`/home/jfortin/devops-solutions-research-wiki/wiki/config/`) on 2026-04-16. These are adoption templates — our fleet agents will adapt them to OpenFleet's identity over time.

Brain's own full config documentation preserved at `README.md.brain-seed` (40 KB — reference).

## What is here

| File / Dir | Role | Adaptation status |
|---|---|---|
| `wiki-schema.yaml` | Frontmatter schema, enums, required sections, relationship verbs | RAW COPY — `required_sections` must be relaxed or our pages aligned before validation is enabled (see Warning below) |
| `templates/` | 19 page-type templates + `templates/methodology/` (7 methodology doc templates) | RAW COPY — usable as-is |
| `artifact-types.yaml` | 18 page types with thresholds and verification | RAW COPY — thresholds may need tuning per tier |
| `domains.yaml` | Domain registry | NEEDS ADAPTATION — brain's domains (ai-agents, devops, knowledge-systems, etc.) must be replaced/augmented with OpenFleet's (architecture, fleet-ops, orchestration, methodology, ...) |
| `domain-profiles/` | TypeScript, Python/Wiki, Infrastructure, Knowledge overrides | RAW COPY — we use Python + TS + Bash; all four partially apply |
| `sdlc-profiles/` | simplified, default, full | RAW COPY — we run Full for fleet dispatch, Default for solo developer sessions |
| `methodology-profiles/` | stage-gated, spec-driven, agile-ai, test-driven | RAW COPY — stage-gated is closest to our model |
| `export-profiles.yaml` | Export transforms for sister projects | NEEDS ADAPTATION — rewrite as what OpenFleet exports (patterns we've extracted: immune system, tier progression, contribution gating, validation matrix) |
| `quality-standards.yaml` | Lint thresholds | RAW COPY |
| `contribution-policy.yaml` | Trust-tiered contribution maturity | RAW COPY — only relevant if we become a knowledge hub ourselves |
| `mcp-runtime-values.yaml` | MCP runtime signaling values | RAW COPY — relevant when fleet agents declare identity at connect |
| `sister-projects.yaml` | Sister project registry | NEEDS ADAPTATION — brain's registry lists us as sister; ours should list brain + openarms + aicp + dspd from OUR perspective |

## What is NOT copied (intentional)

| File | Why not |
|---|---|
| `methodology.yaml` (28 KB, brain's 9-model version) | Semantic conflict. OpenFleet's canonical methodology lives at `../../config/methodology.yaml` — 387 lines, 7 named models, 6-stage model (conversation→analysis→investigation→reasoning→work→review). Copying brain's here would produce two conflicting definitions in the same repo. See `../../config/methodology.yaml` for ours. |

## Warning — Aspirational required_sections

`wiki-schema.yaml` declares `required_sections` per page type that are the brain's quality bar. OpenFleet's existing 51+ wiki pages in `wiki/domains/architecture/`, `wiki/log/`, `wiki/backlog/` were authored before this schema existed and will FAIL validation against it. Do NOT run validation against these required_sections until either (a) pages are aligned, or (b) required_sections are relaxed to describe what we actually have, or (c) exemptions are declared.

This warning is the direct application of `Principle — Declarations Are Aspirational Until Infrastructure Verifies Them`. OpenArms hit the same wall and had to manage 333 violations against their own schema.

## Divergence from brain (known, tracked)

| Aspect | Brain | OpenFleet |
|---|---|---|
| Stages | document → design → scaffold → implement → test (5) | conversation → analysis → investigation → reasoning → work → review (6) |
| Quality tiers | Skyscraper / Pyramid / Mountain | Expert / Capable / Flagship-local / Lightweight / Direct |
| Methodology models | 9 (feature-development, research, knowledge-evolution, documentation, bug-fix, refactor, hotfix, integration, project-lifecycle) | 7 (feature-development, contribution, rework, research, documentation, review, hotfix) |
| Identity | Solo system | Full System (orchestrator + 10 agents) |

These divergences are legitimate — per the `Methodology Is a Flexible FRAMEWORK, Not a Fixed Pipeline` principle. When reconciling later, we map concepts (our `work` stage contains brain's `scaffold + implement + test`), we don't rename.

## Next steps (per integration chain)

1. Compliance re-check: `python3 -m tools.gateway --wiki-root /home/jfortin/openfleet compliance` — expect Tier 1 closure
2. Relax or align `wiki-schema.yaml` required_sections to match our actual page shapes
3. Adapt `domains.yaml` to our domains
4. Adapt `sister-projects.yaml` to OpenFleet's perspective
5. Re-run `gateway health` to see health score against our schema

## See also

- `../../CLAUDE.md` — OpenFleet brain (our agent context, not to be confused with the second brain)
- `../../config/methodology.yaml` — our active methodology
- `README.md.brain-seed` — brain's own 40 KB config documentation (the full reference)
