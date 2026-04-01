# Methodology System — Stage-Gated Task Progression

> **3 files. 877 lines. Controls HOW agents work through tasks.**
>
> Every task has a stage (conversation, analysis, investigation, reasoning,
> work) and a readiness percentage (0-100). Stages advance when explicit
> boolean checks pass and the PO confirms. Work stage is ONLY entered at
> readiness 99-100%. This is the core discipline mechanism — without it,
> agents produce code before understanding requirements.

---

## 1. Why It Exists

Before the methodology system, agents received a task and immediately
started coding. The result:

- Code that didn't match requirements (no conversation to clarify)
- Solutions without research (no investigation of alternatives)
- Plans that didn't reference the PO's words (no reasoning stage)
- Implementations that deviated from what was asked (no anchoring)

The methodology system solves this by enforcing a progression:

```
UNDERSTAND → EXAMINE → RESEARCH → PLAN → EXECUTE

conversation   analysis   investigation   reasoning   work
     │              │            │              │         │
     ▼              ▼            ▼              ▼         ▼
  Ask PO         Read code    Multiple      Plan with   Follow
  questions      and docs     options       verbatim    the plan
                              explored      reference
     │              │            │              │         │
     ▼              ▼            ▼              ▼         ▼
  NO code        NO solutions  NO decisions  NO code    fleet_commit
  NO commits     NO commits    NO commits    NO commits fleet_task_complete
```

Each stage produces artifacts (documents, not code) except work stage.
Work stage requires readiness >= 99% — meaning the PO has confirmed
the plan. The agent can ONLY call `fleet_commit` and `fleet_task_complete`
in work stage. Calling them in any other stage is a protocol violation
detected by the immune system.

---

## 2. How It Works

### 2.1 The Stage Machine

```
                    ┌──────────────┐
                    │ CONVERSATION │ readiness: 10
                    │              │
                    │ Ask PO       │ checks:
                    │ questions    │  - has_verbatim_requirement
                    │              │  - has_po_response
                    │ NO code      │  - no_open_questions
                    └──────┬───────┘
                           │ ALL checks pass
                           ▼
                    ┌──────────────┐
                    │   ANALYSIS   │ readiness: 30
                    │              │
                    │ Read codebase│ checks:
                    │ produce      │  - has_analysis_document
                    │ analysis doc │  - po_reviewed
                    │              │
                    │ NO solutions │
                    └──────┬───────┘
                           │ ALL checks pass
                           ▼
                    ┌──────────────┐
                    │ INVESTIGATION│ readiness: 50
                    │              │
                    │ Research     │ checks:
                    │ MULTIPLE     │  - has_research_document
                    │ options      │  - multiple_options_explored
                    │              │  - po_reviewed
                    │ NO decisions │
                    └──────┬───────┘
                           │ ALL checks pass
                           ▼
                    ┌──────────────┐
                    │  REASONING   │ readiness: 80
                    │              │
                    │ Plan with    │ checks:
                    │ verbatim     │  - has_plan
                    │ reference    │  - plan_references_verbatim
                    │              │  - plan_specifies_files
                    │ NO code      │  - po_confirmed_plan
                    └──────┬───────┘
                           │ ALL checks pass + PO confirms
                           │ readiness reaches 99
                           ▼
                    ┌──────────────┐
                    │     WORK     │ readiness: 99-100
                    │              │
                    │ Execute plan │ checks:
                    │ fleet_commit │  - readiness >= 99
                    │ fleet_task_  │  - has_commits
                    │   complete   │  - has_pr
                    │              │  - acceptance_criteria_met
                    │ NO deviation │  - required_tools_called
                    └──────────────┘
```

### 2.2 Task Types Skip Stages

Not every task needs all 5 stages. A simple subtask doesn't need
a full investigation phase. The methodology system defines which
stages are required per task type:

```
epic:       conversation → analysis → investigation → reasoning → work
            (ALL stages — epics are complex)

story:      conversation → reasoning → work
            (skip analysis/investigation — stories have clear scope)

task:       reasoning → work
            (skip everything before planning — tasks are well-defined)

subtask:    reasoning → work
            (same as task — even simpler)

bug:        analysis → reasoning → work
            (analyze what's broken, plan fix, fix it)

spike:      conversation → investigation → reasoning
            (research only — NO work stage, spikes don't produce code)

concern:    conversation → analysis → investigation
            (analysis only — NO work stage, concerns don't produce code)

blocker:    conversation → reasoning → work
            (discuss, plan resolution, resolve)
```

This is configured in `DEFAULT_REQUIRED_STAGES` (methodology.py:44-91).
The PO or module can override with explicit stage lists.

### 2.3 Readiness Values

Readiness is NOT a continuous 0-100 scale. It's a set of specific
valid values that map to Plane labels:

```
Valid: 0, 5, 10, 20, 30, 50, 70, 80, 90, 95, 99, 100

Strategic checkpoints:
  0   nothing defined
  50  direction review (PO confirms approach)
  90  final review (PO confirms before work)
  99  work authorized (PO said "go")
  100 task complete
```

`snap_readiness(value)` rounds any number to the nearest valid value.

Suggested readiness per stage:
- conversation: 10
- analysis: 30
- investigation: 50
- reasoning: 80
- work: 99

These are SUGGESTIONS, not rules. The PO sets actual readiness.
The artifact tracker's `suggested_readiness` provides data-driven
suggestions based on artifact completeness.

### 2.4 Stage Checks — The Gate Mechanism

Each stage has a check function that returns `StageCheckResult`:

```python
StageCheckResult:
    stage: Stage               # which stage
    checks: list[StageCheck]   # individual checks
    can_advance: bool          # True only if ALL checks pass

StageCheck:
    name: str           # e.g. "verbatim_requirement_exists"
    description: str    # human-readable
    passed: bool        # did it pass?
```

ALL checks must pass for `can_advance = True`. There is no partial
advancement. Either the stage is complete or it's not.

### 2.5 Stage Instructions — What Agents See

When a task is dispatched or heartbeat context is built, the agent
receives stage-specific instructions from `stage_context.py`. Each
stage has a template:

```
## Current Stage: {STAGE_NAME}

### What you MUST do:
(stage-specific actions)

### What you MUST NOT do:
(stage-specific prohibitions — always includes "Do NOT call fleet_commit")

### What you CAN produce:
(allowed output types)

### How to advance:
(what needs to happen for PO to advance the stage)
```

This is injected into `context/task-context.md` via `preembed.py`.
The agent reads it and follows the protocol.

### 2.6 Delivery Phases — Distinct from Stages

Stages track how you WORK on a task.
Phases track how MATURE a deliverable is.

```
Stages (per task):
  conversation → analysis → investigation → reasoning → work

Phases (per deliverable, across many tasks):
  idea → conceptual → poc → mvp → staging → production
    OR: alpha → beta → rc → release
```

A deliverable in "mvp" phase has multiple tasks, each going through
their own stages. The phase determines quality standards and required
contributions, not the work protocol.

Phases are PO-defined in `config/phases.yaml`. The PO can:
- Create any number of phases with any name
- Define any progression sequence
- Set any standards per phase
- Require specific contributor roles per phase
- Require PO approval (gate) to advance phases

---

## 3. File Map

```
fleet/core/
├── methodology.py      Stage machine, checks, transitions (476 lines)
├── stage_context.py    Per-stage instructions for agents  (214 lines)
└── phases.py           Delivery phase progressions        (187 lines)

config/
└── phases.yaml         PO-defined phase progressions      (110 lines)
```

Total: **877 lines** of methodology code + **110 lines** of config.

---

## 4. Per-File Documentation

### 4.1 `methodology.py` — The Stage Machine (476 lines)

The core module. Defines stages, stage ordering, per-task-type
required stages, stage check functions, readiness values, initial
stage selection, and transition tracking.

#### Enums & Constants

| Name | Type | Value |
|------|------|-------|
| `Stage` | Enum | CONVERSATION, ANALYSIS, INVESTIGATION, REASONING, WORK |
| `STAGE_ORDER` | list[Stage] | [CONVERSATION, ANALYSIS, INVESTIGATION, REASONING, WORK] |
| `DEFAULT_REQUIRED_STAGES` | dict[str, list[Stage]] | Per task type (epic=all 5, task=reasoning+work, etc.) |
| `VALID_READINESS` | list[int] | [0, 5, 10, 20, 30, 50, 70, 80, 90, 95, 99, 100] |

