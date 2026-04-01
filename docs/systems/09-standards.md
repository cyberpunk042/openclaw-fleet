# Standards Library — What "Done Right" Looks Like

> **4 files. 739 lines. Defines quality for every artifact type, plan, PR, and tool usage.**
>
> The standards library defines what complete and correct looks like
> for every artifact an agent produces: tasks, bugs, analysis documents,
> investigation documents, plans, PRs, completion claims. Each standard
> has required fields, quality criteria, and examples. Compliance is
> checked by the artifact tracker and feeds the immune system.
> Plan quality is assessed at fleet_task_accept. PR hygiene is monitored
> for conflicts, stale PRs, and orphans. Tool enforcement ensures agents
> use the right MCP tools for their task type.

---

## 1. Why It Exists

Without standards:
- An agent calls a task "done" with 3 of 5 acceptance criteria met
- A plan says "I'll work on it" without specifying files or steps
- A PR has no description, no tests, no task reference
- An analysis document references "the codebase" without specific files
- A completion claim has no evidence that acceptance criteria were met

Standards make quality MEASURABLE. Each artifact type has a checklist
of required fields. If fields are missing, the artifact is incomplete.
Completeness feeds readiness. Readiness gates work stage entry.

```
Agent produces artifact
  ↓
Artifact tracker checks against standard
  ↓
ArtifactCompleteness: required_pct, missing_required
  ↓
suggested_readiness maps completeness to valid readiness value
  ↓
If not complete: readiness stays below 99 → work stage BLOCKED
  ↓
If complete + PO confirms: readiness 99 → work stage unlocked
```

---

## 2. How It Works

### 2.1 Artifact Standards — The Quality Definition

7 artifact types with registered standards:

```
┌──────────────────────────────────────────────────────────────┐
│                   ARTIFACT STANDARDS                         │
│                                                              │
│  task ──────────── title, verbatim, description, criteria,   │
│                    type, stage, readiness, priority, project  │
│                                                              │
│  bug ───────────── title, steps_to_reproduce, expected,      │
│                    actual, environment, impact                │
│                                                              │
│  analysis_document title, scope, current_state, findings,    │
│                    implications                               │
│                                                              │
│  investigation_doc title, scope, findings, options,          │
│                    recommendations                           │
│                                                              │
│  plan ──────────── title, requirement_reference, approach,   │
│                    target_files, steps, criteria_mapping      │
│                                                              │
│  pull_request ──── title, description, changes, testing,     │
│                    task_reference                             │
│                                                              │
│  completion_claim  pr_url, summary, criteria_check,          │
│                    files_changed                              │
└──────────────────────────────────────────────────────────────┘
```

Each standard has:
- **Required fields** — must be present (blocking)
- **Optional fields** — recommended but not blocking
- **Quality criteria** — qualitative checks (not automated)
- **Positive/negative examples** — what good/bad looks like

### 2.2 Compliance Checking

```python
result = check_standard("plan", {
    "title": True,
    "requirement_reference": True,
    "approach": True,
    "target_files": True,
    "steps": False,            # ← MISSING
    "acceptance_criteria_mapping": False,  # ← MISSING
})

# result.missing_fields = ["steps", "acceptance_criteria_mapping"]
# result.compliant = False
# result.score = 70  (100 - 2 × 15)
```

Score: starts at 100, each missing required field deducts 15 points.

### 2.3 Plan Quality Assessment

When agents call `fleet_task_accept(plan="...")`, the plan is
assessed across 3 dimensions:

```
Plan quality score (0-100):

  Steps (40 pts)     — concrete steps found? (first, then, next, will create...)
    ≥3 indicators    → 40 pts
    ≥1 indicator     → 20 pts
    0 indicators     → 0 pts + issue

  Verification (30 pts) — how will you know it works? (test, verify, check...)
    ≥2 indicators    → 30 pts
    ≥1 indicator     → 15 pts
    0 indicators     → 0 pts + issue (except subtasks)

  Risks (20 pts)     — what could go wrong? (risk, concern, might, depends on...)
    ≥1 indicator     → 20 pts
    0 indicators     → suggestion (for epic/story/blocker)

  Length (10 pts)     — sufficient detail?
    ≥50 words        → 10 pts
    ≥20 words        → 5 pts
    <20 words        → 0 pts

  Threshold: score ≥ 40 = acceptable, ≥ 70 = good
```

