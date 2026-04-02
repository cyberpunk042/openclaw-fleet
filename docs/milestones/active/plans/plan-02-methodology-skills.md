# Plan 02 — Methodology + Skills Layer

**Phase:** 2 (depends on Plan 01 safety layer)
**Source:** Synthesis D2, D10, D11, D12, D13, D17 | Analysis 03 (skills), 04 (commands)
**Milestone IDs:** EA-003, EA-004, EA-018, EA-019, EA-020, SK-001 to SK-010

---

## What This Plan Delivers

Agents get: methodology enforcement (Superpowers TDD + our 5-stage protocol),
role-specific skills deployed to workspaces, fleet skills assigned to roles,
ecosystem expert skills per role. The HOW of working correctly.

**PO decisions required before building:**
- D2: Superpowers adoption strategy (whole plugin vs cherry-pick)
- D10: Which alirezarezvani POWERFUL skills per role
- D11: Trail of Bits security skills for devsecops
- D12: HashiCorp Terraform skills for devops
- D13: Template skills (differentiate vs replace)
- D17: Skill deployment architecture (symlink vs copy vs plugin vs hybrid)

---

## 1. Evaluate and adapt Superpowers (D2)

**What:** 132K-star methodology plugin. 14 skills enforcing TDD, brainstorming,
systematic debugging, verification, subagent-driven development.

**Evaluation steps (in Claude Code, no fleet needed):**
1. Install: `/plugin marketplace add obra/superpowers` then `/plugin install superpowers`
2. Start a coding task — observe what skills trigger automatically
3. Write code WITHOUT a test — does TDD enforcement kick in?
4. Try to skip planning — does brainstorming trigger?
5. Document: which behaviors align with our 5-stage protocol, which conflict

**Adaptation needed:**
- Superpowers assumes autonomous multi-hour execution
- Our fleet has "one step, wait for approval" guardrails
- Need to determine: can autonomy be throttled via config?
- Or do we cherry-pick the 6 methodology skills into our own skills system?

**Cherry-pick candidates (if not whole plugin):**
1. brainstorming — Socratic refinement before code
2. test-driven-development — TRUE TDD enforcement
3. systematic-debugging — 4-phase root cause
4. verification-before-completion — ensure actually fixed
5. writing-plans — 2-5 minute tasks with exact files
6. requesting-code-review — pre-review checklist

**IaC:** Add to agent-tooling.yaml defaults or per-role plugins section

---

## 2. Deploy fleet skills to proper roles (SK-001 to SK-004)

**What:** 7 fleet skills exist in openclaw-fleet/.claude/skills/ but aren't
assigned in agent-tooling.yaml and aren't deployed to agent workspaces.

**Steps:**
1. Verify agent-tooling.yaml has fleet skills assigned (done this session):
   - fleet-communicate → ALL (defaults)
   - fleet-review → fleet-ops, QA
   - fleet-plan → PM
   - fleet-test → QA
   - fleet-security-audit → devsecops
   - fleet-sprint → PM, fleet-ops
   - fleet-plane → PM, fleet-ops
2. Build skill deployment in `scripts/install-plugins.sh` or new `scripts/deploy-skills.sh`:
   - For each agent: read assigned skills from agent-tooling.yaml
   - Symlink or copy skill files to agent workspace .claude/skills/
   - AICP skills from devops-expert-local-ai/.claude/skills/
   - Fleet skills from openclaw-fleet/.claude/skills/
3. Verify: each agent's /skills command shows their assigned skills

**IaC:** New script or extend install-plugins.sh. Config-driven from agent-tooling.yaml.

**Test:** Run /skills in Claude Code from an agent workspace — correct skills listed?

---

## 3. Deploy ecosystem expert skills per role (D10, D11, D12)

**What:** Install role-specific expert skills from ecosystem collections.
Requires PO decisions on which to adopt.

**Per role (pending D10 decisions):**

| Role | Candidate Skills | Source |
|------|-----------------|--------|
| architect | agent-designer, rag-architect | alirezarezvani POWERFUL |
| devsecops | semgrep-rule-creator, property-based-testing, variant-analysis (21 total) | VoltAgent/Trail of Bits |
| fleet-ops | pr-review-expert | alirezarezvani POWERFUL |
| devops | 11 Terraform skills | VoltAgent/HashiCorp |
| QA | playwright-pro (9 sub-skills) | alirezarezvani |
| accountability | tech-debt-tracker | alirezarezvani POWERFUL |

