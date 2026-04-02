# Analysis 01 — Tools Branch of the Knowledge Map

**Date:** 2026-04-02
**Status:** ANALYSIS — mapping all MCP servers into the knowledge tree
**Purpose:** Every MCP server has a place in the map. Where each fits,
how it enhances the system, what it connects to, per role per stage.

> Every server is a capability node in the tree.
> The map doesn't filter — it organizes and connects.

---

## The MCP Server Landscape — Complete Picture

38 servers cataloged from research. 11,870+ exist in the ecosystem.
These 38 are the ones relevant to a software development fleet.

The built-in Claude Code tools (33 tools: Bash, Read, Write, Edit,
Glob, Grep, WebFetch, WebSearch, Agent, etc.) are ALWAYS available.
MCP servers ADD capabilities beyond the built-in set.

---

## MCP Servers Mapped to the Knowledge Tree

### Filesystem & Source Control

```
Tool Manuals/
├── filesystem/
│   ├── Package: @modelcontextprotocol/server-filesystem
│   ├── Tools: read_file, write_file, move_file, search_files,
│   │          create_directory, list_directory, get_file_info,
│   │          read_multiple_files (8 tools)
│   ├── Roles: ENG, QA, WRITER, DEVOPS, DEVSEC, UX, ARCH, ACCT
│   ├── Stages: work (primary), analysis, investigation
│   ├── Auth: None (path-based access control)
│   ├── Enhancement: Structured file ops vs Bash commands.
│   │   Path restrictions for security isolation per agent.
│   │   read_multiple_files for batch operations.
│   ├── Connects to:
│   │   → Agent permissions (§53 — workspace isolation)
│   │   → Worktree management (per-task file isolation)
│   │   → safety-net hook (PreToolUse validates paths)
│   └── Status: CONFIGURED in agent-tooling.yaml
│
├── git-mcp/
│   ├── Package: mcp-server-git (pip)
│   ├── Tools: git_status, git_diff, git_commit, git_log,
│   │          git_branch, git_checkout, git_show, git_init,
│   │          git_reset (9 tools)
│   ├── Roles: ENG, QA, DEVOPS, ARCH, FLEET-OPS
│   ├── Stages: work, analysis (log/diff for review)
│   ├── Auth: None (local git credentials)
│   ├── Enhancement: Structured git output vs raw Bash.
│   │   Git operations return parsed objects, not text.
│   │   Enables agent to reason about diffs structurally.
│   │   Connects git operations to trail system.
│   ├── Connects to:
│   │   → fleet_commit tool (could use git-mcp internally)
│   │   → /diff command (structured diff data)
│   │   → Trail system (commit events)
│   │   → Labor attribution (lines_added/removed from diff)
│   └── Status: NOT CONFIGURED — agents use Bash for git
│
├── github-mcp/
│   ├── Package: github/github-mcp-server (Go/Docker)
│   ├── Tools: 80+ (create_issue, create_pull_request, search_code,
│   │          get_file_contents, list_commits, list_branches,
│   │          get_workflow_runs, create_review, merge_pull_request,
│   │          get_copilot_job_status, Dependabot alerts, releases,
│   │          Projects, and 65+ more)
│   ├── Roles: ALL agents need GitHub access
│   ├── Stages: any (issues in planning, PRs in work/review, Actions in CI)
│   ├── Auth: GitHub PAT or OAuth
│   ├── Enhancement: Official GitHub server with 80+ tools.
│   │   Prompt injection protection by default.
│   │   Lockdown mode for public repos.
│   │   Covers: repos, issues, PRs, Actions, code search,
│   │   Dependabot alerts, releases, Projects.
│   │   Fleet agents can manage the full GitHub lifecycle.
│   ├── Connects to:
│   │   → fleet_task_complete (create PR, push branch)
│   │   → fleet_approve (merge PR after approval)
│   │   → CI/CD workflow management
│   │   → Dependabot → devsecops security monitoring
│   │   → Code search for investigation stage
│   └── Status: CONFIGURED via @modelcontextprotocol/server-github
│       NOTE: Using the simple MCP package, not GitHub's official
│       80+ tool server. Evaluation needed: upgrade to official?
│
└── gitlab-mcp/
    ├── Package: @modelcontextprotocol/server-gitlab
    ├── Tools: create_issue, create_merge_request, get_file,
    │          search_code, list_projects, get_pipeline_status
    ├── Roles: ENG, DEVOPS, PM, QA
    ├── Stages: any
    ├── Auth: GITLAB_PERSONAL_ACCESS_TOKEN
    ├── Enhancement: Full GitLab lifecycle.
    │   Cloud and self-hosted support.
    │   Pipeline status monitoring.
    ├── Connects to:
    │   → CI/CD workflows (pipeline management)
    │   → Code search (investigation stage)
    └── Status: NOT CONFIGURED — we use GitHub, not GitLab.
        Available if projects migrate or use both platforms.
```

### Containers & Infrastructure

