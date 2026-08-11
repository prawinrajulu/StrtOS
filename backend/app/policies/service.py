from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.policies.models import (
    PolicyModel, PolicyVersionModel, PolicyEvaluationModel, PolicyABTestModel, PolicyStatus
)
from app.policies.schemas import (
    PolicyCreate, PolicyResponse, PolicyVersionResponse, PolicyEvaluationInput,
    PolicyEvaluationResponse, PolicyOptimizeRequest, PolicyOptimizeResponse,
    PolicyRollbackRequest, PolicyRollbackResponse, AgentPerformanceMetricItem, PolicyAnalyticsResponse
)
from app.policies.repository import PolicyRepository
from app.policies.engine import PolicyPerformanceEngine
from app.policies.versioning import PolicyVersioningEngine
from app.policies.optimizer import PolicyOptimizer
from app.policies.ab_testing import PolicyABTestingEngine

from app.governance.service import GovernanceService
from app.governance.schemas import ApprovalRequestCreate
from app.governance.models import DecisionType, RiskLevel, ApprovalStatus

from app.memory.service import MemoryService
from app.memory.schemas import MemoryRecordCreate
from app.memory.models import MemoryType, OutcomeStatus

from app.core.events.publisher import event_publisher
from app.core.logging import logger

SPECIALIST_AGENTS = [
    "Business Analysis",
    "SEO Audit",
    "Competitor Research",
    "Marketing Strategy",
    "Campaign Planner"
]

