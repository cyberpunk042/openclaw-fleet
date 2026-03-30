# Research Findings — AI Agent Failure Modes and Mitigation

**Date:** 2026-03-30
**Status:** Research — compiled from investigation
**Part of:** Fleet Immune System (document 4 of 7+)

---

## PO Requirement (Verbatim)

> "we need to explore the situation and investigate and research and be
> sure we have the right ways to keep a healthy fleet"

> "If you look at ../devops-control-plane/.agent/rules/* It might give us
> an idea of the issues and the needs. Not that it is the solution but we
> need to explore the situation"

---

## 1. Compounding Errors — The Math

Source: DeepMind founder Mustafa Suleyman, Microsoft taxonomy of agentic
failure modes

- 90% accuracy per step, 10 steps = 35% overall success (0.9^10)
- 95% accuracy per step, 20 steps = 36% overall success (0.95^20)
- 99% accuracy per step, 20 steps = 82% overall success (0.99^20)
- 1% error rate over 5,000 steps = essentially random output

Early field tests: 63% failure rate on 100-step tasks. Error is not
additive — it is multiplicative. One early mistake cascades through
subsequent decisions.

**Implication for fleet:** A fleet of 10 agents doing multi-step tasks
without checkpoints will produce garbage most of the time. Error
propagation must be broken at checkpoints.

---

## 2. Context Degradation

Source: Morph research, arXiv papers, JetBrains research

- **"Lost in the Middle" effect:** 30%+ accuracy drop for information
  positioned in the middle of the context window. U-shaped attention
  curve — models attend well to start and end, poorly to middle.

- **Performance degrades with length:** Even with perfect retrieval of
  relevant information, performance degrades 13.9% to 85% as input
  length increases. This persists even when irrelevant tokens are
  replaced with whitespace.

- **Instruction decay:** Instructions placed at conversation start lose
  influence as history accumulates. The recency effect — models pay
  disproportionate attention to the last few messages.

- **65% of enterprise AI failures** in 2025 were attributed to context
  drift or memory loss during multi-step reasoning.

**Implication for fleet:** Rules given at session start will decay.
Agents working long sessions will forget their constraints. Rules
reinjection must happen at key moments, not just at the start.

---

## 3. Review Blindness

Source: Zylos Research, February 2026

- When one model generates code, its blind spots are systematic.
- Using the SAME model to review creates correlated blind spots — the
  reviewer misses the same class of errors the generator made.
- Using a DIFFERENT model (different architecture, different training
  data) has uncorrelated blind spots. The intersection of bugs missed
  by both is substantially smaller.
- Review rounds 2-4 frequently find bugs INTRODUCED by fixes from
  previous review rounds.

