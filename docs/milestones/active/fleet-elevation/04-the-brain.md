# The Brain — Orchestrator Redesign

**Date:** 2026-03-30
**Status:** Design — comprehensive brain architecture
**Part of:** Fleet Elevation (document 4 of 22)

---

## PO Requirements (Verbatim)

> "Its important to consider the brain too. the orchestration and logic
> layers play an important part in avoiding to give needless work to the
> AI or even things that are not even logical to give to AI, especially
> in a fine-tuned fleet."

> "The Brain is not called brain for nothing it is a critical part for
> the cortexes / agents to do their part."

> "Proper interrelation with the brain / orchestrator and the sync and
> events and notifications and messages."

> "we need to do the right directive so the AI know if it need to use
> this bus or this bus and know that it will do this chain naturally and
> do this and that and so on."

> "WE have to make it possible for the agents to do their work with
> clear chain entries, ins and outs and middles and groups of operations."

---

## What This Document Covers

The brain — the fleet's central orchestrator — redesigned from a
simple task dispatcher to an intelligent logic layer that:
- Maximizes deterministic work (no AI needed)
- Fires chains on events (reactive, not polling)
- Creates contribution opportunities for cross-agent synergy
- Enforces gates (PO approval at strategic checkpoints)
- Manages delivery phases (standards and advancement)
- Routes notifications to the right buses
- Propagates data across related tasks
- Sets up the autocomplete chain for each agent dispatch

---

## Current Brain (What Exists)

The orchestrator in `fleet/cli/orchestrator.py` runs an 11-step cycle
every 30 seconds:

0. Refresh agent contexts (pre-embed full data to context/ files)
1. Security scan (check new/changed tasks for suspicious content)
2. Doctor (immune system observation, detection, response)
3. Ensure review approvals (create approval objects for review tasks)
4. Wake drivers (PM for unassigned tasks, fleet-ops for approvals)
5. Dispatch ready tasks (unblocked inbox → in_progress, 4 gates)
6. Process directives (PO commands from board memory)
7. Evaluate parents (all children done → parent to review)
8. Health check (stuck tasks, offline agents, stale deps)

Plus: fleet control state reading (work mode, cycle phase, backend
mode), mode change detection, work mode support, change detection,
budget monitoring, fleet lifecycle tracking.

### What's Good About the Current Brain
- Cycle-based architecture is reliable and predictable
- Fleet control state respected (mode gates dispatch)
- Doctor integration works (detections → interventions)
- Context refresh writes FULL data every cycle
- Parent evaluation handles child → parent completion
- Driver waking handles PM and fleet-ops activation
- Budget monitoring prevents runaway spending

### What's Missing
- No chain registry — side effects are manually coded in each step
- No event-driven reactions — everything is poll-based (check every 30s)
- No contribution opportunity creation — agents only work on their tasks
- No phase gate enforcement — delivery phases don't exist yet
- No cross-task propagation — child comments don't flow to parent
- No transfer protocol — agent_name changes with no context packaging
- No trail recording — stage transitions aren't systematically logged
- Dispatch logic is simple: unblocked + assigned + online + not busy
  No consideration of: contribution readiness, phase standards, synergy

---

## The Redesigned Brain — Architecture

The brain has three layers:

### Layer 1: The Cycle (poll-based, every 30 seconds)
What it does: reads current state, runs health checks, dispatches work.
This is the HEARTBEAT of the fleet. Even if nothing is happening, the
cycle runs and verifies everything is healthy.

### Layer 2: The Chain Registry (event-driven, reactive)
What it does: when events fire during a cycle, handlers react
deterministically. Stage changes trigger contribution creation.
Completions trigger parent evaluation. Readiness changes trigger
gate checks. This is the NERVOUS SYSTEM — stimulus → response.

### Layer 3: The Logic Engine (rule-based, configurable)
What it does: evaluates complex conditions that require multiple
data points. "Should this task be dispatched?" requires checking:
unblocked, assigned, online, not busy, doctor cleared, phase
standards met, required contributions received, fleet mode allows.
This is the REASONING — not AI reasoning, but deterministic rule
evaluation.

---

## Layer 1: The Cycle — Redesigned Steps

