# Challenge Engine — Iterative Adversarial Validation

> **8 files. 2831 lines. The largest fleet system. Multi-round adversarial
> challenges BEFORE approval. 235 tests — the most thorough test suite.**
>
> Work doesn't go straight to review. It faces adversarial challenges
> first. 4 challenge types with different cost/quality tradeoffs:
> automated (free, pattern-based), agent (domain expert), cross-model
> (different LLM), scenario (reproduce-and-break for bugs). Budget mode
> determines depth. Deferred challenges queue for when budget improves.
> Each challenge round is a FULL adversarial review producing findings
> that the author must address — not a checkbox, but real investigation.

### PO Requirements (Verbatim)

> "we really have to be ready to do multiple agent iteration where the
> validation and testing had to be challenged and challenged in order
> to really fix the bugs and meet the requirements."

> "we need to avoid brainless loop and recursive chain that don't end"

> "in situation like we just experience we really have to be ready to
> do multiple agent iteration where the validation and testing had to
> be challenged and challenged"

---

## 1. Why It Exists

The March catastrophe showed that single-pass review is fiction.
Fleet-ops rubber-stamped approvals in under 30 seconds. Bugs shipped
to production. Surface-level testing ("does it start?") passed while
deep issues festered.

The challenge engine enforces REAL validation:
- **Automated:** deterministic pattern checks (FREE) catch mechanical
  errors — regressions, edge cases, race conditions, import cycles
- **Agent:** a different specialist reviews adversarially — not the
  author, not the same perspective
- **Cross-model:** a DIFFERENT LLM challenges the work — catches
  blind spots of the original model
- **Scenario:** for bug fixes — reproduce the original bug, then
  BREAK the fix with variations (boundary, concurrent, removal)

