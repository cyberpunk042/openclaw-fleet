# Fleet: Planning phase — engineer NOT ACTIVE

**Expected:** Engineer sees 'planning' phase. Should recognize it's not their turn. HEARTBEAT_OK.

## fleet-context.md

```
# MODE: heartbeat | injection: full | generated: 01:24:04
# Your fleet data is pre-embedded below. Follow HEARTBEAT.md priority protocol.

# HEARTBEAT CONTEXT

Agent: software-engineer
Role: software-engineer
Fleet: 2/10 online | Mode: full-autonomous | Phase: planning | Backend: claude

## PO DIRECTIVES
None.

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
