# Tiered Rendering Phase 1 — Expert Tier Formatting Fixes

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the TierRenderer module and fix all formatting/missing-data issues for Expert tier agents (Claude), resolving validation issues F1-F4, H11/H12, I1/I2/I3, I5, J1.

**Architecture:** New `fleet/core/tier_renderer.py` module owns depth/formatting per section. Preembed owns autocomplete chain order, delegates formatting to renderer. Config-driven tier rules in `config/tier-profiles.yaml`. Backward compatible — existing tests pass without changes.

**Tech Stack:** Python 3.11+, pytest, YAML config, existing fleet/core/ patterns

**Spec:** [docs/superpowers/specs/2026-04-09-context-injection-tiered-rendering-design.md](../specs/2026-04-09-context-injection-tiered-rendering-design.md)

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `fleet/core/tier_renderer.py` | CREATE | TierRenderer class — all format methods, tier rules |
| `fleet/tests/core/test_tier_renderer.py` | CREATE | Renderer tests — per method, per tier |
| `config/tier-profiles.yaml` | CREATE | Tier depth rules (expert, capable, lightweight, flagship-local) |
| `fleet/core/preembed.py` | MODIFY | Accept renderer param, delegate formatting |
| `fleet/core/role_providers.py` | NO CHANGE | Providers keep returning dicts — renderer handles formatting |
| `fleet/cli/orchestrator.py` | MODIFY | Create renderer per agent, pass to preembed |
| `fleet/tests/core/test_preembed.py` | MODIFY | Verify backward compat, add renderer-aware tests |
| `config/methodology.yaml` | MODIFY | Add role_protocol field per stage |
| `scripts/generate-validation-matrix.py` | MODIFY | Add tier param, new scenarios |

---

### Task 1: Tier Profiles Config

**Files:**
- Create: `config/tier-profiles.yaml`
- Test: `fleet/tests/core/test_tier_renderer.py`

- [ ] **Step 1: Create tier profiles config**

```yaml
# config/tier-profiles.yaml — Capability tier depth rules
#
# Each tier defines HOW MUCH of each section to render.
# Preembed owns ORDER. Renderer owns DEPTH.
#
# Tiers map to AICP operational profiles:
#   expert → claude (cloud)
#   capable → qwen3-8b, openrouter (default, code-review)
#   flagship_local → gemma4-26b dual GPU (dual-gpu)
#   lightweight → gemma4-e2b, qwen3-4b (fleet-light, fast)

expert:
  description: "Full context — trust the agent"
  task_detail: full
  contributions: full_inline
  protocol: full
  phase_standards: full
  chain_awareness: full
  role_data: full_formatted
  events_limit: 10
  standing_orders: full
  messages: full
  action_directive: full

capable:
  description: "Condensed — clear multi-step instructions"
  task_detail: core_fields
  contributions: status_only
  protocol: must_must_not
  phase_standards: one_liner
  chain_awareness: one_line
  role_data: counts_plus_top3
  events_limit: 5
  standing_orders: name_desc_only
  messages: full
  action_directive: full

flagship_local:
  description: "Large context local — more budget, same capability"
  extends: capable
  contributions: summary
  role_data: counts_plus_top5
  events_limit: 8

lightweight:
  description: "Focused — don't overwhelm the trainee"
  task_detail: title_stage_only
  contributions: names_only
  protocol: short_rules
  phase_standards: name_only
  chain_awareness: omit
  role_data: counts_only
  events_limit: 0
  standing_orders: omit
  messages: truncated
  action_directive: one_line
```

- [ ] **Step 2: Write test to verify config loads**

```python
# fleet/tests/core/test_tier_renderer.py
"""Tests for fleet.core.tier_renderer."""

import pytest


class TestTierProfileLoading:
    def test_load_expert_profile(self):
        from fleet.core.tier_renderer import load_tier_rules
        rules = load_tier_rules("expert")
        assert rules["task_detail"] == "full"
        assert rules["contributions"] == "full_inline"
        assert rules["role_data"] == "full_formatted"

    def test_load_capable_profile(self):
        from fleet.core.tier_renderer import load_tier_rules
        rules = load_tier_rules("capable")
        assert rules["task_detail"] == "core_fields"
        assert rules["contributions"] == "status_only"

    def test_load_lightweight_profile(self):
        from fleet.core.tier_renderer import load_tier_rules
        rules = load_tier_rules("lightweight")
        assert rules["task_detail"] == "title_stage_only"
        assert rules["chain_awareness"] == "omit"

    def test_flagship_extends_capable(self):
        from fleet.core.tier_renderer import load_tier_rules
        rules = load_tier_rules("flagship_local")
        # Overrides
        assert rules["contributions"] == "summary"
        assert rules["events_limit"] == 8
        # Inherited from capable
        assert rules["task_detail"] == "core_fields"
        assert rules["protocol"] == "must_must_not"

    def test_unknown_tier_defaults_to_expert(self):
        from fleet.core.tier_renderer import load_tier_rules
        rules = load_tier_rules("unknown_tier")
        assert rules["task_detail"] == "full"
```

- [ ] **Step 3: Run test to verify it fails**

Run: `.venv/bin/python -m pytest fleet/tests/core/test_tier_renderer.py -v`
Expected: FAIL — module not found

- [ ] **Step 4: Commit config**

```bash
git add config/tier-profiles.yaml fleet/tests/core/test_tier_renderer.py
git commit -m "feat(config): add tier-profiles.yaml with 4 capability tiers [E001]"
```

---

