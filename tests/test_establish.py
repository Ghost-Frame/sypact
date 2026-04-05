"""Tests for end-to-end pact establishment."""

import pytest

from sypact import (
    AgentIdentity,
    AuthenticationFailed,
    Capability,
    EnvBackend,
    NoSharedCapabilities,
    Pact,
    Permission,
    TrustBelowThreshold,
    TrustLedger,
    establish,
)


@pytest.fixture
def backend() -> EnvBackend:
    return EnvBackend(prefix="SYPACT_TEST_EST_")


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


@pytest.fixture
def read_caps() -> list[Capability]:
    return [Capability(name="read_data", permissions=frozenset({Permission.RESOLVE}))]


@pytest.fixture
def write_caps() -> list[Capability]:
    return [Capability(name="write_data", permissions=frozenset({Permission.DELEGATE}))]


class TestHappyPath:
    def test_establish_returns_pact(self, backend, alice, bob, read_caps) -> None:
        alice_id, alice_key = alice
        bob_id, bob_key = bob
        pact = establish(
            initiator=(alice_id, alice_key, read_caps),
            responder=(bob_id, bob_key, read_caps),
            backend=backend,
        )
        assert isinstance(pact, Pact)
        assert pact.initiator.agent_id == "alice"
        assert pact.responder.agent_id == "bob"
        assert len(pact.shared_capabilities) == 1
        assert pact.shared_capabilities[0].name == "read_data"

    def test_establish_with_ledger(self, backend, alice, bob, read_caps) -> None:
        alice_id, alice_key = alice
        bob_id, bob_key = bob
        ledger = TrustLedger()
        pact = establish(
            initiator=(alice_id, alice_key, read_caps),
            responder=(bob_id, bob_key, read_caps),
            backend=backend,
            ledger=ledger,
            trust_threshold=0.5,
        )
        assert pact.trust_scores[0].agent_id == "alice"
        assert pact.trust_scores[1].agent_id == "bob"

    def test_establish_without_ledger_uses_neutral_scores(self, backend, alice, bob, read_caps) -> None:
        alice_id, alice_key = alice
        bob_id, bob_key = bob
        pact = establish(
            initiator=(alice_id, alice_key, read_caps),
            responder=(bob_id, bob_key, read_caps),
            backend=backend,
        )
        assert pact.trust_scores[0].score == 0.5
        assert pact.trust_scores[1].score == 0.5

    def test_pact_is_frozen(self, backend, alice, bob, read_caps) -> None:
        alice_id, alice_key = alice
        bob_id, bob_key = bob
        pact = establish(
            initiator=(alice_id, alice_key, read_caps),
            responder=(bob_id, bob_key, read_caps),
            backend=backend,
        )
        with pytest.raises(AttributeError):
            pact.initiator = alice_id  # type: ignore[misc]


class TestTrustGating:
    def test_initiator_below_threshold_raises(self, backend, alice, bob, read_caps) -> None:
        alice_id, alice_key = alice
        bob_id, bob_key = bob
        ledger = TrustLedger()
        score = ledger.get("alice")
        score.score = 0.2
        ledger.update(score)
        with pytest.raises(TrustBelowThreshold, match="alice"):
            establish(
                initiator=(alice_id, alice_key, read_caps),
                responder=(bob_id, bob_key, read_caps),
                backend=backend,
                ledger=ledger,
                trust_threshold=0.5,
            )

    def test_responder_below_threshold_raises(self, backend, alice, bob, read_caps) -> None:
        alice_id, alice_key = alice
        bob_id, bob_key = bob
        ledger = TrustLedger()
        score = ledger.get("bob")
        score.score = 0.2
        ledger.update(score)
        with pytest.raises(TrustBelowThreshold, match="bob"):
            establish(
                initiator=(alice_id, alice_key, read_caps),
                responder=(bob_id, bob_key, read_caps),
                backend=backend,
                ledger=ledger,
                trust_threshold=0.5,
            )

    def test_exact_threshold_passes(self, backend, alice, bob, read_caps) -> None:
        alice_id, alice_key = alice
        bob_id, bob_key = bob
        ledger = TrustLedger()
        pact = establish(
            initiator=(alice_id, alice_key, read_caps),
            responder=(bob_id, bob_key, read_caps),
            backend=backend,
            ledger=ledger,
            trust_threshold=0.5,
        )
        assert isinstance(pact, Pact)

    def test_neutral_agents_pass_default_threshold(self, backend, alice, bob, read_caps) -> None:
        alice_id, alice_key = alice
        bob_id, bob_key = bob
        ledger = TrustLedger()
        pact = establish(
            initiator=(alice_id, alice_key, read_caps),
            responder=(bob_id, bob_key, read_caps),
            backend=backend,
            ledger=ledger,
        )
        assert isinstance(pact, Pact)


