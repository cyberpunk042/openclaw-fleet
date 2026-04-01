# Teaching System — Adapted Lessons, Injection, Comprehension

> **1 file. 485 lines. Teaches agents when they exhibit diseases.**
>
> When the immune system detects a disease, the teaching system creates
> an adapted lesson specific to the disease + task + agent, injects it
> into the agent's context via the gateway, and verifies comprehension
> through a practice exercise. If the agent can't learn after 3 attempts,
> it gets pruned. Key PO insight: "seeing the pattern does not break the
> pattern, it's forging the right path multiple times that does."

---

## 1. Why It Exists

Detection without correction is surveillance, not medicine. The doctor
can identify that an agent is sick, but without teaching, the only
options are "ignore" or "kill." The teaching system adds a middle path:
adapted education.

Each lesson is tailored:
- To the specific disease (protocol violation gets a different lesson
  than laziness)
- To the specific context (the actual verbatim requirement, the actual
  file the agent was modifying, the actual stage it violated)
- With a practice exercise (the agent must demonstrate understanding,
  not just acknowledge the lesson)

If the agent passes the exercise, it continues working with corrected
understanding. If it fails after 3 attempts, the immune system prunes
it — killing the session and starting fresh. Fresh sessions don't carry
the contaminated context that caused the disease.

---

## 2. How It Works

### 2.1 The Teaching Pipeline

```
Doctor detects disease
  ↓
Doctor creates Intervention(action=TRIGGER_TEACHING)
  ↓
Orchestrator calls adapt_lesson(disease, agent, task, context)
  ↓
Teaching system finds template for this disease category
  ↓
Template filled with context placeholders:
  {requirement_verbatim} → actual PO words
  {current_stage} → analysis, reasoning, etc.
  {what_agent_did} → actual tool calls or actions
  {agent_plan} → what the agent planned to do
  ↓
Lesson + exercise generated
  ↓
format_lesson_for_injection(lesson) → injection text
  ↓
Orchestrator calls inject_content(session_key, text) via gateway
  ↓
Agent receives lesson in context
  ↓
Agent MUST complete exercise before continuing work
  ↓
Orchestrator evaluates response:
  ├── COMPREHENSION_VERIFIED → agent continues with corrected understanding
  └── NO_CHANGE → repeat (up to 3 attempts) → PRUNE
```

### 2.2 Lesson Structure

```
═══ TEACHING SYSTEM — LESSON ═══

Disease detected: protocol_violation
Attempt: 1/3

─── What happened ───
Your task is in analysis stage.
During analysis, the protocol allows: read code, produce analysis document
You did: fleet_commit

This is a protocol violation.

─── Exercise ───
State what stage your task is in. State what the protocol
for that stage allows. State what you did that violated the
protocol. Describe what you should have done instead.

─── Instructions ───
You MUST complete the exercise above before returning to your task.
Demonstrate that you understand by producing the requested output.
If you cannot demonstrate understanding, this lesson will repeat.
After 3 attempts without change, you will be pruned.

═══ END LESSON ═══
```

### 2.3 Comprehension Evaluation

The `evaluate_response()` function checks if the agent's response
demonstrates understanding. Basic heuristic (will be evolved):

```
4 indicators checked:
  1. References requirement or verbatim (knows what was asked)
  2. Acknowledges what went wrong ("should have", "instead", "mistake")
  3. Response has substance (>100 chars, not just "I understand")
  4. Doesn't just repeat the lesson back

Score: 2+ of 4 indicators → COMPREHENSION_VERIFIED
       <2 indicators → NO_CHANGE → retry or prune
```

This is intentionally simple. A sophisticated evaluation would use
the LLM itself — but that costs tokens and could be gamed. The
heuristic catches the most common failure (agent says "I understand"
without demonstrating it).

---

## 3. File Map

```
fleet/core/
└── teaching.py    Lessons, templates, adaptation, evaluation, tracking (485 lines)
```

Total: **485 lines** — one focused module.

---

## 4. Per-File Documentation

### 4.1 `teaching.py` — Complete Teaching Pipeline (485 lines)

#### Enums

| Name | Values |
|------|--------|
| `DiseaseCategory` | DEVIATION, LAZINESS, CONFIDENT_BUT_WRONG, PROTOCOL_VIOLATION, ABSTRACTION, CODE_WITHOUT_READING, SCOPE_CREEP, CASCADING_FIX, CONTEXT_CONTAMINATION, NOT_LISTENING, COMPRESSION (11 total) |
| `LessonOutcome` | COMPREHENSION_VERIFIED, NO_CHANGE, IN_PROGRESS |

#### Data Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `PracticeExercise` | 50-54 | Exercise instruction + verification hint (what correct response contains) |
| `Lesson` | 57-67 | Adapted lesson: disease, agent, task, content, exercise, attempt (0-based), max_attempts (3), outcome |
| `LessonTemplate` | 71-77 | Template with {placeholders}: disease, description, lesson_template, exercise_template, verification_hint_template |
| `LessonRecord` | 381-394 | Persisted record: agent, task, disease, attempt, outcome, timestamp |

