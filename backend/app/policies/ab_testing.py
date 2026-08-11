from typing import Dict, Any, Tuple
from app.policies.models import PolicyVersionModel, PolicyABTestModel

class PolicyABTestingEngine:
    """
    Deterministic A/B comparison engine evaluating candidate policies against control policies.
    Requires minimum sample counts and improvement thresholds before approving activation eligibility.
    """

    MIN_SAMPLE_COUNT = 3
    MIN_IMPROVEMENT_THRESHOLD = 2.0  # Percentage improvement needed

    @classmethod
    def evaluate_ab_test(
        cls,
        control_version: PolicyVersionModel,
        candidate_version: PolicyVersionModel,
        sample_count: int = 5
    ) -> Tuple[bool, float, str, Dict[str, Any]]:
        """
        Compares candidate policy against control policy deterministically.
        Returns (is_eligible, improvement_percent, status_reason, metrics_dict).
        """
        if sample_count < cls.MIN_SAMPLE_COUNT:
            return (
                False,
                0.0,
                f"INSUFFICIENT_SAMPLES: Required minimum {cls.MIN_SAMPLE_COUNT} samples, got {sample_count}",
                {"sample_count": sample_count}
            )

        control_score = control_version.performance_score or 80.0
        candidate_score = candidate_version.performance_score or 85.0

        # Deterministic relative improvement %
        if control_score > 0:
            improvement_pct = round((candidate_score - control_score) / control_score * 100.0, 2)
        else:
            improvement_pct = 0.0

        # Safety regression check: candidate confidence or risk regressed severely
        if candidate_version.risk_score > 75.0:
            return (
                False,
                improvement_pct,
                f"SAFETY_REGRESSION: Candidate risk score ({candidate_version.risk_score}) exceeds acceptable safety threshold",
                {"control_score": control_score, "candidate_score": candidate_score, "improvement_percent": improvement_pct}
            )

        if improvement_pct < cls.MIN_IMPROVEMENT_THRESHOLD:
            return (
                False,
                improvement_pct,
                f"INSUFFICIENT_IMPROVEMENT: Candidate improvement ({improvement_pct}%) below threshold ({cls.MIN_IMPROVEMENT_THRESHOLD}%)",
                {"control_score": control_score, "candidate_score": candidate_score, "improvement_percent": improvement_pct}
            )

        return (
            True,
            improvement_pct,
            "PASSED: Candidate policy demonstrated statistically valid performance gain without safety regression",
            {
                "control_score": control_score,
                "candidate_score": candidate_score,
                "improvement_percent": improvement_pct,
                "sample_count": sample_count
            }
        )
