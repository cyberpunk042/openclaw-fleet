# System 10: Transpose Layer — Object ↔ Rich HTML

**Type:** Fleet System
**ID:** S10
**Files:** transpose.py (~370 lines), artifact_tracker.py (~200 lines)
**Total:** 573 lines
**Tests:** 35+

## What This System Does

Bridges agent-friendly structured objects and human-readable rich HTML on Plane. Agents work with Python dicts (fields, values). Plane displays formatted documents (h2 titles, blockquotes, tables, lists). Transpose converts bidirectionally. The hidden JSON data blob embedded in HTML IS the source of truth — the visible HTML is just a rendering.

Content OUTSIDE artifact markers is NEVER touched — PO can add manual notes alongside fleet artifacts safely.

## How It Works

### Object → HTML (to_html)

```
to_html(artifact_type, object_dict)
├── Look up type-specific renderer (7 registered)
├── Render fields as rich HTML:
│   ├── h2 titles
│   ├── blockquotes for verbatim
│   ├── ordered lists for steps
│   ├── tables for criteria/options
│   └── per-type layout (analysis ≠ plan ≠ bug)
├── Embed object as hidden JSON data blob:
│   <span class="fleet-data" style="display:none">{json}</span>
├── Wrap in artifact markers:
│   <span class="fleet-artifact-start" data-type="{type}"></span>
│   ...rendered HTML + hidden JSON...
│   <span class="fleet-artifact-end"></span>
└── Return complete HTML string
```

### HTML → Object (from_html)

```
from_html(html_string)
├── Regex finds hidden fleet-data span
├── HTML-unescape the JSON string
├── JSON parse → dict
└── Return the object (the source of truth)
```

The JSON blob IS the data. The visible HTML is decoration. Agent reads back the OBJECT, not the HTML.

### Update Flow

```
fleet_artifact_update("findings", [...new finding...], append=True)
├── from_html → extract current object
├── Merge update:
│   ├── APPEND for list fields (findings, steps, options)
│   └── REPLACE for scalar fields (scope, title)
├── to_html → re-render with updated object
├── Regex replaces old artifact section in Plane HTML
│   (content OUTSIDE markers preserved — PO notes safe)
└── Write updated HTML back to Plane
```

## 7 Implemented Renderers

| Type | Produces | Key Layout |
|------|----------|-----------|
| analysis_document | Analysis findings | Scope paragraph, findings as blockquotes, implications |
| investigation_document | Research report | Options as comparison table (name/pros/cons) |
| plan | Implementation plan | Verbatim blockquote, ordered steps, criteria mapping table |
| progress_update | Status | Summary text |
| bug | Bug report | Numbered reproduction steps, expected vs actual split |
| completion_claim | Done claim | PR URL, criteria check table (criterion/met/evidence) |
| pull_request | PR description | Changes, testing, task reference |

## 5 Missing Renderers (block contribution flow)

security_assessment, qa_test_definition, ux_spec, documentation_outline, compliance_report — without these, specialist contributions can't be structured artifacts on Plane.

## Artifact Completeness Tracking

artifact_tracker.py checks object against standard's required fields:
- Maps filled required fields → required_pct (0-100)
- Calculates suggested_readiness via 8-tier scale:
  0% → 0, <25% → 10, <40% → 20, <50% → 30, <60% → 50, <80% → 70, <90% → 80, <100% → 90, 100% → 95
- Tracker SUGGESTS readiness; PO SETS it.

## Progressive Work Pattern

Across multiple orchestrator cycles, agent fills fields incrementally:
1. fleet_artifact_create (title only — completeness ~10%)
2. fleet_artifact_update × N (fill fields — completeness rises)
3. Completeness reaches 100% → suggested_readiness increases → PO reviews

## Why Spans Not Comments

Plane CE strips HTML comments (`<!-- -->`). Fleet uses `<span>` elements with `display:none` CSS because Plane preserves them. The fleet-data class enables reliable regex extraction.

## Relationships

- USED BY: fleet_artifact_create, fleet_artifact_update, fleet_artifact_read (MCP tools)
- USED BY: context_assembly.py (artifact section in task context)
- USED BY: plane_sync.py (artifact HTML on Plane issues)
- CONNECTS TO: S08 MCP tools (artifact tools use transpose)
- CONNECTS TO: S09 standards (completeness checks against standards)
- CONNECTS TO: S17 Plane (HTML lives in Plane issue description_html)
- CONNECTS TO: S07 orchestrator (Step 0 — artifact state in pre-embed)
- CONNECTS TO: S01 methodology (completeness → readiness → stage progression)
- NOT YET IMPLEMENTED: 5 contribution renderers, renderer quality enhancements (syntax highlighting, collapsible sections), live Plane round-trip testing

## For LightRAG Entity Extraction

Key entities: to_html (render), from_html (extract), artifact_type (7 implemented + 5 designed), fleet-artifact-start/end markers, fleet-data span (hidden JSON), ArtifactCompleteness (required_pct, suggested_readiness).

Key relationships: Agent CREATES artifact (fleet_artifact_create). Agent UPDATES fields (fleet_artifact_update). Transpose RENDERS object to HTML. Transpose EXTRACTS object from HTML. Plane STORES HTML. Completeness SUGGESTS readiness. PO DECIDES readiness.