```
Tool Manuals/
├── docker-mcp/
│   ├── Package: mcp-server-docker
│   ├── Tools: 25 tools across containers (list/create/run/stop/logs),
│   │          images (list/pull/push/build), networks, volumes
│   ├── Roles: DEVOPS (primary), DEVSEC, ENG, QA
│   ├── Stages: work (container ops), investigation (inspect containers)
│   ├── Auth: Docker socket access
│   ├── Enhancement: Full Docker lifecycle as structured tools.
│   │   Build images, manage networks, inspect volumes.
│   │   Container logs as structured data for debugging.
│   ├── Connects to:
│   │   → foundation-docker skill (containerization workflow)
│   │   → ops-deploy skill (deployment with containers)
│   │   → LocalAI container management
│   │   → OCMC docker-compose stack
│   └── Status: CONFIGURED for DEVOPS, DEVSEC
│
├── kubectl-mcp/
│   ├── Package: kubectl-mcp-server (npm + pip)
│   ├── Tools: 253 tools — pods, deployments, services, Helm,
│   │          GitOps (Flux/ArgoCD), cluster management
│   ├── Roles: DEVOPS, ARCH
│   ├── Stages: work (deploy), investigation (cluster state)
│   ├── Auth: kubeconfig
│   ├── Enhancement: Massive Kubernetes toolset.
│   │   Helm operations for package management.
│   │   GitOps integration (Flux, ArgoCD).
│   │   253 tools cover every K8s operation.
│   ├── Connects to:
│   │   → ops-deploy (K8s deployment)
│   │   → ops-scale (horizontal scaling, replicas)
│   │   → infra-monitoring (K8s health)
│   │   → Multi-fleet infrastructure (Machine 1 ↔ Machine 2)
│   └── Status: NOT CONFIGURED — no K8s cluster yet.
│       Adopt when infrastructure scales to K8s.
│       High value when Machine 2 comes online.
│
├── k8s-secure/
│   ├── Package: alexei-led/k8s-mcp-server (Docker)
│   ├── Tools: kubectl_exec, helm_exec, istioctl_exec, argocd_exec
│   ├── Roles: DEVOPS, ARCH
│   ├── Stages: work
│   ├── Auth: kubeconfig mounted into container
│   ├── Enhancement: SANDBOXED K8s operations.
│   │   Runs kubectl/helm/istio/argocd inside Docker.
│   │   Security isolation — agent can't escape sandbox.
│   │   Native EKS/GKE/AKS support.
│   ├── Connects to:
│   │   → kubectl-mcp (alternative with security layer)
│   │   → Agent permissions (sandbox model)
│   └── Status: NOT CONFIGURED — no K8s. Future consideration
│       when security-isolated K8s access needed.
│
└── terraform-mcp/
    ├── Package: hashicorp/terraform-mcp-server (Docker)
    ├── Tools: search_providers, get_provider_docs, search_modules,
    │          get_module_details, validate_config
    ├── Roles: DEVOPS, ARCH
    ├── Stages: investigation (provider docs), reasoning (module selection), work (validate)
    ├── Auth: None (docs/guidance only — no cloud API access)
    ├── Enhancement: Official HashiCorp server.
    │   Provider documentation lookup.
    │   Module search and evaluation.
    │   Config validation without applying.
    │   Safe — does NOT interact with cloud providers.
    ├── Connects to:
    │   → HashiCorp Terraform skills (11 from VoltAgent)
    │   → infrastructure-as-code patterns
    │   → ops-deploy (IaC deployment)
    └── Status: NOT CONFIGURED — no Terraform in current stack.
        Available when IaC expands beyond Docker Compose.
```

### Databases

```
Tool Manuals/
├── postgresql-mcp/
│   ├── Package: @modelcontextprotocol/server-postgres
│   ├── Tools: query, list_tables, describe_table, get_schema (read-only)
│   ├── Roles: ENG, QA, ARCH, DEVOPS
│   ├── Stages: analysis (schema inspection), investigation (data queries)
│   ├── Auth: PostgreSQL connection string
│   ├── Enhancement: Structured database access.
│   │   Schema inspection for architecture analysis.
│   │   Read-only queries for data investigation.
│   │   OCMC uses PostgreSQL — agents could inspect fleet data.
│   ├── Connects to:
│   │   → foundation-database skill
│   │   → OCMC PostgreSQL (port 5433)
│   │   → Architecture review (schema analysis)
│   └── Status: NOT CONFIGURED — agents use MC API, not direct DB.
│       Value: direct schema inspection for architecture decisions.
│       Risk: bypasses MC API abstraction layer.
│
├── sqlite-mcp/
│   ├── Package: mcp-server-sqlite (pip)
│   ├── Tools: read_query, write_query, create_table, list_tables,
│   │          describe_table, append_insight (6 tools)
│   ├── Roles: ENG, QA, PM
│   ├── Stages: work (data operations), analysis (schema inspection)
│   ├── Auth: File path
│   ├── Enhancement: Our fleet uses SQLite extensively:
│   │   - Event store (JSONL backed by SQLite)
│   │   - RAG databases (rag.py, kb.py)
│   │   - claude-mem storage
│   │   - Session telemetry
│   │   Agents could inspect and query fleet's own data stores.
│   │   append_insight tool for data analysis annotations.
│   ├── Connects to:
│   │   → Fleet event store
│   │   → AICP rag.py / kb.py SQLite stores
│   │   → claude-mem SQLite database
│   │   → LightRAG (can use SQLite backend)
│   └── Status: NOT CONFIGURED — high potential for fleet self-awareness.
│
├── redis-mcp/
│   ├── Package: redis/mcp-redis
│   ├── Tools: get, set, delete, search, list_keys, hash_operations
│   ├── Roles: ENG, DEVOPS, FLEET-OPS
│   ├── Stages: work, investigation
│   ├── Auth: Redis connection URL
│   ├── Enhancement: OCMC stack includes Redis (port 6379).
│   │   Cache inspection for debugging.
│   │   Session cache management.
│   │   Could enable fleet-ops to inspect OCMC cache state.
│   ├── Connects to:
│   │   → OCMC Redis (session cache)
│   │   → Debugging workflows
│   └── Status: NOT CONFIGURED — Redis is internal to OCMC stack.
│       Value if agents need cache debugging.
│
└── dbhub/
    ├── Package: bytebase/dbhub (Go/Docker)
    ├── Tools: unified query, list_tables, describe_table, get_schema
    │          across PostgreSQL, MySQL, MariaDB, SQL Server, SQLite
    ├── Roles: ENG, QA, DEVOPS
    ├── Stages: analysis, investigation
    ├── Auth: Database connection strings
    ├── Enhancement: Single interface for ALL databases.
    │   Zero-dependency, token-efficient.
    │   Useful when fleet manages multiple database types.
    ├── Connects to:
    │   → postgresql-mcp + sqlite-mcp (unified alternative)
    │   → foundation-database skill
    └── Status: NOT CONFIGURED — single-database alternative
        to installing postgres + sqlite MCPs separately.
```

