# Decision Optimization Optimizer
"""Deterministic optimizer that scores ActionCandidates and produces a recommendation.
All inputs are treated deterministically – the same set of candidates will always
produce the same recommendation and score breakdown.
"""

from typing import List, Tuple, Dict
from app.decision_optimization.models import ActionCandidate
from app.decision_optimization.schemas import (
    ActionCandidateResponse,
    RecommendationResponse,
    RiskLevelEnum,
)

def _normalize(value: float, min_val: float, max_val: float) -> float:
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)

class DecisionOptimizer:
    """Deterministic scoring of candidates with full explainable score breakdown.
    Candidates missing data use default fallback values if non-strict or are filtered out.
    """

    WEIGHTS = {
        "expected_value": 0.25,
        "expected_confidence": 0.15,
        "causal_support": 0.10,
        "historical_success": 0.15,
        "agent_reliability": 0.10,
        "risk": -0.10,
        "cost": -0.05,
        "reversibility": 0.05,
        "time_to_impact": -0.05,
    }

    def __init__(self):
        pass

    def _risk_numeric(self, risk: str | None) -> int:
        if risk is None:
            return 0
        mapping = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        return mapping.get(risk.upper(), 0)

    def _reversibility_score(self, rev: str | None) -> float:
        if rev is None:
            return 0.5
        val = rev.strip().lower()
        if val in ("yes", "true", "reversible"):
            return 1.0
        if val in ("no", "false", "irreversible"):
            return 0.0
        return 0.5

    def _score_candidate(self, cand: ActionCandidate) -> Tuple[float, Dict[str, float]]:
        risk_num = self._risk_numeric(cand.expected_risk)
        reversibility_val = self._reversibility_score(cand.reversibility)

        # Normalize components deterministically
        val_score = _normalize(cand.expected_value or 500.0, 0, 1000)
        conf_score = _normalize(cand.expected_confidence or 0.8, 0, 1)
        causal_score = _normalize(cand.causal_support or 0.75, 0, 1)
        hist_score = _normalize(cand.historical_success or 0.85, 0, 1)
        rel_score = _normalize(cand.agent_reliability or 0.90, 0, 1)
        risk_penalty = _normalize(risk_num, 0, 3)
        cost_penalty = _normalize(cand.expected_cost or 50.0, 0, 10000)
        rev_score = _normalize(reversibility_val, 0, 1)
        time_penalty = _normalize(cand.time_to_impact or 15, 0, 1440)

        breakdown = {
            "value_score": self.WEIGHTS["expected_value"] * val_score,
            "confidence_score": self.WEIGHTS["expected_confidence"] * conf_score,
            "causal_score": self.WEIGHTS["causal_support"] * causal_score,
            "historical_score": self.WEIGHTS["historical_success"] * hist_score,
            "agent_reliability_score": self.WEIGHTS["agent_reliability"] * rel_score,
            "risk_penalty": self.WEIGHTS["risk"] * risk_penalty,
            "cost_penalty": self.WEIGHTS["cost"] * cost_penalty,
            "reversibility_score": self.WEIGHTS["reversibility"] * rev_score,
            "time_to_impact_penalty": self.WEIGHTS["time_to_impact"] * time_penalty,
        }

        total_score = sum(breakdown.values())
        breakdown["total_score"] = total_score
        return total_score, breakdown

    async def optimize(self, candidates: List[ActionCandidate]) -> RecommendationResponse:
        """Run deterministic optimization.
        Returns a RecommendationResponse containing the top candidate, alternatives,
        a score breakdown and an explanation. Raises ValueError("INSUFFICIENT_DATA") if candidates list is empty.
        """
        if not candidates:
            raise ValueError("INSUFFICIENT_DATA")

        scored: List[Tuple[ActionCandidate, float, Dict[str, float]]] = []
        for cand in candidates:
            score, breakdown = self._score_candidate(cand)
            scored.append((cand, score, breakdown))

        scored.sort(key=lambda x: x[1], reverse=True)
        recommended, best_score, best_breakdown = scored[0]

        rec_resp = ActionCandidateResponse.model_validate(recommended, from_attributes=True)
        alt_resps = [ActionCandidateResponse.model_validate(c, from_attributes=True) for c, _, _ in scored[1:]]

        governance_required = recommended.expected_risk in ["HIGH", "CRITICAL"]

        return RecommendationResponse(
            decision_id=recommended.decision_id or f"dec-{recommended.id}",
            recommended_action=rec_resp,
            alternatives=alt_resps,
            score_breakdown=best_breakdown,
            explanation=f"Candidate {recommended.action_type} achieved the highest deterministic score ({best_score:.3f}).",
            risk_level=RiskLevelEnum(recommended.expected_risk) if recommended.expected_risk else RiskLevelEnum.LOW,
            governance_required=governance_required,
        )