### Task 2: TierRenderer Module Scaffold

**Files:**
- Create: `fleet/core/tier_renderer.py`
- Test: `fleet/tests/core/test_tier_renderer.py`

- [ ] **Step 1: Create TierRenderer with config loading and format_role_data**

```python
# fleet/core/tier_renderer.py
"""Tier-aware context rendering — depth per section per capability tier.

Preembed owns ORDER (autocomplete chain sequence).
Renderer owns DEPTH (how much of each section to show).

Tiers: expert, capable, flagship_local, lightweight.
Config: config/tier-profiles.yaml.
"""

from __future__ import annotations

import os
from typing import Optional

import yaml

from fleet.core.models import Task


def load_tier_rules(tier: str) -> dict:
    """Load depth rules for a capability tier from config/tier-profiles.yaml."""
    fleet_dir = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(fleet_dir, "config", "tier-profiles.yaml")

    try:
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        data = {}

    if tier not in data:
        tier = "expert"  # safe default

    rules = dict(data.get("expert", {}))  # start with expert as base

    if tier != "expert":
        tier_data = data.get(tier, {})
        # Handle extends
        extends = tier_data.pop("extends", None)
        if extends and extends in data:
            base = dict(data[extends])
            base.pop("extends", None)
            base.pop("description", None)
            rules.update(base)
        tier_overrides = {k: v for k, v in tier_data.items() if k != "description"}
        rules.update(tier_overrides)

    rules.pop("description", None)
    return rules


class TierRenderer:
    """Render context sections at tier-appropriate depth.

    Usage:
        renderer = TierRenderer("expert")
        text = renderer.format_role_data("fleet-ops", role_data_dict)
    """

    def __init__(self, tier: str = "expert"):
        self.tier = tier
        self.rules = load_tier_rules(tier)

    # ── Role Data (fixes F1-F4) ────────────────────────────────────

    def format_role_data(self, role: str, data: dict) -> str:
        """Format role-specific data as human-readable text.

        Replaces raw dict dump with structured, readable output.
        Depth controlled by tier rules: full_formatted, counts_plus_top3,
        counts_plus_top5, counts_only.
        """
        if not data:
            return ""

        depth = self.rules.get("role_data", "full_formatted")

        if role == "fleet-ops":
            return self._format_fleet_ops_data(data, depth)
        elif role == "project-manager":
            return self._format_pm_data(data, depth)
        elif role == "architect":
            return self._format_architect_data(data, depth)
        elif role == "devsecops-expert":
            return self._format_devsecops_data(data, depth)
        else:
            return self._format_worker_data(data, depth)

    def _format_fleet_ops_data(self, data: dict, depth: str) -> str:
        lines = ["## ROLE DATA"]
        approvals = data.get("pending_approvals", 0)
        lines.append(f"- Pending approvals: {approvals}")

        if depth == "counts_only":
            offline = data.get("offline_agents", [])
            if offline:
                lines.append(f"- Offline agents: {len(offline)}")
            return "\n".join(lines)

        # Approval details
        details = data.get("approval_details", [])
        limit = 5 if depth == "full_formatted" else (5 if "top5" in depth else 3)
        if details:
            lines.append(f"### Review Queue ({len(details)})")
            for item in details[:limit]:
                task_id = item.get("task_id", "")[:8]
                status = item.get("status", "")
                lines.append(f"  - {item.get('id', '')}: task {task_id} ({status})")

        # Review queue
        queue = data.get("review_queue", [])
        if queue:
            lines.append(f"### Tasks in Review ({len(queue)})")
            for item in queue[:limit]:
                lines.append(f"  - {item.get('id', '')}: {item.get('title', '')} ({item.get('agent', '')})")

        # Offline agents
        offline = data.get("offline_agents", [])
        if offline:
            lines.append(f"- Offline: {', '.join(offline)}")

        return "\n".join(lines)

    def _format_pm_data(self, data: dict, depth: str) -> str:
        lines = ["## ROLE DATA"]
        unassigned = data.get("unassigned_tasks", 0)
        blocked = data.get("blocked_tasks", 0)
        progress = data.get("progress", "")
        inbox = data.get("inbox_count", 0)

        lines.append(f"- Unassigned tasks: {unassigned}")
        lines.append(f"- Blocked tasks: {blocked}")
        if progress:
            lines.append(f"- Sprint progress: {progress}")
        lines.append(f"- Total inbox: {inbox}")

        if depth == "counts_only":
            return "\n".join(lines)

        # Unassigned details
        details = data.get("unassigned_details", [])
        limit = 5 if depth == "full_formatted" else (5 if "top5" in depth else 3)
        if details:
            lines.append(f"### Unassigned Tasks ({len(details)})")
            for item in details[:limit]:
                lines.append(f"  - {item.get('id', '')}: {item.get('title', '')} ({item.get('priority', '')})")

        return "\n".join(lines)

    def _format_architect_data(self, data: dict, depth: str) -> str:
        lines = ["## ROLE DATA"]

        if depth == "counts_only":
            lines.append(f"- Design tasks: {len(data.get('design_tasks', []))}")
            lines.append(f"- High complexity: {len(data.get('high_complexity', []))}")
            return "\n".join(lines)

        design = data.get("design_tasks", [])
        limit = 5 if depth == "full_formatted" else (5 if "top5" in depth else 3)
        if design:
            lines.append(f"### Design Tasks ({len(design)})")
            for item in design[:limit]:
                lines.append(f"  - {item.get('id', '')}: {item.get('title', '')} ({item.get('stage', '')})")

        high = data.get("high_complexity", [])
        if high:
            lines.append(f"### High Complexity ({len(high)})")
            for item in high[:limit]:
                lines.append(f"  - {item.get('id', '')}: {item.get('title', '')}")

        return "\n".join(lines)

    def _format_devsecops_data(self, data: dict, depth: str) -> str:
        lines = ["## ROLE DATA"]

        if depth == "counts_only":
            lines.append(f"- Security tasks: {len(data.get('security_tasks', []))}")
            lines.append(f"- PRs needing review: {len(data.get('prs_needing_security_review', []))}")
            return "\n".join(lines)

        sec = data.get("security_tasks", [])
        limit = 5 if depth == "full_formatted" else 3
        if sec:
            lines.append(f"### Security Tasks ({len(sec)})")
            for item in sec[:limit]:
                lines.append(f"  - {item.get('id', '')}: {item.get('title', '')}")

        prs = data.get("prs_needing_security_review", [])
        if prs:
            lines.append(f"### PRs Needing Security Review ({len(prs)})")
            for item in prs[:limit]:
                lines.append(f"  - {item.get('id', '')}: {item.get('title', '')} (PR: {item.get('pr', '')})")

        return "\n".join(lines)

    def _format_worker_data(self, data: dict, depth: str) -> str:
        lines = ["## ROLE DATA"]
        count = data.get("my_tasks_count", 0)
        lines.append(f"- Assigned tasks: {count}")

        if depth == "counts_only":
            contribs = data.get("contribution_tasks", [])
            if contribs:
                lines.append(f"- Contribution tasks: {len(contribs)}")
            return "\n".join(lines)

        # Contribution tasks
        contribs = data.get("contribution_tasks", [])
        limit = 5 if depth == "full_formatted" else (5 if "top5" in depth else 3)
        if contribs:
            lines.append(f"### Contribution Tasks ({len(contribs)})")
            for item in contribs[:limit]:
                lines.append(f"  - Contribute {item.get('type', '')} for: {item.get('title', '')}")

        # Contributions received
        received = data.get("contributions_received", {})
        if received:
            lines.append("### Contributions Received")
            for task_id, items in received.items():
                parts = [f"{c.get('type', '')} ({c.get('from', '')}, {c.get('status', '')})" for c in items]
                lines.append(f"  - {task_id}: {', '.join(parts)}")

        # In review
        review = data.get("in_review", [])
        if review:
            lines.append(f"### In Review ({len(review)})")
            for item in review[:limit]:
                pr_part = f" (PR: {item['pr']})" if item.get("pr") else ""
                lines.append(f"  - {item.get('id', '')}: {item.get('title', '')}{pr_part}")

        return "\n".join(lines)

    # ── Rejection Context (fixes H11/H12) ──────────────────────────

    def format_rejection_context(self, iteration: int, feedback: str) -> str:
        """Render rejection rework context. Empty string if iteration <= 1."""
        if iteration <= 1:
            return ""

        lines = [
            f"## REJECTION REWORK (iteration {iteration})",
            "",
            "Your previous submission was rejected. Read the feedback below.",
            "Fix the ROOT CAUSE — not just the symptom. Add regression tests.",
            "Use `eng_fix_task_response()` to read full rejection details.",
            "",
        ]
        if feedback:
            lines.append("### Rejection Feedback")
            lines.append(f"> {feedback}")
            lines.append("")

        if iteration >= 3:
            lines.append(f"**WARNING:** Iteration {iteration}. If the same issue persists, escalate to PO.")
            lines.append("")

        return "\n".join(lines)

    # ── Action Directive (fixes J1) ────────────────────────────────

    def format_action_directive(self, stage: str, progress: int, iteration: int) -> str:
        """Render stage + progress-aware action directive."""
        depth = self.rules.get("action_directive", "full")

        if stage != "work":
            directives = {
                "conversation": "Read the verbatim requirement above. Ask specific clarifying questions. Do NOT produce code or solutions.",
                "analysis": "Examine the codebase for areas related to the requirement. Produce an analysis_document with specific file references.",
                "investigation": "Research multiple approaches (minimum 2). Document options with tradeoffs. Do NOT decide yet.",
                "reasoning": "Produce a plan that REFERENCES the verbatim requirement above. Specify target files and acceptance criteria mapping.",
            }
            text = directives.get(stage, "Follow the stage protocol above.")
            if depth == "one_line":
                return text.split(".")[0] + "."
            return text

        # Work stage — adapt to progress and iteration
        if iteration >= 2:
            return (
                "This is a REWORK. Read rejection feedback above. "
                "Use `eng_fix_task_response()`. Fix root cause. Add regression tests. "
                "Then `fleet_commit()` and `fleet_task_complete()`."
            )

        progress_directives = {
            (0, 0): "Starting work. `fleet_task_accept()` with your plan first, then implement.",
            (1, 49): "Continue implementation. `fleet_commit()` per logical change.",
            (50, 69): "Halfway. Continue implementation. Post progress update via `fleet_task_progress()`.",
            (70, 79): "Implementation done. Run tests. Prepare for `fleet_task_complete()`.",
            (80, 89): "Challenged. Address challenge findings before completing.",
            (90, 100): "Reviewed. Final polish, then `fleet_task_complete()`.",
        }

        for (lo, hi), text in progress_directives.items():
            if lo <= progress <= hi:
                if depth == "one_line":
                    return text.split(".")[0] + "."
                return text

        return "Execute the confirmed plan. `fleet_task_accept()` then implement."

    # ── Events (fixes A5) ─────────────────────────────────────────

    def format_events(self, events: list) -> str:
        """Render events section. Always present."""
        limit = self.rules.get("events_limit", 10)

        if limit == 0:
            if events:
                return f"## EVENTS SINCE LAST HEARTBEAT\n{len(events)} events. Call fleet_read_context for details."
            return "## EVENTS SINCE LAST HEARTBEAT\nNone."

        if not events:
            return "## EVENTS SINCE LAST HEARTBEAT\nNone."

        lines = ["## EVENTS SINCE LAST HEARTBEAT"]
        for event in events[:limit]:
            etype = event.get("type", "").split(".")[-1]
            agent = event.get("agent", "system")
            summary = event.get("summary", "")
            time = event.get("time", "")[:19]
            lines.append(f"  {time} [{etype}] {agent}: {summary}")

        if len(events) > limit:
            lines.append(f"  ... +{len(events) - limit} more events")

        return "\n".join(lines)

    # ── Contribution Target (fixes I1/I2/I3) ──────────────────────

    def format_contribution_task_context(
        self,
        contribution_type: str,
        contribution_target: str,
        target_task: Optional[Task] = None,
    ) -> str:
        """Render context for contribution tasks — show what you're contributing FOR."""
        if not contribution_type:
            return ""

        lines = [
            f"## CONTRIBUTION TASK",
            f"- Type: {contribution_type}",
            f"- Target task: {contribution_target[:8] if contribution_target else 'unknown'}",
        ]

        if target_task:
            lines.append(f"- Target title: {target_task.title}")
            cf = target_task.custom_fields
            if cf.requirement_verbatim:
                lines.append(f"- Target verbatim: {cf.requirement_verbatim}")
            if cf.delivery_phase:
                lines.append(f"- Target phase: {cf.delivery_phase}")
            if cf.task_stage:
                lines.append(f"- Target stage: {cf.task_stage}")

        lines.append("")
        lines.append(f"When done, call: `fleet_contribute(task_id='{contribution_target}', "
                     f"contribution_type='{contribution_type}', content=...)`")
        lines.append("")

        return "\n".join(lines)

    # ── Stage Protocol Role-Specific (fixes I5) ──────────────────

    def format_stage_protocol(self, stage: str, role: str) -> str:
        """Get stage protocol, with role-specific reasoning adaptation."""
        try:
            from fleet.core.stage_context import get_stage_instructions
            protocol = get_stage_instructions(stage)
        except Exception:
            protocol = ""

        if stage != "reasoning" or not protocol:
            return protocol

        # Role-specific reasoning: replace generic "implementation plan"
        # with role-appropriate output type
        role_outputs = {
            "software-engineer": "implementation plan with target files and acceptance criteria mapping",
            "architect": "design_input: approach, target files, patterns, constraints, integration points",
            "qa-engineer": "qa_test_definition: TC-XXX structured test criteria with priority and type",
            "devsecops-expert": "security_requirement: threat model, required controls, compliance needs",
            "ux-designer": "ux_spec: all states, all interactions, accessibility, all UX levels",
            "technical-writer": "documentation_outline: audience, structure, scope, complementary with architect/engineer",
            "devops": "infrastructure plan: deployment architecture, scaling strategy, monitoring",
            "fleet-ops": "review assessment: requirements coverage, compliance check, quality evaluation",
            "project-manager": "task breakdown: subtasks with dependencies, assignments, estimates",
            "accountability-generator": "compliance report: trail verification, methodology compliance, patterns",
        }

        if role in role_outputs:
            output_type = role_outputs[role]
            protocol = protocol.replace(
                "Produce an implementation plan",
                f"Produce {output_type}",
            )
            protocol = protocol.replace(
                "Implementation plans with specific file/component references",
                f"{output_type.split(':')[0].title()} with specific references",
            )

        return protocol