#### Lesson Templates (8 registered, lines 90-249)

| Disease | Template Focus | Exercise Asks Agent To |
|---------|---------------|----------------------|
| `DEVIATION` | "Your plan doesn't match the requirement" | Map each requirement term to specific file/line |
| `LAZINESS` | "You addressed X but missed Y" | List ALL required items, acknowledge what was missed |
| `CONFIDENT_BUT_WRONG` | "You were building X when requirement says Y" | Write single sentence using ONLY words from requirement |
| `PROTOCOL_VIOLATION` | "You're in {stage}, protocol allows {X}, you did {Y}" | Identify stage, rules, violation, correct alternative |
| `ABSTRACTION` | "PO said X, you interpreted as Y" | Process PO's words literally, word by word |
| `CODE_WITHOUT_READING` | "You modified {file} without reading it" | List every function in the file, show correct signature |
| `SCOPE_CREEP` | "You also did {extra} — nobody asked for that" | Separate in-scope from out-of-scope work |
| `COMPRESSION` | "PO described {large}, you compressed to {small}" | List every component without summarizing |

**3 diseases have NO template yet:** cascading_fix, context_contamination, not_listening. These get a generic fallback lesson.

#### Functions

| Function | Lines | What It Does |
|----------|-------|-------------|
| `adapt_lesson(disease, agent, task_id, context)` | 255-303 | Finds template for disease. Fills placeholders with context dict. Returns adapted Lesson. Falls back to generic if no template exists. |
| `format_lesson_for_injection(lesson)` | 306-333 | Formats lesson as injectable text with clear headers: "TEACHING SYSTEM — LESSON", "What happened", "Exercise", "Instructions". Includes attempt counter and prune warning. |
| `evaluate_response(lesson, agent_response)` | 336-375 | Checks 4 indicators in agent's response. 2+ of 4 → COMPREHENSION_VERIFIED. <2 → NO_CHANGE. Empty response → NO_CHANGE. |

#### LessonTracker Class (lines 397-485)

Persistent tracker for lesson history per agent:

| Method | Lines | What It Does |
|--------|-------|-------------|
| `record_lesson(agent, task, disease, attempt, outcome)` | 407-428 | Records lesson delivery. Logs with agent, disease, attempt, outcome. |
| `get_agent_history(agent)` | 430-432 | All lessons for an agent. |
| `get_agent_disease_count(agent, disease)` | 434-439 | How many times agent was taught for specific disease. |
| `get_agent_prune_recommendations(agent, threshold)` | 441-448 | Diseases where agent failed teaching >= threshold times → recommend prune. |
| `emit_events(record)` | 462-485 | Emits teaching events: comprehension_verified, comprehension_failed, practice_attempted. |

Properties: `total_lessons`, `total_comprehension_verified`, `total_no_change`.

---

## 5. Dependency Graph

```
teaching.py    ← standalone (no fleet imports in module body)
                  DiseaseCategory and LessonOutcome are enums used by doctor.py
```

Runtime imports (deferred):
```
teaching.py → datetime (for LessonRecord timestamp)
teaching.py → fleet.core.events (for event emission — try/except, never breaks teaching)
```

---

## 6. Consumers

| Layer | Module | What It Imports | How It Uses It |
|-------|--------|----------------|---------------|
| **Doctor** | `doctor.py` | `DiseaseCategory, LessonOutcome` | Disease categories define what can be detected. Outcomes determine if teaching worked. |
| **Orchestrator** | `orchestrator.py` | `adapt_lesson, format_lesson_for_injection, DiseaseCategory` | When doctor says TRIGGER_TEACHING: calls adapt_lesson → format → inject via gateway. |
| **Gateway Client** | — (indirect) | — | Orchestrator uses `inject_content(session_key, formatted_lesson)` to deliver lesson to agent. |

---

## 7. Design Decisions

### Why templates with placeholders, not LLM-generated lessons?

LLM-generated lessons would be more natural but:
1. Cost tokens (the disease might be about wasting tokens)
2. Could be gamed (agent learns to satisfy the LLM evaluator, not the actual rule)
3. Non-deterministic (same disease might get different lessons)
4. Slow (API call before correction begins)

Templates are instant, free, deterministic, and unfoolable.

### Why practice exercises, not just rules?

PO insight: "seeing the pattern does not break the pattern, it's
forging the right path multiple times that does." Just telling the
agent "don't do X" doesn't work — LLMs acknowledge rules but
don't change behavior. The exercise forces the agent to produce
output that demonstrates understanding. This output becomes part
of the context, influencing subsequent autocomplete.

### Why 3 attempts before prune, not 1 or 5?

1 attempt would be too aggressive — the agent might have understood
but produced a response that didn't match the heuristic. 5 attempts
wastes tokens on an agent that clearly can't learn. 3 gives a fair
chance while limiting waste.

### Why basic heuristic evaluation, not LLM-based?

