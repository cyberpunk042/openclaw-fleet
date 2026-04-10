---
title: "Tier Rendering Design Rationale"
type: concept
domain: architecture
status: processing
confidence: medium
created: 2026-04-10
updated: 2026-04-10
tags: [tiers, rendering, capability, expert, capable, lightweight, context-injection, trainee]
---

# Tier Rendering Design Rationale

> "I would not overwhelm my trainee" — PO, 2026-04-09

## Summary

Context adaptation isn't about what FITS in the context window — it's about what the model can HANDLE. Five capability tiers drive rendering depth. Each tier represents a different autonomy level and gets appropriately adapted content.

## The Principle

Expert models get full context and full autonomy — they reason about what to do. Lightweight models get focused, direct instructions — the brain does the reasoning, the model executes. The spectrum: trust expert → guide capable → supervise lightweight → deterministic direct.

This is the quality dimension from the Methodology Framework applied to rendering: Expert = Skyscraper (full process). Capable/Flagship-Local = Pyramid (deliberate compression). Lightweight without proper guidance = Mountain (the anti-pattern to prevent).

## Section Depth by Tier

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

## What NEVER Compresses

Regardless of tier:
1. PO directives — sacrosanct
2. Verbatim requirement — the anchor
3. Context awareness warnings — safety mechanism
4. Stage MUST NOT rules — preventing violations
5. Rejection feedback — agent must see what went wrong

## Config: tier-profiles.yaml

The depth rules are DATA, not code. config/tier-profiles.yaml defines each tier's depth per section. The TierRenderer reads it. Adding a new tier or adjusting depth = config change.

## AICP Profile Mapping

| Tier | AICP Profile | Models | Context |
|------|-------------|--------|---------|
| Expert | N/A (cloud) | claude opus/sonnet | 200K-1M |
| Capable | default, code-review | qwen3-8b thinking | 16-32K |
| Flagship-Local | dual-gpu | gemma4-26b | 256K |
| Lightweight | fleet-light, fast | gemma4-e2b, qwen3-4b | 8-16K |
| Direct | N/A | none | 0 |