### 2.4 PR Hygiene

Monitors open PRs for 5 issue types:

| Issue | Severity | Action |
|-------|----------|--------|
| Conflicting (merge conflict) | High | Create resolve-conflict task for agent |
| Stale (task already done) | Medium | Close PR |
| Duplicate (multiple for same task) | Medium | Keep newest, close older |
| Orphaned (no linked task) | Low | Create task or close |
| Long-open (>48h no activity) | Low | Alert |

### 2.5 Tool Enforcement

Per task type, required MCP tools:

```
task:     fleet_read_context ✓, fleet_task_accept ✓,
          fleet_commit ✓, fleet_task_complete ✓,
          fleet_task_progress (recommended)

story:    fleet_read_context ✓, fleet_task_accept ✓,
          fleet_task_create ✓ (stories SHOULD create subtasks),
          fleet_commit ✓, fleet_task_complete ✓,
          fleet_task_progress ✓ (stories are long — required)

epic:     fleet_read_context ✓, fleet_agent_status ✓,
          fleet_task_create ✓ (epics MUST produce subtasks),
          fleet_task_accept ✓

blocker:  fleet_read_context ✓, fleet_task_accept ✓,
          fleet_task_complete ✓, fleet_alert (recommended)
```

Missing required tools lower the confidence score in the approval.
Fleet-ops considers this during review.

---

## 3. File Map

```
fleet/core/
├── standards.py          7 artifact type standards, compliance checker  (264 lines)
├── plan_quality.py       Plan assessment (steps, verification, risks)   (139 lines)
├── pr_hygiene.py         PR issue detection (5 types)                   (209 lines)
└── skill_enforcement.py  Required tools per task type                   (127 lines)
```

Total: **739 lines** across 4 modules.

---

## 4. Per-File Documentation

### 4.1 `standards.py` — Artifact Standards (264 lines)

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `RequiredField` | 19-23 | A field that must be present: name, description, required bool. |
| `Standard` | 27-34 | Artifact type standard: artifact_type, description, required_fields, quality_criteria, positive_example, negative_example. |
| `ComplianceResult` | 38-55 | Check result: missing_fields, failed_criteria. Properties: compliant (nothing missing), score (0-100, -15 per missing). |

#### Registered Standards (7)

| Type | Required Fields | Quality Criteria |
|------|----------------|-----------------|
| `task` | title, verbatim, description, criteria, type, stage, readiness, priority, project (+ optional: agent, SP) | Actionable title, verbatim populated, criteria checkable, deps linked |
| `bug` | title, steps_to_reproduce, expected, actual, environment, impact (+ optional: evidence) | Specific title, numbered steps, error messages verbatim |
| `analysis_document` | title, scope, current_state, findings, implications (+ optional: open_questions) | Specific files/lines, concrete findings, scope stated |
| `investigation_document` | title, scope, findings (+ optional: options, recommendations, open_questions) | Multiple options, sources cited, tradeoffs stated |
| `plan` | title, requirement_reference, approach, target_files, steps, criteria_mapping (+ optional: risks) | References verbatim, specific paths, ordered steps, criteria mapped |
| `pull_request` | title, description, changes, testing, task_reference (+ optional: commits) | Conventional format, WHY not WHAT, test results, task ID |
| `completion_claim` | pr_url, summary, criteria_check, files_changed | Every criterion evidenced, PR valid, summary matches requirement |

#### Functions

| Function | Lines | What It Does |
|----------|-------|-------------|
| `get_standard(type)` | 232-234 | Get standard for artifact type. |
| `list_standards()` | 237-239 | List all registered standards. |
| `check_standard(type, present_fields)` | 242-264 | Check artifact against standard. Returns ComplianceResult with missing fields and score. |

### 4.2 `plan_quality.py` — Plan Assessment (139 lines)

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `PlanAssessment` | 18-32 | Score (0-100), issues list, suggestions list. Properties: acceptable (≥40), good (≥70). |

#### Constants