```
Step 0: CONTEXT REFRESH
  - Read fleet control state (work mode, cycle phase, backend mode)
  - Detect mode changes → emit events
  - Read all tasks and agents from MC
  - Build agent status map (online, busy, idle, in_lesson, pruned)
  - Refresh every agent's context/ files with full pre-embed
  - Clear context assembly cache

Step 1: PROCESS EVENT QUEUE
  - Process any events queued since last cycle
  - Events from MCP tool calls (agent actions between cycles)
  - Events from Plane sync (external changes)
  - Each event dispatched to chain registry handlers

Step 2: DOCTOR
  - Run immune system observation cycle
  - Detection patterns against all active agents
  - Produce DoctorReport: detections, interventions, skip list
  - Execute interventions (prune, compact, teach)
  - NEW: contribution avoidance detection
  - NEW: synergy bypass detection
  - NEW: phase violation detection
  - NEW: trail gap detection

Step 3: GATE PROCESSING
  - Check for pending gate requests (readiness 90%, phase advance)
  - For each gate: has PO responded? (check board memory for PO tags)
  - If PO approved: advance readiness/phase, emit events
  - If PO rejected: regress, notify PM, emit events
  - If pending: do nothing (wait for PO)

Step 4: CONTRIBUTION MANAGEMENT
  - Check for tasks that need contributions based on stage/phase
  - Create contribution opportunity tasks if not already created
  - Check for completed contributions → propagate to parent task
  - Update task context with received contributions

Step 5: DISPATCH
  - Find dispatchable tasks (full logic engine evaluation)
  - For each: build autocomplete chain for target agent
  - Dispatch: update status, write context, notify, emit events
  - Respect: max_dispatch_per_cycle, work_mode limits

Step 6: APPROVAL & TRANSITION
  - Ensure review tasks have approval objects
  - Check for approved approvals → transition to done
  - Check for rejected approvals → set up regression
  - Wake fleet-ops if pending approvals exist

Step 7: PARENT EVALUATION
  - Build parent → children map
  - If ALL children of a parent are done → parent to review
  - Post summary comment on parent aggregating child results
  - Propagate child trail data to parent trail

Step 8: DRIVER MANAGEMENT
  - Wake PM if: unassigned tasks in inbox, or driver interval elapsed
  - Wake fleet-ops if: pending approvals, or review tasks stale
  - Inject relevant data into driver sessions via gateway

Step 9: CROSS-TASK PROPAGATION
  - Child task comments → summarize on parent
  - Contribution artifacts → add to target task's context
  - Transfer context → package for receiving agent
  - Trail events → record on task and parent

Step 10: SESSION MANAGEMENT
  - Read rate limit window usage (5h, 7d) from session telemetry
  - Read each active agent's context usage from session telemetry
  - Two parallel countdowns running:
    a) Context remaining per agent (organic awareness at 7%/5%)
    b) Rate limit session usage fleet-wide (awareness at 85%/90%)

  PO requirements (verbatim, 2026-04-01):
  > "at some point its force compact lol...the agent can only prepare
  > or declare with a till that its ready but we have to be sure that
  > it doesn't do it prematuraly either"

  > "if we reach the end of the reset I can surely tell you that we
  > will force compact all conversation that are too last and will cause
  > a spike, this is why we are aware and will not display a 1m context
  > big quest when approaching that time for example"

  > "imagine you room over 5 x 200 000 or 2 x 1m and whatnot this
  > makes no sense on a pro x5 that will take 50% of the whole 5 hours"

  > "this is why not only you prepare them to extract their work and
  > prepare for compat when appropriate allowing the overflows for the
  > budget of compacting even though over 90"

  > "if you are over 40 to 80 000 tokens or that you do not need to
  > persist your session context (useless predicted cost for the sole
  > purpose of being ready for a next job later...), dump (as smart
  > artifacts) it for a synthesised re-injection later if needed and/or
  > simply a new task if not related. Only smart things. the brain is
  > smart. it goes without saying."

  Session management logic:
  a) DO NOT dispatch 1M context tasks near rate limit rollover
  b) Near rollover, evaluate each agent's context:
     - Does this agent have upcoming work that needs this context?
     - Is the context over ~40-80K tokens (threshold to tune)?
     - If no predicted need → dump as smart artifacts, fresh session
     - If related work coming → synthesised re-injection later
     - If unrelated work → simply new task, no re-injection needed
  c) Force compact IS appropriate near rollover for heavy contexts
     - Allow going over 90% rate limit budget for compacting itself
     - The compaction cost saves more than it spends
  d) After rollover, properly put agents back on track
     - Fresh sessions where needed
     - Re-inject synthesised context where work continues
  e) Aggregate context math matters:
     - 5 × 200K = 1M tokens re-sent on rollover → ~50% of x5 Pro
     - 2 × 1M = 2M tokens re-sent → exceeds x5 Pro window
     - Brain must calculate total fleet context cost vs remaining quota
  f) Smart, not wasteful: don't persist context "just in case"
     - Only keep context alive if there's a predicted upcoming job
     - Idle agents with no predicted work = dump context to artifacts

Step 11: HEALTH & BUDGET
  - Tasks stuck > 48h → alert PM
  - Agents offline with assigned work → alert PM
  - Budget check → if over threshold, reduce work mode
  - Sprint progress → update board memory periodically

Step 12: DIRECTIVES
  - Read PO directives from board memory
  - Route to target agents via their context/ files
  - Mark directives as processed (tag update)
```

---

## Layer 2: The Chain Registry

The chain registry is a mapping from event types to handler functions.
When an event fires, ALL registered handlers for that event type
execute.

### Architecture

```python
class ChainRegistry:
    """Event → handler mapping. Deterministic chains."""

    def __init__(self, config: dict):
        self._handlers: dict[str, list[ChainHandler]] = {}
        self._config = config
        self._max_cascade_depth = 5

    def register(self, event_type: str, handler: ChainHandler):
        """Register a handler for an event type."""
        self._handlers.setdefault(event_type, []).append(handler)

    async def dispatch(self, event: Event, depth: int = 0):
        """Dispatch event to all registered handlers."""
        if depth > self._max_cascade_depth:
            logger.warning("Chain cascade depth exceeded for %s", event.type)
            return

        handlers = self._handlers.get(event.type, [])
        for handler in handlers:
            if handler.should_fire(event, self._config):
                result = await handler.execute(event)
                # Handlers can emit new events (cascade)
                for new_event in result.emitted_events:
                    await self.dispatch(new_event, depth + 1)
```

### Registered Chains

**Stage Change Chains:**
```yaml
fleet.methodology.stage_changed:
  - handler: create_contribution_opportunities
    config:
      to_stage: reasoning
      contributions:
        - role: qa-engineer
          type: qa_test_definition
          required_for: [epic, story, task]
        - role: architect
          type: design_review
          required_for: [epic, story]
        - role: ux-designer
          type: ux_spec
          condition: "task has tag 'ui'"
        - role: devsecops-expert
          type: security_requirement
          required_for: [epic]

  - handler: notify_stage_change
    config:
      channels: [irc_fleet, board_memory]

  - handler: update_trail
    config:
      record: stage_transition
```

**Readiness Change Chains:**
```yaml
fleet.methodology.readiness_changed:
  - handler: checkpoint_notification
    config:
      at_values: [50]
      notify: [po_ntfy, irc_gates, board_memory]

  - handler: gate_enforcement
    config:
      at_values: [90]
      require: po_approval
      block_until_approved: true

  - handler: update_trail
    config:
      record: readiness_change
```

**Task Completion Chains:**
```yaml
fleet.task.completed:
  - handler: create_pr
  - handler: move_to_review
  - handler: create_approval
  - handler: notify_contributors
    config:
      notify_roles: [qa-engineer, architect, devsecops-expert]
  - handler: evaluate_parent
  - handler: update_sprint_progress
  - handler: update_trail
    config:
      record: task_completed
  - handler: phase_standards_check
    config:
      warn_on_gap: true
```

**Contribution Chains:**
```yaml
fleet.contribution.posted:
  - handler: propagate_to_target_task
    config:
      add_to_context: true
      notify_task_owner: true
  - handler: update_trail
    config:
      record: contribution_received
  - handler: check_contribution_completeness
    config:
      if_all_received: notify_pm
```

**Phase Chains:**
```yaml
fleet.phase.advance_requested:
  - handler: check_phase_standards
    config:
      block_if_not_met: true
  - handler: route_to_po
    config:
      channels: [ntfy, irc_gates, board_memory]
      tag: [gate, phase-advance, po-required]

fleet.phase.advanced:
  - handler: update_phase_labels
    config:
      sync_to_plane: true
  - handler: update_standards_context
    config:
      refresh_all_related_tasks: true
  - handler: notify_fleet
    config:
      channels: [irc_fleet, board_memory]
```

**Approval Chains:**
```yaml
fleet.approval.approved:
  - handler: transition_to_done
  - handler: notify_agent
  - handler: update_trail
  - handler: evaluate_parent

fleet.approval.rejected:
  - handler: regress_task
    config:
      set_status: in_progress
      regress_readiness: true  # based on rejection severity
  - handler: notify_agent_of_rejection
  - handler: update_trail
  - handler: doctor_signal
    config:
      if_repeat_rejection: flag_agent
```

