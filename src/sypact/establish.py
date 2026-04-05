"""End-to-end pact establishment -- orchestrates all four layers."""

from __future__ import annotations

from sypact.auth.mutual import MutualAuth
from sypact.backends.base import SecretBackend
from sypact.exceptions import (
    AuthenticationFailed,
    NoSharedCapabilities,
    TrustBelowThreshold,
)
from sypact.handle import CredentialHandle
from sypact.identity.agent import AgentIdentity
from sypact.negotiation.capability import Capability, CapabilitySet
from sypact.pact import Pact
from sypact.trust.scoring import TrustLedger, TrustScore


def establish(
    initiator: tuple[AgentIdentity, CredentialHandle, list[Capability]],
    responder: tuple[AgentIdentity, CredentialHandle, list[Capability]],
    backend: SecretBackend,
    ledger: TrustLedger | None = None,
    trust_threshold: float = 0.5,
) -> Pact:
    """Establish a verified pact between two agents.

    Runs all four layers in sequence:
    1. Trust check (if ledger provided)
    2. Mutual authentication (bidirectional challenge-response)
    3. Capability negotiation (set intersection)
    4. Return frozen Pact

    Raises:
        TrustBelowThreshold: if either agent's trust score < threshold
        AuthenticationFailed: if challenge-response fails in either direction
        NoSharedCapabilities: if agents have no overlapping capabilities
    """
    init_identity, init_key, init_caps = initiator
    resp_identity, resp_key, resp_caps = responder

    # Layer 4: Trust gating
    if ledger is not None:
        init_trust = ledger.get(init_identity.agent_id)
        resp_trust = ledger.get(resp_identity.agent_id)

        if not init_trust.meets_threshold(trust_threshold):
            raise TrustBelowThreshold(
                f"Initiator {init_identity.agent_id!r} trust {init_trust.score:.3f} "
                f"< threshold {trust_threshold}"
            )
        if not resp_trust.meets_threshold(trust_threshold):
            raise TrustBelowThreshold(
                f"Responder {resp_identity.agent_id!r} trust {resp_trust.score:.3f} "
                f"< threshold {trust_threshold}"
            )
    else:
        init_trust = TrustScore(agent_id=init_identity.agent_id)
        resp_trust = TrustScore(agent_id=resp_identity.agent_id)

    # Layer 2: Mutual authentication
    auth = MutualAuth()

    # Initiator challenges responder
    challenge_for_resp = auth.create_challenge(issuer_id=init_identity.agent_id)
    resp_response = auth.respond(
        challenge=challenge_for_resp,
        responder_identity=resp_identity,
        private_key_handle=resp_key,
        backend=backend,
    )
    if not auth.verify_response(
        challenge=challenge_for_resp,
        response=resp_response,
        responder_identity=resp_identity,
    ):
        raise AuthenticationFailed(
            f"Responder {resp_identity.agent_id!r} failed challenge from "
            f"{init_identity.agent_id!r}"
        )

    # Responder challenges initiator
    challenge_for_init = auth.create_challenge(issuer_id=resp_identity.agent_id)
    init_response = auth.respond(
        challenge=challenge_for_init,
        responder_identity=init_identity,
        private_key_handle=init_key,
        backend=backend,
    )
    if not auth.verify_response(
        challenge=challenge_for_init,
        response=init_response,
        responder_identity=init_identity,
    ):
        raise AuthenticationFailed(
            f"Initiator {init_identity.agent_id!r} failed challenge from "
            f"{resp_identity.agent_id!r}"
        )

    # Layer 3: Capability negotiation
    init_capset = CapabilitySet(capabilities=init_caps, owner_id=init_identity.agent_id)
    resp_capset = CapabilitySet(capabilities=resp_caps, owner_id=resp_identity.agent_id)
    shared = init_capset.negotiate(resp_capset)

    if not shared:
        raise NoSharedCapabilities(
            f"No shared capabilities between {init_identity.agent_id!r} "
            f"and {resp_identity.agent_id!r}"
        )

    return Pact(
        initiator=init_identity,
        responder=resp_identity,
        shared_capabilities=tuple(shared),
        trust_scores=(init_trust, resp_trust),
    )
