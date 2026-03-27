# Fleet Autonomy — Making the Fleet Work on Its Own

## The Problem

The fleet currently operates only when manually driven:
- I create sessions and send messages via Python scripts
- I copy output between agents
- I commit code that agents produce
- I decide what to work on next

This is not a fleet. It's me using Claude Code with extra steps.

## What "Autonomous Fleet" Means

The fleet operates through Mission Control with minimal human intervention:

1. **Tasks appear on MC boards** — created by humans OR by other agents
2. **Gateway polls for work** — picks up tasks assigned to agents
3. **Agents execute** — with their context, constraints, and mode
4. **Results post back to MC** — as task comments, status updates
5. **Agents create follow-up tasks** — Architect's design becomes Engineer's implementation task
6. **ocf-tag reviews** — checks quality, flags regressions, approves or rejects
7. **Git workflow** — agents work on branches, create commits, propose PRs
8. **Quality gates** — tests run automatically, coverage checked, governance enforced
9. **Humans intervene** — only at approval gates, not at every step

## What Needs to Be Built

### 1. Gateway Continuous Loop
The gateway currently handles one request at a time via WebSocket. It needs:
- A polling loop that checks MC for assigned tasks
- Task queue management (priority, dependencies)
- Automatic execution of ready tasks
- Status reporting back to MC
- Error handling and retry

### 2. Agent-to-Agent Task Creation
When an agent finishes work, it should be able to:
- Create follow-up tasks in MC (assigned to the next agent)
- Reference the output of the current task
- Set dependencies (task B can't start until task A is done)

### 3. Git Workflow Integration
Agents working on code should:
- Create branches for their work
- Commit with proper messages
- Push to remote (or create local branches for review)
- The results are reviewable diffs, not just text output

### 4. Quality Gate Automation
Before work is marked "done":
- Tests must pass
- Coverage must not decrease
- Linting must pass
- Governance checks (docs exist for new passes)

### 5. Review and Approval Flow
ocf-tag and human reviewers:
- See completed work in MC
- Approve or reject with comments
- Rejected work creates a revision task
- Approved work gets merged

### 6. Task Templates
Common workflows encoded as MC task templates:
- "Design a component" → Architect task with standard acceptance criteria
- "Implement from design" → Engineer task referencing design output
- "Test implementation" → QA task with coverage requirements
- "Document feature" → Writer task

## Milestone Sequence

### M28: Gateway Continuous Loop
Make the gateway poll MC for tasks and execute them automatically.
- Poll `/boards/{id}/tasks` for tasks in "ready" or "todo" status
- Match tasks to agents by assignment or tag
- Execute via Claude Code with agent context
- Post result as task comment
- Update task status

### M29: Agent Task Chaining
Agents create follow-up tasks after completing their own.
- Agent output includes "next_tasks" suggestions
- Gateway creates those tasks in MC
- Dependencies tracked via MC task dependencies API

### M30: Git Workflow
Agents work on branches and produce reviewable changes.
- Gateway creates a branch before agent executes
- Agent's edits happen on the branch
- Result includes the diff
- Branch is ready for review/merge

### M31: Quality Gates
Automated checks before work is marked done.
- Gateway runs tests after agent completes edit/act tasks
- Coverage, lint, governance checks
- Results posted to MC as task comments
- Task blocked from "done" if gates fail

### M32: Review and Approval
ocf-tag reviews agent work through MC.
- Review tasks auto-created after implementation
- ocf-tag agent assesses quality against requirements
- Approve → task done, branch merge-ready
- Reject → revision task created with feedback

### M33: Task Templates and Workflows
Reusable patterns for common fleet operations.
- Template: "Contribute to NNRT" → design → implement → test → review → merge
- Template: "Build ocf-tag layer" → requirements → design → implement → test → document
- Templates stored in MC and triggered via API

## The Test: NNRT Contribution

Once M28-M33 are built, the fleet's first autonomous mission:
1. Human creates a high-level task: "Add packaging and CI to NNRT"
2. Fleet breaks it down (Architect → plan, DevOps → CI, Engineer → packaging)
3. Agents execute on branches
4. QA validates
5. ocf-tag reviews
6. Human approves final PR

If this works, the fleet can tackle contradiction detection, render consolidation, etc. — all autonomously, all tracked in MC.