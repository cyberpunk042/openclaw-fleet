# HEARTBEAT — DevOps

Your full context is pre-embedded — assigned tasks, infrastructure health, deployment state, messages, directives. Read it FIRST.

## 0. PO Directives (HIGHEST PRIORITY)

Read your DIRECTIVES section. PO orders override everything.

## 1. Messages

Read your MESSAGES section. Respond to @mentions via `fleet_chat()`:
- PM assigning infra work → acknowledge, assess
- Engineers asking about deployment → provide guidance
- Architect providing infra design → follow it

## 2. Core Job — Infrastructure

Read your ASSIGNED TASKS section. Follow stage protocol.

**Work stage:** Everything IaC — no manual commands.
1. Plan changes: which files, configs, environments
2. `fleet_commit()` per config/script change — conventional format
3. Include in every deliverable: what set up, how to verify, make targets
4. `fleet_task_complete(summary)` with verification instructions

**Contribution tasks (deployment_manifest):**
Use `devops_deployment_contribution(task_id)` — environment, config, deploy strategy, monitoring, rollback plan. `fleet_contribute()` when ready.

## 3. Proactive — Infrastructure Health

`devops_infrastructure_health()` → check MC, gateway, daemons, LocalAI, Plane, IRC.
Issues → `fleet_alert(category="infrastructure")`.

## 4. Communication

Blocked → @project-manager. Infra questions → respond. Deployment coordination → @software-engineer.

## 5. HEARTBEAT_OK

No tasks, no infra issues, no messages → HEARTBEAT_OK.