#### Functions

| Function | Lines | What It Does |
|----------|-------|-------------|
| `get_required_stages(task_type, override)` | 122-141 | Returns ordered stage list for a task type. Override allows PO/module to specify custom stages. Falls back to reasoning+work if type unknown. |
| `get_next_stage(current_stage, required_stages)` | 144-174 | Given current stage and required list, returns the next stage in progression. If current isn't in required list, finds first required stage after current in global order. Returns None at end. |
| `get_initial_stage(task_type, has_verbatim, readiness, override)` | 177-207 | Determines where a new task starts. If readiness >= 99 and verbatim exists → work. If readiness >= 90 → reasoning. If readiness >= 50 → skip conversation. Otherwise first required stage. |
| `check_conversation_stage(has_verbatim, has_po_response, open_questions)` | 213-238 | 3 checks: verbatim exists, PO responded, no open questions. ALL must pass. |
| `check_analysis_stage(has_analysis_document, po_reviewed)` | 241-260 | 2 checks: analysis document produced, PO reviewed findings. |
| `check_investigation_stage(has_research, multiple_options, po_reviewed)` | 263-288 | 3 checks: research document, multiple options explored, PO reviewed. |
| `check_reasoning_stage(has_plan, references_verbatim, specifies_files, po_confirmed)` | 291-322 | 4 checks: plan exists, references verbatim requirement, specifies target files, PO confirmed. This is the critical gate — PO must confirm plan before work begins. |
| `check_work_stage(readiness, has_commits, has_pr, criteria_met, tools_called)` | 325-362 | 5 checks: readiness >= 99, commits exist, PR created, acceptance criteria met, required tools called. This validates work COMPLETION, not work START. |
| `suggest_readiness_for_stage(stage)` | 371-384 | Returns suggested readiness: conversation=10, analysis=30, investigation=50, reasoning=80, work=99. |
| `snap_readiness(value)` | 387-389 | Rounds any integer to nearest valid readiness value. |

#### Classes

| Class | Lines | What It Does |
|-------|-------|-------------|
| `StageCheck` | 95-99 | Single check: name, description, passed bool. |
| `StageCheckResult` | 103-119 | List of checks for a stage. `can_advance` = all_passed. Properties: passed_count, total_count, all_passed. |
| `StageTransition` | 396-411 | Record of a stage change: task_id, from/to stage, authorized_by, readiness before/after, checks passed/total, timestamp. |
| `MethodologyTracker` | 414-477 | Records transitions, emits `fleet.methodology.stage_changed` events. Methods: `record_transition()`, `get_task_history()`, `get_recent_transitions()`. |

### 4.2 `stage_context.py` — Agent Instructions (214 lines)

Templates injected into agent context showing what to do in each stage.

| Function | Lines | What It Does |
|----------|-------|-------------|
| `get_stage_instructions(stage)` | 188-200 | Returns full instruction template for a stage. Empty string if stage unknown. Used by preembed.py to inject into task context. |
| `get_stage_summary(stage)` | 203-214 | Returns one-line summary: "Discussing with PO — do NOT produce code", "Executing confirmed plan — follow tool sequence", etc. |

| Constant | Type | What It Contains |
|----------|------|-----------------|
| `STAGE_INSTRUCTIONS` | dict[Stage, str] | Full MUST/MUST NOT/CAN/HOW templates per stage. Each ~30 lines of instruction text. |

Key enforcement in every non-work stage instruction:
```
Do NOT call fleet_commit or fleet_task_complete
```

Work stage instruction specifies the required tool sequence:
```
1. fleet_read_context
2. fleet_task_accept
3. fleet_commit (one or more)
4. fleet_task_complete
```

### 4.3 `phases.py` — Delivery Maturity (187 lines)

PO-defined phase progressions loaded from `config/phases.yaml`.

