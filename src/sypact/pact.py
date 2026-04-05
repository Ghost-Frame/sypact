"""The Pact: a verified, authenticated, trust-gated agreement between two agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from sypact.identity.agent import AgentIdentity
from sypact.negotiation.capability import Capability
from sypact.trust.scoring import TrustLedger, TrustScore


@dataclass(frozen=True, slots=True)
class Pact:
    """A verified agreement between two agents.

    Immutable proof that both agents authenticated, negotiated capabilities,
    and passed trust checks. Created only by establish().
    """

    initiator: AgentIdentity
    responder: AgentIdentity
    shared_capabilities: tuple[Capability, ...]
    trust_scores: tuple[TrustScore, TrustScore]
    established_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def record_success(self, ledger: TrustLedger) -> None:
        """Record a successful interaction for both agents."""
        for score in self.trust_scores:
            score.record_success()
            ledger.update(score)

    def record_failure(self, ledger: TrustLedger) -> None:
        """Record a failed interaction for both agents."""
        for score in self.trust_scores:
            score.record_failure()
            ledger.update(score)

    def __repr__(self) -> str:
        caps = [c.name for c in self.shared_capabilities]
        return (
            f"Pact({self.initiator.agent_id!r} <-> {self.responder.agent_id!r}, "
            f"capabilities={caps})"
        )
