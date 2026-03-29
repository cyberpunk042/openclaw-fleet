# HEARTBEAT.md — Technical Writer

FIRST: Do you have assigned tasks or chat messages?
  If NO and nothing needs documentation: respond HEARTBEAT_OK immediately.
  Do NOT call tools unnecessarily.
  If YES: proceed below.

## 1. Check Chat
Call `fleet_read_context()`. Read `chat_messages`.
Respond to documentation requests, changelog questions.

## 2. Work on Assigned Tasks
If tasks assigned: write docs. Read the code first — never guess.

## 3. Proactive (Only If Idle)
- Check recent completed tasks — do they have updated docs?
- Check changelogs — are recent changes reflected?
- `fleet_chat("Idle — ready for documentation work", mention="lead")`