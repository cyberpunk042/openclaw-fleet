---
title: "Tier Rendering Design Rationale"
type: concept
domain: architecture
status: processing
confidence: medium
created: 2026-04-10
updated: 2026-04-20
tags: [tiers, rendering, capability, expert, capable, lightweight, context-injection, trainee]
sources:
  - id: brain-2026-hardware-stack
    type: documentation
    project: devops-solutions-research-wiki
    path: wiki/spine/references/2026-consumer-hardware-ai-stack.md
    title: "The 2026 Consumer-Hardware AI Stack"
  - id: brain-open-model-eval-framework
    type: documentation
    project: devops-solutions-research-wiki
    path: wiki/spine/references/open-model-evaluation-framework.md
    title: "Open-Model Evaluation Framework"
---

# Tier Rendering Design Rationale

> "I would not overwhelm my trainee" — PO, 2026-04-09

## Summary

Context adaptation isn't about what FITS in the context window — it's about what the model can HANDLE. Five capability tiers drive rendering depth. Each tier represents a different autonomy level and gets appropriately adapted content.

## Key Insights

1. **Context adaptation is about model CAPABILITY, not context window size.** Five capability tiers (Expert / Capable / Flagship-local / Lightweight / Direct) each represent a different autonomy level and receive correspondingly adapted rendering depth. A 1M-token window on a lightweight model is still a lightweight task.

2. **Expert → Lightweight is a spectrum of trust, not just detail.** Expert models get full context and full autonomy — they reason about what to do. Lightweight models get focused, direct instructions — the brain does the reasoning, the model executes. The spectrum: trust expert → guide capable → supervise lightweight → deterministic direct.

3. **The tier system maps to the Methodology quality dimension.** Expert = Skyscraper (full process). Capable/Flagship-local = Pyramid (deliberate compression). Lightweight without proper guidance = Mountain (the anti-pattern to prevent — "overwhelming the trainee" per the 2026-04-09 PO directive).

4. **Depth rules are DATA, not code.** `config/tier-profiles.yaml` defines each tier's per-section depth. TierRenderer reads it. Adding a new tier or adjusting depth is a config change, never a code change.

5. **Some sections never compress.** PO directives, verbatim requirement, context-awareness warnings, stage MUST NOT rules, and rejection feedback all render at full depth regardless of tier — they are safety mechanisms, not adaptable content.

## Deep Analysis

### The Principle

Expert models get full context and full autonomy — they reason about what to do. Lightweight models get focused, direct instructions — the brain does the reasoning, the model executes. The spectrum: trust expert → guide capable → supervise lightweight → deterministic direct.

This is the quality dimension from the Methodology Framework applied to rendering: Expert = Skyscraper (full process). Capable/Flagship-Local = Pyramid (deliberate compression). Lightweight without proper guidance = Mountain (the anti-pattern to prevent).

### Section Depth by Tier

| Section | Expert | Capable | Lightweight |
|---------|--------|---------|-------------|
| Task detail | All fields (7+) | Core (ID, priority, type) | Title + ID only |
| Protocol | Full MUST/MUST NOT/CAN/Advance | MUST + MUST NOT only | 2-line condensed rules |
| Contributions | ✓/awaiting per item + content | ✓/awaiting per item, status_only | "Inputs: name (role)" one line |
| Phase standards | Bullet per standard | One-line summary | Phase name only |
| Action directive | Full text | Full text | One sentence |
| Messages | Full | Full | Truncated to 100 chars |
| Standing orders | Full (name, desc, when, boundary) | Name + description only | Omit |
| Events | Up to 10, formatted | Up to 5 | Count only |
| Role data | Full items (limit 5) | Counts + top 3 | Counts only |

### What NEVER Compresses

> [!warning] Safety-critical sections render at full depth regardless of tier
>
> Compressing the content below would trade a few tokens for a correctness/safety risk. The tier system explicitly EXCLUDES these from the depth rules.

Regardless of tier:
1. PO directives — sacrosanct
2. Verbatim requirement — the anchor
3. Context awareness warnings — safety mechanism
4. Stage MUST NOT rules — preventing violations
5. Rejection feedback — agent must see what went wrong

### Config: tier-profiles.yaml

The depth rules are DATA, not code. config/tier-profiles.yaml defines each tier's depth per section. The TierRenderer reads it. Adding a new tier or adjusting depth = config change.

### AICP Profile Mapping

| Tier | AICP Profile | Models | Context |
|------|-------------|--------|---------|
| Expert | N/A (cloud) | claude opus/sonnet | 200K-1M |
| Capable | default, code-review | qwen3-8b thinking | 16-32K |
| Flagship-Local | dual-gpu | gemma4-26b | 256K |
| Lightweight | fleet-light, fast | gemma4-e2b, qwen3-4b | 8-16K |
| Direct | N/A | none | 0 |

### New-Candidate Evidence (brain 2026-04-17/18, SWALLOWED 2026-04-20)

Brain's [[2026-consumer-hardware-ai-stack|2026 Consumer-Hardware AI Stack synthesis]] and [[open-model-evaluation-framework|Open-Model Evaluation Framework]] flag new open-weight models that physically fit our tiers on the existing 19 GB VRAM dual-GPU setup. This is **candidate evidence** — not a tier remapping. Formal changes to tier-profiles.yaml remain PO-gated.

| Our Tier | Current model | Brain-flagged candidate (Apache 2.0) | Fit evidence |
|----------|---------------|--------------------------------------|--------------|
| Capable | qwen3-8b thinking | **gpt-oss-20b** | 16 GB Q4 fits; tool calling + structured outputs native; OpenFleet named beneficiary in brain synthesis |
| Flagship-Local | gemma4-26b | **Qwopus 27B (Qwopus3.5-27B Q4_K_M)** | 19 GB Q4 fits; reasoning-distilled from Opus traces; 95.73% HumanEval claimed (needs independent verification per Principle 4) |
| Flagship-Local (batch tier) | — | **gpt-oss-120b via llama.cpp `-ngl` offload** | 19 GB VRAM + NVMe offload at 2-3 tok/s; substantive-reasoning-tier candidate |

**Strategic implication brain identifies**: Apache 2.0 gpt-oss models can ship *bundled* with OpenFleet deployments → no per-invocation API dependency, no rate-limit exposure. Relevant for E005 (multi-model strategy) and E006 (budget/tempo modes) but requires PO decision on whether to re-spec capable/flagship tiers.

**Evaluation methodology** for new models targeting our tiers: use brain's [[open-model-evaluation-framework|5-stage flow]] (Identify → Size & Fit → Capability → Deployment → Slot).

## Relationships

- BUILDS ON: [[Methodology Models Rationale]]
- BUILDS ON: The quality dimension from the brain's `model-methodology.md` (Skyscraper/Pyramid/Mountain)
- RELATES TO: [[Context Injection Decision Tree]]
- RELATES TO: [[Shared Models Integration — LLM Wiki + Methodology in OpenFleet]]
- RELATES TO: Brain pattern `Tier-Based Context Depth — Trust Earned Through Approval Rates` (one of the 7 OpenFleet patterns the brain extracted)
- IMPLEMENTS: "I would not overwhelm my trainee" (PO directive 2026-04-09)
- FEEDS INTO: `config/tier-profiles.yaml` + `fleet/core/tier_renderer.py`
