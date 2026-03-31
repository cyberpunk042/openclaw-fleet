# Standards and Quality Framework

**Date:** 2026-03-30
**Status:** Design — quality standards the fleet imposes on its work
**Part of:** Fleet Elevation (document 17 of 22)

---

## PO Requirements (Verbatim)

> "we need to make sure a clean structure is respected and SRP, Domain,
> Onion and all the goods standard we want to impose our fleet."

> "we need to do a gold job, we need to elevate the quality and the
> standard."

> "The documentation and the tasks and sub-tasks details and comments
> and all artifacts have to be strong. high standards."

> "This is why we have multiple specialist and multiple stage and
> methodologies."

---

## What This Document Covers

The quality standards the fleet IMPOSES on the work it produces. When
agents write code, it follows SRP. When they design architecture, it
follows Domain-Driven Design and Onion Architecture. When they produce
documentation, it's comprehensive and accurate. When they deliver
artifacts, they meet completeness standards per delivery phase.

These are the standards the fleet applies to its OUTPUT — the code
it commits, the architectures it designs, the documents it writes,
the tests it creates, the PRs it submits.

---

## Code Standards — What Agents Must Follow

### SRP (Single Responsibility Principle)
Every module, class, and function the fleet writes has ONE job:
- One module = one concern
- One class = one entity or service
- One function = one operation
- No god objects, no kitchen-sink modules
- If a file does two things, split it

The architect enforces this in design contributions. Fleet-ops
checks during review. The immune system detects when agents produce
monolithic code.

### Domain-Driven Design
Code the fleet produces is organized by domain:
- Domain entities are pure data (no infrastructure imports)
- Business logic lives in domain services
- Infrastructure adapts external systems to domain interfaces
- Bounded contexts don't bleed into each other
- Ubiquitous language: the code uses the same terms as the PO

The architect defines bounded contexts in design contributions.
Engineers implement within those boundaries.

### Onion Architecture
Systems the fleet builds follow onion layering:
- Core domain (inner): entities, value objects, domain services
- Application layer: use cases, orchestration
- Infrastructure (outer): databases, APIs, file systems
- Dependencies point INWARD — inner layers never reference outer

The architect specifies this in design input. Engineers follow the
layering. Fleet-ops verifies during review.

### Additional Code Principles
- Composition over inheritance
- Type hints on all public functions
- Error handling: fail loudly in dev, gracefully in production
- No secrets in code — use env vars or secret management
- Small, focused modules
- Conventional commits: `type(scope): description`
- Tests for new functionality (phase-appropriate coverage)

---

## Architecture Standards

### What Architects Must Produce
- Clear bounded context definitions
- Dependency direction rules (what can import what)
- Interface definitions for cross-boundary communication
- Data flow diagrams for complex features
- Technology choices with rationale (ADRs)

### What Engineers Must Follow
- Build within the architect's bounded contexts
- Respect dependency direction (no circular imports, no inner
  referencing outer)
- Use defined interfaces for cross-boundary calls
- Follow the architect's technology choices
- Don't over-engineer (POC doesn't need production architecture)
- Don't under-engineer (production needs proper layering)

### Phase-Appropriate Architecture

| Phase | Architecture Standard |
|-------|----------------------|
| poc | Working structure. Can be single-file if small. |
| mvp | Proper separation of concerns. Domain vs infrastructure. |
| staging | Full onion layering. Clean interfaces. Testable boundaries. |
| production | Production architecture. Scalable. Maintainable. Documented. |

---

## Artifact Standards — What "Done Right" Looks Like

### Current Standards (7 types)
Defined in `fleet/core/standards.py`:
- task, bug, analysis_document, investigation_document, plan,
  pull_request, completion_claim

Each has required fields, quality criteria, and completeness checking.

### New Artifact Types Needed

**qa_test_definition:**
Required fields:
- test_criteria (list with IDs, descriptions, types, priorities)
- target_task_reference
- delivery_phase (determines test depth)
- verification_method per criterion

Quality criteria:
- Each criterion is specific and checkable (not "test that it works")
- Criteria cover the verbatim requirement's scope
- Phase-appropriate depth (POC: happy path, production: complete)
- IDs for tracking (TC-001, TC-002, ...)

**security_requirement:**
Required fields:
- threat_assessment (what could go wrong)
- requirements_list (what MUST be done)
- restrictions_list (what MUST NOT be done)
- review_checklist (what to check during review)

Quality criteria:
- Specific to the task (not generic "be secure")
- References actual code/files when possible
- Phase-appropriate rigor

