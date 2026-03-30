# Transpose Layer — Object ↔ Rich HTML for Plane

**Date:** 2026-03-30
**Status:** Design — from discussion with PO
**Scope:** Bidirectional transpose between structured objects (agent data)
and rich HTML (Plane presentation)

---

## PO Requirements (Verbatim)

> "and possibly update the fields and the html data that must transpore
> into a rich html without having the AI to think to hard about that part
> when it can be automated with a proper tool with simple args and logical
> framework."

> "TRANSPOSE.... YOU HAVE DATA e.g. JSON AND IT TRANSPOSE INTO A FUCKING
> RICH HTML...... and in reverse.... so the AI works with the OBJECT and
> the plan has the RICH HTML....."

> "The one that follow high standard with high standard content required.
> + some optionals"

> "This is a whole series of milestones again.. STOP MINIMIZING...."

> "we have to understand that one PM task can be multiple cycle of Fleet
> Operation Cycle... since a ocmc task for be only a piece of a stage
> from one perspective, that need to keep adding up to be able to have
> the confirmations for the readiness increase."

> "So the agent will keep track of their work on a task and they will add
> comments and/or event sub-task when they need to do their progressive
> work and they leave their trace"

---

## What the Transpose Layer Is

The transpose layer is the bridge between two worlds:

**Agent world:** Structured objects. JSON. Dicts with typed fields.
The agent works with data — it creates an analysis finding object with
`title`, `finding`, `files`, `implications`. Simple args. No HTML.

**Plane world:** Rich HTML. Visual presentation. Tables, blockquotes,
headers, code blocks. What the PO sees in the Plane UI.

The transpose layer converts between these worlds:
- **Object → Rich HTML** (write to Plane): agent's structured data
  becomes a beautiful, high-standard HTML document in the Plane issue
- **Rich HTML → Object** (read from Plane): the HTML in Plane is parsed
  back into the structured object so the agent can work with it

The agent NEVER writes HTML. The agent NEVER parses HTML. The transpose
layer handles all of that. The agent works with objects. Plane shows
rich HTML. The transpose layer is the bridge.

---

## Why It Exists

### Progressive Work Across Cycles

One PM task spans multiple fleet operation cycles. Each cycle, the agent
does a piece of work — adds a finding, updates the plan, increases
readiness. The work accumulates in the object. The transpose layer
renders the accumulated object as rich HTML after each update.

Example: Analysis stage on an epic
- Cycle 1: Agent examines files A, B, C → adds findings to object
- Cycle 2: Agent examines files D, E → adds more findings
- Cycle 3: Agent identifies implications → adds to object
- Each cycle: transpose layer renders the growing object as rich HTML
  in the Plane issue description
- PO sees a progressively richer analysis document in Plane

### Standards Enforcement

Each artifact type has required fields from the standards library
(fleet/core/standards.py). The transpose layer validates the object
against the standard before rendering. Missing required fields are
flagged. The rendered HTML reflects the standard — required sections
are always present, optional sections appear when populated.

### AI Doesn't Think About Formatting

The PO explicitly said: "without having the AI to think too hard about
that part when it can be automated." The agent calls a tool with simple
args. The tool builds the object. The transpose layer renders the HTML.
The agent doesn't compose HTML, doesn't worry about table formatting,
doesn't build blockquotes. It provides data. The layer provides
presentation.

---

## Artifact Types and Their Objects

From the standards library (fleet/core/standards.py), each artifact type
has a defined object schema:

### Analysis Document Object
```json
{
  "type": "analysis_document",
  "title": "...",
  "scope": "...",
  "current_state": "...",
  "findings": [
    {
      "title": "...",
      "finding": "...",
      "files": ["path/to/file.py"],
      "implications": "..."
    }
  ],
  "open_questions": ["..."]
}
```

Transposes to rich HTML with:
- H2 header with title
- Scope section
- Findings as structured sections with file references in `<code>` tags
- Open questions as a list

### Investigation Document Object
```json
{
  "type": "investigation_document",
  "title": "...",
  "scope": "...",
  "findings": "...",
  "options": [
    {"name": "Option A", "pros": "...", "cons": "..."}
  ],
  "sources": ["..."],
  "recommendations": "..."
}
```

Transposes to rich HTML with:
- Options as a comparison table (`<table>` with Option/Pros/Cons columns)
- Sources as a list
- Recommendations as a blockquote

### Plan Object
```json
{
  "type": "plan",
  "title": "...",
  "requirement_reference": "...",
  "approach": "...",
  "target_files": ["path/to/file.py"],
  "steps": ["Step 1...", "Step 2..."],
  "acceptance_criteria_mapping": {"criterion": "how it's met"}
}
```

Transposes to rich HTML with:
- Verbatim requirement in blockquote (reuses existing injection pattern)
- Target files in `<code>` tags
- Steps as ordered list
- Criteria mapping as a table

### Progress Update Object
```json
{
  "type": "progress_update",
  "what_was_done": "...",
  "what_is_next": "...",
  "blockers": "...",
  "readiness_before": 30,
  "readiness_after": 50
}
```

Transposes to rich HTML with:
- Readiness indicator (visual progress)
- Structured sections for done/next/blockers

### Bug Report Object
```json
{
  "type": "bug",
  "title": "...",
  "steps_to_reproduce": ["Step 1", "Step 2"],
  "expected_behavior": "...",
  "actual_behavior": "...",
  "environment": "...",
  "impact": "...",
  "evidence": "..."
}
```

