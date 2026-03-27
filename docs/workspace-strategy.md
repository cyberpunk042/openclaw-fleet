# Workspace Strategy — Evaluation

## The Problem

Agents run in MC-provisioned workspaces (`workspace-mc-{id}/`). These workspaces contain
MC bootstrap files (TOOLS.md, SOUL.md, etc.) but NO project code. Agents can't read the
codebase they're supposed to work on.

## What We Have

MC provisions per-agent workspaces with:
- TOOLS.md (credentials: AUTH_TOKEN, BASE_URL, BOARD_ID)
- SOUL.md (role + MC workflow instructions)
- AGENTS.md (session startup protocol)
- HEARTBEAT.md (heartbeat protocol)
- IDENTITY.md, USER.md, MEMORY.md, BOOTSTRAP.md

OpenClaw runs Claude Code with the workspace as CWD.
Claude Code can read/write files, run commands, use git — all within the workspace.

TOOLS.md already has `WORKSPACE_ROOT` (fleet dir) and `WORKSPACE_PATH` (agent workspace).

## Requirements

1. Agent must be able to read target project code
2. Agent must be able to write code that fits the project
3. Changes must be on a branch (never directly on main)
4. Multiple agents can work on the same project without conflicts
5. Human reviews before merge
6. Minimal token waste — agent shouldn't read the whole codebase
7. Minimal disk waste — don't clone N copies of each project
8. Minimal time waste — project should be ready before agent starts
9. Works for any project (NNRT, AICP, fleet itself, future projects)
10. Must not break MC provisioning (TOOLS.md, SOUL.md must still work)

## Options Evaluated

### Option 1: Clone Per Task

At dispatch time, clone the target repo into the agent's workspace.

```
workspace-mc-{id}/
├── TOOLS.md, SOUL.md, ...     (MC files)
└── project/                    (cloned target repo)
```

**Performance:**
- Full clone per task: ~5-30s depending on repo size
- Disk: full copy per agent per project (wastes space)
- Agent reads project/ as working directory

**Pros:** Full isolation, clean state per task.
**Cons:** Slow, disk-heavy, clone per task is wasteful. Agent has to navigate into `project/`.
**Verdict:** Too expensive for routine tasks.

### Option 2: Git Worktrees

Single clone per project (shared object store), worktree per agent.

```
projects/
├── nnrt/                       (bare or main clone)
│   ├── .git/                   (shared object store)
│   └── worktrees/
│       ├── architect-{task}/   (worktree on fleet/architect/xxxx branch)
│       └── sw-eng-{task}/      (worktree on fleet/sw-eng/xxxx branch)
```

Agent workspace symlinked or configured to point at their worktree.

**Performance:**
- First clone: one-time cost per project
- Worktree creation: instant (~100ms, git metadata only)
- Disk: shared objects, each worktree only stores diff
- Branch isolation automatic

**Pros:** Fast, disk-efficient, standard git, per-agent isolation, branches ready.
**Cons:** Worktree management adds complexity. MC workspace can't directly be the worktree
  (MC provisions its own workspace). Need to configure agent to work in worktree CWD.
**Verdict:** Best balance of performance and isolation.

### Option 3: Shared Project Directory

All agents work in the same project directory, on different branches.

```
projects/nnrt/                  (single copy, agents checkout branches)
```

**Performance:** Minimal disk, no clone time.
**Pros:** Simplest setup.
**Cons:** Branch switching is NOT concurrent-safe. Two agents can't work simultaneously.
  Git locks, index conflicts, dirty working tree issues.
**Verdict:** Only works with one agent at a time. Doesn't scale.

### Option 4: Agent Workspace IS the Project

Configure MC to provision the agent workspace inside the project directory.

```
projects/nnrt/
├── .git/
├── src/
├── TOOLS.md                    (MC file, in project root)
├── SOUL.md                     (MC file, in project root)
└── ...
```