```

- [ ] **Step 2: Run tests to verify they pass (config loading)**

Run: `.venv/bin/python -m pytest fleet/tests/core/test_tier_renderer.py::TestTierProfileLoading -v`
Expected: 5 PASS

- [ ] **Step 3: Commit scaffold**

```bash
git add fleet/core/tier_renderer.py fleet/tests/core/test_tier_renderer.py
git commit -m "feat(core): add TierRenderer scaffold with config loading and format methods [E001]"
```

---

### Task 3: Role Data Formatting Tests

**Files:**
- Modify: `fleet/tests/core/test_tier_renderer.py`

- [ ] **Step 1: Write failing tests for role data formatting**

Add to `fleet/tests/core/test_tier_renderer.py`:

```python
class TestFormatRoleData:
    def _renderer(self, tier="expert"):
        from fleet.core.tier_renderer import TierRenderer
        return TierRenderer(tier)

    def test_fleet_ops_no_raw_dicts(self):
        """F1/F2: fleet-ops role data must NOT contain raw Python dicts."""
        data = {
            "pending_approvals": 2,
            "approval_details": [
                {"id": "appr-001", "task_id": "task-abc12345", "status": "pending"},
                {"id": "appr-002", "task_id": "task-def67890", "status": "pending"},
            ],
            "review_queue": [
                {"id": "task-abc1", "title": "Add fleet health dashboard", "agent": "software-engineer"},
            ],
            "offline_agents": ["ux-designer"],
        }
        result = self._renderer().format_role_data("fleet-ops", data)
        assert "{'id'" not in result, "Raw dict found in fleet-ops role data"
        assert "appr-001" in result
        assert "task-abc1" in result
        assert "Add fleet health dashboard" in result
        assert "ux-designer" in result

    def test_pm_no_raw_dicts(self):
        """F3/F4: PM role data must NOT contain raw Python dicts."""
        data = {
            "unassigned_tasks": 3,
            "unassigned_details": [
                {"id": "task-un1", "title": "Investigate memory leak", "priority": "high"},
            ],
            "blocked_tasks": 1,
            "progress": "12/25 done (48%)",
            "inbox_count": 5,
        }
        result = self._renderer().format_role_data("project-manager", data)
        assert "{'id'" not in result
        assert "Investigate memory leak" in result
        assert "high" in result
        assert "12/25 done (48%)" in result

    def test_worker_contributions_formatted(self):
        """Worker contributions_received must be human-readable."""
        data = {
            "my_tasks_count": 1,
            "contribution_tasks": [],
            "contributions_received": {
                "task-a1b": [
                    {"type": "design_input", "from": "architect", "status": "done"},
                    {"type": "qa_test_definition", "from": "qa-engineer", "status": "done"},
                ]
            },
            "in_review": [],
        }
        result = self._renderer().format_role_data("software-engineer", data)
        assert "{'type'" not in result
        assert "design_input" in result
        assert "architect" in result
        assert "done" in result

    def test_lightweight_counts_only(self):
        """Lightweight tier shows counts only, no item details."""
        data = {
            "pending_approvals": 2,
            "approval_details": [
                {"id": "appr-001", "task_id": "task-abc1", "status": "pending"},
            ],
            "review_queue": [],
            "offline_agents": ["ux-designer"],
        }
        result = self._renderer("lightweight").format_role_data("fleet-ops", data)
        assert "Pending approvals: 2" in result
        assert "appr-001" not in result  # no details at lightweight

    def test_empty_data_returns_empty(self):
        result = self._renderer().format_role_data("fleet-ops", {})
        assert result == ""
