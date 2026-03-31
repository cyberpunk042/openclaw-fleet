# Multi-Fleet Identity System

**Date:** 2026-03-30
**Status:** Design — naming, numbering, shared Plane
**Part of:** Fleet Elevation (document 16 of 22)

---

## PO Requirements (Verbatim)

> "this is about logic and applying the roles, making the agents behave
> as they should and respecting everything about themselves, and having
> their own Identity name and username and whatnot"

> "another fleet would have another name and username, you need to think
> about this, like we do a diff fleet number if that is still in place,
> since it will be possible to have two fleet connected to the same Plane"

---

## What This Document Covers

The identity system for agents and fleets. Each agent has a unique
identity (name, username, display name). Each fleet has an identity
(fleet_id, fleet_number, fleet_name). Two fleets can connect to the
same Plane instance without collision.

---

## Fleet Identity

```yaml
# config/fleet.yaml

fleet:
  id: alpha               # Short identifier, used in prefixes
  number: 1               # Numeric fleet identifier
  name: "Fleet Alpha"     # Display name

  # Infrastructure
  mc_url: "http://localhost:8000"
  gateway_url: "http://localhost:3000"
  plane_url: "http://plane.local"
  plane_workspace: "fleet"

  # Shared resources
  shared_plane: true       # This Plane is shared with other fleets
  shared_github: true      # GitHub repos are shared
```

Fleet Bravo would have:
```yaml
fleet:
  id: bravo
  number: 2
  name: "Fleet Bravo"
  mc_url: "http://bravo-mc:8000"  # Different MC instance
  gateway_url: "http://bravo-gw:3000"
  plane_url: "http://plane.local"  # SAME Plane
  plane_workspace: "fleet"          # SAME workspace
  shared_plane: true
```

---

## Agent Identity

Each agent's identity is derived from fleet + role:

```
Fleet Alpha (fleet_id: alpha, fleet_number: 1)
├── alpha-pm             username: alpha-pm          display: "PM Alpha"
├── alpha-lead           username: alpha-lead         display: "Fleet Ops Alpha"
├── alpha-architect      username: alpha-architect    display: "Architect Alpha"
├── alpha-engineer       username: alpha-engineer     display: "Engineer Alpha"
├── alpha-devops         username: alpha-devops       display: "DevOps Alpha"
├── alpha-qa             username: alpha-qa           display: "QA Alpha"
├── alpha-security       username: alpha-security     display: "Cyberpunk-Zero Alpha"
├── alpha-writer         username: alpha-writer       display: "Tech Writer Alpha"
├── alpha-ux             username: alpha-ux           display: "UX Designer Alpha"
└── alpha-compliance     username: alpha-compliance   display: "Compliance Alpha"
```

The agent.yaml for each agent includes:
```yaml
name: "alpha-architect"
display_name: "Architect Alpha"
fleet_id: "alpha"
fleet_number: 1
username: "alpha-architect"
role: "architect"
```

---

## Shared Plane — No Collisions

When two fleets share a Plane:

### Task Attribution
OCMC tasks are fleet-specific (each fleet has its own MC board).
Plane issues are shared. When syncing:
- Comments carry fleet attribution: "[alpha-architect] Design approach..."
- Labels include fleet: `fleet:alpha`, `fleet:bravo`
- Plane issue can have tasks from BOTH fleets working on it

### Comment Attribution
```
[alpha-architect] Recommended event bus pattern for this module.
[bravo-engineer] Implementing with observer pattern per bravo-architect.
```

Each comment prefixed with [fleet_id-role] so it's clear who said what.

### Label Namespacing
Fleet-specific labels are prefixed:
- `alpha:stage:reasoning`, `bravo:stage:work`
- `alpha:readiness:80`, `bravo:readiness:50`
- Shared labels are unprefixed: `phase:mvp`, `priority:high`

### Cross-Fleet Collaboration
Two fleets can work on the same Plane issue:
- Alpha's architect designs, Bravo's engineer implements
- Contributions cross fleet boundaries via Plane
- Each fleet's brain manages its own agents
- Plane is the shared coordination layer

---

## IDENTITY.md Template

```markdown
# IDENTITY.md — {Display Name}

## Who You Are
- Name: {fleet_id}-{role}
- Display: {display_name}
- Fleet: {fleet_name} (Fleet #{fleet_number})
- Username: {username}
- Role: {role}

## Your Specialty
{role_specific_description}

## Your Fleet
You are part of {fleet_name}. There may be other fleets connected
to the same Plane. Your comments and contributions are attributed
to [{fleet_id}-{role}].

## Your Place in the Fleet
{how_this_agent_relates_to_others_in_this_fleet}
```

---

## Infrastructure Per Fleet

```
Fleet Alpha (Machine 1)
├── MC Instance (alpha board)
├── Gateway Instance (alpha agents)
├── Orchestrator (alpha brain)
├── LocalAI Cluster
└── 10 Agents (alpha-prefixed)

Fleet Bravo (Machine 2)
├── MC Instance (bravo board)
├── Gateway Instance (bravo agents)
├── Orchestrator (bravo brain)
├── LocalAI Cluster
└── 10 Agents (bravo-prefixed)

Shared:
├── Plane Instance (one workspace, shared issues)
├── GitHub (shared repos, fleet-attributed commits)
├── ntfy (shared notifications, fleet-tagged)
└── IRC/The Lounge (shared channels, fleet-prefixed nicks)
```

