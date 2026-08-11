import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.policies.engine import PolicyPerformanceEngine

def test_deterministic_scoring_formula():
    # overall_policy_score = accuracy * 0.35 + reliability * 0.20 + outcome * 0.20 + confidence * 0.15 + evidence * 0.10
    scores = PolicyPerformanceEngine.evaluate_performance(
        predicted_kpi=100.0,
        actual_kpi=95.0,
        prediction_accuracy=90.0,
        confidence=85.0,
        outcome_status="SUCCESS",
        agent_execution_success=True,
        evidence_quality=80.0,
        historical_reliability=85.0
    )

    assert "accuracy_score" in scores
    assert "reliability_score" in scores
    assert "outcome_score" in scores
    assert "confidence_score" in scores
    assert "evidence_score" in scores
    assert "overall_policy_score" in scores

    # Check exact weighted calculation transparency
    expected = (
        scores["accuracy_score"] * 0.35 +
        scores["reliability_score"] * 0.20 +
        scores["outcome_score"] * 0.20 +
        scores["confidence_score"] * 0.15 +
        scores["evidence_score"] * 0.10
    )
    assert abs(scores["overall_policy_score"] - round(expected, 2)) <= 0.01

def test_failed_outcome_reduces_score():
    scores_failed = PolicyPerformanceEngine.evaluate_performance(
        predicted_kpi=100.0,
        actual_kpi=50.0,
        prediction_accuracy=50.0,
        confidence=60.0,
        outcome_status="FAILED",
        agent_execution_success=False,
        evidence_quality=40.0
    )
    assert scores_failed["outcome_score"] == 20.0
    assert scores_failed["overall_policy_score"] < 60.0