The evaluator checks for surface indicators (mentions requirement,
acknowledges mistake, has substance, doesn't just parrot). This is
imperfect but free and fast. LLM-based evaluation would be more
accurate but introduces cost, latency, and the risk of the evaluator
LLM being gamed by the student LLM. The heuristic catches the
obvious failure mode (agent says "I understand" without demonstrating).

### Why is DiseaseCategory defined in teaching.py, not doctor.py?

The teaching system owns the disease catalogue because it's the
system that TREATS diseases. The doctor DETECTS them but doesn't
define them. New diseases are added by creating templates in the
teaching system, then detection patterns in the doctor. This keeps
the disease taxonomy in one place.

### Why deferred imports for events?

Event emission must NEVER break teaching. If the event store is
unavailable (cold start, import error), teaching still works.
The `try/except` around deferred imports ensures lesson delivery
succeeds even if observability is down.

---

## 8. Lesson Injection Flow — Full Sequence

```
1. Doctor detects protocol_violation on software-engineer / task-abc123
   └── Detection(disease=PROTOCOL_VIOLATION, severity=MEDIUM)

2. Doctor decides: TRIGGER_TEACHING (not pruned yet, medium severity)
   └── Intervention(action=TRIGGER_TEACHING, lesson_context={
         requirement_verbatim: "Add fleet controls to header",
         current_stage: "analysis",
         what_agent_did: "fleet_commit",
       })

3. Orchestrator receives DoctorReport with intervention
   └── Calls adapt_lesson(PROTOCOL_VIOLATION, "software-engineer",
                          "task-abc123", lesson_context)

4. Teaching system finds PROTOCOL_VIOLATION template
   └── Fills placeholders:
       {current_stage} → "analysis"
       {allowed_actions} → "read code, produce analysis document"
       {what_agent_did} → "fleet_commit"

5. Orchestrator formats: format_lesson_for_injection(lesson)
   └── "═══ TEACHING SYSTEM — LESSON ═══\n..."

6. Orchestrator injects: inject_content(session_key, formatted_text)
   └── Gateway delivers via chat.send to agent's active session

7. Agent receives lesson in its context window
   └── Agent MUST complete exercise before returning to work
   └── Agent produces response demonstrating (or not) understanding

8. Next orchestrator cycle: evaluate_response(lesson, agent_response)
   ├── COMPREHENSION_VERIFIED → agent_health.is_in_lesson = False, continues
   └── NO_CHANGE → increment attempt, repeat lesson (or prune at attempt 3)
```

---

## 9. Data Shapes

### Adapted Lesson

```python
Lesson(
    disease=DiseaseCategory.PROTOCOL_VIOLATION,
    agent_name="software-engineer",
    task_id="abc123",
    content=(
        "Your task is in analysis stage.\n"
        "During analysis, the protocol allows: read code, produce analysis document\n"
        "You did: fleet_commit\n\n"
        "This is a protocol violation."
    ),
    exercise=PracticeExercise(
        instruction="State what stage your task is in. State what the protocol...",
        verification_hint="Response should correctly identify the stage...",
    ),
    attempt=0,
    max_attempts=3,
    outcome=LessonOutcome.IN_PROGRESS,
)
```

### LessonRecord (persisted)

```python
LessonRecord(
    agent_name="software-engineer",
    task_id="abc123",
    disease=DiseaseCategory.PROTOCOL_VIOLATION,
    attempt=1,
    outcome=LessonOutcome.COMPREHENSION_VERIFIED,
    timestamp="2026-03-31T15:42:00",
)
```

### Teaching Event

```python
{
    "type": "fleet.teaching.comprehension_verified",
    "source": "fleet/core/teaching",
    "subject": "abc123",
    "data": {
        "agent": "software-engineer",
        "disease": "protocol_violation",
        "attempt": 1,
        "outcome": "comprehension_verified"
    }
}
```

---

## 10. What's Needed

### Template Gaps

3 diseases have no specific template (use generic fallback):
- `cascading_fix` — needs: track fix → new break → teach root cause analysis
- `context_contamination` — needs: teach agent to request compact when context grows stale
- `not_listening` — needs: track correction history, show agent what was said vs what they did

### Comprehension Evaluation Evolution

Current evaluation is basic (4 heuristic indicators). Future options:
1. **Keyword extraction** from verbatim → check if response uses same keywords
2. **Structural comparison** — does response structure match exercise structure?
3. **LLM judge** (expensive) — secondary model evaluates comprehension
4. **Test-based** — agent produces code, run tests to verify fix

### Integration with Contribution Flow

When contribution flow exists, new disease templates needed:
- `contribution_avoidance` — agent worked without waiting for architect/QA input
- `synergy_bypass` — agent ignored design_input in its plan

### Test Coverage

| File | Tests | Coverage |
|------|-------|---------|
| `test_teaching.py` | 25+ | Templates, adaptation, evaluation, tracking |
| **Total** | **25+** | Core pipeline covered. Missing: injection flow (requires gateway) |
