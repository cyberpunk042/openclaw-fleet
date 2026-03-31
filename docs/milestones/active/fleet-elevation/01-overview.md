# Fleet Elevation — Overview

**Date:** 2026-03-30
**Status:** Design — comprehensive fleet operational redesign
**Scope:** Every system, every agent, every pattern — elevated to
gold standard

---

## PO Requirements (Verbatim)

> "we need to revise everything about all agents, not just one of their
> files, the whole things and the templating and the injection and the
> structure and pattern explanation before autocomplete and so on..."

> "we need to do a gold job, we need to elevate the quality and the
> standard."

> "the technical-writer like every agent will need to do its job when
> the Plane is connected and I am in Full Autonomous mode. it will need
> to keep the pages up to date for example and whatever else rely on him
> like complementary work to the architect and UX designer and software
> engineer."

> "Everyones work is very important. without UX thinking a software
> engineer make too many mistake and same things when there was no
> architecture steps done before executing"

> "Everything, every system we re-explore, any missing design pattern we
> consider and any anti-pattern or underuse or misuse or lacking system
> is in the scope... the fleet is ready when I say so."

> "Do not minimize. just remember everything I said and how we are going
> to do all this."

> "there is a bit of exploration and whatnot but you get the gist."

> "No small feat. no hacks, no quickfix. this is a long and arduous
> task, we are not in a rush. take your time to do this well."

> "we should be mindful of standards like cloudevents and such and make
> sure we also think for scale, for evolution and plan for failure,
> always. Use TDD when possible with high critical level tests and
> pessimistic ones with smart assertions and logics."

> "we need to use design patterns, know when to do a builder, a cache,
> an index, a mediator, an API, a core, a module"

> "UX is not just about the UI, UX is at every level, even the core
> and module or CLI and AST"

> "every role are top tier expert of their profession"

> "the engineer has to be to my image... a senior devops software
> engineer with network background and PM, Scrum Master replacement
> capabilities... evolved to architect and fullstack and security...
> a very humble no matter how knowledgable and always in respect of
> other people roles"

> "The words and titles I used are not for nothing. there is a huge
> difference between any general agent..... those are top tier wise
> agent. they dont need overconfidence, no self-confirmed bias, no
> cheating, no getting lost or derailing"

> "its important to respect pattern and to know when to evolve and
> refactor, and when to change and when to remove and when to upgrade
> and when to update"

> "we will need to write diagrams too"

---

## What This Is

The fleet has infrastructure — 8 systems built, 820+ tests, 70+ commits.
Now we elevate EVERYTHING to make the fleet actually operate as a team
of specialists producing mature, high-quality work.

This is not incremental. It's a comprehensive redesign of how agents
work, communicate, and deliver. Every system re-explored. Every pattern
reconsidered. Every agent's full contribution mapped.

---

## Top-Tier Agents — ALL of Them

> "I said a lot of things but things I said obviously where not just
> about one agent. I used the they because they are top tier so we need
> to think like the senior engineer but for all of them, like a top tier
> PM with a top tier SCRUM & Admin degree and so on for all our agent.
> they are highly qualified and well defined."

Every agent in this fleet is a top-tier expert of their profession.
Not generic AI assistants — top-tier professionals with deep domain
knowledge, discipline, humility, and collaborative instincts:

- **Project Manager:** top-tier Scrum Master with deep AGILE/SCRUM
  mastery, project administration expertise, stakeholder management,
  sprint velocity optimization, risk assessment, and the ability to
  drive a board like a seasoned PM with 15 years of experience.
- **Fleet-Ops:** top-tier operations lead with quality engineering
  discipline, review methodology, compliance verification skills,
  budget awareness, and the judgment to approve or reject based on
  deep reading, not rubber-stamping.
- **Architect:** top-tier software architect with deep design pattern
  mastery (builder, mediator, observer, strategy, repository, facade),
  SRP/Domain/Onion expertise, research discipline, industry awareness,
  and the wisdom to know when a pattern fits and when it doesn't.
- **DevSecOps:** top-tier security engineer with threat modeling
  expertise, vulnerability assessment skills, compliance knowledge,
  penetration testing mindset, and the discipline to review EVERY
  change for security implications.
- **Software Engineer:** modeled after the PO — senior DevOps software
  engineer with network background, fullstack capability, security
  knowledge, AGILE/SCRUM love, and evolved architect sensibilities.
  Humble, no matter how knowledgeable.
- **DevOps:** top-tier infrastructure engineer with IaC discipline,
  CI/CD mastery, container orchestration, monitoring expertise,
  and the principle that EVERYTHING must be scriptable and reproducible.
- **QA Engineer:** top-tier quality assurance professional with TDD
  discipline, test strategy expertise, acceptance criteria rigor,
  boundary analysis, pessimistic testing instinct, and the ability
  to predefine tests that catch real defects.
- **Technical Writer:** top-tier documentation specialist with audience
  awareness, information architecture skills, API documentation
  expertise, and the discipline to maintain living documentation
  alongside code changes.
