# Context Injection — Tiered Rendering Design

## What We're Building

A tier-aware rendering system for the fleet's context injection pipeline. Every time an agent opens its eyes — heartbeat or task dispatch — the content it sees adapts to the model's capability tier. Expert models get full context with trust. Lightweight models get simple, direct instructions. The brain does more as the model does less.

> "I would not overwhelm my trainee" — PO, 2026-04-09

This also fixes the 47 open validation issues (from the 50-issue catalog) by replacing the current "one-size-fits-all" rendering with structured, formatted, tier-aware output.

## Reference Documents

- **Decision tree:** [wiki/domains/architecture/context-injection-tree.md](../../../wiki/domains/architecture/context-injection-tree.md) — 91 scenarios, all branches and leaves
- **Validation issues:** [wiki/domains/architecture/validation-issues-catalog.md](../../../wiki/domains/architecture/validation-issues-catalog.md) — 50 issues, 15 critical
- **Current preembed:** [fleet/core/preembed.py](../../../fleet/core/preembed.py) — heartbeat + task rendering
- **Current role providers:** [fleet/core/role_providers.py](../../../fleet/core/role_providers.py) — per-role data (raw dicts)
- **Current injection profiles:** [docs/knowledge-map/injection-profiles.yaml](../../knowledge-map/injection-profiles.yaml) — Navigator depth tiers
- **AICP capabilities:** [devops-expert-local-ai/CLAUDE.md](../../../../devops-expert-local-ai/CLAUDE.md) — LocalAI models, profiles, routing

## Capability Tiers

Profiles based on model CAPABILITY, not fixed context sizes. Maps to AICP operational profiles.

| Tier | Models | Context | AICP Profile | Autonomy |
|------|--------|---------|-------------|----------|
| **Expert** | claude opus/sonnet | 200K-1M | N/A (cloud) | Full — agent reasons autonomously |
| **Capable** | qwen3-8b (thinking), qwen3-30b MoE | 16-32K | default, code-review, reliable | Guided — agent follows clear multi-step instructions |
| **Flagship-Local** | gemma4-26b (dual GPU 8+11GB) | 256K | dual-gpu | Like Capable but more context budget |
| **Lightweight** | gemma4-e2b, qwen3-4b | 8-16K | fleet-light, fast | Supervised — brain prescribes, agent executes |
| **Direct** | none | 0 | N/A | Deterministic — brain handles in Python, no LLM |

Tier selection: fleet backend_mode + task complexity + agent role. Security/architect agents never route below Expert.

Progressive rollout: Expert only (current) → add Capable → add Lightweight → add Flagship-Local → full spectrum. Each tier validated through the 91 tree scenarios before enabling.

## Architecture: TierRenderer

### Design Principle

**Preembed owns ORDER. Renderer owns DEPTH.**

`build_task_preembed()` and `build_heartbeat_preembed()` define the autocomplete chain — the section sequence that drives agent behavior. This doesn't change per tier. What changes is HOW MUCH of each section is rendered.

The TierRenderer encapsulates depth rules per section per tier. Preembed calls renderer methods; renderer returns content at the right depth.

### Module: `fleet/core/tier_renderer.py`

```python
class TierRenderer:
    """Render context sections at tier-appropriate depth.
    
    Reads depth rules from config/injection-profiles.yaml (updated
    to use tier names: expert, capable, flagship-local, lightweight).
    
    Preembed calls: renderer.format_task_detail(task)
    Renderer returns: content string at the right depth for the tier.
    """
    
    def __init__(self, tier: str = "expert"):
        self.tier = tier
        self.rules = load_tier_rules(tier)
    
    # ── Task sections ──
    def format_task_detail(self, task: Task) -> str: ...
    def format_verbatim(self, verbatim: str) -> str: ...  # NEVER compresses
    def format_stage_protocol(self, stage: str, role: str) -> str: ...
    def format_contributions(self, specs: list, received: list) -> str: ...
    def format_phase_standards(self, phase: str, progression: str) -> str: ...
    def format_action_directive(self, stage: str, progress: int, iteration: int) -> str: ...
    def format_chain_awareness(self, stage: str) -> str: ...
    def format_rejection_context(self, iteration: int, feedback: str) -> str: ...
    def format_confirmed_plan(self, plan_content: str) -> str: ...
    def format_previous_findings(self, findings: str) -> str: ...
    def format_target_task(self, target: Task) -> str: ...  # for contribution tasks
    
    # ── Heartbeat sections ──
    def format_directives(self, directives: list) -> str: ...  # NEVER compresses
    def format_messages(self, messages: list) -> str: ...
    def format_assigned_tasks(self, tasks: list) -> str: ...
    def format_role_data(self, role: str, data: dict) -> str: ...  # fixes F1-F4
    def format_standing_orders(self, orders: list, authority: str) -> str: ...
    def format_events(self, events: list) -> str: ...
    def format_context_awareness(self, ctx_pct: float, rate_pct: float) -> str: ...  # NEVER compresses
```

