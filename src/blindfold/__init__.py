"""blindfold: Agent trust library with opaque credential handling."""

from blindfold.backends.base import SecretBackend
from blindfold.backends.env import EnvBackend
from blindfold.handle import CredentialHandle

__version__ = "0.1.0"

__all__ = [
    "CredentialHandle",
    "SecretBackend",
    "EnvBackend",
    "__version__",
]
