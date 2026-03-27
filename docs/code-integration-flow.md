# Code Integration Flow — Design

## The Problem

Agents work in MC-provisioned workspaces (`workspace-mc-{agent-id}/`). When they write code,
it stays in that workspace. There's no mechanism to get it back to the target project.

## Current State

- Agent receives task via `chat.send`
- Agent works in `workspace-mc-*/` (its OpenClaw workspace)
- Agent reads/writes files there (Claude Code backend)
- Agent reports results to MC via REST API (comments, status)
- Code stays in the workspace — never integrated anywhere

## Constraints

1. Agents should NOT push directly to main branches
2. Human must review before merge
3. Multiple agents may work on the same project
4. Target projects are external repos (NNRT, AICP, etc.) — not the fleet repo itself
5. Workspace dirs are gitignored and ephemeral

## Design Options

### Option A: Workspace = Project Clone

Each agent workspace IS a clone of the target project. When a task is assigned:
1. Workspace is initialized as a clone of the target repo
2. Agent creates a branch: `fleet/{agent-name}/{task-id}`
3. Agent works, commits to branch
4. Agent pushes branch to remote
5. Agent (or lead) creates PR
6. Human reviews and merges

**Pro**: Standard git workflow, PRs for review.
**Con**: Each agent needs its own clone. Workspace management gets complex.
         MC provisions workspace, not us — we'd need to reconfigure it.

### Option B: Shared Project Directory + Branches

All agents work in a shared project directory (not workspace-mc-*).
Task dispatch includes the target project path.
1. Agent checks out a branch in the shared dir
2. Works, commits
3. Pushes and/or creates PR

**Pro**: Single copy of each project.
**Con**: Concurrent agents could conflict. Need branch isolation per task.

### Option C: Agent Produces Patches, Human Applies

Agent works in its workspace and produces a diff/patch file.
1. Agent writes code in workspace
2. Agent runs `git diff` or creates a patch
3. Agent posts patch to MC (board memory or task comment)
4. Human (or automation) applies patch to target repo
5. Human reviews and commits

**Pro**: Simplest, safest. No agent access to target repos needed.
**Con**: Manual step to apply patches. Doesn't scale.

### Option D: Fleet Integration Script

A script that copies agent output from workspace to target project.
1. Agent works in workspace, posts results to MC
2. Script reads task completion, identifies changed files
3. Script copies changes to target project, creates branch + commit
4. Script creates PR (via gh CLI)

**Pro**: Centralized, scriptable, auditable.
**Con**: Needs to track which files changed and where they go.

## Recommended: Option A (Long-term) + Option D (Now)

**Short-term (now):**
- Option D — a `scripts/integrate-task.sh` that:
  1. Takes a task ID and target project path
  2. Reads the agent's workspace to find what changed
  3. Copies changed files to target project
  4. Creates a branch, commits, optionally creates PR
  5. All through a script — human runs it, reviews diff, approves

**Long-term (later):**
- Option A — configure agent workspaces as project clones
  - Requires MC provisioning changes or post-provisioning setup
  - Each agent's workspace targets a specific project
  - Agents push branches, create PRs autonomously

## Short-term Implementation Plan

```bash
# Usage: bash scripts/integrate-task.sh <task-id> <target-project-path>
#
# 1. Find the agent workspace for the task
# 2. List changed/new files in the workspace
# 3. Show diff to human
# 4. On confirmation, copy to target project
# 5. Create branch fleet/<agent>/<task-id>
# 6. Commit and optionally push + create PR
```

## What We Don't Need Yet

- Automated PR creation (human reviews first)
- Multi-project workspace management
- Concurrent access handling (one task at a time per agent for now)
- CI/CD integration (comes with PR workflow)