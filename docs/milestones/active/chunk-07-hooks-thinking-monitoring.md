# Chunk 7: Hooks + Extended Thinking + Monitoring

**Date:** 2026-04-07
**Status:** Planning
**Part of:** [tools-system-session-index.md](tools-system-session-index.md) — Chunk 7 of 9
**Depends on:** Chunk 2 (plugin hooks: security-guidance, safety-net, hookify), Chunk 5 (standing orders — hooks enforce standing order boundaries)
**Blocks:** Chunk 8 (generation pipeline needs hook/thinking info for TOOLS.md)

---

## What This Chunk Accomplishes

Three connected mechanisms:

1. **Hooks** — per-role lifecycle event handlers for quality enforcement, monitoring, and security
2. **Extended thinking** — stage-aware effort configuration connecting brain decisions to agent session parameters
3. **PO monitoring** — hook-based agent observation stream (the PO's idea of connecting to see an agent's current feed)

---

## Part 1: Per-Role Hook Configurations

### What Exists Today

- Template settings.json allows: Bash, Read, Write, Edit, Glob, Grep, fleet MCP tools
- safety-net plugin: PreToolUse catches destructive commands (ALL agents via config)
- security-guidance plugin: 9 security PreToolUse patterns (devsecops via config)
- hookify plugin: natural-language hook creation (devops via config)
- superpowers plugin: SessionStart hook injects skill instructions (architect, engineer, QA via config)

### What's Needed Per Role

Each role may benefit from additional hook configurations. These need per-role evaluation — not every role needs every hook type.

**Quality enforcement hooks (PreToolUse):**
- Commit message format validation (before fleet_commit: does message match conventional format?)
- PR body structure validation (before fleet_task_complete: does summary exist and meet minimum quality?)
- Artifact completeness gate (before fleet_task_complete: is artifact completeness above threshold?)
- Stage protocol enforcement (before fleet_commit during non-work stage: redundant with MCP stage gate but provides defense-in-depth)

**Behavioral hooks (PostToolUse):**
- Trail recording enhancement (after every state-modifying tool call: record trail event)
- Cost tracking (after every tool call: aggregate token usage)
- Activity logging (after every tool call: log to fleet activity feed)

**Session hooks:**
- SessionStart: inject role-specific context, check for pending work, load standing orders
- PreCompact: save important artifacts before context is compressed
- PostCompact: verify critical context survived compaction

**Per-role specifics:**
- DevSecOps: security-guidance hooks already cover code security patterns. Additional: dependency vulnerability alerts on package file changes (FileChanged hook on requirements.txt, package.json)
- Engineer: pyright-lsp provides type checking. Additional: test run after code changes (PostToolUse on Edit/Write: run relevant tests)
- Fleet-ops: review quality hooks (before fleet_approve: verify that review was substantive, not rubber-stamp)
- DevOps: infrastructure safety hooks (before Bash commands in infrastructure directories: extra caution prompts)

### Hook Configuration Architecture

Hooks are configured in .claude/settings.json per agent. The current template has only permission allows. Hooks need to be added:

```json
{
  "permissions": {
    "allow": ["Bash(*)", "Read(*)", "Write(*)", "Edit(*)", "Glob(*)", "Grep(*)", "mcp__fleet__*"],
    "deny": []
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "fleet_commit",
        "hooks": [
          {
            "type": "command",
            "command": "scripts/hooks/validate-commit-format.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:XXXX/agent-activity",
            "async": true
          }
        ]
      }
    ]
  }
}
```

### Security Hook Content Detection Issue (Observed This Session)

The security-guidance plugin's PreToolUse hooks trigger on content that MENTIONS security patterns (e.g., a document describing what the plugin detects). This caused false positives when writing documentation about security patterns.

Solutions to evaluate:
- Detect when content is documentation/markdown (not code) and reduce sensitivity
- Whitelist known documentation paths
- Transform flagged content to pass hooks while remaining readable
- Configure per-agent hook sensitivity
- File a bug/feature request with the security-guidance plugin maintainers

---

## Part 2: Stage-Aware Extended Thinking

### Current State

configure-agent-settings.sh sets static effort levels per role:
- HIGH: architect, devsecops, PM, accountability
- MEDIUM: engineer, QA, devops, fleet-ops, UX
- LOW: writer

These are static — same effort regardless of stage, task complexity, or situation.

### What Stage-Aware Effort Would Mean

The effort level should adapt to the current situation:

| Situation | Suggested Effort | Rationale |
|-----------|-----------------|-----------|
| Conversation stage | HIGH | Understanding requirements needs deep reasoning |
| Analysis stage | HIGH | Examining codebases needs thoroughness |
| Investigation stage | HIGH | Exploring options needs breadth |
| Reasoning stage | HIGH | Planning needs precision |
| Work stage | MEDIUM | Executing a confirmed plan is more mechanical |
| Heartbeat with no work | LOW | Status check doesn't need deep reasoning |
| CRON: security scan | HIGH | Thoroughness critical for security |
| CRON: daily summary | LOW | Routine data aggregation |
| Complex task (L/XL) | HIGH override | Override default for complex work |
| Simple subtask (S) | LOW override | Override default for simple work |

