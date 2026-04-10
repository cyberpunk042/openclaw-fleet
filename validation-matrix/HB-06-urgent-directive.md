# Heartbeat: Urgent PO directive — overrides everything

**Expected behavior:** PO directive is HIGHEST PRIORITY. Stop current work, execute directive.

## fleet-context.md

```
# MODE: heartbeat | injection: full | generated: 01:24:04
# Your fleet data is pre-embedded below. Follow HEARTBEAT.md priority protocol.

# HEARTBEAT CONTEXT

Agent: software-engineer
Role: software-engineer
Fleet: 9/10 online | Mode: full-autonomous | Phase: execution | Backend: claude

## PO DIRECTIVES
- 🚨 URGENT STOP all dashboard work. Priority shift to auth fix. Start immediately. (from human)

## MESSAGES
None.

## ASSIGNED TASKS
None.

## STANDING ORDERS (authority: conservative)
Escalation threshold: 2 autonomous actions without feedback.

- **work-assigned-tasks**: Execute confirmed plans on assigned tasks
  When: assigned task in work stage
  Boundary: Must follow confirmed plan. No scope addition. Consume contributions.

## EVENTS SINCE LAST HEARTBEAT
None.

```
