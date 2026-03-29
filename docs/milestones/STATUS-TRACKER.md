# Fleet Status Tracker — Where We Actually Are

## Last Updated: 2026-03-28 end of session

---

## CRITICAL BUGS (catastrophic-usage-drain-investigation.md)

| # | Bug | Status | Notes |
|---|-----|--------|-------|
| C0 | Revert _send_chat from orchestrator | ✅ CODE DONE | Needs verification when fleet restarts |
| C1 | Clean gateway duplicates (22→11) | ✅ DONE | openclaw.json cleaned |
| C2 | Stale process detection | ✅ TOOL BUILT | scripts/check-fleet-processes.sh |
| C3 | Fleet pause/resume | ✅ CODE DONE | fleet pause / fleet resume commands |
| C4 | Budget monitor in dispatch | ✅ CODE DONE | Reads CLAUDE_QUOTA_* env vars |
| C5 | Real budget monitor | ✅ CODE DONE | fleet/core/budget_monitor.py |
| C6 | Max 2 dispatch per cycle | ✅ CODE DONE | In orchestrator |
| C7 | Cascade depth limit | ✅ CODE DONE | Max 3 levels in fleet_task_create |
| C8 | Effort profiles | ✅ CODE DONE | fleet/core/effort_profiles.py, conservative default |
| C9 | Heartbeat rewrites (all 10) | ✅ CODE DONE | Fast-exit pattern, active participation |
| C10 | Board cleanup | ✅ TOOL BUILT | fleet/core/board_cleanup.py — needs MC to execute |
| C11 | Gateway heartbeat stagger | ✅ DONE | Different intervals per agent (30-90m) |
| C12 | Outage detection | ✅ CODE DONE | fleet/core/outage_detector.py |
| C13 | Effort profiles | ✅ CODE DONE | Same as C8 |
| C14 | fleet-ops budget guardian | ✅ IN HEARTBEAT | fleet-ops HEARTBEAT.md has budget section |

**STATUS: All C items have CODE. NONE verified running. Fleet is stopped.**

---

## ORIGINAL BUGS (critical-bugs-and-missing-work.md)

| # | Bug | Status | Notes |
|---|-----|--------|-------|
| 1 | Heartbeat model wrong | ✅ REDESIGNED | Gateway handles heartbeats, orchestrator doesn't create sessions |
| 2 | MCP server doesn't reload | ✅ TOOL BUILT | scripts/reprovision-agents.sh |
| 3 | Chat not working e2e | ❌ NOT VERIFIED | fleet_chat tool built, never tested with real agents |
| 4 | Sprint work blocked | ✅ CODE DONE | Task scoring, max dispatch, effort profiles |
| 5 | Plane IaC | ✅ AGENT BUILT IT | devops built plane-configure.sh in Sprint 3 |
| 6 | Framework not pushed/provisioned | ✅ TOOL BUILT | scripts/push-agent-framework.sh + reprovision |
| 7 | Board memory pollution | ✅ CODE DONE | Removed post_memory from sync daemon |
| 8 | Review task flooding | ✅ CODE DONE | _wake_lead_for_reviews uses IRC only |
| 9 | No reprovision after code changes | ✅ TOOL BUILT | scripts/reprovision-agents.sh |
| 10 | No verification culture | ❌ ONGOING | We keep claiming done without testing |

---

## MISSING MILESTONES (critical-bugs-and-missing-work.md MM1-MM8)

| # | Milestone | Status | Notes |
|---|-----------|--------|-------|
| MM1 | Event-driven agent wake | ❌ NOT BUILT | Design exists, gateway handles heartbeats, but no event→wake mapping |
| MM2 | MCP hot-reload | ✅ WORKAROUND | reprovision-agents.sh kills and restarts MCP processes |
| MM3 | Communication verification e2e | ❌ NOT DONE | Needs fleet running to test |
| MM4 | Board memory hygiene | ✅ CODE DONE | Sync daemon cleaned, board_cleanup tool built |
| MM5 | Sprint task priority | ✅ CODE DONE | task_scoring.py in orchestrator dispatch |
| MM6 | Plane IaC script | ✅ AGENT BUILT | plane-configure.sh exists |
| MM7 | Reprovision pipeline | ✅ TOOL BUILT | scripts/reprovision-agents.sh |
| MM8 | Agent event filtering | ❌ NOT BUILT | events_for_me in context not implemented |

---

## PRE-RELAUNCH (pre-relaunch-milestones.md PR1-PR8)

| # | Milestone | Status | Notes |
|---|-----------|--------|-------|
| PR1 | Event-driven wake | ❌ NOT BUILT | Same as MM1 |
| PR2 | Agent event filtering | ❌ NOT BUILT | Same as MM8 |
| PR3 | Sprint task priority | ✅ CODE DONE | task_scoring.py |
| PR4 | PM as Scrum Master | ✅ HEARTBEAT DONE | PM HEARTBEAT.md rewritten with scrum duties |
| PR5 | Software engineer active | ✅ HEARTBEAT DONE | sw-eng HEARTBEAT.md rewritten |
| PR6 | All agents active participation | ✅ HEARTBEAT DONE | All 10 rewritten |
| PR7 | Clean board before relaunch | ✅ TOOL BUILT | board_cleanup.py — needs MC to execute |
| PR8 | E2E communication test | ❌ NOT DONE | 8-point check needs fleet running |