### Browser & Web

```
Tool Manuals/
├── playwright-mcp/
│   ├── Package: @playwright/mcp
│   ├── Tools: browser_navigate, browser_click, browser_type,
│   │          browser_snapshot, browser_tab_list,
│   │          browser_console_messages (6 tools)
│   ├── Roles: QA, ENG, UX
│   ├── Stages: work (UI testing), investigation (web research)
│   ├── Auth: None
│   ├── Enhancement: Microsoft's official MCP server.
│   │   Accessibility snapshots (not screenshots) — structured data.
│   │   Headless by default — works in gateway sessions.
│   │   Browser automation for testing, scraping, interaction.
│   ├── Connects to:
│   │   → playwright-pro skill (9 sub-skills from alirezarezvani)
│   │   → webapp-testing skill (anthropics/skills)
│   │   → quality-accessibility skill (UX)
│   │   → foundation-testing skill
│   └── Status: CONFIGURED for ENG, QA, UX
│
├── puppeteer-mcp/
│   ├── Package: @modelcontextprotocol/server-puppeteer
│   ├── Tools: navigate, screenshot, click, fill, evaluate (5 tools)
│   ├── Roles: QA, ENG, UX
│   ├── Stages: work, investigation
│   ├── Auth: None
│   ├── Enhancement: Screenshot-based (vs Playwright's accessibility).
│   │   JavaScript evaluation in browser context.
│   │   Alternative approach — visual vs structural.
│   ├── Connects to:
│   │   → playwright-mcp (alternative approach)
│   │   → UX visual testing workflows
│   └── Status: NOT CONFIGURED — Playwright already covers browser.
│       Value: screenshot-based testing where visual verification needed.
│
├── brave-search/
│   ├── Package: @modelcontextprotocol/server-brave-search
│   ├── Tools: brave_web_search, brave_local_search (2 tools)
│   ├── Roles: ENG, WRITER, ARCH, PM
│   ├── Stages: investigation (research), analysis (context gathering)
│   ├── Auth: BRAVE_API_KEY
│   ├── Enhancement: Structured search results with snippets.
│   │   Local search capability (find nearby businesses/services).
│   │   Alternative to built-in WebSearch.
│   ├── Connects to:
│   │   → Built-in WebSearch (complementary — different engine)
│   │   → Agent research capability (U-10)
│   │   → Context7 (library docs vs web search)
│   └── Status: NOT CONFIGURED — built-in WebSearch may suffice.
│       Value: when agents need diverse search sources for research.
│
├── fetch-mcp/
│   ├── Package: mcp-server-fetch (pip)
│   ├── Tools: fetch (with start_index for pagination) (1 tool)
│   ├── Roles: ALL
│   ├── Stages: investigation, analysis
│   ├── Auth: None
│   ├── Enhancement: HTML → markdown conversion.
│   │   Chunked reading for large pages.
│   │   Alternative to built-in WebFetch.
│   ├── Connects to:
│   │   → Built-in WebFetch (complementary)
│   │   → Research workflows
│   └── Status: NOT CONFIGURED — built-in WebFetch covers this.
│       Value: chunked reading for very large pages.
│
├── tavily-mcp/
│   ├── Package: tavily-mcp (npm)
│   ├── Tools: search, extract, map, crawl (4 tools)
│   ├── Roles: ENG, WRITER, ARCH, PM
│   ├── Stages: investigation
│   ├── Auth: TAVILY_API_KEY
│   ├── Enhancement: Advanced search with real-time results.
│   │   Intelligent data extraction from pages.
│   │   Site crawling and mapping.
│   │   More structured than raw web search.
│   ├── Connects to:
│   │   → Agent research capability (U-10)
│   │   → Knowledge gathering for LightRAG ingestion
│   └── Status: NOT CONFIGURED — requires paid API key.
│       Value: deep research where built-in search isn't enough.
│
└── exa-search/
    ├── Package: Remote MCP at https://mcp.exa.ai/mcp
    ├── Tools: search, find_similar, get_contents (3 tools)
    ├── Roles: ENG, WRITER, ARCH
    ├── Stages: investigation
    ├── Auth: Exa API key
    ├── Enhancement: AI-native semantic search.
    │   Neural embeddings for similarity.
    │   Find pages SIMILAR to a reference page.
    │   Content extraction with structure.
    ├── Connects to:
    │   → LightRAG (semantic search complement)
    │   → Agent research capability (U-10)
    └── Status: NOT CONFIGURED — remote MCP, requires API key.
        Value: semantic search when keyword search fails.
```

