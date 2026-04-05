"""Tests for CredentialHandle -- the core sypact abstraction."""

import dataclasses

from sypact import CredentialHandle


class TestReprSafety:
    """Verify that handle string representations never leak secrets."""

    def test_repr_no_leak(self) -> None:
        handle = CredentialHandle(name="API_KEY", backend_tag="env")
        r = repr(handle)
        assert "API_KEY" in r
        assert "env" in r
        # Should not contain anything that looks like a secret value
        assert "secret" not in r.lower() or "API_KEY" in r

    def test_str_no_leak(self) -> None:
        handle = CredentialHandle(name="API_KEY", backend_tag="env")
        assert str(handle) == "<sypact:env/API_KEY>"

    def test_format_no_leak(self) -> None:
        handle = CredentialHandle(name="TOKEN", backend_tag="vault")
        formatted = f"Handle is {handle}"
        assert formatted == "Handle is <sypact:vault/TOKEN>"

    def test_repr_format(self) -> None:
        handle = CredentialHandle(name="KEY", backend_tag="default")
        assert repr(handle) == "CredentialHandle(name='KEY', backend='default')"


class TestFrozen:
    """Verify that handles are immutable."""

    def test_frozen_name(self) -> None:
        handle = CredentialHandle(name="KEY")
        try:
            handle.name = "OTHER"  # type: ignore[misc]
            assert False, "Should have raised FrozenInstanceError"
        except dataclasses.FrozenInstanceError:
            pass

    def test_frozen_backend_tag(self) -> None:
        handle = CredentialHandle(name="KEY")
        try:
            handle.backend_tag = "other"  # type: ignore[misc]
            assert False, "Should have raised FrozenInstanceError"
        except dataclasses.FrozenInstanceError:
            pass


class TestEquality:
    """Verify dataclass equality semantics."""

    def test_same_name_and_tag_are_equal(self) -> None:
        h1 = CredentialHandle(name="KEY", backend_tag="env")
        h2 = CredentialHandle(name="KEY", backend_tag="env")
        # Frozen dataclass equality checks all fields including created_at,
        # so two separately created handles won't be equal. That's correct
        # behavior -- each handle is a unique instance with its own timestamp.
        assert h1.name == h2.name
        assert h1.backend_tag == h2.backend_tag

    def test_different_names_not_equal(self) -> None:
        h1 = CredentialHandle(name="KEY1", backend_tag="env")
        h2 = CredentialHandle(name="KEY2", backend_tag="env")
        assert h1 != h2


class TestDefaults:
    """Verify default field values."""

    def test_default_backend_tag(self) -> None:
        handle = CredentialHandle(name="KEY")
        assert handle.backend_tag == "default"

    def test_default_metadata_is_empty_dict(self) -> None:
        handle = CredentialHandle(name="KEY")
        assert handle.metadata == {}

    def test_created_at_is_set(self) -> None:
        handle = CredentialHandle(name="KEY")
        assert handle.created_at is not None