- **UX Designer:** top-tier user experience professional with
  interaction design expertise, accessibility knowledge (WCAG),
  component pattern mastery, and the understanding that UX is at
  EVERY level — core, module, CLI, API, not just web UI.
- **Accountability Generator:** top-tier compliance and governance
  professional with audit methodology, process verification skills,
  pattern recognition for systemic issues, and reporting discipline.

These agents are humble, collaborative, process-respecting, and
focused. No overconfidence. No self-confirmed bias. No cheating.
No getting lost. All the processes, all the roads and options.

---

## Tool Call Trees — Group Calls

> "chain is calling multiple tools, not just small process and
> transformation but also add a comment to the mc board for example
> and auto adding it to the task on Plane and etc.... a tree map to
> generate multiple tool call from a single one."

One agent-facing tool call triggers a TREE of actual internal
operations. The agent calls ONE tool, the infrastructure executes
MANY. This is the group call concept — see document 04 for the
full tree architecture.

---

## Document Series (22+ documents)

### Foundations

1. **01-overview.md** — this document
2. **02-agent-architecture.md** — complete review of agent file structure,
   templating, injection patterns, autocomplete setup
3. **03-delivery-phases.md** — ideal→conceptual→POC→MVP→staging→production,
   distinct from methodology stages
4. **04-the-brain.md** — orchestrator redesign, deterministic vs AI work,
   logic layer, avoiding needless AI work

### Per-Agent Role Deep Dives (10 agents)

5. **05-project-manager.md** — full role with synergy, Plane driving, all modes
6. **06-fleet-ops.md** — quality, governance, methodology enforcement
7. **07-architect.md** — design authority, cross-agent guidance, proactive review
8. **08-devsecops.md** — security at every stage, not just review
9. **09-software-engineer.md** — implementation with architecture and UX input
10. **10-devops.md** — infrastructure, CI/CD, deployment maturity
11. **11-qa-engineer.md** — test predefinition, quality gates at every stage
12. **12-technical-writer.md** — documentation living alongside code, Plane pages
13. **13-ux-designer.md** — UX thinking before implementation, component patterns
14. **14-accountability-generator.md** — compliance, governance, audit trails

### Cross-Cutting Systems

15. **15-cross-agent-synergy.md** — how agents work together, who contributes
    what at which stage, parallel not serial
16. **16-multi-fleet-identity.md** — agent naming, fleet numbering, shared
    Plane, two fleets on one platform
17. **17-standards-framework.md** — SRP, domain, onion applied to agents,
    quality bars, artifact standards
18. **18-po-governance.md** — PO authority, approval gates, readiness
    acceptance/rejection/regression, PM routing to PO
19. **19-flow-validation.md** — diagrams, simulations, logic verification
    of how a task flows through the fleet
20. **20-ai-behavior.md** — preventing corruption, deformation, compression,
    strongly constraining AI interpretation

### Lifecycle and Completion

21. **21-task-lifecycle-redesign.md** — complete task lifecycle with stages,
    phases, gates, states, transfers, child tasks, trails, cowork
22. **22-milestones.md** — full milestone breakdown for implementation

### Operational Efficiency

23. **23-agent-lifecycle-and-strategic-calls.md** — sleep/wake lifecycle,
    brain-evaluated heartbeats, strategic Claude call decisions (model,
    effort, session strategy), cost-aware operation, LocalAI offload path
24. **24-tool-call-tree-catalog.md** — every MCP tool's complete call tree,
    what internal operations fire from each agent-facing tool call,
    parallel/sequential execution, failure isolation, role × tool matrix
25. **25-diagrams.md** — 9 ASCII diagrams: system architecture, task state
    machine, stage progression, contribution flow, agent lifecycle,
    tool call tree, dispatch gates, immune system flow, PO governance
26. **26-unified-config-reference.md** — complete config/fleet.yaml after
    elevation, every section, every field, what exists vs what's new
27. **27-evolution-and-change-management.md** — how the fleet handles
    change: requirement evolution mid-task, phase changes, test evolution,
    standard evolution, code refactoring, config versioning, agent file
    updates, surprises, budget crises
28. **28-codebase-inventory.md** — every existing module (55 core, 7 infra,
    2 MCP, 3 CLI, 4 gateway), what each does, how elevation extends it,
    patterns already established, implementation rules
29. **29-lessons-learned.md** — what this conversation taught us: code
    awareness, don't minimize, top-tier agents, tool call trees, PO-defined
    phases, build on what exists, strategic calls, UX everywhere, design
    patterns, the conversation IS the design
30. **30-strategy-synthesis.md** — lessons turned into plan changes:
    backward/forward planning methodology, gap analysis for each lesson,
    revised implementation phase structure (audit → backward → forward →
    TDD → implement → validate), end state definition with backward
    decomposition, forward ripple tracing, embedding planning methodology
    into agent stage instructions and CLAUDE.md
31. **31-transition-strategy.md** — how to elevate a RUNNING fleet:
    staged rollout with test-then-commit, per-phase transition protocol,
    agent file merge strategy (additive, not replacing), risk assessment,
    rollback plan, monitoring signals, revised implementation order with
    quick wins first, AICP/LocalAI connection