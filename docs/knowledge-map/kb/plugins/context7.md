# context7

**Type:** Claude Code Plugin + MCP Server (two deployment modes)
**Source:** github.com/upstash/context7 — 46,978 stars
**Package:** @upstash/context7-mcp (npm)
**Assigned to:** Engineer, Architect, Technical Writer

## What It Actually Is

Two things sharing one name — and understanding the difference matters:

**As a plugin:** context7 automatically INJECTS relevant library documentation into the agent's context at session start and when libraries are referenced. The agent doesn't need to ask — context7 detects which libraries are being used and proactively provides current docs. This prevents the #1 Claude Code problem: hallucinated APIs from stale training data.

**As an MCP server:** context7 provides two TOOLS that agents call on-demand:
1. `resolve-library-id` — takes a library name (e.g., "flask") and returns the Context7 library ID
2. `query-docs` — takes a library ID + query and returns current documentation

The plugin is passive (injects automatically). The MCP server is active (agent queries explicitly). Both use the same upstream documentation index.

## Why This Matters for Fleet

Claude's training data has a cutoff. When an agent implements features using Flask 3.x, React 19, or any library updated after training, Claude may suggest APIs that don't exist or patterns that are deprecated. context7 fixes this by providing the CURRENT documentation at the time of use.

For the fleet, this means:
- Engineer implementing with a library gets current API docs, not hallucinated ones
- Architect evaluating libraries for a design decision sees current capabilities
- Writer documenting API usage gets accurate signatures and patterns

## Plugin vs MCP Server — When to Use Which

| Mode | How | When |
|------|-----|------|
| Plugin (automatic) | Detects library references → injects docs | Always-on for supported agents. Zero effort. |
| MCP server (on-demand) | Agent calls resolve-library-id → query-docs | When agent needs specific docs not auto-detected. Investigation stage research. |

**Recommendation:** Install BOTH. Plugin for passive injection (catches most cases). MCP server for active queries (when agent needs to look up something specific).

## Configuration

- **Install plugin:** `/plugin install context7`
- **Install MCP server:** Add to agent-tooling.yaml:
  ```yaml
  - name: context7
    package: "@upstash/context7-mcp"
  ```
- **API key:** Optional. Free tier has rate limits. API key increases limits.
- **No other config needed.** It discovers libraries from the project automatically.

## Assigned Roles

| Role | Mode | Why |
|------|------|-----|
| Engineer | Plugin + MCP | Implementing with libraries daily — needs current APIs |
| Architect | Plugin + MCP | Evaluating libraries for design decisions |
| Writer | Plugin | Documenting API usage — accuracy is critical |
| QA | MCP only | Occasionally queries test framework docs |
| DevOps | MCP only | Occasionally queries infrastructure tool docs |

## Methodology Stages

| Stage | Usage |
|-------|-------|
| investigation | Active research — agent queries Context7 MCP for library capabilities, compares options |
| reasoning | Verify planned approach uses current APIs (not deprecated patterns) |
| work | Reference current docs during implementation |

## Relationships

- INSTALLED BY: scripts/install-plugins.sh (plugin) + scripts/setup-agent-tools.sh (MCP server)
- CONFIGURED IN: agent-tooling.yaml (MCP server per role) + plugin install (per agent)
- CONNECTS TO: foundation-deps skill (choosing the right libraries — Context7 shows current capabilities)
- CONNECTS TO: feature-implement skill (implementation references current docs)
- CONNECTS TO: architecture-propose skill (design decisions informed by current library state)
- CONNECTS TO: feature-document skill (writer gets accurate API signatures)
- CONNECTS TO: knowledge map (Context7 provides EXTERNAL library knowledge; our map provides INTERNAL fleet knowledge)
- CONNECTS TO: LightRAG (complementary — Context7 = external library docs, LightRAG = internal project knowledge graph)
- CONNECTS TO: /plan command (during read-only exploration, agent can query Context7 for library research)
- FILLS THE GAP: Claude's training data cutoff means agents don't know about new library versions. Context7 bridges this with live documentation.
- ANALOGY: Context7 is to external libraries what our knowledge map is to internal fleet systems — both prevent hallucination by providing current, accurate information.