Each challenge round produces FINDINGS. Each finding has: category,
severity, description, evidence. The author must ADDRESS each finding
(commit fix, explain why it's not an issue, or escalate). Only when
ALL findings are resolved does the challenge pass.

```
BEFORE: work → review (30s rubber stamp) → done → bugs in production

AFTER:  work → challenge (adversarial findings with evidence)
        → author addresses each finding (real fixes)
        → re-challenge (did the fixes work?)
        → pass (all findings resolved)
        → review (fleet-ops has challenge evidence)
        → done (quality verified)
```

---

## 2. How It Works

### 2.1 The Full Challenge Flow

```
Agent calls fleet_task_complete(summary)
  ↓
evaluate_challenge(task, confidence_tier, budget_mode)
  ↓
ChallengeDecision:
  required: bool        ← tier + task_type + story_points determine
  challenge_type: str   ← automated / agent / cross-model / scenario
  deferred: bool        ← budget too tight → queue for later
  max_rounds: int       ← more rounds for lower confidence tiers
  challenger: str       ← who/what performs the challenge
  ↓
If not required:
  → proceed to review (readiness 80 → 90)
  
If deferred (frugal/survival/blackout):
  → labor stamp: challenge_skipped=True, reason="frugal mode" (W2)
  → task tagged: needs-deferred-challenge
  → DeferredChallengeQueue.enqueue(task) → persist to JSON
  → proceed to review (with flag: "challenge deferred")
  
If required:
  ↓
ChallengeRecord.start_round(type, challenger)
  ↓
CHALLENGE EXECUTION (depends on type):
  ↓
  ┌── AUTOMATED (FREE — no LLM, deterministic patterns):
  │   generate_automated_challenges(task, diff, files)
  │   → Up to 7 pattern checks against code diff:
  │     1. Regression: run full test suite
  │     2. Conditional edge cases: boundary values for if/else
  │     3. Loop handling: empty, single, max items
  │     4. Async/concurrency: race conditions, shared state
  │     5. Network timeout: missing timeout on external calls
  │     6. Architecture: import cycles in multi-file changes
  │     7. Error handling: bare except, swallowed exceptions
  │   → Each check produces AutomatedChallenge
  │   → AutomatedChallenge.to_finding() → ChallengeFinding
  │
  ├── AGENT (domain expert, costs Claude tokens):
  │   Brain assigns challenger agent by domain:
  │     security task → devsecops as challenger
  │     architecture task → architect as challenger
  │     code task → qa-engineer or different engineer
  │   Challenger receives:
  │     - Task verbatim requirement
  │     - Code diff
  │     - Author's plan and acceptance criteria
  │   Challenger posts findings as challenge_review contribution
  │   Author must address EACH finding
  │
  ├── CROSS-MODEL (different LLM, cost varies):
  │   CrossModelConfig selects model by complexity:
  │     simple → hermes-3b (free, LocalAI)
  │     medium → sonnet or OpenRouter free
  │     complex → opus (if budget allows)
  │   Build challenge message with full task context
  │   Parse response for findings (category, severity, description)
  │   Validate findings against expected_contains / expected_json_keys
  │
  └── SCENARIO (reproduce-and-break, for bug fixes):
      Generate 5 scenario types:
        1. REPRODUCTION: reproduce the original bug conditions
        2. REMOVAL: verify fix works if buggy code removed
        3. REGRESSION: check other functionality still works
        4. BOUNDARY: test boundary conditions around the fix
        5. CONCURRENCY: test concurrent access around the fix
      Run each scenario → pass/fail per scenario
      Failed scenarios → findings with evidence
  ↓
Findings collected
  ↓
ChallengeRound evaluated:
  ├── all_findings_resolved → PASSED
  │   └── ChallengeRecord.rounds_survived += 1
  │       → labor stamp: challenge_rounds_survived, challenge_types_faced
  │       → readiness: 70% (work complete) → 80% (challenge passed)
  │       → proceed to review
  │
  ├── open_findings remain → FAILED
  │   └── Author receives findings
  │       → Each finding: category, severity, description, evidence
  │       → Author addresses each (commit fix, explain, escalate)
  │       → Finding status: open → addressed → verified
  │       → If can_add_round → re-challenge (new round)
  │       → If max_rounds reached → escalate to PO
  │
  └── round waived → WAIVED (PO decision)
      → proceed to review with waiver noted
```

### 2.2 Challenge Depth by Budget Mode (W1 Wiring)

The challenge depth adapts to budget. W1 wiring means challenge_deferred.py
imports `MODE_ORDER` from budget_modes — no hardcoded constants.

| Budget Mode | Challenge Strategy | Cost |
|------------|-------------------|------|
| blitz | Full: automated + agent + cross-model for SP≥5. Automated for rest. | $$$ |
| standard | Agent for SP≥5 or trainee tier. Automated for rest. | $$ |
| economic | Automated only (free). Agent only for security-tagged tasks. | $ |
| frugal | Automated only. Agent/cross-model/scenario all DEFERRED. | ¢ |
| survival | ALL challenges deferred. Tag task for later. | $0 |
| blackout | No work, no challenges. | $0 |

When challenge is deferred:
- Labor stamp: `challenge_skipped=True, challenge_skip_reason="frugal mode"` (W2 wiring)
- Task tagged: `needs-deferred-challenge`
- Deferred queue persists to `state/deferred_challenges.json`
- When budget improves (e.g., frugal → standard), brain drains queue

### 2.3 Challenge by Confidence Tier

Lower confidence = more challenge. Trainee-tier work (LocalAI) gets
3 rounds of adversarial validation. Expert-tier work (opus) gets
optional automated check only.

| Tier | Required? | Max Rounds | Challenge Types |
|------|-----------|-----------|----------------|
| expert | Optional | 1 | Automated only (if any) |
| standard | Recommended for SP≥5 | 2 | Automated + agent |
| trainee | **MANDATORY** | 3 | Automated + agent + cross-model |
| community | **MANDATORY** | 3 | All 4 types (including scenario for bugs) |
| hybrid | **MANDATORY** | 3 | Automated + agent |

The confidence tier comes from the labor stamp (auto-derived from
backend + model). Trainee/community tier → `requires_challenge = True`
on the stamp → challenge engine enforces.

### 2.4 Challenge Readiness Checkpoints

Challenge results feed task readiness:

```
70% → WORK_COMPLETE      Work is done, ready for challenge
80% → CHALLENGE_PASSED   Challenge survived, ready for review
90% → REVIEW_PASSED      Fleet-ops approved
95% → PO_APPROVED        PO gate confirmed (for phase advancement)
100% → DONE              Task complete
```

### 2.5 Deferred Challenge Queue

When budget is tight, challenges are deferred — NOT skipped permanently.

```
DeferredChallengeQueue:
  Storage: state/deferred_challenges.json (survives restarts)
  Ordering: FIFO + priority boost for high story points
  Status: OK (<10) / warning (10-25) / critical (>25)
  
should_defer_challenge("frugal") → True  (DEFERRAL_MODES)
should_defer_challenge("standard") → False (PROCESSING_MODES)

can_process_deferred(previous="frugal", current="standard") → True
  Budget improved → drain deferred queue

drain_batch_size by mode:
  blitz=10, standard=5, economic=3  (process N deferred per cycle)
```

### 2.6 Finding Lifecycle

Each finding goes through its own lifecycle:

```
OPEN       → Challenger posted finding, author hasn't addressed
ADDRESSED  → Author claims fixed (commit SHA or explanation)
VERIFIED   → Challenger confirmed fix works
WONT_FIX   → Accepted risk (requires PO approval)
INVALID    → Finding was incorrect (challenger agrees)
```

A challenge round PASSES when: all findings are in verified/wont_fix/invalid.
Open or addressed findings → round still FAILED → re-challenge or escalate.

---

## 3. File Map

```
fleet/core/
├── challenge.py            Data model: 3 enums, 3 classes              (353 lines)
│                           ChallengeType, ChallengeStatus, FindingStatus
│                           ChallengeFinding, ChallengeRound, ChallengeRecord
│
├── challenge_protocol.py   Decision engine: evaluate, select, configure (596 lines)
│                           is_challenge_required(), select_challenge_type()
│                           select_challenger_agent(), max_rounds_for_tier()
│                           evaluate_challenge() — combined decision
│
├── challenge_automated.py  7 pattern checks (FREE, no LLM)             (278 lines)
│                           generate_automated_challenges(task, diff, files)
│                           Checks: regression, conditionals, loops, async,
│                           timeout, architecture, error handling
│
├── challenge_cross_model.py Different LLM reviews work                  (346 lines)
│                           CrossModelConfig: models per complexity
│                           build_challenge_message(), parse_response()
│                           extract_findings_from_json()
│
├── challenge_scenario.py   Reproduce-and-break for bug fixes            (299 lines)
│                           5 scenario types: reproduction, removal,
│                           regression, boundary, concurrency
│                           generate_scenarios(), evaluate_results()
│
├── challenge_readiness.py  Readiness gates: 70→80→90→95→100             (281 lines)
│                           5 checkpoints: WORK_COMPLETE, CHALLENGE_PASSED,
│                           REVIEW_PASSED, PO_APPROVED, DONE
│                           check_readiness(), stage_label(), emoji()
│
├── challenge_deferred.py   Budget-aware deferral queue                  (337 lines)
│                           should_defer_challenge(), DeferredChallengeQueue
│                           FIFO + priority, JSON persistence, drain logic
│                           W1 wiring: imports MODE_ORDER from budget_modes
│
└── challenge_analytics.py  Per-agent/tier pass rates, teaching signals  (341 lines)
                            ChallengeEvent, AgentMetrics, TierMetrics
                            TeachingSignal: patterns → teaching system
                            summary(), format_report()
```

Total: **2831 lines** across 8 modules — the largest fleet system.

---

## 4. Per-File Documentation

### 4.1 `challenge.py` — Data Model (353 lines)

#### Enums

| Enum | Values | Purpose |
|------|--------|---------|
| `ChallengeType` | AUTOMATED, AGENT, CROSS_MODEL, SCENARIO | 4 types ordered by cost |
| `ChallengeStatus` | PENDING, IN_PROGRESS, PASSED, FAILED, WAIVED, DEFERRED | Round/challenge lifecycle |
| `FindingStatus` | OPEN, ADDRESSED, VERIFIED, WONT_FIX, INVALID | Individual finding lifecycle |

#### Classes

| Class | Lines | Key Fields | Key Properties |
|-------|-------|-----------|---------------|
| `ChallengeFinding` | 62-91 | finding_id, round_number, challenge_type, category, severity, description, evidence, status, addressed_by | to_dict() |
| `ChallengeRound` | 98-147 | round_number, challenge_type, challenger, status, findings, started/completed_at | is_complete, open_findings, has_open_findings, all_findings_resolved. Methods: add_finding(), start(), complete() |
| `ChallengeRecord` | 153-220 | task_id, rounds, max_rounds, current_round | status (overall), total_findings, open_findings, challenge_types_faced (for stamp), rounds_survived (for stamp), can_add_round. Method: start_round() |

### 4.2 `challenge_protocol.py` — Decision Engine (596 lines)

| Function | What It Does |
|----------|-------------|
| `is_challenge_required(task_type, SP, tier, budget_mode)` | Returns (required, reason). Mandatory for trainee/community. Required for SP≥5 or security. Budget can defer. |
| `select_challenge_type(task_type, SP, tier, budget_mode, is_bug)` | Bugs→scenario. Trainee→cross_model. SP≥5→agent. Else→automated. Budget economic→automated only. |
| `select_challenger_agent(task_type, author)` | Pick domain-appropriate agent that's NOT the author. Security→devsecops. Architecture→architect. |
| `max_rounds_for_tier(tier)` | trainee/community=3, standard=2, expert=1 |
| `evaluate_challenge(task, tier, budget, author, is_bug)` | Combined: required? + type + deferred? + max_rounds + challenger → ChallengeDecision |

ChallengeDecision dataclass: required, reason, challenge_type, challenger, max_rounds, deferred.

### 4.3 `challenge_automated.py` — Free Checks (278 lines)

| Function | What It Does |
|----------|-------------|
| `generate_automated_challenges(task, diff, files)` | Generate challenges from diff patterns. Returns list[AutomatedChallenge]. |

7 pattern detectors (all regex-based, all FREE):

| Check | Detects | Severity | Triggered By |
|-------|---------|----------|-------------|
| Regression | Test suite should be run after code changes | critical | Any .py/.js/.ts/.go changes |
| Conditional edge | Boundary values for new if/elif/else/match | minor | `+.*\b(if|elif|else|match)\b` in diff |
| Loop handling | Empty/single/large input for new for/while loops | minor | `+.*\b(for|while|loop)\b` in diff |
| Async/concurrency | Race conditions, shared state | major | `+.*\b(async|await|Thread|Lock)\b` |
| Network timeout | Missing timeout on HTTP/external calls | major | `+.*\b(requests|httpx|urllib|aiohttp)\b` |
| Import cycles | Circular imports in multi-file changes | minor | >1 file changed + import patterns |
| Error handling | Bare except, swallowed exceptions | minor | `+.*\bexcept\b:` without specific type |

### 4.4 `challenge_cross_model.py` — Cross-Model (346 lines)

| Class/Function | What It Does |
|---------------|-------------|
| `CrossModelConfig` | Maps complexity → challenger model: simple=hermes-3b, medium=sonnet, complex=opus |
| `build_challenge_message(task, diff, requirement)` | Build prompt for challenger model with full context |
| `extract_findings_from_json(response)` | Parse LLM response for structured findings (JSON array) |
| `compare_responses(prod_response, candidate_response, expected)` | Compare production vs candidate outputs |

### 4.5 `challenge_scenario.py` — Reproduce-and-Break (299 lines)

5 scenario types for bug fixes:

| Scenario | What It Tests |
|----------|-------------|
| Reproduction | Reproduce the original bug conditions — verify fix prevents it |
| Removal | What happens if the fix code is removed? Bug should return |
| Regression | Does the fix break anything else? Run related tests |
| Boundary | Test boundary conditions near the bug (off-by-one, limits, empty) |
| Concurrency | Test concurrent access around the fix (race conditions) |

### 4.6 `challenge_readiness.py` — Progression Gates (281 lines)

5 checkpoints mapped to readiness values:

| Checkpoint | Readiness | Meaning |
|-----------|-----------|---------|
| WORK_COMPLETE | 70 | Work is done, challenge can begin |
| CHALLENGE_PASSED | 80 | All challenge findings resolved |
| REVIEW_PASSED | 90 | Fleet-ops approved |
| PO_APPROVED | 95 | PO gate (phase advancement) confirmed |
| DONE | 100 | Task complete |

### 4.7 `challenge_deferred.py` — Budget Queue (337 lines)

| Constant/Function | What It Does |
|-------------------|-------------|
| `DEFERRAL_MODES` | {"frugal", "survival", "blackout"} — defer challenges |
| `PROCESSING_MODES` | {"blitz", "standard", "economic"} — process challenges |
| `MODE_STRICTNESS` | Derived from budget_modes.MODE_ORDER (W1 wiring) |
| `should_defer_challenge(mode)` | True if mode in DEFERRAL_MODES |
| `DeferredChallengeQueue` | FIFO + priority. Persist to JSON. Drain by batch size. Status alerts. |

### 4.8 `challenge_analytics.py` — Metrics (341 lines)

| Class | What It Tracks |
|-------|---------------|
| `ChallengeEvent` | Per-challenge: task, agent, tier, type, passed, rounds, findings |
| `AgentMetrics` | Per-agent: pass rate, avg rounds, findings count, categories |
| `TierMetrics` | Per-tier: pass rate, challenge requirements, findings |
| `TeachingSignal` | Patterns of repeated failures → feed into teaching system |
| `ChallengeAnalytics` | Engine: record(), agent_metrics(), tier_metrics(), common_categories(), teaching_signals() |

---

## 5. Dependency Graph

```
challenge.py              ← standalone (enums, dataclasses, time)
    ↑
challenge_protocol.py     ← imports ChallengeType, ChallengeFinding from challenge
                            imports Task from models
    ↑
challenge_automated.py    ← imports ChallengeFinding, ChallengeType from challenge
                            imports Task from models
    
challenge_cross_model.py  ← standalone (prompt construction, JSON parsing)
    
challenge_scenario.py     ← standalone (scenario generation)
    
challenge_readiness.py    ← standalone (checkpoint definitions)
    
challenge_deferred.py     ← imports MODE_ORDER from budget_modes (W1 wiring)
    
challenge_analytics.py    ← standalone (analytics engine)
```

Cross-system connections:
- W1: challenge_deferred imports budget_modes.MODE_ORDER
- W2: labor_stamp.mark_challenge_skipped() records deferral
- Codex review (codex_review.py) can serve as cross-model challenger

---

## 6. Consumers

| Layer | Module | Connection |
|-------|--------|-----------|
| **Budget** | W1 | challenge_deferred imports MODE_ORDER for budget-aware deferral |
| **Labor Stamps** | W2 | mark_challenge_skipped() records deferral reason on stamp |
| **Labor Stamps** | — | ChallengeRecord.rounds_survived, challenge_types_faced → stamp fields |
| **Codex Review** | W7 | Can serve as cross-model challenger for trainee-tier work |
| **Teaching** | — | ChallengeAnalytics.teaching_signals() feeds disease detection |
| **Methodology** | — | Challenge readiness checkpoints (70→80) gate stage progression |

---

## 7. Design Decisions

### Why 4 challenge types, not 1 or 10?

Each type targets different failure modes:
- **Automated** catches MECHANICAL errors (free, instant, deterministic)
- **Agent** catches DESIGN errors (human-like review, costs tokens)
- **Cross-model** catches MODEL BLIND SPOTS (different perspective)
- **Scenario** catches BUG REGRESSIONS (reproduce + break)

1 type would miss categories. 10 would add ceremony without value.
4 covers the failure taxonomy with clear cost/benefit for each.

### Why deferred queue, not permanent skip?

Permanent skip = trainee work NEVER validated. The PO said: "challenged
and challenged." Deferring means: "we can't afford it NOW but we WILL
validate." The queue persists to JSON. When budget improves (frugal →
standard), the brain drains the queue. Nothing permanently escapes
validation.

