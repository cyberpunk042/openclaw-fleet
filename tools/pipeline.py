# AUTO-GENERATED-STYLE forwarder to the second brain's pipeline orchestrator.
# Follows the same pattern as tools/gateway.py and tools/evolve.py.
#
# STATUS 2026-04-19: STRUCTURAL STUB.
# Testing revealed brain's pipeline does NOT support --wiki-root and hangs when
# invoked via brain's venv from our CWD (even with CLAUDE.md/.git at openfleet
# root). Brain's tools.pipeline is coupled to brain's own config tree.
# This forwarder exists to:
#   1. Satisfy the structural pattern (tools/ has pipeline forwarder like
#      gateway/view/lint/evolve).
#   2. Document the gap for future brain-side support (analogous to evolve.py's
#      caveat about cross-wiki evolution).
# Invoking this file currently errors out fast — it does NOT attempt execution.
# Use `python3 tools/lint.py --summary` + the scan-from-brain-side workflow
# instead until brain's pipeline accepts --wiki-root.
#
# Brain supports: post, fetch, scan, status, run, chain, gaps, crossref,
# integrations, scaffold, evolve, backlog — but currently on brain's own wiki.
# Per Principle 4 (Declarations Aspirational Until Infrastructure Verifies):
# file existence does NOT imply working cross-wiki forwarding.
"""Wiki pipeline forwarder to the second brain (STRUCTURAL STUB — non-functional)."""

import sys

print(
    "tools/pipeline.py is a structural stub — brain's pipeline does not yet\n"
    "support cross-wiki operation via --wiki-root.\n"
    "\n"
    "Workarounds available today:\n"
    "  - Lint: python3 tools/lint.py --summary\n"
    "  - Scan from brain side: cd ../devops-solutions-research-wiki && \\\n"
    "      PYTHONPATH=. .venv/bin/python -m tools.pipeline scan /home/jfortin/openfleet\n"
    "  - Gateway health: python3 tools/gateway.py health\n"
    "\n"
    "See wiki/domains/planning/integration-chain-mapping-2026-04-18.md Step 16\n"
    "for the broader operational-cadence gap this stub flags.\n",
    file=sys.stderr,
)
sys.exit(2)