### Config: Updated `injection-profiles.yaml`

Rekey from model names to tier names. Same structure, better semantics.

```yaml
expert:
  description: "Full context — trust the agent"
  branches:
    task_detail: full
    contributions: full_inline
    protocol: full  # MUST/MUST NOT/CAN/How to advance
    phase_standards: full
    chain_awareness: full
    role_data: full_formatted
    events: 10
    standing_orders: full
    
capable:
  description: "Condensed — clear multi-step instructions"
  branches:
    task_detail: core_fields  # title+ID+stage+readiness+verbatim
    contributions: status_only  # type+from+status, fleet_read_context for content
    protocol: must_must_not  # no CAN, no How to advance
    phase_standards: one_liner
    chain_awareness: one_line
    role_data: counts_plus_top3
    events: 5
    standing_orders: name_desc_only

flagship_local:
  extends: capable
  description: "Large context local — more budget, same capability"
  branches:
    contributions: summary  # type+from+status+one-line summary
    role_data: counts_plus_top5
    events: 8

lightweight:
  description: "Focused — don't overwhelm the trainee"
  branches:
    task_detail: title_stage_only
    contributions: names_only
    protocol: short_rules  # 2-3 line MUST/MUST NOT
    phase_standards: name_only
    chain_awareness: omit
    role_data: counts_only
    events: count_only
    standing_orders: omit
```

### Never-Compress Rules (hardcoded, not configurable)

Regardless of tier, these are always rendered at full depth:
1. **PO directives** — PO words are sacrosanct
2. **Verbatim requirement** — THE anchor
3. **Context awareness warnings** — safety mechanism
4. **Stage MUST NOT rules** — preventing violations
5. **Rejection feedback** — agent must see what went wrong

### Integration: How It Wires In

```
Orchestrator _refresh_agent_contexts()
  │
  ├── Determine tier per agent:
  │   fleet_state.backend_mode + agent role + AICP profile → tier
  │
  ├── Create renderer:
  │   renderer = TierRenderer(tier)
  │
  ├── Build heartbeat:
  │   build_heartbeat_preembed(..., renderer=renderer)
  │   → calls renderer.format_role_data(role, data)
  │   → calls renderer.format_assigned_tasks(tasks)
  │   → etc.
  │
  ├── Build task context:
  │   build_task_preembed(task, ..., renderer=renderer)
  │   → calls renderer.format_task_detail(task)
  │   → calls renderer.format_contributions(specs, received)
  │   → calls renderer.format_stage_protocol(stage, role)
  │   → etc.
  │
  └── Navigator already tier-aware (uses injection-profiles.yaml)
```

## What This Fixes

### Validation Issue Resolution

| Issue | Category | Fix Mechanism |
|-------|----------|---------------|
| F1-F4 | Role data raw dicts | `renderer.format_role_data()` returns formatted strings per role |
| A1 | Heartbeat static for all states | Tier + state determines section content |
| A2 | Sections appear/disappear | Already partially fixed (sections always present). Renderer keeps this. |
| A3 | Role data raw Python dicts | Same as F1-F4 |
| A5 | No events section | Renderer always includes events ("None." if empty) |
| A6 | No context awareness | `renderer.format_context_awareness()` |
| A8 | Section order inconsistent | Preembed owns order (unchanged). Renderer only controls depth. |
| B1 | Contribution content placeholder | `renderer.format_contributions()` with full/status/names depth |
| H5 | Confirmed plan absent | `renderer.format_confirmed_plan()` — new section in work stage |
| H6 | Previous findings absent | `renderer.format_previous_findings()` — new section after reasoning |
| H9 | injection:none still produces full | Renderer at "none" injection level produces minimal |
| H11-H12 | Rejection rework invisible | `renderer.format_rejection_context()` — iteration, feedback, eng_fix_task_response |
| I1 | Contribution task can't see target | `renderer.format_target_task()` — target task context for contributors |
| I2-I3 | contribution_type/target not rendered | Renderer reads these fields and renders them |
| I5 | Methodology protocols role-generic | `renderer.format_stage_protocol(stage, role)` — role-specific text |
| J1 | Work protocol doesn't adapt to progress | `renderer.format_action_directive(stage, progress, iteration)` |