### Why max_rounds by tier, not fixed?

Expert-tier work (opus) is high quality — 1 round of automated
checks is usually sufficient. Trainee-tier work (LocalAI 3B) is
lower quality — 3 rounds catches issues that surface only after
fixes are applied. More rounds = more token cost, so tying it to
tier balances thoroughness with economics.

### Why finding lifecycle (open→addressed→verified)?

A finding isn't resolved just because the author says "fixed."
The challenger must VERIFY the fix. WONT_FIX requires PO approval
(accepting risk). INVALID means the challenger was wrong (it
happens). This lifecycle prevents rubber-stamping findings.

### Why automated checks are pattern-based, not LLM?

Automated challenges must be FREE (zero tokens). They run on EVERY
task regardless of budget mode. Regex pattern detection on diffs
catches common issues (missing timeout, bare except, race conditions)
deterministically. An LLM-based automated check would cost tokens
and defeat the purpose of "free validation."

### Why separate analytics module?

Challenge analytics feeds TWO systems: teaching (repeated failures
suggest disease patterns) and PO reporting (which tiers/agents fail
most). Separating analytics from protocol keeps the decision engine
clean and testable independently.

---

## 8. Data Shapes

### ChallengeDecision

```python
ChallengeDecision(
    required=True,
    reason="trainee tier requires mandatory challenge",
    challenge_type="cross-model",
    challenger="hermes-3b",
    max_rounds=3,
    deferred=False,
)
```