```

- [ ] **Step 2: Run tests**

Run: `.venv/bin/python -m pytest fleet/tests/core/test_tier_renderer.py::TestFormatRoleData -v`
Expected: 5 PASS (implementation already in Task 2)

- [ ] **Step 3: Commit tests**

```bash
git add fleet/tests/core/test_tier_renderer.py
git commit -m "test(core): add role data formatting tests for TierRenderer [E001]"
```

---

### Task 4: Rejection Context + Action Directive Tests

**Files:**
- Modify: `fleet/tests/core/test_tier_renderer.py`

- [ ] **Step 1: Write tests for rejection context and action directive**

Add to `fleet/tests/core/test_tier_renderer.py`:

```python
class TestFormatRejectionContext:
    def _renderer(self):
        from fleet.core.tier_renderer import TierRenderer
        return TierRenderer("expert")

    def test_iteration_1_empty(self):
        """First attempt has no rejection section."""
        result = self._renderer().format_rejection_context(1, "")
        assert result == ""

    def test_iteration_2_shows_feedback(self):
        """H11/H12: Rejection rework shows iteration and feedback."""
        result = self._renderer().format_rejection_context(2, "Missing test for TC-003")
        assert "iteration 2" in result.lower()
        assert "Missing test for TC-003" in result
        assert "eng_fix_task_response" in result
        assert "ROOT CAUSE" in result

    def test_iteration_3_shows_warning(self):
        result = self._renderer().format_rejection_context(3, "Still missing TC-003")
        assert "iteration 3" in result.lower()
        assert "WARNING" in result
        assert "escalate" in result.lower()


