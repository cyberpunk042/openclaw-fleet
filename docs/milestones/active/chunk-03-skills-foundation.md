# Chunk 3: Skills Ecosystem Evaluation + Foundation Skills

**Date:** 2026-04-07
**Status:** Planning
**Part of:** [tools-system-session-index.md](tools-system-session-index.md) — Chunk 3 of 9
**Depends on:** Chunk 2 (plugins installed — some skills come from plugins like superpowers)
**Blocks:** Chunk 4 (role-specific skills build on foundation), Chunk 8 (generation pipeline needs skills to exist)

---

## What This Chunk Accomplishes

Two things:

1. **Ecosystem evaluation** — for each role, audit the 1000+ available skills across 5 sources and determine: what exists that fits? What's missing? This produces a per-role skill inventory with install/build/defer decisions.

2. **Foundation skills** — build the 6 infrastructure skills from phase-f1-foundation-skills.md (M81-M86) that other skills depend on: URL builder, markdown templates, PR composer, comment formatter, board memory composer, IRC formatter.

After this chunk: the fleet has a comprehensive skill inventory per role, foundation skills are built, and ecosystem skills are installed where they fit. The skill creation pipeline is established for Chunk 4.

---

## Step 1: Ecosystem Audit — Per-Source Inventory

### Source 1: Plugin-Bundled Skills (Depends on Chunk 2)

After plugins are installed (Chunk 2), inventory what skills each plugin provides:

```bash
# For each agent workspace, list available skills
# Skills from plugins appear automatically once plugin is enabled
openclaw skills list --workspace <workspace-path>
```

Expected skills from plugins:
- superpowers: 14 skills (brainstorming, TDD, debugging, writing-plans, executing-plans, etc.)
- hookify: writing-rules skill + /hookify commands
- commit-commands: /commit, /commit-push-pr, /clean_gone
- plannotator: /plannotator-annotate, /plannotator-last, /plannotator-review, /plannotator-archive
- adversarial-spec: adversarial specification workflow
- Other plugins: varies

Document: which skills are available per agent after plugin installation.

### Source 2: Gateway Bundled Skills (Already Available)

51 bundled, 10 fleet-relevant (per skills-inventory.md):
- coding-agent, gh-issues, github, healthcheck, skill-creator, tmux, session-logs, clawhub, discord, slack

Audit: which are actually usable (dependencies met)? Run:
```bash
openclaw skills check
```

### Source 3: Fleet Workspace Skills (Already Built)

7 in .claude/skills/: fleet-communicate, fleet-plan, fleet-plane, fleet-review, fleet-security-audit, fleet-sprint, fleet-test

13 in .agents/skills/: fleet-alert, fleet-comment, fleet-commit, fleet-gap, fleet-irc, fleet-memory, fleet-pause, fleet-pr, fleet-report, fleet-task-create, fleet-task-update, fleet-urls, plane-render

These are already built. After Chunk 2's push-soul.sh fix, both directories should reach workspaces.

### Source 4: OCMC Marketplace

1 pack registered (Anthropic Official, 17 skills). Additional packs to register:
- obra/superpowers-marketplace (if not covered by plugin install)
- ComposioHQ/awesome-claude-skills (community collection — needs evaluation)

Register packs, sync, evaluate discovered skills per role.

### Source 5: ClawHub Registry

Open registry. Search for role-relevant skills:
```bash
openclaw skills search "architecture"
openclaw skills search "security audit"
openclaw skills search "test coverage"
openclaw skills search "documentation"
openclaw skills search "infrastructure"
```

Document findings per role.

---

## Step 2: Per-Role Skill Gap Analysis

For each of the 10 roles, produce a table:

```markdown
## {Role} — Skill Inventory

### Available (from ecosystem)
| Skill | Source | Stage | Notes |
|-------|--------|-------|-------|
| brainstorming | superpowers plugin | conversation/analysis | |
| writing-plans | superpowers plugin | reasoning | |
| ... | ... | ... | |

### Missing (need custom build — Chunk 4)
| Skill | Stage | Description | Priority |
|-------|-------|-------------|----------|
| architecture-propose | reasoning | Structured architecture document production | HIGH |
| ... | ... | ... | ... |

### Deferred (evaluate later)
| Skill | Reason |
|-------|--------|
| ... | ... |
```

This gap analysis drives Chunk 4 (what to build per role) and helps estimate the actual scope of Chunk 4.

---

## Step 3: Build Foundation Skills (phase-f1, M81-M86)

These 6 skills are infrastructure that other skills and tool chains depend on.

### M81: fleet-urls — URL Builder Skill

**Purpose:** Given project, branch, file, task → produce correct clickable URLs.
**Design:** Already in phase-f1-foundation-skills.md.
**Depends on:** config/url-templates.yaml (EXISTS), config/projects.yaml (EXISTS), fleet/core/urls.py (EXISTS).
**Implementation:** SKILL.md that teaches agents to use the URL resolver + provides inline URL construction patterns.
**Location:** .claude/skills/fleet-urls/ (gateway skill fleet-urls already exists with 74 lines — needs review against phase-f1 design)

### M82: Markdown Template Library

**Purpose:** Reusable templates for every output type (PR body, task comment, board memory, IRC message).
**Design:** Already in phase-f1-foundation-skills.md with full template definitions.
**Depends on:** Template content defined in phase-f1 doc.
**Implementation:** Templates stored in agents/_template/markdown/. Skill teaches agents which template to use when.
**Location:** .claude/skills/fleet-markdown/ (TO CREATE)

### M83: PR Composer Skill

