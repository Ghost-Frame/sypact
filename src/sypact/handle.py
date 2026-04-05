"""Core abstraction: opaque credential handles that never expose secrets."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class CredentialHandle:
    """Opaque reference to a secret.

    Agents pass these around. The secret is resolved at point of use
    through a SecretBackend, never exposed to the agent or LLM.
    """

    name: str
    backend_tag: str = "default"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"CredentialHandle(name={self.name!r}, backend={self.backend_tag!r})"

    def __str__(self) -> str:
        return f"<sypact:{self.backend_tag}/{self.name}>"

    def __format__(self, format_spec: str) -> str:
        return str(self)
