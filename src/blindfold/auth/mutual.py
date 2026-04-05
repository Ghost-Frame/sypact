"""Layer 2: Mutual authentication -- challenge-response between agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class Challenge:
    """A challenge issued during mutual authentication."""

    nonce: bytes
    issuer_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class ChallengeResponse:
    """A response to an authentication challenge."""

    nonce: bytes
    responder_id: str
    signature: bytes


class MutualAuth:
    """Mutual authentication protocol between two agents.

    Both sides prove identity before the channel opens.
    """

    def create_challenge(self, issuer_id: str) -> Challenge:
        """Create a new authentication challenge."""
        raise NotImplementedError("Layer 2 not yet implemented")

    def respond(self, challenge: Challenge, responder_id: str) -> ChallengeResponse:
        """Respond to an authentication challenge."""
        raise NotImplementedError("Layer 2 not yet implemented")

    def verify_response(self, challenge: Challenge, response: ChallengeResponse) -> bool:
        """Verify a challenge response."""
        raise NotImplementedError("Layer 2 not yet implemented")
