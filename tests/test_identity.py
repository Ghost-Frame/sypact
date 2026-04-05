"""Tests for Layer 1: Agent identity with Ed25519 keypairs."""

from sypact import CredentialHandle, EnvBackend
from sypact.identity import AgentIdentity


class TestGenerate:
    def test_generate_returns_identity_and_handle(self) -> None:
        backend = EnvBackend(prefix="SYPACT_TEST_")
        identity, private_key_handle = AgentIdentity.generate(
            agent_id="agent-001", owner_id="zan", backend=backend,
        )
        assert identity.agent_id == "agent-001"
        assert identity.owner_id == "zan"
        assert isinstance(identity.public_key, bytes)
        assert len(identity.public_key) == 32
        assert isinstance(private_key_handle, CredentialHandle)
        backend.delete(private_key_handle)

    def test_private_key_not_on_identity(self) -> None:
        backend = EnvBackend(prefix="SYPACT_TEST_")
        identity, handle = AgentIdentity.generate(
            agent_id="agent-002", owner_id="zan", backend=backend,
        )
        assert not hasattr(identity, "private_key")
        r = repr(identity)
        assert "private" not in r.lower()
        backend.delete(handle)


class TestSignAndVerify:
    def test_sign_and_verify_roundtrip(self) -> None:
        backend = EnvBackend(prefix="SYPACT_TEST_")
        identity, handle = AgentIdentity.generate(
            agent_id="agent-003", owner_id="zan", backend=backend,
        )
        message = b"hello from agent-003"
        signature = identity.sign(message, private_key_handle=handle, backend=backend)
        assert isinstance(signature, bytes)
        assert identity.verify(message, signature) is True
        backend.delete(handle)

    def test_verify_rejects_tampered_message(self) -> None:
        backend = EnvBackend(prefix="SYPACT_TEST_")
        identity, handle = AgentIdentity.generate(
            agent_id="agent-004", owner_id="zan", backend=backend,
        )
        signature = identity.sign(b"original", private_key_handle=handle, backend=backend)
        assert identity.verify(b"tampered", signature) is False
        backend.delete(handle)

    def test_verify_rejects_wrong_signature(self) -> None:
        backend = EnvBackend(prefix="SYPACT_TEST_")
        identity, handle = AgentIdentity.generate(
            agent_id="agent-005", owner_id="zan", backend=backend,
        )
        assert identity.verify(b"message", b"\x00" * 64) is False
        backend.delete(handle)


class TestReprSafety:
    def test_repr_shows_id_not_key(self) -> None:
        backend = EnvBackend(prefix="SYPACT_TEST_")
        identity, handle = AgentIdentity.generate(
            agent_id="agent-006", owner_id="zan", backend=backend,
        )
        r = repr(identity)
        assert "agent-006" in r
        assert "zan" in r
        assert str(identity.public_key) not in r
        backend.delete(handle)