| Name | Count | Purpose |
|------|-------|---------|
| `STEP_INDICATORS` | 13 | Keywords indicating concrete steps ("step", "first", "then", "will create"...) |
| `VERIFY_INDICATORS` | 10 | Keywords indicating verification ("test", "verify", "check", "validate"...) |
| `RISK_INDICATORS` | 11 | Keywords indicating risk awareness ("risk", "concern", "might", "depends on"...) |

#### Functions

| Function | Lines | What It Does |
|----------|-------|-------------|
| `assess_plan(text, task_type)` | 54-116 | Assess plan across 4 dimensions: steps (40pts), verification (30pts), risks (20pts), length (10pts). Returns PlanAssessment. |
| `format_plan_feedback(assessment)` | 119-139 | Format as feedback text: score, issues, suggestions, verdict. |

### 4.3 `pr_hygiene.py` — PR Health (209 lines)

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `PRIssue` | 28-40 | Detected issue: type, severity, pr_url, task reference, description, recommended_action, target_agent. |
| `PRHygieneReport` | 43-55 | Full report: issues list, total_open_prs, conflicting count, stale count. |

#### Functions

| Function | Lines | What It Does |
|----------|-------|-------------|
| `assess_pr_hygiene(tasks, open_prs, now)` | 57-209 | Check all open PRs against board tasks. Detect: conflicting, stale, duplicate, orphaned, long-open. Returns report with recommended actions. |

### 4.4 `skill_enforcement.py` — Tool Requirements (127 lines)

#### Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `ToolRequirement` | 19-24 | Required tool: tool_name, required bool, reason. |

#### Constants

| Name | Type | Purpose |
|------|------|---------|
| `TASK_TYPE_REQUIREMENTS` | dict[str, list[ToolRequirement]] | Required/recommended tools per task type (task, subtask, story, epic, blocker). |

#### Functions

| Function | Lines | What It Does |
|----------|-------|-------------|
| `check_compliance(task_type, tools_called)` | — | Check if agent called all required tools for this task type. Returns missing tools + confidence impact. |

---

## 5. Dependency Graph

```
standards.py          ← standalone (dataclasses only)
    ↑
plan_quality.py       ← standalone (dataclasses only)

pr_hygiene.py         ← imports Task, TaskStatus from models

skill_enforcement.py  ← standalone (dataclasses only)
```

No circular dependencies. All 4 modules are independent.
Each consumed by different parts of the system.

---

## 6. Consumers

| Layer | Module | What It Imports | How It Uses It |
|-------|--------|----------------|---------------|
| **Artifact Tracker** | `artifact_tracker.py` | `get_standard, check_standard, Standard` | Checks artifact completeness against standard → readiness suggestion |
| **MCP Tools** | `tools.py` | `assess_plan, format_plan_feedback` | fleet_task_accept assesses plan quality → returns feedback |
| **MCP Tools** | `tools.py` | `check_compliance` from skill_enforcement | fleet_task_complete checks required tools called → confidence score |
| **Sync CLI** | `sync.py` | `assess_pr_hygiene` | PR hygiene check during sync cycle |
| **Doctor** | — (indirect) | — | Standards compliance feeds laziness detection (partial criteria met) |

---

## 7. Design Decisions

### Why register standards in code, not config?

Standards need quality_criteria (qualitative descriptions) and examples
(multi-line text). YAML can hold these but editing becomes unwieldy.
Python code with `_register(Standard(...))` is cleaner, version-controlled,
and supports defaults. The PO changes standards by modifying Python —
which is appropriate since standards are engineering decisions.

### Why keyword-based plan assessment, not LLM?

Plan assessment runs on EVERY fleet_task_accept call. LLM-based
assessment would cost tokens, add latency, and could be gamed.
Keyword heuristics are instant, free, and catch the most common
failure: vague plans like "I'll fix it" with no steps, no verification.

### Why -15 per missing field?

The score must be severe enough that 2-3 missing required fields
make the artifact clearly incomplete (30-55 score), but not so
severe that 1 missing optional field fails it. -15 per required
field means: 1 missing = 85 (acceptable), 2 missing = 70 (borderline),
3 missing = 55 (needs work), 5+ = unusable.

### Why separate plan_quality from standards?

