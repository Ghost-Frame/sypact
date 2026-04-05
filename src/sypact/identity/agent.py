"""Layer 1: Agent identity -- provable identity tied to Ed25519 signing keys."""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from datetime import datetime, timezone

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)
from cryptography.exceptions import InvalidSignature

from sypact.backends.base import SecretBackend
from sypact.handle import CredentialHandle


@dataclass(frozen=True, slots=True)
class AgentIdentity:
    """An agent's provable identity backed by Ed25519.

    The public key lives here. The private key is stored in a
    SecretBackend and resolved at sign-time via CredentialHandle.
    """

    agent_id: str
    owner_id: str
    public_key: bytes
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def generate(
        cls,
        agent_id: str,
        owner_id: str,
        backend: SecretBackend,
    ) -> tuple[AgentIdentity, CredentialHandle]:
        private_key = Ed25519PrivateKey.generate()
        public_bytes = private_key.public_key().public_bytes(
            Encoding.Raw, PublicFormat.Raw,
        )
        private_bytes = private_key.private_bytes(
            Encoding.Raw, PrivateFormat.Raw, NoEncryption(),
        )
        handle = backend.store(
            f"{agent_id}.ed25519.private",
            base64.b64encode(private_bytes).decode(),
            agent_id=agent_id,
            key_type="ed25519_private",
        )
        identity = cls(
            agent_id=agent_id,
            owner_id=owner_id,
            public_key=public_bytes,
        )
        return identity, handle

    def sign(
        self,
        data: bytes,
        private_key_handle: CredentialHandle,
        backend: SecretBackend,
    ) -> bytes:
        raw_b64 = backend.resolve(private_key_handle)
        raw_bytes = base64.b64decode(raw_b64)
        private_key = Ed25519PrivateKey.from_private_bytes(raw_bytes)
        return private_key.sign(data)

    def verify(self, data: bytes, signature: bytes) -> bool:
        public_key = Ed25519PublicKey.from_public_bytes(self.public_key)
        try:
            public_key.verify(signature, data)
            return True
        except InvalidSignature:
            return False

    def __repr__(self) -> str:
        return (
            f"AgentIdentity(agent_id={self.agent_id!r}, "
            f"owner_id={self.owner_id!r})"
        )