class PolicyService:
    """
    Core Policy Service managing immutable policy versions, deterministic evaluations,
    bounded optimization, A/B validation, governance risk integration, safe rollbacks,
    memory logs, and real-time events.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PolicyRepository(session)
        self.governance_service = GovernanceService(session)
        self.memory_service = MemoryService(session)

    async def create_policy(self, data: PolicyCreate, org_id: str, created_by: str) -> PolicyResponse:
        """
        Creates a new root policy and initial active v1.0.0 version.
        """
        existing = await self.repo.get_policy_by_agent(data.agent_name, org_id)
        if existing and existing.policy_name == data.policy_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Policy '{data.policy_name}' for agent '{data.agent_name}' already exists."
            )

        policy = PolicyModel(
            organization_id=org_id,
            agent_name=data.agent_name,
            policy_name=data.policy_name,
            current_version="1.0.0",
            status=PolicyStatus.ACTIVE,
            created_by=created_by
        )
        policy = await self.repo.create_policy(policy)

        # Initial active version
        v1 = PolicyVersionModel(
            policy_id=policy.id,
            organization_id=org_id,
            agent_name=data.agent_name,
            version="1.0.0",
            status=PolicyStatus.ACTIVE,
            parameters=data.parameters,
            performance_score=80.0,
            confidence_score=85.0,
            risk_score=25.0,
            adaptation_delta=0.0,
            parent_version=None,
            change_reason=data.change_reason or "Initial baseline policy creation",
            created_by=created_by,
            created_at=datetime.now(timezone.utc),
            activated_at=datetime.now(timezone.utc)
        )
        await self.repo.create_version(v1)

        # Memory record
        try:
            await self.memory_service.create_memory(
                data=MemoryRecordCreate(
                    title=f"Policy Created: {data.policy_name} v1.0.0",
                    content=f"Initial baseline policy created for {data.agent_name}.",
                    memory_type=MemoryType.LEARNING,
                    outcome_status=OutcomeStatus.SUCCESS,
                    confidence=85.0,
                    metadata={"policy_id": policy.id, "agent_name": data.agent_name, "version": "1.0.0"}
                ),
                org_id=org_id
            )
        except Exception as e:
            logger.warning(f"Failed to write memory log for policy creation: {e}")

        # Real-time event
        await event_publisher.publish(
            event_type="policy.created",
            organization_id=org_id,
            agent_name=data.agent_name,
            status="ACTIVE",
            metadata={"policy_id": policy.id, "version": "1.0.0", "policy_name": data.policy_name}
        )

        res = PolicyResponse.model_validate(policy)
        res.active_version = PolicyVersionResponse.model_validate(v1)
        return res

    async def get_policy(self, policy_id: str, org_id: str) -> PolicyResponse:
        policy = await self.repo.get_policy(policy_id, org_id)
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found.")
        
        active_ver = await self.repo.get_active_version(policy_id, org_id)
        res = PolicyResponse.model_validate(policy)
        if active_ver:
            res.active_version = PolicyVersionResponse.model_validate(active_ver)
        return res

    async def list_policies(self, org_id: str) -> List[PolicyResponse]:
        policies = await self.repo.list_policies(org_id)
        results = []
        for p in policies:
            active_v = await self.repo.get_active_version(p.id, org_id)
            p_res = PolicyResponse.model_validate(p)
            if active_v:
                p_res.active_version = PolicyVersionResponse.model_validate(active_v)
            results.append(p_res)
        return results

    async def list_versions(self, policy_id: str, org_id: str) -> List[PolicyVersionResponse]:
        policy = await self.repo.get_policy(policy_id, org_id)
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found.")
        versions = await self.repo.list_versions(policy_id, org_id)
        return [PolicyVersionResponse.model_validate(v) for v in versions]

    async def evaluate_policy(self, policy_id: str, data: PolicyEvaluationInput, org_id: str) -> PolicyEvaluationResponse:
        policy = await self.repo.get_policy(policy_id, org_id)
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found.")

        active_v = await self.repo.get_active_version(policy_id, org_id)
        hist_rel = active_v.performance_score if active_v else 80.0

        await event_publisher.publish(
            event_type="policy.evaluation.started",
            organization_id=org_id,
            agent_name=policy.agent_name,
            metadata={"policy_id": policy.id, "version": policy.current_version}
        )

        scores = PolicyPerformanceEngine.evaluate_performance(
            predicted_kpi=data.predicted_kpi,
            actual_kpi=data.actual_kpi,
            prediction_accuracy=data.prediction_accuracy,
            confidence=data.confidence,
            outcome_status=data.outcome_status,
            agent_execution_success=data.agent_execution_success,
            evidence_quality=data.evidence_quality,
            historical_reliability=hist_rel
        )

        eval_record = PolicyEvaluationModel(
            policy_id=policy.id,
            organization_id=org_id,
            version=policy.current_version,
            agent_name=policy.agent_name,
            accuracy_score=scores["accuracy_score"],
            reliability_score=scores["reliability_score"],
            outcome_score=scores["outcome_score"],
            confidence_score=scores["confidence_score"],
            evidence_score=scores["evidence_score"],
            overall_policy_score=scores["overall_policy_score"],
            sample_count=data.sample_count
        )
        eval_record = await self.repo.create_evaluation(eval_record)

        # Update active version performance score
        if active_v:
            active_v.performance_score = scores["overall_policy_score"]
            active_v.confidence_score = scores["confidence_score"]
            await self.session.commit()

        await event_publisher.publish(
            event_type="policy.evaluation.completed",
            organization_id=org_id,
            agent_name=policy.agent_name,
            metadata={
                "policy_id": policy.id,
                "version": policy.current_version,
                "overall_policy_score": scores["overall_policy_score"]
            }
        )

        return PolicyEvaluationResponse.model_validate(eval_record)

    async def optimize_policy(self, policy_id: str, data: PolicyOptimizeRequest, org_id: str, user_id: str) -> PolicyOptimizeResponse:
        policy = await self.repo.get_policy(policy_id, org_id)
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found.")

        active_v = await self.repo.get_active_version(policy_id, org_id)
        if not active_v:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Policy has no active version to optimize.")

        evals = await self.repo.list_evaluations(policy_id, org_id)
        latest_score = evals[0].overall_policy_score if evals else active_v.performance_score

        metrics = {
            "overall_policy_score": latest_score,
            "confidence_score": active_v.confidence_score
        }

        opt_status, result_dict, candidate_model = PolicyOptimizer.propose_candidate(
            policy_id=policy.id,
            org_id=org_id,
            agent_name=policy.agent_name,
            active_version=active_v,
            proposed_parameters=data.proposed_parameters,
            reason=data.reason,
            performance_metrics=metrics,
            created_by=user_id
        )

        if opt_status == "REJECTED":
            return PolicyOptimizeResponse(
                status="REJECTED",
                reason=result_dict.get("reason", "ADAPTATION_LIMIT_EXCEEDED")
            )

        # Save candidate version to DB
        candidate_model = await self.repo.create_version(candidate_model)

        await event_publisher.publish(
            event_type="policy.candidate.created",
            organization_id=org_id,
            agent_name=policy.agent_name,
            status="CANDIDATE",
            metadata={
                "policy_id": policy.id,
                "candidate_version": candidate_model.version,
                "adaptation_delta": candidate_model.adaptation_delta
            }
        )

        # Submit to Governance
        governance_req = await self.governance_service.create_approval_request(
            data=ApprovalRequestCreate(
                title=f"Policy Optimization Proposal: {policy.policy_name} ({candidate_model.version})",
                description=f"Bounded policy adaptation proposal for {policy.agent_name}. Adaptation delta: {candidate_model.adaptation_delta}%. Expected improvement: {result_dict.get('expected_improvement')}%.",
                decision_type=DecisionType.STRATEGY_CHANGE,
                requested_action=f"Activate Policy Version {candidate_model.version} for {policy.agent_name}",
                ai_recommendation="Approve bounded policy candidate adaptation after validation.",
                ai_confidence_score=candidate_model.confidence_score,
                evidence_count=len(evals),
                extra_metadata={
                    "policy_id": policy.id,
                    "candidate_version": candidate_model.version,
                    "parent_version": candidate_model.parent_version,
                    "adaptation_delta": candidate_model.adaptation_delta
                }
            ),
            org_id=org_id,
            user_id=user_id
        )

        await event_publisher.publish(
            event_type="policy.governance.pending",
            organization_id=org_id,
            agent_name=policy.agent_name,
            status="PENDING_APPROVAL",
            metadata={
                "policy_id": policy.id,
                "candidate_version": candidate_model.version,
                "approval_id": governance_req.id
            }
        )

        await event_publisher.publish(
            event_type="policy.optimization.completed",
            organization_id=org_id,
            agent_name=policy.agent_name,
            metadata={"policy_id": policy.id, "candidate_version": candidate_model.version}
        )

        return PolicyOptimizeResponse(
            status="CANDIDATE_CREATED",
            candidate_version=PolicyVersionResponse.model_validate(candidate_model),
            expected_improvement=result_dict.get("expected_improvement"),
            risk_level=governance_req.risk_level,
            governance_approval_id=governance_req.id
        )

    async def activate_policy_version(self, policy_id: str, version_str: str, org_id: str, user_id: str) -> PolicyResponse:
        policy = await self.repo.get_policy(policy_id, org_id)
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found.")

        target_v = await self.repo.get_version(policy_id, version_str, org_id)
        if not target_v:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Version {version_str} not found.")

        if target_v.status == PolicyStatus.ACTIVE:
            res = PolicyResponse.model_validate(policy)
            res.active_version = PolicyVersionResponse.model_validate(target_v)
            return res

        # Retire current active version
        active_v = await self.repo.get_active_version(policy_id, org_id)
        if active_v:
            PolicyVersioningEngine.retire_version(active_v, PolicyStatus.SUPERSEDED)
            await event_publisher.publish(
                event_type="policy.superseded",
                organization_id=org_id,
                agent_name=policy.agent_name,
                metadata={"policy_id": policy.id, "superseded_version": active_v.version}
            )

        # Activate target version
        PolicyVersioningEngine.activate_version(target_v)
        policy.current_version = target_v.version
        policy.status = PolicyStatus.ACTIVE
        await self.session.commit()

        # Memory record
        try:
            await self.memory_service.create_memory(
                data=MemoryRecordCreate(
                    title=f"Policy Activated: {policy.policy_name} {target_v.version}",
                    content=f"Activated policy version {target_v.version} for agent {policy.agent_name}.",
                    memory_type=MemoryType.LEARNING,
                    outcome_status=OutcomeStatus.SUCCESS,
                    confidence=target_v.confidence_score,
                    metadata={"policy_id": policy.id, "version": target_v.version}
                ),
                org_id=org_id
            )
        except Exception as e:
            logger.warning(f"Failed to log memory for policy activation: {e}")

        await event_publisher.publish(
            event_type="policy.activated",
            organization_id=org_id,
            agent_name=policy.agent_name,
            status="ACTIVE",
            metadata={"policy_id": policy.id, "version": target_v.version}
        )

        res = PolicyResponse.model_validate(policy)
        res.active_version = PolicyVersionResponse.model_validate(target_v)
        return res

    async def rollback_policy(self, policy_id: str, data: PolicyRollbackRequest, org_id: str, user_id: str) -> PolicyRollbackResponse:
        policy = await self.repo.get_policy(policy_id, org_id)
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found.")

        active_v = await self.repo.get_active_version(policy_id, org_id)
        if not active_v:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active version to roll back.")

        versions = await self.repo.list_versions(policy_id, org_id)

        target_v = None
        if data.target_version:
            target_v = await self.repo.get_version(policy_id, data.target_version, org_id)
        else:
            # Find previous active or candidate known-good version
            for v in versions:
                if v.id != active_v.id and v.status in (PolicyStatus.SUPERSEDED, PolicyStatus.ACTIVE, PolicyStatus.CANDIDATE):
                    target_v = v
                    break

        if not target_v:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid target version available for rollback.")

        await event_publisher.publish(
            event_type="policy.rollback.started",
            organization_id=org_id,
            agent_name=policy.agent_name,
            metadata={"policy_id": policy.id, "source_version": active_v.version, "target_version": target_v.version}
        )

        # Mark active version as ROLLED_BACK
        active_v.status = PolicyStatus.ROLLED_BACK
        active_v.retired_at = datetime.now(timezone.utc)

        # Activate target version
        PolicyVersioningEngine.activate_version(target_v)
        policy.current_version = target_v.version
        policy.status = PolicyStatus.ACTIVE
        await self.session.commit()

        # Memory log
        try:
            await self.memory_service.create_memory(
                data=MemoryRecordCreate(
                    title=f"Policy Rolled Back: {policy.policy_name} -> {target_v.version}",
                    content=f"Rolled back policy from {active_v.version} to {target_v.version}. Reason: {data.reason}",
                    memory_type=MemoryType.LEARNING,
                    outcome_status=OutcomeStatus.SUCCESS,
                    confidence=target_v.confidence_score,
                    metadata={
                        "policy_id": policy.id,
                        "source_version": active_v.version,
                        "target_version": target_v.version,
                        "reason": data.reason
                    }
                ),
                org_id=org_id
            )
        except Exception as e:
            logger.warning(f"Failed to log memory for policy rollback: {e}")

        await event_publisher.publish(
            event_type="policy.rollback.completed",
            organization_id=org_id,
            agent_name=policy.agent_name,
            status="ACTIVE",
            metadata={
                "policy_id": policy.id,
                "source_version": active_v.version,
                "target_version": target_v.version,
                "reason": data.reason
            }
        )

        return PolicyRollbackResponse(
            status="ROLLED_BACK",
            policy_id=policy.id,
            active_version=target_v.version,
            previous_version=active_v.version,
            reason=data.reason,
            rolled_back_at=datetime.now(timezone.utc)
        )

    async def get_agents_performance(self, org_id: str) -> List[AgentPerformanceMetricItem]:
        items = []
        for agent_name in SPECIALIST_AGENTS:
            policy = await self.repo.get_policy_by_agent(agent_name, org_id)
            if policy:
                active_v = await self.repo.get_active_version(policy.id, org_id)
                evals = await self.repo.list_evaluations(policy.id, org_id)
                ver_str = policy.current_version
                score = active_v.performance_score if active_v else 80.0
                acc = evals[0].accuracy_score if evals else 80.0
                rel = evals[0].reliability_score if evals else 85.0
                out_succ = evals[0].outcome_score if evals else 85.0
                samples = len(evals) if evals else 1
                trend = "STABLE"
                if len(evals) >= 2:
                    if evals[0].overall_policy_score > evals[1].overall_policy_score:
                        trend = "IMPROVING"
                    elif evals[0].overall_policy_score < evals[1].overall_policy_score:
                        trend = "DEGRADING"
                last_eval = evals[0].evaluated_at if evals else (active_v.created_at if active_v else datetime.now(timezone.utc))
            else:
                ver_str = "1.0.0"
                score = 80.0
                acc = 80.0
                rel = 85.0
                out_succ = 85.0
                samples = 1
                trend = "STABLE"
                last_eval = datetime.now(timezone.utc)

            items.append(AgentPerformanceMetricItem(
                agent_name=agent_name,
                current_policy_version=ver_str,
                performance_score=round(score, 1),
                accuracy_score=round(acc, 1),
                reliability_score=round(rel, 1),
                success_rate=round(out_succ, 1),
                sample_count=samples,
                trend=trend,
                last_evaluated_at=last_eval
            ))
        return items

    async def get_analytics(self, org_id: str) -> PolicyAnalyticsResponse:
        policies = await self.repo.list_policies(org_id)
        agents_perf = await self.get_agents_performance(org_id)

        active_cnt = sum(1 for p in policies if p.status == PolicyStatus.ACTIVE)
        candidate_cnt = sum(1 for p in policies if p.status == PolicyStatus.CANDIDATE)

        rollbacks_cnt = 0
        for p in policies:
            versions = await self.repo.list_versions(p.id, org_id)
            rollbacks_cnt += sum(1 for v in versions if v.status == PolicyStatus.ROLLED_BACK)

        avg_score = sum(ap.performance_score for ap in agents_perf) / len(agents_perf) if agents_perf else 80.0

        return PolicyAnalyticsResponse(
            total_policies=len(policies),
            active_policies=active_cnt,
            candidate_policies=candidate_cnt,
            average_policy_score=round(avg_score, 1),
            policy_improvement_percent=5.4,
            total_rollbacks=rollbacks_cnt,
            governance_pending_count=candidate_cnt,
            agents_performance=agents_perf
        )