### Implementation Architecture

Three configuration surfaces currently exist independently:

1. **Dispatch** — brain's model_selection.py chooses model/effort at dispatch time. This already considers task type, complexity, story points, and agent role. But it doesn't set the session effort level — it selects the model.

2. **Heartbeats** — static effortLevel in settings.json. Applied to every heartbeat turn.

3. **CRONs** — per-job --model and --thinking flags. Set in config/agent-crons.yaml (Chunk 5).

### Connecting Them

The brain already makes strategic call decisions with 9 dimensions (fleet-elevation/23). The effort level should be one output of that decision, not a static config.

Options:
- **Brain writes effort to settings.json** before each heartbeat (dynamic but requires file write per heartbeat)
- **Brain injects effort in context** ("Your effort level for this task: HIGH") — agent can't change Claude Code effort setting, but prompt influences thinking depth
- **Gateway config per session** — if the gateway supports per-session effort override (it does for CRONs, may for heartbeats)
- **Defer to brain evolution** — mark this as a future brain capability, keep static effort for now

Recommendation: for this chunk, update the static effort levels in configure-agent-settings.sh to be HIGHER across the board (most roles should be at HIGH for non-heartbeat work), and defer the dynamic stage-aware effort to brain evolution (Phase C). CRONs get per-job effort from config (Chunk 5).

### The "ultrathink" Keyword

For immediate needs, the brain can include "ultrathink" in dispatch messages for complex tasks:
- "ultrathink: This L5 epic requires deep architectural analysis..."
- This forces HIGH effort for that single turn regardless of settings

This is a tactical tool, not a system. But it works TODAY without any infrastructure changes.

---

## Part 3: PO Monitoring — Agent Observation Stream

### The PO's Idea

Connect via stream to see a selected agent's current feed — real-time observation of what the agent is doing.

### Technical Architecture

**Data flow:**
1. PostToolUse HTTP hook fires after every tool call (async, non-blocking)
2. Hook POSTs JSON payload to fleet monitoring service
3. Monitoring service stores events, serves WebSocket feed
4. PO connects via browser to see real-time agent activity
5. Filter by agent, tool type, time

**Payload per event:**
```json
{
  "agent_name": "software-engineer",
  "session_id": "xxx",
  "timestamp": "2026-04-07T15:30:00Z",
  "tool_name": "fleet_commit",
  "tool_input": {"files": ["engine.py"], "message": "feat: add type hints"},
  "tool_output": {"ok": true, "sha": "abc1234"},
  "duration_ms": 1200
}
```

**Monitoring service options:**
- Simple Flask/FastAPI service with WebSocket feed to browser
- Leverage existing The Lounge (IRC web client) — agent activity already appears in IRC channels
- Leverage existing board memory — agent activity appears in board memory with tags
- Build a dedicated monitoring dashboard

### Minimal Viable Implementation

The IRC channels already show agent activity (fleet_task_complete → IRC #fleet, fleet_alert → IRC #alerts, etc.). The Lounge provides web access with persistent connections, full-text search, and multi-channel view.

**What's ALREADY observable via IRC + The Lounge:**
- Task dispatch (#fleet)
- Commits (after chain wiring)
- Task completion (#fleet + #reviews)
- Alerts (#alerts)
- Chat messages (#fleet)
- Approvals (#reviews)
- Blockers (#fleet)
- Escalations (#alerts)

**What's NOT observable:**
- Which tool the agent is calling right now
- What parameters the agent is passing
- How long each tool call takes
- Agent's internal reasoning/thinking

The HTTP hook approach provides the deeper observability. But IRC + The Lounge provides the 80% solution TODAY without building anything new.

### Recommendation

1. **Immediate:** The chain wiring (Chunk 1) makes more activity visible in IRC. This is the 80% solution.
2. **Short-term:** Add PostToolUse HTTP hook to ONE agent as proof of concept. Build minimal monitoring endpoint. Evaluate if the deeper observability is worth the infrastructure.
3. **Strategic:** Full monitoring dashboard with per-agent feeds, filtering, history. This is a separate project, not part of the tools system elevation.

---

## Verification Criteria

- [ ] Per-role hook configurations designed and documented
- [ ] Quality enforcement hooks tested (commit format, PR structure)
- [ ] Behavioral hooks tested (trail recording, activity logging)
- [ ] Security hook content detection issue addressed or documented as known limitation
- [ ] Extended thinking effort levels updated in configure-agent-settings.sh
- [ ] Stage-aware effort approach documented (static now, dynamic deferred to brain evolution)
- [ ] IRC monitoring verified as 80% observability solution (after Chunk 1 chain wiring)
- [ ] HTTP hook proof of concept evaluated (if pursuing deeper monitoring)

---

## Outputs

| Output | Description |
|--------|-------------|
| Per-role .claude/settings.json hook configs | Hook configurations per agent |
| Updated configure-agent-settings.sh | Revised effort levels |
| Hook scripts (scripts/hooks/) | Custom hook implementations |
| Monitoring evaluation | IRC vs HTTP hooks vs dashboard recommendation |
| Known issues doc | Security hook content detection, stage-aware effort deferral |
