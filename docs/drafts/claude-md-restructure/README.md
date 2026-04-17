# CLAUDE.md Restructure — Proposal Draft (2026-04-16)

> **STATUS: Draft. Awaiting PO approval.** Nothing in this directory has been applied to the real `CLAUDE.md` or created as the real `AGENTS.md`. These are scratch drafts showing what the Progressive Structural Enrichment pattern would produce if executed.

## Why this exists

Current state (measured 2026-04-16):
- `/home/jfortin/openfleet/CLAUDE.md` — 358 lines, 16 sections, loads on every message
- Second-brain standard (per `model-claude-code-standards.md`): <200 lines per context file, route don't contain
- Per ETH Zurich Feb 2026: AI-generated context files HURT success by ~3%; context files ≥300 lines reduce task success by ~3%
- OpenArms trajectory (reference): 471 → 124 → 144 lines via 3-step Progressive Structural Enrichment

Our CLAUDE.md is 158 lines over the standard. About 5 of 16 sections are actually Claude-specific; the rest is universal project context.

## The pattern being applied

`Progressive Structural Enrichment in Agent Config` (brain pattern at `devops-solutions-research-wiki/wiki/patterns/01_drafts/progressive-structural-enrichment-in-agent-config.md`):

1. **Shrink to routing table.** Extract everything that's not Claude-unique into companion files. Target <200 lines. Expect 60-75% reduction.
2. **Add Goldilocks identity structure.** Stable fields only (type, domain, phase, scale, second-brain). Route to the full `wiki/ecosystem/openfleet/identity-profile.md` (already authored).
3. **Add governing principles table.** The brain's 4 principles, with measured evidence where we have it.
4. **Iterate with structural additions only.** Never prose paragraphs. Always tables, numbered lists, typed callouts.

## What this proposal does NOT do

- Does NOT restructure the agent runtime `AGENTS.md` at `agents/_template/AGENTS.md` or any per-agent files in `agents/*/AGENTS.md`. Those are Layer-2-for-runtime-consumers and stay as-is for now. The runtime-template AGENTS.md / SOUL.md / HEARTBEAT.md conflation is a separate (documented) track.
- Does NOT delete existing detail. Everything extracted moves to a companion file; nothing is lost.
- Does NOT change `config/methodology.yaml` or any code.
- Does NOT touch our existing `docs/ARCHITECTURE.md` or other `docs/*.md` files (they're separate concerns — the three-layer pattern is at the REPO-ROOT level: AGENTS.md + CLAUDE.md + thematic roots).

## What this proposal DOES do (if approved)

### Files created
| File | Role | Target lines |
|---|---|---|
| `/home/jfortin/openfleet/AGENTS.md` (REPLACES current agent-workspace-template at root) | Layer 1 universal: cross-tool project context, any AI tool reads this | <150 |
| `/home/jfortin/openfleet/.claude/rules/work-mode.md` | Claude-specific: solo-mode + git safety + behavioral rules | <80 |
| `/home/jfortin/openfleet/.claude/rules/second-brain-connection.md` | Connection pointer to second brain + adoption tier commands | <50 |

### Files modified
| File | Change | Target lines |
|---|---|---|
| `/home/jfortin/openfleet/CLAUDE.md` | Slimmed to Claude-specific delta + routing table | <100 |

### Files preserved untouched
| File | Why |
|---|---|
| `agents/_template/AGENTS.md` + 50+ agent-workspace instances | Runtime consumer Layer-2 templates — separate concern |
| `config/methodology.yaml` | Canonical methodology, not restructure scope |
| `docs/ARCHITECTURE.md`, other docs/* | Public-docs layer (separate from the three-layer AGENTS+CLAUDE+rules pattern) |
| `wiki/ecosystem/openfleet/identity-profile.md` | Already authored correctly; the new AGENTS.md routes to it |

### Critical disambiguation — conflict with existing root AGENTS.md

Our `/home/jfortin/openfleet/AGENTS.md` (9289 bytes, 1-50 lines visible: "# AGENTS.md - Your Workspace") is **functionally a per-agent workspace template**, not a Layer-1 universal project context file. The brain's compliance checker matches it by filename, producing a false positive (see my 2026-04-16 contributions to the brain).

Three options for the PO on this root file:
- **A. Rename existing** — move `AGENTS.md` → `agents/_template/AGENTS.md` (if not already there) or to a clearer template location, then create NEW root AGENTS.md as Layer-1 universal context
- **B. Overwrite existing** — keep the filename, replace content with Layer-1 universal content (loses the runtime template which may be referenced elsewhere)
- **C. Keep as-is + add different Layer-1 name** — e.g., create `PROJECT.md` or `CONTEXT.md` as our Layer-1 (deviates from cross-tool AGENTS.md standard)

Recommend **A** — preserves existing content and fixes the structural conflict. But this is a PO decision; I won't execute either way without explicit approval.

## Files in this draft directory

- `CLAUDE.md.proposed` — draft of the slimmed CLAUDE.md
- `AGENTS.md.proposed` — draft of the new Layer-1 universal AGENTS.md
- `work-mode.md.proposed` — extracted Work Mode rules (for `.claude/rules/`)
- `second-brain-connection.md.proposed` — extracted second-brain connection block

## Decision point

If you approve, the migration is:
1. Rename current `AGENTS.md` → `agents/_template/AGENTS.md` (or equivalent, preserving it for runtime use)
2. Write new Layer-1 `AGENTS.md` at root from draft
3. Write new slimmed `CLAUDE.md` from draft (replacing current 358-line version)
4. Create `.claude/rules/work-mode.md` + `.claude/rules/second-brain-connection.md` from drafts
5. Verify: `gateway compliance` still shows Tier 4; `.claude/rules/` is populated; no reference-chain is broken

If you redirect, I hold the drafts here and continue other work.
