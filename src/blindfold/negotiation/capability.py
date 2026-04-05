"""Layer 3: Capability negotiation -- agents declare and negotiate capabilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Permission(Enum):
    """Permissions that can be granted through capability negotiation."""

    RESOLVE = "resolve"
    DELEGATE = "delegate"
    REVOKE = "revoke"


@dataclass(frozen=True, slots=True)
class Capability:
    """A single capability an agent can offer or request."""

    name: str
    permissions: frozenset[Permission]
    granted_by: str = ""
    expires_at: datetime | None = None


class CapabilitySet:
    """A set of capabilities for negotiation between agents.

    Agents exchange capability sets after mutual auth, so both sides
    know who they're talking to before revealing what they can do.
    """

    def offers(self) -> list[Capability]:
        """List capabilities this agent offers."""
        raise NotImplementedError("Layer 3 not yet implemented")

    def negotiate(self, other: CapabilitySet) -> list[Capability]:
        """Negotiate capabilities with another agent's set."""
        raise NotImplementedError("Layer 3 not yet implemented")
