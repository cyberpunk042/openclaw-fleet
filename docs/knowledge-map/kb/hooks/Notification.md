# Notification

**Type:** Claude Code Hook (lifecycle event)
**Category:** Post-Action (fires when Claude sends a notification)
**Handler types:** command, http, prompt, agent
**Can block:** NO (observation only)

## What It Actually Does

Fires when Claude Code sends a notification (e.g., background task completed, rate limit approaching, long operation finished). The handler can route notifications to custom channels — fleet-specific notification infrastructure instead of default terminal notifications.

## Fleet Use Case: Custom Notification Routing

```
Notification fires (Claude sends notification)
├── Classify notification type:
│   ├── Task completed → post to OCMC board via fleet_chat
│   ├── Rate limit warning → notify brain (session_manager.py)
│   ├── Error/failure → alert via fleet_alert
│   └── Background task done → log to trail
├── Route to fleet channels:
│   ├── IRC #alerts (via S18 notifications)
│   ├── ntfy push notification (PO notification)
│   ├── OCMC board memory (fleet_chat)
│   └── Trail event log
└── Return: {} (observation only)
```

## Why MEDIUM Priority for Fleet

Fleet agents don't have a human watching terminal notifications. Notification hook bridges Claude Code's notification system to fleet's notification infrastructure (IRC, ntfy, OCMC board). Without this hook, notifications are lost in unmonitored terminals.

## Relationships

- FIRES ON: Claude Code sends any notification
- CANNOT BLOCK: observation only
- CONNECTS TO: S18 notification system (IRC #alerts, ntfy)
- CONNECTS TO: fleet_alert tool (fleet's notification mechanism)
- CONNECTS TO: fleet_chat tool (post to OCMC board)
- CONNECTS TO: session_manager.py (rate limit notifications)
- CONNECTS TO: storm monitor (notification volume as possible indicator)
- TIER: 3 in implementation priority (enhances but not required)
