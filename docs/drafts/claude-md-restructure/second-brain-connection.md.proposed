# .claude/rules/second-brain-connection.md — Bridge to the Research Wiki

> Loaded on demand when work touches the brain. `CLAUDE.md` has a summary pointer; this file has the detail.

## What the Second Brain Is (and Isn't)

**IS:** the shared research wiki at `../devops-solutions-research-wiki` — a structured LLM wiki holding methodology, standards, lessons, patterns, decisions, 16 models, 22 per-type standards across 360+ pages with 2,400+ relationships. Maintained across 5 ecosystem projects.

**IS NOT:** our brain. OpenFleet has its own brain (CLAUDE.md + AGENTS.md + `.claude/` + skills + hooks + `agents/*/SOUL.md` + `config/`). Never conflate "brain" with "second brain". The brain is what CONSTITUTES the agent; the second brain is what the agent CONSUMES FROM and CONTRIBUTES TO.

## The Goal

**ADOPT what fits, EVOLVE our own brain.** Not runtime dependency. The brain teaches; OpenFleet learns and evolves its own infrastructure.

Four verbs from the PO: **SWALLOW → INTEGRATE → CONTRIBUTE → EVOLVE**.

## Adoption Status (as of 2026-04-16)

**Tier 4 / 4 — STRUCTURAL.**

- Tier 1 Agent Foundation ✓ (CLAUDE.md + wiki-schema.yaml + templates)
- Tier 2 Stage-Gate Process ✓ (methodology.yaml + backlog + AGENTS.md)
- Tier 3 Evolution Pipeline ✓ (lessons/patterns/decisions dirs + lint.py + evolve.py forwarders)
- Tier 4 Hub Integration ✓ (export-profiles + .mcp.json + connected MCP)

Operationally Tier 2+ (per OpenArms pattern — structural compliance ≠ operational compliance):
- ~58 missing-section errors across 53 pages — migration track
- 0.7 avg relationships per page vs ≥6 healthy — relationship density gap
- 22 orphan pages — cross-linking migration
- CLAUDE.md at 358 lines vs <200 target — Progressive Structural Enrichment track

## Essential Commands (run from openfleet root)

| Command | Use |
|---|---|
| `python3 tools/gateway orient` | First step on ANY fresh session — absorbs the landscape |
| `python3 tools/gateway what-do-i-need` | Task-bound routing (which model to use, which stages) |
| `python3 tools/gateway status` | Project status dashboard |
| `python3 tools/gateway compliance` | Where we are on the 4-tier adoption ladder |
| `python3 tools/gateway health` | Wiki quality score (0-100) |
| `python3 tools/gateway flow` | 8-step Goldilocks flow (identity → action) |
| `python3 tools/gateway navigate` | Full knowledge tree with drill-down |
| `python3 tools/view spine` | All 16 models + standards |
| `python3 tools/view standards` | 25 per-type + per-model standards |
| `python3 tools/view lessons` | 57 validated lessons |
| `python3 tools/view patterns` | 25 validated patterns |
| `python3 tools/view decisions` | 18 validated decisions |
| `python3 tools/view search "query"` | Search across all brain content |
| `python3 tools/view refs "Page Title"` | Trace relationships for a page |
| `python3 tools/gateway query --model <type> --full-chain` | Artifact chain for a methodology model |
| `python3 tools/gateway query --stage <name> --domain <ours>` | Stage rules for our domain |
| `python3 tools/gateway template <type>` | Get a page template |
| `python3 tools/gateway contribute --type lesson\|correction\|remark ...` | Write back |
| `python3 tools/lint.py --summary` | Our lint (forwards to brain's lint with our wiki + schema) |

## Writing Content That Conforms

Every new wiki page:

1. Scaffold from a template: `python3 tools/gateway template <type>` (or copy from `wiki/config/templates/<type>.md`)
2. Fill content per the type's standards (e.g., concept requires Summary + Key Insights + Deep Analysis + Relationships)
3. Validate: `python3 -m tools.validate <path>` (forward via brain's venv: `cd ../devops-solutions-research-wiki && PYTHONPATH=. .venv/bin/python -m tools.validate <our-wiki-path> --schema <our-schema>`)
4. Check the per-type standards at `../devops-solutions-research-wiki/wiki/spine/standards/<type>-page-standards.md` before first authoring

## Contribution Protocol

**When to contribute:**
- Observed a brain-tool bug or drift (correction)
- Learned something the brain doesn't know, with ≥3 evidence items (lesson)
- Want to provide feedback/clarification (remark)

**Before contributing, VERIFY the claim.** Use `ls`/`Read`/`grep`/`pipeline post` against reality. Aspirational contributions weaken the feedback loop.

**How to contribute:**
```bash
python3 tools/gateway contribute \
  --type lesson \
  --title "Title" \
  --content "..." \
  --contributor "openfleet-solo-session" \
  --source "/home/jfortin/openfleet" \
  --reason "Why this is being contributed"
```

Lands in brain's `log/` or `wiki/lessons/00_inbox/` with `pending-review` status. Promotion through the maturity ladder requires human review per the brain's `contribution-policy.yaml`.

## Cross-Reference

- Brain identity of us: `../devops-solutions-research-wiki/wiki/ecosystem/project_profiles/openfleet/identity-profile.md`
- Our self-declared identity: `wiki/ecosystem/openfleet/identity-profile.md`
- Integration chain (17 steps): `../devops-solutions-research-wiki/wiki/spine/references/second-brain-integration-chain.md`
- Consumer integration roadmap exemplar: `../devops-solutions-research-wiki/wiki/spine/references/consumer-integration-roadmap-exemplar.md`
- Our session notes: `wiki/log/2026-04-16-second-brain-integration-session.md`
