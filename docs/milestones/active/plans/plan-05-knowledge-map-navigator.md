# Plan 05 — Knowledge Map Navigator

**Phase:** 5 (depends on Plans 01-04 — capabilities must exist before map navigates them)
**Source:** Research group 03, PO knowledge map vision
**Milestone IDs:** KM-029 to KM-033

---

## What This Plan Delivers

The code that makes the knowledge map ALIVE. The navigator reads the
map metadata (cross-references, intent-map, injection profiles) and
assembles the right content for the right agent at the right time.

This is where the map stops being documents and becomes a system.

---

## 1. Navigator module (KM-029)

**What:** `fleet/core/map_navigator.py` — the brain reads this to
assemble context from the knowledge map.

**Responsibilities:**
- Read cross-references.yaml → understand system relationships
- Read intent-map.yaml → determine what to inject per situation
- Read injection profiles → determine HOW MUCH to inject per model
- Assemble content from map branches (manuals, standards, methodology)
- Return formatted text ready for context injection

**Interface:**
```python
def navigate(
    agent_name: str,
    agent_role: str,
    current_stage: str,
    model: str,
    context_window: int,
    task_type: str = "",
    artifact_type: str = "",
) -> str:
    """Navigate the knowledge map and return assembled content.

    Reads intent-map for this role+stage combination.
    Selects injection profile based on model+context_window.
    Assembles content from map branches at the profile's depth.

    Returns: formatted text for injection into agent context.
    """
```

**Implementation:**
1. Select profile: model + context_window → opus-1m / sonnet-200k / localai-8k / heartbeat
2. Look up intent: role + stage → intent entry from intent-map.yaml
3. For each branch in the intent:
   - Read content at the profile's depth level (full/condensed/minimal/none)
   - Assemble in the autocomplete chain order
4. Return assembled text

**IaC:** Navigator reads from docs/knowledge-map/ files.
Content is config-driven — change the map files, navigator output changes.

---

## 2. Integrate with context_writer.py (KM-030)

**What:** context_writer.py currently writes raw pre-embed data.
Enhancement: use navigator to assemble map-driven content alongside.

**Current flow:**
orchestrator → preembed.py → context_writer.py → write files

**Enhanced flow:**
orchestrator → preembed.py → **map_navigator.py** → context_writer.py → write files

**Changes to context_writer.py:**
- Accept navigator output alongside pre-embed data
- Merge: map content (static, per role+stage) + pre-embed (dynamic, per task)
- Write combined content to context/ files

---

## 3. Integrate with preembed.py (KM-031)

**What:** preembed.py formats task data for injection.
Enhancement: include map-driven content sections.

**Additions to format_task_full():**
- Add: methodology stage recommendations (from methodology-manual.md)
- Add: relevant skills for this stage (from intent-map)
- Add: relevant commands for this stage
- Add: relevant standards for artifact type (if producing artifact)

**These come FROM the navigator, not hardcoded.**

---

## 4. Rework autocomplete.py (KM-032)

**What:** autocomplete.py was built too early. Now it should be a thin
wrapper around the navigator.

**New autocomplete.py:**
```python
def assemble_task_chain(context, agent_name, agent_role, stage, model, context_window):
    """Assemble task context using the knowledge map navigator."""
    # Get map-driven content
    map_content = navigate(agent_name, agent_role, stage, model, context_window)

    # Get dynamic content from context_assembly
    dynamic_content = format_dynamic(context)

    # Combine in autocomplete chain order:
    # (static agent files handle layers 1-5: IDENTITY→SOUL→CLAUDE→TOOLS→AGENTS)
    # Layer 6: fleet-context.md = fleet state + map_content
    # Layer 7: task-context.md = dynamic_content (task + verbatim + contributions)
    # Layer 8: HEARTBEAT.md (static file)

    return map_content + "\n\n" + dynamic_content
```

**Key insight:** autocomplete.py doesn't BUILD the chain — it MERGES
navigator output (map-driven, static per role+stage) with dynamic
content (task-specific, changes every 30s). The 8-layer onion order
is handled by the gateway injection (static files) + brain writing
(dynamic context files).

---

## 5. LightRAG index integration (KM-033)

**What:** LightRAG indexes the full manual content for semantic search.
This is the "magic book" — agents can QUERY the knowledge map.

**Phased (from LightRAG plan §46):**
1. Deploy LightRAG Docker service (port 9621)
2. Ingest: all knowledge map content (system manuals, agent manuals, module manuals, standards, methodology)
3. Ingest: fleet-vision-architecture.md, design docs, WORK-BACKLOG
4. New MCP tool: `fleet_query_knowledge(question, mode)`
   - Modes: local (entity-level), global (cross-document), hybrid, mix
   - Returns: structured answers with source attribution
5. Brain can query map semantically (not just YAML lookup)

**Dependencies:** Docker running, LightRAG deployed, embedding model (LocalAI bge-m3 CPU)

**This is LATER** — requires Docker + LightRAG deployment. The navigator
works WITHOUT LightRAG (reads YAML + markdown directly). LightRAG ADDS
semantic search on top.

---

## Testing Strategy

All testable in Claude Code without fleet running:

1. **Navigator unit test:**
   - Call navigate("architect", "architect", "reasoning", "opus-4-6", 1000000)
   - Verify: returns methodology + skills + commands + standards content
   - Call navigate("engineer", "software-engineer", "work", "hermes-3b", 8192)
   - Verify: returns minimal content (identity + stage + "call fleet_read_context")

2. **Profile selection test:**
   - opus + 1M → opus-1m profile
   - sonnet + 200K → sonnet-200k profile
   - hermes-3b + 8K → localai-8k profile

3. **Integration test:**
   - Simulate full context assembly: navigator + preembed + context_writer
   - Verify: output file contains both map content and task data
   - Verify: autocomplete chain order preserved

---

## Validation Checklist

- [ ] map_navigator.py reads all knowledge map files
- [ ] Profile selection works for all 4 tiers
- [ ] Intent-map lookup returns correct content per role+stage
- [ ] Navigator output formatted for injection
- [ ] context_writer.py integrates navigator output
- [ ] preembed.py includes map-driven sections
- [ ] autocomplete.py reworked as thin navigator wrapper
- [ ] Unit tests cover all 10 roles × 5 stages × 4 profiles
- [ ] Output verified: right content for right agent at right time

---

## What This Enables

With this plan complete:
- The knowledge map is ALIVE — code reads it and injects content
- Context assembly is MAP-DRIVEN — not hardcoded
- Profile-based injection — Opus gets full detail, LocalAI gets minimal
- Every agent gets exactly the right knowledge for their role + stage
- Adding new knowledge = update map files → navigator picks it up
- Future: LightRAG adds semantic search on top of navigated content
