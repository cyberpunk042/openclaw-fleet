"""Tests for deferred challenge queue (M-IV07)."""

import time
from pathlib import Path

from fleet.core.challenge_deferred import (
    DeferredChallenge,
    DeferredChallengeQueue,
    compute_drain_batch_size,
)


# ─── DeferredChallenge ───────────────────────────────────────────


def test_deferred_challenge_creation():
    dc = DeferredChallenge(
        task_id="t1", task_type="task",
        story_points=3, confidence_tier="standard",
    )
    assert dc.task_id == "t1"
    assert dc.deferred_at > 0
    assert dc.priority == 3  # SP-based


def test_priority_trainee_boost():
    dc = DeferredChallenge(
        task_id="t1", task_type="task",
        story_points=3, confidence_tier="trainee",
    )
    assert dc.priority == 8  # 3 SP + 5 trainee


def test_priority_security_boost():
    dc = DeferredChallenge(
        task_id="t1", task_type="blocker",
        story_points=3, confidence_tier="standard",
    )
    assert dc.priority == 13  # 3 SP + 10 security


def test_priority_epic_boost():
    dc = DeferredChallenge(
        task_id="t1", task_type="epic",
        story_points=5, confidence_tier="standard",
    )
    assert dc.priority == 8  # 5 SP + 3 epic


def test_to_dict():
    dc = DeferredChallenge(
        task_id="t1", task_type="task",
        story_points=3, confidence_tier="standard",
        reason="deferred",
    )
    d = dc.to_dict()
    assert d["task_id"] == "t1"
    assert d["reason"] == "deferred"


def test_from_dict():
    d = {
        "task_id": "t2", "task_type": "bug",
        "story_points": 5, "confidence_tier": "trainee",
        "reason": "deferred", "priority": 10,
    }
    dc = DeferredChallenge.from_dict(d)
    assert dc.task_id == "t2"
    assert dc.priority == 10


# ─── DeferredChallengeQueue ──────────────────────────────────────


def test_queue_empty():
    q = DeferredChallengeQueue()
    assert q.is_empty
    assert q.size == 0


def test_enqueue():
    q = DeferredChallengeQueue()
    dc = DeferredChallenge("t1", "task", 3, "standard")
    assert q.enqueue(dc)
    assert q.size == 1


def test_enqueue_duplicate_rejected():
    q = DeferredChallengeQueue()
    dc1 = DeferredChallenge("t1", "task", 3, "standard")
    dc2 = DeferredChallenge("t1", "task", 5, "trainee")
    assert q.enqueue(dc1)
    assert not q.enqueue(dc2)
    assert q.size == 1


def test_enqueue_full_rejected():
    q = DeferredChallengeQueue(max_size=2)
    q.enqueue(DeferredChallenge("t1", "task", 1, "standard"))
    q.enqueue(DeferredChallenge("t2", "task", 2, "standard"))
    assert not q.enqueue(DeferredChallenge("t3", "task", 3, "standard"))


def test_dequeue_fifo():
    q = DeferredChallengeQueue()
    dc1 = DeferredChallenge("t1", "task", 3, "standard", deferred_at=100.0)
    dc2 = DeferredChallenge("t2", "task", 3, "standard", deferred_at=200.0)
    q.enqueue(dc1)
    q.enqueue(dc2)
    result = q.dequeue(1)
    assert len(result) == 1
    assert result[0].task_id == "t1"  # Oldest first


def test_dequeue_priority():
    q = DeferredChallengeQueue()
    dc1 = DeferredChallenge("t1", "task", 1, "standard", deferred_at=100.0)
    dc2 = DeferredChallenge("t2", "blocker", 3, "standard", deferred_at=200.0)
    q.enqueue(dc1)
    q.enqueue(dc2)
    result = q.dequeue(1)
    assert result[0].task_id == "t2"  # Higher priority first


def test_dequeue_multiple():
    q = DeferredChallengeQueue()
    for i in range(5):
        q.enqueue(DeferredChallenge(f"t{i}", "task", 3, "standard", deferred_at=float(i)))
    result = q.dequeue(3)
    assert len(result) == 3
    assert q.size == 2