Plans are assessed at accept time (fleet_task_accept) with text
analysis. Artifact standards are checked at completeness time
(artifact_tracker) with field presence. Different timing, different
input format, different consumers.

### Why PR hygiene as a separate module?

PR issues are detected from GitHub state, not OCMC state. The PR
hygiene module bridges GitHub (PR data) and OCMC (task data). It
runs during sync, not during orchestrator cycle. Different cadence,
different data sources.

---

## 8. Standard → Readiness Pipeline

```
Agent creates artifact (analysis_document)
  ↓
fleet_artifact_create() initializes with standard's fields
  ↓
Agent updates artifact fields one by one
  fleet_artifact_update("findings", append=True, ...)
  ↓
After each update:
  artifact_tracker.check_artifact_completeness()
    ↓
  ArtifactCompleteness:
    required_pct: 60%    (3/5 required fields filled)
    missing_required: ["implications", "open_questions"]
    suggested_readiness: 50
  ↓
Agent continues filling fields across cycles
  ↓
Eventually: required_pct = 100%, suggested_readiness = 90
  ↓
PO reviews and confirms → readiness = 99 → work unlocked
```

---

## 9. Data Shapes

### Standard (registered)

```python
Standard(
    artifact_type="plan",
    description="Implementation plan — what will be done and how",
    required_fields=[
        RequiredField("title", "What's being planned."),
        RequiredField("requirement_reference", "Verbatim requirement quoted."),
        RequiredField("approach", "What will be done. Specific files."),
        RequiredField("target_files", "Which files will be modified."),
        RequiredField("steps", "Ordered implementation steps."),
        RequiredField("acceptance_criteria_mapping", "How each criterion met."),
        RequiredField("risks", "What could go wrong.", required=False),
    ],
    quality_criteria=[
        "Plan explicitly references the verbatim requirement",
        "Target files are specific paths, not categories",
        "Steps are ordered and each is actionable",
        "Acceptance criteria mapped to specific steps",
    ],
)
```

### ComplianceResult

```python
ComplianceResult(
    artifact_type="plan",
    missing_fields=["steps", "acceptance_criteria_mapping"],
    failed_criteria=[],
    # compliant = False
    # score = 70  (100 - 2 × 15)
)
```

### PlanAssessment

```python
PlanAssessment(
    score=65.0,
    issues=["No verification approach. How will you know it works?"],
    suggestions=["Consider what could go wrong"],
    # acceptable = True (≥40)
    # good = False (<70)
)
```

### PRIssue

```python
PRIssue(
    issue_type="conflicting",
    severity="high",
    pr_url="https://github.com/org/repo/pull/42",
    pr_number=42,
    pr_title="feat(auth): add token validation",
    task_id="abc123",
    task_status="in_progress",
    description="PR has merge conflicts",
    recommended_action="Create resolve-conflict task for software-engineer",
    target_agent="software-engineer",
)
```

---

## 10. What's Needed

### Not Yet Implemented

- **Standards injection into agent context (AR-14):** Standards exist
  but are not injected into agent heartbeat context based on current
  task artifact type. Agent doesn't see "your plan needs these fields"
  unless they call fleet_artifact_create.

- **Phase-dependent quality bars:** Phases define standards
  (poc = basic, production = comprehensive) but the standards library
  doesn't vary by phase. All artifacts get the same standard regardless
  of deliverable maturity.

- **More artifact types:** Missing standards for: security_assessment,
  deployment_manifest, compliance_report, ux_spec, qa_test_definition,
  documentation_outline. These are contribution types that don't have
  quality definitions yet.

- **Quality criteria automation:** Currently quality_criteria are
  human-readable descriptions, not automated checks. E.g., "Title is
  an action, not a goal" — this could be keyword-checked.

### Test Coverage

| File | Tests | Coverage |
|------|-------|---------|
| `test_standards.py` | 15+ | Standard registration, compliance checking, scoring |
| `test_plan_quality.py` | 15+ | Plan assessment, keyword detection, scoring |
| `test_pr_hygiene.py` | 10+ | PR issue detection, stale/conflicting/orphaned |
| `test_skill_enforcement.py` | 10+ | Tool requirements per task type |
| **Total** | **50+** | Core logic covered. Missing: phase-dependent standards |
