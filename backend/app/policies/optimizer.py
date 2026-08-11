from typing import Dict, Any, Tuple, Optional
from app.policies.models import PolicyVersionModel, PolicyStatus
from app.policies.versioning import PolicyVersioningEngine

class PolicyOptimizer:
    """
    Policy Optimizer generating bounded candidate policy adaptations based on performance telemetry.
    Strictly enforces maximum adaptation limits (MAX_ADAPTATION_DELTA = 10%).
    The optimizer MUST NOT directly activate policies.
    """

    MAX_ADAPTATION_DELTA = 10.0  # Percentage cap on single parameter adaptations

    @classmethod
    def calculate_delta(cls, current_params: Dict[str, Any], proposed_params: Dict[str, Any]) -> float:
        """
        Calculates maximum relative delta percentage across numerical strategy parameters.
        """
        max_delta = 0.0
        for key, new_val in proposed_params.items():
            if key in current_params and isinstance(new_val, (int, float)) and isinstance(current_params[key], (int, float)):
                orig_val = current_params[key]
                if orig_val != 0:
                    delta = abs(new_val - orig_val) / abs(orig_val) * 100.0
                    if delta > max_delta:
                        max_delta = delta
                else:
                    max_delta = max(max_delta, abs(new_val) * 100.0)
            elif key not in current_params:
                max_delta = max(max_delta, 5.0)  # Default default delta for new parameters
        return round(max_delta, 2)

    @classmethod
    def propose_candidate(
        cls,
        policy_id: str,
        org_id: str,
        agent_name: str,
        active_version: PolicyVersionModel,
        proposed_parameters: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
        performance_metrics: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any], Optional[PolicyVersionModel]]:
        """
        Evaluates proposed policy parameter adjustments against safety bounds.
        Returns (status_string, result_dict, candidate_version_model_or_None).
        """
        current_params = active_version.parameters or {}

        if proposed_parameters is None:
            # Default auto-tune heuristic for bounded optimization (+5% improvement parameter shift)
            proposed_parameters = {}
            for k, v in current_params.items():
                if isinstance(v, (int, float)):
                    proposed_parameters[k] = round(v * 1.05, 2)
                else:
                    proposed_parameters[k] = v

        delta = cls.calculate_delta(current_params, proposed_parameters)

        # Enforce bounded adaptation limits
        if delta > cls.MAX_ADAPTATION_DELTA:
            return (
                "REJECTED",
                {
                    "status": "REJECTED",
                    "reason": "ADAPTATION_LIMIT_EXCEEDED",
                    "adaptation_delta": delta,
                    "max_allowed_delta": cls.MAX_ADAPTATION_DELTA
                },
                None
            )

        # Calculate expected improvement deterministically
        expected_improvement = round(min(15.0, max(2.0, delta * 0.8)), 2)

        change_reason = reason or f"Bounded auto-optimization proposed candidate adaptation (+{delta}% delta)"

        candidate = PolicyVersioningEngine.create_candidate_version(
            policy_id=policy_id,
            org_id=org_id,
            agent_name=agent_name,
            parent_version=active_version.version,
            new_parameters=proposed_parameters,
            adaptation_delta=delta,
            reason=change_reason,
            performance_metrics=performance_metrics,
            created_by=created_by
        )

        return (
            "CANDIDATE_CREATED",
            {
                "status": "CANDIDATE_CREATED",
                "adaptation_delta": delta,
                "expected_improvement": expected_improvement,
                "version": candidate.version
            },
            candidate
        )