def test_dequeue_empty():
    q = DeferredChallengeQueue()
    assert q.dequeue(1) == []


def test_peek():
    q = DeferredChallengeQueue()
    dc = DeferredChallenge("t1", "task", 3, "standard")
    q.enqueue(dc)
    peeked = q.peek(1)
    assert len(peeked) == 1
    assert q.size == 1  # Not removed


def test_remove():
    q = DeferredChallengeQueue()
    q.enqueue(DeferredChallenge("t1", "task", 3, "standard"))
    q.enqueue(DeferredChallenge("t2", "task", 3, "standard"))
    assert q.remove("t1")
    assert q.size == 1
    assert not q.remove("t1")  # Already removed


# ─── Queue Status ────────────────────────────────────────────────


def test_status_empty():
    q = DeferredChallengeQueue()
    s = q.status()
    assert s.total == 0
    assert s.alert_level == "ok"


def test_status_by_tier():
    q = DeferredChallengeQueue()
    q.enqueue(DeferredChallenge("t1", "task", 3, "trainee"))
    q.enqueue(DeferredChallenge("t2", "task", 3, "trainee"))
    q.enqueue(DeferredChallenge("t3", "task", 3, "standard"))
    s = q.status()
    assert s.by_tier["trainee"] == 2
    assert s.by_tier["standard"] == 1


def test_status_warning_size():
    q = DeferredChallengeQueue()
    for i in range(10):
        q.enqueue(DeferredChallenge(f"t{i}", "task", 1, "standard"))
    s = q.status()
    assert s.alert_level == "warning"


def test_status_critical_size():
    q = DeferredChallengeQueue()
    for i in range(25):
        q.enqueue(DeferredChallenge(f"t{i}", "task", 1, "standard"))
    s = q.status()
    assert s.alert_level == "critical"


def test_status_warning_age():
    q = DeferredChallengeQueue()
    old_time = time.time() - (25 * 3600)  # 25 hours ago
    q.enqueue(DeferredChallenge("t1", "task", 1, "standard", deferred_at=old_time))
    s = q.status()
    assert s.alert_level == "warning"
    assert "old" in s.alert_reason


def test_status_critical_age():
    q = DeferredChallengeQueue()
    old_time = time.time() - (73 * 3600)  # 73 hours ago
    q.enqueue(DeferredChallenge("t1", "task", 1, "standard", deferred_at=old_time))
    s = q.status()
    assert s.alert_level == "critical"


def test_status_to_dict():
    q = DeferredChallengeQueue()
    s = q.status()
    d = s.to_dict()
    assert "total" in d
    assert "alert_level" in d


# ─── Serialization ───────────────────────────────────────────────


def test_to_list_and_load():
    q = DeferredChallengeQueue()
    q.enqueue(DeferredChallenge("t1", "task", 3, "standard"))
    q.enqueue(DeferredChallenge("t2", "bug", 5, "trainee"))

    data = q.to_list()
    q2 = DeferredChallengeQueue()
    q2.load_from_list(data)
    assert q2.size == 2


def test_save_and_load(tmp_path: Path):
    q = DeferredChallengeQueue()
    q.enqueue(DeferredChallenge("t1", "task", 3, "standard"))
    q.enqueue(DeferredChallenge("t2", "bug", 5, "trainee"))

    path = tmp_path / "state" / "deferred.json"
    q.save(path)
    assert path.exists()

    q2 = DeferredChallengeQueue()
    q2.load(path)
    assert q2.size == 2


def test_load_nonexistent(tmp_path: Path):
    q = DeferredChallengeQueue()
    q.load(tmp_path / "does_not_exist.json")
    assert q.is_empty


# ─── Drain Logic ─────────────────────────────────────────────────


def test_drain_default():
    assert compute_drain_batch_size(10) == 3


def test_drain_custom_max():
    assert compute_drain_batch_size(10, max_per_cycle=5) == 5


def test_drain_empty_queue():
    assert compute_drain_batch_size(0) == 0


def test_drain_small_queue():
    assert compute_drain_batch_size(2) == 2
