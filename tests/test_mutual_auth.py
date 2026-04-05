"""Tests for Layer 2: Mutual authentication via challenge-response."""

import pytest

from sypact import EnvBackend
from sypact.identity import AgentIdentity
from sypact.auth import MutualAuth, Challenge, ChallengeResponse


@pytest.fixture
def backend() -> EnvBackend:
    return EnvBackend(prefix="SYPACT_TEST_AUTH_")


@pytest.fixture
def alice(backend: EnvBackend) -> tuple[AgentIdentity, ...]:
    identity, handle = AgentIdentity.generate(
        agent_id="alice", owner_id="zan", backend=backend,
    )
    return identity, handle


@pytest.fixture
def bob(backend: EnvBackend) -> tuple[AgentIdentity, ...]:
    identity, handle = AgentIdentity.generate(
        agent_id="bob", owner_id="zan", backend=backend,
    )
    return identity, handle


class TestChallengeCreation:
    def test_create_challenge_has_nonce(self) -> None:
        auth = MutualAuth()
        challenge = auth.create_challenge(issuer_id="alice")
        assert isinstance(challenge, Challenge)
        assert isinstance(challenge.nonce, bytes)
        assert len(challenge.nonce) == 32
        assert challenge.issuer_id == "alice"

    def test_challenges_have_unique_nonces(self) -> None:
        auth = MutualAuth()
        c1 = auth.create_challenge(issuer_id="alice")
        c2 = auth.create_challenge(issuer_id="alice")
        assert c1.nonce != c2.nonce


class TestChallengeResponse:
    def test_respond_produces_signed_response(self, backend, bob) -> None:
        bob_identity, bob_handle = bob
        auth = MutualAuth()
        challenge = auth.create_challenge(issuer_id="alice")
        response = auth.respond(challenge=challenge, responder_identity=bob_identity, private_key_handle=bob_handle, backend=backend)
        assert isinstance(response, ChallengeResponse)
        assert response.nonce == challenge.nonce
        assert response.responder_id == "bob"
        assert isinstance(response.signature, bytes)

    def test_verify_valid_response(self, backend, bob) -> None:
        bob_identity, bob_handle = bob
        auth = MutualAuth()
        challenge = auth.create_challenge(issuer_id="alice")
        response = auth.respond(challenge=challenge, responder_identity=bob_identity, private_key_handle=bob_handle, backend=backend)
        assert auth.verify_response(challenge=challenge, response=response, responder_identity=bob_identity) is True

    def test_verify_rejects_wrong_nonce(self, backend, bob) -> None:
        bob_identity, bob_handle = bob
        auth = MutualAuth()
        challenge = auth.create_challenge(issuer_id="alice")
        response = auth.respond(challenge=challenge, responder_identity=bob_identity, private_key_handle=bob_handle, backend=backend)
        fake_challenge = auth.create_challenge(issuer_id="alice")
        assert auth.verify_response(challenge=fake_challenge, response=response, responder_identity=bob_identity) is False

    def test_verify_rejects_wrong_identity(self, backend, alice, bob) -> None:
        alice_identity, _ = alice
        bob_identity, bob_handle = bob
        auth = MutualAuth()
        challenge = auth.create_challenge(issuer_id="alice")
        response = auth.respond(challenge=challenge, responder_identity=bob_identity, private_key_handle=bob_handle, backend=backend)
        assert auth.verify_response(challenge=challenge, response=response, responder_identity=alice_identity) is False


class TestFullHandshake:
    def test_bidirectional_handshake(self, backend, alice, bob) -> None:
        alice_identity, alice_handle = alice
        bob_identity, bob_handle = bob
        auth = MutualAuth()

        challenge_for_bob = auth.create_challenge(issuer_id="alice")
        bob_response = auth.respond(challenge=challenge_for_bob, responder_identity=bob_identity, private_key_handle=bob_handle, backend=backend)
        assert auth.verify_response(challenge=challenge_for_bob, response=bob_response, responder_identity=bob_identity) is True

        challenge_for_alice = auth.create_challenge(issuer_id="bob")
        alice_response = auth.respond(challenge=challenge_for_alice, responder_identity=alice_identity, private_key_handle=alice_handle, backend=backend)
        assert auth.verify_response(challenge=challenge_for_alice, response=alice_response, responder_identity=alice_identity) is True