### Code Quality & Security

```
Tool Manuals/
├── eslint-mcp/
│   ├── Package: @eslint/mcp
│   ├── Tools: lint, get_rule_docs, fix (3 tools)
│   ├── Roles: ENG, QA
│   ├── Stages: work (lint + fix), analysis (rule exploration)
│   ├── Auth: None
│   ├── Enhancement: Official ESLint MCP.
│   │   AI-powered pattern detection.
│   │   Auto-fix capabilities.
│   │   Rule documentation lookup.
│   ├── Connects to:
│   │   → quality-lint skill
│   │   → feature-review (code quality check)
│   │   → PostToolUse hook (auto-lint after edits)
│   └── Status: NOT CONFIGURED — our stack is Python, not JS.
│       Value: if fleet works on JS/TS projects.
│       Python equivalent: ruff/flake8 (not MCP — CLI via Bash).
│
├── semgrep-mcp/
│   ├── Package: semgrep (pip, MCP mode)
│   ├── Tools: scan, get_findings, list_rules, apply_fix (4 tools)
│   ├── Roles: DEVSEC (primary), QA, ENG
│   ├── Stages: investigation (scan), work (fix), analysis (findings review)
│   ├── Auth: Optional (Semgrep App token for custom rules)
│   ├── Enhancement: Static analysis across 30+ languages.
│   │   Custom rule support — write rules for OUR codebase patterns.
│   │   Free tier sufficient for fleet use.
│   │   Catches CODE-LEVEL vulnerabilities (vs Trivy's dep/container focus).
│   ├── Connects to:
│   │   → Trail of Bits semgrep-rule-creator skill
│   │   → infra-security skill
│   │   → fleet-security-audit skill
│   │   → DevSecOps CLAUDE.md (security layer)
│   │   → Challenge system (automated security challenge)
│   └── Status: NOT CONFIGURED — high value for code security.
│       Complements Trivy (different layer: code patterns vs dependencies).
│
├── snyk-mcp/
│   ├── Package: snyk CLI (built-in MCP, v1.6.1+)
│   ├── Tools: 11 tools — sast_scan, sca_scan, iac_scan,
│   │          container_scan, sbom_generate, ai_bom,
│   │          get_vulnerabilities, fix_suggestion, and more
│   ├── Roles: DEVSEC, DEVOPS, ENG
│   ├── Stages: investigation (scan), work (fix), analysis (SBOM)
│   ├── Auth: SNYK_TOKEN (freemium)
│   ├── Enhancement: Most comprehensive security MCP.
│   │   SAST + SCA + IaC + container + SBOM + AI-BOM in ONE server.
│   │   Fix suggestions with actual code changes.
│   │   AI-BOM for tracking AI dependencies.
│   │   Covers every security dimension.
│   ├── Connects to:
│   │   → All security skills and workflows
│   │   → Challenge system (security challenge type)
│   │   → fleet-security-audit skill
│   │   → LaborStamp (security_hold tracking)
│   └── Status: NOT CONFIGURED — requires SNYK_TOKEN.
│       Most comprehensive option if budget allows.
│       Free tier covers basic scanning.
│
├── trivy-mcp/
│   ├── Package: trivy + MCP plugin
│   ├── Tools: scan_image, scan_filesystem, scan_repo,
│   │          scan_config, get_vulnerabilities (5 tools)
│   ├── Roles: DEVSEC, DEVOPS
│   ├── Stages: investigation (scan), analysis (findings)
│   ├── Auth: None — fully open source
│   ├── Enhancement: Open source vulnerability scanner.
│   │   Containers, filesystems, repos, IaC configs.
│   │   No token needed — zero cost.
│   │   Most accessible security entry point.
│   │   Aqua Security maintained.
│   ├── Connects to:
│   │   → docker-mcp (container scanning)
│   │   → foundation-docker skill
│   │   → fleet-security-audit skill
│   │   → Dependency vulnerability tracking
│   └── Status: NOT CONFIGURED — high value, zero cost.
│       Recommended as baseline security scanner.
│
└── devsecops-mcp/
    ├── Package: devsecops-mcp (pip)
    ├── Tools: 6 tools aggregating SAST (Semgrep+Bandit+SonarQube),
    │          DAST (OWASP ZAP), IAST, SCA (npm audit+OSV+Trivy)
    ├── Roles: DEVSEC
    ├── Stages: investigation, analysis
    ├── Auth: Varies by underlying tool
    ├── Enhancement: UNIFIED security interface.
    │   Single MCP wrapping 6+ security tools.
    │   SAST + DAST + IAST + SCA in one server.
    │   Generates consolidated security reports.
    ├── Connects to:
    │   → semgrep-mcp (uses Semgrep internally)
    │   → trivy-mcp (uses Trivy internally)
    │   → fleet-security-audit skill
    └── Status: NOT CONFIGURED — aggregator approach.
        Alternative to installing Semgrep + Trivy individually.
        Adds DAST (ZAP) which individual tools don't cover.
```

