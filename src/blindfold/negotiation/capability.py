"""Layer 3: Capability negotiation -- agents declare and negotiate capabilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class Permission(Enum):
    RESOLVE = "resolve"
    DELEGATE = "delegate"
    REVOKE = "revoke"


@dataclass(frozen=True, slots=True)
class Capability:
    name: str
    permissions: frozenset[Permission]
    granted_by: str = ""
    expires_at: datetime | None = None

    def is_valid(self) -> bool:
        if self.expires_at is None:
            return True
        return datetime.now(timezone.utc) < self.expires_at


class CapabilitySet:
    def __init__(self, capabilities: list[Capability], owner_id: str) -> None:
        self._capabilities = capabilities
        self._owner_id = owner_id

    @property
    def owner_id(self) -> str:
        return self._owner_id

    def offers(self) -> list[Capability]:
        return [c for c in self._capabilities if c.is_valid()]

    def negotiate(self, other: CapabilitySet) -> list[Capability]:
        our_offers = {c.name: c for c in self.offers()}
        their_offers = {c.name: c for c in other.offers()}
        shared_names = set(our_offers) & set(their_offers)
        result: list[Capability] = []
        for name in sorted(shared_names):
            ours = our_offers[name]
            theirs = their_offers[name]
            shared_perms = ours.permissions & theirs.permissions
            if shared_perms:
                result.append(Capability(
                    name=name,
                    permissions=shared_perms,
                    granted_by=f"{self._owner_id}<>{other._owner_id}",
                ))
        return result
