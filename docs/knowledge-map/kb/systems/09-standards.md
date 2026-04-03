# System 09: Standards Library — What "Done Right" Looks Like

**Type:** Fleet System
**ID:** S09
**Files:** standards.py (~200 lines), plan_quality.py (~180 lines), pr_hygiene.py (~180 lines), skill_enforcement.py (~180 lines)
**Total:** 739 lines
**Tests:** 50+

## What This System Does

Defines quality checklists for every artifact type agents produce. 7 artifact type standards with required fields, quality criteria, and examples. Compliance is checked automatically by artifact_tracker and feeds the readiness system. Plan quality assessed at fleet_task_accept (keyword-based, free, instant). PR hygiene detects stale/conflicting/orphaned PRs. Tool enforcement requires specific MCP tools per task type.

## 7 Artifact Type Standards

| Type | Required Fields | Typical Producer |
|------|----------------|-----------------|
| task | title, requirement_verbatim, description, acceptance_criteria, task_type, task_stage, task_readiness, priority, project (9) | PM |
| bug | title, steps_to_reproduce, expected_behavior, actual_behavior, environment, impact (6) | QA, Engineer |
| analysis_document | title, scope, current_state, findings, implications (5) | Architect |
| investigation_document | title, scope, findings (3 req + options, recommendations optional) | Architect |
| plan | title, requirement_reference, approach, target_files, steps, acceptance_criteria_mapping (6) | Architect, Engineer |
| pull_request | title, description, changes, testing, task_reference (5) | Workers |
| completion_claim | pr_url, summary, acceptance_criteria_check, files_changed (4) | Workers |

## Compliance Scoring

`score = max(0, 100 - (total_issues × 15))`. Each missing required field or failed quality criterion deducts 15 points. 100 = fully compliant. Only required=True fields count. Completeness feeds artifact_tracker → suggested_readiness → PO reviews.

## Plan Quality Assessment

Runs at fleet_task_accept. 4 dimensions scored to 100:
- Steps (40 pts) — concrete implementation steps identified
- Verification (30 pts) — how to verify the work
- Risks (20 pts) — potential issues identified
- Length (10 pts) — sufficient detail

Keyword-based (instant, free, deterministic). Threshold: ≥40 acceptable, ≥70 good.

## PR Hygiene

5 issue types detected: conflicting (merge conflict, HIGH), stale (task done but PR open, MEDIUM), duplicate (multiple PRs for same task, MEDIUM), orphaned (PR without linked task, LOW), long-open (>48h, LOW).

## Tool Enforcement

Required MCP tools per task type: tasks need fleet_read_context + fleet_task_accept + fleet_commit + fleet_task_complete. Epics MUST create subtasks via fleet_task_create. Missing required tools lower confidence score in approval.

## Relationships

- CONSUMED BY: artifact_tracker.py (check completeness against standards)
- CONSUMED BY: fleet_task_accept (plan quality assessment)
- CONSUMED BY: fleet_task_complete (compliance penalty in confidence score)
- CONSUMED BY: fleet-ops review (review against standards)
- CONNECTS TO: S07 orchestrator (readiness suggestions from completeness)
- CONNECTS TO: S08 MCP tools (tool enforcement at completion)
- CONNECTS TO: S10 transpose (7 renderers produce HTML per standard)
- CONNECTS TO: S13 labor (compliance in LaborStamp)
- CONNECTS TO: S15 challenge (challenge checks against standards)
- NOT YET IMPLEMENTED: standards injection into agent context (AR-14), phase-dependent quality bars, 5 missing contribution artifact types (security_assessment, qa_test_definition, ux_spec, documentation_outline, compliance_report)

## For LightRAG Entity Extraction

Key entities: Standard (dataclass), ComplianceResult (score 0-100), ArtifactCompleteness (required_pct, suggested_readiness), PlanAssessment (4 dimensions), PRIssue (5 types), ToolRequirement (per task type).

Key relationships: Standard DEFINES required fields. Artifact tracker CHECKS compliance. Compliance FEEDS readiness suggestions. Plan quality GATES fleet_task_accept. PR hygiene DETECTS issues. Tool enforcement LOWERS confidence on missing tools.
