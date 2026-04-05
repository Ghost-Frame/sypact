"""sypact: Agent trust library with opaque credential handling."""

from sypact.auth.mutual import Challenge, ChallengeResponse, MutualAuth
from sypact.backends.base import SecretBackend
from sypact.backends.env import EnvBackend
from sypact.establish import establish
from sypact.exceptions import (
    AuthenticationFailed,
    NoSharedCapabilities,
    SypactError,
    TrustBelowThreshold,
)
from sypact.handle import CredentialHandle
from sypact.identity.agent import AgentIdentity
from sypact.negotiation.capability import Capability, CapabilitySet, Permission
from sypact.pact import Pact
from sypact.trust.scoring import TrustLedger, TrustScore

__version__ = "0.2.0"

__all__ = [
    "AgentIdentity",
    "AuthenticationFailed",
    "Capability",
    "CapabilitySet",
    "Challenge",
    "ChallengeResponse",
    "CredentialHandle",
    "EnvBackend",
    "establish",
    "MutualAuth",
    "NoSharedCapabilities",
    "Pact",
    "Permission",
    "SecretBackend",
    "SypactError",
    "TrustBelowThreshold",
    "TrustLedger",
    "TrustScore",
    "__version__",
]
