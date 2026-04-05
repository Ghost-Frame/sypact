"""blindfold: Agent trust library with opaque credential handling."""

from blindfold.auth.mutual import Challenge, ChallengeResponse, MutualAuth
from blindfold.backends.base import SecretBackend
from blindfold.backends.env import EnvBackend
from blindfold.handle import CredentialHandle
from blindfold.identity.agent import AgentIdentity
from blindfold.negotiation.capability import Capability, CapabilitySet, Permission
from blindfold.trust.scoring import TrustLedger, TrustScore

__version__ = "0.1.0"

__all__ = [
    "AgentIdentity",
    "Capability",
    "CapabilitySet",
    "Challenge",
    "ChallengeResponse",
    "CredentialHandle",
    "EnvBackend",
    "MutualAuth",
    "Permission",
    "SecretBackend",
    "TrustLedger",
    "TrustScore",
    "__version__",
]