### Chains Are TOOL CALL TREES — Not Side Effects

A chain is NOT "event → notification." A chain is a TREE of actual
function/tool calls that execute from a single agent-facing call.

When an agent calls `fleet_task_complete(summary)`, the system
executes this TREE of real calls:

```
fleet_task_complete(summary)
├── git.push(branch)                      # push code to remote
├── github.create_pr(branch, title, body) # create pull request
├── mc.update_task(board_id, task_id,     # update task fields
│     status="review",
│     custom_fields={pr_url, branch})
├── mc.post_comment(board_id, task_id,    # post completion summary
│     message=completion_summary)
├── mc.create_approval(board_id, task_id) # create approval object
├── plane_sync.update_issue(              # sync to Plane
│     workspace, project, issue_id,
│     status="review",
│     labels=["status:review"],
│     description_html=completion_html)
├── irc.send("#reviews",                  # notify IRC
│     f"[review needed] {title} by {agent}")
├── irc.send("#fleet",                    # fleet notification
│     f"[complete] {agent} finished {title}")
├── events.emit("fleet.task.completed",   # emit event
│     source, task_id, agent, summary)
├── mc.post_memory(board_id,              # trail event
│     content=trail_text,
│     tags=["trail", f"task:{id}"])
├── notify_contributors(task_id,          # notify QA, DevSecOps
│     roles=["qa-engineer", "devsecops"])
└── evaluate_parent(parent_task_id)       # check if parent done
    ├── mc.list_tasks(children)
    ├── if all done:
    │   ├── mc.update_task(parent, status="review")
    │   ├── mc.post_comment(parent, aggregate_summary)
    │   └── mc.create_approval(parent)
    └── else: update child count on parent
```

That's 12+ actual function calls from ONE agent action. The agent
calls ONE tool. The infrastructure executes a TREE. The agent
doesn't need to know the tree — they just know "I call
fleet_task_complete and everything happens."

This is the GROUP CALL concept. One agent-facing tool call maps to
a tree of internal operations. The brain orchestrates the tree.

### Every Agent Tool Has a Call Tree

Each tool in TOOLS.md should document not just "what happens" but
the actual call tree. Examples:

**fleet_commit(files, message):**
```
fleet_commit
├── git.add(files)
├── git.commit(message)           # conventional format
├── mc.post_comment(task_id, commit_summary)
├── plane_sync.update_issue(add_comment=commit_summary)
├── events.emit("fleet.task.commit")
└── mc.post_memory(trail_event)
```

**fleet_contribute(task_id, type, content):**
```
fleet_contribute
├── mc.post_comment(target_task_id,    # typed comment on target
│     message=contribution_content,
│     type=contribution_type)
├── plane_sync.update_issue(           # sync to Plane
│     add_comment=contribution_content)
├── context.update_task(target_task_id, # update target context
│     contributions={type: content})
├── mc.update_task(contribution_task,   # mark contribution done
│     status="done")
├── events.emit("fleet.contribution.posted")
├── mc.post_memory(trail_event)        # trail on target task
├── notify_task_owner(target_task_id)   # owner sees in heartbeat
└── check_contribution_completeness(target_task_id)
    └── if all_required_received:
        └── notify_pm("all contributions received for {task}")
```

**fleet_chat(message, mention):**
```
fleet_chat
├── mc.post_memory(board_id,
│     content=message,
│     tags=[f"mention:{mention}", "chat"])
├── irc.send("#fleet", f"<{agent}> {message}")
├── events.emit("fleet.chat.message")
└── if mention == "human":
    └── ntfy.send(title="Fleet chat", message=message)
```

The agent calls ONE tool. The tree does EVERYTHING. No manual
multi-step work by the agent. This is what makes the fleet
efficient — agents focus on COGNITION, the infrastructure handles
OPERATIONS.

### Group Call Architecture

The tool call tree is implemented as a group call executor:

```python
class ToolCallTree:
    """Executes a tree of operations from a single tool call."""

    def __init__(self, root_call: str):
        self.root = root_call
        self.operations: list[Operation] = []
        self.results: list[OperationResult] = []

    def add(self, operation: Operation, depends_on: list[str] = None):
        """Add an operation to the tree."""
        ...

    async def execute(self, context: dict) -> TreeResult:
        """Execute all operations respecting dependencies."""
        # Operations without dependencies run in parallel
        # Operations with dependencies wait for their parents
        # Failures are logged but don't break the tree
        # (degraded mode: some operations succeed, some fail)
        ...
```

Operations in the tree can run in PARALLEL when they don't depend
on each other. For example, in fleet_task_complete:
- mc.post_comment and irc.send can run in parallel
- mc.create_approval depends on mc.update_task completing
- plane_sync depends on mc.update_task completing
- evaluate_parent depends on mc.create_approval completing

### Chain Configuration

Chains are defined in `config/chains.yaml` and loaded by the brain
at startup. Adding a new chain is a config change — no code needed
for standard patterns. Custom handlers require code but follow a
standard interface.

```python
class ChainHandler:
    """Base class for chain handlers."""

    name: str

    def should_fire(self, event: Event, config: dict) -> bool:
        """Evaluate whether this handler should fire for this event."""
        ...

    async def execute(self, event: Event) -> ChainResult:
        """Execute the handler. Returns result with optional new events."""
        ...
```

---

## Layer 3: The Logic Engine

The logic engine evaluates complex multi-condition decisions. The
biggest one is dispatch readiness.

### Dispatch Decision

For each task in inbox with status ready for dispatch:

```python
async def should_dispatch(
    task: Task,
    agent: Agent,
    doctor_report: DoctorReport,
    fleet_state: FleetControlState,
    contributions: dict,
    phase_config: dict,
) -> tuple[bool, str]:  # (can_dispatch, reason_if_not)

    # Gate 1: Fleet mode allows dispatch?
    if not fleet_should_dispatch(fleet_state):
        return False, f"Fleet mode {fleet_state.work_mode} blocks dispatch"

    # Gate 2: Agent is active for current cycle phase?
    active_agents = get_active_agents_for_phase(fleet_state.cycle_phase)
    if agent.name not in active_agents:
        return False, f"Agent not active in {fleet_state.cycle_phase} phase"

    # Gate 3: Task is unblocked?
    if task.is_blocked:
        return False, f"Blocked by {task.blocked_by_task_ids}"

    # Gate 4: Agent is online?
    if agent.status != "online":
        return False, "Agent offline"

    # Gate 5: Agent is not busy?
    if agent_has_in_progress_task(agent.name, tasks):
        return False, "Agent busy with another task"

    # Gate 6: Doctor hasn't flagged this agent?
    if agent.name in doctor_report.agents_to_skip:
        return False, "Doctor: agent flagged (teaching/pruned)"

    # Gate 7: Task readiness appropriate for stage?
    if task.custom_fields.task_stage == "work" and task.custom_fields.task_readiness < 99:
        return False, f"Work stage requires readiness >= 99, has {task.custom_fields.task_readiness}"

    # Gate 8: PO gate passed? (readiness 90% gate)
    if task.custom_fields.task_readiness >= 90:
        if not po_gate_approved(task, gate="readiness_90"):
            return False, "PO gate at 90% not approved"

    # Gate 9: Required contributions received?
    phase = task.custom_fields.delivery_phase or "ideal"
    required = get_required_contributions(task, phase)
    received = get_received_contributions(task, contributions)
    missing = required - received
    if missing and task.custom_fields.task_stage == "work":
        return False, f"Missing contributions for work stage: {missing}"

    # Gate 10: Phase standards met for current work?
    if phase != "ideal":
        standards_ok, gaps = check_phase_prerequisites(task, phase)
        if not standards_ok:
            return False, f"Phase {phase} prerequisites not met: {gaps}"

    return True, "All gates passed"
```

10 gates. Each one is a deterministic check. No AI needed. The brain
evaluates all of them for each candidate task, and only dispatches
tasks that pass ALL gates.

### Autocomplete Chain Builder

When a task passes all gates and is ready for dispatch, the brain
builds the autocomplete chain for the target agent:

```python
async def build_autocomplete_chain(
    task: Task,
    agent: Agent,
    contributions: dict,
    phase_config: dict,
    role_config: dict,
) -> str:
    """Build the engineered autocomplete chain for agent dispatch.

    The chain flows:
    1. Identity (who you are)
    2. Task context (what you're working on)
    3. Stage protocol (what to do in this stage)
    4. Contributions (what your colleagues provided)
    5. Phase standards (what quality level applies)
    6. Action directive (what to do NOW)
    7. Tool chain documentation (what happens when you call tools)
    """
    cf = task.custom_fields
    stage = cf.task_stage or "reasoning"
    phase = cf.delivery_phase or "ideal"

    sections = []

    # 1. Identity grounding
    sections.append(f"# YOU ARE: {agent.name} ({role_config.get('display', agent.name)})")
    sections.append(f"# YOUR TASK: {task.title}")
    sections.append(f"# YOUR STAGE: {stage}")
    sections.append(f"# READINESS: {cf.task_readiness}%")
    sections.append("")

    # 2. Verbatim requirement (the anchor)
    if cf.requirement_verbatim:
        sections.append("## VERBATIM REQUIREMENT")
        sections.append(f"> {cf.requirement_verbatim}")
        sections.append("")

    # 3. Stage protocol (what to do)
    from fleet.core.stage_context import get_stage_instructions
    instructions = get_stage_instructions(stage)
    if instructions:
        sections.append(instructions)
        sections.append("")

    # 4. Contributions from colleagues
    if contributions:
        sections.append("## INPUTS FROM YOUR COLLEAGUES")
        for role, contrib in contributions.items():
            sections.append(f"### {role} ({contrib.get('type', 'input')})")
            sections.append(f"{contrib.get('content', '')}")
        sections.append("")

    # 5. Phase standards
    if phase != "ideal":
        from fleet.core.phases import get_phase_standards
        standards = get_phase_standards(phase)
        sections.append(f"## DELIVERY PHASE: {phase.upper()}")
        sections.append(f"{phase.upper()} standards apply:")
        for key, value in standards.items():
            sections.append(f"- {key}: {value}")
        sections.append("")

    # 6. Action directive
    sections.append("## WHAT TO DO NOW")
    sections.append(get_action_directive(stage, phase, cf))
    sections.append("")

    # 7. Chain documentation
    sections.append("## WHAT HAPPENS WHEN YOU ACT")
    sections.append(get_chain_documentation(stage))

    return "\n".join(sections)
```

This is the ENGINEERED autocomplete chain. Not a data dump — a
structured flow from identity → requirement → protocol → inputs →
standards → action → consequences. The AI reads this and the correct
action is the natural continuation.

---

## Deterministic vs AI — The Complete Split

### What the Brain Handles (No AI)

| Action | Why No AI |
|--------|-----------|
| Task status transitions (inbox → in_progress) | Just a field update |
| Creating contribution opportunity tasks | Rule: "reasoning stage + story type → create QA task" |
| Parent task evaluation (all children done → review) | Just counting |
| Approval creation (review task → approval object) | Just a record |
| Sprint progress calculation | Math |
| Readiness gate enforcement (90% → require PO) | Comparison |
| Phase standards checking | Checklist evaluation |
| Comment propagation (child → parent) | Copy + format |
| Event emission and chain dispatch | Rule execution |
| Context refresh (write pre-embed files) | Template rendering |
| Driver waking (PM/fleet-ops activation) | Timer + condition check |
| Trail recording (stage transitions, approvals) | Append to log |
| Plane sync (labels, descriptions) | API calls |
| Mode change detection | Comparison |
| Budget monitoring | Math |
| Health checks (stuck tasks, offline agents) | Timer + state check |

### What Agents Handle (AI Required)

| Action | Why AI |
|--------|--------|
| Analyzing a codebase | Requires reading and comprehension |
| Designing architecture | Requires creative reasoning |
| Writing implementation code | Requires programming skill |
| Reviewing work against requirements | Requires understanding intent |
| Breaking down an epic into subtasks | Requires understanding scope |
| Answering PO questions about tradeoffs | Requires domain knowledge |
| Writing documentation | Requires explaining concepts |
| Predefining tests | Requires understanding behavior |
| Security auditing code | Requires pattern recognition |
| Resolving merge conflicts | Requires code understanding |
| Producing analysis/investigation documents | Requires research synthesis |
| Evaluating plan against verbatim requirement | Requires semantic comparison |

The rule: if it can be expressed as "if X then Y" — the brain does it.
If it requires reading, understanding, creating, or evaluating — an
agent does it. Every chain that fires without AI saves tokens.

---

## Cross-Task Propagation

The brain handles data flow between related tasks:

### Child → Parent Propagation
When a child task gets a comment, completion, or artifact:
- Brain reads the update
- Brain formats a summary for the parent
- Brain posts the summary as a comment on the parent
- Parent's context is updated with child status

