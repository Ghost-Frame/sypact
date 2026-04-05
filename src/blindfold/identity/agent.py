"""Layer 1: Agent identity -- provable identity tied to signing keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class AgentIdentity:
    """An agent's provable identity.

    Trust is human-delegated by default -- the owner signs agent
    certificates using their own key material.
    """

    agent_id: str
    public_key: bytes
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def sign(self, data: bytes) -> bytes:
        """Sign data with this agent's private key."""
        raise NotImplementedError("Layer 1 not yet implemented")

    def verify(self, data: bytes, signature: bytes) -> bool:
        """Verify a signature against this agent's public key."""
        raise NotImplementedError("Layer 1 not yet implemented")

    @classmethod
    def generate(cls) -> AgentIdentity:
        """Generate a new agent identity with a fresh keypair."""
        raise NotImplementedError("Layer 1 not yet implemented")
