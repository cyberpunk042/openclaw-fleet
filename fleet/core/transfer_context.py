"""Transfer context packaging — gather everything for task handoff.

When a task transfers from one agent to another (e.g., architect → engineer),
the receiving agent needs ALL context: contributions received, artifacts
produced, trail history, current stage/readiness, and a summary of what
was done and what remains.

This module packages that context for injection into the receiving
agent's task-context.md.

Source: fleet-elevation/24 (fleet_transfer tree: package_context)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class TransferPackage:
    """Complete context package for task transfer."""

    task_id: str
    from_agent: str
    to_agent: str
    stage: str = ""
    readiness: int = 0

    # Contributions received on this task
    contributions: list[dict] = field(default_factory=list)
    # format: [{"type": "design_input", "from": "architect", "summary": "..."}]

    # Artifacts produced (types and completeness)
    artifacts: list[dict] = field(default_factory=list)
    # format: [{"type": "analysis_document", "completeness_pct": 80}]

    # Trail summary (key events)
    trail_events: list[str] = field(default_factory=list)
    # format: ["Stage: analysis → reasoning", "Contribution: architect design_input"]

    # Context summary from the transferring agent
    context_summary: str = ""

    def format_for_injection(self) -> str:
        """Format the transfer package for context file injection.

        The receiving agent reads this in their task-context.md
        to understand what was done before them.
        """
        lines = [
            "## TRANSFER CONTEXT",
            "",
            f"This task was transferred from **{self.from_agent}** to **{self.to_agent}**.",
            f"**Stage:** {self.stage} | **Readiness:** {self.readiness}%",
            "",
        ]

        if self.context_summary:
            lines.extend([
                "### What was done",
                self.context_summary,
                "",
            ])

        if self.contributions:
            lines.append("### Contributions received")
            for c in self.contributions:
                lines.append(
                    f"- **{c.get('type', 'unknown')}** from {c.get('from', 'unknown')}: "
                    f"{c.get('summary', '(no summary)')[:200]}"
                )
            lines.append("")

        if self.artifacts:
            lines.append("### Artifacts")
            for a in self.artifacts:
                lines.append(
                    f"- **{a.get('type', 'unknown')}**: "
                    f"{a.get('completeness_pct', 0)}% complete"
                )
            lines.append("")

        if self.trail_events:
            lines.append("### Trail summary")
            for event in self.trail_events[:20]:
                lines.append(f"- {event}")
            lines.append("")

        return "\n".join(lines)


async def package_transfer_context(
    task_id: str,
    from_agent: str,
    to_agent: str,
    context_summary: str,
    mc,
    board_id: str,
    plane=None,
) -> TransferPackage:
    """Package all context for a task transfer.

    Gathers contributions, artifacts, trail events, and stage/readiness
    from the task's history.

    Args:
        task_id: Task being transferred.
        from_agent: Agent transferring from.
        to_agent: Agent receiving.
        context_summary: Transferring agent's summary of what was done.
        mc: MCClient for reading task data.
        board_id: Board ID.
        plane: Optional PlaneClient for artifact data.

    Returns:
        TransferPackage ready for context injection.
    """
    package = TransferPackage(
        task_id=task_id,
        from_agent=from_agent,
        to_agent=to_agent,
        context_summary=context_summary,
    )

    try:
        # Get task data for stage/readiness
        task = await mc.get_task(board_id, task_id)
        if task:
            cf = task.custom_fields
            package.stage = cf.task_stage or "unknown"
            package.readiness = cf.task_readiness or 0
    except Exception as e:
        logger.debug("Transfer context: failed to read task: %s", e)

    # Gather contributions from task comments
    try:
        comments = await mc.list_comments(board_id, task_id)
        for c in (comments or []):
            content = c.message if hasattr(c, 'message') else c.get("message", "")
            if "**Contribution (" in content:
                # Parse contribution type and contributor
                try:
                    type_start = content.index("(") + 1
                    type_end = content.index(")")
                    contrib_type = content[type_start:type_end]

                    from_start = content.index("from ") + 5
                    from_end = content.index(":", from_start)
                    contributor = content[from_start:from_end].strip()

                    # Summary is the first 200 chars of the content after the header
                    summary_start = content.index("\n\n", from_end) + 2 if "\n\n" in content[from_end:] else from_end
                    summary = content[summary_start:summary_start + 200].strip()

                    package.contributions.append({
                        "type": contrib_type,
                        "from": contributor,
                        "summary": summary,
                    })
                except (ValueError, IndexError):
                    pass
    except Exception as e:
        logger.debug("Transfer context: failed to read comments: %s", e)

    # Gather trail events from board memory
    try:
        memory = await mc.list_memory(board_id, limit=100)
        for m in memory:
            tags = m.tags if hasattr(m, 'tags') else m.get("tags", [])
            content = m.content if hasattr(m, 'content') else m.get("content", "")
            if "trail" in tags and f"task:{task_id}" in str(tags):
                # Extract the trail event text (after "[trail]" prefix)
                trail_text = content.replace("**[trail]**", "").strip()
                if trail_text:
                    package.trail_events.append(trail_text[:150])
    except Exception as e:
        logger.debug("Transfer context: failed to read trail: %s", e)

    # Gather artifact data from Plane (if available)
    if plane:
        try:
            task = await mc.get_task(board_id, task_id)
            cf = task.custom_fields
            plane_id = cf.plane_issue_id or ""
            workspace = cf.plane_workspace or ""
            project_id = cf.plane_project_id or ""

            if plane_id and workspace and project_id:
                from fleet.core.transpose import from_html, get_artifact_type
                from fleet.core.artifact_tracker import check_artifact_completeness

                issues = await plane.list_issues(workspace, project_id)
                issue = next((i for i in issues if i.id == plane_id), None)
                if issue and issue.description_html:
                    obj = from_html(issue.description_html)
                    art_type = get_artifact_type(issue.description_html)
                    if obj and art_type:
                        completeness = check_artifact_completeness(art_type, obj)
                        package.artifacts.append({
                            "type": art_type,
                            "completeness_pct": completeness.required_pct,
                        })
        except Exception as e:
            logger.debug("Transfer context: failed to read artifacts: %s", e)

    return package
