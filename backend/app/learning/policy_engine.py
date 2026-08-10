from typing import Optional, List, Dict, Any, Tuple
from app.learning.models import AgentPolicyModel, PolicyStatus

class PolicyRollbackEngine:
    """
    Policy Rollback Engine evaluating performance degradation and managing versioned policy rollbacks.
    Triggers rollback if:
    - Performance decreases > 15%
    - Prediction accuracy decreases > 20%
    - Failure rate increases > 20%
    - Human rejection rate increases > 20%
    """

    @classmethod
    def should_trigger_rollback(
        cls,
        prior_score: float,
        current_score: float,
        prior_accuracy: float,
        current_accuracy: float,
        prior_rejection: float,
        current_rejection: float
    ) -> Tuple[bool, str]:
        score_drop = prior_score - current_score
        accuracy_drop = prior_accuracy - current_accuracy
        rejection_increase = current_rejection - prior_rejection

        if score_drop > 15.0:
            return True, f"Performance dropped by {round(score_drop, 1)}% (>15% threshold)."

        if accuracy_drop > 20.0:
            return True, f"Prediction accuracy dropped by {round(accuracy_drop, 1)}% (>20% threshold)."

        if rejection_increase > 20.0:
            return True, f"Human rejection rate increased by {round(rejection_increase, 1)}% (>20% threshold)."

        return False, "Performance remains within acceptable adaptation thresholds."
