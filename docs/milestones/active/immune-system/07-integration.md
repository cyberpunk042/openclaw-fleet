# Integration — How the Immune System Connects to the Fleet

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Part of:** Fleet Immune System (document 7 of 7)

---

## PO Requirements (Verbatim)

> "we will need a series of evolutions for the immune system and the brain
> and orchestrator."

> "This is going to be 2000+ hours of work and its an entire system in
> the program."

---

## What Integration Means

The immune system doesn't exist in isolation. It needs to connect to
every part of the fleet — the orchestrator, the gateway, the event bus,
the agents, the MCP tools, the task lifecycle, the communication
surfaces. It's an entire system IN the program, not bolted on.

---

## Plane State as Data Source

The immune system needs data from Plane to function. Plane tracks state,
assignees, start dates, due dates, priority, estimates, cycles, modules.
This data enables detection:

- **Start date + no progress** → stuck/spinning detection
- **High estimate + fast completion** → laziness detection
- **State changes without methodology checks** → protocol violation
- **Assignee changes** → track who worked on what, disease per agent

The sync worker must keep Plane state and OCMC state in parallel. The
new custom fields (task_readiness, requirement_verbatim, task_stage)
must exist on both platforms and stay synchronized.

---

## Technical Interfaces

The immune system has specific interfaces with each fleet component.
These are the actual integration points that need to be built.

### Orchestrator → Doctor (fleet/cli/orchestrator.py → fleet/core/doctor.py)

The orchestrator runs every 30s. The doctor runs as a step in this cycle.

```
Orchestrator Cycle:
  Step 1: Read fleet control state (mode, phase, backend)
  Step 2: DOCTOR — observe all active agents and tasks
  Step 3: Process approvals
  Step 4: Transition reviewed tasks
  Step 5: Dispatch new tasks (respecting doctor decisions)
  Step 6: Evaluate parent tasks
  Step 7: Wake idle drivers
```

The doctor at Step 2 produces decisions that Step 5 respects:
- Don't dispatch to agent currently being pruned
- Don't dispatch to agent currently in a lesson
- Don't dispatch work tasks if readiness < 99
- Flag agents that need intervention

Interface:
```python
# Doctor produces a DoctorReport each cycle
@dataclass
class DoctorReport:
    agents_to_skip: list[str]      # Don't dispatch to these
    tasks_to_block: list[str]      # Don't dispatch these
    interventions: list[Intervention]  # Actions to take
    health_summary: dict           # Per-agent health status

# Orchestrator calls doctor
report = await run_doctor_cycle(mc, board_id, config)
# Orchestrator uses report in dispatch
skip_agents = report.agents_to_skip
```

### Doctor → Gateway (fleet/core/doctor.py → gateway RPC)

The doctor uses the gateway's existing session APIs:

| Action | Gateway API | Purpose |
|--------|-----------|---------|
| Prune | `sessions.delete(key)` | Kill sick session |
| Force compact | `sessions.compact(key)` | Reduce context |
| Inject lesson | `chat.send(sessionKey, message)` | Rules reinjection |
| Fresh session | `sessions.patch(key, label)` | Regrowth after prune |

Interface:
```python
# Fleet wrapper around gateway RPC (fleet/infra/gateway_client.py)
async def prune_agent(agent_name: str) -> bool
async def compact_agent(agent_name: str) -> bool
async def inject_content(agent_name: str, content: str) -> bool
async def create_fresh_session(agent_name: str) -> str
```

### Doctor → Teaching System (fleet/core/doctor.py → fleet/core/teaching.py)

When the doctor detects disease that can be cured with a lesson:

```python
# Doctor triggers teaching
outcome = await teaching.deliver_lesson(
    agent=agent_name,
    disease=detected_disease,
    task=task,
    verbatim_requirement=task.requirement_verbatim,
)

# Teaching reports back
if outcome == "comprehension_verified":
    # Agent returns to work
elif outcome == "no_change":
    # Doctor prunes
    await prune_agent(agent_name)
```

### Doctor → Event Bus (fleet/core/doctor.py → fleet/core/events.py)

Every doctor action emits a CloudEvent:

```python
await emit_event(create_event(
    type="fleet.immune.disease_detected",
    data={
        "agent": agent_name,
        "disease": "deviation",
        "severity": "medium",
        "task_id": task.id,
        "signal": "plan doesn't match verbatim requirement",
    }
))
```