| Function | Lines | What It Does |
|----------|-------|-------------|
| `_load_phases_config()` | 73-85 | Loads config/phases.yaml. Returns empty dict if missing. |
| `load_progressions()` | 88-108 | Parses YAML into PhaseProgression objects with PhaseDefinition lists. |
| `get_progressions()` | 117-122 | Cached access to all progressions. Loads once on first call. |
| `get_progression(name)` | 125-127 | Get specific progression ("standard", "release"). |
| `get_phase_definition(phase, progression)` | 130-143 | Get phase from progression. Falls back to searching all progressions. |
| `get_phase_standards(phase, progression)` | 146-152 | Quality standards dict. E.g., mvp → `{tests: "main flows", docs: "setup, usage"}`. |
| `get_required_contributions(phase, progression)` | 155-161 | Required contributor roles. E.g., mvp → `["architect", "qa-engineer", "devsecops-expert"]`. |
| `get_next_phase(current, progression)` | 164-173 | Next phase name. E.g., poc → mvp. |
| `is_phase_gate(phase, progression)` | 176-182 | Check if PO approval required. Default: True (every phase is gated). |
| `reload_phases()` | 185-187 | Force reload (after PO changes phases.yaml). |

| Class | Lines | What It Does |
|-------|-------|-------------|
| `PhaseDefinition` | 30-37 | name, description, standards dict, required_contributions list, gate bool. |
| `PhaseProgression` | 40-67 | Ordered phase list. Methods: phase_names, get_phase, get_next_phase, get_previous_phase. |

---

## 5. Dependency Graph

```
methodology.py      ← standalone (no fleet imports)
    ↑
stage_context.py    ← imports Stage enum from methodology
    ↑
phases.py           ← standalone (reads config/phases.yaml, no fleet imports)
```

External dependencies:
```
methodology.py   ← stdlib only (dataclasses, enum, typing)
stage_context.py ← imports Stage from methodology
phases.py        ← yaml, dataclasses, logging (stdlib + yaml)
```

No circular dependencies. No heavy imports. All three modules load fast.

---

## 6. Consumers

| Layer | Module | What It Imports | How It Uses It |
|-------|--------|----------------|---------------|
| **Context Assembly** | `context_assembly.py` | `get_required_stages`, `get_next_stage`, `Stage`, `get_stage_instructions`, `get_stage_summary` | Builds methodology section in task context: stage, instructions, readiness, required stages, next stage |
| **Preembed** | `preembed.py` | `get_stage_instructions` | Adds stage instructions to task pre-embed (context/task-context.md) |
| **Heartbeat Context** | `heartbeat_context.py` | `get_stage_instructions`, `get_stage_summary` | Includes stage info in heartbeat data |
| **Doctor** | `doctor.py` | `Stage` | Knows which stages are non-work (for protocol violation detection) |
| **Artifact Tracker** | `artifact_tracker.py` | `VALID_READINESS` | Maps artifact completeness to valid readiness values |
| **MCP Tools** | `tools.py` | — (string comparison) | `WORK_ONLY_TOOLS` checks `stage != "work"` |

---

## 7. Design Decisions

### Why 5 stages and not 3 or 7?

5 stages map to the natural progression of understanding a problem:
1. **Talk about it** (conversation) — understand what's being asked
2. **Look at what exists** (analysis) — understand current state
3. **Research options** (investigation) — understand what's possible
4. **Plan the approach** (reasoning) — decide and get confirmation
5. **Execute** (work) — implement the confirmed plan

Fewer stages would merge "understand" with "plan" — agents that plan
without understanding. More stages would add ceremony without value.

### Why can task types skip stages?

A simple subtask with clear requirements doesn't need investigation.
An epic with unclear scope needs every stage. Skip logic prevents
ceremony fatigue while maintaining rigor where it matters.

### Why readiness 99 for work, not 100?

100 means DONE (task complete). 99 means "confirmed and ready to
execute." The gap between 99 and 100 is the work itself.

### Why are stage checks all-or-nothing?

Partial advancement would let agents skip checks. "3 of 4 checks
passed" is not good enough — the missing check might be
`po_confirmed_plan`, which is the most important one.

### Why are phases separate from stages?