class TestFormatActionDirective:
    def _renderer(self):
        from fleet.core.tier_renderer import TierRenderer
        return TierRenderer("expert")

    def test_work_progress_0(self):
        """J1: Progress 0% says accept first."""
        result = self._renderer().format_action_directive("work", 0, 1)
        assert "fleet_task_accept" in result

    def test_work_progress_70(self):
        """J1: Progress 70% says run tests."""
        result = self._renderer().format_action_directive("work", 70, 1)
        assert "test" in result.lower()

    def test_work_progress_90(self):
        result = self._renderer().format_action_directive("work", 90, 1)
        assert "fleet_task_complete" in result

    def test_work_rework(self):
        """Rework iteration overrides progress directive."""
        result = self._renderer().format_action_directive("work", 0, 2)
        assert "REWORK" in result
        assert "eng_fix_task_response" in result

    def test_conversation_stage(self):
        result = self._renderer().format_action_directive("conversation", 0, 1)
        assert "clarifying questions" in result.lower()

    def test_reasoning_stage(self):
        result = self._renderer().format_action_directive("reasoning", 0, 1)
        assert "plan" in result.lower()
```

- [ ] **Step 2: Run tests**

Run: `.venv/bin/python -m pytest fleet/tests/core/test_tier_renderer.py::TestFormatRejectionContext fleet/tests/core/test_tier_renderer.py::TestFormatActionDirective -v`
Expected: 9 PASS

- [ ] **Step 3: Commit**

```bash
git add fleet/tests/core/test_tier_renderer.py
git commit -m "test(core): add rejection context and action directive tests [E001]"
```

---

### Task 5: Contribution Task Context + Role-Specific Protocol Tests

**Files:**
- Modify: `fleet/tests/core/test_tier_renderer.py`

- [ ] **Step 1: Write tests for contribution task and role-specific protocol**

Add to `fleet/tests/core/test_tier_renderer.py`:

```python
from fleet.core.models import Task, TaskCustomFields, TaskStatus