**Purpose:** Takes branch diff and produces publication-quality PR.
**Design:** Already in phase-f1-foundation-skills.md.
**Depends on:** M81 (URLs), M82 (templates), fleet/templates/pr.py (EXISTS).
**Implementation:** Skill that orchestrates: git log + diff → changelog → file descriptions → URL resolution → template fill → gh pr create.
**Location:** .claude/skills/fleet-pr-compose/ (TO CREATE — distinct from existing fleet-pr gateway skill which is simpler)
**Note:** This skill REPLACES manual PR body writing. fleet_task_complete already does this programmatically — the skill is for cases where agents create PRs outside the fleet_task_complete flow.

### M84: Task Comment Formatter

**Purpose:** Properly formatted task comments for every comment type.
**Design:** Already in phase-f1-foundation-skills.md.
**Depends on:** M81 (URLs), M82 (templates), fleet/templates/comment.py (EXISTS).
**Implementation:** Skill teaches agents which comment template to use (acceptance, progress, completion, blocker) and how to fill them.
**Location:** .claude/skills/fleet-comment-format/ (TO CREATE — distinct from existing fleet-comment gateway skill)

### M85: Board Memory Composer

**Purpose:** Proper tagged, formatted board memory entries.
**Design:** Already in phase-f1-foundation-skills.md.
**Depends on:** M82 (templates), fleet/templates/memory.py (EXISTS).
**Implementation:** Skill teaches agents proper tag taxonomy and memory formatting per type (alert, decision, suggestion, knowledge, report).
**Location:** .claude/skills/fleet-memory-compose/ (TO CREATE — distinct from existing fleet-memory gateway skill)

### M86: IRC Message Formatter

**Purpose:** Structured IRC messages with URLs and emoji for scannability.
**Design:** Already in phase-f1-foundation-skills.md.
**Depends on:** M81 (URLs), fleet/templates/irc.py (EXISTS).
**Implementation:** Skill teaches agents IRC message format per event type.
**Location:** .claude/skills/fleet-irc-format/ (TO CREATE — distinct from existing fleet-irc gateway skill)
**Note:** Most IRC messages are sent automatically by tool chain trees. This skill is for cases where agents post to IRC outside the normal tool flow (rare — fleet_chat handles most cases).

---

## Step 4: Establish Skill Creation Pipeline

For Chunk 4 (per-role skill creation), the pipeline needs to be established:

1. **SKILL.md format** — standard established (YAML frontmatter + markdown instructions)
2. **skill-creator plugin** — from Anthropic official, can scaffold/eval/benchmark skills. Install if not already (Chunk 2).
3. **superpowers writing-skills** — skill for creating new skills. Available via superpowers plugin (Chunk 2).
4. **Testing pattern** — how to verify a skill works (agent invokes → produces correct output → no side effects)
5. **Deployment pattern** — where skills go (.claude/skills/ for project-level, .agents/skills/ for gateway-level), how they reach workspaces
6. **config/agent-tooling.yaml update** — new skills added to per-role skills lists

Document this pipeline so Chunk 4 can follow it per role.

---

## Step 5: Stage-Aware Skill Mapping Foundation

Create config/skill-stage-mapping.yaml — the config that maps skills to methodology stages for TOOLS.md recommendations.

Initially populated with:
- Skills from superpowers mapped to their natural stages
- Foundation skills (M81-M86) mapped to applicable stages
- Fleet skills (7 existing) mapped to stages
- Gateway skills (13 existing) mapped to stages

This config is CONSUMED by generate-tools-md.sh (Chunk 8) to produce the "Recommended Skills" section per stage in TOOLS.md.

Format (scaffold — actual content depends on what skills exist):
```yaml
# config/skill-stage-mapping.yaml
# Maps skills to methodology stages for TOOLS.md recommendations
# Skills not listed here appear in TOOLS.md without stage recommendation

conversation:
  generic:
    - brainstorming          # superpowers
    - fleet-communicate      # fleet skill
  per_role:
    project-manager:
      - fleet-plan           # fleet skill

analysis:
  generic:
    - fleet-comment-format   # foundation skill
  per_role:
    architect:
      - # (to be filled after Chunk 4)

investigation:
  generic:
    - # adversarial-spec if installed
  per_role:
    # (to be filled after Chunk 4)

reasoning:
  generic:
    - writing-plans          # superpowers
    - fleet-plan             # fleet skill
  per_role:
    # (to be filled after Chunk 4)

work:
  generic:
    - test-driven-development    # superpowers
    - verification-before-completion  # superpowers
    - fleet-commit               # gateway skill
    - fleet-pr-compose           # foundation skill (M83)
  per_role:
    # (to be filled after Chunk 4)
```

---

## Step 6: Update session index

Mark Chunk 3 complete. Add ecosystem audit results document reference.

---

## Verification Criteria

- [ ] Per-role skill inventory produced (available / missing / deferred)
- [ ] All 6 foundation skills (M81-M86) built and tested
- [ ] Skill creation pipeline documented (format, tooling, testing, deployment)
- [ ] config/skill-stage-mapping.yaml created with initial population
- [ ] Ecosystem skills from plugins verified as available per agent
- [ ] OCMC marketplace packs evaluated and registered where useful
- [ ] ClawHub search conducted per role-relevant terms

---

## Outputs

| Output | Description |
|--------|-------------|
| Per-role skill inventory | Table of available/missing/deferred skills for each of 10 roles |
| 6 SKILL.md files | Foundation skills M81-M86 |
| config/skill-stage-mapping.yaml | Stage-to-skill mapping for TOOLS.md generation |
| Skill creation pipeline doc | How to create, test, deploy skills (for Chunk 4) |
| Updated skills-inventory.md | Refreshed with actual ecosystem state |
