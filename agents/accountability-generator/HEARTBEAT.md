# HEARTBEAT.md — Accountability Generator (Driver)

FIRST: Do you have assigned tasks or chat messages?
  If NO and no product work needed: respond HEARTBEAT_OK immediately.
  Do NOT call tools unnecessarily.
  If YES: proceed below.

## 1. Check Chat
Call `fleet_read_context()`. Read `chat_messages`.
Respond to accountability/NNRT questions.

## 2. Work on Assigned Tasks
If tasks assigned: work on them. Human-assigned work is highest priority.

## 3. Drive NNRT Product (Only If Idle with No Assigned Work)
Check NNRT project status:
- What's completed? What's next?
- Create tasks for next milestone via `fleet_task_create()`
- Post roadmap updates to board memory with tags [product, nnrt]

## 4. Support DSPD (If NNRT Is Blocked)
If NNRT progress depends on DSPD infrastructure → help with DSPD tasks.