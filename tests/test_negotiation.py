"""Tests for Layer 3: Capability negotiation."""

from datetime import datetime, timezone
from sypact.negotiation import Capability, CapabilitySet, Permission


class TestCapabilitySet:
    def test_offers_returns_capabilities(self) -> None:
        cap = Capability(name="read_data", permissions=frozenset({Permission.RESOLVE}))
        cs = CapabilitySet(capabilities=[cap], owner_id="alice")
        assert cs.offers() == [cap]

    def test_empty_set(self) -> None:
        cs = CapabilitySet(capabilities=[], owner_id="alice")
        assert cs.offers() == []


class TestNegotiation:
    def test_matching_capabilities(self) -> None:
        read = Capability(name="read_data", permissions=frozenset({Permission.RESOLVE}))
        alice = CapabilitySet(capabilities=[read], owner_id="alice")
        bob = CapabilitySet(capabilities=[read], owner_id="bob")
        result = alice.negotiate(bob)
        assert len(result) == 1
        assert result[0].name == "read_data"

    def test_no_overlap(self) -> None:
        read = Capability(name="read_data", permissions=frozenset({Permission.RESOLVE}))
        write = Capability(name="write_data", permissions=frozenset({Permission.DELEGATE}))
        alice = CapabilitySet(capabilities=[read], owner_id="alice")
        bob = CapabilitySet(capabilities=[write], owner_id="bob")
        assert alice.negotiate(bob) == []

    def test_partial_overlap(self) -> None:
        read = Capability(name="read_data", permissions=frozenset({Permission.RESOLVE}))
        write = Capability(name="write_data", permissions=frozenset({Permission.DELEGATE}))
        delete = Capability(name="delete_data", permissions=frozenset({Permission.REVOKE}))
        alice = CapabilitySet(capabilities=[read, write], owner_id="alice")
        bob = CapabilitySet(capabilities=[write, delete], owner_id="bob")
        result = alice.negotiate(bob)
        assert len(result) == 1
        assert result[0].name == "write_data"

    def test_permission_intersection(self) -> None:
        cap_a = Capability(name="data", permissions=frozenset({Permission.RESOLVE, Permission.DELEGATE}))
        cap_b = Capability(name="data", permissions=frozenset({Permission.RESOLVE, Permission.REVOKE}))
        alice = CapabilitySet(capabilities=[cap_a], owner_id="alice")
        bob = CapabilitySet(capabilities=[cap_b], owner_id="bob")
        result = alice.negotiate(bob)
        assert len(result) == 1
        assert result[0].permissions == frozenset({Permission.RESOLVE})


class TestExpiry:
    def test_expired_capability_excluded_from_offers(self) -> None:
        expired = Capability(name="old", permissions=frozenset({Permission.RESOLVE}), expires_at=datetime(2020, 1, 1, tzinfo=timezone.utc))
        valid = Capability(name="current", permissions=frozenset({Permission.RESOLVE}), expires_at=datetime(2099, 1, 1, tzinfo=timezone.utc))
        cs = CapabilitySet(capabilities=[expired, valid], owner_id="alice")
        offers = cs.offers()
        assert len(offers) == 1
        assert offers[0].name == "current"

    def test_no_expiry_means_valid(self) -> None:
        cap = Capability(name="forever", permissions=frozenset({Permission.RESOLVE}))
        cs = CapabilitySet(capabilities=[cap], owner_id="alice")
        assert len(cs.offers()) == 1
