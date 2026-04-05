"""Backend protocol: the interface all secret backends implement."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from blindfold.handle import CredentialHandle


@runtime_checkable
class SecretBackend(Protocol):
    """Protocol defining the interface for secret storage backends.

    Backends resolve opaque handles to secrets at point of use.
    The naming is intentional: resolve() not get(), signaling that
    callers should not cache or store the result.
    """

    @property
    def tag(self) -> str:
        """Backend identifier string."""
        ...

    def resolve(self, handle: CredentialHandle) -> str:
        """Resolve a handle to its secret value.

        This is the point-of-use resolution. The returned value should
        be used immediately and not stored.
        """
        ...

    def store(self, name: str, value: str, **metadata: str) -> CredentialHandle:
        """Store a secret and return an opaque handle to it."""
        ...

    def delete(self, handle: CredentialHandle) -> None:
        """Remove a secret from the backend."""
        ...

    def list(self) -> list[CredentialHandle]:
        """List all managed handles. Never returns secret values."""
        ...