**design_input:**
Required fields:
- approach (which pattern/architecture to use)
- target_files (where things go)
- constraints (what to avoid)
- integration_points (how this connects)
- complexity_assessment (story points, risks)

Quality criteria:
- References specific files and line numbers
- Considers existing patterns in the codebase
- Addresses the verbatim requirement
- Multiple approaches considered (not just first idea)

**ux_spec:**
Required fields:
- component_structure (what components, hierarchy)
- interaction_patterns (click → response, states)
- layout_guidance (spacing, alignment, responsive)
- accessibility (ARIA, keyboard navigation)

Quality criteria:
- Specific enough to implement from
- References existing component patterns
- Addresses all user-facing states (loading, error, empty, success)

**compliance_report:**
Required fields:
- sprint/period covered
- methodology_compliance (% tasks following stages)
- contribution_coverage (% tasks with required contributions)
- gate_compliance (% gates properly approved)
- trail_completeness (% tasks with complete trails)
- quality_metrics (PR standards, commit standards)
- findings (specific issues)
- recommendations (process improvements)

**sprint_plan:**
Required fields:
- sprint_id, dates, goals
- task_list (with assignments, priorities, dependencies)
- velocity_target
- contribution_plan (who contributes what to which tasks)
- risk_assessment

---

## Phase-Aware Standards — PO-Defined

Every artifact standard has phase variants. The delivery phase
determines how strictly standards are enforced. But the PHASES
themselves are PO-defined (see document 03):

> The PO can invent unlimited phases, use any sequence, and define
> any standards. The system supports arbitrary phases — it does NOT
> prescribe what a phase is or what it contains.

### How Phase-Aware Standards Work

The standards library reads phase definitions from `config/phases.yaml`.
Each phase has a `standards` section that defines quality bars. The
`check_standard()` function takes a `phase` parameter and applies
the PO-defined standards for that phase.

```python
def check_standard(
    artifact_type: str,
    present_fields: dict[str, bool],
    phase: str = "",  # empty = use strictest
) -> ComplianceResult:
    """Check artifact against PO-defined phase standards."""
    phase_config = load_phase_standards(phase)  # from config
    standard = get_standard(artifact_type)
    # Apply phase-specific required/optional field overrides
    ...
```

The PO defines in config what each phase requires. The system
enforces whatever the PO decided. If the PO says a "poc" phase
requires 60% artifact completeness and a "production" phase requires
100%, the system enforces exactly that. If the PO later decides POC
needs 80%, they update the config and the system adjusts.

### Example (PO-Defined, Not System-Prescribed)

These are EXAMPLES of what a PO might define — not hard-coded rules:

```yaml
# config/phases.yaml — PO writes this
phases:
  standard:
    - name: poc
      standards:
        artifact_completeness: 60
        tests: "happy path"
        docs: "readme"
    - name: mvp
      standards:
        artifact_completeness: 80
        tests: "main flows + critical edges"
        docs: "setup, usage, API"
    - name: production
      standards:
        artifact_completeness: 100
        tests: "complete coverage"
        docs: "comprehensive"
        security: "certified"
```

The system reads this config. The PO changes this config. The system
adapts. No code change needed to adjust phase standards.

---

## Task Quality Standards

What a well-formed task looks like:

### Title
- Starts with a verb ("Add", "Fix", "Implement", "Design")
- Specific (not "improve things")
- Under 80 characters

### Description
- Explains WHAT to do, WHY, and WHAT success looks like
- References codebase locations when applicable
- Enough context that the agent doesn't need to guess

### Acceptance Criteria
- Specific, checkable conditions
- Not "it works" — checkable yes/no
- Good: "Returns 200 for valid input, 400 for missing required fields"
- Each criterion is independently verifiable

### Required Fields
ALL tasks must have:
- task_type, task_stage, task_readiness, story_points
- agent_name (assigned), requirement_verbatim, delivery_phase
- priority, project

### Comments
- Trail of work history
- Typed where applicable (contribution, decision, progress)
- Substantive (not just "done")

---

## PR Standards

### Title
Conventional commit format: `type(scope): description`

### Description
- WHY the change was made (not just WHAT changed)
- Task reference: OCMC task ID + Plane issue link
- Summary of approach
- Test results or test plan

### Commits
- Conventional commit format
- One logical change per commit
- Task ID in commit messages
- Clean history (no "fix typo" chains)

### Diff
- Only changes related to the task
- No scope creep ("while I'm here" changes)
- No unrelated formatting changes
- Clean, reviewable diff

---

## Documentation Standards