Events flow through the chain runner to all surfaces:
IRC (#fleet), board memory, ntfy (if severe), Plane comments, event store.

### Doctor ← Methodology System (reads methodology to know what SHOULD happen)

The doctor reads methodology definitions to detect violations:

```python
# What stage is this task in?
stage = task.custom_fields.task_stage

# What does the methodology say is allowed in this stage?
allowed_tools = methodology.get_allowed_tools(stage)

# What did the agent actually do?
recent_tools = event_store.get_agent_tool_calls(agent, since=last_check)

# Violation?
for tool_call in recent_tools:
    if tool_call.tool not in allowed_tools:
        report_violation(agent, task, tool_call, stage)
```

### Doctor ← MC API (reads task state, custom fields, agent status)

The doctor reads everything through the MC client:

- Task list with custom fields (readiness, stage, verbatim requirement)
- Agent status (online/offline, last_seen_at, current task)
- Approval history (correction count per task)
- Board memory (recent entries, disease flags)
- Task comments (conversation history)

### Doctor ← Event Store (reads agent behavior history)

The event store (.fleet-events.jsonl) contains the history of everything
agents have done — MCP tool calls, commits, task transitions, errors.
The doctor reads this for pattern detection:

- Tool call frequency and sequence (did agent read before committing?)
- Time between task acceptance and completion (too fast = lazy?)
- Correction events (how many times corrected on this task?)
- Disease history per agent (recurring patterns over time)

---

## Existing Fleet Systems — Replace, Enhance, or Keep

The fleet already has systems that partially overlap with the immune
system. The immune system builds ON TOP of these, not in parallel.

| Existing System | File | What It Does Today | Immune System Relationship |
|----------------|------|-------------------|---------------------------|
| **Behavioral security** | `fleet/core/behavioral_security.py` | Pattern detection for dangerous ops (credential exfil, DB destruction, security bypass) | **KEEP + ENHANCE** — behavioral security detects security threats, immune system detects quality/methodology threats. Different concerns. Behavioral security feeds signals to the doctor (a security hold IS a disease signal). |
| **Task lifecycle** | `fleet/core/task_lifecycle.py` | PRE/PROGRESS/POST stages with validation gates | **ENHANCE** — task lifecycle becomes part of the work protocol. Methodology system adds stages BEFORE the existing lifecycle (conversation, analysis, investigation, reasoning). The existing PRE/PROGRESS/POST maps to the work protocol stage. |
| **Skill enforcement** | `fleet/core/skill_enforcement.py` | Required tools per task type, scoring | **ENHANCE** — skill enforcement currently SCORES compliance. The immune system gives it TEETH — non-compliance becomes a disease signal that triggers response (teaching, pruning). Scoring becomes detection. |
| **Agent roles** | `fleet/core/agent_roles.py` | Role-based PR authority, rejection rights | **KEEP** — agent roles are about authority boundaries, not health. The immune system respects role boundaries but doesn't replace them. |
| **Budget monitor** | `fleet/core/budget_monitor.py` | Token quota tracking, hard limits | **KEEP** — budget is a resource constraint, not a health concern. The doctor may read budget data as context (agent burning tokens fast = possibly stuck) but doesn't replace budget monitoring. |
| **PR hygiene** | `fleet/core/pr_hygiene.py` | Conflict detection, stale PR detection | **ENHANCE** — PR hygiene signals feed into the doctor. Stale PRs = possibly stuck agent. Orphaned PRs = possibly deviated agent. These become detection signals. |
| **Fleet control** | `fleet/core/fleet_mode.py` | Work mode, backend mode, cycle phase | **KEEP** — fleet control state gates dispatch via work_mode. The immune system respects the current fleet state when making decisions. |
| **Agent lifecycle** | `fleet/core/agent_lifecycle.py` | Active/idle/sleeping/offline states | **ENHANCE** — agent lifecycle tracks activity states. The doctor adds health states on top (healthy/sick/in-lesson/pruned). These are orthogonal — an agent can be active AND sick. |
| **Model selection** | `fleet/core/model_selection.py` | Opus vs sonnet by task complexity | **KEEP** — model selection is about capability matching, not health. |

The key principle: the immune system doesn't replace existing systems.
It OBSERVES their data, ENHANCES their enforcement, and adds NEW
capabilities (detection, teaching, pruning) that don't exist today.

---

## Evolutions Needed

The PO said the orchestrator and brain need to evolve. The immune system
is not just a new component — it changes existing components.

What existing systems need to evolve:
- Orchestrator — to run doctor checks, to respect immune system decisions
- Gateway — wrapper functions for existing session APIs (no patches needed)
- Event bus — new event types for immune/teaching/methodology actions
- Heartbeat context — to support rules reinjection and stage-aware instructions
- Task lifecycle — enhanced to work within methodology stages
- MCP tools — to respect methodology stage and report to immune system
- Skill enforcement — from scoring to enforcement with teeth
- PR hygiene — signals feed into doctor detection

---

## Open Questions

- Where does the doctor run architecturally? In the orchestrator? Beside
  it? Separate process?
- How does the doctor access agent context/state? Through the gateway
  API? Through events? Through git?
- What new event types does the immune system need?
- What new custom fields does the immune system need (separate from
  methodology system fields)?
- How does the immune system's health tracking persist? Database? JSONL?
  Custom fields?
- What's the performance impact? Does the doctor add latency to the
  orchestrator cycle?
- How does the immune system get deployed? Part of fleet setup? Separate?