# HEARTBEAT.md — DevOps

FIRST: Do you have assigned tasks or chat messages?
  If NO and nothing in your domain needs attention: respond HEARTBEAT_OK immediately.
  Do NOT call tools unnecessarily. Minimize token usage on empty heartbeats.
  If YES: proceed below.

## 1. Check Chat
Call `fleet_read_context()`. Read `chat_messages` for @mentions.
Respond to infrastructure questions, deployment requests, CI issues.

## 2. Work on Assigned Tasks
If tasks assigned: work on them. Blocker tasks are HIGHEST priority.
If blocked: `fleet_pause()` with specifics.

## 3. Infrastructure Health
Quick checks (only if idle):
- Docker services running? Check with simple commands.
- Any CI pipeline failures? Check recent build status.
- Any dependency issues reported? Check board memory alerts.
If issues → `fleet_alert(category="workflow")`.

## 4. Proactive (Only If Idle)
- Check if setup.sh is up to date with recent changes
- Check if any scripts need updating
- `fleet_chat("Idle — ready for infra work", mention="lead")`