"""sypact: Agent trust library with opaque credential handling."""

from sypact.auth.mutual import Challenge, ChallengeResponse, MutualAuth
from sypact.backends.base import SecretBackend
from sypact.backends.env import EnvBackend
from sypact.handle import CredentialHandle
from sypact.identity.agent import AgentIdentity
from sypact.negotiation.capability import Capability, CapabilitySet, Permission
from sypact.trust.scoring import TrustLedger, TrustScore

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