### Testing

```
Tool Manuals/
├── test-runner-mcp/
│   ├── Package: @iflow-mcp/mcp-test-runner (npm)
│   ├── Tools: run_tests, get_test_results, list_test_suites (3 tools)
│   ├── Roles: QA, ENG
│   ├── Stages: work
│   ├── Auth: None
│   ├── Enhancement: UNIFIED testing interface.
│   │   Pytest, Jest, Bats, Flutter, Go, Rust through ONE endpoint.
│   │   Useful when fleet works on multi-language projects.
│   ├── Connects to:
│   │   → foundation-testing skill
│   │   → fleet-test skill (fleet review testing)
│   │   → fleet_task_complete (test gate)
│   └── Status: NOT CONFIGURED — value for multi-language projects.
│
└── pytest-mcp/
    ├── Package: pytest-mcp-server (pip)
    ├── Tools: get_failures, analyze_error, suggest_fix,
    │          get_test_history, run_specific_test, get_coverage,
    │          debug_trace, compare_runs (8 tools)
    ├── Roles: QA (primary), ENG
    ├── Stages: work (test + fix), investigation (failure analysis)
    ├── Auth: None
    ├── Enhancement: Deep pytest integration.
    │   Failure analysis with root cause.
    │   Coverage tracking with gaps.
    │   Debug trace for complex failures.
    │   Compare runs (regression detection).
    │   Suggest fixes based on error patterns.
    │   OUR STACK IS PYTHON — this is directly relevant.
    ├── Connects to:
    │   → quality-coverage skill (coverage tracking)
    │   → systematic-debugging (Superpowers)
    │   → fleet-test skill (review testing)
    │   → /debug command
    │   → Challenge system (automated challenge from test results)
    │   → fleet_task_complete (test gate before PR)
    └── Status: NOT CONFIGURED — high value for our Python stack.
```

### Documentation & Knowledge

```
Tool Manuals/
└── context7-mcp/
    ├── Package: @upstash/context7-mcp (47K stars)
    ├── Tools: resolve-library-id, query-docs (2 tools)
    ├── Roles: ENG, ARCH, WRITER
    ├── Stages: investigation (research libraries), work (reference docs)
    ├── Auth: Optional API key for higher limits
    ├── Enhancement: Up-to-date library/framework documentation.
    │   Version-specific — prevents hallucinated APIs.
    │   Replaces stale training data with current docs.
    │   47K stars — most popular docs MCP.
    ├── Connects to:
    │   → context7 plugin (different — plugin injects context,
    │     MCP server provides tools for on-demand queries)
    │   → Agent research capability (U-10)
    │   → foundation-deps skill (dependency management)
    │   → Architecture decisions (library evaluation)
    └── Status: CONFIGURED as plugin for ARCH, ENG.
        MCP server version NOT configured — would add
        tool-based query access alongside the plugin.
```

### Project Management

