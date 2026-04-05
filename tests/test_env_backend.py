"""Tests for EnvBackend -- environment variable secret backend."""

import os

import pytest

from blindfold import CredentialHandle, EnvBackend, SecretBackend


@pytest.fixture
def backend() -> EnvBackend:
    return EnvBackend()


@pytest.fixture
def prefixed_backend() -> EnvBackend:
    return EnvBackend(prefix="BLINDFOLD_TEST_")


class TestStoreAndResolve:
    """Round-trip store/resolve tests."""

    def test_store_and_resolve(self, backend: EnvBackend) -> None:
        handle = backend.store("TEST_SECRET_XYZ", "super-secret-value")
        assert isinstance(handle, CredentialHandle)
        assert handle.name == "TEST_SECRET_XYZ"
        assert handle.backend_tag == "env"
        assert backend.resolve(handle) == "super-secret-value"
        # Cleanup
        backend.delete(handle)

    def test_resolve_missing(self, backend: EnvBackend) -> None:
        handle = CredentialHandle(name="DOES_NOT_EXIST_ABC123", backend_tag="env")
        with pytest.raises(KeyError, match="not set"):
            backend.resolve(handle)


class TestDelete:
    """Delete operation tests."""

    def test_delete(self, backend: EnvBackend) -> None:
        handle = backend.store("TEST_DEL_KEY", "value")
        backend.delete(handle)
        assert "TEST_DEL_KEY" not in os.environ
        assert len(backend.list()) == 0

    def test_delete_missing(self, backend: EnvBackend) -> None:
        handle = CredentialHandle(name="NEVER_STORED", backend_tag="env")
        with pytest.raises(KeyError, match="not tracked"):
            backend.delete(handle)


class TestList:
    """List operation tests."""

    def test_list(self, backend: EnvBackend) -> None:
        h1 = backend.store("TEST_LIST_A", "val_a")
        h2 = backend.store("TEST_LIST_B", "val_b")
        handles = backend.list()
        names = {h.name for h in handles}
        assert names == {"TEST_LIST_A", "TEST_LIST_B"}
        # Cleanup
        backend.delete(h1)
        backend.delete(h2)


class TestPrefix:
    """Prefix functionality tests."""

    def test_prefix(self, prefixed_backend: EnvBackend) -> None:
        handle = prefixed_backend.store("MY_KEY", "my_value")
        assert os.environ.get("BLINDFOLD_TEST_MY_KEY") == "my_value"
        assert prefixed_backend.resolve(handle) == "my_value"
        # Cleanup
        prefixed_backend.delete(handle)


class TestProtocol:
    """Protocol conformance tests."""

    def test_protocol_conformance(self) -> None:
        backend = EnvBackend()
        assert isinstance(backend, SecretBackend)