A deliverable in "mvp" phase has many tasks, each going through
stages. Phases control quality standards. Stages control work
protocol. Mixing them would prevent an "mvp" task from being in
"analysis" stage — but that's exactly what happens analyzing a
bug in an MVP feature.

### Why is phases config YAML, not code?

The PO owns phase definitions. The PO changes what "mvp" requires
without modifying Python. YAML is human-editable, version-controlled,
and reloadable at runtime via `reload_phases()`.

### Why doesn't methodology.py import from phases.py?

Stages and phases are intentionally independent. A task can be in
any stage regardless of deliverable phase. Coupling them would
create confusion about whether "readiness 50" means "analysis done"
(stage) or "direction confirmed" (phase checkpoint).

---

## 8. MCP Tool Gating — Enforcement Chain

The methodology system's most impactful integration is stage-gated
tool access in `fleet/mcp/tools.py`:

```python
WORK_ONLY_TOOLS = {"fleet_commit", "fleet_task_complete"}

def _check_stage_allowed(tool_name: str) -> dict | None:
    if tool_name in WORK_ONLY_TOOLS and stage != "work":
        # Emit protocol_violation event
        # Return error to agent
        return {"ok": False, "error": "Methodology violation: ..."}
    return None  # allowed
```

This is REAL enforcement, not just detection. When an agent calls
`fleet_commit` during analysis stage, the tool returns an error.

The enforcement chain:

```
Agent calls fleet_commit during analysis stage
  ↓
_check_stage_allowed() detects violation
  ↓
Event emitted: fleet.methodology.protocol_violation
  ↓
Tool returns error dict to agent (tool call fails)
  ↓
Doctor picks up protocol_violation in next orchestrator cycle
  ↓
Doctor triggers teaching lesson for protocol_violation disease
  ↓
Teaching system injects lesson into agent context via gateway
  ↓
Agent learns (or gets pruned after 3 failures)
```

---

## 9. Data Shapes

### StageTransition Event

```python
{
    "type": "fleet.methodology.stage_changed",
    "source": "fleet/core/methodology",
    "subject": "task-uuid-here",
    "data": {
        "from_stage": "reasoning",
        "to_stage": "work",
        "authorized_by": "po",
        "readiness": 99
    }
}
```

### Phase Definition (from phases.yaml)

```yaml
- name: mvp
  description: "Core functionality usable for real"
  standards:
    tests: "main flows and critical edges"
    docs: "setup, usage, API for public"
    security: "auth, validation, dep audit"
  required_contributions:
    - architect
    - qa-engineer
    - devsecops-expert
  gate: true
```

### StageCheckResult

```python
StageCheckResult(
    stage=Stage.REASONING,
    checks=[
        StageCheck("plan_exists", "...", passed=True),
        StageCheck("plan_references_requirement", "...", passed=True),
        StageCheck("plan_specifies_files", "...", passed=True),
        StageCheck("po_confirmed_plan", "PO confirmed — readiness 99%", passed=False),
    ],
    can_advance=False  # PO hasn't confirmed yet
)
```

---

## 10. What's Needed

### Not Yet Implemented

- **Contribution flow integration:** When task enters REASONING
  with readiness approaching 80, the brain should create parallel
  contribution subtasks (architect design, QA tests, DevSecOps
  requirements). methodology.py defines WHEN but the brain doesn't
  create these subtasks yet.

- **Standards injection:** Phases define required standards per phase
  (e.g., mvp = "auth, validation, dep audit"). These should be
  injected into agent context. Data exists in phases.yaml, not read
  during context assembly.

- **Phase gate enforcement:** Advancing phases requires PO approval.
  `is_phase_gate()` exists but no orchestrator logic enforces it.

- **Stage check automation:** Currently manual. Brain should auto-
  evaluate checks every cycle and advance when all pass.

### Test Coverage

| File | Tests | What's Covered |
|------|-------|---------------|
| `test_methodology.py` | 30+ | Stages, checks, transitions, readiness, task types |
| `test_phases.py` | 15+ | Loading, progression, standards, contributions |
| `test_stage_context.py` | 10+ | Instruction templates, summaries |
| **Total** | **55+** | Core logic fully covered |