Example: DevOps completes "Implement CI config" (child of "Add CI/CD
to NNRT" epic). Brain posts on the epic: "Child completed: Implement
CI config. PR: #42. Summary: GitHub Actions workflow for lint + test.
Status: 3/5 children done."

### Contribution → Target Propagation
When QA posts a test definition on a contribution task:
- Brain reads the contribution artifact
- Brain adds it to the target task's contribution data
- Target task's context is updated to include QA's tests
- Target task's owner is notified

### Transfer → Receiving Agent Propagation
When a task transfers from architect to engineer:
- Brain packages the architect's contributions (design plan, constraints)
- Brain writes the package into the engineer's task context
- Engineer's pre-embed includes: "INPUTS FROM YOUR COLLEAGUES: architect
  provided design plan, target files, approach."

All of this is deterministic. The brain reads structured data and moves
it. No AI comprehension needed.

---

## Notification Routing Matrix

The brain routes notifications to the correct buses. Each event type
has a routing configuration:

```yaml
# config/notifications.yaml

routing:
  fleet.task.dispatched:
    - bus: irc
      channel: "#fleet"
      format: "[dispatch] {agent} → {task_title} ({stage})"
    - bus: board_memory
      tags: [dispatch, task:{task_id}]

  fleet.task.completed:
    - bus: irc
      channel: "#fleet"
      format: "[complete] {agent} finished {task_title}"
    - bus: irc
      channel: "#reviews"
      format: "[review needed] {task_title} by {agent}"
    - bus: board_memory
      tags: [completion, task:{task_id}]

  fleet.methodology.stage_changed:
    - bus: irc
      channel: "#fleet"
      format: "[stage] {task_title}: {from_stage} → {to_stage}"
    - bus: board_memory
      tags: [methodology, stage-change, task:{task_id}]

  fleet.gate.requested:
    - bus: irc
      channel: "#gates"
      format: "[gate] {gate_type} on {task_title} — PO approval needed"
    - bus: ntfy
      title: "Gate: {gate_type}"
      message: "{summary}"
      priority: high
    - bus: board_memory
      tags: [gate, po-required, task:{task_id}]

  fleet.phase.advanced:
    - bus: irc
      channel: "#fleet"
      format: "[phase] {task_title}: {from_phase} → {to_phase}"
    - bus: irc
      channel: "#sprint"
      format: "[milestone] {task_title} advanced to {to_phase}"
    - bus: board_memory
      tags: [phase, milestone, task:{task_id}]

  fleet.contribution.posted:
    - bus: irc
      channel: "#contributions"
      format: "[contribute] {role} → {task_title}: {contribution_type}"
    - bus: board_memory
      tags: [contribution, task:{task_id}]

  fleet.immune.disease_detected:
    - bus: board_memory
      tags: [immune-system, detection]
    # NOT in agent feeds — hidden

  fleet.approval.rejected:
    - bus: irc
      channel: "#reviews"
      format: "[rejected] {task_title}: {reason}"
    - bus: board_memory
      tags: [review, rejection, task:{task_id}]

  fleet.security.alert:
    - bus: irc
      channel: "#alerts"
      format: "[SECURITY] {severity}: {title}"
    - bus: ntfy
      title: "Security: {title}"
      priority: urgent
    - bus: board_memory
      tags: [security, alert]
```

The brain reads this config and routes every event to the right buses.
Agents don't need to know the routing — they emit events via their
tool calls, the brain handles distribution.

---

## Contribution Opportunity Creation

One of the brain's most important new functions: creating contribution
opportunities based on task state.

### When Contributions Are Created

The brain checks contribution rules from config every cycle:

```python
async def _create_contribution_opportunities(
    self, task: Task, config: dict
) -> list[Task]:
    """Create contribution tasks for a task based on stage/phase rules."""
    created = []
    stage = task.custom_fields.task_stage
    phase = task.custom_fields.delivery_phase or "ideal"
    task_type = task.custom_fields.task_type or "task"

    rules = config.get("contributions", {}).get(stage, [])

    for rule in rules:
        # Check if this task type needs this contribution
        if task_type not in rule.get("required_for", []):
            continue

        # Check conditions (e.g., "task has tag 'ui'")
        if rule.get("condition") and not evaluate_condition(rule["condition"], task):
            continue

        # Check if contribution already exists
        if contribution_exists(task.id, rule["role"], rule["type"]):
            continue

        # Check if phase requires this contribution
        phase_contribs = get_phase_contributions(phase)
        if rule["role"] not in phase_contribs:
            continue

        # Create the contribution task
        contrib_task = await mc.create_task(
            board_id=task.board_id,
            title=f"[{rule['type']}] {task.title}",
            description=f"Contribute {rule['type']} for: {task.title}\n"
                        f"Verbatim: {task.custom_fields.requirement_verbatim}\n"
                        f"Phase: {phase} — {phase} standards apply",
            agent_name=rule["role"],
            custom_fields={
                "task_type": "subtask",
                "parent_task": task.id,
                "contribution_type": rule["type"],
                "contribution_target": task.id,
                "delivery_phase": phase,
                "task_stage": "reasoning",  # contributor reasons about what to contribute
                "task_readiness": 50,  # clear what to do, just needs to do it
            },
            auto_created=True,
            auto_reason=f"Brain: {rule['type']} contribution for {task.id[:8]}",
        )
        created.append(contrib_task)

    return created
```

### Contribution Task Lifecycle

1. Brain creates contribution task → assigned to role agent → inbox
2. Orchestrator dispatches when agent is available
3. Agent produces contribution artifact (QA: test_definition, architect:
   design_review, etc.)
4. Agent calls fleet_contribute() or fleet_task_complete()
5. Chain fires: contribution propagated to target task
6. Target task's context updated with new contribution
7. If all required contributions received → PM notified → task can
   advance

Contribution tasks are SMALL. QA predefining tests for one task is
a focused micro-task — one heartbeat cycle, one artifact. It doesn't
consume a full agent session for long. This keeps budget manageable.

---

## Trail System Integration

The brain records every significant event in a task's trail:

```python
async def record_trail_event(
    task_id: str,
    event_type: str,  # "stage_transition", "contribution_received",
                       # "approval_decision", "po_gate", "phase_advance"
    data: dict,
):
    """Record a trail event in board memory with task tag."""
    content = format_trail_event(event_type, data)
    tags = ["trail", f"task:{task_id}", event_type]
    if data.get("agent"):
        tags.append(f"agent:{data['agent']}")
    await mc.post_memory(board_id, content, tags=tags)
```

The trail is reconstructable from board memory by filtering on
`trail` + `task:{id}` tags. The accountability generator reads these
to produce compliance reports.

---

## Brain Configuration

```yaml
# config/brain.yaml

cycle:
  interval: 30  # seconds between cycles
  max_dispatch_per_cycle: 2
  max_cascade_depth: 5  # chain event cascade limit

dispatch:
  gates:
    - fleet_mode_allows
    - agent_active_for_phase
    - task_unblocked
    - agent_online
    - agent_not_busy
    - doctor_cleared
    - readiness_appropriate
    - po_gate_passed
    - contributions_received
    - phase_prerequisites_met

  priority_order: [urgent, high, medium, low]

drivers:
  agents: [project-manager, fleet-ops]
  wake_interval: 1800  # seconds
  wake_conditions:
    project-manager:
      - unassigned_tasks_in_inbox
      - sprint_needs_attention
    fleet-ops:
      - pending_approvals_exist
      - review_tasks_stale

propagation:
  child_to_parent:
    on_comment: summarize_and_post
    on_completion: aggregate_and_post
    on_artifact: reference_on_parent
  contribution_to_target:
    on_complete: add_to_target_context

autocomplete:
  chain_order:
    - identity
    - verbatim_requirement
    - stage_protocol
    - colleague_contributions
    - phase_standards
    - action_directive
    - chain_documentation
```

---

## Interaction with Other Systems

### Brain ↔ Immune System
- Brain runs the doctor as Step 2
- Doctor report feeds dispatch decisions (skip list)
- Brain executes interventions (prune, compact, teach via gateway)
- Brain records doctor detections in board memory (hidden from agents)

### Brain ↔ Teaching System
- When doctor triggers teaching, brain calls adapt_lesson()
- Brain injects lesson into agent session via gateway
- Brain monitors teaching outcomes (comprehension verified / no change)
- After max attempts without change → brain triggers prune

### Brain ↔ Methodology System
- Brain reads task_stage and task_readiness for dispatch decisions
- Brain enforces stage-appropriate dispatch (work stage needs readiness 99+)
- Brain fires chains on stage transitions
- Brain records stage transitions in trail

### Brain ↔ Phase System
- Brain reads delivery_phase for standards application
- Brain enforces phase gates (PO approval for advancement)
- Brain creates phase-appropriate contribution opportunities
- Brain applies phase-aware work modes

### Brain ↔ Event Bus
- Brain is the primary event dispatcher
- Brain registers chain handlers at startup
- Brain processes event queue at start of each cycle
- Brain controls cascade depth

### Brain ↔ Context System
- Brain calls build_heartbeat_preembed for context refresh
- Brain calls build_autocomplete_chain for dispatch
- Brain writes to agents/{name}/context/ files every cycle
- Brain reads from context assembly for dispatch decisions

### Brain ↔ Session Management (NEW — 2026-04-01)

PO requirement (verbatim):
> "its not just about waiting when the current session limite is use
> at 90% but also preparing at 85%, in a similar fasion as the end
> game strategy to not lose work but at the same time to compact not
> to create huge spike of cost"

> "for every milestones remain we will need to ask ourselves these
> kind of question and revise everything of the logic that will make
> this fleet amazing and unstopable with good outputs"

- Brain tracks TWO parallel countdowns:
  1. Context remaining per agent (organic awareness: 7%/5% remaining)
  2. Rate limit session usage fleet-wide (awareness: 85%/90% used)
- Brain knows each agent's context size and calculates aggregate:
  5 × 200K = 1M tokens on rollover. 2 × 1M = 2M. This math matters.
- Brain factors distance to rate limit window rollover
- At 85% used: progressive awareness, don't dispatch expensive work
- At 90% used: organic preparation — agents extract to artifacts
  Allow going over 90% for the compacting itself (saves more than costs)
- Near rollover: evaluate each agent — does it NEED its context?
  Over ~40-80K with no predicted upcoming job → dump to artifacts
  Unrelated next work → fresh session, no re-injection
  Related next work → synthesised re-injection later
- DO NOT dispatch 1M context quests near rollover
- Force compact IS appropriate near rollover for heavy contexts
  (the agent prepares, but the brain ultimately decides)
- After rollover: put agents back on track with fresh or re-injected
  sessions as appropriate
- Feeds: session telemetry (real data), budget monitor (quota %),
  agent lifecycle (context levels), work modes (cost constraints)
- Cross-ref: System 22 §4.7 (rate limit session cycle awareness)

### Brain ↔ Gateway
- Brain reads agent status from gateway (online/offline)
- Brain injects content into sessions (teaching, waking)
- Brain prunes sessions (immune system response)
- Brain creates fresh sessions (after prune)
- Brain does NOT create heartbeats (gateway handles that)

### Brain ↔ Plane Sync
- Brain triggers Plane sync for phase label updates
- Brain reads Plane changes (new issues, priority changes)
- Brain propagates Plane data to OCMC tasks

### Brain ↔ Standards Library
- Brain calls check_standard with phase context for completion checks
- Brain uses standards to evaluate phase advancement readiness
- Brain reports standards gaps to PM

---

## What Changes in the Existing Orchestrator

The existing `fleet/cli/orchestrator.py` needs to evolve:

### New modules to create:
- `fleet/core/chain_registry.py` — event → handler mapping
- `fleet/core/chain_handlers.py` — standard handler implementations
- `fleet/core/logic_engine.py` — multi-condition dispatch evaluation
- `fleet/core/autocomplete.py` — autocomplete chain builder
- `fleet/core/trail.py` — trail recording and retrieval
- `fleet/core/propagation.py` — cross-task data propagation
- `fleet/core/contributions.py` — contribution opportunity management

### Orchestrator changes:
- Import and initialize ChainRegistry
- Add Step 1 (event queue processing)
- Add Step 3 (gate processing)
- Add Step 4 (contribution management)
- Add Step 9 (cross-task propagation)
- Refactor Step 5 (dispatch) to use logic engine
- Refactor context refresh to use autocomplete chain builder
- Add trail recording calls throughout

### Config changes:
- `config/chains.yaml` — chain definitions
- `config/brain.yaml` — brain configuration
- `config/notifications.yaml` — routing matrix
- `config/fleet.yaml` — contribution rules, phase config additions

---

## Testing Requirements

### Chain Registry Tests
- Event dispatched → correct handlers fire
- Handler conditions evaluated correctly
- Cascade depth limit enforced
- Config-driven chain definitions load correctly

### Logic Engine Tests
- All 10 dispatch gates evaluated correctly
- Gate failure returns specific reason
- Phase-aware dispatch decisions
- Contribution-aware dispatch decisions

### Autocomplete Chain Tests
- Chain built correctly for each role × stage combination
- Contributions included when available
- Phase standards included
- Action directive matches stage protocol

### Propagation Tests
- Child comment → parent summary
- Contribution → target task context
- Transfer → receiving agent context
- Trail events recorded correctly

### Contribution Tests
- Contribution opportunities created at correct stage
- Only created when required by config
- Phase-aware contribution requirements
- Duplicate contribution prevention

### Integration Tests
- Full cycle: task created → contributions → dispatch → complete → review
- Phase advancement: POC → MVP with all gates and chains
- Regression: PO regresses → correct state, correct notifications
- Multi-agent synergy: architect + QA + engineer on one task

---

## Gateway Executor — System Prompt Ordering

The gateway at `gateway/executor.py` builds the agent's system prompt
from their files. The ORDER of injection matters for autocomplete chain
effectiveness — rules near the start of context have more influence
than rules buried in the middle (Lost in the Middle effect).

### Required Injection Order

```
1. IDENTITY.md    — "I am the architect for Fleet Alpha."
                     Grounds the AI's identity. Every token generated
                     FROM this identity.

2. SOUL.md        — "I value design before implementation."
                     Sets behavioral boundaries early.

3. CLAUDE.md      — "Role-specific rules: you produce analysis and
                     investigation artifacts, your plans reference
                     verbatim requirements."
                     Role-specific methodology and constraints.

4. TOOLS.md       — "Available tools with chain documentation."
                     What the AI CAN do and what each action triggers.

5. AGENTS.md      — "Your colleagues: PM dispatches, QA predefines
                     tests, engineers implement your designs."
                     Fleet awareness and synergy knowledge.

6. context/       — "Fleet state, task data, autocomplete chain."
   fleet-context.md  Dynamic fleet awareness.
   task-context.md   Current work with engineered autocomplete chain.

7. HEARTBEAT.md   — "What to do now."
                     The action prompt that the AI autocompletes from.
```

The order creates a funnel: identity → values → rules → capabilities
→ team → state → task → action. Each layer narrows the AI's response
space. By the time it reaches the action prompt, there's a narrow
band of correct responses.

### Changes Needed in gateway/executor.py
- Current: reads files in directory order or alphabetically
- Needed: explicit injection order controlled by configuration
- The executor should read a file order config and inject accordingly
- Anti-corruption rules (in CLAUDE.md) are injected at position 3 —
  early enough to have maximum effect

---

## Error Recovery and Resilience

### Agent Session Crashes
- Gateway detects session death
- Next orchestrator cycle: agent has in_progress task, no session
- Brain creates fresh session via gateway
- Agent's context/task-context.md still has progress (artifacts,
  comments, completeness state)
