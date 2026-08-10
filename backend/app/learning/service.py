from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.learning.models import (
    AgentPerformanceModel, ToolReliabilityModel, LLMProviderPerformanceModel,
    AgentPolicyModel, AgentAdaptationModel, PolicyStatus, AdaptationStatus, ReliabilityClass
)
from app.learning.schemas import (
    AgentPerformanceResponse, ToolReliabilityResponse, LLMProviderPerformanceResponse,
    AgentPolicyResponse, AgentAdaptationResponse, LearningOverviewResponse,
    PolicyActivateResponse, PolicyRollbackResponse
)
from app.learning.repository import LearningRepository
from app.learning.reliability_engine import ReliabilityEngine
from app.learning.adaptation_engine import AdaptationEngine
from app.learning.performance_engine import PerformanceEngine
from app.learning.policy_engine import PolicyRollbackEngine

from app.governance.service import GovernanceService
from app.governance.schemas import ApprovalRequestCreate
from app.governance.models import DecisionType, RiskLevel

from app.memory.service import MemoryService
from app.memory.schemas import MemoryRecordCreate
from app.memory.models import MemoryType, OutcomeStatus

from app.core.events.publisher import event_publisher
from app.core.logging import logger

class LearningService:
    """
    High-level Learning Service managing performance telemetry, reliability scoring,
    bounded agent adaptations, versioned policy management, rollback execution, and Redis/SSE events.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = LearningRepository(session)

    async def get_overview(self, org_id: str) -> LearningOverviewResponse:
        perfs = await self.repo.list_agent_performances(org_id)
        tools = await self.repo.list_tool_reliabilities(org_id)
        providers = await self.repo.list_provider_performances(org_id)
        adaptations = await self.repo.list_adaptations(org_id)

        avg_reliability = sum(p.current_reliability_score for p in perfs) / len(perfs) if perfs else 80.0
        avg_pred_acc = sum(p.prediction_accuracy for p in perfs) / len(perfs) if perfs else 80.0
        active_policies = sum(1 for p in perfs if p.current_reliability_score >= 60.0)

        return LearningOverviewResponse(
            overall_system_reliability=round(avg_reliability, 1),
            prediction_accuracy_avg=round(avg_pred_acc, 1),
            total_adaptations_applied=len([a for a in adaptations if a.status == AdaptationStatus.ACTIVATED]),
            active_policies_count=active_policies,
            agent_performance=[AgentPerformanceResponse.model_validate(p) for p in perfs],
            tool_reliability=[ToolReliabilityResponse.model_validate(t) for t in tools],
            provider_performance=[LLMProviderPerformanceResponse.model_validate(pr) for pr in providers]
        )

    async def list_agent_performances(self, org_id: str) -> List[AgentPerformanceResponse]:
        perfs = await self.repo.list_agent_performances(org_id)
        return [AgentPerformanceResponse.model_validate(p) for p in perfs]

    async def get_agent_performance(self, agent_name: str, org_id: str) -> AgentPerformanceResponse:
        perf = await self.repo.get_or_create_agent_performance(agent_name, org_id)
        return AgentPerformanceResponse.model_validate(perf)

    async def record_execution_telemetry(
        self,
        agent_name: str,
        status_val: str,
        confidence: float,
        latency_ms: float,
        token_usage: int,
        org_id: str,
        prediction_accuracy: Optional[float] = None
    ) -> AgentPerformanceResponse:
        perf = await self.repo.get_or_create_agent_performance(agent_name, org_id)
        updated_perf = PerformanceEngine.update_agent_telemetry(
            perf=perf,
            status=status_val,
            confidence=confidence,
            latency_ms=latency_ms,
            token_usage=token_usage,
            prediction_accuracy=prediction_accuracy
        )
        await self.session.commit()
        await self.session.refresh(updated_perf)

        await event_publisher.publish(
            event_type="learning.performance.updated",
            workflow_id=None,
            organization_id=org_id,
            status=updated_perf.reliability_class.value,
            metadata={"agent_name": agent_name, "reliability_score": updated_perf.current_reliability_score}
        )

        return AgentPerformanceResponse.model_validate(updated_perf)

    async def propose_agent_adaptation(
        self,
        agent_name: str,
        proposed_delta: float,
        org_id: str,
        creator_user: Any
    ) -> AgentAdaptationResponse:
        perf = await self.repo.get_or_create_agent_performance(agent_name, org_id)

        valid, bounded_delta, explanation = AdaptationEngine.evaluate_adaptation_proposal(perf, proposed_delta)
        if not valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=explanation)

        # High delta (> 5%) requires Governance approval!
        requires_gov = bounded_delta > 5.0
        init_status = AdaptationStatus.PENDING_GOVERNANCE if requires_gov else AdaptationStatus.APPROVED

        approval_id = None
        if requires_gov:
            gov_svc = GovernanceService(self.session)
            app_req = await gov_svc.create_approval_request(
                payload=ApprovalRequestCreate(
                    title=f"Agent Adaptation Proposal: {agent_name}",
                    description=f"Bounded policy adaptation +{bounded_delta}% delta requested for {agent_name}.",
                    decision_type=DecisionType.STRATEGY_CHANGE,
                    requested_action=f"Activate Adaptation +{bounded_delta}% for {agent_name}",
                    ai_recommendation=explanation,
                    ai_confidence_score=perf.average_confidence
                ),
                org_id=org_id,
                creator_id=creator_user.id
            )
            approval_id = app_req.id

        # Create Adaptation Model
        adaptation = AgentAdaptationModel(
            organization_id=org_id,
            agent_name=agent_name,
            title=f"Bounded Policy Adaptation +{bounded_delta}%",
            description=explanation,
            previous_performance={"reliability": perf.current_reliability_score, "accuracy": perf.prediction_accuracy},
            expected_improvement={"expected_reliability_boost": bounded_delta},
            adaptation_delta=bounded_delta,
            status=init_status,
            approval_id=approval_id
        )
        created_adapt = await self.repo.create_adaptation(adaptation)

        # Grounded Lesson in Memory
        mem_svc = MemoryService(self.session)
        await mem_svc.create_memory(
            payload=MemoryRecordCreate(
                memory_type=MemoryType.LESSON,
                title=f"Adaptive Learning: {agent_name}",
                content=explanation,
                confidence_score=perf.average_confidence,
                importance_score=85.0,
                outcome_status=OutcomeStatus.SUCCESS,
                extra_metadata={"adaptation_id": created_adapt.id, "bounded_delta": bounded_delta}
            ),
            org_id=org_id,
            creator_id=creator_user.id
        )

        await self.session.commit()
        await self.session.refresh(created_adapt)

        await event_publisher.publish(
            event_type="learning.adaptation.proposed",
            workflow_id=None,
            organization_id=org_id,
            status=init_status.value,
            metadata={"agent_name": agent_name, "bounded_delta": bounded_delta}
        )

        return AgentAdaptationResponse.model_validate(created_adapt)

    async def list_policies(self, agent_name: str, org_id: str) -> List[AgentPolicyResponse]:
        policies = await self.repo.list_policies_by_agent(agent_name, org_id)
        return [AgentPolicyResponse.model_validate(p) for p in policies]

    async def activate_policy(self, policy_id: str, org_id: str) -> PolicyActivateResponse:
        policy = await self.repo.get_policy_by_id(policy_id, org_id)
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found.")

        # Deprecate prior active policy
        active = await self.repo.get_active_policy(policy.agent_name, org_id)
        if active and active.id != policy.id:
            active.status = PolicyStatus.DEPRECATED
            await self.repo.update_policy(active)

        policy.status = PolicyStatus.ACTIVE
        updated = await self.repo.update_policy(policy)
        await self.session.commit()

        await event_publisher.publish(
            event_type="learning.policy.created",
            workflow_id=None,
            organization_id=org_id,
            status="ACTIVE",
            metadata={"policy_id": updated.id, "agent_name": updated.agent_name}
        )

        return PolicyActivateResponse(
            policy_id=updated.id,
            agent_name=updated.agent_name,
            policy_version=updated.policy_version,
            status=PolicyStatus.ACTIVE,
            message=f"Policy version {updated.policy_version} successfully activated."
        )

    async def rollback_policy(self, agent_name: str, org_id: str) -> PolicyRollbackResponse:
        policies = await self.repo.list_policies_by_agent(agent_name, org_id)
        if len(policies) < 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No previous policy version available for rollback.")

        current_active = await self.repo.get_active_policy(agent_name, org_id) or policies[0]
        previous_policy = [p for p in policies if p.id != current_active.id][0]

        current_active.status = PolicyStatus.ROLLED_BACK
        await self.repo.update_policy(current_active)

        previous_policy.status = PolicyStatus.ACTIVE
        await self.repo.update_policy(previous_policy)

        await self.session.commit()

        await event_publisher.publish(
            event_type="learning.policy.rollback",
            workflow_id=None,
            organization_id=org_id,
            status="ROLLED_BACK",
            metadata={"agent_name": agent_name, "active_policy_id": previous_policy.id}
        )

        return PolicyRollbackResponse(
            agent_name=agent_name,
            rolled_back_policy_id=current_active.id,
            activated_policy_id=previous_policy.id,
            reason="Performance degradation detected; restored previous active policy version."
        )