### User-Facing Documentation
- Written for the audience (not for the developer)
- Includes: purpose, setup, usage, examples
- Kept up to date when features change
- Lives on Plane pages (maintained by technical writer)

### API Documentation
- All public endpoints documented
- Parameters, types, examples, error codes
- Generated from code where possible
- Versioned when API changes

### Architecture Documentation
- Decision records (ADRs) for significant choices
- System overviews with component diagrams
- Data flow documentation
- Maintained by technical writer alongside architect

---

## Enforcement Mechanism

### Who Enforces What

| Standard | Primary Enforcer | Secondary |
|----------|-----------------|-----------|
| Code SRP/Domain/Onion | Architect (design input) | Fleet-ops (review) |
| Artifact completeness | Standards library (automated) | Fleet-ops (review) |
| Task quality | PM (triage) | Fleet-ops (review) |
| PR standards | Fleet-ops (review) | Doctor (detection) |
| Test coverage | QA (predefined tests) | Fleet-ops (review) |
| Documentation | Technical writer (continuous) | PM (sprint review) |
| Security | DevSecOps (requirements + review) | Doctor (detection) |
| Trail completeness | Accountability generator | Fleet-ops (review) |
| Phase standards | Brain (dispatch gates) | Fleet-ops (review) |

### Automated Checks
- `check_standard(artifact_type, fields, phase)` — standards library
- `check_artifact_completeness(type, data)` — artifact tracker
- `check_phase_prerequisites(task, phase)` — phase system
- `detect_protocol_violation(agent, stage, tools)` — doctor

### Human Checks
- Fleet-ops reviews against verbatim requirement
- PO approves at gates
- Accountability generator verifies trail

---

## Design Patterns — Know When to Use What

### PO Requirements (Verbatim)

> "we need to use design patterns, know when to do a builder, a cache,
> an index, a mediator, an API, a core, a module...."

> "we need to understand semantics and adapted pattern and research when
> needed and tools and / or lib / or packages when needed or even
> infrastructure when appropriated and validated."

> "like I said design patterns are really important and use of framework
> and sdk and tools and lib when appropriated."

### Pattern Selection by Agents

Agents — particularly the architect and software engineer — must know
WHEN to apply WHICH pattern. This is not generic "use patterns" — it's
knowing the right tool for the right job:

| Pattern | When to Use | Fleet Example |
|---------|-------------|---------------|
| **Builder** | Complex object construction with many optional parts | Context assembly, autocomplete chain construction |
| **Mediator** | Components need to communicate without tight coupling | Event bus, chain registry |
| **Observer** | One event triggers multiple independent reactions | Event handlers, notification routing |
| **Strategy** | Algorithm varies by context | Phase-aware standards, role-specific providers |
| **Factory** | Object creation depends on runtime type | Contribution creation, artifact creation |
| **Cache** | Repeated expensive lookups | Context assembly cache, task context per cycle |
| **Index** | Fast lookup by multiple keys | Agent → tasks, task → contributions, task → trail |
| **Adapter** | External system API doesn't match domain interface | MC client, Plane client, gateway client |
| **Facade** | Simplify complex subsystem | MCP tools as facade over core domain |
| **Chain of Responsibility** | Multiple handlers for same request | Dispatch gates, review validation chain |

### Research Before Building

> "research when needed and tools and / or lib / or packages when needed
> or even infrastructure when appropriated and validated"

