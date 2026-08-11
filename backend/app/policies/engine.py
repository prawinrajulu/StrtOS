from typing import Dict, Any, Optional

class PolicyPerformanceEngine:
    """
    Deterministic performance evaluation engine for agent decision policies.
    Calculates overall policy score based on weighted transparent metrics.
    DO NOT use LLM for metric calculation.
    """

    WEIGHT_ACCURACY = 0.35
    WEIGHT_RELIABILITY = 0.20
    WEIGHT_OUTCOME = 0.20
    WEIGHT_CONFIDENCE = 0.15
    WEIGHT_EVIDENCE = 0.10

    @classmethod
    def evaluate_performance(
        cls,
        predicted_kpi: float,
        actual_kpi: float,
        prediction_accuracy: float = 80.0,
        confidence: float = 85.0,
        outcome_status: str = "SUCCESS",
        agent_execution_success: bool = True,
        evidence_quality: float = 85.0,
        historical_reliability: float = 80.0
    ) -> Dict[str, float]:
        """
        Calculates accuracy_score, reliability_score, outcome_score, confidence_score,
        evidence_score, and overall_policy_score deterministically.
        """
        # 1. Accuracy Score calculation based on prediction delta
        if predicted_kpi > 0:
            kpi_delta_pct = abs(actual_kpi - predicted_kpi) / predicted_kpi * 100.0
            kpi_acc = max(0.0, 100.0 - kpi_delta_pct)
        else:
            kpi_acc = prediction_accuracy

        accuracy_score = round(max(0.0, min(100.0, 0.6 * kpi_acc + 0.4 * prediction_accuracy)), 2)

        # 2. Reliability Score
        reliability_base = 90.0 if agent_execution_success else 40.0
        reliability_score = round(max(0.0, min(100.0, 0.5 * reliability_base + 0.5 * historical_reliability)), 2)

        # 3. Outcome Score
        outcome_map = {
            "SUCCESS": 100.0,
            "PARTIAL_SUCCESS": 75.0,
            "FAILED": 20.0,
            "CANCELLED": 50.0
        }
        outcome_score = outcome_map.get(outcome_status.upper(), 70.0)

        # 4. Confidence Score
        confidence_score = round(max(0.0, min(100.0, confidence)), 2)

        # 5. Evidence Score
        evidence_score = round(max(0.0, min(100.0, evidence_quality)), 2)

        # Overall Policy Score Weighted Formula
        overall_policy_score = round(
            accuracy_score * cls.WEIGHT_ACCURACY +
            reliability_score * cls.WEIGHT_RELIABILITY +
            outcome_score * cls.WEIGHT_OUTCOME +
            confidence_score * cls.WEIGHT_CONFIDENCE +
            evidence_score * cls.WEIGHT_EVIDENCE,
            2
        )

        return {
            "accuracy_score": accuracy_score,
            "reliability_score": reliability_score,
            "outcome_score": outcome_score,
            "confidence_score": confidence_score,
            "evidence_score": evidence_score,
            "overall_policy_score": overall_policy_score
        }
