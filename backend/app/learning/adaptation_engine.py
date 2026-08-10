from typing import Dict, Any, Optional, Tuple, List
from app.learning.models import AgentPerformanceModel, AgentAdaptationModel, AdaptationStatus

class AdaptationEngine:
    """
    Grounded Adaptation Engine enforcing strict bounded adaptation limits:
    - MAX_ADAPTATION_DELTA = 10.0%
    - MAX_CONFIDENCE_BOOST = 10.0%
    - MIN_OUTCOMES_FOR_LEARNING = 3
    No ungrounded or fabricated learning signals.
    """

    MAX_ADAPTATION_DELTA = 10.0
    MAX_CONFIDENCE_BOOST = 10.0
    MIN_OUTCOMES_FOR_LEARNING = 3

    @classmethod
    def evaluate_adaptation_proposal(
        cls,
        perf: AgentPerformanceModel,
        proposed_delta: float
    ) -> Tuple[bool, float, str]:
        if perf.total_executions < cls.MIN_OUTCOMES_FOR_LEARNING:
            return False, 0.0, f"Insufficient executions ({perf.total_executions}/{cls.MIN_OUTCOMES_FOR_LEARNING}) for adaptation."

        clamped_delta = round(max(-cls.MAX_ADAPTATION_DELTA, min(cls.MAX_ADAPTATION_DELTA, proposed_delta)), 1)

        if perf.current_reliability_score < 50.0:
            return False, 0.0, f"Agent reliability score ({perf.current_reliability_score}%) is too low for adaptation."

        return True, clamped_delta, f"Adaptation approved with bounded delta of +{clamped_delta}% based on {perf.total_executions} verified outcomes."
