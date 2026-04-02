# Plan 04 — Hooks Infrastructure

**Phase:** 4 (depends on Plan 01 safety-net experience)
**Source:** Synthesis D16 | Analysis 05 (hooks)
**Milestone IDs:** HK-001 to HK-008

---

## What This Plan Delivers

The enforcement layer of the knowledge map. Hooks are DETERMINISTIC —
they fire every time, 100% reliable. Unlike skills (agent chooses) or
commands (agent invokes), hooks are AUTOMATIC. This is Line 1
anti-corruption: structural prevention.

---

## Tier 1 Hooks (implement first)

### HK-001: PreToolUse — safety gate + stage enforcement

**What:** Intercept every tool call. Block destructive commands AND
validate tool matches current methodology stage.

**Components:**
- safety-net plugin (Plan 01) handles destructive commands
- Custom stage enforcement hook handles methodology gating
- Combined: belt + suspenders

**Implementation:**
```
hooks.json:
  PreToolUse:
    - type: command
      command: "python -m fleet.hooks.pre_tool_gate"
      match: ["Bash", "Write", "Edit", "Agent"]
```

`fleet/hooks/pre_tool_gate.py`:
- Read tool name + input from stdin (JSON)
- Read current stage from environment or context
- If stage=conversation and tool writes files → deny + feedback
- If tool matches safety patterns (rm -rf, git reset --hard) → deny
- If contribution gate: check contributions received → deny if missing
- Return: {"allow": true} or {"deny": true, "message": "..."}

**Test:** Try writing a file in conversation stage → blocked with message

### HK-002: PostToolUse — trail recording

**What:** After every successful tool call, record a trail event.

**Implementation:**
```
hooks.json:
  PostToolUse:
    - type: command
      command: "python -m fleet.hooks.post_tool_trail"
      match: ["*"]
```

`fleet/hooks/post_tool_trail.py`:
- Read tool name + result from stdin
- Post trail event to board memory (via MC API or local file)
- Tags: trail, task:{id}, tool:{name}, agent:{name}
- Must complete in <100ms (non-blocking)

**Test:** Call fleet_read_context → trail event appears

### HK-003: SessionStart — knowledge map injection

**What:** At session start, inject fleet context from knowledge map.

**Implementation:**
```
hooks.json:
  SessionStart:
    - type: command
      command: "python -m fleet.hooks.session_start_inject"
```

`fleet/hooks/session_start_inject.py`:
- Read agent name from env
- Read injection profile (from intent-map.yaml based on model)
- Assemble context from knowledge map content
- Return: {"additionalContext": "...assembled content..."}
- This is WHERE the knowledge map becomes ACTIVE

**Test:** Start session → injected context includes fleet state + role data

### HK-004: Stop — state save + optional review gate

**What:** When Claude finishes responding, save session state.
Optional: review gate pattern (independent check before completion).

**Implementation:**
```
hooks.json:
  Stop:
    - type: command
      command: "python -m fleet.hooks.stop_save_state"
```

`fleet/hooks/stop_save_state.py`:
- Save key decisions to memory (for context recovery after compact)
- Record trail event "turn completed"
- If review gate enabled: run independent quality check
  (future — starts as state save only)

### HK-005: StopFailure — rate limit detection

**What:** When a turn ends from API error, detect and handle.

**Implementation:**
```
hooks.json:
  StopFailure:
    - type: command
      command: "python -m fleet.hooks.stop_failure_handler"
      match: ["rate_limit", "authentication_failed"]
```

`fleet/hooks/stop_failure_handler.py`:
- If rate_limit: write signal file for orchestrator to detect
- If auth_failed: alert for human intervention
- Log the failure for storm monitor

---

## Tier 2 Hooks (implement after Tier 1 proven)

### HK-005: PreCompact — save state before context loss

**What:** Before compaction, save critical state to persistent storage.

`fleet/hooks/pre_compact_save.py`:
- Save current task context to memory
- Save key decisions made this session
- Save artifact progress
- Record what should be preserved in compaction instructions

### HK-006: PostCompact — verify context recovery

**What:** After compaction, verify critical context survived.

`fleet/hooks/post_compact_verify.py`:
- Check: does agent still know current task?
- Check: does agent still know its role?
- If critical context lost: re-inject from knowledge map

### HK-007: InstructionsLoaded — augment CLAUDE.md with map data

**What:** When CLAUDE.md is loaded, augment with dynamic knowledge map content.

`fleet/hooks/instructions_augment.py`:
- Read current agent role
- Read current task stage (if available)
- Inject per-stage skill/command/tool recommendations from methodology manual
- This makes CLAUDE.md DYNAMIC without changing the file

### HK-008: Per-agent hook configuration via IaC

**What:** agent-tooling.yaml defines hooks per role, provisioning deploys them.

```yaml
defaults:
  hooks:
    PreToolUse: [stage_gate]
    PostToolUse: [trail_record]
    SessionStart: [map_inject]
    Stop: [state_save]
    StopFailure: [error_handler]

agents:
  devsecops-expert:
    hooks:
      PreToolUse: [stage_gate, security_scan]  # additional security hook
  fleet-ops:
    hooks:
      Stop: [state_save, review_gate]  # additional review gate
```

---

## IaC Integration

All hooks provisioned via:
1. `config/agent-tooling.yaml` — hook assignments per role
2. `scripts/provision-agent-files.sh` — generates hooks.json per agent
3. `fleet/hooks/` — Python hook handler modules
4. `scripts/validate-agents.sh` — verifies hooks registered

---

## Validation Checklist

- [ ] PreToolUse blocks file writes in conversation stage
- [ ] PreToolUse allows file writes in work stage
- [ ] PostToolUse records trail event for every tool call
- [ ] SessionStart injects knowledge map context
- [ ] Stop saves session state
- [ ] StopFailure detects rate limits
- [ ] PreCompact saves state before context loss
- [ ] PostCompact verifies context recovery
- [ ] InstructionsLoaded augments CLAUDE.md with stage recommendations
- [ ] Per-agent hook config provisioned from agent-tooling.yaml
- [ ] All hooks complete in <100ms (non-blocking)

---

## What This Enables

With this plan complete:
- Knowledge map becomes ACTIVE (SessionStart injects, InstructionsLoaded augments)
- Trail recording is AUTOMATIC (PostToolUse, never missed)
- Stage enforcement is STRUCTURAL (PreToolUse, can't bypass)
- Context survives compaction (PreCompact saves, PostCompact verifies)
- Rate limits detected instantly (StopFailure)
- Per-role hook specialization via IaC (devsecops gets security hooks, fleet-ops gets review gate)