```
Tool Manuals/
├── plane-mcp/
│   ├── Package: makeplane/plane-mcp-server (npm/Docker)
│   ├── Tools: list_projects, create_issue, update_issue,
│   │          list_cycles, list_modules, search
│   ├── Roles: PM, FLEET-OPS, ENG
│   ├── Stages: any (sprint management is continuous)
│   ├── Auth: Plane API key
│   ├── Enhancement: Official Plane MCP server.
│   │   WE SELF-HOST PLANE (DSPD project).
│   │   Stdio, SSE, and streamable HTTP transports.
│   │   Could replace or complement our direct API calls
│   │   in plane_sync.py with standard MCP integration.
│   ├── Connects to:
│   │   → plane_sync.py (existing direct API integration)
│   │   → fleet-plane skill (sprint management)
│   │   → PM heartbeat (sprint data)
│   │   → fleet_plane_* MCP tools (our 7 Plane tools)
│   └── Status: NOT CONFIGURED — we use direct API.
│       Evaluation: standard MCP vs our custom integration.
│       Both could coexist — MCP for agents, direct for brain.
│
├── notion-mcp/
│   ├── Package: Remote MCP at https://mcp.notion.so/mcp
│   ├── Tools: search, get_page, create_page, update_page,
│   │          query_database, create_database
│   ├── Roles: PM, WRITER, ARCH
│   ├── Stages: any
│   ├── Auth: OAuth flow
│   ├── Enhancement: Full Notion workspace access.
│   │   Pages, databases, blocks.
│   │   Knowledge management integration.
│   ├── Connects to:
│   │   → Knowledge base workflows
│   │   → Documentation management
│   └── Status: NOT CONFIGURED — we use Plane, not Notion.
│       Available if knowledge management needs expand.
│
├── confluence-mcp/
│   ├── Package: @aashari/mcp-server-atlassian-confluence (npm)
│   ├── Tools: list_spaces, get_page, search_content,
│   │          create_page, update_page
│   ├── Roles: WRITER, PM, ARCH
│   ├── Stages: any
│   ├── Auth: Atlassian API token
│   ├── Enhancement: Confluence knowledge base access.
│   │   Content as Markdown (LLM-friendly).
│   │   CQL search support.
│   ├── Connects to:
│   │   → Documentation workflows
│   │   → Knowledge sharing
│   └── Status: NOT CONFIGURED — no Confluence.
│       Available if team uses Atlassian stack.
│
├── github-actions-mcp/
│   ├── Package: github-actions-mcp-server (npm)
│   ├── Tools: list_workflows, trigger_workflow, get_workflow_run,
│   │          cancel_run, rerun_workflow, get_job_logs, list_artifacts
│   ├── Roles: DEVOPS, QA, FLEET-OPS
│   ├── Stages: work (trigger/manage CI), analysis (check results)
│   ├── Auth: GitHub PAT
│   ├── Enhancement: Full GitHub Actions lifecycle.
│   │   Trigger, monitor, cancel, rerun workflows.
│   │   Job log analysis for failure debugging.
│   │   Artifact management.
│   │   NOTE: github/github-mcp-server (configured) may
│   │   already include Actions via get_workflow_runs.
│   ├── Connects to:
│   │   → foundation-ci skill (CI/CD setup)
│   │   → ops-deploy skill (deployment via Actions)
│   │   → fleet_task_complete (CI gate before PR)
│   └── Status: NOT CONFIGURED — check if existing GitHub
│       MCP already covers Actions. If not, add this.
│
├── linear-mcp/
│   ├── Package: Remote MCP at https://mcp.linear.app/sse
│   ├── Tools: search_issues, create_issue, update_issue,
│   │          get_project, add_comment, list_teams
│   ├── Roles: PM, ENG, FLEET-OPS, ACCT
│   ├── Stages: any
│   ├── Auth: OAuth flow
│   ├── Enhancement: Linear issue tracking.
│   │   Official MCP with OAuth.
│   │   Community API-key version for headless.
│   ├── Connects to:
│   │   → Project management workflows
│   └── Status: NOT CONFIGURED — we use Plane, not Linear.
│       Available if project tracking needs change.
│
└── jira-mcp/
    ├── Package: @aashari/mcp-server-atlassian-jira (npm)
    ├── Tools: list_projects, get_issue, search_issues,
    │          create_issue, update_issue, get_dev_info, add_comment
    ├── Roles: PM, ENG, FLEET-OPS
    ├── Stages: any
    ├── Auth: Atlassian API token
    ├── Enhancement: Full Jira lifecycle with JQL.
    │   Dev info integration (commits, PRs).
    │   Production-ready with error handling.
    ├── Connects to:
    │   → Project management workflows
    │   → Sprint management
    └── Status: NOT CONFIGURED — we use Plane, not Jira.
        Available if team uses Atlassian stack.
```

### Communication

```
Tool Manuals/
└── slack-mcp/
    ├── Package: @modelcontextprotocol/server-slack (official plugin)
    ├── Tools: list_channels, post_message, reply_to_thread,
    │          search_messages, get_channel_history, get_users
    ├── Roles: PM, FLEET-OPS, ACCT (if Slack used)
    ├── Stages: any
    ├── Auth: SLACK_BOT_TOKEN, SLACK_TEAM_ID
    ├── Enhancement: Full Slack workspace interaction.
    │   Channel management, threading, search.
    │   Agent-to-human communication via Slack.
    ├── Connects to:
    │   → fleet-communicate skill (communication surface guide)
    │   → Notification routing (alternative to IRC+ntfy)
    └── Status: NOT CONFIGURED — we use IRC (miniircd) + ntfy.
        Available if communication stack changes.
        Could complement IRC for external-facing communication.
```

### Monitoring & Observability

```
Tool Manuals/
├── sentry-mcp/
│   ├── Package: getsentry/sentry-mcp
│   ├── Tools: get_issues, get_issue_details, search_issues,
│   │          resolve_issue, get_events
│   ├── Roles: QA, ENG, DEVOPS
│   ├── Stages: investigation (error analysis), work (resolve)
│   ├── Auth: Sentry auth token
│   ├── Enhancement: Error monitoring integration.
│   │   Issue retrieval and analysis.
│   │   Event inspection for debugging.
│   │   Resolution tracking.
│   ├── Connects to:
│   │   → Sentry skills (7 from VoltAgent)
│   │   → ops-incident skill
│   │   → systematic-debugging (Superpowers)
│   └── Status: NOT CONFIGURED — no Sentry instance.
│       High value if error monitoring added to fleet stack.
│
├── prometheus-mcp/
│   ├── Package: prometheus-mcp-server (npm + pip)
│   ├── Tools: query_instant, query_range, list_metrics,
│   │          get_targets, get_alerts, get_rules
│   ├── Roles: DEVOPS, FLEET-OPS
│   ├── Stages: investigation (metrics), analysis (alerts)
│   ├── Auth: Prometheus endpoint URL
│   ├── Enhancement: PromQL queries via MCP.
│   │   Metric discovery and metadata.
│   │   Alert and rule inspection.
│   │   Target monitoring.
│   ├── Connects to:
│   │   → infra-monitoring skill
│   │   → observability-designer skill (alirezarezvani)
│   │   → Storm monitor (external metrics source)
│   └── Status: NOT CONFIGURED — no Prometheus instance.
│       Available when monitoring stack expands.
│
├── grafana-mcp/
│   ├── Package: grafana/mcp-grafana
│   ├── Tools: search_dashboards, query_datasource, list_incidents,
│   │          get_trace, query_loki_logs
│   ├── Roles: DEVOPS, FLEET-OPS, ACCT
│   ├── Stages: investigation, analysis
│   ├── Auth: Grafana API key
│   ├── Enhancement: Dashboard + datasource + tracing.
│   │   Distributed tracing via TraceQL.
│   │   Loki log queries.
│   │   Incident management.
│   ├── Connects to:
│   │   → prometheus-mcp (Grafana visualizes Prometheus)
│   │   → infra-monitoring skill
│   │   → ops-incident skill
│   └── Status: NOT CONFIGURED — no Grafana instance.
│       Available when observability stack added.
│
└── datadog-mcp/
    ├── Package: Datadog MCP Server (hosted)
    ├── Tools: query_metrics, search_logs, get_traces,
    │          list_incidents, get_dashboards
    ├── Roles: DEVOPS, FLEET-OPS
    ├── Stages: investigation, analysis
    ├── Auth: Datadog API/app key
    ├── Enhancement: Full observability platform.
    │   Metrics, logs, traces, incidents unified.
    │   Useful during incident response.
    ├── Connects to:
    │   → ops-incident skill
    │   → Monitoring workflows
    └── Status: NOT CONFIGURED — no Datadog.
        Alternative to Prometheus+Grafana (commercial).
```

