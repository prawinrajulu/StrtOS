from typing import Dict, Any, Tuple
from app.learning.models import ReliabilityClass

class ReliabilityEngine:
    """
    Deterministic Agent Reliability Engine calculating 0-100 score based on:
    - Prediction Accuracy (30%)
    - Outcome Success Rate (25%)
    - Evidence Quality (15%)
    - Human Approval Rate (10%)
    - Tool Reliability (10%)
    - Swarm Consensus (5%)
    - Execution Stability (5%)
    """

    @classmethod
    def calculate_reliability(
        cls,
        total_executions: int,
        successful_executions: int,
        prediction_accuracy: float,
        outcome_success_rate: float,
        evidence_quality_score: float,
        human_approval_rate: float,
        tool_success_rate: float,
        swarm_consensus_rate: float
    ) -> Tuple[float, ReliabilityClass]:
        if total_executions < 3:
            return 0.0, ReliabilityClass.INSUFFICIENT_DATA

        execution_stability = (successful_executions / total_executions) * 100.0 if total_executions > 0 else 0.0

        # Weighted Score Calculation
        score = (
            (prediction_accuracy * 0.30) +
            (outcome_success_rate * 0.25) +
            (evidence_quality_score * 0.15) +
            (human_approval_rate * 0.10) +
            (tool_success_rate * 0.10) +
            (swarm_consensus_rate * 0.05) +
            (execution_stability * 0.05)
        )

        final_score = round(max(0.0, min(100.0, score)), 1)

        if final_score >= 90.0:
            rel_class = ReliabilityClass.EXCELLENT
        elif final_score >= 75.0:
            rel_class = ReliabilityClass.GOOD
        elif final_score >= 60.0:
            rel_class = ReliabilityClass.MODERATE
        elif final_score >= 40.0:
            rel_class = ReliabilityClass.LOW
        else:
            rel_class = ReliabilityClass.CRITICAL

        return final_score, rel_class