- Agent picks up from persistent artifacts
- Trail: "Session interrupted, recovered at {completeness}%"

### Orchestrator Crashes
- Daemon system restarts it
- Persistent state is in MC (tasks, comments, approvals) and agent
  files (context/) — not in orchestrator memory
- Health profiles reset (doctor loses history — acceptable, fresh
  observation)
- Chain registry reloads from config
- No data loss — MC is source of truth

### MC Backend Down
- Orchestrator can't read tasks or agents
- Cycle skips — no dispatch, no evaluation
- Agents already in-progress continue (have their context)
- When MC returns, orchestrator resumes
- Alert to PO via ntfy: "MC backend unreachable"

### Plane Down
- Transpose can't sync artifacts to Plane
- Artifacts still exist in OCMC task data
- Sync queue accumulates
- When Plane returns, backlog processed
- Agent work continues — Plane is display, not source of truth

### Gateway Down
- No agent sessions — fleet is dark
- Orchestrator cycles but can't dispatch (no agents online)
- All in-progress work preserved in task data and context files
- When gateway returns, agents come online, orchestrator dispatches

### Chain Cascade Failure
- Event handler creates event → handler → event → infinite loop
- Cascade depth limit (max 5 levels) prevents runaway
- If depth exceeded: log error, stop cascade, alert fleet-ops
- Partial chain execution: some effects applied, others not
- Recovery: next cycle re-evaluates state, catches anything missed

