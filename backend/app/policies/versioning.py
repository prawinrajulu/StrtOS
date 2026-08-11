from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.policies.models import PolicyVersionModel, PolicyStatus

class PolicyVersioningEngine:
    """
    Manages immutable policy versioning, lineage tracking, semver incrementing,
    and target version resolution for policy rollbacks.
    """

    @staticmethod
    def bump_semver(current_version: str, minor: bool = True) -> str:
        """
        Increments semantic version string (e.g. '1.0.0' -> '1.1.0').
        """
        clean_v = current_version.lstrip("v")
        parts = clean_v.split(".")
        if len(parts) != 3:
            parts = ["1", "0", "0"]
        major, min_v, patch = int(parts[0]), int(parts[1]), int(parts[2])
        if minor:
            min_v += 1
            patch = 0
        else:
            patch += 1
        return f"{major}.{min_v}.{patch}"

    @classmethod
    def create_candidate_version(
        cls,
        policy_id: str,
        org_id: str,
        agent_name: str,
        parent_version: str,
        new_parameters: Dict[str, Any],
        adaptation_delta: float,
        reason: str,
        performance_metrics: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> PolicyVersionModel:
        """
        Creates a new immutable candidate policy version without mutating parent version.
        """
        next_version = cls.bump_semver(parent_version, minor=True)

        candidate = PolicyVersionModel(
            policy_id=policy_id,
            organization_id=org_id,
            agent_name=agent_name,
            version=next_version,
            status=PolicyStatus.CANDIDATE,
            parameters=new_parameters,
            performance_score=performance_metrics.get("overall_policy_score", 80.0) if performance_metrics else 80.0,
            confidence_score=performance_metrics.get("confidence_score", 85.0) if performance_metrics else 85.0,
            risk_score=30.0,
            adaptation_delta=adaptation_delta,
            parent_version=parent_version,
            change_reason=reason,
            performance_metrics=performance_metrics or {},
            created_by=created_by,
            created_at=datetime.now(timezone.utc)
        )
        return candidate

    @classmethod
    def activate_version(cls, version_model: PolicyVersionModel) -> None:
        """
        Transitions candidate policy version to ACTIVE status.
        """
        version_model.status = PolicyStatus.ACTIVE
        version_model.activated_at = datetime.now(timezone.utc)

    @classmethod
    def retire_version(cls, version_model: PolicyVersionModel, new_status: PolicyStatus = PolicyStatus.SUPERSEDED) -> None:
        """
        Retires an existing active policy version.
        """
        version_model.status = new_status
        version_model.retired_at = datetime.now(timezone.utc)
