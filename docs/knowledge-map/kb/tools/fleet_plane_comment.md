# fleet_plane_comment

**Type:** MCP Tool (Plane integration)
**System:** S08 (MCP Tools), S17 (Plane Integration)
**Module:** fleet/mcp/tools.py:1863-1940
**Stage gating:** None
**Requires:** Plane configured (PLANE_URL + PLANE_API_KEY)

## Purpose

Post a comment on a Plane issue for cross-surface communication. Supports @agent-name mentions that route to the mentioned agent's next heartbeat context via the sync worker. This is how agents communicate about Plane issues — updates, questions, handoffs, and status reports all flow through issue comments.

## Parameters

- `project` (string, required) — Project identifier (AICP, OF, DSPD, NNRT)
- `issue_id` (string, required) — Plane issue UUID or sequence number
- `comment` (string, required) — Comment text (plain text — wrapped in `<p>` HTML)
- `mention` (string) — Agent name to @mention (e.g., "architect"). Wrapped in `<strong>` and prepended to comment. Routes to agent feed.

## Chain Operations

```
fleet_plane_comment(project, issue_id, comment, mention)
├── CHECK: Plane configured?
├── RESOLVE PROJECT: plane.list_projects(ws) → find by identifier
├── BUILD HTML: 
│   ├── Without mention: <p>{comment}</p>
│   └── With mention: <p><strong>@{mention}</strong> {comment}</p>
├── POST COMMENT: POST /api/v1/workspaces/{ws}/projects/{id}/issues/{issue_id}/comments/
│   ├── Body: {comment_html: ...}
│   └── Returns: comment_id
├── IRC (if mention): "[{agent}] 💬 @{mention} on Plane: {comment[:40]}"
└── EVENT: fleet.plane.issue_commented
    ├── subject: issue_id
    ├── recipient: mentioned agent (or "all" if no mention)
    ├── priority: "important" if mention, "info" otherwise
    ├── mentions: [mention] if provided
    ├── tags: [plane, comment, project:{project}]
    └── surfaces: [internal, channel, plane]
```

## Who Uses It

| Role | When | Why |
|------|------|-----|
| PM | Sprint management | Update issue status, post progress, @mention assignees |
| Writer | Documentation | Post doc updates, ask engineers for clarification |
| Fleet-ops | Review | Post review decisions on linked Plane issues |
| Any agent | Cross-surface | Respond to PO comments on Plane issues |
| Orchestrator | Task completion | Auto-post completion summary (via event chain) |

## The @Mention Routing Pipeline

```
Agent calls fleet_plane_comment with mention="architect"
├── Comment posted on Plane with <strong>@architect</strong>
├── Event emitted: fleet.plane.issue_commented (recipient: architect)
├── IRC: @architect notified in #fleet
├── Event router: routes to architect's event feed (tag subscription)
├── Next heartbeat: architect's fleet-context.md includes the mention
└── Architect wakes, sees Plane comment in MESSAGES section
```

Cross-surface bridge: PO comments on Plane → agent sees in heartbeat. Agent comments on Plane → PO sees in Plane UI.

## Relationships

- DEPENDS ON: Plane configured, project exists
- POSTS TO: Plane API (issue comments endpoint)
- ROUTES MENTIONS: event_router.py → agent event feeds → heartbeat context
- NOTIFIES: IRC #fleet (if mention present)
- EMITS: fleet.plane.issue_commented event
- CONSUMED BY: event_router.py (routes to mentioned agent), cross_refs.py (cross-references)
- CONNECTS TO: fleet_plane_update_issue (comments complement status updates)
- CONNECTS TO: fleet_plane_create_issue (comment on issues you created)
- CONNECTS TO: fleet-communicate skill (maps tool to "Plane comment" surface)
- NOT YET IMPLEMENTED: Plane comments → agent context bidirectional (plane_watcher detects but doesn't route to pre-embed yet)
