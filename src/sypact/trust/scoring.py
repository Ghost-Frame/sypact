"""Layer 4: Trust scoring -- behavioral reputation that builds over time."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

_SUCCESS_WEIGHT = 0.1
_FAILURE_WEIGHT = 0.15
_DECAY_RATE = 0.02
_NEUTRAL = 0.5


@dataclass(slots=True)
class TrustScore:
    agent_id: str
    score: float = _NEUTRAL
    interactions: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def _clamp(self) -> None:
        self.score = max(0.0, min(1.0, self.score))

    def record_success(self) -> None:
        headroom = 1.0 - self.score
        self.score += _SUCCESS_WEIGHT * headroom
        self.interactions += 1
        self.last_updated = datetime.now(timezone.utc)
        self._clamp()

    def record_failure(self) -> None:
        self.score -= _FAILURE_WEIGHT * self.score
        self.interactions += 1
        self.last_updated = datetime.now(timezone.utc)
        self._clamp()

    def decay(self) -> None:
        now = datetime.now(timezone.utc)
        days_elapsed = (now - self.last_updated).total_seconds() / 86400.0
        if days_elapsed < 0.01:
            return
        distance = self.score - _NEUTRAL
        self.score -= distance * _DECAY_RATE * days_elapsed
        self.last_updated = now
        self._clamp()

    def meets_threshold(self, threshold: float) -> bool:
        return self.score >= threshold


class TrustLedger:
    def __init__(self) -> None:
        self._scores: dict[str, TrustScore] = {}

    def get(self, agent_id: str) -> TrustScore:
        if agent_id not in self._scores:
            self._scores[agent_id] = TrustScore(agent_id=agent_id)
        return self._scores[agent_id]

    def update(self, score: TrustScore) -> None:
        self._scores[score.agent_id] = score