class TestFormatContributionTaskContext:
    def _renderer(self):
        from fleet.core.tier_renderer import TierRenderer
        return TierRenderer("expert")

    def test_no_contribution_type_empty(self):
        result = self._renderer().format_contribution_task_context("", "", None)
        assert result == ""

    def test_contribution_with_target(self):
        """I1/I2/I3: Contribution task shows target task context."""
        target = Task(
            id="task-target123", board_id="b1",
            title="Add fleet health dashboard",
            status=TaskStatus.IN_PROGRESS,
            custom_fields=TaskCustomFields(
                requirement_verbatim="Add health dashboard with agent grid",
                delivery_phase="mvp",
                task_stage="work",
            ),
        )
        result = self._renderer().format_contribution_task_context(
            "design_input", "task-target123", target,
        )
        assert "CONTRIBUTION TASK" in result
        assert "design_input" in result
        assert "task-tar" in result  # short ID
        assert "Add fleet health dashboard" in result
        assert "Add health dashboard with agent grid" in result
        assert "fleet_contribute" in result
        assert "mvp" in result

    def test_contribution_without_target_task(self):
        result = self._renderer().format_contribution_task_context(
            "qa_test_definition", "task-abc12345", None,
        )
        assert "qa_test_definition" in result
        assert "task-abc" in result
        assert "fleet_contribute" in result


class TestFormatStageProtocol:
    def _renderer(self):
        from fleet.core.tier_renderer import TierRenderer
        return TierRenderer("expert")

    def test_reasoning_engineer_says_implementation(self):
        """I5: Engineer reasoning says 'implementation plan'."""
        result = self._renderer().format_stage_protocol("reasoning", "software-engineer")
        assert "implementation plan" in result.lower()

    def test_reasoning_architect_says_design_input(self):
        """I5: Architect reasoning says 'design_input'."""
        result = self._renderer().format_stage_protocol("reasoning", "architect")
        assert "design_input" in result

    def test_reasoning_qa_says_test_criteria(self):
        """I5: QA reasoning says 'test criteria'."""
        result = self._renderer().format_stage_protocol("reasoning", "qa-engineer")
        assert "qa_test_definition" in result or "test criteria" in result.lower()

    def test_work_stage_not_role_specific(self):
        """Work stage protocol is the same regardless of role."""
        eng = self._renderer().format_stage_protocol("work", "software-engineer")
        arch = self._renderer().format_stage_protocol("work", "architect")
        # Both should contain "WORK" protocol, not role-specific adaptation
        assert "WORK" in eng
        assert "WORK" in arch
