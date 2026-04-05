"""Environment variable backend: resolves handles from os.environ."""

from __future__ import annotations

import os
from datetime import datetime, timezone

from blindfold.handle import CredentialHandle


class EnvBackend:
    """Secret backend that resolves handles from environment variables.

    The simplest possible backend -- zero dependencies, works everywhere.
    Useful for testing, development, and simple deployments.
    """

    def __init__(self, prefix: str = "") -> None:
        self._prefix = prefix
        self._handles: dict[str, CredentialHandle] = {}

    @property
    def tag(self) -> str:
        return "env"

    def _env_key(self, name: str) -> str:
        return f"{self._prefix}{name}"

    def resolve(self, handle: CredentialHandle) -> str:
        """Resolve a handle by looking up the environment variable."""
        key = self._env_key(handle.name)
        try:
            return os.environ[key]
        except KeyError:
            raise KeyError(f"Environment variable {key!r} not set") from None

    def store(self, name: str, value: str, **metadata: str) -> CredentialHandle:
        """Store a secret as an environment variable and return a handle."""
        key = self._env_key(name)
        os.environ[key] = value
        handle = CredentialHandle(
            name=name,
            backend_tag=self.tag,
            metadata=dict(metadata),
            created_at=datetime.now(timezone.utc),
        )
        self._handles[name] = handle
        return handle

    def delete(self, handle: CredentialHandle) -> None:
        """Remove the environment variable and stop tracking the handle."""
        key = self._env_key(handle.name)
        if handle.name not in self._handles:
            raise KeyError(f"Handle {handle.name!r} not tracked by this backend")
        del os.environ[key]
        del self._handles[handle.name]

    def list(self) -> list[CredentialHandle]:
        """Return all tracked handles (not all env vars)."""
        return list(self._handles.values())
