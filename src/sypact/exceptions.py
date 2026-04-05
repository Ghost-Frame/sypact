"""sypact exception hierarchy."""


class SypactError(Exception):
    """Base exception for all sypact errors."""


class AuthenticationFailed(SypactError):
    """Mutual authentication challenge-response failed."""


class NoSharedCapabilities(SypactError):
    """Capability negotiation found no overlap between agents."""


class TrustBelowThreshold(SypactError):
    """Agent trust score is below the required threshold."""