**Performance:** Zero overhead — agent is already in the project.
**Pros:** No setup needed, agent has full access.
**Cons:** MC bootstrap files pollute the project. Multiple agents can't share the dir.
  TOOLS.md with auth tokens in a project repo is a security risk.
**Verdict:** Too dirty. MC files don't belong in project repos.

### Option 5: Worktree + MC Overlay

Git worktree for project access + MC files symlinked or copied in.

```
workspace-mc-{id}/
├── TOOLS.md, SOUL.md, ...     (MC provisioned, stays here)
└── .claude/settings.json       (Claude Code permissions)

worktrees/{project}/{agent}-{task}/
├── .git                        (worktree link)
├── src/, tests/, ...           (project files)
├── TOOLS.md → ../../workspace-mc-{id}/TOOLS.md  (symlink)
└── SOUL.md → ../../workspace-mc-{id}/SOUL.md    (symlink)
```

**Performance:** Same as Option 2. Symlinks are instant.
**Pros:** Clean separation. MC files accessible via symlink. Project files are the real thing.
**Cons:** Symlink management. Claude Code CWD needs to be the worktree, not the MC workspace.
  Requires reconfiguring how OpenClaw sets the agent's working directory.
**Verdict:** Clean but complex. Need to understand if OpenClaw supports CWD override per session.

## Recommended: Option 2 (Git Worktrees) with Simple CWD Strategy

### How It Works

1. **Project registry** (`config/projects.yaml` already exists) maps project names to git URLs
2. **First time**: `scripts/clone-project.sh <project>` clones the repo to `projects/<name>/`
3. **At dispatch time**: `dispatch-task.sh` creates a git worktree for the task:
   ```
   projects/<name>/
   git worktree add worktrees/<agent>-<task-short> -b fleet/<agent>/<task-short>
   ```
4. **Task message** includes the worktree path so the agent knows where to work
5. **Agent** reads TOOLS.md from its MC workspace, then `cd` to the worktree to do actual work
6. **After completion**: `integrate-task.sh` pushes the branch from the worktree, creates PR
7. **Cleanup**: `git worktree remove` after PR merged or task abandoned

### What Changes

- `dispatch-task.sh`: adds worktree creation, includes path in task message
- `integrate-task.sh`: pushes from worktree instead of copying files
- New: `scripts/clone-project.sh` — one-time project setup
- New: `scripts/cleanup-worktrees.sh` — remove stale worktrees
- `config/projects.yaml`: add git URLs

### Performance Profile

| Operation | Time | Disk |
|-----------|------|------|
| First clone | 5-30s (one-time) | Full repo |
| Worktree creation | <1s | Negligible (metadata) |
| Agent CWD switch | 0s | 0 |
| Branch push | 2-5s | 0 |
| Worktree cleanup | <1s | Frees metadata |

### What We Don't Change

- MC provisioning (TOOLS.md, SOUL.md stay in workspace-mc-*)
- OpenClaw agent configuration
- Agent SOUL.md / MC workflow instructions (agent still calls MC API same way)
- Board/task structure in MC

### Confirmed: Agents Can Work With Absolute Paths

Claude Code uses absolute paths for file tools (read, write, edit). An agent CAN:
- Read TOOLS.md from its MC workspace at session start
- Then work in a completely different directory using absolute paths
- Shell commands (`exec` tool) can `cd` to the worktree

This means we don't need to change OpenClaw agent workspace config. The task message
just includes the worktree path, and the agent works there.

### Design Decisions

1. **Worktrees persist per agent-project pair, not per task.**
   - Saves creation time for repeat work on the same project
   - Branch is reset/updated before each task
   - Cleanup script removes stale worktrees

2. **Projects registered in `config/projects.yaml` with git URLs (not absolute paths).**
   - Portable across machines
   - Clone to `projects/<name>/` at setup time or on first use

3. **Task message includes the project working directory.**
   - `dispatch-task.sh` resolves the worktree path and includes it in the message
   - Agent reads TOOLS.md first, then works in the specified directory