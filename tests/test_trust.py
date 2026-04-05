"""Tests for Layer 4: Trust scoring and reputation."""

from datetime import datetime, timezone, timedelta
from blindfold.trust import TrustScore, TrustLedger


class TestTrustScore:
    def test_initial_score_is_neutral(self) -> None:
        score = TrustScore(agent_id="agent-001")
        assert score.score == 0.5
        assert score.interactions == 0

    def test_success_increases_score(self) -> None:
        score = TrustScore(agent_id="agent-001")
        score.record_success()
        assert score.score > 0.5
        assert score.interactions == 1

    def test_failure_decreases_score(self) -> None:
        score = TrustScore(agent_id="agent-001")
        score.record_failure()
        assert score.score < 0.5
        assert score.interactions == 1

    def test_failure_hits_harder_than_success(self) -> None:
        s1 = TrustScore(agent_id="a")
        s2 = TrustScore(agent_id="b")
        s1.record_success()
        s2.record_failure()
        assert (0.5 - s2.score) > (s1.score - 0.5)

    def test_score_clamped_to_zero_one(self) -> None:
        score = TrustScore(agent_id="agent-001")
        for _ in range(100):
            score.record_failure()
        assert score.score >= 0.0
        for _ in range(200):
            score.record_success()
        assert score.score <= 1.0

    def test_diminishing_returns_on_success(self) -> None:
        score = TrustScore(agent_id="agent-001")
        score.record_success()
        first_gain = score.score - 0.5
        score.record_success()
        second_gain = score.score - (0.5 + first_gain)
        assert second_gain < first_gain


class TestMeetsThreshold:
    def test_meets_threshold_true(self) -> None:
        assert TrustScore(agent_id="a", score=0.8).meets_threshold(0.7) is True

    def test_meets_threshold_false(self) -> None:
        assert TrustScore(agent_id="a", score=0.3).meets_threshold(0.5) is False

    def test_meets_threshold_exact(self) -> None:
        assert TrustScore(agent_id="a", score=0.5).meets_threshold(0.5) is True


class TestDecay:
    def test_decay_pulls_toward_neutral(self) -> None:
        score = TrustScore(agent_id="a", score=0.9, last_updated=datetime.now(timezone.utc) - timedelta(days=30))
        score.decay()
        assert 0.5 < score.score < 0.9

    def test_decay_pulls_low_scores_up(self) -> None:
        score = TrustScore(agent_id="a", score=0.1, last_updated=datetime.now(timezone.utc) - timedelta(days=30))
        score.decay()
        assert 0.1 < score.score < 0.5

    def test_no_decay_when_recent(self) -> None:
        score = TrustScore(agent_id="a", score=0.9)
        original = score.score
        score.decay()
        assert score.score == original


class TestTrustLedger:
    def test_get_unknown_agent_returns_neutral(self) -> None:
        ledger = TrustLedger()
        score = ledger.get("unknown")
        assert score.agent_id == "unknown"
        assert score.score == 0.5

    def test_update_and_get(self) -> None:
        ledger = TrustLedger()
        score = ledger.get("agent-001")
        score.record_success()
        ledger.update(score)
        assert ledger.get("agent-001").score > 0.5

    def test_multiple_agents(self) -> None:
        ledger = TrustLedger()
        s1 = ledger.get("agent-a")
        s2 = ledger.get("agent-b")
        s1.record_success()
        s2.record_failure()
        ledger.update(s1)
        ledger.update(s2)
        assert ledger.get("agent-a").score > ledger.get("agent-b").score