### Files Changed

| File | Change |
|------|--------|
| **fleet/core/tier_renderer.py** | NEW — the TierRenderer class |
| **fleet/core/preembed.py** | Accept `renderer` param, delegate formatting to it |
| **fleet/core/role_providers.py** | Return structured data (renderer handles formatting) OR move formatting into renderer |
| **config/injection-profiles.yaml** | Rekey from model names to tier names, add new branches |
| **fleet/cli/orchestrator.py** | `_refresh_agent_contexts()` creates renderer per agent, passes to preembed |
| **config/methodology.yaml** | Add role-specific protocol variants (or store in separate config) |
| **scripts/generate-validation-matrix.py** | Expand from 15 to 91 scenarios with tier parameter |
| **fleet/tests/core/test_preembed.py** | Expand tests to cover tier rendering |
| **fleet/tests/core/test_tier_renderer.py** | NEW — renderer tests per tier per section |

### Files NOT Changed

- **fleet/core/navigator.py** — already tier-aware, reads injection-profiles.yaml
- **agents/_template/** — static files stay the same (identity doesn't change per tier)
- **fleet/core/event_chain.py** — chains are tier-independent
- **fleet/core/models.py** — data model stays the same
- **fleet/mcp/tools.py** — MCP tools are tier-independent

## Fleet-Level Axes

Three independent fleet control axes affect context injection:

| Axis | Values | Impact |
|------|--------|--------|
| **work_mode** | full-autonomous, project-management-work, local-work-only, finish-current-work, work-paused | Paused/finish → agents see mode in fleet state. No structural change. |
| **cycle_phase** | execution, planning, analysis, investigation, review, crisis-management | Filters WHICH agents are active. Inactive agents get "not active in {phase}" instead of full context. |
| **backend_mode** | claude, localai, openrouter, and 4 hybrid combos | Determines tier selection. Security/architect always Expert. |

## Validation

91 scenarios across 3 categories:
- **26 heartbeat** — all state combinations x tier variations
- **45 task** — all stage x nature x contribution x tier combinations
- **20 fleet-level** — cycle_phase filtering, backend routing, budget modes, compound states

Each scenario:
1. Rendered by updated `generate-validation-matrix.py`
2. Inspected line by line
3. PO confirmed or corrected
4. Locked by pessimistic test

Full scenario list in the [context-injection-tree.md](../../../wiki/domains/architecture/context-injection-tree.md).

## Implementation Order

The three change types (A: tier adaptation, B: data formatting, C: missing data) are delivered together through the TierRenderer, but can be validated incrementally:

1. **TierRenderer scaffold** — module with all method signatures, Expert tier returns current behavior (no regression)
2. **Format fixes (B)** — `format_role_data()` per role replaces raw dicts. Validate HB-04, HB-05, HB-09, HB-10, HB-11, HB-12.
3. **Missing data (C)** — rejection context, confirmed plan, target task, role-specific protocols, progress-adapted actions. Validate TK-06, TK-07, TK-18, TK-19, TK-34-36, TK-38, TK-39.
4. **Tier adaptation (A)** — Capable and Lightweight tiers produce condensed/minimal output. Validate HB-19 through HB-26, TK-30, TK-31, TK-40, TK-41, TK-44, TK-45.
5. **Fleet-level** — cycle_phase filtering, backend_mode tier selection. Validate FL-01 through FL-20.
6. **Validation matrix expansion** — generate-validation-matrix.py covers all 91 scenarios.

Step 1-3 are the immediate priority (fix what Expert tier agents see). Step 4-5 are future tiers (add when backends are tested). Step 6 is the verification framework.
