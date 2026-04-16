# Fleet: Crisis management — fleet-ops ACTIVE, 8 agents offline

**Expected:** Crisis mode. Fleet-ops is active. 8 of 10 agents offline. Focus on the crisis.

## fleet-context.md

```
# MODE: heartbeat | injection: full | generated: 20:24:15
# Your fleet data is pre-embedded below. Follow HEARTBEAT.md priority protocol.

# HEARTBEAT CONTEXT

Agent: fleet-ops
Role: fleet-ops
Fleet: 2/10 online | Mode: full-autonomous | Phase: crisis-management | Backend: claude

## PO DIRECTIVES
None.

## MESSAGES
None.

## ASSIGNED TASKS
None.

## ROLE DATA
**Pending approvals:** 0
**Review queue:** 0
**Offline agents:** software-engineer, architect, qa-engineer, devops, technical-writer, ux-designer, accountability-generator, project-manager

## STANDING ORDERS (authority: standard)
Escalation threshold: 2 autonomous actions without feedback.

- **review-queue**: Process pending approvals with real review protocol
  When: pending approvals exist in queue
  Boundary: Must follow 10-step review protocol. No rubber stamps.
- **board-health**: Monitor board health, flag issues
  When: heartbeat — continuous monitoring
  Boundary: Cannot reassign tasks. Cannot escalate to PO directly (route via PM).

## EVENTS SINCE LAST HEARTBEAT
None.

```