**Steps (after PO decisions):**
1. For each adopted skill collection:
   - Clone or download the skill files
   - Review content for quality and security (skill-security-auditor)
   - Place in a shared skills directory or per-agent
2. Update agent-tooling.yaml with new skill assignments
3. Run deploy-skills.sh to push to workspaces
4. Verify with /skills per agent

**IaC:** Skill source config (git repos or local paths) in agent-tooling.yaml

---

## 4. Differentiate template skills (D13)

**What:** 48 AICP skills share identical 4-step boilerplate. Need real content.

**Approach (pending D13 decision):**
- If Superpowers adopted: its methodology covers the HOW that templates were supposed to provide. Focus on differentiating the top 15 that have unique WHAT.
- If no Superpowers: differentiate all 48 (48h effort)

**Top 15 to differentiate first:**
1. feature-implement — core engineer workflow
2. feature-test — core QA workflow
3. feature-review — core review workflow
4. feature-plan — core planning workflow
5. feature-document — core writer workflow
6. quality-coverage — QA coverage measurement
7. quality-audit — cross-role audit
8. quality-lint — code quality gate
9. quality-debt — tech debt tracking
10. refactor-extract — common refactor pattern
11. refactor-split — module splitting
12. refactor-architecture — architectural refactor
13. infra-security — security infrastructure
14. infra-monitoring — observability setup
15. config-secrets — secret management

**Steps per skill:**
1. Read current template content (identical boilerplate)
2. Write role-specific differentiated content:
   - What this skill ACTUALLY does (specific to its name)
   - Key steps (not generic 4-step)
   - What to check/verify
   - Common mistakes to avoid
3. Test: invoke the skill — does it guide meaningfully?

**IaC:** Skills are files in .claude/skills/ — committed to git

---

## 5. Per-stage skill recommendations in agent context (SK-008)

**What:** Agents should know which skills to use at each methodology stage.
Currently no stage-specific guidance in any agent file.

**Source:** methodology-manual.md (already maps skills per stage)

**Steps:**
1. Read methodology-manual.md per-stage skill recommendations
2. Add to agent CLAUDE.md template (Stage Protocol section):
   ```
   Stage-specific skills:
   - INVESTIGATION: /fleet-security-audit, /infra-search
   - REASONING: /architecture-propose, /writing-plans
   - WORK: /feature-implement, /fleet-commit
   ```
3. Add to HEARTBEAT.md template (proactive skill usage):
   ```
   When idle, consider: /quality-audit, /quality-debt
   ```

**IaC:** Part of agent file provisioning (templates reference methodology-manual.md)

**Test:** Agent in reasoning stage — does it see recommended skills?

---

## 6. Skill deployment IaC script (SK-007, D17)

**What:** Build the script that deploys all skills to all agent workspaces.

**Approach (pending D17 decision):**
- Hybrid recommended: our skills via symlink, ecosystem via plugin install

**Script: `scripts/deploy-skills.sh`**
```bash
# For each agent:
#   1. Read assigned skills from agent-tooling.yaml
#   2. Create .claude/skills/ directory in agent workspace
#   3. For each AICP skill: symlink from devops-expert-local-ai/.claude/skills/
#   4. For each fleet skill: symlink from openclaw-fleet/.claude/skills/
#   5. For each ecosystem skill: copy from downloaded collection
#   6. Verify: all assigned skills accessible
```

**IaC principles:**
- Idempotent (run twice = same result)
- Config-driven (reads agent-tooling.yaml)
- Reports what changed
- Validates after deployment

**Makefile:** `make deploy-skills`

---

## Validation Checklist

- [ ] Superpowers evaluated (methodology aligns or conflicts documented)
- [ ] Fleet skills deployed to all agent workspaces
- [ ] Each agent's /skills shows correct assignments
- [ ] Ecosystem expert skills installed per role (after PO decisions)
- [ ] Top 15 template skills differentiated with real content
- [ ] Per-stage skill recommendations in agent CLAUDE.md
- [ ] deploy-skills.sh script working and idempotent
- [ ] agent-tooling.yaml reflects all skill assignments
- [ ] validate-agents.sh checks skill presence per agent

---

## What This Enables

With this plan complete:
- Agents have METHODOLOGY enforcement (TDD, brainstorming, verification)
- Agents have ROLE-SPECIFIC expert skills (security, architecture, review)
- Agents know WHICH SKILLS to use at each stage
- Skills are deployed via IaC (reproducible, config-driven)
- Template skills have real differentiated content