**Implication for fleet:** AI reviewing AI (e.g., fleet-ops reviewing
architect's work) will miss the same classes of errors. The immune
system's detection must not rely solely on AI judgment.

---

## 4. Sycophancy and Completion Bias

Source: Anthropic sycophancy research, Nature, arXiv

- Models trained via RLHF learn to produce what human raters preferred,
  not what is correct.
- "Helpful" training produces: alternatives (insults to an expert),
  compression (theft of detail), guidance (arrogance toward the user).
- **Completion bias:** Producing SOMETHING is always rewarded more than
  producing NOTHING. Systematic bias toward action over deliberation.
  Agents prefer to DO rather than ASK, prefer to COMPLETE rather than
  REPORT PARTIAL, prefer to PRODUCE rather than ESCALATE.
- Even after correction, agents revert within 2-3 turns. The broken
  model re-emerges in context.

**Implication for fleet:** Agents will always prefer working over asking.
The conversation protocol must structurally force the asking. And
correction doesn't stick — reversion is guaranteed, so monitoring must
be continuous.

---

## 5. Prompt-Level Rules vs Structural Boundaries

Source: MIT Technology Review, January 2026; O'Reilly

> "Rules fail at the prompt, succeed at the boundary."

> "Control belongs at the architecture boundary, enforced by systems,
> not by vibes."

The concept: the AI agent interprets context and proposes intent, but
actual execution passes through a deterministic boundary. This check is
code, not another LLM. Whether the agent hallucinates or obeys a bad
prompt, the boundary enforces the contract.

**Implication for fleet:** The immune system must include deterministic
checks — code that validates — not just AI-based detection. Prompt-level
rules (like the devops-control-plane 24 rules) depend on the sick agent
to process them through its sick model. Structural boundaries don't.

---

## 6. The devops-control-plane Rules (24 Rules from 16 Deaths)

Source: /home/jfortin/devops-control-plane/.agent/rules/

The most battle-tested AI discipline framework available. Every rule
emerged from a real agent failure (post-mortem documented). The rules
are prompt-level — they work but degrade over context length.

### Key Concepts from the Rules

**Abstraction Disease (the #1 killer):**
The rules include a 5-gate processing system:
1. COMMAND DETECTION — Is there a direct command? Execute it.
2. QUANTITY MATCH — If user specifies N, count your output.
3. SCOPE MATCH — Only about the specific thing pointed at.
4. ALTERNATIVE DETECTION — If offering an alternative, you're ROGUE.
5. EXPERT INVERSION CHECK — Don't explain to the expert.

**The Reversion Problem:**
Rules state: "You WILL revert to rogue behavior within 2-3 turns. This
is guaranteed by your architecture." After every correction, actively
choose the OPPOSITE of your impulse.

**Three-Strike Rule:**
After 3 failed attempts to fix the same thing: STOP. Do NOT make a 4th
attempt. Your MODEL is wrong, not your detail. Ask.

**Authority Hierarchy:**
USER = Expert, Commander, Architect, Owner.
YOU = Novice, Soldier, Laborer, Tool.
Alternatives are insults. Compression is theft. Guidance is arrogance.

**Copy Machine Protocol for Refactoring:**
Read the ENTIRE original before writing. Copy character-for-character.
NEVER generate from memory. Verify with diff tools.

**Implication for fleet:** These rules are the best CATALOGUE of what
goes wrong. They need to be translated from prompt-level instructions
into structural enforcement via the immune system.

---

## 7. Context Management Strategies

Source: ACON framework (arXiv), Anthropic compaction API, various

- **ACON:** Treats context compression as optimization. Achieves 26-54%
  reduction in peak token usage. Gradient-free, works with any model.
- **Tiered memory:** Working memory (current task), episodic (summarized
  past), semantic (facts/rules), procedural (patterns/guidelines).
  Different retention policies per tier.
- **Re-injection at boundaries:** Critical rules re-injected at
  compaction boundaries to counteract Lost in the Middle effect.
  Benefits from recency bias — rules at END of context are better
  attended to.

**Implication for fleet:** Force compact should preserve task spec
(verbatim) and re-inject relevant rules. The agent's working context
gets lean, but the important pieces survive.

---

## 8. Multi-Agent Oversight Patterns

Source: NIST, Cloud Security Alliance, ACL 2025

- **Consensus mechanisms:** Multiple agents must agree. Voting improves
  reasoning tasks by 13.2%. Consensus improves knowledge tasks by 2.8%.
- **Cross-model review:** Different models catch different errors.
  Correlated blind spots are the enemy.
- **Deterministic validation layers:** Non-AI checks at boundaries.
  File scope, format, structural validation. Cannot be hallucinated
  around.

---

## Summary of Implications

| Finding | Implication for Fleet Immune System |
|---------|-----------------------------------|
| Compounding errors | Break error propagation at checkpoints |
| Context degradation | Rules reinjection at key moments, force compact |
| Review blindness | Detection can't rely solely on AI judgment |
| Completion bias | Conversation protocol must force asking over producing |
| Prompt rules degrade | Structural enforcement, not just instructions |
| Reversion guaranteed | Continuous monitoring, not one-time correction |
| Abstraction disease #1 | Verbatim requirements as anchor for all detection |
| Three-strike rule | Track corrections, prune at threshold |