class TestCapabilityNegotiation:
    def test_no_shared_capabilities_raises(self, backend, alice, bob, read_caps, write_caps) -> None:
        alice_id, alice_key = alice
        bob_id, bob_key = bob
        with pytest.raises(NoSharedCapabilities):
            establish(
                initiator=(alice_id, alice_key, read_caps),
                responder=(bob_id, bob_key, write_caps),
                backend=backend,
            )

    def test_permission_mismatch_raises(self, backend, alice, bob) -> None:
        alice_id, alice_key = alice
        bob_id, bob_key = bob
        cap_a = [Capability(name="data", permissions=frozenset({Permission.RESOLVE}))]
        cap_b = [Capability(name="data", permissions=frozenset({Permission.DELEGATE}))]
        with pytest.raises(NoSharedCapabilities):
            establish(
                initiator=(alice_id, alice_key, cap_a),
                responder=(bob_id, bob_key, cap_b),
                backend=backend,
            )

    def test_multiple_shared_capabilities(self, backend, alice, bob) -> None:
        alice_id, alice_key = alice
        bob_id, bob_key = bob
        caps = [
            Capability(name="read", permissions=frozenset({Permission.RESOLVE})),
            Capability(name="write", permissions=frozenset({Permission.DELEGATE})),
        ]
        pact = establish(
            initiator=(alice_id, alice_key, caps),
            responder=(bob_id, bob_key, caps),
            backend=backend,
        )
        assert len(pact.shared_capabilities) == 2


class TestTrustRecording:
    def test_record_success_updates_both(self, backend, alice, bob, read_caps) -> None:
        alice_id, alice_key = alice
        bob_id, bob_key = bob
        ledger = TrustLedger()
        pact = establish(
            initiator=(alice_id, alice_key, read_caps),
            responder=(bob_id, bob_key, read_caps),
            backend=backend,
            ledger=ledger,
        )
        pact.record_success(ledger)
        assert ledger.get("alice").score > 0.5
        assert ledger.get("bob").score > 0.5

    def test_record_failure_updates_both(self, backend, alice, bob, read_caps) -> None:
        alice_id, alice_key = alice
        bob_id, bob_key = bob
        ledger = TrustLedger()
        pact = establish(
            initiator=(alice_id, alice_key, read_caps),
            responder=(bob_id, bob_key, read_caps),
            backend=backend,
            ledger=ledger,
        )
        pact.record_failure(ledger)
        assert ledger.get("alice").score < 0.5
        assert ledger.get("bob").score < 0.5


class TestSelfPact:
    def test_same_agent_both_sides(self, backend) -> None:
        identity, key = AgentIdentity.generate(
            agent_id="solo", owner_id="zan", backend=backend,
        )
        caps = [Capability(name="self_op", permissions=frozenset({Permission.RESOLVE}))]
        pact = establish(
            initiator=(identity, key, caps),
            responder=(identity, key, caps),
            backend=backend,
        )
        assert pact.initiator.agent_id == "solo"
        assert pact.responder.agent_id == "solo"
        assert len(pact.shared_capabilities) == 1


class TestRepr:
    def test_pact_repr(self, backend, alice, bob, read_caps) -> None:
        alice_id, alice_key = alice
        bob_id, bob_key = bob
        pact = establish(
            initiator=(alice_id, alice_key, read_caps),
            responder=(bob_id, bob_key, read_caps),
            backend=backend,
        )
        r = repr(pact)
        assert "alice" in r
        assert "bob" in r
        assert "read_data" in r
