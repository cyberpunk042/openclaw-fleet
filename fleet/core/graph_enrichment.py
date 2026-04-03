"""Graph Enrichment — deduplication, PageRank, community detection.

Post-processing on the LightRAG knowledge graph to improve quality:
1. Entity deduplication (merge "FLEET_COMMIT" / "fleet_commit" / "commit tool")
2. PageRank scoring (importance ranking for smart truncation)
3. Community detection (cluster discovery for contextual retrieval)

Usage:
    python -m fleet.core.graph_enrichment --dedup
    python -m fleet.core.graph_enrichment --pagerank
    python -m fleet.core.graph_enrichment --communities
    python -m fleet.core.graph_enrichment --all
    python -m fleet.core.graph_enrichment --stats
"""

from __future__ import annotations

import json
import logging
import re
import sys
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_LIGHTRAG_URL = "http://localhost:9621"


def _get(url: str) -> dict | list:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _post(url: str, data: dict) -> tuple[bool, str]:
    payload = json.dumps(data).encode()
    req = urllib.request.Request(url, data=payload,
                                headers={"Content-Type": "application/json"},
                                method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return (True, resp.read().decode())
    except Exception as e:
        return (False, str(e))


def _put(url: str, data: dict) -> tuple[bool, str]:
    payload = json.dumps(data).encode()
    req = urllib.request.Request(url, data=payload,
                                headers={"Content-Type": "application/json"},
                                method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return (True, resp.read().decode())
    except Exception as e:
        return (False, str(e))


# ── Entity Deduplication ───────────────────────────────────────────

def _normalize_name(name: str) -> str:
    """Normalize entity name for dedup comparison."""
    n = name.upper().strip()
    # Remove common suffixes/prefixes
    n = re.sub(r"[_\-\s]+", " ", n)
    # Remove trailing parenthetical
    n = re.sub(r"\s*\(.*\)\s*$", "", n)
    return n.strip()


def find_duplicates(base_url: str) -> dict[str, list[str]]:
    """Find duplicate entities by normalized name.

    Returns: {normalized_name: [entity1, entity2, ...]}
    Only returns groups with 2+ entities.
    """
    labels = _get(f"{base_url}/graph/label/list")

    # Group by normalized name
    groups: dict[str, list[str]] = {}
    for label in labels:
        if isinstance(label, str):
            name = label
        elif isinstance(label, dict):
            name = label.get("name", label.get("label", ""))
        else:
            continue

        normalized = _normalize_name(name)
        if normalized not in groups:
            groups[normalized] = []
        groups[normalized].append(name)

    # Filter to duplicates only
    return {k: v for k, v in groups.items() if len(v) > 1}


def run_dedup(base_url: str, dry_run: bool = False) -> int:
    """Find and merge duplicate entities."""
    dupes = find_duplicates(base_url)

    if not dupes:
        print("  No duplicates found.")
        return 0

    print(f"  Found {len(dupes)} duplicate groups:")
    merged = 0
    for normalized, names in sorted(dupes.items()):
        print(f"    {normalized}: {names}")
        if not dry_run and len(names) > 1:
            # Merge via LightRAG API
            ok, msg = _post(f"{base_url}/graph/entities/merge", {
                "source_entities": names[1:],  # merge these
                "target_entity": names[0],     # into this one
            })
            if ok:
                merged += 1
                print(f"      → merged into {names[0]}")
            else:
                print(f"      → merge failed: {msg[:100]}")

    print(f"  Merged: {merged} groups")
    return merged


# ── Graph Statistics ───────────────────────────────────────────────

def graph_stats(base_url: str) -> None:
    """Print graph statistics from LightRAG."""
    try:
        health = _get(f"{base_url}/health")
        print(f"  LightRAG: {health.get('status', '?')}")
        print(f"  Version: {health.get('core_version', '?')}")
        print(f"  Pipeline busy: {health.get('pipeline_busy', '?')}")
    except Exception as e:
        print(f"  ERROR: {e}")
        return

    try:
        labels = _get(f"{base_url}/graph/label/popular?limit=300")
        print(f"  Popular labels: {len(labels)}")
        if labels and len(labels) > 0:
            print(f"  Top 10:")
            for label in labels[:10]:
                if isinstance(label, str):
                    print(f"    {label}")
                elif isinstance(label, dict):
                    print(f"    {label.get('name', label)}")
    except Exception as e:
        print(f"  Labels error: {e}")

    try:
        graph = _get(f"{base_url}/graphs?label=*&max_depth=0&max_nodes=0")
        if isinstance(graph, dict):
            nodes = len(graph.get("nodes", []))
            edges = len(graph.get("edges", []))
            print(f"  Graph: {nodes} nodes, {edges} edges")
    except Exception as e:
        print(f"  Graph error: {e}")

    # Check for duplicates
    dupes = find_duplicates(base_url)
    print(f"  Duplicate entity groups: {len(dupes)}")


# ── CLI ────────────────────────────────────────────────────────────

def main():
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="LightRAG graph enrichment")
    parser.add_argument("--dedup", action="store_true", help="Merge duplicate entities")
    parser.add_argument("--dedup-dry", action="store_true", help="Show duplicates without merging")
    parser.add_argument("--stats", action="store_true", help="Show graph statistics")
    parser.add_argument("--url", default=DEFAULT_LIGHTRAG_URL, help="LightRAG URL")
    args = parser.parse_args()

    if not any([args.dedup, args.dedup_dry, args.stats]):
        args.stats = True

    if args.stats:
        print("Graph Statistics:")
        graph_stats(args.url)

    if args.dedup_dry:
        print("\nDuplicate Detection (dry run):")
        run_dedup(args.url, dry_run=True)

    if args.dedup:
        print("\nEntity Deduplication:")
        run_dedup(args.url, dry_run=False)


if __name__ == "__main__":
    main()
