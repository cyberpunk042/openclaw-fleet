"""Tests for fleet SQLite cache."""

import asyncio
import json
import os
import tempfile

import pytest

from fleet.infra.cache_sqlite import SQLiteCache


@pytest.fixture
def cache():
    """Create a temporary cache for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    c = SQLiteCache(db_path)
    yield c
    c.close()
    os.unlink(db_path)


def test_set_and_get(cache):
    asyncio.run(_test_set_get(cache))


async def _test_set_get(cache):
    await cache.set("key1", {"hello": "world"})
    result = await cache.get("key1")
    assert result == {"hello": "world"}


def test_get_missing(cache):
    result = asyncio.run(cache.get("nonexistent"))
    assert result is None


def test_ttl_expiry(cache):
    asyncio.run(_test_ttl(cache))


async def _test_ttl(cache):
    await cache.set("short", "value", ttl_seconds=0)  # Already expired
    result = await cache.get("short")
    assert result is None


def test_delete(cache):
    asyncio.run(_test_delete(cache))


async def _test_delete(cache):
    await cache.set("del_me", "value")
    await cache.delete("del_me")
    result = await cache.get("del_me")
    assert result is None


def test_clear_all(cache):
    asyncio.run(_test_clear_all(cache))


async def _test_clear_all(cache):
    await cache.set("a", 1)
    await cache.set("b", 2)
    await cache.clear()
    assert await cache.get("a") is None
    assert await cache.get("b") is None


def test_clear_prefix(cache):
    asyncio.run(_test_clear_prefix(cache))


async def _test_clear_prefix(cache):
    await cache.set("tasks:board1:list", [1, 2])
    await cache.set("tasks:board2:list", [3, 4])
    await cache.set("agents:list", [5])
    await cache.clear(prefix="tasks:")
    assert await cache.get("tasks:board1:list") is None
    assert await cache.get("agents:list") == [5]


def test_stats(cache):
    asyncio.run(_test_stats(cache))


async def _test_stats(cache):
    await cache.set("a", 1)
    await cache.set("b", 2)
    stats = cache.stats()
    assert stats["total_entries"] == 2
    assert stats["active_entries"] == 2


def test_export_import(cache):
    asyncio.run(_test_export_import(cache))


async def _test_export_import(cache):
    await cache.set("export1", {"data": "test"}, ttl_seconds=3600)
    await cache.set("export2", [1, 2, 3], ttl_seconds=3600)

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        export_path = f.name

    count = cache.export_json(export_path)
    assert count == 2

    # Clear and reimport
    await cache.clear()
    assert await cache.get("export1") is None

    imported = cache.import_json(export_path)
    assert imported == 2
    assert await cache.get("export1") == {"data": "test"}
    assert await cache.get("export2") == [1, 2, 3]

    os.unlink(export_path)


def test_cleanup_expired(cache):
    asyncio.run(_test_cleanup(cache))


async def _test_cleanup(cache):
    await cache.set("fresh", "yes", ttl_seconds=3600)
    await cache.set("stale", "no", ttl_seconds=0)
    removed = cache.cleanup_expired()
    assert removed == 1
    assert await cache.get("fresh") == "yes"