---

## FLEET MILESTONES (pre-relaunch-milestones.md F1-F4)

| # | Milestone | Status | Notes |
|---|-----------|--------|-------|
| F1 | PM drives Sprint 3 properly | ❌ NOT STARTED | Needs fleet relaunch |
| F2 | Agents communicate during work | ❌ NOT STARTED | Needs fleet relaunch |
| F3 | Review chain with quality | ❌ NOT STARTED | Needs fleet relaunch |
| F4 | Sprint 3 completes with quality | ❌ NOT STARTED | Needs fleet relaunch |

---

## COMMUNICATION (communication-infrastructure-milestones.md M230-M236)

| # | Milestone | Status | Notes |
|---|-----------|--------|-------|
| M230 | Internal chat (fleet_chat) | ✅ CODE DONE | Tool built, @mention routing, not verified |
| M231 | IRC 10 channels | ✅ CODE DONE | Routing matrix in irc.py, setup-irc.sh updated |
| M232 | ntfy operational | ✅ CODE DONE | Triggers expanded, topics configured |
| M233 | Agent context enrichment | ✅ CODE DONE | sprint, role, health, chat in fleet_read_context |
| M234 | Pre-Plane verification | ✅ SCRIPT DONE | 8-point check passed once, needs re-verify |
| M235 | Plane integration comms | ❌ NOT STARTED | Needs Plane configured first |
| M236 | Documentation and skills | ✅ DONE | 6 Claude Code skills built |

---

## EVOLUTION (fleet-evolution-milestones.md M220-M227)

| # | Milestone | Status | Notes |
|---|-----------|--------|-------|
| M220 | Agent secondary roles | ✅ CODE DONE | fleet/core/agent_roles.py with PR authority |
| M221 | Behavioral security | ✅ CODE DONE | fleet/core/behavioral_security.py |
| M222 | Multi-machine federation | ✅ CODE DONE | fleet/core/federation.py |
| M223 | Remote change detection | ✅ CODE DONE | fleet/core/remote_watcher.py + sync integration |
| M224 | Planning enforcement | ✅ CODE DONE | fleet/core/plan_quality.py in fleet_task_accept |
| M225 | Dynamic model selection | ✅ CODE DONE | fleet/core/model_selection.py in dispatch |
| M226 | Skill enforcement | ✅ CODE DONE | fleet/core/skill_enforcement.py |
| M227 | Strong cohesive memory | ✅ STRUCTURE DONE | memory_structure.py, 50 files initialized |

---

## STRATEGIC (strategic-vision-localai-independence.md)

| # | Stage | Status | Notes |
|---|-------|--------|-------|
| 1 | Make LocalAI functional | ❌ NOT STARTED | Assess AICP + LocalAI current state first |
| 2 | Route simple ops to LocalAI | ❌ NOT STARTED | Needs Stage 1 |
| 3 | Progressive offload | ❌ NOT STARTED | Needs Stage 2 |
| 4 | Reliability and failover | ❌ NOT STARTED | Needs Stage 3 |
| 5 | Near-independent operation | ❌ NOT STARTED | Needs Stage 4 |

---

## SPRINT STATUS

| Sprint | Status |
|--------|--------|
| DSPD Sprint 1 | ✅ COMPLETE (8/8 tasks) |
| DSPD Sprint 2 | ✅ COMPLETE (8/8 tasks) |
| DSPD Sprint 3 | ⏸️ PAUSED — 1/10 done, fleet stopped after drain |

---

## WHAT'S ACTUALLY NEXT (in order)

1. **Start MC containers** (Docker) — needed for board cleanup and verification
2. **Execute board cleanup** — use board_cleanup tool via fleet-ops or CLI
3. **Push framework to agents** — reprovision with latest heartbeats/tools
4. **Start gateway with cleaned config** — 11 agents, staggered heartbeats
5. **Verify communication e2e** — PR8 8-point check
6. **Start orchestrator in conservative mode** — effort_profile=conservative
7. **Observe** — does the fleet behave? Is budget under control?
8. **Sprint 3 resumes** — PM drives, agents communicate, review chain works
9. **Sprint 3 completes** — Plane configured, IaC scripts verified
10. **DSPD Sprint 4** — Plane ↔ OCMC sync, PM uses Plane
11. **LocalAI epic** — first Plane epic, long-run

---

## THINGS BUILT BUT NEVER VERIFIED RUNNING

- fleet_chat tool (#14) — agents have it in MCP but never used it
- fleet_notify_human tool — ntfy publishes work (tested once) but agents never called it
- fleet_escalate tool — never called by an agent
- Budget monitor — CLAUDE_QUOTA_* env vars never tested in agent session
- Board cleanup tool — plan_cleanup tested in unit tests, never executed on real board
- Effort profiles — code in orchestrator, never ran with conservative profile
- Outage detector — code in orchestrator, never triggered
- All 10 agent HEARTBEAT.md rewrites — pushed to workspaces but agents haven't read them yet
- 10 IRC channels — routing matrix built but channels not created yet (IRC config updated, not restarted)
- Review gates — fleet_task_complete populates them but fleet-ops never reviewed with them
- Agent roles — PR authority coded but never enforced in a real approval flow