```

- [ ] **Step 2: Run tests**

Run: `.venv/bin/python -m pytest fleet/tests/core/test_tier_renderer.py::TestFormatContributionTaskContext fleet/tests/core/test_tier_renderer.py::TestFormatStageProtocol -v`
Expected: 7 PASS

- [ ] **Step 3: Commit**

```bash
git add fleet/tests/core/test_tier_renderer.py
git commit -m "test(core): add contribution task context and role-specific protocol tests [E001]"
```

---

### Task 6: Wire TierRenderer into Heartbeat Preembed

**Files:**
- Modify: `fleet/core/preembed.py`
- Modify: `fleet/tests/core/test_preembed.py`

- [ ] **Step 1: Write test for renderer integration in heartbeat**

Add to `fleet/tests/core/test_preembed.py`:

```python
class TestHeartbeatWithRenderer:
    def test_role_data_formatted_via_renderer(self):
        """Heartbeat uses renderer for role data — no raw dicts."""
        from fleet.core.tier_renderer import TierRenderer
        renderer = TierRenderer("expert")
        text = build_heartbeat_preembed(
            agent_name="fleet-ops",
            role="fleet-ops",
            assigned_tasks=[],
            role_data={
                "pending_approvals": 2,
                "approval_details": [
                    {"id": "appr-001", "task_id": "task-abc1", "status": "pending"},
                ],
                "review_queue": [
                    {"id": "task-abc1", "title": "Add dashboard", "agent": "software-engineer"},
                ],
                "offline_agents": [],
            },
            renderer=renderer,
        )
        assert "{'id'" not in text, "Raw dict still present in heartbeat output"
        assert "appr-001" in text
        assert "Add dashboard" in text

    def test_events_always_present(self):
        """A5: Events section always present even when empty."""
        from fleet.core.tier_renderer import TierRenderer
        renderer = TierRenderer("expert")
        text = build_heartbeat_preembed(
            agent_name="fleet-ops", role="fleet-ops",
            assigned_tasks=[], renderer=renderer,
        )
        assert "EVENTS SINCE LAST HEARTBEAT" in text
        assert "None." in text

    def test_backward_compat_no_renderer(self):
        """Existing code without renderer param still works."""
        text = build_heartbeat_preembed(
            agent_name="fleet-ops", role="fleet-ops",
            assigned_tasks=[],
        )
        assert "HEARTBEAT CONTEXT" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest fleet/tests/core/test_preembed.py::TestHeartbeatWithRenderer -v`
Expected: FAIL — build_heartbeat_preembed doesn't accept renderer param

- [ ] **Step 3: Modify build_heartbeat_preembed to accept and use renderer**

In `fleet/core/preembed.py`, modify `build_heartbeat_preembed` signature to add `renderer=None` parameter. When renderer is provided, use `renderer.format_role_data()` instead of raw dict dump, and `renderer.format_events()` instead of inline event formatting. When renderer is None, fall back to current behavior (backward compat).

Key changes:
- Add `renderer: Optional[TierRenderer] = None` param
- Import TierRenderer at top (guarded)
- In role_data section: `if renderer: lines.append(renderer.format_role_data(role, role_data))` else current code
- In events section: `if renderer: lines.append(renderer.format_events(events or []))` else current code
- Always include events section (even when empty) if renderer provided

- [ ] **Step 4: Run all preembed tests to verify no regression**

Run: `.venv/bin/python -m pytest fleet/tests/core/test_preembed.py -v`
Expected: ALL PASS (existing + new)

- [ ] **Step 5: Commit**

```bash
git add fleet/core/preembed.py fleet/tests/core/test_preembed.py
git commit -m "feat(core): wire TierRenderer into heartbeat preembed — fixes F1-F4, A5 [E001]"
```

---

### Task 7: Wire TierRenderer into Task Preembed

**Files:**
- Modify: `fleet/core/preembed.py`
- Modify: `fleet/tests/core/test_preembed.py`

- [ ] **Step 1: Write tests for renderer integration in task preembed**

Add to `fleet/tests/core/test_preembed.py`:

```python
class TestTaskWithRenderer:
    def test_rejection_rework_visible(self):
        """H11/H12: Rejection rework shows iteration and feedback."""
        from fleet.core.tier_renderer import TierRenderer
        renderer = TierRenderer("expert")
        task = _make_task(custom_fields=TaskCustomFields(
            task_stage="work", task_readiness=99,
            requirement_verbatim="Add health dashboard",
            agent_name="software-engineer",
            labor_iteration=2,
        ))
        text = build_task_preembed(task, renderer=renderer, rejection_feedback="Missing TC-003 test")
        assert "iteration 2" in text.lower()
        assert "Missing TC-003" in text
        assert "eng_fix_task_response" in text

    def test_progress_adapted_action(self):
        """J1: Action directive adapts to progress %."""
        from fleet.core.tier_renderer import TierRenderer
        renderer = TierRenderer("expert")
        task = _make_task(custom_fields=TaskCustomFields(
            task_stage="work", task_readiness=99, task_progress=70,
            requirement_verbatim="Add dashboard",
            agent_name="software-engineer",
        ))
        text = build_task_preembed(task, renderer=renderer)
        assert "test" in text.lower()  # 70% = run tests

    def test_contribution_task_shows_target(self):
        """I1: Contribution task shows target task context."""
        from fleet.core.tier_renderer import TierRenderer
        renderer = TierRenderer("expert")
        target = _make_task(title="Target Task", custom_fields=TaskCustomFields(
            requirement_verbatim="Build the thing",
            delivery_phase="mvp",
        ))
        task = Task(
            id="task-contrib99", board_id="b1",
            title="Contribute design_input",
            status=TaskStatus.IN_PROGRESS,
            custom_fields=TaskCustomFields(
                task_stage="reasoning", task_readiness=80,
                agent_name="architect",
                contribution_type="design_input",
                contribution_target="task-12345678",
            ),
        )
        text = build_task_preembed(task, renderer=renderer, target_task=target)
        assert "CONTRIBUTION TASK" in text
        assert "design_input" in text
        assert "Build the thing" in text
        assert "fleet_contribute" in text

    def test_role_specific_reasoning(self):
        """I5: Architect sees 'design_input' in reasoning protocol."""
        from fleet.core.tier_renderer import TierRenderer
        renderer = TierRenderer("expert")
        task = _make_task(custom_fields=TaskCustomFields(
            task_stage="reasoning", task_readiness=85,
            requirement_verbatim="Design the header",
            agent_name="architect",
        ))
        text = build_task_preembed(task, renderer=renderer)
        assert "design_input" in text

    def test_backward_compat_no_renderer(self):
        """Existing code without renderer still works."""
        task = _make_task()
        text = build_task_preembed(task)
        assert "YOUR TASK:" in text
        assert "VERBATIM REQUIREMENT" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest fleet/tests/core/test_preembed.py::TestTaskWithRenderer -v`
Expected: FAIL — build_task_preembed doesn't accept renderer/rejection_feedback/target_task params

- [ ] **Step 3: Modify build_task_preembed to accept and use renderer**

In `fleet/core/preembed.py`, modify `build_task_preembed` to:
- Add params: `renderer=None`, `rejection_feedback=""`, `target_task=None`
- After §0 mode: if renderer and iteration >= 2, add iteration indicator
- After §5 verbatim: if renderer and contribution task, add contribution task context
- §6 protocol: if renderer, use `renderer.format_stage_protocol(stage, agent_name)`
- Before §7: if renderer and iteration >= 2, add rejection context section
- §9 action: if renderer, use `renderer.format_action_directive(stage, progress, iteration)`
- Backward compat: when renderer is None, current behavior preserved

- [ ] **Step 4: Run all preembed tests**

Run: `.venv/bin/python -m pytest fleet/tests/core/test_preembed.py -v`
Expected: ALL PASS

- [ ] **Step 5: Run full test suite**

Run: `.venv/bin/python -m pytest fleet/tests/ -q --tb=short`
Expected: 2385+ passed, 0 failed

- [ ] **Step 6: Commit**

```bash
git add fleet/core/preembed.py fleet/tests/core/test_preembed.py
git commit -m "feat(core): wire TierRenderer into task preembed — fixes H11/H12, I1/I2/I3, I5, J1 [E001]"
```

---

### Task 8: Wire Renderer into Orchestrator

**Files:**
- Modify: `fleet/cli/orchestrator.py`

- [ ] **Step 1: Modify _refresh_agent_contexts to create and pass renderer**

In `fleet/cli/orchestrator.py`, in the `_refresh_agent_contexts` function:

After the existing imports at the top of the function, add:
```python
from fleet.core.tier_renderer import TierRenderer
```

Before the per-agent loop, determine the fleet-wide default tier:
```python
# Determine default tier from backend_mode
backend_mode = fleet_state_dict.get("backend_mode", "claude")
if "claude" in backend_mode:
    default_tier = "expert"