### Bad Agent Output
- Doctor detects disease → teaching or prune
- After prune: agent regrows fresh, picks up from persistent data
- If still bad after regrow → escalate to PO
- Fleet doesn't try to fix what it can't fix — it escalates

---

## Board Memory Organization

Board memory is the fleet's shared knowledge store. Organized by tags:

### Tag Convention

```
Type tags (what it is):
  directive       — PO order
  decision        — strategic decision with rationale
  chat            — inter-agent message
  event           — system event record
  report          — periodic report
  trail           — task lifecycle event
  gate            — gate request or decision

Subject tags (what it's about):
  task:{task_id}  — related to specific task
  agent:{name}    — related to specific agent
  sprint:{id}     — related to specific sprint
  mention:{name}  — directed at specific agent

System tags (which system):
  immune-system   — doctor detections and responses
  teaching-system — lesson deliveries and outcomes
  methodology     — stage transitions and protocol events
  security        — security alerts and reviews
  architecture    — design decisions
  infrastructure  — infrastructure health
  compliance      — accountability findings
  quality         — quality observations

Priority tags:
  po-required     — needs PO attention
  urgent          — time-sensitive
  escalation      — escalated issue
```

### How Agents Find What They Need
- PM: filters by `mention:project-manager` + `directive`
- Fleet-ops: filters by `immune-system` + `quality`
- Any agent: filters by `mention:{self}` + `chat`
- Accountability: filters by `trail` + `task:{id}`
- PO: filters by `po-required` + `gate`

### Retention
- Directives: persist until superseded
- Decisions: persist indefinitely
- Chat: persist for current sprint
- Events: persist for 2 sprints
- Trails: persist indefinitely (audit requirement)
- Reports: persist for 3 sprints

---

## IRC Channel Structure

```
#fleet          — general activity. Dispatches, completions, stage
                  changes. High volume, low urgency.

#alerts         — security alerts, immune detections, budget warnings,
                  infrastructure failures. Low volume, HIGH urgency.
                  PO must see these.

#reviews        — tasks entering review, approval decisions, rejection
                  feedback. Fleet-ops and PO monitor.

#gates          — gate requests and PO decisions. "Task X at readiness
                  90%, PO approval needed." PO action channel.

#contributions  — contribution activity. "QA predefined tests for
                  task X." Synergy visibility.

#sprint         — sprint-level activity. Velocity, summaries, phase
                  advancements. PM posts, PO reviews periodically.
```

Each event type routes to specific channels via the notification
routing matrix in config. Agents know which channel to watch.

---

## MCP Tool Evolution

### Current Tools (25) — What Changes

**Tools that need tree upgrades (existing → expanded tree):**

