"""Methodology system — stage progression, protocol checks, readiness gate.

The methodology system defines HOW agents work through phases on a task.
Each task has a stage and a readiness percentage (0-100). Stages advance
when their methodology checks pass and the PO confirms.

All stage definitions, readiness boundaries, task-type requirements, and
tool restrictions are loaded from config/methodology.yaml — the single
source of truth. PO can modify that file to add/remove/reorder stages,
change boundaries, or customize per-task-type requirements.

Public API (unchanged — all consumers keep working):
  Stage              — enum of stage names (built from config)
  STAGE_ORDER        — ordered list of Stage values
  DEFAULT_REQUIRED_STAGES — per-task-type required stages
  VALID_READINESS    — discrete readiness values for Plane labels
  get_required_stages(task_type, override) → list[Stage]
  get_initial_stage(task_type, has_verbatim, readiness, override) → Stage
  get_next_stage(current_stage, required_stages) → Stage | None
  suggest_readiness_for_stage(stage) → int
  snap_readiness(value) → int
  StageCheck, StageCheckResult — check data structures
  check_*_stage() — per-stage completion checks
  MethodologyTracker — transition tracking with events
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from fleet.core.methodology_config import get_methodology_config


# ─── Dynamic Stage Enum ───────────────────────────────────────────────
#
# Built from config/methodology.yaml stage names.
# If config has [conversation, analysis, investigation, reasoning, work],
# this produces the same Stage enum as the old hardcoded version.
# If PO adds a stage, it appears here automatically.


def _build_stage_enum() -> type:
    """Build the Stage enum from config."""
    try:
        cfg = get_methodology_config()
        members = {s.name.upper(): s.name for s in cfg.stages}
    except Exception:
        # Fallback if config not found (e.g., during tests without config)
        members = {
            "CONVERSATION": "conversation",
            "ANALYSIS": "analysis",
            "INVESTIGATION": "investigation",
            "REASONING": "reasoning",
            "WORK": "work",
        }
    return Enum("Stage", members, type=str)


Stage = _build_stage_enum()


def _stage(name: str) -> "Stage":
    """Convert a stage name string to a Stage enum value.

    Handles both config-driven and hardcoded scenarios gracefully.
    """
    try:
        return Stage(name)
    except ValueError:
        # Stage name not in enum — might be a custom stage added to config
        # after the enum was built. Return as-is for forward compatibility.
        return name  # type: ignore[return-value]


# ─── Config-Derived Constants ─────────────────────────────────────────
#
# These module-level constants are rebuilt from config on import.
# They exist for backward compatibility with consumers that import them
# directly (e.g., `from fleet.core.methodology import STAGE_ORDER`).


def _build_stage_order() -> list:
    """Build STAGE_ORDER from config."""
    try:
        cfg = get_methodology_config()
        return [_stage(s.name) for s in cfg.stages]
    except Exception:
        return [Stage.CONVERSATION, Stage.ANALYSIS, Stage.INVESTIGATION, Stage.REASONING, Stage.WORK]


def _build_default_required_stages() -> dict:
    """Build DEFAULT_REQUIRED_STAGES from config."""
    try:
        cfg = get_methodology_config()
        result = {}
        for tt_name, tt_def in cfg.task_types.items():
            result[tt_name] = [_stage(s) for s in tt_def.required_stages]
        return result
    except Exception:
        return {
            "epic": [Stage.CONVERSATION, Stage.ANALYSIS, Stage.INVESTIGATION, Stage.REASONING, Stage.WORK],
            "story": [Stage.CONVERSATION, Stage.REASONING, Stage.WORK],
            "task": [Stage.REASONING, Stage.WORK],
            "subtask": [Stage.REASONING, Stage.WORK],
            "bug": [Stage.ANALYSIS, Stage.REASONING, Stage.WORK],
            "spike": [Stage.CONVERSATION, Stage.INVESTIGATION, Stage.REASONING],
            "blocker": [Stage.CONVERSATION, Stage.REASONING, Stage.WORK],
            "request": [Stage.CONVERSATION, Stage.ANALYSIS, Stage.REASONING, Stage.WORK],
            "concern": [Stage.CONVERSATION, Stage.ANALYSIS, Stage.INVESTIGATION],
        }


def _build_valid_readiness() -> list[int]:
    """Build VALID_READINESS from config."""
    try:
        cfg = get_methodology_config()
        return cfg.valid_readiness
    except Exception:
        return [0, 5, 10, 20, 30, 50, 70, 80, 90, 95, 99, 100]


STAGE_ORDER: list = _build_stage_order()
DEFAULT_REQUIRED_STAGES: dict = _build_default_required_stages()
VALID_READINESS: list[int] = _build_valid_readiness()


# ─── Check Data Structures ────────────────────────────────────────────


@dataclass
class StageCheck:
    """A single methodology check for a stage."""
    name: str
    description: str
    passed: bool = False


@dataclass
class StageCheckResult:
    """Result of evaluating all checks for a stage."""
    stage: object  # Stage enum value
    checks: list[StageCheck] = field(default_factory=list)
    can_advance: bool = False

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def total_count(self) -> int:
        return len(self.checks)

    @property
    def all_passed(self) -> bool:
        return all(c.passed for c in self.checks)


# ─── Public API ───────────────────────────────────────────────────────


def get_required_stages(
    task_type: str,
    override: Optional[list[str]] = None,
) -> list:
    """Get the required stages for a task type.

    Args:
        task_type: The task type (epic, story, task, etc.)
        override: Optional explicit stage list (PO or module override)

    Returns:
        Ordered list of stages the task must go through.
    """
    if override:
        return [_stage(s) for s in override]

    try:
        cfg = get_methodology_config()
        ordered = cfg.required_stage_names(task_type)
        return [_stage(s) for s in ordered]
    except Exception:
        return DEFAULT_REQUIRED_STAGES.get(
            task_type,
            [_stage("reasoning"), _stage("work")],
        )


def get_next_stage(
    current_stage: str,
    required_stages: list,
) -> Optional[object]:
    """Get the next stage in the progression.

    Args:
        current_stage: The current stage value.
        required_stages: The stages this task must go through.

    Returns:
        The next required stage, or None if current is the last stage.
    """
    # Normalize to string for comparison
    current_val = current_stage.value if hasattr(current_stage, 'value') else str(current_stage)
    required_vals = [s.value if hasattr(s, 'value') else str(s) for s in required_stages]

    if current_val not in required_vals:
        # Current stage isn't in required list — find first required stage
        # that comes after current in the global order
        try:
            cfg = get_methodology_config()
            stage_names = cfg.stage_names()
        except Exception:
            stage_names = [s.value if hasattr(s, 'value') else str(s) for s in STAGE_ORDER]

        current_idx = stage_names.index(current_val) if current_val in stage_names else -1
        for rv in required_vals:
            rv_idx = stage_names.index(rv) if rv in stage_names else -1
            if rv_idx > current_idx:
                return _stage(rv)
        return None

    idx = required_vals.index(current_val)
    if idx + 1 < len(required_vals):
        return _stage(required_vals[idx + 1])
    return None


def get_initial_stage(
    task_type: str,
    has_verbatim_requirement: bool = False,
    readiness: int = 0,
    override: Optional[list[str]] = None,
) -> object:
    """Determine the initial stage for a task.

    Logic (config-driven):
    1. Get required stages for this task_type
    2. If no metadata at all (no type, readiness=0, no verbatim),
       return defaults.no_metadata_stage
    3. If verbatim exists, check verbatim_skip rules (highest threshold first)
       — skip to the target stage if readiness >= threshold
    4. Otherwise, map readiness to a stage via readiness_range,
       then find the nearest required stage at or before that position

    Args:
        task_type: The task type (epic, story, task, etc.)
        has_verbatim_requirement: Whether requirement_verbatim is populated
        readiness: Task readiness percentage (0-100)
        override: Optional explicit stage list
    """
    required = get_required_stages(task_type, override)
    if not required:
        return _stage("reasoning")

    try:
        cfg = get_methodology_config()
    except Exception:
        # Config unavailable — use simple fallback
        return required[0]

    required_names = [s.value if hasattr(s, 'value') else str(s) for s in required]
    stage_names = cfg.stage_names()

    # Case 1: Zero metadata — under-specified task.
    # Override to no_metadata_stage regardless of required stages.
    # An under-specified task NEEDS conversation even if the default
    # task type doesn't list it — the PO hasn't written requirements yet.
    if readiness == 0 and not has_verbatim_requirement and not task_type:
        return _stage(cfg.no_metadata_stage)

    # Case 2: Verbatim exists — check skip rules
    if has_verbatim_requirement:
        for rule in cfg.verbatim_skip:  # sorted highest threshold first
            if readiness >= rule.threshold:
                target = rule.target_stage
                if target in required_names:
                    return _stage(target)
                # Target not in required stages — find nearest required
                # stage at or after the target in stage order
                target_idx = stage_names.index(target) if target in stage_names else -1
                for rn in required_names:
                    rn_idx = stage_names.index(rn) if rn in stage_names else -1
                    if rn_idx >= target_idx:
                        return _stage(rn)
                # No required stage at or after target — use last required
                return required[-1]

    # Case 3: Map readiness to stage via readiness_range
    readiness_stage = cfg.stage_for_readiness(readiness)
    if readiness_stage:
        target_name = readiness_stage.name
        # Find the required stage at or before this position
        target_idx = stage_names.index(target_name) if target_name in stage_names else 0

        # Walk backward from target to find the latest required stage
        # that's at or before the readiness-mapped stage
        best = None
        for rn in required_names:
            rn_idx = stage_names.index(rn) if rn in stage_names else -1
            if rn_idx <= target_idx:
                best = rn
        if best:
            return _stage(best)

    # Default: first required stage
    return required[0]


def suggest_readiness_for_stage(stage) -> int:
    """Suggest a readiness percentage based on the current stage.

    These are suggestions, not rules. The PO sets the actual value.
    """
    stage_name = stage.value if hasattr(stage, 'value') else str(stage)
    try:
        cfg = get_methodology_config()
        s = cfg.stage_by_name(stage_name)
        if s:
            return s.suggested_readiness
    except Exception:
        pass
    # Fallback
    fallback = {"conversation": 10, "analysis": 30, "investigation": 50, "reasoning": 80, "work": 99}
    return fallback.get(stage_name, 0)


def snap_readiness(value: int) -> int:
    """Snap a readiness value to the nearest valid value."""
    try:
        cfg = get_methodology_config()
        valid = cfg.valid_readiness
    except Exception:
        valid = VALID_READINESS
    return min(valid, key=lambda v: abs(v - value))


# ─── Stage checks ────────────────────────────────────────────────────
#
# These check functions are stage-specific completion criteria.
# They remain here because they contain business logic, not config data.
# The config tells you WHAT stages exist and WHEN to enter them.
# These checks tell you WHEN a stage is COMPLETE (can advance).


def check_conversation_stage(
    has_verbatim_requirement: bool,
    has_po_response: bool,
    open_questions: int = 0,
) -> StageCheckResult:
    """Check if conversation stage is complete."""
    checks = [
        StageCheck(
            "verbatim_requirement_exists",
            "PO's verbatim requirement is populated on the task",
            passed=has_verbatim_requirement,
        ),
        StageCheck(
            "po_responded",
            "PO has responded to agent questions",
            passed=has_po_response,
        ),
        StageCheck(
            "no_open_questions",
            "No unresolved questions from agent to PO",
            passed=open_questions == 0,
        ),
    ]
    result = StageCheckResult(stage=_stage("conversation"), checks=checks)
    result.can_advance = result.all_passed
    return result


def check_analysis_stage(
    has_analysis_document: bool,
    po_reviewed: bool,
) -> StageCheckResult:
    """Check if analysis stage is complete."""
    checks = [
        StageCheck(
            "analysis_document_exists",
            "Agent produced an analysis document",
            passed=has_analysis_document,
        ),
        StageCheck(
            "po_reviewed_analysis",
            "PO reviewed the analysis findings",
            passed=po_reviewed,
        ),
    ]
    result = StageCheckResult(stage=_stage("analysis"), checks=checks)
    result.can_advance = result.all_passed
    return result


def check_investigation_stage(
    has_research_document: bool,
    multiple_options_explored: bool,
    po_reviewed: bool,
) -> StageCheckResult:
    """Check if investigation stage is complete."""
    checks = [
        StageCheck(
            "research_document_exists",
            "Agent produced a research/investigation document",
            passed=has_research_document,
        ),
        StageCheck(
            "multiple_options",
            "Multiple options or approaches explored (not just one)",
            passed=multiple_options_explored,
        ),
        StageCheck(
            "po_reviewed_investigation",
            "PO reviewed the investigation findings",
            passed=po_reviewed,
        ),
    ]
    result = StageCheckResult(stage=_stage("investigation"), checks=checks)
    result.can_advance = result.all_passed
    return result


def check_reasoning_stage(
    has_plan: bool,
    plan_references_verbatim: bool,
    plan_specifies_files: bool,
    po_confirmed_plan: bool,
) -> StageCheckResult:
    """Check if reasoning stage is complete."""
    checks = [
        StageCheck(
            "plan_exists",
            "Agent produced an implementation plan",
            passed=has_plan,
        ),
        StageCheck(
            "plan_references_requirement",
            "Plan explicitly references the verbatim requirement",
            passed=plan_references_verbatim,
        ),
        StageCheck(
            "plan_specifies_files",
            "Plan specifies target files/components",
            passed=plan_specifies_files,
        ),
        StageCheck(
            "po_confirmed_plan",
            "PO confirmed the plan — readiness at 99-100%",
            passed=po_confirmed_plan,
        ),
    ]
    result = StageCheckResult(stage=_stage("reasoning"), checks=checks)
    result.can_advance = result.all_passed
    return result


def check_work_stage(
    readiness: int,
    has_commits: bool,
    has_pr: bool,
    acceptance_criteria_met: bool,
    required_tools_called: bool,
) -> StageCheckResult:
    """Check if work stage is complete (task can move to review)."""
    checks = [
        StageCheck(
            "readiness_threshold",
            "Task readiness at 99-100%",
            passed=readiness >= 99,
        ),
        StageCheck(
            "has_commits",
            "Agent committed code (for code tasks)",
            passed=has_commits,
        ),
        StageCheck(
            "has_pr",
            "Pull request created",
            passed=has_pr,
        ),
        StageCheck(
            "acceptance_criteria_met",
            "All acceptance criteria addressed",
            passed=acceptance_criteria_met,
        ),
        StageCheck(
            "required_tools_called",
            "All required MCP tools called for this task type",
            passed=required_tools_called,
        ),
    ]
    result = StageCheckResult(stage=_stage("work"), checks=checks)
    result.can_advance = result.all_passed
    return result


# ─── Stage Transition Tracking (B07: Observability) ───────────────────


@dataclass
class StageTransition:
    """Record of a stage transition on a task."""
    task_id: str
    from_stage: str
    to_stage: str
    authorized_by: str  # "po", "pm", "agent:{name}", "system"
    readiness_before: int = 0
    readiness_after: int = 0
    checks_passed: int = 0
    checks_total: int = 0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            from datetime import datetime
            self.timestamp = datetime.now().isoformat()


class MethodologyTracker:
    """Tracks methodology stage transitions and compliance.

    Records every stage change, who authorized it, what checks passed.
    Feeds observability for the PO and the immune system.
    """

    def __init__(self) -> None:
        self._transitions: list[StageTransition] = []

    def record_transition(
        self,
        task_id: str,
        from_stage: str,
        to_stage: str,
        authorized_by: str,
        readiness_before: int = 0,
        readiness_after: int = 0,
        check_result: Optional[StageCheckResult] = None,
    ) -> StageTransition:
        """Record a stage transition."""
        transition = StageTransition(
            task_id=task_id,
            from_stage=from_stage,
            to_stage=to_stage,
            authorized_by=authorized_by,
            readiness_before=readiness_before,
            readiness_after=readiness_after,
            checks_passed=check_result.passed_count if check_result else 0,
            checks_total=check_result.total_count if check_result else 0,
        )
        self._transitions.append(transition)
        self._emit_event(transition)
        return transition

    def get_task_history(self, task_id: str) -> list[StageTransition]:
        """Get all stage transitions for a task."""
        return [t for t in self._transitions if t.task_id == task_id]

    def get_recent_transitions(self, limit: int = 20) -> list[StageTransition]:
        """Get most recent transitions across all tasks."""
        return self._transitions[-limit:]

    @property
    def total_transitions(self) -> int:
        return len(self._transitions)

    def _emit_event(self, transition: StageTransition) -> None:
        """Emit a methodology event for the transition."""
        try:
            from fleet.core.events import create_event, EventStore
            store = EventStore()
            event = create_event(
                event_type="fleet.methodology.stage_changed",
                source="fleet/core/methodology",
                subject=transition.task_id,
                from_stage=transition.from_stage,
                to_stage=transition.to_stage,
                authorized_by=transition.authorized_by,
                readiness=transition.readiness_after,
            )
            store.append(event)
        except Exception:
            pass  # Event emission must never break methodology
