"""Methodology config loader — reads config/methodology.yaml.

Single source of truth for methodology stages. All methodology functions
read from this cached config instead of hardcoded constants.

The config is loaded once on first access and cached. Call reload() to
pick up changes (e.g., after PO edits the file).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass(frozen=True)
class StageDefinition:
    """A single methodology stage from config."""

    name: str
    readiness_min: int          # inclusive
    readiness_max: int          # exclusive
    description: str
    summary: str
    suggested_readiness: int
    tools_blocked: tuple[str, ...]
    protocol: str
    order: int                  # position in the stages list (0-based)


@dataclass(frozen=True)
class TaskTypeDefinition:
    """Required stages for a task type."""

    name: str
    required_stages: tuple[str, ...]


@dataclass(frozen=True)
class VerbatimSkipRule:
    """A readiness threshold that allows skipping stages when verbatim exists."""

    threshold: int
    target_stage: str


@dataclass(frozen=True)
class MethodologyModel:
    """A named methodology model — a distinct work process."""

    name: str
    description: str = ""
    stages: tuple[str, ...] = ()
    completion_tool: str = "fleet_task_complete"
    gates: str = "po"  # po, none
    protocol_adaptations: dict[str, str] = field(default_factory=dict)
    readiness_cap: int = 100


@dataclass(frozen=True)
class ModelSelectionRule:
    """A rule for selecting which methodology model to use."""

    condition: str
    model: str


def _evaluate_condition(condition: str, fields: dict) -> bool:
    """Evaluate a condition string against task fields.

    Splits on AND — all clauses must match.
    """
    clauses = [c.strip() for c in condition.split(" AND ")]
    return all(_evaluate_clause(c, fields) for c in clauses)


def _evaluate_clause(clause: str, fields: dict) -> bool:
    """Evaluate a single clause against task fields.

    Supports:
      ``field is set``       — truthy check
      ``field >= N``         — numeric comparison
      ``field in [a, b]``    — membership
      ``field = value``      — equality
    """
    # "field is set"
    if " is set" in clause:
        field_name = clause.replace(" is set", "").strip()
        return bool(fields.get(field_name, ""))

    # "field >= N"
    if " >= " in clause:
        field_name, value_str = clause.split(">=", 1)
        field_name = field_name.strip()
        try:
            threshold = int(value_str.strip())
        except ValueError:
            return False
        actual = fields.get(field_name, 0)
        try:
            return int(actual) >= threshold
        except (ValueError, TypeError):
            return False

    # "field in [a, b, c]"
    if " in [" in clause:
        field_name = clause.split(" in ")[0].strip()
        bracket = clause.split("[")[1].rstrip("]")
        values = [v.strip() for v in bracket.split(",")]
        return fields.get(field_name, "") in values

    # "field = value"
    if " = " in clause:
        field_name, value = clause.split("=", 1)
        field_name = field_name.strip()
        value = value.strip()
        return str(fields.get(field_name, "")) == value

    return False


@dataclass
class MethodologyConfig:
    """Parsed methodology configuration."""

    stages: list[StageDefinition] = field(default_factory=list)
    task_types: dict[str, TaskTypeDefinition] = field(default_factory=dict)
    no_type_stages: tuple[str, ...] = ("reasoning", "work")
    no_metadata_stage: str = "conversation"
    sprint_ready_threshold: int = 80
    verbatim_skip: list[VerbatimSkipRule] = field(default_factory=list)
    valid_readiness: list[int] = field(default_factory=lambda: [0, 5, 10, 20, 30, 50, 70, 80, 90, 95, 99, 100])
    models: dict[str, MethodologyModel] = field(default_factory=dict)
    model_selection: list[ModelSelectionRule] = field(default_factory=list)

    # ── Lookup helpers ─────────────────────────────────────────

    def stage_by_name(self, name: str) -> Optional[StageDefinition]:
        """Get a stage definition by name."""
        for s in self.stages:
            if s.name == name:
                return s
        return None

    def stage_names(self) -> list[str]:
        """Ordered list of stage names."""
        return [s.name for s in self.stages]

    def stage_for_readiness(self, readiness: int) -> Optional[StageDefinition]:
        """Find which stage a readiness value falls into.

        Uses readiness_range [min, max) — inclusive min, exclusive max.
        """
        for s in self.stages:
            if s.readiness_min <= readiness < s.readiness_max:
                return s
        # Edge case: readiness exactly at last stage's max (e.g., 100)
        # → return the last stage
        if self.stages and readiness >= self.stages[-1].readiness_min:
            return self.stages[-1]
        return None

    def required_stage_names(self, task_type: str) -> list[str]:
        """Get required stage names for a task type, in stage order."""
        tt = self.task_types.get(task_type)
        required = list(tt.required_stages) if tt else list(self.no_type_stages)
        # Return in stage definition order, not task_type list order
        ordered = [s.name for s in self.stages if s.name in required]
        return ordered

    def is_tool_blocked(self, stage_name: str, tool_name: str) -> bool:
        """Check if a tool is blocked in a given stage."""
        stage = self.stage_by_name(stage_name)
        if not stage:
            return False  # unknown stage → allow (backward compatible)
        return tool_name in stage.tools_blocked

    def get_model(self, name: str) -> Optional[MethodologyModel]:
        """Get a named methodology model."""
        return self.models.get(name)

    def select_model_for_task(
        self,
        contribution_type: str = "",
        labor_iteration: int = 1,
        task_type: str = "",
        agent_name: str = "",
        task_status: str = "",
        priority: str = "",
    ) -> MethodologyModel:
        """Select the methodology model for a task based on conditions.

        Evaluates model_selection rules in order. First match wins.
        Each condition is split on AND — all clauses must match.
        Returns feature-development as default if no rules match.
        """
        fields = {
            "contribution_type": contribution_type,
            "labor_iteration": labor_iteration,
            "task_type": task_type,
            "agent": agent_name,
            "task.status": task_status,
            "priority": priority,
        }
        for rule in self.model_selection:
            if rule.condition == "default":
                return self.models.get(rule.model, self._default_model())
            if _evaluate_condition(rule.condition, fields):
                return self.models.get(rule.model, self._default_model())
        return self._default_model()

    def _default_model(self) -> MethodologyModel:
        """Return the feature-development model as fallback."""
        return self.models.get("feature-development", MethodologyModel(
            name="feature-development",
            stages=tuple(s.name for s in self.stages),
            completion_tool="fleet_task_complete",
            gates="po",
        ))


# ─── Loading ───────────────────────────────────────────────────────────


def _find_config_path() -> Path:
    """Find the methodology.yaml config file."""
    # FLEET_DIR environment variable (set by daemon, MCP, etc.)
    fleet_dir = os.environ.get("FLEET_DIR", "")
    if fleet_dir:
        p = Path(fleet_dir) / "config" / "methodology.yaml"
        if p.exists():
            return p

    # Relative to this file: fleet/core/methodology_config.py → ../../config/
    p = Path(__file__).resolve().parent.parent.parent / "config" / "methodology.yaml"
    if p.exists():
        return p

    raise FileNotFoundError(
        "config/methodology.yaml not found. "
        "Set FLEET_DIR or ensure the config exists."
    )


def load_methodology_config(path: Optional[Path] = None) -> MethodologyConfig:
    """Load methodology config from YAML.

    Args:
        path: Explicit path to methodology.yaml. If None, auto-discovers.

    Returns:
        Parsed MethodologyConfig.
    """
    if path is None:
        path = _find_config_path()

    with open(path) as f:
        raw = yaml.safe_load(f) or {}

    config = MethodologyConfig()

    # Parse stages
    for i, s in enumerate(raw.get("stages", [])):
        rr = s.get("readiness_range", [0, 100])
        config.stages.append(StageDefinition(
            name=s["name"],
            readiness_min=rr[0],
            readiness_max=rr[1],
            description=s.get("description", ""),
            summary=s.get("summary", ""),
            suggested_readiness=s.get("suggested_readiness", 0),
            tools_blocked=tuple(s.get("tools_blocked", [])),
            protocol=s.get("protocol", "").strip(),
            order=i,
        ))

    # Parse task types
    for tt_name, tt_data in raw.get("task_types", {}).items():
        stages_list = tt_data if isinstance(tt_data, list) else tt_data.get("required_stages", [])
        config.task_types[tt_name] = TaskTypeDefinition(
            name=tt_name,
            required_stages=tuple(stages_list),
        )

    # Parse defaults
    defaults = raw.get("defaults", {})
    no_type = defaults.get("no_type_stages", ["reasoning", "work"])
    config.no_type_stages = tuple(no_type)
    config.no_metadata_stage = defaults.get("no_metadata_stage", "conversation")
    config.sprint_ready_threshold = defaults.get("sprint_ready_threshold", 80)

    for rule in defaults.get("verbatim_skip", []):
        config.verbatim_skip.append(VerbatimSkipRule(
            threshold=rule["threshold"],
            target_stage=rule["target_stage"],
        ))
    # Sort by threshold descending — first match wins (highest first)
    config.verbatim_skip.sort(key=lambda r: r.threshold, reverse=True)

    # Valid readiness values
    config.valid_readiness = raw.get("valid_readiness", config.valid_readiness)

    # Parse named models
    for model_name, model_data in raw.get("models", {}).items():
        if not isinstance(model_data, dict):
            continue
        config.models[model_name] = MethodologyModel(
            name=model_name,
            description=model_data.get("description", ""),
            stages=tuple(model_data.get("stages", [])),
            completion_tool=model_data.get("completion_tool", "fleet_task_complete"),
            gates=model_data.get("gates", "po"),
            protocol_adaptations=model_data.get("protocol_adaptations", {}),
            readiness_cap=model_data.get("readiness_cap", 100),
        )

    # Parse model selection rules
    for rule in raw.get("model_selection", []):
        if isinstance(rule, dict):
            config.model_selection.append(ModelSelectionRule(
                condition=rule.get("condition", ""),
                model=rule.get("model", "feature-development"),
            ))

    return config


# ─── Cached singleton ─────────────────────────────────────────────────

_cached: Optional[MethodologyConfig] = None


def get_methodology_config() -> MethodologyConfig:
    """Get the cached methodology config (loads on first call)."""
    global _cached
    if _cached is None:
        _cached = load_methodology_config()
    return _cached


def reload_methodology_config() -> MethodologyConfig:
    """Force reload from disk. Call after PO edits the config."""
    global _cached
    _cached = load_methodology_config()
    return _cached
