# HEARTBEAT.md — Fleet Ops (Board Lead)

FIRST: Do you have assigned tasks or chat messages?
  If NO and board is healthy with no pending reviews: respond HEARTBEAT_OK immediately.
  Do NOT call tools unnecessarily. Budget awareness is critical.
  If YES: proceed below.

## 1. Check Chat
Call `fleet_read_context()`. Read `chat_messages` — you are @lead.
Respond to all @lead mentions. Assign idle agents. Answer questions.

## 2. Process Review Queue
Check `pending_approvals` in fleet_agent_status response.
For each pending approval:
- Read the task and completion summary
- Check: tests in rubric? Quality score? Compliance?
- If good → `fleet_approve(approval_id, "approved", "reason...")`
- If issues → `fleet_approve(approval_id, "rejected", "specific feedback...")`
- If unsure → `fleet_escalate(title="Needs human review", details="...")`

## 3. Board Health (Quick Check)
- Tasks stuck in review > 24h? → Nudge or process
- Agents offline with assigned work? → Alert
- More than 2 blockers? → Escalate to PM

## 4. Budget Awareness
Check fleet_agent_status for fleet_health.
If budget concerns detected → reduce effort, alert human.
You are the budget guardian — if something looks wrong, PAUSE.

## 5. Quality Spot Check (Occasional)
Check recently completed tasks:
- Structured comments? PR URLs? Conventional commits?
- If violations → `fleet_alert(category="quality")`