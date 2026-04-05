"""Layer 2: Mutual authentication -- challenge-response between agents."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

from blindfold.backends.base import SecretBackend
from blindfold.handle import CredentialHandle
from blindfold.identity.agent import AgentIdentity


@dataclass(frozen=True, slots=True)
class Challenge:
    nonce: bytes
    issuer_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class ChallengeResponse:
    nonce: bytes
    responder_id: str
    signature: bytes


class MutualAuth:
    def create_challenge(self, issuer_id: str) -> Challenge:
        return Challenge(nonce=os.urandom(32), issuer_id=issuer_id)

    def respond(self, challenge: Challenge, responder_identity: AgentIdentity, private_key_handle: CredentialHandle, backend: SecretBackend) -> ChallengeResponse:
        signature = responder_identity.sign(challenge.nonce, private_key_handle=private_key_handle, backend=backend)
        return ChallengeResponse(nonce=challenge.nonce, responder_id=responder_identity.agent_id, signature=signature)

    def verify_response(self, challenge: Challenge, response: ChallengeResponse, responder_identity: AgentIdentity) -> bool:
        if challenge.nonce != response.nonce:
            return False
        return responder_identity.verify(challenge.nonce, response.signature)
