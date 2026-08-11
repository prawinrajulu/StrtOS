# Decision Optimization Risk Engine
"""Evaluates risk for ActionCandidates based on multiple factors.
Returns a RiskLevelEnum (LOW, MEDIUM, HIGH, CRITICAL).
"""

from typing import Optional, Any
from app.decision_optimization.schemas import RiskLevelEnum
from app.decision_optimization.models import ActionCandidate

class ActionRiskEngine:
    """Computes composite risk score and maps to enum.
    HIGH and CRITICAL require governance; CRITICAL also needs explicit human approval.
    """

    def __init__(self):
        pass

    def _numeric_score(
        self,
        financial_exposure: Optional[float] = None,
        irreversibility: Optional[bool] = None,
        uncertainty: Optional[float] = None,
        prediction_confidence: Optional[float] = None,
        causal_confidence: Optional[float] = None,
        agent_reliability: Optional[float] = None,
        historical_failure_rate: Optional[float] = None,
        execution_complexity: Optional[int] = None,
        policy_restriction: Optional[bool] = None,
    ) -> float:
        """Calculate a weighted numeric risk score (0-100).
        Missing values are treated as neutral.
        """
        score = 0.0
        weight_sum = 0.0
        weights = {
            "financial_exposure": 0.20,
            "irreversibility": 0.15,
            "uncertainty": 0.15,
            "prediction_confidence": 0.10,
            "causal_confidence": 0.10,
            "agent_reliability": 0.10,
            "historical_failure_rate": 0.10,
            "execution_complexity": 0.05,
            "policy_restriction": 0.05,
        }

        def add(value: Optional[float], weight: float, transform=lambda x: x):
            nonlocal score, weight_sum
            if value is not None:
                score += transform(value) * weight
                weight_sum += weight

        add(financial_exposure, weights["financial_exposure"], lambda v: min(max(v, 0.0), 1.0))
        add(1.0 if irreversibility else 0.0, weights["irreversibility"])
        add(uncertainty, weights["uncertainty"], lambda v: min(max(v, 0.0), 1.0))
        add(1.0 - (prediction_confidence or 0.5), weights["prediction_confidence"], lambda v: min(max(v, 0.0), 1.0))
        add(1.0 - (causal_confidence or 0.5), weights["causal_confidence"], lambda v: min(max(v, 0.0), 1.0))
        add(1.0 - (agent_reliability or 0.5), weights["agent_reliability"], lambda v: min(max(v, 0.0), 1.0))
        add(historical_failure_rate, weights["historical_failure_rate"], lambda v: min(max(v, 0.0), 1.0))
        add(execution_complexity, weights["execution_complexity"], lambda v: min(max(v / 10.0, 0.0), 1.0))
        add(1.0 if policy_restriction else 0.0, weights["policy_restriction"])

        if weight_sum == 0:
            return 0.0
        return (score / weight_sum) * 100.0

    def evaluate(
        self,
        financial_exposure: Optional[float] = None,
        irreversibility: Optional[bool] = None,
        uncertainty: Optional[float] = None,
        prediction_confidence: Optional[float] = None,
        causal_confidence: Optional[float] = None,
        agent_reliability: Optional[float] = None,
        historical_failure_rate: Optional[float] = None,
        execution_complexity: Optional[int] = None,
        policy_restriction: Optional[bool] = None,
    ) -> RiskLevelEnum:
        """Public API – returns a RiskLevelEnum based on the numeric score."""
        numeric = self._numeric_score(
            financial_exposure=financial_exposure,
            irreversibility=irreversibility,
            uncertainty=uncertainty,
            prediction_confidence=prediction_confidence,
            causal_confidence=causal_confidence,
            agent_reliability=agent_reliability,
            historical_failure_rate=historical_failure_rate,
            execution_complexity=execution_complexity,
            policy_restriction=policy_restriction,
        )
        if numeric < 25:
            return RiskLevelEnum.LOW
        if numeric < 50:
            return RiskLevelEnum.MEDIUM
        if numeric < 75:
            return RiskLevelEnum.HIGH
        return RiskLevelEnum.CRITICAL

    def evaluate_candidate(self, candidate: ActionCandidate) -> RiskLevelEnum:
        """Helper to evaluate risk directly from an ActionCandidate object."""
        is_irreversible = candidate.reversibility in ["false", "no", "irreversible"] if candidate.reversibility else False
        hist_failure = (1.0 - candidate.historical_success) if candidate.historical_success is not None else None
        
        return self.evaluate(
            financial_exposure=(candidate.expected_cost or 0.0) / 10000.0 if candidate.expected_cost else None,
            irreversibility=is_irreversible,
            prediction_confidence=candidate.expected_confidence,
            causal_confidence=candidate.causal_support,
            agent_reliability=candidate.agent_reliability,
            historical_failure_rate=hist_failure,
            execution_complexity=candidate.time_to_impact // 10 if candidate.time_to_impact else None,
        )
