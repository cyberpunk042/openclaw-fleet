"""Fleet SQLite cache — persistent key-value store with TTL.

Implements core.cache.Cache with SQLite backend.
Supports: caching API responses, indexing fleet state, backup/export.

> "I wanna be able to have every index and/or cache I need and even
> backup it if I really wanted to"
"""

from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional

from fleet.core.cache import Cache


class SQLiteCache(Cache):
    """SQLite-backed cache with TTL support.

    Data persists across restarts. Supports export for backup.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            fleet_dir = os.environ.get("FLEET_DIR", ".")
            db_path = os.path.join(fleet_dir, ".fleet-cache.db")
        self._db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._ensure_table()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self._db_path)
            self._conn.execute("PRAGMA journal_mode=WAL")
        return self._conn

    def _ensure_table(self) -> None:
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expires_at REAL NOT NULL,
                created_at REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_expires
            ON cache(expires_at)
        """)
        conn.commit()

    async def get(self, key: str) -> Optional[Any]:
        """Get a cached value. Returns None if missing or expired."""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT value, expires_at FROM cache WHERE key = ?", (key,)
        ).fetchone()

        if row is None:
            return None

        value_str, expires_at = row
        if time.time() > expires_at:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()
            return None

        return json.loads(value_str)

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Set a cached value with TTL."""
        now = time.time()
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO cache (key, value, expires_at, created_at) VALUES (?, ?, ?, ?)",
            (key, json.dumps(value, default=str), now + ttl_seconds, now),
        )
        conn.commit()

    async def delete(self, key: str) -> None:
        """Delete a cached value."""
        conn = self._get_conn()
        conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        conn.commit()

    async def clear(self, prefix: str = "") -> None:
        """Clear cache entries. If prefix given, only matching keys."""
        conn = self._get_conn()
        if prefix:
            conn.execute("DELETE FROM cache WHERE key LIKE ?", (f"{prefix}%",))
        else:
            conn.execute("DELETE FROM cache")
        conn.commit()

    # ─── Extras (not in base interface) ─────────────────────────────────

    def cleanup_expired(self) -> int:
        """Remove all expired entries. Returns count removed."""
        conn = self._get_conn()
        cursor = conn.execute(
            "DELETE FROM cache WHERE expires_at < ?", (time.time(),)
        )
        conn.commit()
        return cursor.rowcount

    def stats(self) -> dict:
        """Get cache statistics."""
        conn = self._get_conn()
        total = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
        expired = conn.execute(
            "SELECT COUNT(*) FROM cache WHERE expires_at < ?", (time.time(),)
        ).fetchone()[0]
        size = os.path.getsize(self._db_path) if os.path.exists(self._db_path) else 0
        return {
            "total_entries": total,
            "expired_entries": expired,
            "active_entries": total - expired,
            "db_size_bytes": size,
            "db_path": self._db_path,
        }

    def export_json(self, output_path: str) -> int:
        """Export all non-expired entries as JSON. Returns count exported."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT key, value, expires_at, created_at FROM cache WHERE expires_at > ?",
            (time.time(),),
        ).fetchall()

        entries = [
            {
                "key": row[0],
                "value": json.loads(row[1]),
                "expires_at": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]

        with open(output_path, "w") as f:
            json.dump(entries, f, indent=2, default=str)

        return len(entries)

    def import_json(self, input_path: str) -> int:
        """Import entries from JSON export. Returns count imported."""
        with open(input_path) as f:
            entries = json.load(f)

        conn = self._get_conn()
        count = 0
        for entry in entries:
            if entry.get("expires_at", 0) > time.time():
                conn.execute(
                    "INSERT OR REPLACE INTO cache (key, value, expires_at, created_at) VALUES (?, ?, ?, ?)",
                    (
                        entry["key"],
                        json.dumps(entry["value"], default=str),
                        entry["expires_at"],
                        entry["created_at"],
                    ),
                )
                count += 1
        conn.commit()
        return count

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None