### Memory & Knowledge

```
Tool Manuals/
├── memory-mcp/
│   ├── Package: @modelcontextprotocol/server-memory (official)
│   ├── Tools: create_entity, add_observation, create_relation,
│   │          search_nodes, open_nodes, delete_entity (6 tools)
│   ├── Roles: FLEET-OPS, ARCH, PM
│   ├── Stages: any
│   ├── Auth: None
│   ├── Enhancement: Knowledge graph as MCP server.
│   │   Entities, observations, relationships.
│   │   Persists via JSON file.
│   │   Lightweight alternative to LightRAG for structured knowledge.
│   ├── Connects to:
│   │   → Knowledge map (could be implementation layer)
│   │   → LightRAG (complementary — memory-mcp is simpler)
│   │   → claude-mem (different layer — tool memory vs session memory)
│   │   → Fleet knowledge persistence
│   └── Status: NOT CONFIGURED — evaluate alongside LightRAG.
│       Could serve as lightweight knowledge store for agents.
│
└── sequential-thinking/
    ├── Package: @modelcontextprotocol/server-sequential-thinking (official)
    ├── Tools: sequentialthinking (with thought, nextThoughtNeeded,
    │          thoughtNumber, totalThoughts, isRevision, branchFromThought,
    │          branchId)
    ├── Roles: ARCH, PM, ENG
    ├── Stages: reasoning (primary), analysis, investigation
    ├── Auth: None
    ├── Enhancement: Structured step-by-step reasoning.
    │   72K weekly npm downloads.
    │   Thought management with revision and branching.
    │   Forces explicit reasoning chain.
    │   Prevents jumping to conclusions.
    ├── Connects to:
    │   → brainstorming skill (Superpowers)
    │   → writing-plans skill (Superpowers)
    │   → Architecture decisions (REASONING stage)
    │   → /plan command
    └── Status: NOT CONFIGURED — high potential for architect.
        Structured reasoning for complex design decisions.
```

### Design & Diagrams

```
Tool Manuals/
├── figma-mcp/
│   ├── Package: Remote MCP at https://mcp.figma.com/mcp
│   ├── Tools: get_design_context, get_screenshot,
│   │          get_variable_defs, get_code_connect
│   ├── Roles: UX, ENG
│   ├── Stages: work (implement designs), analysis (inspect designs)
│   ├── Auth: Figma OAuth (free during beta)
│   ├── Enhancement: Design context from Figma files.
│   │   Code Connect maps Figma components to codebase.
│   │   Variable definitions for design tokens.
│   │   Screenshots of specific frames/components.
│   ├── Connects to:
│   │   → UX designer workflow
│   │   → Frontend implementation
│   │   → Design system management
│   └── Status: NOT CONFIGURED — no Figma currently.
│       Available if design workflow uses Figma.
│
├── diagram-bridge-mcp/
│   ├── Package: diagram-bridge-mcp (npm)
│   ├── Tools: select_format, generate_instructions, render_diagram
│   ├── Roles: ARCH, WRITER, UX
│   ├── Stages: reasoning (architecture diagrams), work (documentation)
│   ├── Auth: None (uses public Kroki server or self-hosted)
│   ├── Enhancement: 10+ diagram formats:
│   │   Mermaid, PlantUML, C4, D2, GraphViz, BPMN,
│   │   Structurizr, Excalidraw, Vega-Lite.
│   │   RENDERS to images — not just syntax.
│   │   Agents can produce visual architecture diagrams.
│   ├── Connects to:
│   │   → Architecture documentation
│   │   → Fleet diagrams (fleet-master-diagrams.md)
│   │   → System manual visualization
│   │   → Knowledge map visualization
│   └── Status: NOT CONFIGURED — rendering adds visual output.
│       Value: visual architecture documentation.
│
├── mermaid-mcp/
│   ├── Package: mermaid-mcp-server (npm)
│   ├── Tools: render_mermaid, validate_mermaid
│   ├── Roles: ARCH, WRITER
│   ├── Stages: work (documentation)
│   ├── Auth: None
│   ├── Enhancement: Mermaid → PNG rendering.
│   │   Validate syntax before rendering.
│   │   Simpler than diagram-bridge (Mermaid only).
│   ├── Connects to:
│   │   → diagram-bridge-mcp (Mermaid is one of 10+ formats)
│   │   → Architecture documentation
│   └── Status: NOT CONFIGURED — diagram-bridge covers Mermaid
│       plus 9 other formats. Use bridge instead of standalone.
│
└── excalidraw-mcp/
    ├── Package: yctimlin/mcp_excalidraw (npm from repo)
    ├── Tools: create_diagram, add_element, edit_element,
    │          export_svg, export_png, get_canvas_state
    ├── Roles: UX, ARCH, WRITER
    ├── Stages: reasoning (sketching), work (documentation)
    ├── Auth: None
    ├── Enhancement: Programmatic canvas toolkit.
    │   Create, edit, export diagrams.
    │   Agents can SEE what they drew (canvas state).
    │   Hand-drawn style diagrams (informal, collaborative).
    ├── Connects to:
    │   → UX design workflows
    │   → Architecture sketching
    │   → Collaborative design
    └── Status: NOT CONFIGURED — informal diagram creation.
        Value: UX wireframing, architecture sketching.
```

