"""Context strategy — progressive response to context and rate limit pressure.

Evaluates each agent's context usage and rate limit position, then
produces an action the orchestrator writes to the agent's pre-embed.
Agents see the action structurally — they don't poll for it.

Design: wiki/domains/architecture/context-strategy-design.md

Thresholds:
  Context: 70% AWARE → 80% PREPARE → 90% EXTRACT → 95% COMPACT
  Rate limit: 70% INFORM → 85% CONSERVE → 90% CRITICAL → 95% STOP

PO directive: "strategical in context switching and mindful of the
current context size relative to the next forced compact"
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class ContextAction(str, Enum):
    """Progressive action based on context/rate limit pressure."""
    NORMAL = "normal"       # < 70% — work freely
    AWARE = "aware"         # 70% — informed, no change needed
    PREPARE = "prepare"     # 80% — save working state to artifacts
    EXTRACT = "extract"     # 95% used (5% remaining) — dump NOW, compact imminent


class RateLimitAction(str, Enum):
    """Progressive action based on rate limit pressure.

    From PO (CW doc §7):
      85% = start preparing (controlled transition)
      90% = actively managing (force compact heavy contexts)
    """
    NORMAL = "normal"       # < 85%
    CONSERVE = "conserve"   # 85% — start preparing, controlled transition
    CRITICAL = "critical"   # 90% — actively managing, compact heavy contexts


@dataclass
class ContextEvaluation:
    """Result of evaluating one agent's context and rate limit position."""
    agent_name: str
    context_pct: float
    rate_limit_pct: float
    context_action: ContextAction
    rate_limit_action: RateLimitAction
    message: str  # Human-readable for pre-embed injection

    @property
    def needs_attention(self) -> bool:
        return (self.context_action != ContextAction.NORMAL
                or self.rate_limit_action != RateLimitAction.NORMAL)

    @property
    def should_block_dispatch(self) -> bool:
        return self.rate_limit_action == RateLimitAction.CRITICAL

    @property
    def should_compact(self) -> bool:
        return self.context_action == ContextAction.EXTRACT


class ContextStrategy:
    """Evaluate and respond to context pressure per agent.

    Called by orchestrator Step 0 (context refresh) every 30s cycle.
    Results written to agent pre-embed so agents see their position.
    """

    # Context thresholds — from PO requirements (CW doc §1, §6)
    # "7% remaining" = 93% used = prepare (extract artifacts)
    # "5% remaining" = 95% used = active management (compact before forced)
    CONTEXT_PREPARE = 93.0    # 7% remaining — prepare artifacts, save state
    CONTEXT_EXTRACT = 95.0    # 5% remaining — dump everything NOW, compact imminent

    # Rate limit thresholds — from PO requirements (CW doc §7)
    # "85% rate limit used = start preparing (like 7% context remaining)"
    # "90% rate limit used = actively managing (like 5% context remaining)"
    RATE_PREPARE = 85.0       # Start preparing — controlled transition
    RATE_MANAGE = 90.0        # Actively managing — force compact heavy contexts

    def __init__(self):
        # Track compaction times to stagger across agents
        self._last_compact: dict[str, datetime] = {}
        # Minimum seconds between compactions fleet-wide
        self._compact_stagger_seconds = 120

    def evaluate(
        self,
        agent_name: str,
        context_pct: float = 0.0,
        rate_limit_pct: float = 0.0,
    ) -> ContextEvaluation:
        """Evaluate context and rate limit position for one agent.

        Args:
            agent_name: Agent being evaluated.
            context_pct: Context window usage (0-100). 0 if unknown.
            rate_limit_pct: Rate limit usage (0-100). 0 if unknown.

        Returns:
            ContextEvaluation with actions and message for pre-embed.
        """
        ctx_action = self._evaluate_context(context_pct)
        rate_action = self._evaluate_rate_limit(rate_limit_pct)
        message = self._build_message(context_pct, rate_limit_pct, ctx_action, rate_action)

        return ContextEvaluation(
            agent_name=agent_name,
            context_pct=context_pct,
            rate_limit_pct=rate_limit_pct,
            context_action=ctx_action,
            rate_limit_action=rate_action,
            message=message,
        )

    def should_dispatch(self, rate_limit_pct: float) -> bool:
        """Can the fleet dispatch new work at this rate limit level?"""
        return rate_limit_pct < self.RATE_MANAGE

    def should_compact_agent(self, agent_name: str, context_pct: float) -> bool:
        """Should this agent be proactively compacted?

        Checks context threshold AND stagger (don't compact all agents at once).
        """
        if context_pct < self.CONTEXT_EXTRACT:
            return False

        # Stagger check — don't compact if another agent compacted recently
        now = datetime.now()
        for name, last_time in self._last_compact.items():
            if name != agent_name:
                elapsed = (now - last_time).total_seconds()
                if elapsed < self._compact_stagger_seconds:
                    logger.debug(
                        "Stagger: skip compact for %s — %s compacted %ds ago",
                        agent_name, name, elapsed,
                    )
                    return False

        return True

    def record_compaction(self, agent_name: str) -> None:
        """Record that an agent was compacted (for stagger tracking)."""
        self._last_compact[agent_name] = datetime.now()

    def _evaluate_context(self, pct: float) -> ContextAction:
        if pct <= 0:
            return ContextAction.NORMAL  # No data
        if pct >= self.CONTEXT_EXTRACT:
            return ContextAction.EXTRACT  # 5% remaining — dump NOW
        if pct >= self.CONTEXT_PREPARE:
            return ContextAction.PREPARE  # 7% remaining — save state to artifacts
        return ContextAction.NORMAL

    def _evaluate_rate_limit(self, pct: float) -> RateLimitAction:
        if pct <= 0:
            return RateLimitAction.NORMAL  # No data
        if pct >= self.RATE_MANAGE:
            return RateLimitAction.CRITICAL  # 90% — actively managing, compact heavy contexts
        if pct >= self.RATE_PREPARE:
            return RateLimitAction.CONSERVE  # 85% — start preparing, controlled transition
        return RateLimitAction.NORMAL

    def _build_message(
        self,
        context_pct: float,
        rate_limit_pct: float,
        ctx_action: ContextAction,
        rate_action: RateLimitAction,
    ) -> str:
        """Build human-readable message for agent pre-embed."""
        parts = []

        if ctx_action == ContextAction.NORMAL and rate_action == RateLimitAction.NORMAL:
            return ""  # No message needed

        if ctx_action == ContextAction.PREPARE:
            parts.append(
                f"Context: {context_pct:.0f}% used (7% remaining). "
                "PREPARE — save working state to artifacts "
                "(fleet_task_progress, fleet_artifact_update, fleet_commit)."
            )
        elif ctx_action == ContextAction.EXTRACT:
            parts.append(
                f"Context: {context_pct:.0f}% used (5% remaining). "
                "EXTRACT — dump all working state to artifacts NOW. "
                "Commit uncommitted work. Post progress. Compaction imminent."
            )

        if rate_action == RateLimitAction.CONSERVE:
            parts.append(
                f"Rate limit: {rate_limit_pct:.0f}%. "
                "PREPARE — start controlled transition. "
                "Don't dispatch 1M context tasks. Compact heavy sessions."
            )
        elif rate_action == RateLimitAction.CRITICAL:
            parts.append(
                f"Rate limit: {rate_limit_pct:.0f}%. "
                "MANAGE — actively managing. Force compact contexts over 40-80K. "
                "No new dispatches until rollover."
            )

        return "\n".join(parts)
