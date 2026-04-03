# sage

**Type:** Claude Code Plugin
**Source:** github.com/gendigitalinc/sage
**Stars:** 162
**Installed for:** DevSecOps

## What It Does

Agent Detection and Response (ADR). Monitors AI agent behavior for anomalies — detecting when agents deviate from expected patterns, attempt unauthorized actions, or exhibit signs of prompt injection. The security equivalent of endpoint detection for AI agents.

## Fleet Use Case

DevSecOps monitors fleet agent behavior. sage adds automated anomaly detection — if an agent starts doing something unusual (accessing unexpected files, making abnormal API calls, deviating from task scope), sage flags it.

Complements the doctor system (S02) which detects laziness, stuck agents, and protocol violations. sage focuses on SECURITY anomalies while doctor focuses on BEHAVIORAL anomalies.

## Relationships

- INSTALLED FOR: devsecops-expert
- CONNECTS TO: doctor system (S02 — behavioral detection vs sage security detection)
- CONNECTS TO: storm monitor (S11 — agent anomalies may correlate with storm indicators)
- CONNECTS TO: fleet_alert tool (flag security anomalies)
- CONNECTS TO: trail system (agent actions logged → sage analyzes patterns)
- CONNECTS TO: anti-corruption rules (sage enforces from security angle)