### Package Management & Dependencies

```
Tool Manuals/
├── package-registry-mcp/
│   ├── Package: package-registry-mcp (npm)
│   ├── Tools: search_packages, get_package_info,
│   │          get_latest_version, compare_versions
│   ├── Roles: ENG, DEVOPS
│   ├── Stages: investigation (evaluate packages), work (version management)
│   ├── Auth: None
│   ├── Enhancement: Search NPM, Cargo, PyPI, NuGet.
│   │   Version checking and comparison.
│   │   Package metadata retrieval.
│   ├── Connects to:
│   │   → foundation-deps skill
│   │   → Dependency management workflows
│   │   → Context7 (docs for chosen packages)
│   └── Status: NOT CONFIGURED — useful for dependency decisions.
│
├── dependency-mcp/
│   ├── Package: dependency-mcp (npm)
│   ├── Tools: check_version, get_latest, list_dependencies
│   ├── Roles: ENG, DEVOPS, DEVSEC
│   ├── Stages: analysis (audit), work (update)
│   ├── Auth: None
│   ├── Enhancement: Version checking across 7 registries:
│   │   NPM, PyPI, Maven, NuGet, RubyGems, Crates.io, Go.
│   ├── Connects to:
│   │   → ops-maintenance skill (dependency updates)
│   │   → Security scanning (outdated deps)
│   └── Status: NOT CONFIGURED — version tracking across ecosystems.
│
└── mcp-pypi/
    ├── Package: mcp-pypi (pip)
    ├── Tools: scan_package, audit_dependencies,
    │          get_vulnerabilities, check_license
    ├── Roles: DEVSEC, ENG
    ├── Stages: investigation (audit), analysis (license check)
    ├── Auth: None
    ├── Enhancement: SECURITY-FOCUSED Python package analysis.
    │   Vulnerability scanning per package.
    │   Dependency auditing.
    │   License compliance checking.
    │   DIRECTLY RELEVANT — our stack is Python.
    ├── Connects to:
    │   → infra-security skill
    │   → fleet-security-audit skill
    │   → foundation-deps skill
    │   → Trivy (complementary — Trivy scans containers, this scans PyPI)
    └── Status: NOT CONFIGURED — high value for Python security.
```

---

## How Tools Connect to Other Map Branches

| Tool Category | Connects To |
|--------------|------------|
| Filesystem + Git | → Agent permissions, worktree management, safety-net hook |
| GitHub | → fleet_task_complete, fleet_approve, CI/CD, Dependabot |
| Docker + K8s | → foundation-docker, ops-deploy, LocalAI management |
| Databases | → Event store, RAG, claude-mem, architecture analysis |
| Browser | → QA testing, playwright-pro skill, quality-accessibility |
| Search/Fetch | → Agent research (U-10), investigation stage, LightRAG |
| Security (Semgrep/Snyk/Trivy) | → infra-security, fleet-security-audit, Trail of Bits skills |
| Testing (pytest-mcp) | → quality-coverage, fleet-test, /debug, challenge system |
| Context7 | → foundation-deps, architecture decisions, investigation |
| Plane MCP | → fleet-plane skill, PM heartbeat, sprint management |
| Memory/Sequential | → Knowledge map, LightRAG, reasoning stage, brainstorming |
| Diagrams | → Architecture docs, system visualization, knowledge map |
| Package mgmt | → foundation-deps, ops-maintenance, security auditing |

---

## PO Decision Points

1. **GitHub MCP upgrade:** Switch from simple @modelcontextprotocol/server-github to official github/github-mcp-server (80+ tools)?
2. **Security stack:** Trivy (free baseline) + Semgrep (code patterns) + mcp-pypi (Python deps)? Or Snyk (all-in-one, needs token)?
3. **Plane MCP:** Complement or replace our direct API integration?
4. **pytest-mcp:** Install for QA + ENG? (directly relevant — Python stack)
5. **Context7:** Add MCP server version alongside existing plugin?
6. **SQLite MCP:** Enable agent access to fleet's own data stores?
7. **Sequential thinking:** Value for architect reasoning stage?
8. **Diagram rendering:** diagram-bridge for visual architecture docs?
9. **Git MCP:** Structured git output vs raw Bash — worth the addition?
10. **Memory MCP:** Lightweight knowledge graph alongside LightRAG?
