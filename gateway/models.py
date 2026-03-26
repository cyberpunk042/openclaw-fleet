"""Domain models for the OCF Gateway."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import uuid4


@dataclass
class Claim:
    source: str
    content: str
    timestamp: datetime
    confidence_level: float
    linked_actors: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid4().hex)