### ChallengeFinding

```python
ChallengeFinding(
    finding_id="CF-001",
    round_number=1,
    challenge_type="automated",
    category="edge_case",
    severity="minor",
    description="Empty input list not handled — function crashes with IndexError",
    evidence="pytest test_router.py::test_empty_input FAILED\n"
             "IndexError: list index out of range at line 42",
    status="open",
    addressed_by="",
)
```

### ChallengeRecord (after 2 rounds)

```python
ChallengeRecord(
    task_id="abc123",
    max_rounds=3,
    current_round=2,
    rounds=[
        ChallengeRound(
            round_number=1,
            challenge_type="automated",
            challenger="automated",
            status="failed",
            findings=[finding_1, finding_2],  # 2 issues found
        ),
        ChallengeRound(
            round_number=2,
            challenge_type="automated",
            challenger="automated",
            status="passed",
            findings=[],  # author fixed both issues
        ),
    ],
    # status = "passed"
    # rounds_survived = 1  (1 passed round)
    # challenge_types_faced = ["automated"]
    # total_findings = 2
    # open_findings = 0
)
```

### DeferredChallengeQueue Status

```python
{
    "queue_size": 15,
    "status": "warning",  # OK < 10, warning 10-25, critical > 25
    "oldest_age_hours": 48,
    "by_tier": {"trainee": 8, "community": 5, "hybrid": 2},
    "by_type": {"automated": 3, "agent": 7, "cross-model": 5},
}
```