| Tool | Current Behavior | Elevated Tree |
|------|-----------------|---------------|
| fleet_task_complete | push, PR, update status | + plane_sync, trail, contributors notify, parent eval, sprint update |
| fleet_commit | git commit, comment | + plane_sync comment, trail event, methodology check |
| fleet_chat | board memory, IRC | + typed routing, mention tagging, ntfy if @human |
| fleet_alert | IRC, board memory | + ntfy for high/critical, trail event, event emit |
| fleet_task_accept | store plan | + methodology check, plan vs verbatim check, event emit |
| fleet_read_context | return task data | + include contributions, phase standards, autocomplete chain |
| fleet_artifact_create | create + transpose | + phase-aware completeness, readiness suggestion, trail |
| fleet_artifact_update | update + transpose | + re-check completeness, readiness re-suggestion |

**New tools needed:**

| Tool | Purpose | Tree |
|------|---------|------|
| fleet_contribute | Agent contributes to another's task | mc.comment(typed), plane_sync, context.update target, complete contribution task, events, trail, notify owner, check all contributions received |
| fleet_request_input | Request specific role's input | mc.memory(mention), irc, events, contribution task check |
| fleet_transfer | Transfer task to another agent | mc.update agent_name, package context, write target context, events, trail, irc, notify receiving agent |
| fleet_gate_request | Request PO approval at gate | mc.memory(tags: gate, po-required), irc #gates, ntfy to PO, events, trail |
| fleet_phase_advance | Request phase advancement | check phase standards, mc.memory(gate), ntfy, irc, events, trail |

**Tools that stay largely the same:**
- fleet_escalate (already has ntfy + IRC + board memory)
- fleet_task_create (needs + auto_created flag, + contribution_type fields)
- fleet_agent_status (read-only, no tree changes)

### Total Tools After Elevation: ~30

Current 25 + 5 new = 30. Each with a documented call tree.
The MCP server registration needs to handle 30 tools with proper
parameter validation and stage-awareness checks.

---

## Complete Event Type Registry

### Current Events (16 types)

```
fleet.immune.disease_detected
fleet.immune.agent_pruned
fleet.immune.agent_compacted
fleet.immune.rule_injected
fleet.immune.health_report
fleet.teaching.lesson_started
fleet.teaching.practice_attempted
fleet.teaching.comprehension_verified
fleet.teaching.comprehension_failed
fleet.teaching.agent_lesson_cleared
fleet.teaching.escalated_to_prune
fleet.methodology.stage_changed
fleet.methodology.readiness_changed
fleet.methodology.protocol_violation
fleet.methodology.checkpoint_reached
fleet.methodology.stage_context_loaded
```

### New Events Needed

```
# Task lifecycle
fleet.task.created
fleet.task.assigned
fleet.task.dispatched
fleet.task.commit
fleet.task.completed
fleet.task.transferred
fleet.task.done

# Review chain
fleet.review.started
fleet.review.qa_validated
fleet.review.security_completed
fleet.review.architecture_checked
fleet.approval.approved
fleet.approval.rejected

# Contributions
fleet.contribution.opportunity_created
fleet.contribution.posted
fleet.contribution.propagated
fleet.contribution.all_received

# Gates
fleet.gate.requested
fleet.gate.decided
fleet.gate.timeout_warning

# Phases
fleet.phase.advance_requested
fleet.phase.advanced
fleet.phase.advance_rejected
fleet.phase.regressed
fleet.phase.standards_checked

# Governance
fleet.methodology.readiness_regressed
fleet.po.directive_posted
fleet.po.gate_approved
fleet.po.gate_rejected

# System
fleet.system.mode_changed          (already exists)
fleet.system.cycle_completed
fleet.system.health_check
fleet.system.budget_warning

# Fleet
fleet.chat.message
fleet.sprint.progress_updated
fleet.sprint.report_generated
```

### Total Events After Elevation: ~50+

Each event has:
- Event type (string, dot-separated namespace)
- Source (which module/tool emitted it)
- Subject (which task, if applicable)
- Data (event-specific payload)
- Timestamp

Each event routes through the chain registry (handlers fire) AND
the notification router (IRC/ntfy/board memory). The routing matrix
in config maps each event type to its channels.

---

## Orchestrator Cycle ↔ Gateway Heartbeat Interaction

### Two Independent Cycles

```
ORCHESTRATOR CYCLE (every 30s):
  Runs in the fleet daemon process.
  Reads MC state, runs brain logic, writes context/ files.
  Does NOT create agent sessions.
  Does NOT trigger heartbeats.

GATEWAY HEARTBEAT (per-agent interval, e.g. every 10m):
  Runs in the OpenClaw gateway process.
  Creates/continues Claude Code session for the agent.
  Reads the agent's files (IDENTITY, SOUL, CLAUDE, TOOLS, context/).
  Builds system prompt from files.
  Agent wakes up, reads pre-embedded data, follows HEARTBEAT.md.

INTERACTION:
  Orchestrator writes context/ files → gateway reads them when
  heartbeat fires → agent gets fresh data.

  Agent calls MCP tools → tools emit events → events queued →
  next orchestrator cycle processes event queue.
```

The two cycles are INDEPENDENT. The orchestrator doesn't know when
heartbeats fire. The gateway doesn't know when orchestrator cycles run.
They communicate through FILES (context/) and EVENTS (event queue).

### Why This Matters

- The orchestrator can run 30s cycles without waking any agent
  (context refresh only)
- Agents wake on their own schedule (gateway-controlled)
- An agent's heartbeat gets FRESH data because the orchestrator
  just wrote it (at most 30s stale)
- Agent actions (MCP tool calls) queue events for the next cycle
- The brain processes those events and fires chains DETERMINISTICALLY
- No AI needed for chain execution — it all happens in the orchestrator

### What the Orchestrator NEVER Does
- Create Claude Code sessions (gateway does this)
- Directly invoke agents (gateway heartbeat does this)
- Run AI inference (agents do this via gateway)
- Process agent conversations (gateway session handles this)

The orchestrator is PURE LOGIC. No AI. Just data reading, rule
evaluation, file writing, API calls. That's why it's the BRAIN —
deterministic, reliable, fast.

---

## Open Questions

- Should the chain registry support priority ordering of handlers?
  (Some handlers must run before others — e.g., log before act)
- Should the event queue persist across orchestrator restarts?
  (Currently lost — acceptable if MC is source of truth)
- How do we handle chains that fail partway through?
  (Partial execution — some side effects applied, others not)
- Should the autocomplete chain be cached per agent between cycles?
  (If task/stage/phase/contributions haven't changed, skip rebuild)
- How does the brain handle concurrent MCP calls from multiple agents?
  (Events queued, processed in order next cycle — acceptable latency?)
- Should contribution opportunity creation be configurable per
  project/module, not just globally? (Different projects have different
  contribution needs)