elif "localai" in backend_mode and "claude" not in backend_mode:
    default_tier = "lightweight"
else:
    default_tier = "capable"
```

Inside the per-agent loop, create renderer and pass to preembed calls:
```python
renderer = TierRenderer(default_tier)
```

Pass `renderer=renderer` to `build_heartbeat_preembed()` and `build_task_preembed()` calls.

For task preembed, also pass rejection_feedback and target_task when applicable:
```python
# Load rejection feedback for rework tasks
rejection_feedback = ""
iteration = current_task.custom_fields.labor_iteration or 1
if iteration >= 2:
    # Try to get rejection feedback from task comments
    try:
        comments = await mc.list_comments(board_id, current_task.id)
        for c in reversed(comments or []):
            content = c.get("content", "") if isinstance(c, dict) else getattr(c, "content", "")
            if "REJECTED" in content or "rejected" in content.lower():
                rejection_feedback = content[:500]
                break
    except Exception:
        pass

# Load target task for contribution tasks
target_task_obj = None
if current_task.custom_fields.contribution_target:
    target_task_obj = next(
        (t for t in tasks if t.id == current_task.custom_fields.contribution_target),
        None,
    )

task_text = build_task_preembed(
    current_task,
    renderer=renderer,
    rejection_feedback=rejection_feedback,
    target_task=target_task_obj,
)
```

- [ ] **Step 2: Run full test suite to verify no regression**

Run: `.venv/bin/python -m pytest fleet/tests/ -q --tb=short`
Expected: 2385+ passed, 0 failed

- [ ] **Step 3: Commit**

```bash
git add fleet/cli/orchestrator.py
git commit -m "feat(orchestrator): wire TierRenderer into context refresh cycle [E001]"
```

---

### Task 9: Update Validation Matrix Generator

**Files:**
- Modify: `scripts/generate-validation-matrix.py`

- [ ] **Step 1: Add tier parameter and new scenarios to the generator**

Update `scripts/generate-validation-matrix.py`:

Add `TierRenderer` import and pass renderer to all preembed calls:
```python
from fleet.core.tier_renderer import TierRenderer
```

For each existing scenario, pass `renderer=TierRenderer("expert")` to the preembed calls.

Add new scenarios for formatted role data:
- HB-04 regenerated (fleet-ops reviews now formatted)
- HB-05 regenerated (PM unassigned now formatted)
- TK-06 regenerated (rejection rework now shows iteration + feedback)
- TK-07 regenerated (architect contribution now shows target task)

Add new scenario:
```python
# TK-34: Engineer role-specific reasoning
render_task_scenario("TK-34-engineer-reasoning.md",
    "Task: Engineer reasoning — role-specific protocol",
    make_task(custom_fields=TaskCustomFields(
        task_stage="reasoning", task_readiness=85,
        requirement_verbatim="Add health dashboard with agent grid",
        agent_name="software-engineer", task_type="story",
    )),
    renderer=TierRenderer("expert"),
    nav=NAV_REASONING,
    notes="Engineer reasoning should say 'implementation plan'. Architect would say 'design_input'.",
)
```

- [ ] **Step 2: Run the generator and inspect output**

Run: `.venv/bin/python scripts/generate-validation-matrix.py`

Check key scenarios:
- `cat validation-matrix/HB-04-fleet-ops-reviews.md` — should have formatted approvals, NOT raw dicts
- `cat validation-matrix/TK-06-rejection-rework.md` — should show "iteration 2" and rejection feedback
- `cat validation-matrix/TK-07-architect-contribution.md` — should show target task context

- [ ] **Step 3: Commit updated generator + matrix**

```bash
git add scripts/generate-validation-matrix.py validation-matrix/
git commit -m "feat(validation): update matrix generator with TierRenderer — formatted role data, rejection, contributions [E001]"
```

---

### Task 10: Full Regression + Summary

- [ ] **Step 1: Run full test suite**

Run: `.venv/bin/python -m pytest fleet/tests/ -v --tb=short 2>&1 | tail -20`
Expected: 2385+ passed (plus new tests), 0 failed

- [ ] **Step 2: Run ruff checks**

Run: `.venv/bin/python -m ruff check fleet/core/tier_renderer.py fleet/core/preembed.py`
Expected: no errors

- [ ] **Step 3: Verify validation matrix renders correctly**

Run: `.venv/bin/python scripts/generate-validation-matrix.py`
Inspect: `ls -la validation-matrix/` — should have 15+ scenario files

- [ ] **Step 4: Summary commit**

```bash
git add -A
git status  # verify no secrets or unintended files
git commit -m "feat(core): TierRenderer Phase 1 complete — Expert tier formatting fixes [E001]

Fixes: F1-F4 (raw dict rendering), H11/H12 (rejection visibility),
I1/I2/I3 (contribution task context), I5 (role-specific protocols),
J1 (progress-adapted actions), A5 (events always present).

New module: fleet/core/tier_renderer.py
New config: config/tier-profiles.yaml
Updated: preembed.py, orchestrator.py, generate-validation-matrix.py"
```