---

## 9. What's Needed

### Integration Gaps

- **Connect to fleet-ops review flow:** Challenge results should be
  available to fleet-ops during review — currently challenge and review
  are separate flows not connected
- **Automated challenge live test:** Run pattern checks against a REAL
  code diff from a REAL agent completion — never tested end-to-end
- **Cross-model with LocalAI:** Use hermes-3b as free challenger for
  trainee-tier work — the infrastructure exists but integration doesn't
- **Deferred queue drain in orchestrator:** Brain should monitor budget
  mode changes and drain the deferred queue when budget improves —
  the queue logic exists but orchestrator doesn't call it
- **Teaching signals:** ChallengeAnalytics.teaching_signals() identifies
  repeated failure patterns — these should feed the teaching system
  for adapted lessons
- **Contribution flow dependency:** Agent challenges (type=AGENT)
  require the contribution flow (fleet_contribute tool) which doesn't
  exist yet

### Test Coverage

| File | Tests | What's Covered |
|------|-------|---------------|
| `test_challenge.py` | 20 | Data model: types, statuses, finding lifecycle, round management |
| `test_challenge_protocol.py` | 37 | Decision logic: every tier × budget × task_type combination |
| `test_challenge_automated.py` | 15 | Pattern detection: each of 7 checks |
| `test_challenge_cross_model.py` | 30 | Config, message building, JSON parsing, response comparison |
| `test_challenge_scenario.py` | 31 | 5 scenario types: generation, evaluation, findings |
| `test_challenge_readiness.py` | 35 | Checkpoints, readiness computation, stage labels |
| `test_challenge_deferred.py` | 43 | Queue: enqueue, dequeue, priority, persistence, drain, status |
| `test_challenge_analytics.py` | 24 | Events, per-agent/tier metrics, teaching signals |
| **Total** | **235** | **Most thorough test suite in the fleet** |