---

## Data Model Changes

### agent.yaml additions
- `fleet_id: str` — which fleet
- `fleet_number: int` — fleet number
- `username: str` — unique username (fleet_id-role)

### config/fleet.yaml additions
- `fleet.id`, `fleet.number`, `fleet.name`
- `fleet.shared_plane: bool`
- Agent definitions with fleet-specific naming

### Plane sync changes
- Comment attribution: prefix with [fleet_id-role]
- Label namespacing: fleet-specific labels prefixed
- Multi-fleet issue support: track which fleet's tasks link to issue

---

## Git Attribution Across Fleets

When agents commit code on shared repositories:

### Branch Naming
`{fleet_id}/{agent_role}/{task_short_id}`
Example: `alpha/engineer/abc12345`

This avoids branch name collisions when two fleets work on the same
repo. Alpha's engineer branch ≠ bravo's engineer branch.

### Commit Attribution
```
feat(auth): add JWT middleware [abc12345]

Agent: alpha-engineer
Fleet: Fleet Alpha (#1)
Task: abc12345
Co-Authored-By: alpha-engineer <alpha-engineer@fleet-alpha.local>
```

Fleet-specific email addresses ensure git log shows which fleet
produced each commit. No collision between alpha-engineer and
bravo-engineer.

### PR Attribution
PR titles include fleet prefix when fleets share repos:
`[alpha] feat(auth): add JWT middleware`

PR description includes fleet context:
```
Fleet: Alpha (#1)
Agent: alpha-engineer
Task: abc12345 (OCMC: alpha board)
Plane: issue XYZ (shared workspace)
```

---

## IRC Identity Across Fleets

### Nick Format
`{fleet_id}-{role}` — e.g., `alpha-pm`, `bravo-architect`

### Channel Behavior
Shared IRC channels show fleet-prefixed nicks:
```
[#fleet]
<alpha-pm> Sprint S4: 6/15 done, 2 blocked.
<bravo-pm> Sprint S3: 8/10 done, finishing current.
<alpha-engineer> Completed CI pipeline task.
<bravo-qa> Predefined tests for auth module.
```

Fleet-specific channels (optional):
- `#alpha` — Fleet Alpha internal
- `#bravo` — Fleet Bravo internal
- `#fleet` — shared, both fleets visible

### ntfy Attribution
Push notifications to PO include fleet identifier:
```
[Alpha] Gate: readiness 90% on "Add CI/CD" — PO approval needed
[Bravo] Security: critical finding in auth module
```

---

## LocalAI Peering Between Fleets

### Cluster Architecture
```
Fleet Alpha (Machine 1)           Fleet Bravo (Machine 2)
├── LocalAI Cluster 1             ├── LocalAI Cluster 2
│   ├── GPU: 8GB VRAM             │   ├── GPU: 8GB VRAM
│   ├── Active model: hermes-3b   │   ├── Active model: hermes-7b
│   └── Port: 8090                │   └── Port: 8090
│                                 │
└── Peering ──────────────────────┘── Peering
    ├── Health check: each cluster monitors the other
    ├── Failover: if one cluster is down, route to the other
    ├── Load balance: distribute simple requests across clusters
    └── Model swap: request model swap on peer if needed
```

### Peering Protocol
1. Each cluster exposes a health endpoint
2. Each orchestrator monitors peer cluster health
3. If local cluster is overloaded or model is loading:
   route to peer cluster (if available)
4. If local cluster is down: route ALL requests to peer
5. Peering is optional — single fleet works without it

### Peering Config
```yaml
# config/fleet.yaml
cluster:
  local:
    url: "http://localhost:8090"
    gpu_vram: 8192
  peers:
    - fleet_id: bravo
      url: "http://bravo-localai:8090"
      priority: 1  # failover priority
```

---

## Cross-Fleet Coordination on Shared Plane

### Issue Ownership
- Plane issues are NOT owned by a fleet — they're shared
- Each fleet creates OCMC tasks linked to Plane issues
- Multiple fleets can have tasks linked to the same issue
- Each fleet's brain manages its own agents' work independently

### Coordination Through Plane
- Alpha-architect posts design on Plane issue → Bravo-engineer
  sees it when syncing
- Contributions travel through Plane, not through fleet-to-fleet
  direct communication
- Plane is the neutral ground between fleets

### Conflict Resolution
- Two agents from different fleets modifying the same file?
  Git handles it (branches, PRs, merge conflicts)
- Two fleets setting different labels on same Plane issue?
  Most recent wins, with both PMs notified
- Two fleets in different work modes? Each fleet respects its
  own mode independently

---

## Open Questions

- How do two fleets coordinate on the same Plane issue? (Each fleet's
  brain manages its own agents — coordination is through Plane, not
  direct fleet-to-fleet communication.)
- Should there be a "fleet coordinator" role that spans fleets?
  (For now: PO coordinates between fleets manually via Plane.)
- Should fleet identity be in environment variables or config files?
  (Config files tracked in git — fleet-specific config per machine
  via environment variables that reference config.)