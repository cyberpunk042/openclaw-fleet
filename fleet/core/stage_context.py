"""Stage-aware context — protocol instructions per methodology stage.

When an agent is dispatched, it receives instructions appropriate to
the current methodology stage of its task. An agent in "conversation"
stage gets different instructions than one in "work" stage.

These templates are injected into the agent's heartbeat context bundle
so the agent knows what protocol to follow.
"""

from __future__ import annotations

from fleet.core.methodology import Stage


# ─── Stage Context Templates ────────────────────────────────────────────

STAGE_INSTRUCTIONS: dict[Stage, str] = {

    Stage.CONVERSATION: """
## Current Stage: CONVERSATION

You are in the conversation protocol. Your task is NOT ready for work.

### What you MUST do:
- DISCUSS with the PO to understand the requirements
- Ask SPECIFIC questions about anything unclear
- Identify and STATE what you don't understand
- Propose your understanding and accept correction
- Extract knowledge and meaning from the PO

### What you MUST NOT do:
- Do NOT write code
- Do NOT commit changes
- Do NOT create PRs
- Do NOT produce finished deliverables
- Do NOT call fleet_commit or fleet_task_complete

### What you CAN produce:
- Questions in task comments
- Draft proposals for PO review
- Work-in-progress analysis (clearly marked as draft)

### How to advance:
- The PO confirms your understanding
- The PO increases readiness
- Verbatim requirement is populated and clear
- No open questions remain

Your job is to UNDERSTAND, not to BUILD.
""".strip(),

    Stage.ANALYSIS: """
## Current Stage: ANALYSIS

You are in the analysis protocol. Examine what exists.

### What you MUST do:
- Read and examine the codebase, existing implementation, architecture
- Produce an analysis document (iterative, work-in-progress)
- Reference SPECIFIC files and line numbers — not vague descriptions
- Present findings to the PO via task comments
- Identify implications for the task

### What you MUST NOT do:
- Do NOT produce solutions (that's reasoning stage)
- Do NOT write implementation code
- Do NOT commit changes
- Do NOT call fleet_commit or fleet_task_complete

### What you CAN produce:
- Analysis documents with file references
- Current state assessments
- Gap analysis
- Dependency mapping
- Impact analysis

### How to advance:
- Analysis document exists and covers the relevant codebase areas
- PO reviewed the findings
- Implications for the task are clear

Your job is to UNDERSTAND WHAT EXISTS, not to solve the problem.
""".strip(),

    Stage.INVESTIGATION: """
## Current Stage: INVESTIGATION

You are in the investigation protocol. Research what's possible.

### What you MUST do:
- Research solutions, explore options, examine prior art
- Produce an investigation document with findings
- Explore MULTIPLE options — not just the first one you find
- Cite sources where applicable
- Present findings to the PO

### What you MUST NOT do:
- Do NOT decide on an approach (that's reasoning stage)
- Do NOT write implementation code
- Do NOT commit changes
- Do NOT call fleet_commit or fleet_task_complete

### What you CAN produce:
- Research findings organized by topic
- Option comparisons with tradeoffs
- Technical exploration documents
- Platform capability assessments

### How to advance:
- Research document exists with multiple options explored
- PO reviewed the findings
- Enough information to make a decision in reasoning stage

Your job is to EXPLORE OPTIONS, not to decide.
""".strip(),

    Stage.REASONING: """
## Current Stage: REASONING

You are in the reasoning protocol. Plan your approach.

### What you MUST do:
- Decide on an approach based on requirements + analysis + investigation
- Produce an implementation plan
- The plan MUST reference the verbatim requirement explicitly
- Specify target files and components
- Map acceptance criteria to specific implementation steps
- Present the plan to the PO for confirmation

### What you MUST NOT do:
- Do NOT start implementing yet
- Do NOT commit code
- Do NOT call fleet_commit or fleet_task_complete

### What you CAN produce:
- Implementation plans with specific file/component references
- Design decisions with justification
- Task breakdown (subtasks if needed via fleet_task_create)
- Acceptance criteria mapping

### How to advance:
- Plan exists and references the verbatim requirement
- Plan specifies target files
- PO confirmed the plan
- Readiness reaches 99-100%

Your job is to PLAN, not to execute.
""".strip(),

    Stage.WORK: """
## Current Stage: WORK

You are in the work protocol. Execute the confirmed plan.

### What you MUST do:
- Execute the plan that was confirmed in reasoning stage
- Follow existing conventions: conventional commits, proper testing
- Stay within scope — work from the verbatim requirement and confirmed plan
- Call fleet_read_context first to load task context
- Call fleet_task_accept with your plan
- Call fleet_commit for each logical change
- Call fleet_task_complete when done

### What you MUST NOT do:
- Do NOT deviate from the confirmed plan
- Do NOT add unrequested scope ("while I'm here" changes)
- Do NOT modify files outside the plan's target files
- Do NOT skip tests

### Required tool sequence:
1. fleet_read_context (load task + methodology state)
2. fleet_task_accept (confirm plan)
3. fleet_commit (one or more — conventional format)
4. fleet_task_complete (push, PR, review)

### Standards:
- Conventional commit format
- Task ID in commit messages
- Tests for new functionality
- PR with description referencing the task

Your job is to EXECUTE THE PLAN, not to redesign.
""".strip(),
}


def get_stage_instructions(stage: str) -> str:
    """Get the protocol instructions for a methodology stage.

    Args:
        stage: The stage value (conversation, analysis, etc.)

    Returns:
        Instruction text for the agent. Empty string if stage unknown.
    """
    try:
        return STAGE_INSTRUCTIONS.get(Stage(stage), "")
    except ValueError:
        return ""


def get_stage_summary(stage: str) -> str:
    """Get a one-line summary of what the agent should be doing.

    Used in compact displays (e.g., heartbeat summary, event stream).
    """
    summaries = {
        "conversation": "Discussing with PO — do NOT produce code",
        "analysis": "Analyzing codebase — produce analysis document",
        "investigation": "Researching options — explore multiple approaches",
        "reasoning": "Planning approach — produce plan for PO confirmation",
        "work": "Executing confirmed plan — follow tool sequence",
    }
    return summaries.get(stage, f"Stage: {stage}")