Before implementing, agents must:
1. Check if a library/package solves the problem (don't reinvent)
2. Check if a framework provides the pattern (don't re-implement)
3. Check if an industry standard exists (don't invent protocols)
4. Validate the choice (security, maintenance, license, community)
5. Document the decision (architect creates ADR)

### Industry Standards Awareness

> "we should be mindful of standards like cloudevents and such"

The fleet should adopt industry standards where they exist:

| Domain | Standard to Consider |
|--------|---------------------|
| Events | CloudEvents specification for event format |
| API | OpenAPI/Swagger for API documentation |
| Auth | OAuth2/OIDC for authentication flows |
| Commits | Conventional Commits (already adopted) |
| Containers | OCI for container images |
| CI/CD | GitHub Actions workflow syntax |
| Monitoring | OpenTelemetry for observability |
| Config | YAML/TOML standards for configuration |

When the fleet builds event systems, it should consider CloudEvents
format rather than inventing a custom event structure. When building
APIs, use OpenAPI. When adding observability, use OpenTelemetry.

The architect evaluates which standards apply. The engineer implements
to those standards. DevOps validates infrastructure standards. DevSecOps
validates security standards.

---

## TDD and Testing Standards

### PO Requirements (Verbatim)

> "Use TDD when possible with high critical level tests and pessimistic
> ones with smart assertions and logics."

### Test-Driven Development

When possible, tests are written BEFORE implementation:
1. QA predefines test criteria (what must pass)
2. Engineer writes test cases that fail (red)
3. Engineer implements to make tests pass (green)
4. Engineer refactors while keeping tests green (refactor)

This aligns with the contribution model: QA's predefined tests ARE
the TDD test specification. The engineer implements to satisfy them.

### Pessimistic Testing

Tests assume things WILL go wrong:
- What happens when the API returns 500?
- What happens when the database is down?
- What happens when input is malformed?
- What happens when auth expires mid-request?
- What happens when disk is full?
- What happens when concurrent requests race?

Don't just test happy paths. Test failure paths with the same rigor.

### Smart Assertions

Tests verify BEHAVIOR, not implementation:
- Good: "returns 200 with valid token and body contains user.id"
- Bad: "mock was called 3 times" (tests implementation, not behavior)
- Good: "rejects input with SQL injection characters"
- Bad: "input passes through sanitize() function" (tests wiring)

Assertions should be:
- Specific (verify exact expected output, not just "no error")
- Independent (each test verifies one thing)
- Deterministic (same input → same result, no flaky tests)
- Phase-appropriate (POC: happy path, production: exhaustive)

### Critical Level Tests

Tests are prioritized by criticality:

| Level | What | Example |
|-------|------|---------|
| **Critical** | Security, data integrity, auth | "Unauthenticated request returns 401" |
| **High** | Core business logic, data flow | "Task dispatch follows all 10 gates" |
| **Medium** | Feature behavior, integrations | "Contribution propagates to target task" |
| **Low** | Display, formatting, convenience | "IRC message formats correctly" |

Critical and high tests MUST pass. Medium tests SHOULD pass.
Low tests are informational.

---

## Planning for Scale, Evolution, and Failure

### PO Requirements (Verbatim)

> "make sure we also think for scale, for evolution and plan for
> failure, always."

### Scale Thinking

Design decisions should consider growth:
- What happens when there are 100 tasks instead of 10?
- What happens when there are 50 agents instead of 10?
- What happens when there are 5 fleets instead of 2?
- What happens when the event bus processes 1000 events/minute?

Not over-engineer for scale (POC doesn't need Kubernetes), but
DESIGN for it (don't hardcode limits, use config, use proper
data structures).

### Evolution Thinking

> "its important to respect pattern and to know when to evolve and
> refactor, and when to change and when to remove and when to upgrade
> and when to update"

The fleet must know:
- **When to evolve:** feature works but needs better patterns → refactor
- **When to refactor:** code is correct but hard to maintain → clean up
- **When to change:** requirements changed → adapt the implementation
- **When to remove:** feature no longer needed → delete cleanly
- **When to upgrade:** dependency has new version → evaluate and update
- **When to update:** standard changed → align with new standard

The architect evaluates evolution decisions. The accountability
generator tracks technical debt. The PM plans evolution work in sprints.

### Failure Planning

Plan for failure at every level:
- **Agent failure:** session crashes, picks up from persistent artifacts
- **System failure:** MC/gateway/Plane down, graceful degradation
- **Chain failure:** partial execution, next cycle catches up
- **Data failure:** invalid input, validation at boundaries
- **Network failure:** retries with backoff, circuit breaker
- **Human failure:** PO unavailable, PM can handle within scope

Every system has a failure mode and a recovery path. These are
documented and tested.

---

## How Standards Evolve

Standards are NOT static. They evolve as the PO identifies quality
gaps:

1. **PO identifies gap:** "Tasks are being completed without proper
   test evidence."
2. **Standard updated:** completion_claim standard adds "test_results"
   as required field.
3. **Config updated:** `config/fleet.yaml` adds new standard requirement.
4. **Teaching updated:** New lesson template for "completion without
   test evidence."
5. **Detection updated:** Doctor pattern for missing test results.

This cycle is config-driven where possible, code change where necessary.
The goal is that standards can be tightened without deploying new code.

---

## Open Questions

- Should there be a "standards dashboard" showing compliance across
  the fleet?
- How do standards differ per project? (NNRT might have different
  standards than Fleet itself)
- Should agents receive the relevant standards in their context?
  (e.g., engineer sees "SRP, Domain, Onion" in CLAUDE.md)
- How do we handle standards conflicts? (Architect says one pattern,
  standards say another)