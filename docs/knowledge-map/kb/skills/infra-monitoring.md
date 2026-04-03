# infra-monitoring

**Type:** Skill (AICP Lifecycle)
**Location:** devops-expert-local-ai/.claude/skills/infra-monitoring/
**Invocation:** /infra-monitoring
**Effort:** medium
**Roles:** DevOps

## What It Does

Set up monitoring: health check endpoints, metrics collection, alerting rules, dashboard configuration. Covers service uptime, resource usage (CPU, memory, disk), error rates, response times.

## Fleet Use Case

DevOps monitors fleet infrastructure: Mission Control, LightRAG, LocalAI, PostgreSQL, Redis, The Lounge. Each service has health endpoints. Storm monitor (S11) provides fleet-level monitoring. infra-monitoring sets up the infrastructure layer beneath it.

## Relationships

- USED BY: devops
- CONNECTS TO: storm monitor S11 (fleet-level anomaly detection)
- CONNECTS TO: /loop command (periodic monitoring checks)
- CONNECTS TO: fleet_alert tool (monitoring threshold → alert)
- CONNECTS TO: ops-incident skill (monitoring detects → incident response)
- CONNECTS TO: docker-compose.yaml (healthcheck definitions)