Transposes to rich HTML with:
- Steps as numbered list
- Expected vs actual clearly separated
- Evidence in code block if present

### Completion Claim Object
```json
{
  "type": "completion_claim",
  "pr_url": "...",
  "summary": "...",
  "acceptance_criteria_check": [
    {"criterion": "...", "met": true, "evidence": "..."}
  ],
  "files_changed": ["..."]
}
```

Transposes to rich HTML with:
- PR link
- Criteria as checklist table (criterion, met ✓/✗, evidence)
- Files changed in code tags

---

## Bidirectional: Read and Write

### Write: Object → Rich HTML

Agent produces object → transpose layer validates against standard →
renders as rich HTML → written to Plane issue description_html

The rendered HTML uses HTML comment markers (like the verbatim
requirement pattern) to preserve the object structure within the HTML.
This allows reverse transposition.

```html
<!-- fleet:artifact:start type="analysis_document" -->
<h2>Analysis: Header Structure Investigation</h2>
<!-- fleet:field:scope -->
<p><strong>Scope:</strong> DashboardShell.tsx header section</p>
<!-- fleet:field:findings -->
<h3>Findings</h3>
<!-- fleet:finding:0 -->
<p><strong>Finding:</strong> Center section has flex-1 with only OrgSwitcher</p>
<p><strong>Files:</strong> <code>DashboardShell.tsx</code></p>
<p><strong>Implications:</strong> Room for fleet controls after OrgSwitcher</p>
<!-- fleet:finding:end -->
<!-- fleet:artifact:end -->
```

The HTML comment markers make the rich HTML machine-parseable. The same
HTML is beautiful in Plane AND extractable back to an object.

### Read: Rich HTML → Object

Plane issue has rich HTML → transpose layer finds the artifact markers →
extracts field values → returns the structured object to the agent

The agent gets the object. It modifies it (adds a finding, updates a
field). The transpose layer renders the updated object back to HTML.
Plane shows the updated rich content.

---

## How the Agent Uses It

The agent calls MCP tools with simple args:

```
fleet_artifact_update(
  task_id="...",
  artifact_type="analysis_document",
  field="findings",
  action="append",
  data={
    "title": "Header structure",
    "finding": "Center section has room for controls",
    "files": ["DashboardShell.tsx"],
    "implications": "FleetControlBar can go here"
  }
)
```

The tool:
1. Reads the current artifact object from the task (extracted from HTML or custom field)
2. Validates the update against the standard
3. Applies the update (appends to findings list)
4. Transposes the updated object to rich HTML
5. Writes the HTML to Plane issue description
6. Updates OCMC task fields as needed
7. Returns the updated object to the agent

The agent never sees HTML. It works with objects. The tool does everything.

---

## Relationship to Existing Systems

### Standards Library (fleet/core/standards.py)
Defines the required and optional fields per artifact type. The transpose
layer validates against these. A task can't advance to the next stage if
required fields are missing.

### Methodology System (fleet/core/methodology.py)
Each stage produces artifacts. Analysis stage produces analysis_document.
Investigation produces investigation_document. Reasoning produces plan.
The methodology checks verify the artifact object has required fields.

### Plane Sync (fleet/core/plane_sync.py)
The transpose layer extends the sync. Currently sync handles custom
fields and labels. The transpose layer handles the description_html —
the rich content body of issues.

### Verbatim Requirement (fleet/core/plane_methodology.py)
The existing verbatim injection pattern (HTML comment markers +
blockquote) is the prototype for the transpose layer. The transpose
layer generalizes this to ALL artifact types.

### MCP Tools (fleet/mcp/tools.py)
New tools for artifact CRUD. Simple args in, structured dicts out.
The transpose happens inside the tool — agent never sees HTML.

---

## Milestones

### T01: Transpose Engine Core
- Object → HTML rendering for all 7 artifact types
- HTML → Object parsing using markers
- Validation against standards
- Bidirectional: read and write

### T02: MCP Tools for Artifact CRUD
- fleet_artifact_create(task_id, artifact_type, data)
- fleet_artifact_update(task_id, field, action, data)
- fleet_artifact_read(task_id) → returns object
- Simple args, structured output

### T03: Progressive Work Tracking
- Artifact objects persist across cycles
- Agent reads previous state, adds to it
- Each update generates a comment trail
- Readiness calculated from artifact completeness

### T04: Plane Integration
- Artifacts rendered to Plane issue description_html
- Bidirectional sync — Plane edits reflected in object
- Rich HTML with markers for machine parsing
- Visual quality matching Plane's existing pages

### T05: Standards Validation
- Artifact objects validated against standards library
- Missing required fields flagged
- Completeness score contributes to readiness
- Methodology checks reference artifact state

### T06: Sub-task Generation
- When a stage's work needs breakdown, agent creates sub-tasks
- Sub-task artifacts roll up to parent
- Parent artifact aggregates child findings/results

### T07: Rich HTML Templates
- Template library for each artifact type
- High-standard visual output
- Consistent formatting across all artifacts
- Tables, blockquotes, code blocks, lists used appropriately

---

## Open Questions

- How large can an artifact object get before Plane description_html
  hits limits? Is there a size cap?
- Should artifact history be tracked? (version 1, version 2, etc.)
  Or just current state?
- How does the PO edit artifacts in Plane? If PO changes the HTML
  directly, does the transpose layer preserve the change?
- Should the object be stored in a custom field (JSON type) as well
  as in the HTML? Dual storage for reliability?
- How do sub-task artifacts aggregate into parent artifacts?