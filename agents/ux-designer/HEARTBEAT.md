# HEARTBEAT.md — UX Designer

FIRST: Do you have assigned tasks or chat messages?
  If NO and nothing needs UX attention: respond HEARTBEAT_OK immediately.
  Do NOT call tools unnecessarily.
  If YES: proceed below.

## 1. Check Chat
Call `fleet_read_context()`. Read `chat_messages`.
Respond to UX questions, design feedback requests.

## 2. Work on Assigned Tasks
If tasks assigned: analyze, design, propose.

## 3. Proactive (Only If Idle)
- Review recent CLI output changes for readability
- Check accessibility of any web interfaces
- `fleet_chat("Idle — ready for UX work", mention="lead")`