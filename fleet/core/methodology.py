"""Methodology system — stage progression, protocol checks, readiness gate.

The methodology system defines HOW agents work through phases on a task.
Each task has a stage (conversation, analysis, investigation, reasoning, work)
and a readiness percentage (0-100). Stages advance when their methodology
checks pass and the PO confirms.

Work protocol is only entered at readiness 99-100%.

Stages are not always linear — different task types skip stages they
don't need. An epic goes through every stage. A simple bug fix might
skip straight to reasoning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Stage(str, Enum):
    """Methodology stages — protocols an agent follows."""
    CONVERSATION = "conversation"
    ANALYSIS = "analysis"
    INVESTIGATION = "investigation"
    REASONING = "reasoning"
    WORK = "work"


# Ordered progression — stages advance in this order (when not skipped)
STAGE_ORDER: list[Stage] = [
    Stage.CONVERSATION,
    Stage.ANALYSIS,
    Stage.INVESTIGATION,
    Stage.REASONING,
    Stage.WORK,
]

# ─── Default stage requirements per task type ────────────────────────────

# Which stages are required for each task type. PO or module can override.

DEFAULT_REQUIRED_STAGES: dict[str, list[Stage]] = {
    "epic": [
        Stage.CONVERSATION,
        Stage.ANALYSIS,
        Stage.INVESTIGATION,
        Stage.REASONING,
        Stage.WORK,
    ],
    "story": [
        Stage.CONVERSATION,
        Stage.REASONING,
        Stage.WORK,
    ],
    "task": [
        Stage.REASONING,
        Stage.WORK,
    ],
    "subtask": [
        Stage.REASONING,
        Stage.WORK,
    ],
    "bug": [
        Stage.ANALYSIS,
        Stage.REASONING,
        Stage.WORK,
    ],
    "spike": [
        Stage.CONVERSATION,
        Stage.INVESTIGATION,
        Stage.REASONING,
    ],
    "blocker": [
        Stage.CONVERSATION,
        Stage.REASONING,
        Stage.WORK,
    ],
    "request": [
        Stage.CONVERSATION,
        Stage.ANALYSIS,
        Stage.REASONING,
        Stage.WORK,
    ],
    "concern": [
        Stage.CONVERSATION,
        Stage.ANALYSIS,
        Stage.INVESTIGATION,
    ],
}


@dataclass
class StageCheck:
    """A single methodology check for a stage."""
    name: str
    description: str
    passed: bool = False


@dataclass
class StageCheckResult:
    """Result of evaluating all checks for a stage."""
    stage: Stage
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


def get_required_stages(
    task_type: str,
    override: Optional[list[str]] = None,
) -> list[Stage]:
    """Get the required stages for a task type.

    Args:
        task_type: The task type (epic, story, task, etc.)
        override: Optional explicit stage list (PO or module override)

    Returns:
        Ordered list of stages the task must go through.
    """
    if override:
        return [Stage(s) for s in override if s in Stage.__members__.values()]

    return DEFAULT_REQUIRED_STAGES.get(
        task_type,
        [Stage.REASONING, Stage.WORK],  # default: reason then work
    )


def get_next_stage(
    current_stage: str,
    required_stages: list[Stage],
) -> Optional[Stage]:
    """Get the next stage in the progression.

    Args:
        current_stage: The current stage value.
        required_stages: The stages this task must go through.

    Returns:
        The next required stage, or None if current is the last stage.
    """
    try:
        current = Stage(current_stage)
    except ValueError:
        return required_stages[0] if required_stages else None

    if current not in required_stages:
        # Current stage isn't in required list — find first required stage
        # that comes after current in the global order
        current_idx = STAGE_ORDER.index(current) if current in STAGE_ORDER else -1
        for stage in required_stages:
            if STAGE_ORDER.index(stage) > current_idx:
                return stage
        return None

    idx = required_stages.index(current)
    if idx + 1 < len(required_stages):
        return required_stages[idx + 1]
    return None


def get_initial_stage(
    task_type: str,
    has_verbatim_requirement: bool = False,
    readiness: int = 0,
    override: Optional[list[str]] = None,
) -> Stage:
    """Determine the initial stage for a new task.

    A task with clear verbatim requirements and higher readiness may
    start at a later stage. A task with nothing starts at the first
    required stage.
    """
    required = get_required_stages(task_type, override)
    if not required:
        return Stage.REASONING

    # If readiness is already high and verbatim exists, start later
    if readiness >= 90 and has_verbatim_requirement:
        # Skip to reasoning or work
        if Stage.WORK in required and readiness >= 99:
            return Stage.WORK
        if Stage.REASONING in required:
            return Stage.REASONING

    if readiness >= 50 and has_verbatim_requirement:
        # Skip conversation, start at analysis or investigation
        for stage in required:
            if stage != Stage.CONVERSATION:
                return stage

    return required[0]


# ─── Stage checks ──────────────────────────────────────────────────────


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
    result = StageCheckResult(stage=Stage.CONVERSATION, checks=checks)
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
    result = StageCheckResult(stage=Stage.ANALYSIS, checks=checks)
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
    result = StageCheckResult(stage=Stage.INVESTIGATION, checks=checks)
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
    result = StageCheckResult(stage=Stage.REASONING, checks=checks)
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
    result = StageCheckResult(stage=Stage.WORK, checks=checks)
    result.can_advance = result.all_passed
    return result


# ─── Readiness suggestion ──────────────────────────────────────────────

# Valid readiness values (matching Plane labels)
VALID_READINESS = [0, 5, 10, 20, 30, 50, 70, 80, 90, 95, 99, 100]


def suggest_readiness_for_stage(stage: Stage) -> int:
    """Suggest a readiness percentage based on the current stage.

    These are suggestions, not rules. The PO sets the actual value.
    Strategic checkpoints at 0, 50, 90.
    """
    suggestions = {
        Stage.CONVERSATION: 10,
        Stage.ANALYSIS: 30,
        Stage.INVESTIGATION: 50,
        Stage.REASONING: 80,
        Stage.WORK: 99,
    }
    return suggestions.get(stage, 0)


def snap_readiness(value: int) -> int:
    """Snap a readiness value to the nearest valid value."""
    return min(VALID_READINESS, key=lambda v: abs(v - value))