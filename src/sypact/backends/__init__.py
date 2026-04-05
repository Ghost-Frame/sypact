"""Secret backends for sypact."""

from sypact.backends.base import SecretBackend
from sypact.backends.env import EnvBackend

__all__ = ["SecretBackend", "EnvBackend"]
