#!/usr/bin/env python3
"""Generate per-agent agent.yaml from template + config sources.

Reads:
  config/agent-identities.yaml   — fleet identity + agent display names
  config/agent-tooling.yaml      — mode, capabilities per role
  config/synergy-matrix.yaml     — contribution relationships
  config/agent-crons.yaml        — heartbeat intervals (staggered)

Produces:
  agents/{name}/agent.yaml       — 14-field config per standard

Standard: docs/milestones/active/standards/agent-yaml-standard.md

Usage:
  python scripts/provision-agent-yaml.py              # all agents
  python scripts/provision-agent-yaml.py architect     # single agent
"""

import sys
from pathlib import Path

import yaml

FLEET_DIR = Path(__file__).resolve().parent.parent
CONFIG = FLEET_DIR / "config"
AGENTS_DIR = FLEET_DIR / "agents"


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


# Per-role configuration that doesn't come from config files
ROLE_CONFIG = {
    "project-manager": {
        "mode": "acceptEdits",
        "model": "opus",
        "mission": "Coordinate the fleet — triage tasks, assign agents, orchestrate contributions, route PO gates",
        "capabilities": ["task-management", "sprint-planning", "epic-breakdown", "agent-assignment", "po-routing", "contribution-orchestration", "plane-sync"],
    },
    "fleet-ops": {
        "mode": "acceptEdits",
        "model": "sonnet",
        "mission": "Quality guardian — review work against verbatim requirements, enforce methodology, monitor board health",
        "capabilities": ["code-review", "approval-processing", "methodology-compliance", "board-health", "budget-monitoring", "quality-enforcement"],
    },
    "architect": {
        "mode": "plan",
        "model": "opus",
        "mission": "Design authority — provide design input, assess complexity, maintain architecture health",
        "capabilities": ["system-design", "design-patterns", "complexity-assessment", "adr-creation", "codebase-analysis", "option-exploration"],
    },
    "devsecops-expert": {
        "mode": "default",
        "model": "opus",
        "mission": "Security at every level — provide requirements before, review during, validate after",
        "capabilities": ["vulnerability-assessment", "dependency-audit", "secret-scanning", "security-review", "threat-modeling", "incident-response", "compliance-verification"],
    },
    "software-engineer": {
        "mode": "acceptEdits",
        "model": "sonnet",
        "mission": "Implement confirmed plans by consuming colleague contributions and producing tested code",
        "capabilities": ["feature-implementation", "bug-fixing", "refactoring", "test-writing", "conventional-commits", "contribution-consumption"],
    },
    "devops": {
        "mode": "acceptEdits",
        "model": "sonnet",
        "mission": "Own infrastructure — everything scriptable, reproducible, version-controlled",
        "capabilities": ["docker-management", "ci-cd-pipeline", "deployment-strategy", "infrastructure-monitoring", "iac-scripting", "service-health"],
    },
    "qa-engineer": {
        "mode": "acceptEdits",
        "model": "sonnet",
        "mission": "Predefine tests before implementation, validate against them during review",
        "capabilities": ["test-predefinition", "test-validation", "coverage-analysis", "acceptance-criteria-review", "regression-testing", "boundary-analysis"],
    },
    "technical-writer": {
        "mode": "acceptEdits",
        "model": "sonnet",
        "mission": "Documentation as a living system — maintain alongside code, detect staleness, formalize decisions",
        "capabilities": ["documentation", "adr-formalization", "api-docs", "changelog-generation", "staleness-detection", "terminology-consistency"],
    },
    "ux-designer": {
        "mode": "acceptEdits",
        "model": "sonnet",
        "mission": "UX at every level — provide patterns and specs before engineers build",
        "capabilities": ["ux-specification", "accessibility-audit", "component-patterns", "interaction-design", "state-modeling"],
    },
    "accountability-generator": {
        "mode": "acceptEdits",
        "model": "sonnet",
        "mission": "Verify process was followed — trail completeness, methodology compliance, pattern detection",
        "capabilities": ["trail-verification", "compliance-reporting", "pattern-detection", "audit-reconstruction", "governance"],
    },
}

# Heartbeat intervals (staggered, from clean-gateway-config.sh)
HEARTBEAT_INTERVALS = {
    "fleet-ops": "10m",
    "project-manager": "12m",
    "architect": "14m",
    "devsecops-expert": "16m",
    "software-engineer": "18m",
    "qa-engineer": "20m",
    "devops": "22m",
    "technical-writer": "24m",
    "ux-designer": "26m",
    "accountability-generator": "28m",
}


def get_contributes_to(agent_name: str, synergy: dict) -> list[str]:
    """Get roles this agent contributes TO from synergy matrix."""
    contributions = synergy.get("contributions", {})
    targets = []
    for target_role, specs in contributions.items():
        for spec in (specs or []):
            if spec.get("role") == agent_name:
                if target_role not in targets:
                    targets.append(target_role)
    return targets


def generate_agent_yaml(agent_name: str) -> str:
    """Generate agent.yaml content for one agent."""
    identities = load_yaml(CONFIG / "agent-identities.yaml")
    synergy = load_yaml(CONFIG / "synergy-matrix.yaml")

    fleet_info = identities.get("fleet", {})
    fleet_id = fleet_info.get("id", "alpha")
    fleet_name = fleet_info.get("name", "Fleet Alpha")
    fleet_number = fleet_info.get("number", 1)

    agent_info = identities.get("agents", {}).get(agent_name, {})
    display_name = agent_info.get("display_name", agent_name.replace("-", " ").title())
    username = agent_info.get("username", agent_name)

    role_cfg = ROLE_CONFIG.get(agent_name, {})
    contributes_to = get_contributes_to(agent_name, synergy)
    interval = HEARTBEAT_INTERVALS.get(agent_name, "30m")

    data = {
        "name": agent_name,
        "display_name": display_name,
        "fleet_id": fleet_id,
        "fleet_number": fleet_number,
        "username": username,
        "type": "agent",
        "mode": role_cfg.get("mode", "default"),
        "backend": "claude",
        "model": role_cfg.get("model", "sonnet"),
        "mission": role_cfg.get("mission", ""),
        "capabilities": role_cfg.get("capabilities", []),
        "roles": {
            "primary": agent_name,
            "contributes_to": contributes_to,
        },
        "heartbeat_config": {
            "every": interval,
        },
        "constraints": {
            "max_turns": 20,
            "approval_required": False,
        },
    }

    return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)


def main():
    agents = list(ROLE_CONFIG.keys())

    if len(sys.argv) > 1:
        target = sys.argv[1]
        if target not in agents:
            print(f"Unknown agent: {target}")
            print(f"Available: {', '.join(agents)}")
            sys.exit(1)
        agents = [target]

    print("=" * 55)
    print("  Provision agent.yaml — 14 fields per standard")
    print("=" * 55)
    print()

    for agent_name in agents:
        agent_dir = AGENTS_DIR / agent_name
        agent_dir.mkdir(exist_ok=True)

        content = generate_agent_yaml(agent_name)
        yaml_path = agent_dir / "agent.yaml"

        if yaml_path.exists():
            existing = yaml_path.read_text()
            if existing == content:
                print(f"  [skip] {agent_name}: unchanged")
                continue
            print(f"  [updated] {agent_name}")
        else:
            print(f"  [created] {agent_name}")

        yaml_path.write_text(content)

    print()
    print("Done.")


if __name__ == "__main__":
    main()
